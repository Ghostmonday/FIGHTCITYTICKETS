"use client";

import { useState } from "react";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

// Force dynamic rendering
export const dynamic = "force-dynamic";

export default function PricingPage() {
  const { state, updateState } = useAppeal();
  const [selectedType, setSelectedType] = useState<"standard" | "certified">(
    state.appealType || "certified"
  );

  const handleContinue = () => {
    updateState({ appealType: selectedType });
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-5xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-6 mb-8">
          <h1 className="text-2xl font-bold mb-2 text-stone-800">
            Select Mailing Option
          </h1>
          <p className="text-stone-600">
            Choose your procedural compliance submission method.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Certified Mail Option */}
          <div
            className={`bg-white rounded-lg border-2 p-6 cursor-pointer transition-all ${
              selectedType === "certified"
                ? "border-stone-800 shadow-md"
                : "border-stone-200 hover:border-stone-400"
            }`}
            onClick={() => setSelectedType("certified")}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-semibold text-stone-800">
                  Certified Mail
                </h2>
                <span className="px-2 py-1 bg-stone-100 text-stone-700 text-xs font-medium rounded-full">
                  Standard
                </span>
              </div>
              <div
                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                  selectedType === "certified"
                    ? "border-stone-800 bg-stone-800"
                    : "border-stone-300"
                }`}
              >
                {selectedType === "certified" && (
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={4}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
            </div>

            <div className="mb-6">
              <p className="text-3xl font-light text-stone-800">
                $19.89
                <span className="text-base font-normal text-stone-500 ml-1">
                  /submission
                </span>
              </p>
            </div>

            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-stone-700 mr-3 mt-0.5"
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
                <span className="text-stone-700">
                  <strong className="text-stone-800">Tracking number</strong>{" "}
                  provided
                </span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-stone-700 mr-3 mt-0.5"
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
                <span className="text-stone-700">
                  <strong className="text-stone-800">
                    Delivery confirmation
                  </strong>{" "}
                  from USPS
                </span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-stone-700 mr-3 mt-0.5"
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
                <span className="text-stone-700">
                  <strong className="text-stone-800">Online status</strong>{" "}
                  tracking
                </span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-stone-700 mr-3 mt-0.5"
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
                <span className="text-stone-700">
                  <strong className="text-stone-800">Proof of mailing</strong>{" "}
                  for records
                </span>
              </li>
            </ul>

            <div className="p-3 bg-stone-50 border border-stone-200 rounded">
              <p className="text-sm text-stone-600">
                Recommended for procedural compliance and due process
                documentation.
              </p>
            </div>
          </div>

          {/* Standard Mail Option */}
          <div
            className={`bg-white rounded-lg border-2 p-6 cursor-pointer transition-all ${
              selectedType === "standard"
                ? "border-stone-400"
                : "border-stone-200 hover:border-stone-400"
            }`}
            onClick={() => setSelectedType("standard")}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-stone-600">
                Standard Mail
              </h2>
              <div
                className={`w-5 h-5 rounded-full border-2 flex items-center justify-center ${
                  selectedType === "standard"
                    ? "border-stone-500 bg-stone-500"
                    : "border-stone-300"
                }`}
              >
                {selectedType === "standard" && (
                  <svg
                    className="w-3 h-3 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={4}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
            </div>

            <p className="text-3xl font-light text-stone-600 mb-6">
              $9.89
              <span className="text-base font-normal text-stone-400 ml-1">
                /submission
              </span>
            </p>

            <div className="p-3 bg-stone-100 border border-stone-200 rounded mb-6">
              <p className="text-sm text-stone-600 font-medium">
                ⚠️ No Tracking Available
              </p>
              <p className="text-xs text-stone-500 mt-1">
                Delivery confirmation cannot be provided.
              </p>
            </div>

            <ul className="space-y-2 mb-4">
              <li className="flex items-start text-stone-500">
                <span className="mr-3 mt-0.5">•</span>
                <span className="text-sm">Regular USPS delivery</span>
              </li>
              <li className="flex items-start text-stone-500">
                <span className="mr-3 mt-0.5">•</span>
                <span className="text-sm">No delivery confirmation</span>
              </li>
              <li className="flex items-start text-stone-500">
                <span className="mr-3 mt-0.5">•</span>
                <span className="text-sm">No status updates available</span>
              </li>
            </ul>

            <p className="text-sm text-stone-400 italic">Budget option only.</p>
          </div>
        </div>

        <LegalDisclaimer variant="compact" className="mb-6" />

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
            Continue with{" "}
            {selectedType === "certified" ? "Certified" : "Standard"} Mail →
          </Link>
        </div>
      </div>
    </div>
  );
}
