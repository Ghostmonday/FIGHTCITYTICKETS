"use client";

import { useEffect } from "react";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

// Force dynamic rendering
export const dynamic = "force-dynamic";

export default function PricingPage() {
  const { state, updateState } = useAppeal();

  // Auto-select certified (only option) and store in context
  useEffect(() => {
    if (state.appealType !== "certified") {
      updateState({ appealType: "certified" });
    }
  }, []);

  const handleContinue = () => {
    updateState({ appealType: "certified" });
  };

  const PRICE = "$14.50";

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-6 mb-8">
          <h1 className="text-3xl font-bold mb-2 text-stone-800">
            Certified Defense Package
          </h1>
          <p className="text-stone-600 text-lg">
            Professional procedural compliance with certified mailing and
            tracking.
          </p>
        </div>

        {/* Single Option - Certified Mail */}
        <div className="bg-white rounded-lg border-2 border-stone-800 p-8 mb-8 shadow-md">
          <div className="flex items-center justify-between mb-6">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-stone-800 rounded-full flex items-center justify-center">
                <svg
                  className="w-6 h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <div>
                <h2 className="text-2xl font-semibold text-stone-800">
                  Certified Mail with Tracking
                </h2>
                <p className="text-stone-500">
                  Electronic Return Receipt Included
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-4xl font-light text-stone-800">{PRICE}</p>
              <p className="text-stone-500 text-sm">one-time payment</p>
            </div>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 gap-4 mb-6">
            <div className="flex items-start">
              <svg
                className="w-6 h-6 text-green-600 mr-3 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <div>
                <p className="text-stone-800 font-medium">
                  USPS Tracking Number
                </p>
                <p className="text-stone-500 text-sm">
                  Monitor delivery status online
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <svg
                className="w-6 h-6 text-green-600 mr-3 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <div>
                <p className="text-stone-800 font-medium">
                  Delivery Confirmation
                </p>
                <p className="text-stone-500 text-sm">
                  Know exactly when it arrives
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <svg
                className="w-6 h-6 text-green-600 mr-3 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <div>
                <p className="text-stone-800 font-medium">Proof of Mailing</p>
                <p className="text-stone-500 text-sm">
                  Certificate for your records
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <svg
                className="w-6 h-6 text-green-600 mr-3 mt-0.5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M5 13l4 4L19 7"
                />
              </svg>
              <div>
                <p className="text-stone-800 font-medium">
                  Legal Admissibility
                </p>
                <p className="text-stone-500 text-sm">
                  Court-ready documentation
                </p>
              </div>
            </div>
          </div>

          {/* What's Included */}
          <div className="bg-stone-50 border border-stone-200 rounded-lg p-4 mb-6">
            <p className="text-stone-700 font-medium mb-2">
              Your $14.50 includes:
            </p>
            <div className="grid md:grid-cols-3 gap-4 text-sm text-stone-600">
              <div>• Professional appeal letter</div>
              <div>• Certified USPS mailing</div>
              <div>• Tracking & delivery proof</div>
            </div>
          </div>

          {/* Value Proposition */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <p className="text-green-800 text-sm">
              <strong>Worth it:</strong> For the cost of this service, you get a
              physical tracking number and proof the municipality received your
              appeal. Critical if they claim "we never got it."
            </p>
          </div>
        </div>

        <LegalDisclaimer variant="compact" className="mb-6" />

        {/* Navigation */}
        <div className="flex justify-between items-center pt-6 border-t border-stone-200">
          <Link
            href="/appeal"
            className="text-stone-600 hover:text-stone-800 transition-colors"
          >
            ← Back
          </Link>
          <Link
            href="/appeal/camera"
            onClick={handleContinue}
            className="bg-stone-900 hover:bg-stone-800 text-white px-8 py-4 rounded-lg font-medium text-lg transition-colors"
          >
            Continue to Upload →
          </Link>
        </div>
      </div>
    </div>
  );
}
