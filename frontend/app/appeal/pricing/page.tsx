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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h1 className="text-2xl font-bold mb-2">
            Choose Your Mailing Option
          </h1>
          <p className="text-gray-700">
            Select how you want your appeal letter mailed.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-6 mb-8">
          {/* Certified Mail Option */}
          <div
            className={`bg-white rounded-lg shadow-lg p-6 cursor-pointer transition ${
              selectedType === "certified"
                ? "ring-4 ring-green-500"
                : "hover:shadow-xl"
            }`}
            onClick={() => setSelectedType("certified")}
          >
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-2">
                <h2 className="text-xl font-bold text-green-700">
                  Certified Mail ✓
                </h2>
                <span className="px-2 py-1 bg-green-100 text-green-800 text-xs font-bold rounded-full">
                  Recommended
                </span>
              </div>
              <div
                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                  selectedType === "certified"
                    ? "border-green-600 bg-green-600"
                    : "border-gray-300"
                }`}
              >
                {selectedType === "certified" && (
                  <svg
                    className="w-4 h-4 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
            </div>

            <div className="flex items-center gap-2 mb-4">
              <p className="text-3xl font-bold">
                $19.89<span className="text-base font-normal">/appeal</span>
              </p>
              <svg
                className="w-6 h-6 text-blue-600"
                fill="currentColor"
                viewBox="0 0 24 24"
              >
                <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z" />
              </svg>
            </div>

            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-green-600 mr-2 mt-0.5"
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
                <span>
                  <strong>Tracking number</strong> provided
                </span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-green-600 mr-2 mt-0.5"
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
                <span>
                  <strong>Delivery confirmation</strong> from USPS
                </span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-green-600 mr-2 mt-0.5"
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
                <span>
                  <strong>Check status online</strong> anytime
                </span>
              </li>
              <li className="flex items-start">
                <svg
                  className="w-5 h-5 text-green-600 mr-2 mt-0.5"
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
                <span>
                  <strong>Proof of mailing</strong> for your records
                </span>
              </li>
            </ul>

            <p className="text-sm text-green-700 font-medium">
              Recommended for peace of mind
            </p>
          </div>

          {/* Standard Mail Option */}
          <div
            className={`bg-white rounded-lg shadow-lg p-6 cursor-pointer transition ${
              selectedType === "standard"
                ? "ring-4 ring-amber-400"
                : "hover:shadow-xl"
            }`}
            onClick={() => setSelectedType("standard")}
          >
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-bold text-gray-700">Standard Mail</h2>
              <div
                className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                  selectedType === "standard"
                    ? "border-amber-500 bg-amber-500"
                    : "border-gray-300"
                }`}
              >
                {selectedType === "standard" && (
                  <svg
                    className="w-4 h-4 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={3}
                      d="M5 13l4 4L19 7"
                    />
                  </svg>
                )}
              </div>
            </div>

            <p className="text-3xl font-bold mb-4">
              $9.89<span className="text-base font-normal">/appeal</span>
            </p>

            <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-800 font-medium">
                ⚠️ No Tracking Available
              </p>
              <p className="text-xs text-red-600 mt-1">
                We cannot confirm delivery or provide status updates after
                mailing.
              </p>
            </div>

            <ul className="space-y-2 mb-4">
              <li className="flex items-start text-gray-600">
                <span className="mr-2">•</span>
                <span className="text-sm">
                  Regular USPS delivery (no tracking)
                </span>
              </li>
              <li className="flex items-start text-gray-600">
                <span className="mr-2">•</span>
                <span className="text-sm">No delivery confirmation</span>
              </li>
              <li className="flex items-start text-gray-600">
                <span className="mr-2">•</span>
                <span className="text-sm">
                  Cannot check status after mailing
                </span>
              </li>
            </ul>

            <p className="text-sm text-gray-500 italic">
              Choose only if cost is a concern
            </p>
          </div>
        </div>

        <LegalDisclaimer variant="compact" className="mb-6" />

        <div className="flex justify-between items-center">
          <Link href="/appeal" className="text-gray-600 hover:text-gray-800">
            ← Back
          </Link>
          <Link
            href="/appeal/camera"
            onClick={handleContinue}
            className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white px-8 py-4 rounded-lg font-bold text-lg shadow-lg hover:shadow-xl transition"
          >
            Continue with{" "}
            {selectedType === "certified" ? "Certified" : "Standard"} Mail →
          </Link>
        </div>
      </div>
    </div>
  );
}
