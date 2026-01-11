"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, Link } from "next/navigation";
import LegalDisclaimer from "../../components/LegalDisclaimer";

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
          `${apiBase}/checkout/session/${sessionId}`
        );

        if (!response.ok) {
          throw new Error("Failed to fetch payment status");
        }

        const data = await response.json();
        // Generate Clerical ID for display
        const clericalId = `ND-${Math.random().toString(36).substr(2, 4).toUpperCase()}-${Date.now().toString().slice(-4)}`;

        setPaymentData({
          citation_number: data.citation_number || "Unknown",
          clerical_id: clericalId,
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
  const formatAppealType = (type: string) =>
    type === "certified" ? "Certified Mail" : "Standard Mail";

  return (
    <div className="min-h-screen bg-stone-50">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {loading ? (
          <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-12 text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-stone-800 mx-auto mb-4"></div>
            <p className="text-stone-600">Processing your submission...</p>
          </div>
        ) : error ? (
          <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-8">
            <div className="text-center">
              <div className="w-14 h-14 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-6 h-6 text-stone-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                  />
                </svg>
              </div>
              <h1 className="text-xl font-bold text-stone-800 mb-2">
                Submission Status Unavailable
              </h1>
              <p className="text-stone-600 mb-6">{error}</p>
              <Link
                href="/"
                className="inline-block bg-stone-800 text-white px-6 py-3 rounded-lg font-medium hover:bg-stone-900 transition"
              >
                Return to Home
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Success Header - Institutional */}
            <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-8 text-center">
              <div className="w-16 h-16 bg-stone-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg
                  className="w-8 h-8 text-stone-700"
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
              <h1 className="text-2xl font-semibold text-stone-800 mb-3">
                Due Process Submission Complete
              </h1>
              <p className="text-stone-600">
                Your procedural compliance submission has been received and is
                being processed.
              </p>
            </div>

            {/* Submission Details */}
            <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-8">
              <h2 className="text-lg font-semibold text-stone-800 mb-6">
                Submission Details
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-stone-100">
                  <span className="text-stone-600">Citation Number</span>
                  <span className="font-mono text-stone-800">
                    {paymentData?.citation_number}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-stone-100">
                  <span className="text-stone-600">Clerical ID</span>
                  <span className="font-mono text-stone-800">
                    {paymentData?.clerical_id}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-stone-100">
                  <span className="text-stone-600">Submission Type</span>
                  <span className="text-stone-800">
                    {formatAppealType(paymentData?.appeal_type || "standard")}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-stone-100">
                  <span className="text-stone-600">Procedural Fee</span>
                  <span className="font-semibold text-stone-800">
                    {formatAmount(paymentData?.amount_total || 0)}
                  </span>
                </div>
                {paymentData?.tracking_number && (
                  <div className="flex justify-between items-center py-3 border-b border-stone-100">
                    <span className="text-stone-600">Tracking Number</span>
                    <span className="font-mono text-stone-800">
                      {paymentData.tracking_number}
                    </span>
                  </div>
                )}
                {paymentData?.expected_delivery && (
                  <div className="flex justify-between items-center py-3">
                    <span className="text-stone-600">Expected Processing</span>
                    <span className="text-stone-800">
                      {paymentData.expected_delivery}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Process Timeline */}
            <div className="bg-stone-100 rounded-lg border border-stone-200 p-6">
              <h2 className="text-lg font-semibold text-stone-800 mb-4">
                Procedural Timeline
              </h2>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-stone-700 rounded-full flex items-center justify-center text-white text-xs font-medium">
                    1
                  </div>
                  <div>
                    <p className="font-medium text-stone-800">
                      Submission Received
                    </p>
                    <p className="text-sm text-stone-600">
                      Your procedural compliance documents are being prepared.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-stone-300 rounded-full flex items-center justify-center text-white text-xs font-medium">
                    2
                  </div>
                  <div>
                    <p className="font-medium text-stone-600">
                      Mailing in Progress
                    </p>
                    <p className="text-sm text-stone-500">
                      Your appeal will be mailed within 1-2 business days.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="flex-shrink-0 w-6 h-6 bg-stone-300 rounded-full flex items-center justify-center text-white text-xs font-medium">
                    3
                  </div>
                  <div>
                    <p className="font-medium text-stone-600">
                      Municipal Review
                    </p>
                    <p className="text-sm text-stone-500">
                      The issuing agency will review your submission.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Important Information */}
            <div className="bg-amber-50 border border-amber-200 rounded-lg p-5">
              <h3 className="font-semibold text-amber-900 mb-3">
                Important Information
              </h3>
              <ul className="space-y-2 text-sm text-amber-800">
                <li>
                  • The municipal authority will respond directly to your
                  mailing address.
                </li>
                <li>
                  • Response times vary by jurisdiction (typically 2-8 weeks).
                </li>
                <li>
                  • This service provides procedural compliance documentation
                  only.
                </li>
                <li>
                  • Outcome determinations are made solely by the issuing
                  agency.
                </li>
              </ul>
            </div>

            {/* Support */}
            <div className="bg-stone-100 rounded-lg p-6 text-center">
              <p className="text-stone-700 mb-4">
                Questions about your procedural submission?
              </p>
              <a
                href="mailto:support@fightcitytickets.com"
                className="inline-block bg-stone-800 text-white px-6 py-3 rounded-lg font-medium hover:bg-stone-900 transition"
              >
                Contact Compliance Support
              </a>
            </div>

            {/* Legal Disclaimer */}
            <LegalDisclaimer variant="elegant" />

            {/* Continue */}
            <div className="text-center pt-4">
              <Link
                href="/"
                className="inline-block bg-stone-800 text-white px-8 py-4 rounded-lg font-medium hover:bg-stone-900 transition"
              >
                Submit Another Citation →
              </Link>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-screen bg-stone-50 flex items-center justify-center">
          <div className="bg-white rounded-lg shadow-sm border border-stone-200 p-8 text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-stone-800 mx-auto mb-4"></div>
            <p className="text-stone-600">Loading...</p>
          </div>
        </div>
      }
    >
      <SuccessContent />
    </Suspense>
  );
}
