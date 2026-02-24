import { Metadata } from "next";
import Link from "next/link";
import { config } from "../lib/config";
import { loadBlogPosts } from "../lib/seo-data";

export const metadata: Metadata = {
  title: "Parking Ticket Appeal Blog | FIGHTCITYTICKETS.com",
  description:
    "Learn how to appeal parking tickets, understand violation codes, and navigate the appeals process in cities across the US.",
  openGraph: {
    title: "Parking Ticket Appeal Blog | FIGHTCITYTICKETS.com",
    description:
      "Expert guides on appealing parking tickets in major US cities",
    type: "website",
  },
};

export default function BlogIndexPage() {
  const posts = loadBlogPosts();

  // Group posts by city
  const postsByCity: Record<string, typeof posts> = {};
  posts.forEach((post) => {
    const cityMatch = post.title.match(
      /(phoenix|san francisco|los angeles|new york|chicago|seattle|dallas|houston|denver|portland|philadelphia|miami|atlanta|boston|baltimore|detroit|minneapolis|charlotte|louisville|salt lake city|oakland|sacramento|san diego)/i
    );
    const city = cityMatch ? cityMatch[0] : "Other";
    if (!postsByCity[city]) {
      postsByCity[city] = [];
    }
    postsByCity[city].push(post);
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-white">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <Link
            href="/"
            className="text-blue-600 hover:text-blue-700 font-bold text-xl"
          >
            ← FIGHTCITYTICKETS.com
          </Link>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-12">
        {/* Page Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4">
            Parking Ticket Appeal Blog
          </h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Expert guides on appealing parking tickets, understanding violation
            codes, and navigating the appeals process in cities across the US.
          </p>
        </div>

        {/* All Posts Grid */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            All Articles
          </h2>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {posts.map((post) => {
              const cityMatch = post.title.match(
                /(phoenix|san francisco|los angeles|new york|chicago|seattle|dallas|houston|denver|portland|philadelphia|miami|atlanta|boston|baltimore|detroit|minneapolis|charlotte|louisville|salt lake city|oakland|sacramento|san diego)/i
              );
              const violationMatch = post.title.match(
                /(PCC \d+-\d+[a-z]?|Section \d+\.\d+\.\d+[(a-z)]?|Section \d+[a-z]?)/i
              );

              return (
                <Link
                  key={post.slug}
                  href={`/blog/${post.slug}`}
                  className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition group"
                >
                  {violationMatch && (
                    <span className="inline-block px-2 py-1 bg-blue-100 text-blue-800 text-xs font-medium rounded mb-3">
                      {violationMatch[0]}
                    </span>
                  )}
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition line-clamp-2">
                    {post.title}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-3 mb-4">
                    {post.content.substring(0, 150)}...
                  </p>
                  <div className="flex items-center justify-between text-sm text-gray-500">
                    {cityMatch && (
                      <span className="font-medium">{cityMatch[0]}</span>
                    )}
                    <span className="text-blue-600 group-hover:underline">
                      Read more →
                    </span>
                  </div>
                </Link>
              );
            })}
          </div>
        </div>

        {/* CTA Section - Compliance Focus */}
        <div className="bg-gradient-to-r from-stone-600 to-stone-800 rounded-2xl p-8 text-white text-center shadow-xl">
          <h2 className="text-3xl font-bold mb-4">
            Paperwork is Power.
          </h2>
          <p className="text-xl text-stone-100 mb-2 max-w-2xl mx-auto font-medium">
            Municipalities win through clerical precision.
          </p>
          <p className="text-lg text-stone-50 mb-6 max-w-2xl mx-auto">
            We help you meet their exacting standards with a professionally
            articulated appeal. Don&apos;t be intimidated into paying a
            ticket you believe is unfair.
            <strong>
              {" "}
              The Clerical Engine™ ensures your appeal is formatted exactly how
              they require it.
            </strong>
          </p>
          <Link
            href="/"
            className="inline-block bg-white text-stone-800 px-8 py-4 rounded-lg font-bold hover:bg-stone-50 transition text-lg shadow-lg hover:shadow-xl"
          >
            Prepare My Appeal →
          </Link>
        </div>
      </main>

      {/* Structured Data */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Blog",
            name: "FIGHTCITYTICKETS.com Blog",
            description: "Expert guides on appealing parking tickets",
            url: `${config.baseUrl}/blog`,
            publisher: {
              "@type": "Organization",
              name: "FIGHTCITYTICKETS.com",
            },
            blogPost: posts.slice(0, 10).map((post) => ({
              "@type": "BlogPosting",
              headline: post.title,
              url: `${config.baseUrl}/blog/${post.slug}`,
            })),
          }),
        }}
      />
    </div>
  );
}
