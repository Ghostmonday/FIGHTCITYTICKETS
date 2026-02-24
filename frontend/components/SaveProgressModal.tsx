"use client";

import { useState } from "react";
import { useAppeal } from "../app/lib/appeal-context";

interface SaveProgressModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function SaveProgressModal({ isOpen, onClose }: SaveProgressModalProps) {
  const { state, updateState, sendResumeLink } = useAppeal();
  const [email, setEmail] = useState(state.userInfo.email || "");
  const [sending, setSending] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setSending(true);
    setError("");

    try {
      // If email changed, update it in state
      if (email !== state.userInfo.email) {
        updateState({ userInfo: { ...state.userInfo, email } });
      }

      const sent = await sendResumeLink(email);
      if (sent) {
        setSuccess(true);
      } else {
        setError("Failed to send email. Please try again.");
      }
    } catch (e) {
      setError("An error occurred. Please try again.");
    } finally {
      setSending(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4">
      <div
        className="w-full max-w-md rounded-lg p-6 shadow-xl theme-transition"
        style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
      >
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold" style={{ color: "var(--text-primary)" }}>
            Save & Resume Later
          </h2>
          <button
            onClick={onClose}
            className="text-2xl leading-none hover:opacity-70"
            style={{ color: "var(--text-muted)" }}
          >
            &times;
          </button>
        </div>

        {success ? (
          <div className="text-center py-4">
            <div className="mx-auto w-12 h-12 rounded-full bg-green-100 flex items-center justify-center mb-4">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="font-medium mb-2" style={{ color: "var(--text-primary)" }}>Link Sent!</p>
            <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
              Check your email for a link to resume your appeal.
            </p>
            <button
              onClick={onClose}
              className="btn-primary w-full"
            >
              Close
            </button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <p className="mb-4" style={{ color: "var(--text-secondary)" }}>
              We'll send you a secure link to continue your appeal exactly where you left off.
            </p>

            <div className="mb-4">
              <label
                htmlFor="resume-email"
                className="block text-sm font-medium mb-1"
                style={{ color: "var(--text-primary)" }}
              >
                Email Address
              </label>
              <input
                id="resume-email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                className="w-full p-2 rounded border"
                style={{
                  backgroundColor: "var(--bg-page)",
                  borderColor: "var(--border)",
                  color: "var(--text-primary)"
                }}
              />
            </div>

            {error && (
              <p className="mb-4 text-sm text-red-500">{error}</p>
            )}

            <div className="flex gap-3">
              <button
                type="button"
                onClick={onClose}
                className="btn-secondary flex-1"
              >
                Cancel
              </button>
              <button
                type="submit"
                disabled={sending || !email}
                className="btn-primary flex-1"
              >
                {sending ? "Sending..." : "Send Link"}
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
}
