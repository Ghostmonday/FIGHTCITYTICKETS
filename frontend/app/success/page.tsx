"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";
import { Card } from "../../components/ui/Card";
import { Alert } from "../../components/ui/Alert";
import { Button } from "../../components/ui/Button";

function SuccessContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paymentData, setPaymentData] = useState<{
    citation_number: string;
    clerical_id: string;
    amount_total: number;
    appeal_type: string;
    tracking_number?: string;
    expected_delivery?: string;
  } | null>(null);

  useEffect(() => {
    if (!sessionId) {
      setError("No session ID provided");
      setLoading(false);
      return;
    }

    const fetchPaymentStatus = async () => {
      try {
        const apiBase =
          process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
        const response = await fetch(
          `${apiBase}/checkout/session-status?session_id=${sessionId}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch payment status");
        }

        const data = await response.json();

        setPaymentData({
          citation_number: data.citation_number || "Unknown",
          clerical_id: data.clerical_id || "",
          amount_total: data.amount_total || 0,
          appeal_type: data.appeal_type || "standard",
          tracking_number: data.tracking_number,
          expected_delivery: data.expected_delivery,
        });
      } catch (e) {
        setError(
          e instanceof Error ? e.message : "Failed to load payment details"
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPaymentStatus();
  }, [sessionId]);

  const formatAmount = (cents: number) => `$${(cents / 100).toFixed(2)}`;

  return (
    <main className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {loading ? (
          <Card padding="lg" className="text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent mx-auto mb-4" />
            <p className="text-body text-text-secondary">
              Processing your submission...
            </p>
          </Card>
        ) : error ? (
          <Alert variant="error" title="Unable to load submission details">
            {error}
            <div className="mt-4">
              <Link href="/" className="text-primary hover:underline">
                Return to home
              </Link>
            </div>
          </Alert>
        ) : (
          <div className="space-y-6 animate-fade-in">
            {/* Success Header - Clerical ID as Hero */}
            <Card padding="lg" className="text-center">
              <div className="w-16 h-16 bg-success-bg rounded-full flex items-center justify-center mx-auto mb-6">
                <svg
                  className="w-8 h-8 text-success"
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
              <h1 className="text-heading-lg text-text-primary mb-2">
                Appeal Submitted
              </h1>
              <p className="text-body text-text-secondary mb-6">
                Your appeal documents have been received and are being
                processed.
              </p>

              {/* Clerical ID Hero */}
              <div className="bg-bg-subtle border border-border rounded-lg p-4 inline-block">
                <p className="text-caption text-text-muted mb-1">
                  Reference ID
                </p>
                <p className="text-xl font-mono font-semibold text-text-primary">
                  {paymentData?.clerical_id}
                </p>
              </div>
            </Card>

            {/* Submission Details */}
            <Card padding="lg">
              <h2 className="text-heading-md text-text-primary mb-4">
                Submission Details
              </h2>
              <div className="space-y-3">
                <div className="flex justify-between py-2 border-b border-border">
                  <span className="text-text-secondary">Citation</span>
                  <span className="font-mono text-text-primary">
                    {paymentData?.citation_number}
                  </span>
                </div>
                <div className="flex justify-between py-2 border-b border-border">
                  <span className="text-text-secondary">Amount paid</span>
                  <span className="font-medium text-text-primary">
                    {formatAmount(paymentData?.amount_total || 0)}
                  </span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-text-secondary">Status</span>
                  <span className="text-success font-medium">Submitted</span>
                </div>
              </div>
            </Card>

            {/* Next Steps */}
            <Card padding="lg">
              <h2 className="text-heading-md text-text-primary mb-4">
                What Happens Next
              </h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-primary-muted rounded-full flex items-center justify-center flex-shrink-0 text-primary text-sm font-medium">
                    1
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">
                      Your appeal is being prepared
                    </p>
                    <p className="text-body-sm text-text-secondary">
                      We format your documents for procedural compliance.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-bg-subtle rounded-full flex items-center justify-center flex-shrink-0 text-text-muted text-sm">
                    2
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">
                      Mailed via certified mail
                    </p>
                    <p className="text-body-sm text-text-secondary">
                      Your appeal will be mailed within 1-2 business days.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-6 h-6 bg-bg-subtle rounded-full flex items-center justify-center flex-shrink-0 text-text-muted text-sm">
                    3
                  </div>
                  <div>
                    <p className="font-medium text-text-primary">
                      Municipal review
                    </p>
                    <p className="text-body-sm text-text-secondary">
                      The city will respond to your mailing address.
                    </p>
                  </div>
                </div>
              </div>
            </Card>

            {/* Important Information */}
            <Alert variant="warning" title="What to know">
              <ul className="space-y-1 text-body-sm">
                <li>• Response times vary by city (typically 2-8 weeks)</li>
                <li>
                  • The municipal authority will mail their response to you
                </li>
                <li>• This is document preparation only—not legal advice</li>
                <li>• Outcome determined by the issuing agency</li>
              </ul>
            </Alert>

            {/* Support */}
            <Card padding="md" className="text-center">
              <p className="text-body text-text-secondary mb-4">
                Questions about your submission?
              </p>
              <a
                href={`mailto:${process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}`}
                className="text-primary hover:text-primary-hover font-medium"
              >
                Contact support
              </a>
            </Card>

            {/* Legal Disclaimer */}
            <LegalDisclaimer variant="elegant" />

            {/* Actions */}
            <div className="text-center pt-4">
              <Link
                href="/"
                className="inline-flex items-center justify-center font-medium rounded-button px-6 py-3 text-body min-h-touch bg-primary text-white hover:bg-primary-hover active:bg-primary-hover focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary/50 transition-all duration-200"
              >
                Submit Another Citation →
              </Link>
            </div>
          </div>
        )}
      </div>
    </main>
  );
}

export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-bg-page flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-2 border-primary border-t-transparent mx-auto mb-4" />
            <p className="text-body text-text-secondary">Loading...</p>
          </div>
        </div>
      }
    >
      <SuccessContent />
    </Suspense>
  );
}
