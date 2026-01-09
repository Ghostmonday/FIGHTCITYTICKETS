"use client";

import { useSearchParams } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { useAppeal } from "../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";

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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-2xl font-bold mb-2">
            Get Your {formatCityName(state.cityId)} Ticket Dismissed
          </h1>
          <p className="text-gray-700 mb-2 font-medium">
            You&apos;re about to save money and protect your record.
          </p>
          <p className="text-gray-600">Citation: {state.citationNumber}</p>
        </div>

        <div className="flex justify-between mb-8">
          {steps.map((s) => (
            <div key={s.num} className="flex-1 text-center">
              <div
                className={`w-10 h-10 rounded-full mx-auto mb-2 flex items-center justify-center ${
                  step >= s.num
                    ? "bg-blue-600 text-white"
                    : "bg-gray-200 text-gray-600"
                }`}
              >
                {s.num}
              </div>
              <p className="text-sm font-medium">{s.name}</p>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-xl font-bold mb-4">Step 1: Upload Photos</h2>
          <p className="text-gray-600 mb-6">
            Upload photos of your parking situation, meter, signs, or other
            evidence.
          </p>
          <LegalDisclaimer variant="compact" className="mb-6" />
          <Link
            href="/appeal/camera"
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Continue to Photos →
          </Link>
        </div>
      </div>
    </div>
  );
}

export default function AppealPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-gray-50 flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading...</p>
          </div>
        </div>
      }
    >
      <AppealPageContent />
    </Suspense>
  );
}
