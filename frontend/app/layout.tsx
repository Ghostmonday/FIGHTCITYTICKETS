import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import FooterDisclaimer from "../components/FooterDisclaimer";
import { Providers } from "./providers";
import { config } from "./lib/config";
import ThemeToggle from "../components/ThemeToggle";
import Link from "next/link";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FightCityTickets - Beat Your Parking Ticket",
  description:
    "One-step parking ticket appeals. Upload your ticket, generate your defense, fight back.",
  keywords:
    "parking ticket appeal, contest parking ticket, fight parking citation, appeal parking violation, parking ticket help",
  authors: [{ name: "FightCityTickets" }],
  openGraph: {
    title: "FightCityTickets - Beat Your Parking Ticket",
    description: "One-step parking ticket appeals",
    type: "website",
    url: config.baseUrl,
    siteName: "FightCityTickets",
  },
  twitter: {
    card: "summary_large_image",
    title: "FightCityTickets - Beat Your Parking Ticket",
    description: "One-step parking ticket appeals",
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      "max-video-preview": -1,
      "max-image-preview": "large",
      "max-snippet": -1,
    },
  },
  alternates: {
    canonical: config.baseUrl,
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <head>
        {/* Structured Data for Organization */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              name: "FightCityTickets",
              url: config.baseUrl,
              logo: `${config.baseUrl}/logo.png`,
              description:
                "One-step parking ticket appeals",
              sameAs: [],
            }),
          }}
        />
        {/* Structured Data for WebSite */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "WebSite",
              name: "FightCityTickets",
              url: config.baseUrl,
              potentialAction: {
                "@type": "SearchAction",
                target: `${config.baseUrl}/search?q={search_term_string}`,
                "query-input": "required name=search_term_string",
              },
            }),
          }}
        />
      </head>
      <body className={inter.className}>
        <Providers>
          {/* Header */}
          <header className="fixed top-0 left-0 right-0 z-50 theme-transition" style={{ backgroundColor: "var(--bg-page)" }}>
            <div className="max-w-6xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between">
              <Link href="/" className="flex items-center">
                <img 
                  src="/logo.png" 
                  alt="FightCityTickets" 
                  className="h-16 w-auto"
                />
              </Link>
              <ThemeToggle />
            </div>
          </header>
          
          {/* Main Content */}
          <main className="pt-20">
            {children}
          </main>
          
          <FooterDisclaimer />
        </Providers>
      </body>
    </html>
  );
}
