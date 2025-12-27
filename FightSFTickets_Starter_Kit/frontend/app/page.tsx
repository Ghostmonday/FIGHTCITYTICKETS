"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "./lib/appeal-context";
import {
  CALIFORNIA_CITIES,
  getCityDisplayName,
} from "./lib/california-cities";
import LegalDisclaimer from "../components/LegalDisclaimer";

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
  city_mismatch?: boolean;
  selected_city_mismatch_message?: string;
}

export default function Home() {
  const [selectedCity, setSelectedCity] = useState<string>("");
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

    if (!selectedCity) {
      setError("Please select the city where you received the citation");
      return;
    }

    if (!citationNumber.trim()) {
      setError("Please enter a citation number");
      return;
    }

    setIsValidating(true);
    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/96493b5c-15b2-431a-84c8-c85c02fa001b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:62',message:'API Base URL',data:{apiBase,envVar:process.env.NEXT_PUBLIC_API_BASE,fullUrl:`${apiBase}/tickets/validate`},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A'})}).catch(()=>{});
      // #endregion
      const response = await fetch(`${apiBase}/tickets/validate`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          citation_number: citationNumber.trim(),
          license_plate: licensePlate.trim() || null,
          violation_date: violationDate.trim() || null,
          city_id: selectedCity, // Send selected city for validation
        }),
      });

      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/96493b5c-15b2-431a-84c8-c85c02fa001b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:78',message:'Fetch response received',data:{status:response.status,statusText:response.statusText,ok:response.ok,type:response.type,url:response.url},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'B,C,D,E'})}).catch(()=>{});
      // #endregion

      if (!response.ok) {
        // #region agent log
        const errBody = await response.text().catch(() => 'could not read body');
        fetch('http://127.0.0.1:7242/ingest/96493b5c-15b2-431a-84c8-c85c02fa001b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:85',message:'Response not OK',data:{status:response.status,statusText:response.statusText,body:errBody},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'E'})}).catch(()=>{});
        // #endregion
        throw new Error(`Validation failed: ${response.statusText}`);
      }

      const result = await response.json();

      // Check for city mismatch
      if (result.city_id && result.city_id !== selectedCity) {
        result.city_mismatch = true;
        const detectedCity = CALIFORNIA_CITIES.find(
          (c) => c.cityId === result.city_id,
        );
        const selectedCityName = CALIFORNIA_CITIES.find(
          (c) => c.cityId === selectedCity,
        )?.name;
        result.selected_city_mismatch_message = `The citation number appears to be from ${detectedCity?.name || result.city_id}, but you selected ${selectedCityName}. Please verify your selection or citation number.`;
      }

      setValidationResult(result);

      if (result.is_valid && !result.city_mismatch) {
        // Update appeal context with citation info
        updateState({
          citationNumber: result.citation_number,
          cityId: result.city_id || selectedCity,
          sectionId: result.section_id,
          appealDeadlineDays: result.appeal_deadline_days,
        });
      }
    } catch (err) {
      // #region agent log
      fetch('http://127.0.0.1:7242/ingest/96493b5c-15b2-431a-84c8-c85c02fa001b',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'page.tsx:115',message:'Catch block error',data:{errorType:err?.constructor?.name,errorMessage:err instanceof Error ? err.message : String(err),errorStack:err instanceof Error ? err.stack : undefined},timestamp:Date.now(),sessionId:'debug-session',hypothesisId:'A,B,C,D'})}).catch(()=>{});
      // #endregion
      setError(
        err instanceof Error ? err.message : "Failed to validate citation",
      );
    } finally {
      setIsValidating(false);
    }
  };

  const handleStartAppeal = () => {
    if (validationResult?.is_valid && !validationResult.city_mismatch) {
      router.push("/appeal");
    }
  };

  const formatCityName = (cityId: string | null) => {
    if (!cityId) return "Unknown City";
    const city = CALIFORNIA_CITIES.find((c) => c.cityId === cityId);
    return city
      ? getCityDisplayName(city)
      : cityId
          .replace(/us-ca-|-/g, " ")
          .replace(/_/g, " ")
          .split(" ")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" ");
  };

  const formatAgency = (agency: string, sectionId: string | null) => {
    if (sectionId) {
      const sections: Record<string, string> = {
        // San Francisco
        sfmta: "SFMTA (San Francisco Municipal Transportation Agency)",
        sfpd: "SFPD (San Francisco Police Department)",
        sfsu: "SFSU (San Francisco State University)",
        sfmud: "SFMUD (San Francisco Municipal Utility District)",
        // Los Angeles
        lapd: "LAPD (Los Angeles Police Department)",
        ladot: "LADOT (Los Angeles Department of Transportation)",
        ladot_pvb: "LADOT Parking Violations Bureau",
        // New York City
        nypd: "NYPD (New York Police Department)",
        nydot: "NYC DOT (New York City Department of Transportation)",
        // Other cities (add as needed)
        chicago_parking: "Chicago Department of Finance",
        seattle_parking: "Seattle Department of Transportation",
        phoenix_parking: "Phoenix Parking Enforcement",
        denver_parking: "Denver Public Works",
      };
      return sections[sectionId] || `${agency} - ${sectionId}`;
    }
    return agency;
  };

  return (
    <main className="min-h-screen bg-stone-50">
      {/* Legal Disclaimer Banner */}
      <div className="border-b border-gray-400 py-3 px-4 sm:px-6 bg-gray-100">
        <div className="max-w-6xl mx-auto">
          <div className="rounded-lg p-3 shadow-sm bg-white border border-gray-400">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0 mt-0.5">
                <svg
                  className="w-5 h-5 text-gray-700"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z"
                    clipRule="evenodd"
                  />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-base font-semibold mb-1 text-gray-700">
                  Important Legal Notice
                </h3>
                <p className="text-xs leading-relaxed text-gray-700">
                  <strong>
                    FightCityTickets.com does NOT practice law and does NOT
                    provide legal advice.
                  </strong>{" "}
                  We are a document preparation service that helps you
                  articulate and format your own reasons for appealing a parking
                  ticket.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Banner */}
      <div className="py-10 px-4 sm:px-6 bg-gray-100">
        <div className="max-w-4xl mx-auto text-center">
          <h1 className="text-3xl sm:text-4xl md:text-5xl font-light mb-4 tracking-tight text-gray-700">
            Keep Your Money. Get Your Ticket Dismissed.
          </h1>
          <p className="text-lg sm:text-xl mb-6 font-light text-gray-700">
            Stop paying unfair parking tickets. Get them dismissed and keep your
            hard-earned money.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-6 text-sm sm:text-base text-gray-700">
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Keep hundreds of dollars</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>No points on your record</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Protect your insurance rates</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 sm:p-6 md:p-8">
        {/* Header */}
        <div className="text-center mb-10 sm:mb-12">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-light mb-3 sm:mb-4 tracking-tight text-gray-700">
            Stop Paying Unfair Parking Tickets
          </h2>
          <p className="text-lg sm:text-xl max-w-2xl mx-auto px-2 mb-4 font-light text-gray-700">
            Get your ticket dismissed. Keep your money. Protect your record.
          </p>
          <p className="text-base sm:text-lg max-w-2xl mx-auto px-2 font-light text-gray-700">
            In just 5 minutes, you can appeal your parking ticket and
            potentially save hundreds of dollars.
            <strong className="font-normal">
              {" "}
              No legal knowledge needed. No complicated forms. Just results.
            </strong>
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* Left Column: Citation Form */}
          <div className="rounded-xl shadow-lg p-6 md:p-8 border bg-gray-100 border-gray-400">
            <h2 className="text-xl font-medium mb-6 text-gray-700">
              Check Your Citation
            </h2>

            <form onSubmit={handleValidateCitation} className="space-y-5">
              {/* City Selection Dropdown */}
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">
                  City Where Citation Was Issued *
                </label>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="w-full px-4 py-3 rounded-lg transition bg-white border border-gray-400 text-gray-700 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-400"
                  required
                  disabled={isValidating}
                >
                  <option value="">Select a city...</option>
                  {CALIFORNIA_CITIES.map((city) => (
                    <option key={city.cityId} value={city.cityId}>
                      {getCityDisplayName(city)}
                    </option>
                  ))}
                </select>
                <p className="mt-2 text-xs text-gray-400">
                  Select the city where you received the parking citation.
                </p>
              </div>

              {/* Citation Number */}
              <div>
                <label className="block text-sm font-medium mb-2 text-gray-700">
                  Citation Number *
                </label>
                <input
                  type="text"
                  value={citationNumber}
                  onChange={(e) => setCitationNumber(e.target.value)}
                  placeholder="e.g., 912345678, LA123456, 1234567"
                  className="w-full px-4 py-3 rounded-lg transition bg-white border border-gray-400 text-gray-700 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-400"
                  required
                  disabled={isValidating}
                />
                <p className="mt-2 text-xs text-gray-400">
                  Enter your citation number exactly as it appears on your
                  ticket.
                </p>
              </div>

              {/* Optional Fields */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700">
                    License Plate (Optional)
                  </label>
                  <input
                    type="text"
                    value={licensePlate}
                    onChange={(e) =>
                      setLicensePlate(e.target.value.toUpperCase())
                    }
                    placeholder="e.g., ABC123"
                    className="w-full px-4 py-3 rounded-lg transition bg-white border border-gray-400 text-gray-700 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-400"
                    disabled={isValidating}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-gray-700">
                    Violation Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={violationDate}
                    onChange={(e) => setViolationDate(e.target.value)}
                    className="w-full px-4 py-3 rounded-lg transition bg-white border border-gray-400 text-gray-700 focus:border-gray-500 focus:outline-none focus:ring-1 focus:ring-gray-400"
                    disabled={isValidating}
                  />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="px-4 py-3 rounded-lg text-sm bg-red-50 border border-red-200 text-red-700">
                  {error}
                </div>
              )}

              {/* City Mismatch Warning */}
              {validationResult?.city_mismatch && (
                <div className="px-4 py-3 rounded-lg text-sm bg-yellow-50 border border-yellow-300 text-yellow-800">
                  <div className="flex items-start gap-2">
                    <svg
                      className="w-5 h-5 mt-0.5 flex-shrink-0"
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
                      <p className="font-medium mb-1">Citation City Mismatch</p>
                      <p>{validationResult.selected_city_mismatch_message}</p>
                    </div>
                  </div>
                </div>
              )}

              {/* Submit Button */}
              <button
                type="submit"
                disabled={
                  isValidating || !citationNumber.trim() || !selectedCity
                }
                className={`w-full py-3 px-4 rounded-lg font-medium transition shadow-sm ${
                  isValidating
                    ? "bg-gray-300 text-gray-500 cursor-not-allowed"
                    : "bg-gray-400 text-white hover:bg-gray-500"
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
              <div className="rounded-xl shadow-lg p-6 md:p-8 border bg-gray-100 border-gray-400">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-medium text-gray-700">
                    Validation Results
                  </h2>
                  <div
                    className={`px-3 py-1 rounded-full text-xs font-medium ${
                      validationResult.is_valid &&
                      !validationResult.city_mismatch
                        ? validationResult.is_urgent
                          ? "bg-yellow-100 text-yellow-800"
                          : "bg-green-100 text-green-800"
                        : "bg-red-100 text-red-800"
                    }`}
                  >
                    {validationResult.is_valid &&
                    !validationResult.city_mismatch
                      ? validationResult.is_urgent
                        ? "URGENT"
                        : "VALID"
                      : "INVALID"}
                  </div>
                </div>

                {validationResult.is_valid &&
                !validationResult.city_mismatch ? (
                  <div className="space-y-6">
                    {/* Citation Info */}
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-xs mb-1 text-gray-400">
                          Citation Number
                        </p>
                        <p className="font-medium text-base text-gray-700">
                          {validationResult.formatted_citation ||
                            validationResult.citation_number}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs mb-1 text-gray-400">City</p>
                        <p className="font-medium text-base text-gray-700">
                          {formatCityName(
                            validationResult.city_id || selectedCity,
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs mb-1 text-gray-400">Agency</p>
                        <p className="font-medium text-sm text-gray-700">
                          {formatAgency(
                            validationResult.agency,
                            validationResult.section_id,
                          )}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs mb-1 text-gray-400">Deadline</p>
                        <p className="font-medium text-sm text-gray-700">
                          {validationResult.days_remaining !== null
                            ? `${validationResult.days_remaining} days`
                            : "Check date"}
                        </p>
                      </div>
                    </div>

                    {/* Special Requirements */}
                    {validationResult.phone_confirmation_required && (
                      <div className="rounded-lg p-3 bg-blue-50 border border-blue-200">
                        <div className="flex items-start">
                          <svg
                            className="w-4 h-4 mt-0.5 mr-2 text-blue-700"
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
                            <p className="font-medium text-sm text-blue-800">
                              Phone Confirmation Required
                            </p>
                            <p className="text-xs mt-1 text-blue-700">
                              This citation section requires phone confirmation
                              before appeal submission. We&apos;ll guide you through
                              this process.
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Deadline Warning */}
                    {validationResult.is_urgent && (
                      <div className="rounded-lg p-3 bg-yellow-50 border border-yellow-300">
                        <div className="flex items-start">
                          <svg
                            className="w-4 h-4 mt-0.5 mr-2 text-yellow-800"
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
                            <p className="font-medium text-sm text-yellow-800">
                              Urgent Deadline
                            </p>
                            <p className="text-xs mt-1 text-yellow-700">
                              Your appeal deadline is approaching! You have{" "}
                              {validationResult.days_remaining} day(s)
                              remaining.
                            </p>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* Legal Disclaimer */}
                    <LegalDisclaimer variant="compact" className="mb-4" />

                    {/* Start Appeal Button */}
                    <button
                      onClick={handleStartAppeal}
                      className="w-full py-3 px-6 rounded-lg font-medium transition shadow-sm bg-gray-400 text-white hover:bg-gray-500"
                    >
                      Get My Ticket Dismissed →
                    </button>
                  </div>
                ) : (
                  <div className="text-center py-6">
                    <div className="mb-3 text-red-600">
                      <svg
                        className="w-10 h-10 mx-auto"
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
                    <p className="text-sm text-gray-700">
                      {validationResult.error_message ||
                        "Invalid citation number format."}
                    </p>
                    <p className="text-xs mt-2 text-gray-400">
                      Please check your citation number and try again.
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* What You Get */}
            <div className="rounded-xl shadow-lg p-6 md:p-8 border bg-gray-100 border-gray-400">
              <h2 className="text-xl font-medium mb-6 text-gray-700">
                What Happens When You Appeal
              </h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mt-0.5 bg-gray-400">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-sm text-gray-700">
                      You Keep Your Money
                    </h3>
                    <p className="text-sm text-gray-700">
                      Save $50-$500+ per ticket. That&apos;s money back in your
                      pocket.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mt-0.5 bg-gray-400">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-sm text-gray-700">
                      Your Record Stays Clean
                    </h3>
                    <p className="text-sm text-gray-700">
                      No points. No insurance rate increases. No future
                      consequences.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center mt-0.5 bg-gray-400">
                    <svg
                      className="w-4 h-4 text-white"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div>
                    <h3 className="font-medium text-sm text-gray-700">
                      You Get Peace of Mind
                    </h3>
                    <p className="text-sm text-gray-700">
                      Stop worrying about unfair tickets. Take control and fight
                      back.
                    </p>
                  </div>
                </div>
              </div>
              <div className="mt-6 p-3 rounded-lg border bg-white border-gray-400">
                <p className="text-xs text-gray-700">
                  <strong className="text-gray-700">The math is simple:</strong>{" "}
                  If you pay a $100 ticket, you lose $100. If you appeal and
                  win, you keep $100. The cost to appeal is a fraction of what
                  you save.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  );
}
