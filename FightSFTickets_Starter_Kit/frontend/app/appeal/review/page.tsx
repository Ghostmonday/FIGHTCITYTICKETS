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
  const [userStory, setUserStory] = useState(state.transcript || "");

  // Agency-specific salutations
  const agencySalutations: Record<string, string> = {
    SFMTA: "SFMTA Citation Review",
    SFPD: "San Francisco Police Department - Traffic Division",
    SFSU: "San Francisco State University - Parking & Transportation",
    SFMUD: "San Francisco Municipal Utility District",
    UNKNOWN: "Citation Review Department",
  };

  // Agency display names
  const agencyDisplayNames: Record<string, string> = {
    SFMTA: "SFMTA (San Francisco Municipal Transportation Agency)",
    SFPD: "San Francisco Police Department",
    SFSU: "San Francisco State University",
    SFMUD: "San Francisco Municipal Utility District",
    UNKNOWN: "San Francisco Parking Citation Agency",
  };

  const currentAgency = state.agency || "UNKNOWN";
  const salutation = agencySalutations[currentAgency];

  useEffect(() => {
    // If draftLetter exists, use it. Otherwise, generate one from user story and metadata.
    if (state.draftLetter) {
      setDraftText(state.draftLetter);
      setOriginalText(state.draftLetter);
    } else {
      // Auto-refine if we have a user story but no draft yet
      const generateDraft = async () => {
        setIsRefining(true);
        try {
          const { refineStatement } = await import("../../lib/api");
          const result = await refineStatement({
            original_statement:
              userStory || "I am writing to appeal this ticket.",
            citation_number: state.citationNumber || "912345678",
          });

          if (result.success && result.refined_text) {
            setDraftText(result.refined_text);
            setOriginalText(result.refined_text);
            updateState({ draftLetter: result.refined_text });
          } else {
            // Fallback to template if API fails
            const initialDraft = `Dear SFMTA Citation Review,\n\nI am writing to appeal parking citation #${state.citationNumber || "912345678"}.\n\n${userStory || "[YOUR STORY]"}\n\nSincerely,\n[YOUR NAME]`;
            setDraftText(initialDraft);
            setOriginalText(initialDraft);
          }
        } catch (e) {
          console.error("Auto-draft generation error:", e);
          // Fallback to template if API fails
          const initialDraft = `Dear ${salutation},\n\nI am writing to appeal parking citation #${state.citationNumber || "912345678"}.\n\n${userStory || "[YOUR STORY]"}\n\nSincerely,\n[YOUR NAME]`;
          setDraftText(initialDraft);
          setOriginalText(initialDraft);
        } finally {
          setIsRefining(false);
        }
      };

      if (userStory) {
        generateDraft();
      } else {
        // No user story, just set placeholder
        const initialDraft = `Dear ${salutation},\n\nI am writing to appeal parking citation #${state.citationNumber || "912345678"}.\n\n[YOUR STORY]\n\nSincerely,\n[YOUR NAME]`;
        setDraftText(initialDraft);
        setOriginalText(initialDraft);
      }
    }
  }, [state.draftLetter]); // Only run if draftLetter status changes (or initially)

  const handleRefine = async () => {
    setIsRefining(true);
    try {
      const { refineStatement } = await import("../../lib/api");

      // Use userStory if available, otherwise use draftText
      const textToRefine = userStory.trim() || draftText;

      const result = await refineStatement({
        original_statement: textToRefine,
        citation_number: state.citationNumber || "912345678",
      });

      if (result.success && result.refined_text) {
        setDraftText(result.refined_text);
        setOriginalText(result.refined_text);
        updateState({ draftLetter: result.refined_text });
        setIsEditing(false);

        // Also update the transcript if we used userStory
        if (userStory.trim()) {
          updateState({ transcript: userStory });
        }
      } else {
        alert(
          result.error_message ||
            "Failed to polish letter. The AI service might be temporarily unavailable. You can continue editing manually.",
        );
      }
    } catch (error) {
      console.error("Refinement error:", error);
      alert(
        "Failed to connect to AI service. This might be a temporary issue. " +
          "You can continue with the current draft or try again in a moment.",
      );
    } finally {
      setIsRefining(false);
    }
  };

  // Removed handleUpdateStory function - not needed

  const handleReset = () => {
    setDraftText(originalText);
    setIsEditing(false);
  };

  const handleContinue = () => {
    // Always save the current draft text, whether polished or not
    try {
      updateState({ draftLetter: draftText });
      if (userStory.trim()) {
        updateState({ transcript: userStory });
      }
      router.push(`/appeal/signature?type=${appealType}`);
    } catch (error) {
      console.error("Continue error:", error);
      alert("Failed to save draft. Please try again.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Header */}
        <div className="mb-8">
          <Link
            href="/appeal/camera"
            className="text-indigo-600 hover:text-indigo-700 font-medium"
          >
            ← Back
          </Link>
          <h1 className="text-3xl font-bold text-gray-900 mt-4">
            Review Your Appeal Letter
          </h1>
          <p className="text-gray-600 mt-2">
            Step 3 of 5: Tell your story and review your appeal letter
          </p>
          <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-200">
            <div className="flex justify-between items-center">
              <div>
                <p className="text-sm font-medium text-gray-700">
                  Citation #{state.citationNumber || "Not provided"}
                </p>
                <p className="text-sm text-gray-600">
                  Agency: {agencyDisplayNames[currentAgency]}
                </p>
              </div>
              <div className="text-right">
                <p className="text-xs text-gray-500">
                  Appeal type:{" "}
                  {appealType === "certified"
                    ? "Certified Mail ($19)"
                    : "Standard Mail ($9)"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* User Story Input */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Tell Your Story
          </h2>
          <p className="text-gray-600 mb-4">
            Describe what happened and why you believe the citation was issued
            in error. Most phones have built-in voice-to-text if you prefer to
            speak.
          </p>
          <textarea
            value={userStory}
            onChange={(e) => setUserStory(e.target.value)}
            placeholder="Example: The parking meter was broken and wouldn't accept my payment. I tried multiple times but it kept showing an error message..."
            className="w-full h-40 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-gray-900 mb-4"
          />
          <div className="flex justify-between items-center">
            <p className="text-sm text-gray-500">
              {userStory.length} characters
            </p>
            <p className="text-sm text-gray-600">
              Your story will be used for AI refinement
            </p>
          </div>
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
                    className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
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
            className={`w-full h-96 px-4 py-2 border rounded-lg font-mono text-sm text-gray-900 ${
              isEditing
                ? "border-indigo-500 focus:ring-2 focus:ring-indigo-500 bg-white"
                : "border-gray-300 bg-gray-50"
            }`}
            onKeyDown={(e) => {
              // Prevent form submission on Enter key in textarea
              if (e.key === "Enter" && e.ctrlKey) {
                handleContinue();
              }
            }}
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
            href="/appeal/camera"
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
