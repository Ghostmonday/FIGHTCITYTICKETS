import type { ReactNode } from "react";
import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";
import { BackgroundAudio } from "./components/BackgroundAudio";

export const metadata: Metadata = {
  title: "FightSFTickets.com — Appeal Your SF Parking Ticket",
  description:
    "Appeal your parking ticket in 5 minutes. We format your statement, print your letter, and mail it to the right place.",
  openGraph: {
    title: "FightSFTickets.com — Appeal Your SF Parking Ticket",
    description: "Appeal your parking ticket in 5 minutes. We handle the paperwork.",
    type: "website",
  },
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link
          rel="preconnect"
          href="https://fonts.gstatic.com"
          crossOrigin="anonymous"
        />
        <Script
          defer
          data-domain="fightsftickets.com"
          src="https://plausible.io/js/script.js"
          strategy="afterInteractive"
        />
      </head>
      <body className="min-h-screen antialiased">
        <BackgroundAudio />
        {children}
      </body>
    </html>
  );
}
