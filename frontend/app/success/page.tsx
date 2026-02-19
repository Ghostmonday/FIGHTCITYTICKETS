"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
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
        const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
        const response = await fetch(`${apiBase}/checkout/session-status?session_id=${sessionId}`);

        if (!response.ok) {
          throw new Error("Failed to fetch payment status");
        }

        const data = await response.json();
        setPaymentData({
          citation_number: data.citation_number || "Unknown",
          clerical_id: data.clerical_id || "",
          amount_total: data.amount_total || 0,
          tracking_number: data.tracking_number,
          expected_delivery: data.expected_delivery,
        });
      } catch (e) {
        setError(e instanceof Error ? e.message : "Failed to load payment details");
      } finally {
        setLoading(false);
      }
    };

    fetchPaymentStatus();
  }, [sessionId]);

  const formatAmount = (cents: number) => `$${(cents / 100).toFixed(2)}`;

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-5rem)] flex items-center justify-center theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
        <div className="text-center">
          <div 
            className="animate-spin rounded-full h-10 w-10 mx-auto mb-4"
            style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }}
          />
          <p style={{ color: "var(--text-secondary)" }}>Processing your submission...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <main className="min-h-[calc(100vh-5rem)] px-4 py-12 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
        <div className="max-w-lg mx-auto step-content">
          <div className="card-step p-6 text-center" style={{ backgroundColor: "#FEE2E2" }}>
            <h2 className="font-semibold mb-2" style={{ color: "#991B1B" }}>Unable to load details</h2>
            <p style={{ color: "#991B1B" }}>{error}</p>
            <Link href="/" style={{ color: "var(--accent)", marginTop: "1rem" }} className="inline-block">Return to home</Link>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-[calc(100vh-5rem)] px-4 py-12 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
      <div className="max-w-lg mx-auto step-content space-y-6 animate-fade-in">
        
        {/* Success Header */}
        <div className="card-step p-8 text-center">
          <div 
            className="w-16 h-16 rounded-full flex items-center justify-center mx-auto mb-6"
            style={{ backgroundColor: "#D1FAE5" }}
          >
            <svg className="w-8 h-8" style={{ color: "#065F46" }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold mb-2" style={{ color: "var(--text-primary)" }}>
            Appeal Submitted
          </h1>
          <p className="mb-6" style={{ color: "var(--text-secondary)" }}>
            Your appeal documents have been received and are being processed.
          </p>

          {/* Reference ID */}
          <div 
            className="inline-block p-4 rounded-lg"
            style={{ backgroundColor: "var(--bg-subtle)" }}
          >
            <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Reference ID</p>
            <p style={{ color: "var(--text-primary)", fontFamily: "monospace", fontSize: "1.25rem", fontWeight: 600 }}>
              {paymentData?.clerical_id}
            </p>
          </div>
        </div>

        {/* Details */}
        <div className="card-step p-6">
          <h2 className="text-lg font-semibold mb-4" style={{ color: "var(--text-primary)" }}>Submission Details</h2>
          <div className="space-y-3">
            <div className="flex justify-between py-2" style={{ borderBottom: "1px solid var(--border)" }}>
              <span style={{ color: "var(--text-secondary)" }}>Citation</span>
              <span style={{ color: "var(--text-primary)", fontFamily: "monospace" }}>{paymentData?.citation_number}</span>
            </div>
            <div className="flex justify-between py-2" style={{ borderBottom: "1px solid var(--border)" }}>
              <span style={{ color: "var(--text-secondary)" }}>Amount paid</span>
              <span style={{ color: "var(--text-primary)", fontWeight: 500 }}>{formatAmount(paymentData?.amount_total || 0)}</span>
            </div>
            <div className="flex justify-between py-2">
              <span style={{ color: "var(--text-secondary)" }}>Status</span>
              <span style={{ color: "#065F46", fontWeight: 500 }}>Submitted</span>
            </div>
          </div>
        </div>

        {/* Next Steps */}
        <div className="card-step p-6">
          <h2 className="text-lg font-semibold mb-4" style={{ color: "var(--text-primary)" }}>What Happens Next</h2>
          <div className="space-y-4">
            <div className="flex gap-3">
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: "var(--accent)", color: "white", fontSize: "0.875rem" }}>1</div>
              <div>
                <p style={{ color: "var(--text-primary)", fontWeight: 500 }}>Appeal being prepared</p>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>We format your documents for procedural compliance.</p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: "var(--bg-subtle)", color: "var(--text-muted)", fontSize: "0.875rem" }}>2</div>
              <div>
                <p style={{ color: "var(--text-primary)", fontWeight: 500 }}>Mailed via certified mail</p>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>Your appeal will be mailed within 1-2 business days.</p>
              </div>
            </div>
            <div className="flex gap-3">
              <div className="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style={{ backgroundColor: "var(--bg-subtle)", color: "var(--text-muted)", fontSize: "0.875rem" }}>3</div>
              <div>
                <p style={{ color: "var(--text-primary)", fontWeight: 500 }}>Municipal review</p>
                <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>The city will respond to your mailing address.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Warning */}
        <div className="p-4 rounded-lg" style={{ backgroundColor: "#FEF3C7" }}>
          <h3 className="font-semibold mb-2" style={{ color: "#92400E" }}>What to know</h3>
          <ul style={{ color: "#92400E", fontSize: "0.875rem" }} className="space-y-1">
            <li>• Response times vary by city (typically 2-8 weeks)</li>
            <li>• The municipal authority will mail their response to you</li>
            <li>• This is document preparation only—not legal advice</li>
          </ul>
        </div>

        {/* Support */}
        <div className="card-step p-6 text-center">
          <p style={{ color: "var(--text-secondary)", marginBottom: "1rem" }}>Questions about your submission?</p>
          <a href={`mailto:${process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}`} style={{ color: "var(--accent)" }}>Contact support</a>
        </div>

        <LegalDisclaimer variant="compact" />

        {/* Actions */}
        <div className="text-center">
          <Link href="/" className="btn-strike">
            Submit Another Citation →
          </Link>
        </div>
      </div>
    </main>
  );
}

export default function SuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="min-h-[calc(100vh-5rem)] flex items-center justify-center theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
          <div className="text-center">
            <div 
              className="animate-spin rounded-full h-10 w-10 mx-auto mb-4"
              style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }}
            />
            <p style={{ color: "var(--text-secondary)" }}>Loading...</p>
          </div>
        </div>
      }
    >
      <SuccessContent />
    </Suspense>
  );
}
