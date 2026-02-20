"use client";

import Link from "next/link";
import { useState } from "react";
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
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/status/lookup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email: email.trim(), citation_number: citationNumber.trim() }),
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
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to lookup appeal");
    } finally {
      setLoading(false);
    }
  };

  const formatAmount = (cents: number) => `$${(cents / 100).toFixed(2)}`;

  const getStatusColor = (status: string) => {
    switch (status) {
      case "paid":
      case "mailed":
        return { bg: "#D1FAE5", text: "#065F46", label: status === "paid" ? "Paid" : "Mailed" };
      case "pending":
        return { bg: "#FEF3C7", text: "#92400E", label: "Pending" };
      case "failed":
        return { bg: "#FEE2E2", text: "#991B1B", label: "Failed" };
      default:
        return { bg: "var(--bg-subtle)", text: "var(--text-secondary)", label: status };
    }
  };

  return (
    <main className="min-h-[calc(100vh-5rem)] px-4 py-12 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
      <div className="max-w-lg mx-auto step-content">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-3 theme-transition" style={{ color: "var(--text-primary)" }}>
            Check Your Appeal Status
          </h1>
          <p className="theme-transition" style={{ color: "var(--text-secondary)" }}>
            Enter your email and citation number to see your status
          </p>
        </div>

        {/* Lookup Form */}
        <div className="card-step p-6 mb-8">
          <form onSubmit={handleLookup} className="space-y-5">
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                Email *
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-strike"
                placeholder="your@email.com"
              />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2" style={{ color: "var(--text-secondary)" }}>
                Citation Number *
              </label>
              <input
                type="text"
                value={citationNumber}
                onChange={(e) => setCitationNumber(e.target.value)}
                className="input-strike"
                placeholder="e.g., 912345678"
              />
            </div>
            {error && (
              <div className="p-3 rounded-lg" style={{ backgroundColor: "#FEE2E2", color: "#991B1B" }}>
                {error}
              </div>
            )}
            <button type="submit" disabled={loading} className="btn-strike w-full">
              {loading ? "Looking up..." : "Check Status →"}
            </button>
          </form>
        </div>

        {/* Results */}
        {appealData && (
          <div className="animate-fade-in space-y-6">
            {/* Status Card */}
            <div className="card-step p-6">
              <h2 className="text-lg font-semibold mb-4" style={{ color: "var(--text-primary)" }}>
                Appeal Status
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Citation</p>
                  <p style={{ color: "var(--text-primary)", fontFamily: "monospace" }}>{appealData.citation_number}</p>
                </div>
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Amount</p>
                  <p style={{ color: "var(--accent)", fontWeight: 600 }}>{formatAmount(appealData.amount_paid)}</p>
                </div>
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Payment</p>
                  {(() => {
                    const s = getStatusColor(appealData.payment_status);
                    return (
                      <span className="inline-block px-3 py-1 rounded-full text-sm font-medium" style={{ backgroundColor: s.bg, color: s.text }}>
                        {s.label}
                      </span>
                    );
                  })()}
                </div>
                <div>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Mailing</p>
                  {(() => {
                    const s = getStatusColor(appealData.mailing_status);
                    return (
                      <span className="inline-block px-3 py-1 rounded-full text-sm font-medium" style={{ backgroundColor: s.bg, color: s.text }}>
                        {s.label}
                      </span>
                    );
                  })()}
                </div>
              </div>
            </div>

            {/* Tracking */}
            {appealData.tracking_number && (
              <div className="card-step p-6" style={{ backgroundColor: "#D1FAE5", borderColor: "#A7F3D0" }}>
                <h3 className="font-semibold mb-2" style={{ color: "#065F46" }}>Certified Mail with Tracking</h3>
                <p style={{ color: "#065F46", fontSize: "0.875rem" }}>
                  Tracking: <span style={{ fontFamily: "monospace" }}>{appealData.tracking_number}</span>
                </p>
                {appealData.expected_delivery && (
                  <p style={{ color: "#065F46", fontSize: "0.875rem" }}>
                    Expected: {appealData.expected_delivery}
                  </p>
                )}
                <a
                  href={`https://tools.usps.com/go/TrackConfirmAction?tLabels=${appealData.tracking_number}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{ color: "#065F46", textDecoration: "underline", fontSize: "0.875rem" }}
                >
                  Track on USPS.com →
                </a>
              </div>
            )}

            {/* Timeline */}
            <div className="card-step p-6">
              <h3 className="font-semibold mb-4" style={{ color: "var(--text-primary)" }}>Timeline</h3>
              <div className="space-y-4">
                <div className="flex gap-3">
                  <div className={`w-6 h-6 rounded-full flex items-center justify-center ${appealData.payment_status === "paid" ? "" : "bg-gray-200"}`}
                    style={{ backgroundColor: appealData.payment_status === "paid" ? "#10B981" : "var(--bg-subtle)" }}>
                    {appealData.payment_status === "paid" && <span style={{ color: "white" }}>✓</span>}
                  </div>
                  <div>
                    <p style={{ color: "var(--text-primary)", fontWeight: 500 }}>Payment received</p>
                    <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>Your document preparation fee was processed.</p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center"
                    style={{ backgroundColor: appealData.mailing_status === "mailed" ? "#10B981" : appealData.mailing_status === "pending" ? "#F59E0B" : "var(--bg-subtle)" }}>
                    {appealData.mailing_status === "mailed" ? <span style={{ color: "white" }}>✓</span> : <span style={{ color: "white", fontSize: "0.75rem" }}>2</span>}
                  </div>
                  <div>
                    <p style={{ color: "var(--text-primary)", fontWeight: 500 }}>Appeal mailed</p>
                    <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
                      {appealData.mailing_status === "mailed" ? "Your appeal has been mailed." : "Your appeal will be mailed within 1-2 business days."}
                    </p>
                  </div>
                </div>
                <div className="flex gap-3">
                  <div className="w-6 h-6 rounded-full flex items-center justify-center" style={{ backgroundColor: "var(--bg-subtle)" }}>
                    <span style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>3</span>
                  </div>
                  <div>
                    <p style={{ color: "var(--text-primary)", fontWeight: 500 }}>City response</p>
                    <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>The city will mail their response (typically 2-8 weeks).</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Support */}
        <div className="card-step p-6 mt-8 text-center">
          <p style={{ color: "var(--text-secondary)", marginBottom: "0.75rem" }}>Can&apos;t find your appeal?</p>
          <a href={`mailto:${process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}`} style={{ color: "var(--accent)" }}>
            Contact support
          </a>
        </div>

        <LegalDisclaimer variant="compact" />

        <div className="text-center mt-8">
          <Link href="/" style={{ color: "var(--accent)" }}>← Return to home</Link>
        </div>
      </div>
    </main>
  );
}
