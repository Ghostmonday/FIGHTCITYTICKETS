"use client";

import { useSearchParams, useRouter } from "next/navigation";
import { useEffect, useState, Suspense } from "react";
import { useAppeal } from "../../lib/appeal-context";

export const dynamic = "force-dynamic";

function ResumePageContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const { loadFromDatabase } = useAppeal();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const resume = async () => {
      const token = searchParams.get("token");
      const intakeId = searchParams.get("intake_id");

      if (!token || !intakeId) {
        setError("Invalid resume link. Missing token or intake ID.");
        setLoading(false);
        return;
      }

      try {
        const success = await loadFromDatabase(parseInt(intakeId), token);
        if (success) {
          // Determine where to redirect based on state
          // For now, redirect to review as a safe default, or maybe check fields
          router.push("/appeal/review");
        } else {
          setError("Failed to load appeal. The link may have expired.");
        }
      } catch (e) {
        setError("An error occurred while resuming your appeal.");
      } finally {
        setLoading(false);
      }
    };

    resume();
  }, [searchParams, loadFromDatabase, router]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 mx-auto mb-4" style={{ borderColor: "var(--accent)", borderTopColor: "transparent" }} />
          <p style={{ color: "var(--text-secondary)" }}>Resuming your appeal...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
        <div className="max-w-md p-6 bg-white rounded-lg shadow-lg text-center">
          <div className="mx-auto w-12 h-12 rounded-full bg-red-100 flex items-center justify-center mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <h2 className="text-xl font-bold mb-2 text-gray-900">Unable to Resume</h2>
          <p className="text-gray-600 mb-6">{error}</p>
          <button
            onClick={() => router.push("/")}
            className="btn-primary w-full"
          >
            Start New Appeal
          </button>
        </div>
      </div>
    );
  }

  return null;
}

export default function ResumePage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <ResumePageContent />
    </Suspense>
  );
}
