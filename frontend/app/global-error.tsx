"use client";

import { useEffect } from "react";
import Link from "next/link";

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  useEffect(() => {
    // Log error to console for debugging
    console.error("Global error:", error);
  }, [error]);

  return (
    <html lang="en">
      <body>
        <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="mb-6">
              <svg
                className="mx-auto h-16 w-16 text-red-500"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-stone-800 mb-4">
              System Error
            </h1>
            <p className="text-gray-600 mb-6">
              A critical error occurred. Our team has been notified. Please try
              again later or contact support if the problem persists.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center">
              <button
                onClick={reset}
                className="bg-stone-800 text-white px-6 py-3 rounded-lg hover:bg-stone-900 transition-colors font-medium"
              >
                Try again
              </button>
              <Link
                href="/"
                className="bg-stone-100 text-stone-800 px-6 py-3 rounded-lg hover:bg-stone-200 transition-colors font-medium"
              >
                Go home
              </Link>
            </div>
            <p className="mt-6 text-sm text-gray-500">
              Need help?{" "}
              <a
                href={`mailto:${process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}`}
                className="text-stone-800 hover:underline"
              >
                {process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com"}
              </a>
            </p>
          </div>
        </div>
      </body>
    </html>
  );
}
