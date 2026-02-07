"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense, useEffect, useState } from "react";
import LegalDisclaimer from "../../components/LegalDisclaimer";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { useAppeal } from "../lib/appeal-context";

// Force dynamic rendering - this page uses client-side context
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
    <main className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex justify-between">
            {steps.map((s) => (
              <div key={s.num} className="flex-1 text-center">
                <div
                  className={`w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center ${step >= s.num
                      ? "bg-primary text-white"
                      : "bg-bg-subtle text-text-muted"
                    }`}
                >
                  {s.num}
                </div>
                <p
                  className={`text-body-sm ${step >= s.num
                      ? "text-text-primary font-medium"
                      : "text-text-muted"
                    }`}
                >
                  {s.name}
                </p>
              </div>
            ))}
          </div>
          <div className="relative mt-2">
            <div className="absolute top-0 left-0 right-0 h-0.5 bg-border" />
            <div
              className="absolute top-0 left-0 h-0.5 bg-primary transition-all duration-300"
              style={{ width: `${((step - 1) / (steps.length - 1)) * 100}%` }}
            />
          </div>
        </div>

        {/* Header Card */}
        <Card padding="lg" className="mb-6">
          <h1 className="text-heading-lg text-text-primary mb-2">
            Appeal Your {formatCityName(state.cityId)} Ticket
          </h1>
          <p className="text-body text-text-secondary mb-4">
            You&apos;re almost done. Add evidence and review your appeal before
            submitting.
          </p>
          <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-bg-subtle rounded-lg">
            <span className="text-caption text-text-muted">Citation:</span>
            <span className="font-mono text-body-sm text-text-primary">
              {state.citationNumber || "Not provided"}
            </span>
          </div>
        </Card>

        {/* Next Step */}
        <Card padding="lg" className="mb-6">
          <h2 className="text-heading-md text-text-primary mb-4">
            Step 1: Upload Evidence
          </h2>
          <p className="text-body text-text-secondary mb-6">
            Add photos of parking signs, meters, or anything that supports your
            appeal.
          </p>

          <Link href="/appeal/camera">
            <Button>Upload Photos →</Button>
          </Link>
        </Card>

        {/* Quick Links */}
        <div className="flex flex-wrap gap-4 mb-6">
          <Link
            href="/appeal/review"
            className="text-body text-primary hover:text-primary-hover font-medium"
          >
            Skip to review →
          </Link>
        </div>

        {/* Legal Disclaimer */}
        <LegalDisclaimer variant="compact" />
      </div>
    </main>
  );
}

export default function AppealPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-bg-page flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent mx-auto mb-4" />
            <p className="text-body text-text-secondary">Loading...</p>
          </div>
        </div>
      }
    >
      <AppealPageContent />
    </Suspense>
  );
}
