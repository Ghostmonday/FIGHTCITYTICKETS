"use client";

import { ReactNode } from "react";
import { AppealProvider } from "./lib/appeal-context";
import { ThemeProvider } from "./lib/theme-context";

export function Providers({ children }: { children: ReactNode }) {
  return (
    <ThemeProvider>
      <AppealProvider>{children}</AppealProvider>
    </ThemeProvider>
  );
}
