import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import FooterDisclaimer from "../components/FooterDisclaimer";
import { Providers } from "./providers";
import { config } from "./lib/config";
import ThemeToggle from "../components/ThemeToggle";
import Link from "next/link";
import GoogleAnalytics from "../components/analytics/GoogleAnalytics";
import Mixpanel from "../components/analytics/Mixpanel";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Procedural Compliance | Clerical Engine™ | FIGHTCITYTICKETS.com",
  description:
    "We aren't lawyers. We're paperwork experts. Procedural compliance services for municipal ticket appeals.",
  keywords:
    "parking ticket appeal, clerical engine, paperwork expert, municipal appeal help, procedural compliance",
  authors: [{ name: "FIGHTCITYTICKETS.com" }],
  openGraph: {
    title: "Procedural Compliance | Clerical Engine™",
    description: "We aren't lawyers. We're paperwork experts.",
    type: "website",
    url: config.baseUrl,
    siteName: "FIGHTCITYTICKETS.com",
  },
  twitter: {
    card: "summary_large_image",
    title: "Procedural Compliance | Clerical Engine™",
    description: "We aren't lawyers. We're paperwork experts.",
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
              name: "FIGHTCITYTICKETS.com",
              url: config.baseUrl,
              logo: `${config.baseUrl}/logo.png`,
              description:
                "Procedural compliance services for parking ticket appeals",
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
              name: "FIGHTCITYTICKETS.com",
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
        <GoogleAnalytics />
        <Mixpanel />
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
