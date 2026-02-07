"use client";

/**
 * Appeal Context - Global state management for appeal workflow
 *
 * Manages the complete appeal process from citation capture to submission.
 * All state is persisted to sessionStorage for recovery on refresh.
 *
 * DATA RETENTION NOTES:
 * - Photos stored as base64 strings (sessionStorage limit ~5MB)
 * - Consider: Offload photos to S3/Blob storage for large appeals
 * - Consider: IndexedDB for larger local storage
 *
 * TODO: Implement S3 photo upload for large appeals
 *       - sessionStorage has ~5MB limit
 *       - Photos quickly exceed this
 *       - Upload to S3, store reference in state
 *
 * TODO: Add multi-step progress saving
 *       - Save after each major step
 *       - Enable "continue where you left off" via email
 *
 * TODO: Add citation OCR retry logic
 *       - Tesseract.js can fail on blurry photos
 *       - Add "Try again" button
 *       - Fallback to manual entry
 */

import {
  createContext,
  ReactNode,
  useCallback,
  useContext,
  useEffect,
  useState,
} from "react";
import { debug, info, error as logError } from "../../lib/logger";

export interface UserInfo {
  name: string;
  addressLine1: string;
  addressLine2?: string;
  city: string;
  state: string;
  zip: string;
  email: string;
}

export interface AppealState {
  citationNumber: string;
  violationDate: string;
  licensePlate: string;
  vehicleInfo: string;
  // CERTIFIED-ONLY MODEL: All appeals use Certified Mail with tracking
  appealType: "certified";
  agency?: string;
  cityId?: string;
  sectionId?: string;
  appealDeadlineDays?: number;
  // Store base64 strings instead of File objects for sessionStorage persistence
  photos: string[];
  transcript: string;
  draftLetter: string;
  signature: string | null;
  userInfo: UserInfo;
  // Database reference
  intakeId?: number;
  draftId?: number;
  lastSaved?: string;
  // Optional features
  telemetryEnabled?: boolean;
}

interface AppealContextType {
  state: AppealState;
  updateState: (updates: Partial<AppealState>) => void;
  resetState: () => void;
  saveToDatabase: () => Promise<boolean>;
  loadFromDatabase: (intakeId: number) => Promise<boolean>;
  markForPersistence: () => void;
}

const defaultUserInfo: UserInfo = {
  name: "",
  addressLine1: "",
  addressLine2: "",
  city: "",
  state: "",
  zip: "",
  email: "",
};

const defaultState: AppealState = {
  citationNumber: "",
  violationDate: "",
  licensePlate: "",
  vehicleInfo: "",
  // CERTIFIED-ONLY: All appeals default to certified
  appealType: "certified",
  agency: undefined,
  cityId: undefined,
  sectionId: undefined,
  appealDeadlineDays: undefined,
  photos: [],
  transcript: "",
  draftLetter: "",
  signature: null,
  userInfo: defaultUserInfo,
  intakeId: undefined,
  draftId: undefined,
  lastSaved: undefined,
  telemetryEnabled: undefined,
};

const AppealContext = createContext<AppealContextType | undefined>(undefined);

const STORAGE_KEY = "fightcitytickets_appeal_state";

