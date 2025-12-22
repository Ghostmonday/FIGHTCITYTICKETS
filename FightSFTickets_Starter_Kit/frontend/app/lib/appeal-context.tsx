"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface UserInfo {
  name: string;
  addressLine1: string;
  addressLine2?: string;
  city: string;
  state: string;
  zip: string;
  email: string;
}

interface AppealState {
  citationNumber: string;
  violationDate: string;
  licensePlate: string;
  vehicleInfo: string;
  appealType: "standard" | "certified";
  // Store base64 strings instead of File objects for sessionStorage persistence
  photos: string[];
  transcript: string;
  draftLetter: string;
  signature: string | null;
  userInfo: UserInfo;
}

interface AppealContextType {
  state: AppealState;
  updateState: (updates: Partial<AppealState>) => void;
  resetState: () => void;
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
  appealType: "standard",
  photos: [],
  transcript: "",
  draftLetter: "",
  signature: null,
  userInfo: defaultUserInfo,
};

const AppealContext = createContext<AppealContextType | undefined>(undefined);

const STORAGE_KEY = 'fightsftickets_appeal_state';

export function AppealProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppealState>(defaultState);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load from sessionStorage on mount
  useEffect(() => {
    try {
      const stored = sessionStorage.getItem(STORAGE_KEY);
      if (stored) {
        setState(JSON.parse(stored));
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

  return (
    <AppealContext.Provider value={{ state, updateState: (updates) => setState(prev => ({ ...prev, ...updates })), resetState: () => setState(defaultState) }}>
      {children}
    </AppealContext.Provider>
  );
}

export function useAppeal() {
  const context = useContext(AppealContext);
  if (context === undefined) {
    throw new Error('useAppeal must be used within an AppealProvider');
  }
  return context;
}
