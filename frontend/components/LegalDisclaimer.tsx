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

  const baseText = {
    color: "var(--text-secondary)",
    fontSize: "0.875rem",
    lineHeight: "1.6",
  };

  const mutedText = {
    color: "var(--text-muted)",
    fontSize: "0.75rem",
  };

  const disclaimerText = {
    full: (
      <div style={{ ...baseText, display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <p>
          <strong style={{ color: "var(--text-primary)" }}>
            We aren&apos;t lawyers. We&apos;re paperwork experts.
          </strong>{" "}
          In a bureaucracy, paperwork is power. We help you articulate and
          refine your own reasons for appealing a parking ticket. We act as a
          scribe, helping you express what{" "}
          <strong style={{ color: "var(--text-primary)" }}>you</strong> tell us is your
          reason for appealing.
        </p>
        <p>
          FightCityTickets is a{" "}
          <strong>document preparation service</strong>. We do not provide legal
          advice, legal representation, or legal recommendations. We do not
          interpret laws or guarantee outcomes. We ensure your appeal meets the
          clerical standards that municipalities use.
        </p>
        <p style={{ ...mutedText, fontStyle: "italic", borderTop: "1px solid var(--border)", paddingTop: "0.75rem" }}>
          If you require legal advice, please consult with a licensed attorney.
        </p>
      </div>
    ),
    compact: (
      <p style={{ ...mutedText, lineHeight: "1.6" }}>
        <strong style={{ color: "var(--text-secondary)" }}>
          Document preparation only — not legal advice.
        </strong>{" "}
        We help you prepare appeal paperwork but don&apos;t provide legal advice
        or representation.{" "}
        <Link
          href="/terms"
          style={{ color: "var(--text-secondary)", textDecoration: "underline", textUnderlineOffset: "2px" }}
          className="hover:opacity-80 transition-opacity"
        >
          Learn more
        </Link>
      </p>
    ),
    inline: (
      <span style={{ ...mutedText, fontStyle: "italic" }}>
        Document preparation only — not legal advice
      </span>
    ),
    elegant: (
      <div style={{ ...baseText, display: "flex", flexDirection: "column", gap: "0.75rem" }}>
        <p>
          <strong style={{ color: "var(--text-primary)" }}>
            Document preparation only — not legal advice.
          </strong>{" "}
          We help you prepare appeal paperwork but don&apos;t provide legal
          advice, legal representation, or recommendations.
        </p>
        <p style={{ ...mutedText, borderTop: "1px solid var(--border)", paddingTop: "0.75rem" }}>
          FightCityTickets is a{" "}
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
      <div 
        className={`theme-transition ${className}`}
        style={{ 
          borderTop: "1px solid var(--border)", 
          paddingTop: "1rem",
        }}
      >
        {disclaimerText.compact}
      </div>
    );
  }

  if (variant === "elegant") {
    return (
      <div
        className={`theme-transition ${className}`}
        style={{ 
          backgroundColor: "var(--bg-subtle)", 
          border: "1px solid var(--border)", 
          borderRadius: "8px", 
          padding: "1.25rem" 
        }}
      >
        {disclaimerText.elegant}
      </div>
    );
  }

  return (
    <div
      className={`theme-transition ${className}`}
      style={{ 
        backgroundColor: "var(--bg-subtle)", 
        border: "1px solid var(--border)", 
        borderRadius: "8px", 
        padding: "1.25rem" 
      }}
    >
      {!isExpanded ? (
        <div>
          <p style={{ ...baseText, marginBottom: "0.5rem" }}>
            <strong>Document preparation only — not legal advice.</strong> We
            help you prepare appeal paperwork but don&apos;t provide legal
            representation.
          </p>
          <button
            onClick={() => setIsExpanded(true)}
            style={{ 
              ...mutedText, 
              textDecoration: "underline", 
              textUnderlineOffset: "2px",
              cursor: "pointer",
            }}
            className="hover:opacity-80 transition-opacity"
          >
            Learn more
          </button>
        </div>
      ) : (
        <div>
          {disclaimerText.full}
          <button
            onClick={() => setIsExpanded(false)}
            style={{ 
              ...mutedText, 
              marginTop: "0.75rem",
              textDecoration: "underline", 
              textUnderlineOffset: "2px",
              cursor: "pointer",
            }}
            className="hover:opacity-80 transition-opacity"
          >
            Show less
          </button>
        </div>
      )}
    </div>
  );
}
