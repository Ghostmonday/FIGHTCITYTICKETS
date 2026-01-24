"use client";

import { useState, useEffect } from "react";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import AddressAutocomplete from "../../../components/AddressAutocomplete";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

// Force dynamic rendering - this page uses client-side context
export const dynamic = "force-dynamic";

export default function CheckoutPage() {
  const { state, updateState } = useAppeal();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [addressError, setAddressError] = useState<string | null>(null);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [clericalId, setClericalId] = useState<string>("");

  // Generate Clerical ID on component mount
  useEffect(() => {
    const generateClericalId = () => {
      const timestamp = Date.now().toString(36).toUpperCase();
      const random = Math.random().toString(36).substring(2, 6).toUpperCase();
      return `ND-${timestamp.slice(-4)}-${random}`;
    };
    setClericalId(generateClericalId());
  }, []);

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

  // CERTIFIED-ONLY MODEL: $19.95 flat rate
  const totalFee = 1995; // $19.95 in cents

  const formatPrice = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const handleCheckout = async () => {
    // Block payment unless terms are accepted
    if (!acceptedTerms) {
      setError("Please acknowledge the service terms to proceed");
      return;
    }

    if (!state.userInfo.name || !state.userInfo.addressLine1) {
      setError("Please complete your information");
      return;
    }

    // Validate address components
    if (!state.userInfo.city || !state.userInfo.state || !state.userInfo.zip) {
      setError(
        "Please ensure your address is complete. Use the autocomplete for best results."
      );
      return;
    }

    // Validate ZIP code format (basic check)
    if (!/^\d{5}(-\d{4})?$/.test(state.userInfo.zip)) {
      setError("Please enter a valid ZIP code (e.g., 94102 or 94102-1234)");
      return;
    }

    // Validate state format (2 letters)
    if (!/^[A-Z]{2}$/.test(state.userInfo.state)) {
      setError("Please enter a valid 2-letter state code (e.g., CA, NY)");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(
        `${apiBase}/checkout/create-appeal-checkout`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            citation_number: state.citationNumber,
            city_id: state.cityId,
            section_id: state.sectionId,
            user_attestation: acceptedTerms,
          }),
        }
      );

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(
          errorData.detail || "Failed to create checkout session"
        );
      }

      const data = await response.json();

      // Store Clerical ID from response if available
      if (data.clerical_id) {
        setClericalId(data.clerical_id);
      }

      // Redirect to Stripe checkout
      window.location.href = data.checkout_url;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Checkout failed");
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-8">
          <h1 className="text-2xl font-bold mb-2 text-stone-800">
            Complete Your Submission
          </h1>
          <p className="text-stone-600 mb-8">
            Provide your information for procedural compliance processing.
          </p>

          <div className="mb-8 space-y-5">
            <div>
              <label className="block mb-2 font-medium text-stone-700">
                Full Name *
              </label>
              <input
                type="text"
                value={state.userInfo.name}
                onChange={(e) =>
                  updateState({
                    userInfo: { ...state.userInfo, name: e.target.value },
                  })
                }
                className="w-full p-3 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
                required
              />
            </div>
            <div>
              <label className="block mb-2 font-medium text-stone-700">
                Street Address *
                <span className="text-sm text-stone-500 ml-2 font-normal">
                  (Start typing to autocomplete)
                </span>
              </label>
              <AddressAutocomplete
                value={state.userInfo.addressLine1 || ""}
                onChange={(address) => {
                  updateState({
                    userInfo: {
                      ...state.userInfo,
                      addressLine1: address.addressLine1,
                      addressLine2: address.addressLine2 || "",
                      city: address.city,
                      state: address.state,
                      zip: address.zip,
                    },
                  });
                  setAddressError(null);
                }}
                onError={(errorMsg) => {
                  setAddressError(errorMsg);
                }}
                placeholder="123 Main St, San Francisco, CA 94102"
                required
                className={addressError ? "border-red-500" : ""}
              />
              {addressError && (
                <p className="mt-1 text-sm text-red-700">{addressError}</p>
              )}
              <p className="mt-1 text-xs text-stone-500">
                ⚠️ This address must be accurate. The municipal authority will
                send their response here.
              </p>
            </div>
            {state.userInfo.addressLine2 !== undefined && (
              <div>
                <label className="block mb-2 font-medium text-stone-700">
                  Address Line 2 (Apt, Suite, etc.)
                </label>
                <input
                  type="text"
                  value={state.userInfo.addressLine2 || ""}
                  onChange={(e) =>
                    updateState({
                      userInfo: {
                        ...state.userInfo,
                        addressLine2: e.target.value,
                      },
                    })
                  }
                  className="w-full p-3 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
                  placeholder="Apt 4B, Suite 200, etc."
                />
              </div>
            )}
            <div className="grid grid-cols-2 gap-5">
              <div>
                <label className="block mb-2 font-medium text-stone-700">
                  City *
                </label>
                <input
                  type="text"
                  value={state.userInfo.city}
                  onChange={(e) =>
                    updateState({
                      userInfo: { ...state.userInfo, city: e.target.value },
                    })
                  }
                  className="w-full p-3 border border-stone-300 rounded-lg bg-stone-50 focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
                  required
                  readOnly={
                    !!state.userInfo.addressLine1 && !!state.userInfo.city
                  }
                  title={
                    state.userInfo.addressLine1 && state.userInfo.city
                      ? "Auto-filled and locked - do not edit"
                      : ""
                  }
                />
                {!!state.userInfo.addressLine1 && !!state.userInfo.city && (
                  <p className="mt-1 text-xs text-stone-400">
                    Auto-filled from address • Locked for accuracy
                  </p>
                )}
              </div>
              <div>
                <label className="block mb-2 font-medium text-stone-700">
                  State *
                </label>
                <input
                  type="text"
                  value={state.userInfo.state}
                  onChange={(e) =>
                    updateState({
                      userInfo: {
                        ...state.userInfo,
                        state: e.target.value.toUpperCase(),
                      },
                    })
                  }
                  className="w-full p-3 border border-stone-300 rounded-lg bg-stone-50 focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
                  maxLength={2}
                  required
                  placeholder="CA"
                  readOnly={
                    !!state.userInfo.addressLine1 && !!state.userInfo.state
                  }
                  title={
                    state.userInfo.addressLine1 && state.userInfo.state
                      ? "Auto-filled and locked - do not edit"
                      : ""
                  }
                />
                {!!state.userInfo.addressLine1 && !!state.userInfo.state && (
                  <p className="mt-1 text-xs text-stone-400">
                    Auto-filled from address • Locked for accuracy
                  </p>
                )}
              </div>
            </div>
            <div>
              <label className="block mb-2 font-medium text-stone-700">
                ZIP Code *
              </label>
              <input
                type="text"
                value={state.userInfo.zip}
                onChange={(e) =>
                  updateState({
                    userInfo: { ...state.userInfo, zip: e.target.value },
                  })
                }
                className="w-full p-3 border border-stone-300 rounded-lg bg-stone-50 focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
                required
                placeholder="94102"
                readOnly={!!state.userInfo.addressLine1 && !!state.userInfo.zip}
                title={
                  state.userInfo.addressLine1 && state.userInfo.zip
                    ? "Auto-filled from address"
                    : ""
                }
              />
            </div>
            <div>
              <label className="block mb-2 font-medium text-stone-700">
                Email
              </label>
              <input
                type="email"
                value={state.userInfo.email}
                onChange={(e) =>
                  updateState({
                    userInfo: { ...state.userInfo, email: e.target.value },
                  })
                }
                className="w-full p-3 border border-stone-300 rounded-lg focus:ring-2 focus:ring-stone-500 focus:border-stone-500 transition-colors"
              />
            </div>
          </div>

          <LegalDisclaimer variant="elegant" className="mb-6" />

          <div className="mb-6 p-5 bg-stone-50 border border-stone-200 rounded-lg">
            <p className="font-semibold mb-3 text-stone-800">
              Procedural Submission Summary
            </p>
            <div className="space-y-2 text-sm text-stone-600">
              <div className="flex justify-between">
                <span className="text-stone-500">City:</span>
                <span className="text-stone-800 font-medium">
                  {formatCityName(state.cityId)}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-stone-500">Citation:</span>
                <div className="flex items-center gap-2">
                  <span className="font-mono text-stone-800">
                    {state.citationNumber || "Pending"}
                  </span>
                  {clericalId && (
                    <span className="px-2 py-0.5 bg-stone-200 text-stone-600 text-xs font-mono rounded">
                      {clericalId}
                    </span>
                  )}
                </div>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-500">Submission Type:</span>
                <span className="text-stone-800">
                  Certified Mail with Tracking
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-stone-500">Service:</span>
                <span className="text-stone-800">
                  Procedural Compliance Document Preparation
                </span>
              </div>
            </div>
          </div>

          {/* Total Procedural Fee */}
          <div className="mb-6 p-4 bg-stone-100 border border-stone-300 rounded-lg">
            <div className="flex justify-between items-center">
              <span className="font-semibold text-stone-800">
                Total Procedural Fee
              </span>
              <span className="text-2xl font-light text-stone-800">
                {formatPrice(totalFee)}
              </span>
            </div>
            <p className="text-xs text-stone-500 mt-2">
              Includes professional appeal letter, certified mailing with
              tracking, and delivery proof.
            </p>
          </div>

          <div className="mb-6 p-4 bg-amber-50 border border-amber-200 rounded-lg">
            <label className="flex items-start cursor-pointer">
              <input
                type="checkbox"
                checked={acceptedTerms}
                onChange={(e) => setAcceptedTerms(e.target.checked)}
                className="mt-1 mr-3 h-5 w-5 text-stone-800 border-stone-300 rounded focus:ring-stone-500"
              />
              <span className="text-sm text-stone-800">
                I understand I am purchasing{" "}
                <strong>
                  procedural compliance and document preparation services only
                </strong>
                . The outcome of my appeal is determined solely by the municipal
                authority. This fee is non-refundable regardless of the citation
                outcome. I have reviewed the{" "}
                <Link href="/refund" className="underline hover:text-amber-900">
                  Refund Policy
                </Link>
                .
              </span>
            </label>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div className="flex justify-between items-center pt-4 border-t border-stone-200">
            <Link
              href="/appeal/signature"
              className="text-stone-600 hover:text-stone-800 transition-colors"
            >
              ← Back
            </Link>
            <button
              onClick={handleCheckout}
              disabled={loading || !acceptedTerms}
              className="bg-stone-900 hover:bg-stone-800 text-white px-8 py-4 rounded-lg font-medium text-lg transition-colors disabled:bg-stone-400 disabled:cursor-not-allowed"
            >
              {loading ? "Processing..." : "Complete Procedural Fee →"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
