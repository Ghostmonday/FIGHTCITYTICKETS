import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getSearchPhrase,
  violationCodeToSlug,
  locationToSlug,
  getSearchPhrasesByCity,
  loadSearchPhrases,
} from "../../../../lib/seo-data";
import { getCityBySlug } from "../../../../lib/city-routing";
import LegalDisclaimer from "../../../../../components/LegalDisclaimer";

interface ViolationLocationPageProps {
  params: Promise<{
    city: string;
    code: string;
    location: string;
  }>;
}

// Generate static params for all violation/location combinations
export async function generateStaticParams() {
  const { loadSearchPhrases } = await import("../../../../lib/seo-data");
  const phrases = loadSearchPhrases();

  return phrases.map((phrase) => ({
    city: phrase.city_slug,
    code: violationCodeToSlug(phrase.violation_code),
    location: locationToSlug(phrase.hot_location),
  }));
}

// Generate metadata for SEO
export async function generateMetadata({
  params,
}: ViolationLocationPageProps): Promise<Metadata> {
  const { loadSearchPhrases, violationCodeToSlug, locationToSlug } =
    await import("../../../../lib/seo-data");
  const resolvedParams = await params;
  const phrases = loadSearchPhrases();
  const phrase = phrases.find((p) => {
    const codeSlug = violationCodeToSlug(p.violation_code);
    const locationSlug = locationToSlug(p.hot_location);
    return (
      p.city_slug === resolvedParams.city &&
      codeSlug === resolvedParams.code &&
      locationSlug === resolvedParams.location
    );
  });

  if (!phrase) {
    return {
      title: "Page Not Found",
    };
  }

  const cityName = phrase.city_name.replace(/,.*$/, "");
  const title = `Appeal ${phrase.violation_code} Parking Ticket at ${phrase.hot_location} in ${cityName}`;
  const description = `Learn how to appeal parking ticket ${phrase.violation_code} at ${phrase.hot_location} in ${cityName}. Our automated system makes it easy to contest your citation.`;

  return {
    title: `${title} | FIGHTCITYTICKETS.com`,
    description,
    openGraph: {
      title,
      description,
      type: "website",
      url: `https://fightcitytickets.com/${resolvedParams.city}/violations/${resolvedParams.code}/${resolvedParams.location}`,
    },
    twitter: {
      card: "summary_large_image",
      title,
      description,
    },
    alternates: {
      canonical: `https://fightcitytickets.com/${resolvedParams.city}/violations/${resolvedParams.code}/${resolvedParams.location}`,
    },
  };
}

