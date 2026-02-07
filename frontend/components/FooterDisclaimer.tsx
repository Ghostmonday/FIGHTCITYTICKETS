"use client";

import Link from "next/link";

const supportEmail =
  process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com";

export default function FooterDisclaimer() {
  return (
    <div className="bg-bg-surface border-t border-border py-6 px-4">
      <div className="max-w-7xl mx-auto">
        <p className="text-tiny text-text-muted text-center leading-relaxed max-w-4xl mx-auto mb-4">
          <strong>Document preparation only — not legal advice.</strong>{" "}
          FightCityTickets.com helps you prepare appeal paperwork but does not
          provide legal advice, legal representation, or legal recommendations.
          The decision to appeal and the arguments presented are entirely yours.
          Outcome determined by the municipal authority.
        </p>
        <div className="flex flex-wrap justify-center gap-4 text-tiny">
          <Link
            href="/terms"
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            Terms of Service
          </Link>
          <Link
            href="/privacy"
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            Privacy Policy
          </Link>
          <Link
            href="/refund"
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            Refund Policy
          </Link>
          <Link
            href="/appeal/status"
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            Check Status
          </Link>
          <a
            href={`mailto:${supportEmail}`}
            className="text-text-secondary hover:text-text-primary transition-colors"
          >
            Support
          </a>
        </div>
        <p className="text-tiny text-text-muted text-center mt-4">
          © {new Date().getFullYear()} FightCityTickets.com — All rights
          reserved
        </p>
      </div>
    </div>
  );
}
