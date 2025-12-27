import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import FooterDisclaimer from "../components/FooterDisclaimer";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FightCityTickets.com - Appeal Parking Tickets in 15+ Cities",
  description:
    "Fight parking tickets in 15+ cities across the US. Automated appeal system that handles everything including mailing your appeal directly to the city.",
  keywords:
    "parking ticket appeal, contest parking ticket, fight parking citation, appeal parking violation, parking ticket help",
  authors: [{ name: "FightCityTickets.com" }],
  openGraph: {
    title: "FightCityTickets.com - Appeal Parking Tickets",
    description: "Automated parking ticket appeals for 15+ US cities",
    type: "website",
    url: "https://fightcitytickets.com",
    siteName: "FightCityTickets.com",
  },
  twitter: {
    card: "summary_large_image",
    title: "FightCityTickets.com - Appeal Parking Tickets",
    description: "Automated parking ticket appeals for 15+ US cities",
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
    canonical: "https://fightcitytickets.com",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* Structured Data for Organization */}
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              "@context": "https://schema.org",
              "@type": "Organization",
              name: "FightCityTickets.com",
              url: "https://fightcitytickets.com",
              logo: "https://fightcitytickets.com/logo.png",
              description:
                "Automated parking ticket appeal service for major US cities",
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
              name: "FightCityTickets.com",
              url: "https://fightcitytickets.com",
              potentialAction: {
                "@type": "SearchAction",
                target:
                  "https://fightcitytickets.com/search?q={search_term_string}",
                "query-input": "required name=search_term_string",
              },
            }),
          }}
        />
      </head>
      <body className={inter.className}>
        {children}
        <FooterDisclaimer />
      </body>
    </html>
  );
}
