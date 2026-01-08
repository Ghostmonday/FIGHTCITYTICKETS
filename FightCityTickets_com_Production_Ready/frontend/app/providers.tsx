"use client";

import { ReactNode } from "react";
import { AppealProvider } from "./lib/appeal-context";

export function Providers({ children }: { children: ReactNode }) {
  return <AppealProvider>{children}</AppealProvider>;
}
