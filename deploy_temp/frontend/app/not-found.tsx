"use client";

import Link from "next/link";

export default function NotFound() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="max-w-md w-full bg-white rounded-lg shadow-lg p-8 text-center">
        <div className="mb-6">
          <span className="text-8xl font-bold text-green-600">4</span>
          <span className="text-8xl font-bold text-gray-300">0</span>
          <span className="text-8xl font-bold text-green-600">4</span>
        </div>

        <h1 className="text-2xl font-bold text-gray-800 mb-4">
          Page Not Found
        </h1>

        <p className="text-gray-600 mb-6">
          Sorry, we couldn&apos;t find the page you&apos;re looking for. It may have
          been moved or doesn&apos;t exist.
        </p>

        <div className="space-y-3">
          <Link
            href="/"
            className="block w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-bold py-3 px-6 rounded-lg transition"
          >
            Go Home
          </Link>

          <Link
            href="/appeal"
            className="block w-full bg-white border-2 border-gray-200 hover:border-green-500 text-gray-700 hover:text-green-600 font-semibold py-3 px-6 rounded-lg transition"
          >
            Start an Appeal
          </Link>
        </div>

        <div className="mt-8 pt-6 border-t border-gray-100">
          <p className="text-sm text-gray-500">
            Need help?{" "}
            <Link href="/contact" className="text-green-600 hover:underline">
              Contact us
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
