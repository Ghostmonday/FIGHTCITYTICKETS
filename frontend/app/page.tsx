"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "./lib/appeal-context";
import LegalDisclaimer from "../components/LegalDisclaimer";

// Force dynamic rendering - this page uses client-side context
export const dynamic = "force-dynamic";

interface City {
  cityId: string;
  name: string;
  agency: string;
  sectionId?: string;
  appealDeadlineDays: number;
}

const CITIES: City[] = [
  { cityId: "sf", name: "San Francisco", agency: "sf", appealDeadlineDays: 21 },
  { cityId: "la", name: "Los Angeles", agency: "la", appealDeadlineDays: 21 },
  {
    cityId: "nyc",
    name: "New York City",
    agency: "nyc",
    appealDeadlineDays: 30,
  },
  {
    cityId: "chicago",
    name: "Chicago",
    agency: "chicago",
    appealDeadlineDays: 20,
  },
  {
    cityId: "seattle",
    name: "Seattle",
    agency: "seattle",
    appealDeadlineDays: 20,
  },
  {
    cityId: "denver",
    name: "Denver",
    agency: "denver",
    appealDeadlineDays: 20,
  },
  {
    cityId: "portland",
    name: "Portland",
    agency: "portland",
    appealDeadlineDays: 10,
  },
  {
    cityId: "phoenix",
    name: "Phoenix",
    agency: "phoenix",
    appealDeadlineDays: 15,
  },
];

