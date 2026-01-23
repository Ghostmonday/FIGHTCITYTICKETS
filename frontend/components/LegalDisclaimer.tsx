"use client";

import { useState } from "react";

interface LegalDisclaimerProps {
  variant?: "full" | "compact" | "inline" | "elegant";
  className?: string;
}

export default function LegalDisclaimer({
  variant = "elegant",
  className = "",
}: LegalDisclaimerProps) {
  const [isExpanded, setIsExpanded] = useState(false);

  const disclaimerText = {
    full: (
      <div className="space-y-3 text-sm text-gray-600 leading-relaxed">
        <p>
          <strong className="text-gray-800">
            We aren't lawyers. We're paperwork experts.
          </strong>{" "}
          In a bureaucracy, paperwork is power. We help you articulate and
          refine your own reasons for appealing a parking ticket. We act as a
          scribe, helping you express what{" "}
          <strong className="text-gray-800">you</strong> tell us is your reason
          for appealing.
        </p>
        <p>
          FIGHTCITYTICKETS.com is a{" "}
          <strong>procedural compliance service</strong>. We do not provide
          legal advice, legal representation, or legal recommendations. We do
          not interpret laws or guarantee outcomes. We ensure your appeal meets
          the exacting clerical standards that municipalities use to reject
          citizen submissions.
        </p>
        <p className="text-xs text-gray-500 italic border-t border-gray-200 pt-3">
          If you require legal advice, please consult with a licensed attorney.
        </p>
      </div>
    ),
    compact: (
      <p className="text-xs text-gray-500 leading-relaxed">
        <strong>We aren't lawyers. We're paperwork experts.</strong> We help you
        articulate your own reasons for appealing. Our service is procedural
        compliance—not legal advice.{" "}
        <a
          href="/terms"
          className="text-gray-700 hover:text-gray-900 underline underline-offset-2"
        >
          Terms
        </a>
      </p>
    ),
    inline: (
      <span className="text-xs text-gray-400 italic">
        Procedural compliance service. Not a law firm. Paperwork is power.
      </span>
    ),
    elegant: (
      <div className="space-y-3 text-sm text-gray-600 leading-relaxed">
        <p>
          <strong className="text-gray-800">
            We aren't lawyers. We're paperwork experts.
          </strong>{" "}
          In a bureaucracy, paperwork is power. We help you articulate and
          refine your own reasons for appealing a parking ticket.
        </p>
        <p className="text-xs text-gray-500 border-t border-gray-200 pt-3">
          FIGHTCITYTICKETS.com is a{" "}
          <strong>procedural compliance service</strong>. We do not provide
          legal advice. For legal guidance, consult a licensed attorney.
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
      <div
        className={`bg-gray-50 border border-gray-200 rounded-lg p-5 ${className}`}
      >
        {disclaimerText.elegant}
      </div>
    );
  }

  return (
    <div
      className={`bg-gray-50 border border-gray-200 rounded-lg p-5 ${className}`}
    >
      {!isExpanded ? (
        <div>
          <p className="text-sm text-gray-700 mb-2">
            <strong>We aren't lawyers. We're paperwork experts.</strong> We help
            you articulate your own reasons for appealing. Our service is
            procedural compliance—not legal advice.
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
