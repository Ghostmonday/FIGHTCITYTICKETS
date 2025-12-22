"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface AppealState {
  citationNumber: string;
  violationDate: string;
  licensePlate: string;
  vehicleInfo: string;
  appealType: "standard" | "certified";
  photos: File[];
  transcript: string;
  draftLetter: string;
  signature: string | null;
}

interface AppealContextType {
  state: AppealState;
  updateState: (updates: Partial<AppealState>) => void;
  resetState: () => void;
}

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
};

const AppealContext = createContext<AppealContextType | undefined>(undefined);

export function AppealProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AppealState>(defaultState);

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
