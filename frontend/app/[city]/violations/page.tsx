import { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import {
  getSearchPhrasesByCity,
  violationCodeToSlug,
  locationToSlug,
} from "../../lib/seo-data";
import { getCityBySlug } from "../../lib/city-routing";

interface ViolationsPageProps {
  params: Promise<{
    city: string;
  }>;
}

export async function generateMetadata({
  params,
}: ViolationsPageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const cityData = getCityBySlug(resolvedParams.city);
  const cityName = cityData?.name || resolvedParams.city;

  return {
    title: `${cityName} Parking Violation Codes & Locations | FightCityTickets.com`,
    description: `Find information about parking violation codes and common citation locations in ${cityName}. Learn how to appeal your parking ticket.`,
    openGraph: {
      title: `${cityName} Parking Violations`,
      description: `Parking violation codes and locations in ${cityName}`,
    },
  };
}

export default async function ViolationsPage({ params }: ViolationsPageProps) {
  const resolvedParams = await params;
  const cityData = getCityBySlug(resolvedParams.city);

  if (!cityData) {
    notFound();
  }

  const phrases = getSearchPhrasesByCity(resolvedParams.city);

  // Group by violation code
  const violationsMap: Record<string, typeof phrases> = {};
  phrases.forEach((phrase) => {
    if (!violationsMap[phrase.violation_code]) {
      violationsMap[phrase.violation_code] = [];
    }
    violationsMap[phrase.violation_code].push(phrase);
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <Link
            href={`/${resolvedParams.city}`}
            className="text-blue-600 hover:text-blue-700 font-bold text-xl"
          >
            ← {cityData.name}
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-12">
        <h1 className="text-4xl font-extrabold text-gray-900 mb-4">
          Parking Violations in {cityData.name}
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Find information about specific violation codes and common citation
          locations in {cityData.name}.
        </p>

        {Object.keys(violationsMap).length === 0 ? (
          <div className="bg-white rounded-lg p-8 text-center">
            <p className="text-gray-600">
              No violation data available for this city yet.
            </p>
            <Link
              href={`/${resolvedParams.city}`}
              className="text-blue-600 hover:text-blue-700 mt-4 inline-block"
            >
              Return to {cityData.name} page
            </Link>
          </div>
        ) : (
          <div className="space-y-8">
            {Object.entries(violationsMap).map(([violationCode, locations]) => (
              <div
                key={violationCode}
                className="bg-white rounded-lg shadow-lg p-6"
              >
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  {violationCode}
                </h2>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {locations.map((phrase) => (
                    <Link
                      key={`${phrase.violation_code}-${phrase.hot_location}`}
                      href={`/${resolvedParams.city}/violations/${violationCodeToSlug(phrase.violation_code)}/${locationToSlug(phrase.hot_location)}`}
                      className="block p-4 border border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-md transition"
                    >
                      <h3 className="font-semibold text-gray-900 mb-2">
                        {phrase.hot_location}
                      </h3>
                      <p className="text-sm text-gray-600">
                        Learn how to appeal citations at this location
                      </p>
                    </Link>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-12 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white text-center">
          <h2 className="text-2xl font-bold mb-4">
            Ready to Appeal Your Citation?
          </h2>
          <p className="mb-6 text-blue-100">
            Our automated system makes it easy to appeal your parking ticket in{" "}
            {cityData.name}.
          </p>
          <Link
            href={`/${resolvedParams.city}`}
            className="inline-block bg-white text-blue-600 px-8 py-4 rounded-lg font-semibold hover:bg-blue-50 transition"
          >
            Start Your Appeal Now
          </Link>
        </div>
      </main>
    </div>
  );
}
