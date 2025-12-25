"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "./lib/appeal-context";

interface CitationValidationResponse {
  is_valid: boolean;
  citation_number: string;
  agency: string;
  deadline_date: string | null;
  days_remaining: number | null;
  is_past_deadline: boolean;
  is_urgent: boolean;
  error_message: string | null;
  formatted_citation: string | null;
  city_id: string | null;
  section_id: string | null;
  appeal_deadline_days: number;
  phone_confirmation_required: boolean;
  phone_confirmation_policy: Record<string, any> | null;
}

export default function Home() {
  const [citationNumber, setCitationNumber] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [violationDate, setViolationDate] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] =
    useState<CitationValidationResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const router = useRouter();
  const { updateState } = useAppeal();

  const handleValidateCitation = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setValidationResult(null);

    if (!citationNumber.trim()) {
      setError("Please enter a citation number");
      return;
    }

    setIsValidating(true);
    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/tickets/validate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          citation_number: citationNumber.trim(),
          license_plate: licensePlate.trim() || null,
          violation_date: violationDate.trim() || null,
        }),
      });

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`);
      }

      const result = await response.json();
      setValidationResult(result);

      if (result.is_valid) {
        // Update appeal context with citation info
        updateState({
          citationNumber: result.citation_number,
          cityId: result.city_id,
          sectionId: result.section_id,
          appealDeadlineDays: result.appeal_deadline_days,
        });
      }
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Failed to validate citation",
      );
    } finally {
      setIsValidating(false);
    }
  };

  const handleStartAppeal = () => {
    if (validationResult?.is_valid) {
      router.push("/appeal");
    }
  };

  const formatCityName = (cityId: string | null) => {
    if (!cityId) return "Unknown City";

    const cityNames: Record<string, string> = {
      sf: "San Francisco",
      la: "Los Angeles",
      nyc: "New York City",
    };

    return cityNames[cityId] || cityId.toUpperCase();
  };

  const formatAgency = (agency: string, sectionId: string | null) => {
    if (sectionId) {
      const sections: Record<string, string> = {
        sfmta: "SFMTA (San Francisco Municipal Transportation Agency)",
        sfpd: "SFPD (San Francisco Police Department)",
        lapd: "LAPD (Los Angeles Police Department)",
        ladot: "LADOT (Los Angeles Department of Transportation)",
        nypd: "NYPD (New York Police Department)",
        nydot: "NYC DOT (New York City Department of Transportation)",
      };
      return sections[sectionId] || `${agency} - ${sectionId}`;
    }
    return agency;
  };

  return (
    <main className="min-h-screen bg-gradient-to-b from-gray-50 to-white p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 mb-4">
            Fight Parking Tickets in{" "}
            <span className="text-blue-600">3 Cities</span>
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Appeal your parking ticket with our automated system. We handle San
            Francisco, Los Angeles, and New York City citations with
            city-specific validation.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column: Citation Form */}
          <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8">
            <h2 className="text-2xl font-bold text-gray-800 mb-6">
              Check Your Citation
            </h2>

            <form onSubmit={handleValidateCitation} className="space-y-6">
              {/* Citation Number */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Citation Number *
                </label>
                <input
                  type="text"
                  value={citationNumber}
                  onChange={(e) => setCitationNumber(e.target.value)}
                  placeholder="e.g., 912345678, LA123456, 1234567"
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                  required
                  disabled={isValidating}
                />
                <p className="mt-2 text-sm text-gray-500">
                  Enter your citation number. We support SF, LA, and NYC
                  formats.
                </p>
              </div>

              {/* Optional Fields */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    License Plate (Optional)
                  </label>
                  <input
                    type="text"
                    value={licensePlate}
                    onChange={(e) =>
                      setLicensePlate(e.target.value.toUpperCase())
                    }
                    placeholder="e.g., ABC123"
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    disabled={isValidating}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Violation Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={violationDate}
                    onChange={(e) => setViolationDate(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition"
                    disabled={isValidating}
                  />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                  {error}
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={isValidating || !citationNumber.trim()}
                className={`w-full py-3 px-4 rounded-lg font-medium transition ${
                  isValidating
                    ? "bg-gray-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700 text-white"
                }`}
              >
                {isValidating ? (
                  <span className="flex items-center justify-center">
                    <svg
                      className="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                      xmlns="http://www.w3.org/2000/svg"
                      fill="none"
                      viewBox="0 0 24 24"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      ></circle>
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                      ></path>
                    </svg>
                    Validating...
                  </span>
                ) : (
                  "Validate Citation"
                )}
              </button>
            </form>
          </div>

          {/* Right Column: Results & Info */}
          <div className="space-y-8">
            {/* Validation Results */}
            {validationResult && (
              <div className="bg-white rounded-2xl shadow-lg p-6 md:p-8">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold text-gray-800">
                    Validation Results
                  </h2>
                  <div
                    className={`px-3 py-1 rounded-full text-sm font-medium ${
                      validationResult.is_valid
                        ? validationResult.is_urgent
                          ? "bg-orange-100 text-orange-800"
                          : "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {validationResult.is_valid
                      ? validationResult.is_urgent
                        ? "URGENT"
                        : "VALID"
                      : "INVALID"}
                  </div>
                </div>

                {validationResult.is_valid ? (
                  <div className="space-y-6">
                    {/* Citation Info */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-500">Citation Number</p>
                        <p className="font-semibold text-lg">
                          {validationResult.formatted_citation ||
                            validationResult.citation_number}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">City</p>
                        <p className="font-semibold text-lg">
                          {formatCityName(validationResult.city_id)}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Agency</p>
                        <p className="font-semibold">
                          {formatAgency(
                            validationResult.agency,
                            validationResult.section_id,
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Deadline</p>
                        <p className="font-semibold">
                          {validationResult.days_remaining !== null
                            ? `${validationResult.days_remaining} days`
                            : "Check date"}
                        </p>
                      </div>
                    </div>

                    {/* Special Requirements */}
                    {validationResult.phone_confirmation_required && (
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                        <div className="flex items-start">
                          <svg
                            className="w-5 h-5 text-blue-600 mt-0.5 mr-3"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <div>
                            <p className="font-medium text-blue-800">
                              Phone Confirmation Required
                            </p>
                            <p className="text-sm text-blue-700 mt-1">
                              This citation section requires phone confirmation
                              before appeal submission. We'll guide you through
                              this process.
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Deadline Warning */}
                    {validationResult.is_urgent && (
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-4">
                        <div className="flex items-start">
                          <svg
                            className="w-5 h-5 text-orange-600 mt-0.5 mr-3"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path
                              fillRule="evenodd"
                              d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                              clipRule="evenodd"
                            />
                          </svg>
                          <div>
                            <p className="font-medium text-orange-800">
                              Urgent Deadline
                            </p>
                            <p className="text-sm text-orange-700 mt-1">
                              Your appeal deadline is approaching! You have{" "}
                              {validationResult.days_remaining} day(s)
                              remaining.
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Start Appeal Button */}
                    <button
                      onClick={handleStartAppeal}
                      className="w-full py-3 px-4 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition"
                    >
                      Start Appeal Process
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <div className="text-red-600 mb-4">
                      <svg
                        className="w-12 h-12 mx-auto"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                      >
                        <path
                          strokeLinecap="round"
                          strokeLinejoin="round"
                          strokeWidth="2"
                          d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                      </svg>
                    </div>
                    <p className="text-gray-700">
                      {validationResult.error_message ||
                        "Invalid citation number format."}
                    </p>
                    <p className="text-sm text-gray-500 mt-2">
                      Please check your citation number and try again.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* City Support Info */}
            <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl shadow-lg p-6 md:p-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-6">
                Multi-City Support
              </h2>
              <div className="grid grid-cols-3 gap-4">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-blue-600 font-bold">SF</span>
                  </div>
                  <p className="font-medium text-gray-800">San Francisco</p>
                  <p className="text-sm text-gray-600">SFMTA, SFPD</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-green-600 font-bold">LA</span>
                  </div>
                  <p className="font-medium text-gray-800">Los Angeles</p>
                  <p className="text-sm text-gray-600">LAPD, LADOT</p>
                </div>
                <div className="text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-3">
                    <span className="text-purple-600 font-bold">NYC</span>
                  </div>
                  <p className="font-medium text-gray-800">New York City</p>
                  <p className="text-sm text-gray-600">NYPD, NYC DOT</p>
                </div>
              </div>
              <p className="text-sm text-gray-600 mt-6">
                Our system automatically detects your city from the citation
                number format and applies city-specific rules, deadlines, and
                requirements.
              </p>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
