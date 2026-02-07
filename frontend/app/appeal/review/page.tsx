"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAppeal } from "../../lib/appeal-context";
import Link from "next/link";
import LegalDisclaimer from "../../../components/LegalDisclaimer";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";
import { Alert } from "../../../components/ui/Alert";

// Force dynamic rendering - this page uses client-side context
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
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/statement/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_statement:
            state.transcript || "I believe this citation was issued in error.",
          citation_number: state.citationNumber,
        }),
      });
      const data = await response.json();
      setDraft(
        data.refined_statement || data.refined_text || data.draft_text || ""
      );
      updateState({
        draftLetter:
          data.refined_statement || data.refined_text || data.draft_text || "",
      });
    } catch (e) {
      setDraft("I am appealing this parking citation because...");
    } finally {
      setLoading(false);
    }
  };

  const handleRefineWithAI = async () => {
    setIsRefining(true);
    try {
      const apiBase =
        process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";
      const response = await fetch(`${apiBase}/statement/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_statement: draft,
          citation_number: state.citationNumber,
        }),
      });
      const data = await response.json();
      if (data.refined_statement) {
        setDraft(data.refined_statement);
        updateState({ draftLetter: data.refined_statement });
      } else if (data.refined_text) {
        setDraft(data.refined_text);
        updateState({ draftLetter: data.refined_text });
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
    <main className="min-h-screen bg-bg-page">
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-heading-lg text-text-primary mb-2">
            Review Your Appeal
          </h1>
          <p className="text-body text-text-secondary">
            Review and edit your appeal statement before signing.
          </p>
        </div>

        <div className="space-y-6">
          {/* Summary Card */}
          <Card padding="lg">
            <h2 className="text-heading-md text-text-primary mb-4">
              Appeal Details
            </h2>
            <div className="grid md:grid-cols-2 gap-4 text-body-sm">
              <div>
                <p className="text-text-muted">Citation number</p>
                <p className="font-mono font-medium text-text-primary">
                  {state.citationNumber || "Not provided"}
                </p>
              </div>
              <div>
                <p className="text-text-muted">Photos uploaded</p>
                <p className="font-medium text-text-primary">
                  {state.photos?.length || 0} photo(s)
                </p>
              </div>
            </div>
          </Card>

          {/* Statement Editor */}
          <Card padding="lg">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-heading-md text-text-primary">
                Your Statement
              </h2>
              <Button
                variant="secondary"
                size="sm"
                onClick={handleRefineWithAI}
                loading={isRefining}
                disabled={!draft || draft.length < 10}
              >
                {isRefining ? "Refining..." : "Refine with AI"}
              </Button>
            </div>

            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary border-t-transparent mx-auto mb-3" />
                <p className="text-body text-text-secondary">
                  Generating your appeal statement...
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
                  className="w-full h-64 p-4 bg-bg-surface border border-border rounded-input text-text-primary placeholder-text-muted focus:border-primary focus:ring-2 focus:ring-primary/20 transition-all resize-none"
                  placeholder="Describe why you're appealing..."
                />
                <div className="flex justify-between items-center mt-4">
                  <p className="text-caption text-text-muted">
                    {draft.length} characters
                  </p>
                  <p className="text-caption text-text-muted">
                    This will appear on your official appeal document
                  </p>
                </div>
              </>
            )}
          </Card>

          {/* Tips */}
          <Alert variant="info" title="Tips for a stronger appeal">
            <ul className="space-y-1 text-body-sm">
              <li>• Be factual and specific about what happened</li>
              <li>• Include relevant dates, times, and locations</li>
              <li>• Stick to the relevant details—keep it concise</li>
            </ul>
          </Alert>

          {/* Actions */}
          <div className="flex justify-between items-center pt-4">
            <Link
              href="/appeal/camera"
              className="text-body text-text-secondary hover:text-text-primary transition-colors"
            >
              ← Back to photos
            </Link>
            <Button onClick={handleContinue}>Continue to Signature →</Button>
          </div>

          {/* Legal Disclaimer */}
          <LegalDisclaimer variant="compact" className="mt-6" />
        </div>
      </div>
    </main>
  );
}
