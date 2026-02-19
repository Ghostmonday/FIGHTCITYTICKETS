"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

export const dynamic = "force-dynamic";

export default function ReviewPage() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [draft, setDraft] = useState(state.draftLetter || "");
  const [loading, setLoading] = useState(false);
  const [isRefining, setIsRefining] = useState(false);

  useEffect(() => {
    if (!draft && state.citationNumber) {
      generateDraft();
    }
  }, []);

  const generateDraft = async () => {
    setLoading(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/statement/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_statement: state.transcript || "I believe this citation was issued in error.",
          citation_number: state.citationNumber,
        }),
      });
      const data = await response.json();
      const text = data.refined_statement || data.refined_text || data.draft_text || "";
      setDraft(text);
      updateState({ draftLetter: text });
    } catch (e) {
      setDraft("I am appealing this parking citation because...");
    } finally {
      setLoading(false);
    }
  };

  const handleRefineWithAI = async () => {
    setIsRefining(true);
    try {
      const apiBase = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/statement/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ original_statement: draft, citation_number: state.citationNumber }),
      });
      const data = await response.json();
      const text = data.refined_statement || data.refined_text || "";
      if (text) {
        setDraft(text);
        updateState({ draftLetter: text });
      }
    } catch (e) {
      console.error("Refinement failed:", e);
    } finally {
      setIsRefining(false);
    }
  };

  const handleContinue = () => {
    updateState({ draftLetter: draft });
    router.push("/appeal/signature");
  };

  return (
    <main className="min-h-[calc(100vh-5rem)] px-4 py-8 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
      <div className="max-w-lg mx-auto step-content">
        
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2 theme-transition" style={{ color: "var(--text-primary)" }}>
            Review Your Appeal
          </h1>
          <p className="theme-transition" style={{ color: "var(--text-secondary)" }}>
            Review and edit your statement before signing
          </p>
        </div>

        {/* Summary Card */}
        <div className="card-step p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4 theme-transition" style={{ color: "var(--text-primary)" }}>
            Appeal Details
          </h2>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Citation</p>
              <p style={{ color: "var(--text-primary)", fontFamily: "monospace", fontWeight: 500 }}>
                {state.citationNumber || "Not provided"}
              </p>
            </div>
            <div>
              <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Photos</p>
              <p style={{ color: "var(--text-primary)", fontWeight: 500 }}>
                {state.photos?.length || 0} photo(s)
              </p>
            </div>
          </div>
        </div>

        {/* Statement Card */}
        <div className="card-step p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold theme-transition" style={{ color: "var(--text-primary)" }}>
              Your Statement
            </h2>
            <button
              onClick={handleRefineWithAI}
              disabled={!draft || draft.length < 10 || isRefining}
              className="btn-secondary text-sm py-2 px-4"
              style={{ opacity: (!draft || draft.length < 10) ? 0.5 : 1 }}
            >
              {isRefining ? "Refining..." : "Refine with AI"}
            </button>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div 
                className="animate-spin rounded-full h-8 w-8 mx-auto mb-3"
                style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }}
              />
              <p style={{ color: "var(--text-secondary)" }}>Generating your appeal statement...</p>
            </div>
          ) : (
            <>
              <textarea
                value={draft}
                onChange={(e) => {
                  setDraft(e.target.value);
                  updateState({ draftLetter: e.target.value });
                }}
                className="w-full h-64 p-4 rounded-input resize-none"
                style={{ 
                  backgroundColor: "var(--bg-surface)", 
                  border: "2px solid var(--border)",
                  color: "var(--text-primary)",
                }}
                placeholder="Describe why you're appealing..."
              />
              <div className="flex justify-between mt-4">
                <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>{draft.length} characters</p>
                <p style={{ color: "var(--text-muted)", fontSize: "0.875rem" }}>Appears on your official document</p>
              </div>
            </>
          )}
        </div>

        {/* Tips */}
        <div 
          className="p-4 rounded-lg mb-6"
          style={{ backgroundColor: "var(--bg-subtle)", border: "1px solid var(--border)" }}
        >
          <h3 className="font-semibold mb-2" style={{ color: "var(--text-primary)" }}>Tips for a stronger appeal</h3>
          <ul className="space-y-1" style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>
            <li>• Be factual and specific about what happened</li>
            <li>• Include relevant dates, times, and locations</li>
            <li>• Keep it concise and relevant</li>
          </ul>
        </div>

        {/* Actions */}
        <div className="flex gap-4 mb-6">
          <Link href="/appeal/camera" className="btn-secondary flex-1">
            ← Back
          </Link>
          <button onClick={handleContinue} className="btn-strike flex-1">
            Continue to Signature →
          </button>
        </div>

        <LegalDisclaimer variant="compact" />
      </div>
    </main>
  );
}
