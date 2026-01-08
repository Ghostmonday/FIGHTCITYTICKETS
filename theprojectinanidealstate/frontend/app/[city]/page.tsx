"use client";

import { useParams, useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import Link from "next/link";
import { getCityBySlug, CITY_SLUG_MAP } from "../lib/city-routing";
import LegalDisclaimer from "../../components/LegalDisclaimer";

// City data mapping - will be enhanced with actual city registry data
const CITY_DATA = {
  sf: {
    name: "San Francisco",
    state: "CA",
    fullName: "San Francisco, California",
    agencies: ["SFMTA", "SFPD", "SFSU"],
    citationPatterns: ["9XXXXXXXX (9 digits)", "SFXXXXXX (SF + 6 digits)"],
    appealDeadlineDays: 21,
    color: "blue",
    description: "Fight San Francisco parking tickets with automated appeals",
  },
  nyc: {
    name: "New York City",
    state: "NY",
    fullName: "New York City, New York",
    agencies: ["NYPD", "NYC DOT"],
    citationPatterns: ["XXXXXXXXXX (10 digits)"],
    appealDeadlineDays: 30,
    color: "purple",
    description: "Challenge NYC parking violations with our streamlined system",
  },
  la: {
    name: "Los Angeles",
    state: "CA",
    fullName: "Los Angeles, California",
    agencies: ["LAPD", "LADOT"],
    citationPatterns: ["XXXXXXXXXXX (11 alphanumeric)"],
    appealDeadlineDays: 21,
    color: "green",
    description: "Appeal Los Angeles parking citations efficiently",
  },
  san_diego: {
    name: "San Diego",
    state: "CA",
    fullName: "San Diego, California",
    agencies: ["SDPD", "San Diego Parking"],
    citationPatterns: ["XXXXXX (6-8 digits)"],
    appealDeadlineDays: 21,
    color: "orange",
    description: "Dispute San Diego parking tickets with confidence",
  },
  chicago: {
    name: "Chicago",
    state: "IL",
    fullName: "Chicago, Illinois",
    agencies: ["Chicago DOF"],
    citationPatterns: ["XXXXXXXXXX (10 digits)"],
    appealDeadlineDays: 21,
    color: "red",
    description: "Contest Chicago parking and camera citations",
  },
  dallas: {
    name: "Dallas",
    state: "TX",
    fullName: "Dallas, Texas",
    agencies: ["Dallas Parking"],
    citationPatterns: ["XXXXXX (6-8 digits)"],
    appealDeadlineDays: 20,
    color: "blue",
    description: "Fight Dallas parking violations effectively",
  },
  houston: {
    name: "Houston",
    state: "TX",
    fullName: "Houston, Texas",
    agencies: ["Houston Parking"],
    citationPatterns: ["XXXXXX (6-8 digits)"],
    appealDeadlineDays: 20,
    color: "green",
    description: "Appeal Houston parking tickets with ease",
  },
  seattle: {
    name: "Seattle",
    state: "WA",
    fullName: "Seattle, Washington",
    agencies: ["Seattle DOT"],
    citationPatterns: ["XXXXXX (6-8 digits)"],
    appealDeadlineDays: 15,
    color: "emerald",
    description: "Challenge Seattle parking citations professionally",
  },
  philadelphia: {
    name: "Philadelphia",
    state: "PA",
    fullName: "Philadelphia, Pennsylvania",
    agencies: ["Philadelphia Parking"],
    citationPatterns: ["XXXXXX (6-8 digits)"],
    appealDeadlineDays: 30,
    color: "blue",
    description: "Dispute Philadelphia parking violations successfully",
  },
  washington: {
    name: "Washington, DC",
    state: "DC",
    fullName: "Washington, District of Columbia",
    agencies: ["DC DPW"],
    citationPatterns: ["XXXXXX (6-8 digits)"],
    appealDeadlineDays: 60,
    color: "red",
    description: "Appeal Washington, DC parking tickets with our help",
  },
};

const COLOR_CLASSES: Record<string, string> = {
  blue: "bg-blue-100 text-blue-800",
  purple: "bg-purple-100 text-purple-800",
  green: "bg-green-100 text-green-800",
  orange: "bg-orange-100 text-orange-800",
  red: "bg-red-100 text-red-800",
  emerald: "bg-emerald-100 text-emerald-800",
};

export default function CityPage() {
  const params = useParams();
  const router = useRouter();
  const [citationNumber, setCitationNumber] = useState("");
  const [isValidating, setIsValidating] = useState(false);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [detectedCitySlug, setDetectedCitySlug] = useState<string | null>(null);

  // Detect subdomain on client side
  useEffect(() => {
    if (typeof window !== "undefined") {
      const hostname = window.location.hostname;
      const subdomain = hostname.split(".")[0]?.toLowerCase();

      // Map subdomain to city slug
      const subdomainMap: Record<string, string> = {
        sf: "SF",
        sanfrancisco: "SF",
        sd: "SD",
        sandiego: "SD",
        nyc: "NYC",
        newyork: "NYC",
        la: "LA",
        losangeles: "LA",
        sj: "SJ",
        sanjose: "SJ",
        chi: "CHI",
        chicago: "CHI",
        sea: "SEA",
        seattle: "SEA",
        phx: "PHX",
        phoenix: "PHX",
        den: "DEN",
        denver: "DEN",
        dal: "DAL",
        dallas: "DAL",
        hou: "HOU",
        houston: "HOU",
        phi: "PHI",
        philadelphia: "PHI",
        pdx: "PDX",
        portland: "PDX",
        slc: "SLC",
        saltlake: "SLC",
      };

      if (
        subdomain &&
        subdomainMap[subdomain] &&
        subdomain !== "www" &&
        !hostname.includes("localhost")
      ) {
        setDetectedCitySlug(subdomainMap[subdomain]);
      }
    }
  }, []);

  const citySlugParam =
    detectedCitySlug || ((params?.city as string) || "").toUpperCase();

  // Get city mapping from slug (handles SF, SD, NYC, etc.)
  const cityMapping = getCityBySlug(citySlugParam);

  // Get city data - try slug first, then fallback to internal ID
  const citySlug = cityMapping?.internalId || citySlugParam.toLowerCase();
  const cityData = CITY_DATA[citySlug as keyof typeof CITY_DATA] ||
    CITY_DATA[cityMapping?.internalId as keyof typeof CITY_DATA] || {
      name:
        cityMapping?.name ||
        citySlugParam
          .split("_")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" "),
      state: cityMapping?.state || "",
      fullName:
        cityMapping?.name ||
        citySlugParam
          .split("_")
          .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
          .join(" "),
      agencies: ["Local Parking Authority"],
      citationPatterns: ["Check your citation format"],
      appealDeadlineDays: 21,
      color: "gray",
      description: `Fight parking tickets in ${cityMapping?.name || citySlugParam}`,
    };

  const cityColor = cityData.color in COLOR_CLASSES ? cityData.color : "gray";
  const bgColorClass = COLOR_CLASSES[cityColor] || "bg-gray-100 text-gray-800";

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
          city_id: cityMapping?.cityId || `us-${citySlug}`.replace(/_/g, "-"),
        }),
      });

      if (!response.ok) {
        throw new Error(`Validation failed: ${response.statusText}`);
      }

      const result = await response.json();
      setValidationResult(result);

      if (result.is_valid) {
        // Redirect to appeal flow with city context
        const redirectSlug = cityMapping?.slug || citySlug;
        window.location.href = `/appeal?city=${redirectSlug}&citation=${encodeURIComponent(citationNumber.trim())}`;
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
      const redirectSlug = cityMapping?.slug || citySlug;
      const cityId = validationResult.city_id || redirectSlug;
      router.push(
        `/appeal?city=${encodeURIComponent(cityId)}&citation=${encodeURIComponent(citationNumber.trim())}`,
      );
    }
  };

  // Format city slug for display
  const formattedCityName = citySlug
    .split("_")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(" ");

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      {/* Navigation */}
      <nav className="bg-white/95 backdrop-blur-md shadow-sm border-b border-gray-100 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-3 sm:px-4 lg:px-8">
          <div className="flex justify-between items-center h-14 sm:h-16">
            <div className="flex items-center min-w-0 flex-1">
              <Link
                href="/"
                className="text-lg sm:text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent hover:from-blue-700 hover:to-purple-700 transition-all truncate"
              >
                FightCityTickets
              </Link>
              <div className="ml-2 sm:ml-6 flex items-center space-x-2 sm:space-x-3 min-w-0">
                <span className="text-gray-400 text-xs sm:text-sm hidden sm:inline">
                  /
                </span>
                <span
                  className={`px-2 py-1 sm:px-3 sm:py-1.5 rounded-full text-xs sm:text-sm font-semibold ${bgColorClass} shadow-sm truncate max-w-[120px] sm:max-w-none`}
                >
                  <span className="hidden sm:inline">{cityData.fullName}</span>
                  <span className="sm:hidden">{cityData.name}</span>
                </span>
              </div>
            </div>
            <div className="flex items-center flex-shrink-0">
              <Link
                href="/"
                className="text-gray-600 hover:text-gray-900 px-2 sm:px-4 py-2 rounded-lg text-xs sm:text-sm font-medium hover:bg-gray-100 transition-colors whitespace-nowrap"
              >
                <span className="hidden sm:inline">All Cities</span>
                <span className="sm:hidden">Cities</span>
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Transformation Banner - What You Get */}
      <div className="bg-gradient-to-r from-green-600 via-emerald-600 to-teal-700 text-white py-6 px-4 sm:px-6">
        <div className="max-w-7xl mx-auto text-center">
          <h2 className="text-2xl sm:text-3xl font-extrabold mb-3">
            Get Your {cityData.name} Parking Ticket Dismissed
          </h2>
          <p className="text-lg sm:text-xl text-green-100 mb-4 font-medium">
            Stop paying unfair tickets. Keep your money. Protect your record.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4 text-sm sm:text-base">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M8.433 7.418c.155-.103.346-.196.567-.267v1.698a2.305 2.305 0 01-.567-.267C8.07 8.34 8 8.114 8 8c0-.114.07-.34.433-.582zM11 12.849v-1.698c.22.071.412.164.567.267.364.243.433.468.433.582 0 .114-.07.34-.433.582a2.305 2.305 0 01-.567.267z" />
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-13a1 1 0 10-2 0v.092a4.535 4.535 0 00-1.676.662C6.602 6.234 6 7.009 6 8c0 .99.602 1.765 1.324 2.246.48.32 1.054.545 1.676.662v1.941c-.391-.127-.68-.317-.843-.504a1 1 0 10-1.51 1.31c.562.649 1.413 1.076 2.353 1.253V15a1 1 0 102 0v-.092a4.535 4.535 0 001.676-.662C13.398 13.766 14 12.991 14 12c0-.99-.602-1.765-1.324-2.246A4.535 4.535 0 0011 9.092V7.151c.391.127.68.317.843.504a1 1 0 101.511-1.31c-.563-.649-1.413-1.076-2.354-1.253V5z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Save $50-$500+ per ticket</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>No insurance rate increases</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path
                  fillRule="evenodd"
                  d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                  clipRule="evenodd"
                />
              </svg>
              <span>Clean driving record</span>
            </div>
          </div>
        </div>
      </div>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 sm:py-12 md:py-16">
        <div className="text-center">
          <div className="inline-block mb-4">
            <span
              className={`px-3 py-1.5 sm:px-4 sm:py-2 rounded-full text-xs sm:text-sm font-semibold ${bgColorClass} shadow-sm`}
            >
              {cityData.state} • {cityData.appealDeadlineDays} Day Appeal Window
            </span>
          </div>
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl lg:text-7xl mb-4 sm:mb-6 leading-tight">
            Get Your{" "}
            <span className="bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              {cityData.name}
            </span>{" "}
            Parking Ticket Dismissed
          </h1>
          <p className="mt-3 max-w-3xl mx-auto text-lg sm:text-xl md:text-2xl text-gray-700 sm:mt-4 sm:mt-6 leading-relaxed px-2 font-semibold">
            Stop paying unfair tickets. Keep your money. Protect your record.
          </p>
          <p className="mt-4 max-w-2xl mx-auto text-base sm:text-lg text-gray-600 leading-relaxed px-2">
            Every ticket you pay is money you'll never see again. Appeal now and
            potentially save hundreds of dollars.
          </p>
        </div>

        <div className="mt-8 sm:mt-12 md:mt-16 grid grid-cols-1 lg:grid-cols-2 gap-6 sm:gap-8">
          {/* Left Column: Citation Validation */}
          <div className="bg-white rounded-xl sm:rounded-2xl shadow-xl border border-gray-100 p-5 sm:p-6 md:p-8 hover:shadow-2xl transition-shadow duration-300">
            <div className="flex items-center mb-4 sm:mb-6">
              <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mr-3 sm:mr-4 shadow-lg flex-shrink-0">
                <svg
                  className="w-5 h-5 sm:w-6 sm:h-6 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
              </div>
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900">
                Start Your Appeal
              </h2>
            </div>
            <p className="text-sm sm:text-base text-gray-600 mb-4 sm:mb-6 -mt-2 sm:mt-0 ml-12 sm:ml-16">
              Enter your citation number below. The entire process takes just
              5-8 minutes.
            </p>

            <form onSubmit={handleValidateCitation}>
              <div className="space-y-4">
                <div>
                  <label
                    htmlFor="citation"
                    className="block text-sm font-medium text-gray-700 mb-2"
                  >
                    Citation Number
                  </label>
                  <input
                    type="text"
                    id="citation"
                    value={citationNumber}
                    onChange={(e) => setCitationNumber(e.target.value)}
                    placeholder="Enter citation number"
                    className="w-full px-4 py-4 sm:py-3.5 text-base sm:text-sm border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all bg-gray-50 focus:bg-white"
                    disabled={isValidating}
                  />
                  <p className="mt-2 text-xs sm:text-sm text-gray-500">
                    {cityData.citationPatterns.length > 0 ? (
                      <>
                        Common format
                        {cityData.citationPatterns.length > 1 ? "s" : ""}:{" "}
                        {cityData.citationPatterns.join(", ")}
                      </>
                    ) : (
                      "Enter the citation number from your ticket"
                    )}
                  </p>
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                    <p className="text-red-800 text-sm">{error}</p>
                  </div>
                )}

                {validationResult && !validationResult.is_valid && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                    <p className="text-yellow-800 text-sm">
                      {validationResult.error_message ||
                        "Invalid citation format"}
                    </p>
                  </div>
                )}

                <button
                  type="submit"
                  disabled={isValidating || !citationNumber.trim()}
                  className={`w-full py-4 sm:py-4 px-6 rounded-xl font-bold text-base sm:text-lg text-white shadow-lg transition-all transform ${
                    isValidating
                      ? "bg-gray-400 cursor-not-allowed"
                      : "bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 hover:shadow-xl hover:scale-[1.01] active:scale-[0.99]"
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
                    "Continue to Appeal →"
                  )}
                </button>
              </div>
            </form>

            {validationResult?.is_valid && (
              <div className="mt-6 space-y-4">
                <div className="bg-gradient-to-br from-green-50 to-emerald-50 border-2 border-green-200 rounded-2xl p-6 shadow-lg">
                  <div className="flex items-start">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center shadow-lg">
                        <svg
                          className="h-7 w-7 text-white"
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth="3"
                            d="M5 13l4 4L19 7"
                          />
                        </svg>
                      </div>
                    </div>
                    <div className="ml-4 flex-1">
                      <h3 className="text-xl font-bold text-green-900 mb-2">
                        Citation Validated! ✅
                      </h3>
                      <div className="mt-2 text-green-800 space-y-1">
                        <p className="font-medium">
                          Your citation number is valid for {cityData.name}.
                        </p>
                        <p className="text-sm">
                          ⏰ Appeal deadline:{" "}
                          <span className="font-semibold">
                            {validationResult.days_remaining !== null
                              ? `${validationResult.days_remaining} days remaining`
                              : `${cityData.appealDeadlineDays} days from citation date`}
                          </span>
                        </p>
                      </div>
                      <button
                        onClick={handleStartAppeal}
                        className="mt-5 w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white py-4 px-6 rounded-xl font-bold text-lg shadow-lg hover:shadow-xl transition-all transform hover:scale-[1.02] active:scale-[0.98]"
                      >
                        Get My Ticket Dismissed →
                      </button>
                    </div>
                  </div>
                </div>
                <LegalDisclaimer variant="compact" />
              </div>
            )}
          </div>

          {/* Right Column: City Information */}
          <div className="space-y-4 sm:space-y-6">
            {/* What You Get - Transformation Focus */}
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-xl sm:rounded-2xl border-2 border-green-200 p-5 sm:p-6 md:p-8 shadow-lg">
              <h2 className="text-xl sm:text-2xl font-bold text-gray-900 mb-4 sm:mb-6 flex items-center">
                <svg
                  className="w-6 h-6 sm:w-7 sm:h-7 text-green-600 mr-2 sm:mr-3"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                What You Get When You Appeal
              </h2>
              <div className="space-y-4 mb-6">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mt-1">
                    <svg
                      className="w-5 h-5 text-white"
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
                    <h3 className="font-bold text-gray-900">Keep Your Money</h3>
                    <p className="text-sm text-gray-700">
                      Save $50-$500+ per ticket. That's real money back in your
                      pocket.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mt-1">
                    <svg
                      className="w-5 h-5 text-white"
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
                    <h3 className="font-bold text-gray-900">
                      Protect Your Insurance
                    </h3>
                    <p className="text-sm text-gray-700">
                      No points. No rate increases. Your insurance stays
                      affordable.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-8 h-8 bg-green-500 rounded-full flex items-center justify-center mt-1">
                    <svg
                      className="w-5 h-5 text-white"
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
                    <h3 className="font-bold text-gray-900">Clean Record</h3>
                    <p className="text-sm text-gray-700">
                      No future consequences. No background check issues.
                    </p>
                  </div>
                </div>
              </div>
              <div className="bg-white rounded-lg p-4 border border-green-200">
                <p className="text-sm text-gray-700">
                  <strong className="text-gray-900">The math:</strong> Pay $100
                  ticket = lose $100 forever. Appeal for $10 = potentially save
                  $100. <strong>That's a 10x return.</strong>
                </p>
              </div>
            </div>

            {/* How It Works - Minimal (10% plane) */}
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl sm:rounded-2xl border border-blue-200 p-5 sm:p-6 shadow">
              <h2 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 flex items-center">
                <svg
                  className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 mr-2"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M13 10V3L4 14h7v7l9-11h-7z"
                  />
                </svg>
                Quick Process
              </h2>
              <div className="space-y-3 sm:space-y-4">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm sm:text-base mr-3 sm:mr-4">
                    1
                  </div>
                  <div className="flex-1 pt-1 sm:pt-0">
                    <p className="text-sm sm:text-base font-semibold text-gray-900">
                      Enter Citation
                    </p>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">
                      Takes 30 seconds
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm sm:text-base mr-3 sm:mr-4">
                    2
                  </div>
                  <div className="flex-1 pt-1 sm:pt-0">
                    <p className="text-sm sm:text-base font-semibold text-gray-900">
                      Upload Photos & Tell Your Story
                    </p>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">
                      2-3 minutes
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold text-sm sm:text-base mr-3 sm:mr-4">
                    3
                  </div>
                  <div className="flex-1 pt-1 sm:pt-0">
                    <p className="text-sm sm:text-base font-semibold text-gray-900">
                      Review & Sign
                    </p>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">
                      1 minute
                    </p>
                  </div>
                </div>
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-8 h-8 sm:w-10 sm:h-10 bg-green-600 rounded-lg flex items-center justify-center text-white font-bold text-sm sm:text-base mr-3 sm:mr-4">
                    ✓
                  </div>
                  <div className="flex-1 pt-1 sm:pt-0">
                    <p className="text-sm sm:text-base font-semibold text-gray-900">
                      We Mail It Automatically
                    </p>
                    <p className="text-xs sm:text-sm text-gray-600 mt-1">
                      No work for you - we handle everything
                    </p>
                  </div>
                </div>
              </div>
              <div className="mt-4 sm:mt-6 pt-4 sm:pt-6 border-t border-blue-200">
                <p className="text-center text-sm sm:text-base font-bold text-blue-900">
                  ⏱️ Total Time: 5-8 Minutes • 💰 One-Time Fee • 📮 We Mail It
                  For You
                </p>
              </div>
            </div>

            <div className="bg-white rounded-xl sm:rounded-2xl shadow-xl border border-gray-100 p-5 sm:p-6 md:p-8 hover:shadow-2xl transition-shadow duration-300">
              <div className="flex items-center mb-4 sm:mb-6">
                <div className="w-10 h-10 sm:w-12 sm:h-12 bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl flex items-center justify-center mr-3 sm:mr-4 shadow-lg flex-shrink-0">
                  <svg
                    className="w-5 h-5 sm:w-6 sm:h-6 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                    />
                  </svg>
                </div>
                <h2 className="text-lg sm:text-2xl font-bold text-gray-900">
                  About {cityData.name} Appeals
                </h2>
              </div>

              <div className="space-y-4 sm:space-y-6">
                <div>
                  <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-2">
                    Appeal Process
                  </h3>
                  <ul className="space-y-2 sm:space-y-2 text-sm sm:text-base text-gray-600">
                    <li className="flex items-start group">
                      <span className="inline-flex items-center justify-center h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white text-sm font-bold mr-4 shadow-md group-hover:scale-110 transition-transform">
                        1
                      </span>
                      <span className="pt-1">
                        Validate your citation number
                      </span>
                    </li>
                    <li className="flex items-start group">
                      <span className="inline-flex items-center justify-center h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white text-sm font-bold mr-4 shadow-md group-hover:scale-110 transition-transform">
                        2
                      </span>
                      <span className="pt-1">Upload photos and evidence</span>
                    </li>
                    <li className="flex items-start group">
                      <span className="inline-flex items-center justify-center h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white text-sm font-bold mr-4 shadow-md group-hover:scale-110 transition-transform">
                        3
                      </span>
                      <span className="pt-1">Craft your appeal statement</span>
                    </li>
                    <li className="flex items-start group">
                      <span className="inline-flex items-center justify-center h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white text-sm font-bold mr-4 shadow-md group-hover:scale-110 transition-transform">
                        4
                      </span>
                      <span className="pt-1">Review and sign your letter</span>
                    </li>
                    <li className="flex items-start group">
                      <span className="inline-flex items-center justify-center h-8 w-8 rounded-xl bg-gradient-to-br from-blue-500 to-blue-600 text-white text-sm font-bold mr-4 shadow-md group-hover:scale-110 transition-transform">
                        5
                      </span>
                      <span className="pt-1">
                        We mail it directly to {cityData.name}
                      </span>
                    </li>
                  </ul>
                </div>

                <div className="border-t pt-4 sm:pt-6">
                  <h3 className="text-base sm:text-lg font-medium text-gray-900 mb-3 sm:mb-4">
                    City Details
                  </h3>
                  <dl className="grid grid-cols-2 gap-3 sm:gap-4">
                    <div>
                      <dt className="text-xs sm:text-sm font-medium text-gray-500">
                        State
                      </dt>
                      <dd className="mt-1 text-sm sm:text-base text-gray-900 font-semibold">
                        {cityData.state || "N/A"}
                      </dd>
                    </div>
                    <div>
                      <dt className="text-xs sm:text-sm font-medium text-gray-500">
                        Appeal Deadline
                      </dt>
                      <dd className="mt-1 text-sm sm:text-base text-gray-900 font-semibold">
                        {cityData.appealDeadlineDays} days
                      </dd>
                    </div>
                    <div className="col-span-2">
                      <dt className="text-xs sm:text-sm font-medium text-gray-500">
                        Issuing Agencies
                      </dt>
                      <dd className="mt-1 text-sm sm:text-base text-gray-900">
                        {cityData.agencies.join(", ")}
                      </dd>
                    </div>
                  </dl>
                </div>
              </div>
            </div>

            <div className="bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 border-2 border-blue-200 rounded-xl sm:rounded-2xl p-4 sm:p-6 shadow-lg">
              <div className="flex items-center mb-3">
                <svg
                  className="w-5 h-5 sm:w-6 sm:h-6 text-blue-600 mr-2 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                  />
                </svg>
                <h3 className="text-base sm:text-lg font-bold text-blue-900">
                  Need Help?
                </h3>
              </div>
              <p className="text-sm sm:text-base text-blue-800 mb-3 sm:mb-4 font-medium">
                Our automated system handles {cityData.name}'s specific
                requirements:
              </p>
              <ul className="text-sm sm:text-base text-blue-800 space-y-2">
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2 flex-shrink-0">✓</span>
                  <span>Correct mailing address for {cityData.name}</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2 flex-shrink-0">✓</span>
                  <span>{cityData.name}'s specific appeal deadlines</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2 flex-shrink-0">✓</span>
                  <span>Proper citation format validation</span>
                </li>
                <li className="flex items-start">
                  <span className="text-blue-600 mr-2 flex-shrink-0">✓</span>
                  <span>Agency-specific requirements</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-500 text-sm mb-6">
            <p className="font-medium text-gray-700">
              © {new Date().getFullYear()} FightCityTickets.com
            </p>
            <p className="mt-2 text-gray-500">
              Document preparation service for parking ticket appeals
            </p>
            <div className="mt-4 flex justify-center space-x-6">
              <Link
                href="/privacy"
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                Privacy Policy
              </Link>
              <Link
                href="/terms"
                className="text-gray-500 hover:text-gray-700 transition-colors"
              >
                Terms of Service
              </Link>
            </div>
          </div>
          <div className="border-t border-gray-100 pt-6">
            <LegalDisclaimer variant="compact" />
          </div>

          {/* SEO Links Section */}
          <div className="border-t border-gray-100 pt-6 mt-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">
              Learn More About {cityData.name} Parking Tickets
            </h3>
            <div className="grid md:grid-cols-2 gap-4">
              <Link
                href="/blog"
                className="block p-4 bg-blue-50 rounded-lg border border-blue-200 hover:border-blue-400 hover:shadow-md transition"
              >
                <h4 className="font-semibold text-blue-900 mb-2">
                  📚 Read Our Blog
                </h4>
                <p className="text-sm text-blue-700">
                  Expert guides on appealing parking tickets, understanding
                  violation codes, and navigating the appeals process.
                </p>
              </Link>
              <div className="p-4 bg-green-50 rounded-lg border border-green-200">
                <h4 className="font-semibold text-green-900 mb-2">
                  🔍 Find Your Violation
                </h4>
                <p className="text-sm text-green-700 mb-3">
                  Looking for specific violation codes or locations? Check our
                  violation guides.
                </p>
                <Link
                  href={`/${cityMapping?.slug || citySlug}/violations`}
                  className="text-sm text-green-600 hover:text-green-700 font-medium"
                >
                  View {cityData.name} Violations →
                </Link>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
