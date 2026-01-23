"use client";

import Link from "next/link";

export default function FooterDisclaimer() {
  return (
    <div className="bg-white border-t border-gray-200 py-6 px-4">
      <div className="max-w-7xl mx-auto">
        <p className="text-xs text-gray-500 text-center leading-relaxed max-w-4xl mx-auto mb-4">
          FIGHTCITYTICKETS.com is a document preparation service that helps you articulate your own 
          reasons for appealing a parking ticket. We refine and format the information you provide 
          to create a professional appeal letter. We are not a law firm and do not provide legal 
          advice, legal representation, or legal recommendations. The decision to appeal and the 
          arguments presented are entirely yours.
        </p>
        <div className="flex flex-wrap justify-center gap-4 text-xs">
          <Link href="/terms" className="text-gray-600 hover:text-gray-900 underline underline-offset-2">
            Terms of Service
          </Link>
          <Link href="/privacy" className="text-gray-600 hover:text-gray-900 underline underline-offset-2">
            Privacy Policy
          </Link>
          <Link href="/refund" className="text-gray-600 hover:text-gray-900 underline underline-offset-2">
            Refund Policy
          </Link>
          <Link href="/appeal/status" className="text-gray-600 hover:text-gray-900 underline underline-offset-2">
            Check Appeal Status
          </Link>
          <a href="mailto:support@fightcitytickets.com" className="text-gray-600 hover:text-gray-900 underline underline-offset-2">
            Support
          </a>
        </div>
        <p className="text-xs text-gray-400 text-center mt-4">
          © {new Date().getFullYear()} FIGHTCITYTICKETS.com - All rights reserved
        </p>
      </div>
    </div>
  );
}