export function AppealProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppealState>(defaultState);
  const [isInitialized, setIsInitialized] = useState(false);
  const [needsDatabaseSync, setNeedsDatabaseSync] = useState(false);

  // Load from sessionStorage on mount
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        // Don't restore sensitive PII from storage - only restore non-sensitive fields
        setState((prev) => ({
          ...prev,
          citationNumber: parsed.citationNumber || prev.citationNumber,
          violationDate: parsed.violationDate || prev.violationDate,
          licensePlate: parsed.licensePlate || prev.licensePlate,
          vehicleInfo: parsed.vehicleInfo || prev.vehicleInfo,
          appealType: parsed.appealType || prev.appealType,
          cityId: parsed.cityId || prev.cityId,
          sectionId: parsed.sectionId || prev.sectionId,
          intakeId: parsed.intakeId || prev.intakeId,
          draftId: parsed.draftId || prev.draftId,
          // Don't restore userInfo, photos, signature, or other PII from storage
        }));
      }
    } catch (e) {
      logError("Failed to load state from storage", e);
    } finally {
      setIsInitialized(true);
    }
  }, []);

  // Save to sessionStorage on change - but exclude sensitive PII
  useEffect(() => {
    if (isInitialized) {
      try {
        // Only save non-sensitive fields to sessionStorage
        const safeState = {
          citationNumber: state.citationNumber,
          violationDate: state.violationDate,
          licensePlate: state.licensePlate,
          vehicleInfo: state.vehicleInfo,
          appealType: state.appealType,
          cityId: state.cityId,
          sectionId: state.sectionId,
          intakeId: state.intakeId,
          draftId: state.draftId,
          // Explicitly exclude: userInfo, photos, signature, draftLetter, transcript
        };
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(safeState));
      } catch (e) {
        logError("Failed to save state to storage", e);
      }
    }
  }, [
    isInitialized,
    state.citationNumber,
    state.violationDate,
    state.licensePlate,
    state.vehicleInfo,
    state.appealType,
    state.cityId,
    state.sectionId,
    state.intakeId,
    state.draftId,
  ]);

  const saveToDatabase = useCallback(async (): Promise<boolean> => {
    // Only save if we have an intake_id
    if (!state.intakeId) {
      debug("No intakeId, skipping database save");
      return false;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ""}/api/appeals/${state.intakeId
        }`,
        {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            citation_number: state.citationNumber,
            violation_date: state.violationDate,
            vehicle_info: state.vehicleInfo,
            license_plate: state.licensePlate,
            appeal_reason: state.draftLetter,
            selected_evidence: state.photos,
            signature_data: state.signature,
            user_name: state.userInfo.name,
            user_address_line1: state.userInfo.addressLine1,
            user_address_line2: state.userInfo.addressLine2,
            user_city: state.userInfo.city,
            user_state: state.userInfo.state,
            user_zip: state.userInfo.zip,
            user_email: state.userInfo.email,
            user_phone: null, // Not collected in current flow
            city: state.cityId,
          }),
        }
      );

      if (response.ok) {
        const timestamp = new Date().toISOString();
        setState((prev) => ({ ...prev, lastSaved: timestamp }));
        info(`State saved to database at ${timestamp}`);
        return true;
      } else {
        logError("Failed to save to database:", response.statusText);
        return false;
      }
    } catch (error) {
      logError("Error saving to database:", error);
      return false;
    }
  }, [state]);

  // Auto-save to database when needed
  // NOTE: saveToDatabase uses useCallback with proper dependencies, so we include it here
  useEffect(() => {
    if (needsDatabaseSync && state.intakeId && isInitialized) {
      saveToDatabase();
      setNeedsDatabaseSync(false);
    }
  }, [needsDatabaseSync, state.intakeId, isInitialized, saveToDatabase]);

  const updateState = useCallback((updates: Partial<AppealState>) => {
    setState((prev) => {
      const newState = { ...prev, ...updates, lastSaved: undefined };
      return newState;
    });
    setNeedsDatabaseSync(true);
  }, []);

  const resetState = useCallback(() => {
    setState(defaultState);
    setNeedsDatabaseSync(false);
    try {
      sessionStorage.removeItem(STORAGE_KEY);
    } catch (e) {
      logError("Failed to clear storage", e);
    }
  }, []);

  const loadFromDatabase = useCallback(
    async (intakeId: number): Promise<boolean> => {
      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE || ""}/api/appeals/${intakeId}`
        );

        if (response.ok) {
          const data = await response.json();

          // Map database fields to state
          const newState: Partial<AppealState> = {
            intakeId: data.id,
            citationNumber: data.citation_number,
            violationDate: data.violation_date || "",
            vehicleInfo: data.vehicle_info || "",
            licensePlate: data.license_plate || "",
            cityId: data.city,
            draftLetter: data.appeal_reason || "",
            photos: data.selected_evidence || [],
            signature: data.signature_data || null,
          };

          // Update user info if available
          if (data.user_name) {
            newState.userInfo = {
              name: data.user_name || "",
              addressLine1: data.user_address_line1 || "",
              addressLine2: data.user_address_line2 || "",
              city: data.user_city || "",
              state: data.user_state || "",
              zip: data.user_zip || "",
              email: data.user_email || "",
            };
          }

          setState((prev) => ({ ...prev, ...newState }));
          debug(`State loaded from database for intake ${intakeId}`);
          return true;
        } else {
          logError("Failed to load from database:", response.statusText);
          return false;
        }
      } catch (error) {
        logError("Error loading from database:", error);
        return false;
      }
    },
    []
  );

  const markForPersistence = useCallback(() => {
    setNeedsDatabaseSync(true);
  }, []);

  return (
    <AppealContext.Provider
      value={{
        state,
        updateState,
        resetState,
        saveToDatabase,
        loadFromDatabase,
        markForPersistence,
      }}
    >
      {children}
    </AppealContext.Provider>
  );
}

export function useAppeal() {
  const context = useContext(AppealContext);
  if (context === undefined) {
    throw new Error("useAppeal must be used within an AppealProvider");
  }
  return context;
}
