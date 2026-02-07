"use client";

import { useState, useEffect } from "react";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import AddressAutocomplete from "../../../components/AddressAutocomplete";
import LegalDisclaimer from "../../../components/LegalDisclaimer";
import { Button } from "../../../components/ui/Button";
import { Card } from "../../../components/ui/Card";
import { Input } from "../../../components/ui/Input";
import { Alert } from "../../../components/ui/Alert";

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

  // CERTIFIED-ONLY MODEL: $39 flat rate
  const totalFee = 3900; // $39.00 in cents

  const formatPrice = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const handleCheckout = async () => {
    // Block payment unless terms are accepted
    if (!acceptedTerms) {
      setError("Please acknowledge the terms to proceed");
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
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
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
    <main className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-heading-lg text-text-primary mb-2">
            Complete Your Submission
          </h1>
          <p className="text-body text-text-secondary">
            Provide your information for document preparation.
          </p>
        </div>

        <div className="space-y-6">
          {/* Contact Information */}
          <Card padding="lg">
            <h2 className="text-heading-md text-text-primary mb-6">
              Your Information
            </h2>

            <div className="space-y-5">
              <Input
                label="Full name *"
                value={state.userInfo.name}
                onChange={(e) =>
                  updateState({
                    userInfo: { ...state.userInfo, name: e.target.value },
                  })
                }
                placeholder="John Doe"
              />

              <div>
                <label className="block text-body-sm font-medium text-text-secondary mb-2">
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
                  onInputChange={(value) => {
                    updateState({
                      userInfo: {
                        ...state.userInfo,
                        addressLine1: value,
                      },
                    });
                  }}
                  onError={(errorMsg) => {
                    setAddressError(errorMsg);
                  }}
                  placeholder="123 Main St, San Francisco, CA 94102"
                />
                {addressError && (
                  <p className="mt-1 text-caption text-error">{addressError}</p>
                )}
                <p className="mt-1 text-caption text-text-muted">
                  The municipal authority will send their response to this
                  address.
                </p>
              </div>

              {state.userInfo.addressLine2 !== undefined && (
                <Input
                  label="Address line 2 (optional)"
                  value={state.userInfo.addressLine2 || ""}
                  onChange={(e) =>
                    updateState({
                      userInfo: {
                        ...state.userInfo,
                        addressLine2: e.target.value,
                      },
                    })
                  }
                  placeholder="Apt 4B, Suite 200"
                />
              )}

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="City *"
                  value={state.userInfo.city}
                  onChange={(e) =>
                    updateState({
                      userInfo: { ...state.userInfo, city: e.target.value },
                    })
                  }
                  readOnly={
                    !!state.userInfo.addressLine1 && !!state.userInfo.city
                  }
                  placeholder="San Francisco"
                />
                <Input
                  label="State *"
                  value={state.userInfo.state}
                  onChange={(e) =>
                    updateState({
                      userInfo: {
                        ...state.userInfo,
                        state: e.target.value.toUpperCase(),
                      },
                    })
                  }
                  maxLength={2}
                  placeholder="CA"
                  readOnly={
                    !!state.userInfo.addressLine1 && !!state.userInfo.state
                  }
                />
              </div>

              <Input
                label="ZIP code *"
                value={state.userInfo.zip}
                onChange={(e) =>
                  updateState({
                    userInfo: { ...state.userInfo, zip: e.target.value },
                  })
                }
                placeholder="94102"
                readOnly={!!state.userInfo.addressLine1 && !!state.userInfo.zip}
              />

              <Input
                label="Email (optional)"
                type="email"
                value={state.userInfo.email}
                onChange={(e) =>
                  updateState({
                    userInfo: { ...state.userInfo, email: e.target.value },
                  })
                }
                placeholder="your@email.com"
              />
            </div>
          </Card>

          {/* Order Summary */}
          <Card padding="lg">
            <h2 className="text-heading-md text-text-primary mb-6">
              Order Summary
            </h2>

            <div className="space-y-3 text-body">
              <div className="flex justify-between">
                <span className="text-text-secondary">City</span>
                <span className="text-text-primary font-medium">
                  {formatCityName(state.cityId)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-text-secondary">Citation</span>
                <span className="font-mono text-text-primary">
                  {state.citationNumber || "Pending"}
                </span>
              </div>
              {clericalId && (
                <div className="flex justify-between">
                  <span className="text-text-secondary">Reference ID</span>
                  <span className="font-mono text-caption bg-bg-subtle px-2 py-0.5 rounded">
                    {clericalId}
                  </span>
                </div>
              )}
              <div className="border-t border-border pt-3 mt-3">
                <div className="flex justify-between items-center">
                  <span className="text-text-primary font-medium">Total</span>
                  <span className="text-2xl font-semibold text-text-primary">
                    {formatPrice(totalFee)}
                  </span>
                </div>
                <p className="text-caption text-text-muted mt-2">
                  Includes appeal letter preparation and certified mailing.
                </p>
              </div>
            </div>
          </Card>

          {/* UPL Terms */}
          <Alert variant="warning" title="Important">
            <p className="mb-3">
              This is a <strong>document preparation service only</strong>. We
              do not provide legal advice, legal representation, or guarantees
              about outcomes.
            </p>
            <p>
              The municipal authority will review your appeal and make the final
              decision. This fee is non-refundable regardless of the outcome.
            </p>
          </Alert>

          {/* Terms Checkbox */}
          <label className="flex items-start cursor-pointer">
            <input
              type="checkbox"
              checked={acceptedTerms}
              onChange={(e) => setAcceptedTerms(e.target.checked)}
              className="mt-1 mr-3 h-5 w-5 text-primary border-border rounded focus:ring-primary/50 cursor-pointer"
            />
            <span className="text-body-sm text-text-secondary">
              I understand I am purchasing{" "}
              <strong>document preparation services only</strong>. The outcome
              of my appeal is determined solely by the municipal authority. This
              fee is non-refundable regardless of the citation outcome.{" "}
              <Link
                href="/refund"
                className="text-primary hover:text-primary-hover underline"
              >
                Read full terms
              </Link>
              .
            </span>
          </label>

          {/* Error Message */}
          {error && (
            <Alert variant="error" dismissible onDismiss={() => setError(null)}>
              {error}
            </Alert>
          )}

          {/* Actions */}
          <div className="flex justify-between items-center pt-4 border-t border-border">
            <Link
              href="/appeal/signature"
              className="text-body text-text-secondary hover:text-text-primary transition-colors"
            >
              ← Back
            </Link>
            <Button
              onClick={handleCheckout}
              loading={loading}
              disabled={loading || !acceptedTerms}
              className="min-w-[200px]"
            >
              {loading ? "Processing..." : "Proceed to Payment →"}
            </Button>
          </div>

          {/* Full Disclaimer */}
          <LegalDisclaimer variant="elegant" className="mt-6" />
        </div>
      </div>
    </main>
  );
}
