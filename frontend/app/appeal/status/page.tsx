"use client";

import Link from "next/link";
import { useState } from "react";
import LegalDisclaimer from "../../../components/LegalDisclaimer";
import { Alert } from "../../../components/ui/Alert";
import { Button } from "../../../components/ui/Button";
import { Card } from "../../../components/ui/Card";
import { Input } from "../../../components/ui/Input";

export default function AppealStatusPage() {
  const [email, setEmail] = useState("");
  const [citationNumber, setCitationNumber] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [appealData, setAppealData] = useState<{
    citation_number: string;
    payment_status: string;
    mailing_status: string;
    tracking_number?: string;
    expected_delivery?: string;
    mailed_date?: string;
    amount_paid: number;
    appeal_type: string;
    tracking_visible: boolean;
  } | null>(null);

  const handleLookup = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setAppealData(null);

    if (!email || !citationNumber) {
      setError("Please enter both email and citation number");
      setLoading(false);
      return;
    }

    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/status/lookup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          email: email.trim(),
          citation_number: citationNumber.trim(),
        }),
      });

      if (!response.ok) {
        if (response.status === 404) {
          setError("No appeal found with that email and citation number");
        } else {
          throw new Error("Failed to lookup appeal");
        }
        return;
      }

      const data = await response.json();
      setAppealData({
        citation_number: data.citation_number,
        payment_status: data.payment_status,
        mailing_status: data.mailing_status || "pending",
        tracking_number: data.tracking_number,
        expected_delivery: data.expected_delivery,
        amount_paid: data.amount_total || 0,
        appeal_type: data.appeal_type || "standard",
        tracking_visible: data.tracking_visible !== false,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to lookup appeal");
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const getStatusConfig = (status: string) => {
    switch (status) {
      case "paid":
      case "mailed":
        return {
          bg: "bg-success-bg",
          border: "border-success-border",
          text: "text-success",
          icon: (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                clipRule="evenodd"
              />
            </svg>
          ),
        };
      case "pending":
        return {
          bg: "bg-warning-bg",
          border: "border-warning-border",
          text: "text-warning",
          icon: (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                clipRule="evenodd"
              />
            </svg>
          ),
        };
      case "failed":
        return {
          bg: "bg-error-bg",
          border: "border-error-border",
          text: "text-error",
          icon: (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
                clipRule="evenodd"
              />
            </svg>
          ),
        };
      default:
        return {
          bg: "bg-bg-subtle",
          border: "border-border",
          text: "text-text-secondary",
          icon: (
            <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z"
                clipRule="evenodd"
              />
            </svg>
          ),
        };
    }
  };

  return (
    <main className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-heading-lg text-text-primary mb-3">
            Check Your Appeal Status
          </h1>
          <p className="text-body text-text-secondary">
            Enter your email and citation number to see your appeal status.
          </p>
        </div>

        {/* Lookup Form */}
        <Card padding="lg" className="mb-8">
          <form onSubmit={handleLookup} className="space-y-5">
            <Input
              label="Email address *"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
            />
            <Input
              label="Citation number *"
              value={citationNumber}
              onChange={(e) => setCitationNumber(e.target.value)}
              placeholder="e.g., 912345678"
            />
            {error && (
              <Alert
                variant="error"
                dismissible
                onDismiss={() => setError(null)}
              >
                {error}
              </Alert>
            )}
            <Button type="submit" loading={loading} fullWidth>
              {loading ? "Looking up..." : "Check Status →"}
            </Button>
          </form>
        </Card>

        {/* Appeal Status Results */}
        {appealData && (
          <div className="space-y-6 animate-fade-in">
            {/* Status Overview */}
            <Card padding="lg">
              <h2 className="text-heading-md text-text-primary mb-6">
                Appeal Status
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <p className="text-body-sm text-text-muted mb-1">Citation</p>
                  <p className="font-mono text-lg text-text-primary">
                    {appealData.citation_number}
                  </p>
                </div>
                <div>
                  <p className="text-body-sm text-text-muted mb-1">Payment</p>
                  {(() => {
                    const config = getStatusConfig(appealData.payment_status);
                    return (
                      <span
                        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.border} ${config.text}`}
                      >
                        {config.icon}
                        {appealData.payment_status === "paid"
                          ? "Paid"
                          : appealData.payment_status}
                      </span>
                    );
                  })()}
                </div>
                <div>
                  <p className="text-body-sm text-text-muted mb-1">Mailing</p>
                  {(() => {
                    const config = getStatusConfig(appealData.mailing_status);
                    return (
                      <span
                        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-medium ${config.bg} ${config.border} ${config.text}`}
                      >
                        {config.icon}
                        {appealData.mailing_status === "mailed"
                          ? "Mailed"
                          : appealData.mailing_status === "pending"
                            ? "Pending"
                            : appealData.mailing_status}
                      </span>
                    );
                  })()}
                </div>
                <div>
                  <p className="text-body-sm text-text-muted mb-1">
                    Amount Paid
                  </p>
                  <p className="text-lg font-semibold text-success">
                    {formatAmount(appealData.amount_paid)}
                  </p>
                </div>
              </div>
            </Card>

            {/* Tracking Information */}
            {appealData.tracking_number && appealData.tracking_visible && (
              <Card
                padding="lg"
                className="bg-success-bg border-success-border"
              >
                <div className="flex items-start gap-3">
                  <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center flex-shrink-0">
                    <svg
                      className="w-5 h-5 text-success"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path
                        fillRule="evenodd"
                        d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z"
                        clipRule="evenodd"
                      />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <h3 className="font-medium text-text-primary mb-2">
                      Certified Mail with Tracking
                    </h3>
                    <p className="text-body-sm text-text-secondary mb-3">
                      Tracking number:{" "}
                      <span className="font-mono font-medium">
                        {appealData.tracking_number}
                      </span>
                    </p>
                    {appealData.expected_delivery && (
                      <p className="text-body-sm text-text-secondary mb-3">
                        Expected delivery:{" "}
                        <span className="font-medium">
                          {appealData.expected_delivery}
                        </span>
                      </p>
                    )}
                    <a
                      href={`https://tools.usps.com/go/TrackConfirmAction?tLabels=${appealData.tracking_number}`}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-primary hover:text-primary-hover text-body-sm font-medium"
                    >
                      Track on USPS.com →
                    </a>
                  </div>
                </div>
              </Card>
            )}

            {/* Timeline */}
            <Card padding="lg">
              <h3 className="text-heading-sm text-text-primary mb-4">
                Timeline
              </h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${appealData.payment_status === "paid"
                        ? "bg-success text-white"
                        : "bg-bg-subtle text-text-muted"
                      }`}
                  >
                    {appealData.payment_status === "paid" ? (
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ) : (
                      <span className="text-xs">1</span>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">
                      Payment received
                    </p>
                    <p className="text-body-sm text-text-secondary">
                      Your document preparation fee was processed.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div
                    className={`w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 ${appealData.mailing_status === "mailed"
                        ? "bg-success text-white"
                        : appealData.mailing_status === "pending"
                          ? "bg-warning text-white"
                          : "bg-bg-subtle text-text-muted"
                      }`}
                  >
                    {appealData.mailing_status === "mailed" ? (
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ) : appealData.mailing_status === "pending" ? (
                      <svg
                        className="w-4 h-4"
                        fill="currentColor"
                        viewBox="0 0 20 20"
                      >
                        <path
                          fillRule="evenodd"
                          d="M10 18a8 8 0 100-16 8 8 0 000 16zm1-12a1 1 0 10-2 0v4a1 1 0 00.293.707l2.828 2.829a1 1 0 101.415-1.415L11 9.586V6z"
                          clipRule="evenodd"
                        />
                      </svg>
                    ) : (
                      <span className="text-xs">2</span>
                    )}
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">
                      Appeal mailed
                    </p>
                    <p className="text-body-sm text-text-secondary">
                      {appealData.mailing_status === "mailed"
                        ? "Your appeal has been mailed to the city."
                        : "Your appeal will be mailed within 1-2 business days."}
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0 bg-bg-subtle text-text-muted">
                    <span className="text-xs">3</span>
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">
                      City response
                    </p>
                    <p className="text-body-sm text-text-secondary">
                      The city will mail their response to you (typically 2-8
                      weeks).
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            {/* What This Means */}
            <Alert variant="info">
              <p className="font-medium text-text-primary mb-1">
                What happens next
              </p>
              <p className="text-body-sm">
                Wait for the city&apos;s response to be mailed to your address.
                This is document preparation only—the outcome is determined by
                the municipal authority.
              </p>
            </Alert>
          </div>
        )}

        {/* Support */}
        <Card padding="md" className="mt-8 text-center">
          <p className="text-body text-text-secondary mb-3">
            Can&apos;t find your appeal?
          </p>
          <a
            href={`mailto:${process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}`}
            className="text-primary hover:text-primary-hover font-medium"
          >
            Contact support
          </a>
        </Card>

        <LegalDisclaimer variant="compact" className="mt-6" />

        <div className="text-center mt-8">
          <Link
            href="/"
            className="text-primary hover:text-primary-hover font-medium"
          >
            ← Return to home
          </Link>
        </div>
      </div>
    </main>
  );
}