export default function Home() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [selectedCity, setSelectedCity] = useState("");
  const [citationNumber, setCitationNumber] = useState("");
  const [licensePlate, setLicensePlate] = useState("");
  const [violationDate, setViolationDate] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<{
    valid: boolean;
    citationId: string;
    detectedCity: string;
    selectedCityName: string;
    cityId: string;
    sectionId: string;
    appealDeadlineDays: number;
  } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const getCityDisplayName = (city: City): string => {
    return `${city.name} (${city.agency.toUpperCase()})`;
  };

  const handleValidateCitation = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setValidationResult(null);
    setIsValidating(true);

    const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

    try {
      const response = await fetch(`${apiBase}/api/citations/validate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          citation_number: citationNumber,
          license_plate: licensePlate || undefined,
          violation_date: violationDate || undefined,
          city_id: selectedCity,
        }),
      });

      const data = await response.json();

      if (!response.ok || !data.valid) {
        setError(
          data.error ||
            "We could not validate this citation. Please check the number and try again."
        );
        setIsValidating(false);
        return;
      }

      const detectedCity = CITIES.find((c) => c.cityId === selectedCity);
      const selectedCityName = detectedCity
        ? getCityDisplayName(detectedCity)
        : "Unknown City";

      // Store in context
      updateState({
        citationNumber: citationNumber,
        licensePlate: licensePlate,
        violationDate: violationDate,
        cityId: selectedCity,
        sectionId: detectedCity?.sectionId,
        appealDeadlineDays: detectedCity?.appealDeadlineDays,
      });

      setValidationResult({
        valid: true,
        citationId: data.citation_id,
        detectedCity: data.detected_city || selectedCity,
        selectedCityName,
        cityId: selectedCity,
        sectionId: detectedCity?.sectionId || "",
        appealDeadlineDays: detectedCity?.appealDeadlineDays || 21,
      });
    } catch (err) {
      setError(
        "We could not validate this citation. Please check the number and try again."
      );
    } finally {
      setIsValidating(false);
    }
  };

  const handleStartAppeal = () => {
    if (validationResult) {
      updateState({
        citationNumber: validationResult.citationId,
        cityId: validationResult.cityId,
        sectionId: validationResult.sectionId,
        appealDeadlineDays: validationResult.appealDeadlineDays,
      });
      router.push("/appeal");
    }
  };

  const formatAgency = (agency: string): string => {
    const agencies: Record<string, { name: string; sectionId: string }> = {
      sfmta: { name: "SFMTA", sectionId: "parking" },
      sfpd: { name: "SF Police", sectionId: "traffic" },
      sfsu: { name: "SFSU Police", sectionId: "parking" },
      sfmud: { name: "SF Municipal", sectionId: "utilities" },
      lapd: { name: "LAPD", sectionId: "parking" },
      ladot: { name: "LA DOT", sectionId: "parking" },
      nyc: { name: "NYC Finance", sectionId: "parking" },
      nypd: { name: "NY Police", sectionId: "traffic" },
      chicago: {
        name: "Chicago Finance",
        sectionId: "parking",
      },
      seattle: {
        name: "Seattle DOT",
        sectionId: "parking",
      },
      denver: {
        name: "Denver Public Works",
        sectionId: "parking",
      },
      portland: {
        name: "Portland Transportation",
        sectionId: "parking",
      },
    };
    return agencies[agency.toLowerCase()]?.name || agency;
  };

  return (
    <main
      className="min-h-screen"
      style={{
        background: "linear-gradient(180deg, #faf8f5 0%, #f5f2ed 100%)",
      }}
    >
      {/* Hero Banner */}
      <div
        className="py-16 sm:py-20 px-4 sm:px-6"
        style={{
          background:
            "linear-gradient(180deg, #f7f3ed 0%, #efe9df 40%, #e9e2d6 100%)",
        }}
      >
        <div className="max-w-3xl mx-auto text-center">
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extralight mb-6 tracking-tight text-stone-800 leading-tight">
            They Demand Perfection.
            <br className="hidden sm:block" /> We Deliver It.
          </h1>
          <p className="text-xl sm:text-2xl mb-3 font-light text-stone-500 max-w-xl mx-auto tracking-wide">
            A parking citation is a procedural document.
          </p>
          <p className="text-lg sm:text-xl text-stone-600 max-w-xl mx-auto mb-6">
            Municipalities win through clerical precision.
            <br className="hidden sm:block" />
            <span className="font-normal text-stone-700">
              We make their weapon our shield.
            </span>
          </p>

          {/* Civil Shield Disclaimer */}
          <p className="text-sm text-stone-500 font-medium mb-6">
            <strong>
              We aren&apos;t lawyers. We&apos;re paperwork experts.
            </strong>{" "}
            And in a bureaucracy, paperwork is power.
          </p>

          {/* Social Proof & Trust Badges */}
          <div className="flex flex-wrap items-center justify-center gap-6 mb-8 text-sm text-stone-500">
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-stone-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Procedural Compliance Engine</span>
            </div>
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-stone-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <span>USPS Certified</span>
            </div>
            <div className="flex items-center gap-2">
              <svg
                className="w-5 h-5 text-stone-600"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path
                  fillRule="evenodd"
                  d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Court-Ready Documents</span>
            </div>
          </div>

          {/* Pricing Badge */}
          <div className="inline-flex items-center gap-8 px-8 py-4 rounded-full bg-white/60 backdrop-blur-sm border border-stone-200/80 shadow-sm">
            <div className="text-center">
              <span className="text-3xl sm:text-4xl font-light text-stone-800">
                $19
              </span>
            </div>
            <div className="h-8 w-px bg-stone-200"></div>
            <div className="text-center">
              <span className="text-lg text-stone-600">5 minutes</span>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto p-4 sm:p-6 md:p-8 pt-12 sm:pt-16">
        {/* Header */}
        <div className="text-center mb-12 sm:mb-16">
          <h2 className="text-2xl sm:text-3xl md:text-4xl font-extralight mb-4 tracking-tight text-stone-700">
            Your Submission, Procedurally Compliant
          </h2>
          <p className="text-base sm:text-lg max-w-lg mx-auto font-light text-stone-500">
            The Clerical Engine™ ensures your appeal meets the exacting
            standards municipalities use to reject citizen submissions.
          </p>
        </div>

        <div className="grid md:grid-cols-2 gap-10">
          {/* Left Column: Citation Form */}
          <div className="rounded-2xl shadow-sm p-6 md:p-8 bg-white border border-stone-100">
            <h2 className="text-lg font-medium mb-6 text-stone-700 tracking-wide">
              Validate Your Citation
            </h2>

            <form onSubmit={handleValidateCitation} className="space-y-5">
              {/* City Selection Dropdown */}
              <div>
                <label className="block text-sm font-medium mb-2 text-stone-600 tracking-wide">
                  City Where Citation Was Issued *
                </label>
                <select
                  value={selectedCity}
                  onChange={(e) => setSelectedCity(e.target.value)}
                  className="w-full px-4 py-3.5 rounded-xl transition bg-stone-50/50 border border-stone-200 text-stone-700 focus:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-100 focus:bg-white"
                  required
                  disabled={isValidating}
                >
                  <option value="">Select a city...</option>
                  {CITIES.sort((a, b) => a.name.localeCompare(b.name)).map(
                    (city) => (
                      <option key={city.cityId} value={city.cityId}>
                        {getCityDisplayName(city)}
                      </option>
                    )
                  )}
                </select>
                <p className="mt-2 text-xs text-stone-400">
                  Select the city where you received the parking citation.
                </p>
              </div>

              {/* Citation Number */}
              <div>
                <label className="block text-sm font-medium mb-2 text-stone-600 tracking-wide">
                  Citation Number *
                </label>
                <input
                  type="text"
                  value={citationNumber}
                  onChange={(e) => setCitationNumber(e.target.value)}
                  placeholder="e.g., 912345678, LA123456, 1234567"
                  className="w-full px-4 py-3.5 rounded-xl transition bg-stone-50/50 border border-stone-200 text-stone-700 focus:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-100 focus:bg-white"
                  required
                  disabled={isValidating}
                />
                <p className="mt-2 text-xs text-stone-400">
                  Enter your citation number exactly as it appears on your
                  ticket.
                </p>
              </div>

              {/* Optional Fields */}
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2 text-stone-600 tracking-wide">
                    License Plate (Optional)
                  </label>
                  <input
                    type="text"
                    value={licensePlate}
                    onChange={(e) =>
                      setLicensePlate(e.target.value.toUpperCase())
                    }
                    placeholder="e.g., ABC123"
                    className="w-full px-4 py-3.5 rounded-xl transition bg-stone-50/50 border border-stone-200 text-stone-700 focus:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-100 focus:bg-white"
                    disabled={isValidating}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2 text-stone-600 tracking-wide">
                    Violation Date (Optional)
                  </label>
                  <input
                    type="date"
                    value={violationDate}
                    onChange={(e) => setViolationDate(e.target.value)}
                    className="w-full px-4 py-3.5 rounded-xl transition bg-stone-50/50 border border-stone-200 text-stone-700 focus:border-stone-300 focus:outline-none focus:ring-2 focus:ring-stone-100 focus:bg-white"
                    disabled={isValidating}
                  />
                </div>
              </div>

              {/* Error Message */}
              {error && (
                <div className="p-4 bg-red-50 border border-red-200 rounded-xl">
                  <p className="text-sm text-red-700">{error}</p>
                </div>
              )}

              {/* Validation Result */}
              {validationResult && (
                <div className="p-4 bg-green-50 border border-green-200 rounded-xl">
                  <div className="flex items-center gap-2 mb-2">
                    <svg
                      className="w-5 h-5 text-green-600"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                    <span className="font-medium text-green-800">
                      Citation Validated
                    </span>
                  </div>
                  <p className="text-sm text-green-700">
                    <strong>
                      {formatAgency(validationResult.detectedCity)}
                    </strong>{" "}
                    will process your appeal.
                  </p>
                  <p className="text-xs text-green-600 mt-1">
                    Deadline: {validationResult.appealDeadlineDays} days from
                    violation date
                  </p>
                </div>
              )}

              {/* Buttons */}
              <div className="flex gap-3 pt-2">
                {!validationResult ? (
                  <button
                    type="submit"
                    disabled={isValidating}
                    className="flex-1 bg-stone-800 text-white px-6 py-3.5 rounded-xl font-medium hover:bg-stone-900 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {isValidating ? (
                      <span className="flex items-center justify-center gap-2">
                        <svg
                          className="animate-spin h-5 w-5"
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
                      "Validate Citation →"
                    )}
                  </button>
                ) : (
                  <button
                    type="button"
                    onClick={handleStartAppeal}
                    className="flex-1 bg-stone-800 text-white px-6 py-3.5 rounded-xl font-medium hover:bg-stone-900 transition"
                  >
                    Begin Appeal →
                  </button>
                )}
              </div>
            </form>
          </div>

          {/* Right Column: How It Works */}
          <div className="space-y-6">
            <h2 className="text-lg font-medium mb-4 text-stone-700 tracking-wide">
              Procedural Compliance Process
            </h2>

            {/* Step 1 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-stone-100 rounded-full flex items-center justify-center text-stone-600 font-medium">
                1
              </div>
              <div>
                <h3 className="font-medium text-stone-800 mb-1">
                  The Clerical Engine™ Scans
                </h3>
                <p className="text-sm text-stone-600">
                  We analyze your citation for procedural defects, timing
                  errors, and clerical flaws municipalities use to reject
                  appeals.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-stone-100 rounded-full flex items-center justify-center text-stone-600 font-medium">
                2
              </div>
              <div>
                <h3 className="font-medium text-stone-800 mb-1">
                  Your Statement Is Articulated
                </h3>
                <p className="text-sm text-stone-600">
                  We transform your description into professionally formatted,
                  procedurally compliant language.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-stone-100 rounded-full flex items-center justify-center text-stone-600 font-medium">
                3
              </div>
              <div>
                <h3 className="font-medium text-stone-800 mb-1">
                  Court-Ready Documents Generated
                </h3>
                <p className="text-sm text-stone-600">
                  Your submission includes all required elements for due
                  process: signature, date, citation number, and statement.
                </p>
              </div>
            </div>

            {/* Step 4 */}
            <div className="flex gap-4">
              <div className="flex-shrink-0 w-8 h-8 bg-stone-100 rounded-full flex items-center justify-center text-stone-600 font-medium">
                4
              </div>
              <div>
                <h3 className="font-medium text-stone-800 mb-1">
                  Certified Mailing
                </h3>
                <p className="text-sm text-stone-600">
                  Your appeal is mailed via USPS Certified with tracking, with
                  delivery confirmation for your records.
                </p>
              </div>
            </div>

            {/* Trust Badges */}
            <div className="pt-6 mt-6 border-t border-stone-200">
              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-center gap-2 text-sm text-stone-600">
                  <svg
                    className="w-4 h-4 text-stone-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Secure Payment</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-stone-600">
                  <svg
                    className="w-4 h-4 text-stone-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>Document Prep</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-stone-600">
                  <svg
                    className="w-4 h-4 text-stone-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>No Legal Advice</span>
                </div>
                <div className="flex items-center gap-2 text-sm text-stone-600">
                  <svg
                    className="w-4 h-4 text-stone-500"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path
                      fillRule="evenodd"
                      d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                      clipRule="evenodd"
                    />
                  </svg>
                  <span>5-Minute Process</span>
                </div>
              </div>
            </div>

            {/* Disclaimer */}
            <div className="pt-4">
              <LegalDisclaimer variant="compact" />
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-stone-200 py-8 px-4">
        <div className="max-w-4xl mx-auto flex flex-col sm:flex-row justify-between items-center gap-4 text-sm text-stone-500">
          <p>© 2025 FightCityTickets.com</p>
          <div className="flex gap-6">
            <Link href="/terms" className="hover:text-stone-800 transition">
              Terms
            </Link>
            <Link href="/privacy" className="hover:text-stone-800 transition">
              Privacy
            </Link>
            <Link
              href="/what-we-are"
              className="hover:text-stone-800 transition"
            >
              What We Are
            </Link>
          </div>
        </div>
      </footer>
    </main>
  );
}
