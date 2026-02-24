"use client";

import Link from "next/link";

const supportEmail =
  process.env.NEXT_PUBLIC_SUPPORT_EMAIL || "support@example.com";

export default function FooterDisclaimer() {
  return (
    <footer
      className="border-t py-6 px-4 mt-auto theme-transition"
      style={{
        borderColor: "var(--border)",
        backgroundColor: "var(--bg-surface)",
      }}
    >
      <div className="max-w-7xl mx-auto">
        <p
          className="text-center leading-relaxed max-w-4xl mx-auto mb-4"
          style={{
            color: "var(--text-muted)",
            fontSize: "0.75rem",
          }}
        >
          <strong style={{ color: "var(--text-secondary)" }}>We aren&apos;t lawyers. We&apos;re paperwork experts.</strong>{" "}
          FIGHTCITYTICKETS.com is a procedural compliance service that helps you articulate
          your own reasons for appealing a parking ticket. We refine and format the information
          you provide to create a professional appeal letter. We do not provide legal advice.
          The decision to appeal and the arguments presented are entirely yours.
        </p>
        <div className="flex flex-wrap justify-center gap-4">
          <Link
            href="/terms"
            className="transition-colors hover:opacity-80"
            style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}
          >
            Terms
          </Link>
          <Link
            href="/privacy"
            className="transition-colors hover:opacity-80"
            style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}
          >
            Privacy
          </Link>
          <Link
            href="/refund"
            className="transition-colors hover:opacity-80"
            style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}
          >
            Refund
          </Link>
          <Link
            href="/appeal/status"
            className="transition-colors hover:opacity-80"
            style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}
          >
            Check Status
          </Link>
          <a
            href={`mailto:${supportEmail}`}
            className="transition-colors hover:opacity-80"
            style={{ color: "var(--text-secondary)", fontSize: "0.75rem" }}
          >
            Support
          </a>
        </div>
        <p
          className="text-center mt-4"
          style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}
        >
          © {new Date().getFullYear()} FightCityTickets — All rights reserved
        </p>
      </div>
    </footer>
  );
}
