import { MetadataRoute } from "next";
import {
  getAllBlogSlugs,
  loadSearchPhrases,
  violationCodeToSlug,
  locationToSlug,
} from "./lib/seo-data";
import { CITY_SLUG_MAP } from "./lib/city-routing";

export default function sitemap(): MetadataRoute.Sitemap {
  const baseUrl = "https://fightcitytickets.com";
  const currentDate = new Date().toISOString();

  const routes: MetadataRoute.Sitemap = [
    // Main pages
    {
      url: baseUrl,
      lastModified: currentDate,
      changeFrequency: "daily",
      priority: 1.0,
    },
    {
      url: `${baseUrl}/blog`,
      lastModified: currentDate,
      changeFrequency: "daily",
      priority: 0.9,
    },
    {
      url: `${baseUrl}/terms`,
      lastModified: currentDate,
      changeFrequency: "monthly",
      priority: 0.5,
    },
    {
      url: `${baseUrl}/privacy`,
      lastModified: currentDate,
      changeFrequency: "monthly",
      priority: 0.5,
    },
  ];

  // City pages
  Object.keys(CITY_SLUG_MAP).forEach((citySlug) => {
    routes.push({
      url: `${baseUrl}/${citySlug}`,
      lastModified: currentDate,
      changeFrequency: "weekly",
      priority: 0.8,
    });
  });

  // Blog posts
  const blogSlugs = getAllBlogSlugs();
  blogSlugs.forEach((slug) => {
    routes.push({
      url: `${baseUrl}/blog/${slug}`,
      lastModified: currentDate,
      changeFrequency: "monthly",
      priority: 0.7,
    });
  });

  // Violation/location landing pages
  const phrases = loadSearchPhrases();
  phrases.forEach((phrase) => {
    const codeSlug = violationCodeToSlug(phrase.violation_code);
    const locationSlug = locationToSlug(phrase.hot_location);
    routes.push({
      url: `${baseUrl}/${phrase.city_slug}/violations/${codeSlug}/${locationSlug}`,
      lastModified: currentDate,
      changeFrequency: "monthly",
      priority: 0.6,
    });
  });

  return routes;
}
