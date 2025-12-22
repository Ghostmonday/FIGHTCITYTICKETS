"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import Link from "next/link";
import { useAppeal } from "../../lib/appeal-context";

function ReviewPageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const appealType = searchParams.get("type") || "standard";
  const { state, updateState } = useAppeal();

  const [draftText, setDraftText] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [isRefining, setIsRefining] = useState(false);
  const [originalText, setOriginalText] = useState("");

  useEffect(() => {
    // If draftLetter exists, use it. Otherwise, generate one from transcript and metadata.
    if (state.draftLetter) {
      setDraftText(state.draftLetter);
      setOriginalText(state.draftLetter);
    } else {
      const { citationNumber, violationDate, transcript } = state;
      const initialDraft = `Dear SFMTA Citation Review,

I am writing to appeal parking citation #${citationNumber || "912345678"} issued on ${violationDate || "[DATE]"}.

On the date of the violation, I parked my vehicle in what I believed to be a legal parking space. ${transcript || "[YOUR STORY WILL BE INSERTED HERE]"}

I respectfully request that this citation be dismissed.

Thank you for your consideration.

Sincerely,
[YOUR NAME]`;
      setDraftText(initialDraft);
      setOriginalText(initialDraft);
    }
  }, [state]);

  const handleRefine = async () => {
    setIsRefining(true);
    try {
      const { refineStatement } = await import("../../lib/api");
      const result = await refineStatement({
        transcript: draftText,
        citation_number: state.citationNumber || "912345678",
      });

      if (result.success && result.refined_text) {
        setDraftText(result.refined_text);
        setIsEditing(false);
      } else {
        alert(
          result.error_message ||
            "Failed to refine letter. You can continue editing manually."
        );
      }
    } catch (error) {
      console.error("Refinement error:", error);
      alert("Failed to refine letter. You can continue editing manually.");
    } finally {
      setIsRefining(false);
    }
  };

  const handleReset = () => {
    setDraftText(originalText);
    setIsEditing(false);
  };

  const handleContinue = () => {
    updateState({ draftLetter: draftText });
    router.push(`/appeal/signature?type=${appealType}`);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/appeal/voice"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-4">
            Review Your Appeal Letter
          </h1>
          <p className="text-gray-600 mt-2">
            Step 4 of 5: Review and edit your professionally formatted letter
          </p>
        </div>

        {/* Letter Editor */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">
              Your Appeal Letter
            </h2>
            <div className="flex gap-2">
              {!isEditing ? (
                <>
                  <button
                    onClick={() => setIsEditing(true)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
                  >
                    Edit
                  </button>
                  <button
                    onClick={handleRefine}
                    disabled={isRefining}
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg disabled:opacity-50"
                  >
                    {isRefining ? "Refining..." : "Polish with AI"}
                  </button>
                </>
              ) : (
                <button
                  onClick={handleReset}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 font-medium hover:bg-gray-50"
                >
                  Reset
                </button>
              )}
            </div>
          </div>

          <textarea
            value={draftText}
            onChange={(e) => setDraftText(e.target.value)}
            readOnly={!isEditing}
            className={`w-full h-96 px-4 py-2 border rounded-lg font-mono text-sm ${
              isEditing
                ? "border-indigo-500 focus:ring-2 focus:ring-indigo-500"
                : "border-gray-300 bg-gray-50"
            }`}
          />

          <div className="mt-4 flex justify-between items-center">
            <p className="text-sm text-gray-500">
              {draftText.length} characters
            </p>
            {isEditing && (
              <button
                onClick={() => setIsEditing(false)}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg"
              >
                Save Changes
              </button>
            )}
          </div>
        </div>

        {/* UPL Disclaimer */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded mb-6">
          <p className="text-sm text-gray-700">
            <strong>Legal Notice:</strong> This letter is generated based on
            your input. We do not provide legal advice, recommend specific
            arguments, or promise outcomes. You are responsible for the content
            of your appeal.
          </p>
        </div>

        {/* Navigation */}
        <div className="flex gap-4">
          <Link
            href="/appeal/voice"
            className="flex-1 px-6 py-3 border border-gray-300 rounded-lg text-gray-700 font-medium text-center hover:bg-gray-50 transition-colors"
          >
            ← Back
          </Link>
          <button
            onClick={handleContinue}
            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors"
          >
            Continue to Signature →
          </button>
        </div>
      </div>
    </div>
  );
}

export default function ReviewPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ReviewPageContent />
    </Suspense>
  );
}
