"use client";

import { useState, useEffect } from "react";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import AddressAutocomplete from "../../../components/AddressAutocomplete";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

export const dynamic = "force-dynamic";

export default function CheckoutPage() {
  const { state, updateState } = useAppeal();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [addressError, setAddressError] = useState<string | null>(null);
  const [acceptedTerms, setAcceptedTerms] = useState(false);
  const [clericalId, setClericalId] = useState<string>("");

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
      cityId.replace(/us-|-/g, " ").replace(/_/g, " ").split(" ").map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(" ")
    );
  };

  const totalFee = 3900;

  const formatPrice = (cents: number) => `$${(cents / 100).toFixed(2)}`;

  const handleCheckout = async () => {
    if (!acceptedTerms) {
      setError("Please acknowledge the terms to proceed");
      return;
    }
    if (!state.userInfo.name || !state.userInfo.addressLine1) {
      setError("Please complete your information");
      return;
    }
    if (!state.userInfo.city || !state.userInfo.state || !state.userInfo.zip) {
      setError("Please ensure your address is complete");
      return;
    }
    if (!/^\d{5}(-\d{4})?$/.test(state.userInfo.zip)) {
      setError("Please enter a valid ZIP code");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/checkout/create-appeal-checkout`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          citation_number: state.citationNumber,
          city_id: state.cityId,
          section_id: state.sectionId,
          user_attestation: acceptedTerms,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to create checkout session");
      }

      const data = await response.json();
      if (data.clerical_id) setClericalId(data.clerical_id);
      window.location.href = data.checkout_url;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Checkout failed");
      setLoading(false);
    }
  };

  return (
    <main className="min-h-[calc(100vh-5rem)] px-4 py-8 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
      <div className="max-w-lg mx-auto step-content">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 theme-transition" style={{ color: "var(--text-primary)" }}>
            Complete Your Submission
          </h1>
          <p className="theme-transition" style={{ color: "var(--text-secondary)" }}>
            Provide your information for document preparation
          </p>
        </div>

        {/* Contact Info Card */}
        <div className="card-step p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 theme-transition" style={{ color: "var(--text-primary)" }}>
            Your Information
          </h2>

          <div className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                Full name *
              </label>
              <input
                type="text"
                value={state.userInfo.name}
                onChange={(e) => updateState({ userInfo: { ...state.userInfo, name: e.target.value } })}
                className="input-strike"
                placeholder="John Doe"
              />
            </div>

            {/* Address */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                Street address *
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
                onInputChange={(value) => updateState({ userInfo: { ...state.userInfo, addressLine1: value } })}
                onError={setAddressError}
                className="input-strike"
                placeholder="123 Main St"
              />
              {addressError && <p style={{ color: "#DC2626", fontSize: "0.875rem", marginTop: "rem" }}>{addressError}0.25</p>}
              <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginTop: "0.25rem" }}>
                The municipal authority will send their response here.
              </p>
            </div>

            {/* City/State/ZIP */}
            <div className="grid grid-cols-3 gap-3">
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>City *</label>
                <input
                  type="text"
                  value={state.userInfo.city}
                  onChange={(e) => updateState({ userInfo: { ...state.userInfo, city: e.target.value } })}
                  className="input-strike text-center"
                  placeholder="City"
                  readOnly={!!state.userInfo.addressLine1 && !!state.userInfo.city}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>State *</label>
                <input
                  type="text"
                  value={state.userInfo.state}
                  onChange={(e) => updateState({ userInfo: { ...state.userInfo, state: e.target.value.toUpperCase() } })}
                  className="input-strike text-center"
                  placeholder="CA"
                  maxLength={2}
                  readOnly={!!state.userInfo.addressLine1 && !!state.userInfo.state}
                />
              </div>
              <div>
                <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>ZIP *</label>
                <input
                  type="text"
                  value={state.userInfo.zip}
                  onChange={(e) => updateState({ userInfo: { ...state.userInfo, zip: e.target.value } })}
                  className="input-strike text-center"
                  placeholder="94102"
                  readOnly={!!state.userInfo.addressLine1 && !!state.userInfo.zip}
                />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>Email (optional)</label>
              <input
                type="email"
                value={state.userInfo.email}
                onChange={(e) => updateState({ userInfo: { ...state.userInfo, email: e.target.value } })}
                className="input-strike"
                placeholder="your@email.com"
              />
            </div>
          </div>
        </div>

        {/* Order Summary */}
        <div className="card-step p-6 mb-6">
          <h2 className="text-xl font-semibold mb-4 theme-transition" style={{ color: "var(--text-primary)" }}>
            Order Summary
          </h2>

          <div className="space-y-3">
            <div className="flex justify-between">
              <span style={{ color: "var(--text-secondary)" }}>City</span>
              <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>{formatCityName(state.cityId)}</span>
            </div>
            <div className="flex justify-between">
              <span style={{ color: "var(--text-secondary)" }}>Citation</span>
              <span style={{ color: "var(--text-primary)", fontFamily: "monospace" }}>{state.citationNumber || "Pending"}</span>
            </div>
            {clericalId && (
              <div className="flex justify-between">
                <span style={{ color: "var(--text-secondary)" }}>Reference</span>
                <span style={{ color: "var(--text-muted)", fontFamily: "monospace", fontSize: "0.875rem" }}>{clericalId}</span>
              </div>
            )}
            <div className="border-t pt-3 mt-3" style={{ borderColor: "var(--border)" }}>
              <div className="flex justify-between items-center">
                <span style={{ color: "var(--text-primary)", fontWeight: 600 }}>Total</span>
                <span className="text-3xl font-bold" style={{ color: "var(--accent)" }}>{formatPrice(totalFee)}</span>
              </div>
              <p style={{ color: "var(--text-muted)", fontSize: "0.875rem", marginTop: "0.5rem" }}>
                Includes appeal letter preparation and certified mailing
              </p>
            </div>
          </div>
        </div>

        {/* Warning */}
        <div 
          className="p-4 rounded-lg mb-6"
          style={{ backgroundColor: "#FEF3C7", border: "1px solid #FDE68A" }}
        >
          <h3 className="font-semibold mb-2" style={{ color: "#92400E" }}>Important</h3>
          <p style={{ color: "#92400E", fontSize: "0.875rem" }}>
            This is a <strong>document preparation service only</strong>. We do not provide legal advice or guarantees about outcomes. The municipal authority will review your appeal and make the final decision. This fee is non-refundable.
          </p>
        </div>

        {/* Terms Checkbox */}
        <label className="flex items-start cursor-pointer mb-6">
          <input
            type="checkbox"
            checked={acceptedTerms}
            onChange={(e) => setAcceptedTerms(e.target.checked)}
            className="mt-1 mr-3"
            style={{ accentColor: "var(--accent)" }}
          />
          <span style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            I understand I am purchasing <strong>document preparation services only</strong>. The outcome is determined solely by the municipal authority. This fee is non-refundable.{" "}
            <Link href="/refund" style={{ color: "var(--accent)", textDecoration: "underline" }}>Read full terms</Link>.
          </span>
        </label>

        {/* Error */}
        {error && (
          <div className="p-4 rounded-lg mb-6" style={{ backgroundColor: "#FEF2F2", border: "1px solid #FECACA" }}>
            <p style={{ color: "#DC2626" }}>{error}</p>
          </div>
        )}

        {/* Actions */}
        <div className="flex gap-4">
          <Link href="/appeal/signature" className="btn-secondary flex-1">
            ← Back
          </Link>
          <button
            onClick={handleCheckout}
            disabled={loading || !acceptedTerms}
            className="btn-strike flex-1"
          >
            {loading ? "Processing..." : "Proceed to Payment →"}
          </button>
        </div>

        <LegalDisclaimer variant="compact" />
      </div>
    </main>
  );
}
