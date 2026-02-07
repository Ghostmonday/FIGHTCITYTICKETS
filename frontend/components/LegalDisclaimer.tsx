"use client";

import Link from "next/link";
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
      <div className="space-y-3 text-body-sm text-text-secondary leading-relaxed">
        <p>
          <strong className="text-text-primary">
            We aren&apos;t lawyers. We&apos;re paperwork experts.
          </strong>{" "}
          In a bureaucracy, paperwork is power. We help you articulate and
          refine your own reasons for appealing a parking ticket. We act as a
          scribe, helping you express what{" "}
          <strong className="text-text-primary">you</strong> tell us is your
          reason for appealing.
        </p>
        <p>
          FightCityTickets.com is a{" "}
          <strong>document preparation service</strong>. We do not provide legal
          advice, legal representation, or legal recommendations. We do not
          interpret laws or guarantee outcomes. We ensure your appeal meets the
          clerical standards that municipalities use.
        </p>
        <p className="text-tiny text-text-muted italic border-t border-border pt-3">
          If you require legal advice, please consult with a licensed attorney.
        </p>
      </div>
    ),
    compact: (
      <p className="text-tiny text-text-muted leading-relaxed">
        <strong className="text-text-secondary">
          Document preparation only — not legal advice.
        </strong>{" "}
        We help you prepare appeal paperwork but don&apos;t provide legal advice
        or representation.{" "}
        <Link
          href="/terms"
          className="text-text-secondary hover:text-text-primary underline underline-offset-2"
        >
          Learn more
        </Link>
      </p>
    ),
    inline: (
      <span className="text-tiny text-text-muted italic">
        Document preparation only — not legal advice
      </span>
    ),
    elegant: (
      <div className="space-y-3 text-body-sm text-text-secondary leading-relaxed">
        <p>
          <strong className="text-text-primary">
            Document preparation only — not legal advice.
          </strong>{" "}
          We help you prepare appeal paperwork but don&apos;t provide legal
          advice, legal representation, or recommendations.
        </p>
        <p className="text-tiny text-text-muted border-t border-border pt-3">
          FightCityTickets.com is a{" "}
          <strong>document preparation service</strong>. Outcome determined by
          the municipal authority.
        </p>
      </div>
    ),
  };

  if (variant === "inline") {
    return <span className={className}>{disclaimerText.inline}</span>;
  }

  if (variant === "compact") {
    return (
      <div className={`border-t border-border pt-4 ${className}`}>
        {disclaimerText.compact}
      </div>
    );
  }

  if (variant === "elegant") {
    return (
      <div
        className={`bg-bg-subtle border border-border rounded-lg p-5 ${className}`}
      >
        {disclaimerText.elegant}
      </div>
    );
  }

  return (
    <div
      className={`bg-bg-subtle border border-border rounded-lg p-5 ${className}`}
    >
      {!isExpanded ? (
        <div>
          <p className="text-body-sm text-text-secondary mb-2">
            <strong>Document preparation only — not legal advice.</strong> We
            help you prepare appeal paperwork but don&apos;t provide legal
            representation.
          </p>
          <button
            onClick={() => setIsExpanded(true)}
            className="text-tiny text-text-secondary hover:text-text-primary underline underline-offset-2 transition-colors"
          >
            Learn more
          </button>
        </div>
      ) : (
        <div>
          {disclaimerText.full}
          <button
            onClick={() => setIsExpanded(false)}
            className="mt-3 text-tiny text-text-secondary hover:text-text-primary underline underline-offset-2 transition-colors"
          >
            Show less
          </button>
        </div>
      )}
    </div>
  );
}
