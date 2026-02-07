import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import FooterDisclaimer from "../components/FooterDisclaimer";
import { Providers } from "./providers";
import { config } from "./lib/config";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "FIGHTCITYTICKETS.com - Procedural Parking Ticket Assistance",
  description:
    "Document preparation service for parking ticket appeals in 23 cities across the US. We help you generate the exact paperwork required by municipal code.",
  keywords:
    "parking ticket appeal, contest parking ticket, fight parking citation, appeal parking violation, parking ticket help",
  authors: [{ name: "FIGHTCITYTICKETS.com" }],
  openGraph: {
    title: "FIGHTCITYTICKETS.com - Procedural Parking Ticket Assistance",
    description: "Document preparation service for parking ticket appeals",
    type: "website",
    url: config.baseUrl,
    siteName: "FIGHTCITYTICKETS.com",
  },
  twitter: {
    card: "summary_large_image",
    title: "FIGHTCITYTICKETS.com - Procedural Parking Ticket Assistance",
    description: "Document preparation service for parking ticket appeals",
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
    <html lang="en">
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
                "Document preparation service for parking ticket appeals",
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
        <Providers>{children}</Providers>
        <FooterDisclaimer />
      </body>
    </html>
  );
}
