"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import LegalDisclaimer from "../../components/LegalDisclaimer";

function SuccessContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const sessionId = searchParams.get("session_id");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paymentData, setPaymentData] = useState<{
    citation_number: string;
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

    // Fetch payment status
    const fetchPaymentStatus = async () => {
      try {
        const apiBase =
          process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
        const response = await fetch(
          `${apiBase}/checkout/session/${sessionId}`,
        );

        if (!response.ok) {
          throw new Error("Failed to fetch payment status");
        }

        const data = await response.json();
        setPaymentData({
          citation_number: data.citation_number || "Unknown",
          amount_total: data.amount_total || 0,
          appeal_type: data.appeal_type || "standard",
          tracking_number: data.tracking_number,
          expected_delivery: data.expected_delivery,
        });
      } catch (e) {
        setError(
          e instanceof Error ? e.message : "Failed to load payment details",
        );
      } finally {
        setLoading(false);
      }
    };

    fetchPaymentStatus();
  }, [sessionId]);

  const formatAmount = (cents: number) => {
    return `$${(cents / 100).toFixed(2)}`;
  };

  const formatAppealType = (type: string) => {
    return type === "certified" ? "Certified Mail" : "Standard Mail";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50">
      <div className="max-w-3xl mx-auto px-4 py-12">
        {loading ? (
          <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p className="text-gray-600">
              Loading your payment confirmation...
            </p>
          </div>
        ) : error ? (
          <div className="bg-white rounded-2xl shadow-xl p-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg
                  className="w-8 h-8 text-red-600"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Payment Status Unavailable
              </h1>
              <p className="text-gray-600 mb-6">{error}</p>
              <Link
                href="/"
                className="inline-block bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition"
              >
                Return to Home
              </Link>
            </div>
          </div>
        ) : (
          <div className="space-y-6">
            {/* Success Header */}
            <div className="bg-white rounded-2xl shadow-xl p-8 text-center border-2 border-green-200">
              <div className="w-20 h-20 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                <svg
                  className="w-12 h-12 text-white"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={3}
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </div>
              <h1 className="text-4xl font-extrabold text-gray-900 mb-3">
                Payment Successful!
              </h1>
              <p className="text-xl text-gray-700 mb-2 font-semibold">
                Your appeal is being processed
              </p>
              <p className="text-gray-600">
                We've received your payment and will mail your appeal letter
                within 1-2 business days.
              </p>
            </div>

            {/* What Happens Next - Transformation Focus */}
            <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl shadow-xl p-8 text-white">
              <h2 className="text-2xl font-bold mb-6">What Happens Next</h2>
              <div className="space-y-4">
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-bold">
                    1
                  </div>
                  <div>
                    <h3 className="font-bold text-lg mb-1">
                      We Prepare Your Appeal
                    </h3>
                    <p className="text-green-100">
                      Your appeal letter is being formatted and prepared for
                      mailing.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-bold">
                    2
                  </div>
                  <div>
                    <h3 className="font-bold text-lg mb-1">
                      We Mail It For You
                    </h3>
                    <p className="text-green-100">
                      Your appeal will be mailed via{" "}
                      {formatAppealType(paymentData?.appeal_type || "standard")}{" "}
                      within 1-2 business days.
                    </p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-10 h-10 bg-white/20 rounded-full flex items-center justify-center font-bold">
                    3
                  </div>
                  <div>
                    <h3 className="font-bold text-lg mb-1">
                      You Get Your Money Back
                    </h3>
                    <p className="text-green-100">
                      If your appeal is successful, you keep your money. No
                      ticket to pay. Clean record.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Payment Details */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Payment Details
              </h2>
              <div className="space-y-4">
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Citation Number</span>
                  <span className="font-semibold text-gray-900">
                    {paymentData?.citation_number}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Appeal Type</span>
                  <span className="font-semibold text-gray-900">
                    {formatAppealType(paymentData?.appeal_type || "standard")}
                  </span>
                </div>
                <div className="flex justify-between items-center py-3 border-b border-gray-200">
                  <span className="text-gray-600">Amount Paid</span>
                  <span className="font-bold text-green-600 text-xl">
                    {formatAmount(paymentData?.amount_total || 0)}
                  </span>
                </div>
                {paymentData?.tracking_number && (
                  <div className="flex justify-between items-center py-3 border-b border-gray-200">
                    <span className="text-gray-600">Tracking Number</span>
                    <span className="font-semibold text-gray-900 font-mono">
                      {paymentData.tracking_number}
                    </span>
                  </div>
                )}
                {paymentData?.expected_delivery && (
                  <div className="flex justify-between items-center py-3">
                    <span className="text-gray-600">Expected Delivery</span>
                    <span className="font-semibold text-gray-900">
                      {paymentData.expected_delivery}
                    </span>
                  </div>
                )}
              </div>
            </div>

            {/* Value Reminder - Transformation Focus */}
            <div className="bg-gradient-to-br from-blue-50 to-indigo-50 rounded-2xl border-2 border-blue-200 p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                What You Just Saved
              </h2>
              <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    $50-$500+
                  </div>
                  <div className="text-sm text-gray-600">
                    Potential ticket savings
                  </div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    0
                  </div>
                  <div className="text-sm text-gray-600">
                    Points on your record
                  </div>
                </div>
                <div className="text-center p-4 bg-white rounded-lg">
                  <div className="text-3xl font-bold text-green-600 mb-2">
                    0%
                  </div>
                  <div className="text-sm text-gray-600">
                    Insurance rate increase
                  </div>
                </div>
              </div>
              <p className="text-gray-700 text-center font-medium">
                <strong>
                  You paid {formatAmount(paymentData?.amount_total || 0)} to
                  potentially save hundreds.
                </strong>{" "}
                That's a smart investment in keeping your money and protecting
                your record.
              </p>
            </div>

            {/* Next Steps */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-4">
                What To Do Now
              </h2>
              <div className="space-y-3 text-gray-700">
                <p>
                  ✅ <strong>Check your email</strong> - We'll send you a
                  confirmation with tracking details
                </p>
                <p>
                  ✅ <strong>Wait for delivery</strong> - Your appeal will
                  arrive at the city within 3-5 business days
                </p>
                <p>
                  ✅ <strong>Track your appeal</strong> - Use the tracking
                  number to see when it's delivered
                </p>
                <p>
                  ✅ <strong>Check back in 2-4 weeks</strong> - The city will
                  respond by mail
                </p>
              </div>
            </div>

            {/* Support */}
            <div className="bg-gray-50 rounded-2xl p-6 text-center">
              <p className="text-gray-700 mb-4">
                Questions about your appeal? Need help?
              </p>
              <a
                href="mailto:support@fightcitytickets.com"
                className="inline-block bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-900 transition"
              >
                Contact Support
              </a>
            </div>

            {/* Legal Disclaimer */}
            <LegalDisclaimer variant="elegant" />

            {/* CTA */}
            <div className="text-center">
              <Link
                href="/"
                className="inline-block bg-green-600 text-white px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-700 transition shadow-lg hover:shadow-xl"
              >
                Appeal Another Ticket →
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
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-emerald-50 to-teal-50 flex items-center justify-center">
        <div className="bg-white rounded-2xl shadow-xl p-8 text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading...</p>
        </div>
      </div>
    }>
      <SuccessContent />
    </Suspense>
  );
}
