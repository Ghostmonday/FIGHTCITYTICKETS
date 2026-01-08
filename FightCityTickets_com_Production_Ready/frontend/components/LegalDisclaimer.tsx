"use client";

import { useState } from "react";

interface LegalDisclaimerProps {
  variant?: "full" | "compact" | "inline" | "elegant";
  className?: string;
}

export default function LegalDisclaimer({ variant = "elegant", className = "" }: LegalDisclaimerProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const disclaimerText = {
    full: (
      <div className="space-y-3 text-sm text-gray-600 leading-relaxed">
        <p>
          FightCityTickets.com is a document preparation service. We help you articulate and refine 
          your own reasons for appealing a parking ticket. We act as a scribe, helping you express 
          what <strong className="text-gray-800">you</strong> tell us is your reason for appealing.
        </p>
        <p>
          We are not a law firm, and we do not provide legal advice, legal representation, or legal 
          recommendations. We do not suggest legal strategies, interpret laws, or guarantee outcomes. 
          The decision to appeal and the arguments presented are entirely yours.
        </p>
        <p className="text-xs text-gray-500 italic">
          If you require legal advice, please consult with a licensed attorney.
        </p>
      </div>
    ),
    compact: (
      <p className="text-xs text-gray-500 leading-relaxed">
        FightCityTickets.com is a document preparation service. We help you articulate your own reasons 
        for appealing. We are not a law firm and do not provide legal advice.{" "}
        <a href="/terms" className="text-gray-700 hover:text-gray-900 underline underline-offset-2">
          Terms
        </a>
      </p>
    ),
    inline: (
      <span className="text-xs text-gray-400 italic">
        Document preparation service. Not a law firm.
      </span>
    ),
    elegant: (
      <div className="space-y-2 text-sm text-gray-600 leading-relaxed">
        <p>
          FightCityTickets.com is a document preparation service that helps you articulate your own 
          reasons for appealing a parking ticket. We refine and format the information you provide 
          to create a professional appeal letter.
        </p>
        <p className="text-xs text-gray-500 border-t border-gray-100 pt-2">
          We are not a law firm and do not provide legal advice. For legal guidance, consult a licensed attorney.
        </p>
      </div>
    ),
  };

  if (variant === "inline") {
    return <span className={className}>{disclaimerText.inline}</span>;
  }

  if (variant === "compact") {
    return (
      <div className={`border-t border-gray-100 pt-4 ${className}`}>
        {disclaimerText.compact}
      </div>
    );
  }

  if (variant === "elegant") {
    return (
      <div className={`bg-gray-50 border border-gray-200 rounded-lg p-5 ${className}`}>
        {disclaimerText.elegant}
      </div>
    );
  }

  return (
    <div className={`bg-gray-50 border border-gray-200 rounded-lg p-5 ${className}`}>
      {!isExpanded ? (
        <div>
          <p className="text-sm text-gray-700 mb-2">
            FightCityTickets.com is a document preparation service. We help you articulate your own 
            reasons for appealing. We are not a law firm and do not provide legal advice.
          </p>
          <button
            onClick={() => setIsExpanded(true)}
            className="text-xs text-gray-600 hover:text-gray-800 underline underline-offset-2"
          >
            Read more
          </button>
        </div>
      ) : (
        <div>
          {disclaimerText.full}
          <button
            onClick={() => setIsExpanded(false)}
            className="mt-3 text-xs text-gray-600 hover:text-gray-800 underline underline-offset-2"
          >
            Show less
          </button>
        </div>
      )}
    </div>
  );
}

