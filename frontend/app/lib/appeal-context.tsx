"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  useCallback,
  ReactNode,
} from "react";

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
        setState((prev) => ({ ...prev, ...parsed }));
      }
    } catch (e) {
      console.error("Failed to load state from storage", e);
    } finally {
      setIsInitialized(true);
    }
  }, []);

  // Save to sessionStorage on change
  useEffect(() => {
    if (isInitialized) {
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(state));
      } catch (e) {
        console.error("Failed to save state to storage", e);
      }
    }
  }, [state, isInitialized]);

  // Auto-save to database when needed
  useEffect(() => {
    if (needsDatabaseSync && state.intakeId && isInitialized) {
      saveToDatabase();
      setNeedsDatabaseSync(false);
    }
  }, [needsDatabaseSync, state.intakeId, isInitialized]);

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
      console.error("Failed to clear storage", e);
    }
  }, []);

  const saveToDatabase = useCallback(async (): Promise<boolean> => {
    // Only save if we have an intake_id
    if (!state.intakeId) {
      console.log("No intakeId, skipping database save");
      return false;
    }

    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || ""}/api/appeals/${
          state.intakeId
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
        console.log(`State saved to database at ${timestamp}`);
        return true;
      } else {
        console.error("Failed to save to database:", response.statusText);
        return false;
      }
    } catch (error) {
      console.error("Error saving to database:", error);
      return false;
    }
  }, [state]);

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
            appealReason: data.appeal_reason,
            selected_evidence: data.selected_evidence || [],
            signature_data: data.signature_data,
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
          console.log(`State loaded from database for intake ${intakeId}`);
          return true;
        } else {
          console.error("Failed to load from database:", response.statusText);
          return false;
        }
      } catch (error) {
        console.error("Error loading from database:", error);
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
