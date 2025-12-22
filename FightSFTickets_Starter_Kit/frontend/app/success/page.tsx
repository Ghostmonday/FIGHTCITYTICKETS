"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

function SuccessPageContent() {
  const searchParams = useSearchParams();
  const sessionId = searchParams.get("session_id");

  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="container mx-auto px-4 max-w-2xl text-center">
        {/* Success Icon */}
        <div className="mb-8">
          <div className="mx-auto w-24 h-24 bg-green-100 rounded-full flex items-center justify-center">
            <svg
              className="w-12 h-12 text-green-600"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M5 13l4 4L19 7"
              />
            </svg>
          </div>
        </div>

        {/* Success Message */}
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Appeal Submitted Successfully!
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Your appeal letter has been sent to SFMTA
        </p>

        {/* What Happens Next */}
        <div className="bg-white rounded-lg shadow-md p-8 mb-8 text-left">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            What Happens Next?
          </h2>
          <div className="space-y-4">
            <div className="flex items-start">
              <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0">
                <span className="text-indigo-600 font-semibold">1</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  Letter Mailed
                </h3>
                <p className="text-gray-600">
                  Your appeal letter will be printed and mailed within 1-2
                  business days.
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0">
                <span className="text-indigo-600 font-semibold">2</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  Delivery Timeline
                </h3>
                <p className="text-gray-600">
                  Standard mail: 3-5 business days. Certified mail: 2-3 business
                  days with tracking.
                </p>
              </div>
            </div>
            <div className="flex items-start">
              <div className="bg-indigo-100 rounded-full w-8 h-8 flex items-center justify-center mr-4 flex-shrink-0">
                <span className="text-indigo-600 font-semibold">3</span>
              </div>
              <div>
                <h3 className="font-semibold text-gray-900 mb-1">
                  SFMTA Review
                </h3>
                <p className="text-gray-600">
                  SFMTA typically responds within 21-30 days. You'll receive
                  notification by mail.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Receipt Info */}
        {sessionId && (
          <div className="bg-gray-100 rounded-lg p-6 mb-8">
            <p className="text-sm text-gray-600 mb-2">Payment Session ID</p>
            <p className="font-mono text-sm text-gray-900 break-all">
              {sessionId}
            </p>
            <p className="text-sm text-gray-600 mt-4">
              A receipt has been sent to your email address.
            </p>
          </div>
        )}

        {/* Actions */}
        <div className="space-y-4">
          <Link
            href="/"
            className="inline-block bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-8 rounded-lg transition-colors"
          >
            Return to Home
          </Link>
          <p className="text-sm text-gray-600">
            Need help? Contact us at{" "}
            <a
              href="mailto:support@fightsftickets.com"
              className="text-indigo-600 hover:text-indigo-700"
            >
              support@fightsftickets.com
            </a>
          </p>
        </div>
      </div>
    </div>
  );
}

export default function SuccessPage() {
  return (
    <Suspense fallback={<div>Loading...</div>}>
      <SuccessPageContent />
    </Suspense>
  );
}
