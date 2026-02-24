"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import LegalDisclaimer from "../../components/LegalDisclaimer";
import { useAppeal } from "../lib/appeal-context";

export const dynamic = "force-dynamic";

function AppealPageContent() {
  const searchParams = useSearchParams();
  const { state, updateState } = useAppeal();
  const [step] = useState(1);

  useEffect(() => {
    const citation = searchParams.get("citation");
    const city = searchParams.get("city");
    if (citation && !state.citationNumber) {
      updateState({ citationNumber: citation });
    }
    if (city && !state.cityId) {
      updateState({ cityId: city });
    }
  }, [searchParams, state.citationNumber, state.cityId, updateState]);

  const cityNames: Record<string, string> = {
    sf: "San Francisco",
    "us-ca-san_francisco": "San Francisco",
    la: "Los Angeles",
    "us-ca-los_angeles": "Los Angeles",
    nyc: "New York City",
    "us-ny-new_york": "New York City",
    "us-ca-san_diego": "San Diego",
    "us-az-phoenix": "Phoenix",
    "us-co-denver": "Denver",
    "us-il-chicago": "Chicago",
    "us-or-portland": "Portland",
    "us-pa-philadelphia": "Philadelphia",
    "us-tx-dallas": "Dallas",
    "us-tx-houston": "Houston",
    "us-ut-salt_lake_city": "Salt Lake City",
    "us-wa-seattle": "Seattle",
  };

  const formatCityName = (cityId: string | null | undefined) => {
    if (!cityId) return "Your City";
    return (
      cityNames[cityId] ||
      cityId
        .replace(/us-|-/g, " ")
        .replace(/_/g, " ")
        .split(" ")
        .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
        .join(" ")
    );
  };

  const steps = [
    { num: 1, name: "Photos", path: "/appeal/camera" },
    { num: 2, name: "Review", path: "/appeal/review" },
    { num: 3, name: "Sign", path: "/appeal/signature" },
    { num: 4, name: "Pay", path: "/appeal/checkout" },
  ];

  return (
    <main className="min-h-[calc(100vh-5rem)] flex flex-col items-center justify-center px-4 py-8 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
      <div className="w-full max-w-lg step-content">

        {/* Progress Bar */}
        <div className="mb-12">
          <div className="progress-bar">
            <div
              className="progress-bar-fill"
              style={{ width: `${((step - 1) / (steps.length - 1)) * 100}%` }}
            />
          </div>
          <div className="flex justify-between mt-2 text-sm" style={{ color: "var(--text-muted)" }}>
            {steps.map((s) => (
              <span key={s.num}>{s.name}</span>
            ))}
          </div>
        </div>

        {/* Header */}
        <div className="text-center mb-10">
          <h1 className="text-3xl font-bold mb-3 theme-transition" style={{ color: "var(--text-primary)" }}>
            Submitting to {formatCityName(state.cityId)}
          </h1>
          <p className="font-medium theme-transition" style={{ color: "var(--text-secondary)" }}>
            Your appeal is being processed through the Clerical Engine™.
          </p>
          <div
            className="inline-flex items-center gap-2 px-4 py-2 mt-4 rounded-lg"
            style={{ backgroundColor: "var(--bg-subtle)" }}
          >
            <span style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Citation:</span>
            <span style={{ color: "var(--text-primary)", fontFamily: "monospace" }}>
              {state.citationNumber || "Not provided"}
            </span>
          </div>
        </div>

        {/* Next Step Card */}
        <div className="card-step p-8 mb-8">
          <h2 className="text-xl font-semibold mb-4 theme-transition" style={{ color: "var(--text-primary)" }}>
            Step 1: Upload Evidence
          </h2>
          <p className="mb-6 theme-transition" style={{ color: "var(--text-secondary)" }}>
            Add photos of parking signs, meters, or anything that supports your appeal.
          </p>

          <Link href="/appeal/camera" className="btn-strike w-full">
            Upload Photos →
          </Link>
        </div>

        {/* Skip Link */}
        <div className="text-center mb-8">
          <Link
            href="/appeal/review"
            className="font-medium"
            style={{ color: "var(--accent)" }}
          >
            Skip to review →
          </Link>
        </div>

        {/* Disclaimer */}
        <LegalDisclaimer variant="compact" />
      </div>
    </main>
  );
}

export default function AppealPage() {
  return (
    <Suspense
      fallback={
        <div
          className="min-h-screen flex items-center justify-center theme-transition"
          style={{ backgroundColor: "var(--bg-page)" }}
        >
          <div className="text-center">
            <div
              className="animate-spin rounded-full h-10 w-10 mx-auto mb-4"
              style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }}
            />
            <p style={{ color: "var(--text-secondary)" }}>Loading...</p>
          </div>
        </div>
      }
    >
      <AppealPageContent />
    </Suspense>
  );
}
