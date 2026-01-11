"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

// Force dynamic rendering - this page uses client-side context
export const dynamic = "force-dynamic";

export default function ReviewPage() {
  const router = useRouter();
  const { state, updateState } = useAppeal();
  const [draft, setDraft] = useState(state.draftLetter || "");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!draft && state.citationNumber) {
      generateDraft();
    }
  }, []);

  const generateDraft = async () => {
    setLoading(true);
    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/api/statement/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          citation_number: state.citationNumber,
          appeal_reason:
            state.transcript || "I believe this citation was issued in error.",
        }),
      });
      const data = await response.json();
      setDraft(data.refined_text || data.draft_text || "");
      updateState({ draftLetter: data.refined_text || data.draft_text || "" });
    } catch (e) {
      setDraft("I am appealing this parking citation because...");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h1 className="text-2xl font-bold mb-4">
            Review Your Procedural Submission
          </h1>

          <div className="mb-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
            <p className="text-sm text-gray-600 leading-relaxed">
              Our{" "}
              <span className="font-semibold text-stone-800">
                Clerical Engine™
              </span>{" "}
              has refined your articulation for maximum procedural compliance.
              Review the letter below to ensure it accurately represents your
              position.
            </p>
          </div>

          <LegalDisclaimer variant="compact" className="mb-6" />

          {loading ? (
            <div className="text-center py-8">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-gray-900 mb-4"></div>
              <p className="text-gray-600">
                Processing via Clerical Engine™...
              </p>
            </div>
          ) : (
            <>
              <textarea
                value={draft}
                onChange={(e) => {
                  setDraft(e.target.value);
                  updateState({ draftLetter: e.target.value });
                }}
                className="w-full h-64 p-4 border rounded-lg mb-6 font-mono text-sm"
                placeholder="Your appeal letter will appear here..."
              />

              <div className="flex justify-between items-center">
                <Link
                  href="/appeal/camera"
                  className="text-gray-600 hover:text-gray-800 transition-colors"
                >
                  ← Back
                </Link>
                <button
                  onClick={() => router.push("/appeal/signature")}
                  className="bg-stone-800 text-white px-6 py-3 rounded-lg hover:bg-stone-900 transition-colors font-medium"
                >
                  Continue to Signature →
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
