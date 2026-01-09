"use client";

import { useState } from "react";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

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
    amount_paid: number;
    appeal_type: string;
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
        tracking_number: data.lob_tracking_id,
        expected_delivery: data.expected_delivery,
        amount_paid: data.amount_total || 0,
        appeal_type: data.appeal_type || "standard",
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

  const getStatusColor = (status: string) => {
    if (status === "paid" || status === "mailed")
      return "text-green-600 bg-green-100";
    if (status === "pending") return "text-yellow-600 bg-yellow-100";
    if (status === "failed") return "text-red-600 bg-red-100";
    return "text-gray-600 bg-gray-100";
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      <div className="max-w-4xl mx-auto px-4 py-12">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
            Check Your Appeal Status
          </h1>
          <p className="text-lg text-gray-600">
            Enter your email and citation number to see the status of your
            appeal
          </p>
        </div>

        {/* Lookup Form */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <form onSubmit={handleLookup} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address *
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="your@email.com"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Citation Number *
              </label>
              <input
                type="text"
                value={citationNumber}
                onChange={(e) => setCitationNumber(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="e.g., 912345678"
                required
              />
            </div>
            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
                {error}
              </div>
            )}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white py-4 px-6 rounded-lg font-bold text-lg shadow-lg hover:shadow-xl disabled:bg-gray-400 disabled:shadow-none transition"
            >
              {loading ? "Looking up..." : "Check Status →"}
            </button>
          </form>
        </div>

        {/* Appeal Status Results */}
        {appealData && (
          <div className="space-y-6">
            {/* Status Overview */}
            <div className="bg-white rounded-2xl shadow-lg p-8">
              <h2 className="text-2xl font-bold text-gray-900 mb-6">
                Appeal Status
              </h2>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <div className="text-sm text-gray-600 mb-2">
                    Citation Number
                  </div>
                  <div className="text-xl font-bold text-gray-900">
                    {appealData.citation_number}
                  </div>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-2">
                    Payment Status
                  </div>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(appealData.payment_status)}`}
                  >
                    {appealData.payment_status === "paid"
                      ? "✅ Paid"
                      : appealData.payment_status}
                  </span>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-2">
                    Mailing Status
                  </div>
                  <span
                    className={`inline-block px-3 py-1 rounded-full text-sm font-semibold ${getStatusColor(appealData.mailing_status)}`}
                  >
                    {appealData.mailing_status === "mailed"
                      ? "📮 Mailed"
                      : appealData.mailing_status === "pending"
                        ? "⏳ Pending"
                        : appealData.mailing_status}
                  </span>
                </div>
                <div>
                  <div className="text-sm text-gray-600 mb-2">Amount Paid</div>
                  <div className="text-xl font-bold text-green-600">
                    {formatAmount(appealData.amount_paid)}
                  </div>
                </div>
              </div>
            </div>

            {/* Tracking Information */}
            {appealData.tracking_number && (
              <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-2xl border-2 border-green-200 p-8">
                <h3 className="text-xl font-bold text-gray-900 mb-4">
                  Tracking Information
                </h3>
                <div className="space-y-3">
                  <div>
                    <div className="text-sm text-gray-600 mb-1">
                      Tracking Number
                    </div>
                    <div className="text-lg font-mono font-semibold text-gray-900">
                      {appealData.tracking_number}
                    </div>
                  </div>
                  {appealData.expected_delivery && (
                    <div>
                      <div className="text-sm text-gray-600 mb-1">
                        Expected Delivery
                      </div>
                      <div className="text-lg font-semibold text-gray-900">
                        {appealData.expected_delivery}
                      </div>
                    </div>
                  )}
                  <p className="text-sm text-gray-700 mt-4">
                    You can track your appeal letter delivery using the tracking
                    number above.
                  </p>
                </div>
              </div>
            )}

            {/* What This Means - Transformation Focus */}
            <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white">
              <h3 className="text-xl font-bold mb-4">
                What This Means For You
              </h3>
              <div className="space-y-3">
                {appealData.payment_status === "paid" && (
                  <p>
                    ✅ <strong>Your payment was successful.</strong> Your appeal
                    is being processed.
                  </p>
                )}
                {appealData.mailing_status === "mailed" && (
                  <p>
                    📮 <strong>Your appeal has been mailed.</strong> The city
                    will receive it within 3-5 business days.
                  </p>
                )}
                {appealData.mailing_status === "pending" && (
                  <p>
                    ⏳ <strong>Your appeal is being prepared.</strong> It will
                    be mailed within 1-2 business days.
                  </p>
                )}
                <p className="mt-4">
                  <strong>Next step:</strong> Wait for the city&apos;s response
                  (typically 2-4 weeks). If your appeal is successful, you keep
                  your money and maintain a clean record.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Support */}
        <div className="bg-gray-50 rounded-2xl p-6 text-center mt-8">
          <p className="text-gray-700 mb-4">
            Can&apos;t find your appeal? Need help?
          </p>
          <a
            href="mailto:support@fightcitytickets.com"
            className="inline-block bg-gray-800 text-white px-6 py-3 rounded-lg font-semibold hover:bg-gray-900 transition"
          >
            Contact Support
          </a>
        </div>

        <LegalDisclaimer variant="compact" className="mt-8" />

        <div className="text-center mt-8">
          <Link
            href="/"
            className="text-green-600 hover:text-green-700 font-semibold"
          >
            ← Return to Home
          </Link>
        </div>
      </div>
    </div>
  );
}
