import { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getBlogPostBySlug,
  getAllBlogSlugs,
  loadBlogPosts,
} from "../../lib/seo-data";
import LegalDisclaimer from "../../../components/LegalDisclaimer";

interface BlogPostPageProps {
  params: Promise<{
    slug: string;
  }>;
}

// Generate static params for all blog posts
export async function generateStaticParams() {
  const slugs = getAllBlogSlugs();
  return slugs.map((slug) => ({
    slug,
  }));
}

// Generate metadata for SEO
export async function generateMetadata({
  params,
}: BlogPostPageProps): Promise<Metadata> {
  const resolvedParams = await params;
  const post = getBlogPostBySlug(resolvedParams.slug);

  if (!post) {
    return {
      title: "Blog Post Not Found",
    };
  }

  const description =
    post.content.substring(0, 160).replace(/\n/g, " ").trim() + "...";

  return {
    title: `${post.title} | FIGHTCITYTICKETS.com`,
    description,
    openGraph: {
      title: post.title,
      description,
      type: "article",
      url: `https://fightcitytickets.com/blog/${post.slug}`,
      siteName: "FIGHTCITYTICKETS.com",
    },
    twitter: {
      card: "summary_large_image",
      title: post.title,
      description,
    },
    alternates: {
      canonical: `https://fightcitytickets.com/blog/${post.slug}`,
    },
  };
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const resolvedParams = await params;
  const post = getBlogPostBySlug(resolvedParams.slug);

  if (!post) {
    notFound();
  }

  // Extract city from content or title
  const cityMatch = post.title.match(
    /(phoenix|san francisco|los angeles|new york|chicago|seattle|dallas|houston|denver|portland|philadelphia|miami|atlanta|boston|baltimore|detroit|minneapolis|charlotte|louisville|salt lake city|oakland|sacramento|san diego)/i,
  );
  const citySlug = cityMatch
    ? cityMatch[0].toLowerCase().replace(/\s+/g, "_")
    : null;

  // Extract violation code from title
  const violationMatch = post.title.match(
    /(PCC \d+-\d+[a-z]?|Section \d+\.\d+\.\d+[\(a-z\)]?|Section \d+[a-z]?)/i,
  );
  const violationCode = violationMatch ? violationMatch[0] : null;

  // Format content with paragraphs
  const paragraphs = post.content.split(/\n\n+/).filter((p) => p.trim());

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

      <article className="max-w-4xl mx-auto px-4 py-8 md:py-12">
        {/* Breadcrumb */}
        <nav className="mb-6 text-sm text-gray-600">
          <Link href="/" className="hover:text-blue-600">
            Home
          </Link>
          <span className="mx-2">/</span>
          <Link href="/blog" className="hover:text-blue-600">
            Blog
          </Link>
          <span className="mx-2">/</span>
          <span className="text-gray-900">{post.title}</span>
        </nav>

        {/* Article Header */}
        <header className="mb-8">
          <h1 className="text-4xl md:text-5xl font-extrabold text-gray-900 mb-4 leading-tight">
            {post.title}
          </h1>
          <div className="flex items-center gap-4 text-sm text-gray-600">
            <time dateTime={new Date().toISOString()}>
              {new Date().toLocaleDateString("en-US", {
                year: "numeric",
                month: "long",
                day: "numeric",
              })}
            </time>
            {violationCode && (
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-medium">
                {violationCode}
              </span>
            )}
          </div>
        </header>

        {/* Article Content */}
        <div className="prose prose-lg max-w-none mb-12">
          {paragraphs.map((paragraph, index) => (
            <p key={index} className="mb-4 text-gray-700 leading-relaxed">
              {paragraph.trim()}
            </p>
          ))}
        </div>

        {/* CTA Section - Transformation Focus */}
        <div className="bg-gradient-to-r from-green-600 to-emerald-600 rounded-2xl p-8 mb-8 text-white shadow-xl">
          <h2 className="text-3xl font-bold mb-4">
            Stop Paying. Start Winning.
          </h2>
          <p className="mb-2 text-lg text-green-100 font-medium">
            Every ticket you pay is money you&apos;ll never see again.
          </p>
          <p className="mb-6 text-green-50">
            Appeal your ticket now and keep your money. Get it dismissed.
            Protect your record.
            <strong>
              {" "}
              The cost to appeal is tiny compared to what you&apos;ll save.
            </strong>
          </p>
          <div className="flex flex-col sm:flex-row gap-4">
            {citySlug ? (
              <Link
                href={`/${citySlug}`}
                className="bg-white text-green-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-50 transition text-center shadow-lg hover:shadow-xl"
              >
                Get My Ticket Dismissed →
              </Link>
            ) : (
              <Link
                href="/"
                className="bg-white text-green-600 px-8 py-4 rounded-lg font-bold text-lg hover:bg-green-50 transition text-center shadow-lg hover:shadow-xl"
              >
                Get My Ticket Dismissed →
              </Link>
            )}
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

        {/* Related Posts */}
        <section className="border-t border-gray-200 pt-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Related Articles
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            {loadBlogPosts()
              .filter((p) => p.slug !== post.slug)
              .slice(0, 4)
              .map((relatedPost) => (
                <Link
                  key={relatedPost.slug}
                  href={`/blog/${relatedPost.slug}`}
                  className="block p-6 bg-white rounded-lg border border-gray-200 hover:border-blue-500 hover:shadow-lg transition"
                >
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                    {relatedPost.title}
                  </h3>
                  <p className="text-sm text-gray-600 line-clamp-2">
                    {relatedPost.content.substring(0, 120)}...
                  </p>
                </Link>
              ))}
          </div>
        </section>
      </article>

      {/* Structured Data for SEO */}
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{
          __html: JSON.stringify({
            "@context": "https://schema.org",
            "@type": "Article",
            headline: post.title,
            description: post.content.substring(0, 160),
            author: {
              "@type": "Organization",
              name: "FIGHTCITYTICKETS.com",
            },
            publisher: {
              "@type": "Organization",
              name: "FIGHTCITYTICKETS.com",
              logo: {
                "@type": "ImageObject",
                url: "https://fightcitytickets.com/logo.png",
              },
            },
            datePublished: new Date().toISOString(),
            dateModified: new Date().toISOString(),
            mainEntityOfPage: {
              "@type": "WebPage",
              "@id": `https://fightcitytickets.com/blog/${post.slug}`,
            },
          }),
        }}
      />
    </div>
  );
}