export default async function ViolationLocationPage({
  params,
}: ViolationLocationPageProps) {
  const resolvedParams = await params;
  // Find phrase by matching slugs
  const phrases = loadSearchPhrases();
  const phrase = phrases.find((p) => {
    const codeSlug = violationCodeToSlug(p.violation_code);
    const locationSlug = locationToSlug(p.hot_location);
    return (
      p.city_slug === resolvedParams.city &&
      codeSlug === resolvedParams.code &&
      locationSlug === resolvedParams.location
    );
  });

  const cityData = getCityBySlug(resolvedParams.city);

  if (!phrase) {
    notFound();
  }

  const violationCode = phrase.violation_code;
  const locationName = phrase.hot_location;

  const cityName = phrase.city_name.replace(/,.*$/, "");

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-700 font-bold text-xl"
          >
            ← FIGHTCITYTICKETS.com
          </Link>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-12">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span className="mx-2">/</span>
          <Link
            href={`/${resolvedParams.city}`}
            className="hover:text-blue-600"
          >
            {cityName}
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">Violations</span>
        </nav>

        {/* Page Header */}
        <header className="mb-8">
          <div className="mb-4">
            <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
              {phrase.violation_code}
            </span>
            <span className="ml-3 px-3 py-1 bg-green-100 text-green-800 rounded-full text-sm font-medium">
              {phrase.hot_location}
            </span>
          </div>
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4 leading-tight">
            Appeal {phrase.violation_code} Parking Ticket at{" "}
            {phrase.hot_location}
          </h1>
          <p className="text-xl text-gray-600">Located in {cityName}</p>
        </header>

        {/* Content Section */}
        <div className="bg-white rounded-2xl shadow-lg p-8 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Understanding Your {phrase.violation_code} Citation
          </h2>
          <p className="text-gray-700 mb-6 leading-relaxed">
            If you received a parking ticket with violation code{" "}
            <strong>{phrase.violation_code}</strong> at{" "}
            <strong>{phrase.hot_location}</strong> in {cityName}, you have the
            right to appeal the citation if you believe it was issued in error.
            The appeals process varies by city, but generally involves
            submitting a written explanation along with any supporting evidence.
          </p>

          <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">
            Why You Might Want to Appeal
          </h3>
          <ul className="list-disc list-inside text-gray-700 mb-6 space-y-2">
            <li>The citation was issued incorrectly or in error</li>
            <li>Signage was unclear or missing</li>
            <li>Your vehicle was legally parked</li>
            <li>You have evidence that contradicts the citation</li>
            <li>
              Extenuating circumstances prevented you from moving your vehicle
            </li>
          </ul>

          <h3 className="text-xl font-semibold text-gray-900 mb-3 mt-6">
            How Our Service Helps
          </h3>
          <p className="text-gray-700 mb-4 leading-relaxed">
            FIGHTCITYTICKETS.com makes the appeals process simple and
            stress-free. Our automated system helps you:
          </p>
          <ul className="list-disc list-inside text-gray-700 mb-6 space-y-2">
            <li>Create a professional, well-written appeal letter</li>
            <li>Ensure all required information is included</li>
            <li>Handle mailing your appeal directly to the city</li>
            <li>Track your appeal submission</li>
            <li>Save time and avoid the hassle of manual paperwork</li>
          </ul>
        </div>

        {/* CTA Section - Transformation Focus */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-8 mb-8 text-white shadow-xl">
          <h2 className="text-3xl font-bold mb-4">
            Stop Paying. Get It Dismissed.
          </h2>
          <p className="mb-2 text-lg text-green-100 font-medium">
            Don't let this ticket cost you hundreds of dollars.
          </p>
          <p className="mb-6 text-green-50">
            Appeal your {phrase.violation_code} citation at{" "}
            {phrase.hot_location} now. Keep your money. Protect your record.{" "}
            <strong>
              The cost to appeal is a fraction of what you'll save.
            </strong>
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            <Link
              href={`/${resolvedParams.city}`}
              className="bg-white text-green-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-50 transition text-center shadow-lg hover:shadow-xl"
            >
              Get My Ticket Dismissed →
            </Link>
            <Link
              href="/blog"
              className="bg-green-700 text-white px-8 py-4 rounded-lg font-semibold hover:bg-green-800 transition text-center"
            >
              Learn More
            </Link>
          </div>
        </div>

        {/* Legal Disclaimer */}
        <LegalDisclaimer variant="elegant" className="mb-8" />

        {/* Related Violations */}
        <section className="border-t border-gray-200 pt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Other Violations in {cityName}
          </h2>
          <div className="grid md:grid-cols-2 gap-4">
            {getSearchPhrasesByCity(resolvedParams.city)
              .filter(
                (p) =>
                  p.violation_code !== phrase.violation_code ||
                  p.hot_location !== phrase.hot_location,
              )
              .slice(0, 4)
              .map((relatedPhrase) => (
                <Link
                  key={`${relatedPhrase.violation_code}-${relatedPhrase.hot_location}`}
                  href={`/${resolvedParams.city}/violations/${violationCodeToSlug(relatedPhrase.violation_code)}/${locationToSlug(relatedPhrase.hot_location)}`}
                  className="block p-4 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition"
                >
                  <span className="text-sm font-medium text-blue-600">
                    {relatedPhrase.violation_code}
                  </span>
                  <h3 className="text-lg font-semibold text-gray-900 mt-2">
                    {relatedPhrase.hot_location}
                  </h3>
                </Link>
              ))}
          </div>
        </section>
      </main>

      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "WebPage",
            name: `Appeal ${phrase.violation_code} at ${phrase.hot_location}`,
            description: `Learn how to appeal parking ticket ${phrase.violation_code} at ${phrase.hot_location} in ${cityName}`,
            url: `https://fightcitytickets.com/${resolvedParams.city}/violations/${resolvedParams.code}/${resolvedParams.location}`,
            mainEntity: {
              "@type": "FAQPage",
              mainEntity: [
                {
                  "@type": "Question",
                  name: `How do I appeal a ${phrase.violation_code} citation at ${phrase.hot_location}?`,
                  acceptedAnswer: {
                    "@type": "Answer",
                    text: `You can appeal your ${phrase.violation_code} citation at ${phrase.hot_location} by submitting a written appeal to ${cityName}. Our automated service helps you create a professional appeal letter and handles mailing it for you.`,
                  },
                },
              ],
            },
          }),
        }}
      />
    </div>
  );
}
