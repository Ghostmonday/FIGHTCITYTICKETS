/**
 * SEO Data Utilities
 *
 * Loads and parses SEO content from CSV files for blog posts and landing pages.
 *
 * NOTE: This module only works on the server side (Node.js environment).
 * Use it in Server Components, API routes, or getStaticProps/getServerSideProps.
 */

import fs from "fs";
import path from "path";
import { parse } from "csv-parse/sync";

export interface BlogPost {
  title: string;
  slug: string;
  content: string;
}

export interface SearchPhrase {
  city_name: string;
  city_slug: string;
  violation_code: string;
  hot_location: string;
  search_phrase_one: string;
  search_phrase_two: string;
  monthly_volume?: string;
}

let blogPostsCache: BlogPost[] | null = null;
let searchPhrasesCache: SearchPhrase[] | null = null;

/**
 * Load blog posts from CSV file
 * Only works on server side (Node.js)
 */
export function loadBlogPosts(): BlogPost[] {
  if (blogPostsCache) {
    return blogPostsCache;
  }

  // Only run on server side
  if (typeof window !== "undefined") {
    // TODO: CODE_REVIEW - Consider using proper server-side logging
    console.warn("loadBlogPosts() can only be called on the server side");
    return [];
  }

  try {
    // During Docker build, files are at /app, so data is at /app/../data
    // In production, try multiple paths
    const possiblePaths = [
      path.join(process.cwd(), "..", "data", "seo", "parking_blog_posts.csv"),
      path.join(process.cwd(), "data", "seo", "parking_blog_posts.csv"),
      path.join("/app", "..", "data", "seo", "parking_blog_posts.csv"),
    ];
    let csvPath = possiblePaths.find((p) => fs.existsSync(p));
    if (!csvPath) csvPath = possiblePaths[0]; // Use first as fallback

    // Check if file exists
    if (!fs.existsSync(csvPath)) {
      // TODO: CODE_REVIEW - Consider using proper server-side logging
      console.warn(`Blog posts CSV not found at: ${csvPath}`);
      return [];
    }

    const fileContent = fs.readFileSync(csvPath, "utf-8");

    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    }) as BlogPost[];

    blogPostsCache = records.filter(
      (post) => post.title && post.slug && post.content
    );
    return blogPostsCache;
  } catch (error) {
    // TODO: CODE_REVIEW - Consider using proper server-side logging
    console.error("Error loading blog posts:", error);
    return [];
  }
}

/**
 * Load search phrases from CSV file
 * Only works on server side (Node.js)
 */
export function loadSearchPhrases(): SearchPhrase[] {
  if (searchPhrasesCache) {
    return searchPhrasesCache;
  }

  // Only run on server side
  if (typeof window !== "undefined") {
    // TODO: CODE_REVIEW - Consider using proper server-side logging
    console.warn("loadSearchPhrases() can only be called on the server side");
    return [];
  }

  try {
    // During Docker build, files are at /app, so data is at /app/../data
    // In production, try multiple paths
    const possiblePaths = [
      path.join(process.cwd(), "..", "data", "seo", "parking_phrases.csv"),
      path.join(process.cwd(), "data", "seo", "parking_phrases.csv"),
      path.join("/app", "..", "data", "seo", "parking_phrases.csv"),
    ];
    let csvPath = possiblePaths.find((p) => fs.existsSync(p));
    if (!csvPath) csvPath = possiblePaths[0]; // Use first as fallback

    // Check if file exists
    if (!fs.existsSync(csvPath)) {
      console.warn(`Search phrases CSV not found at: ${csvPath}`);
      return [];
    }

    const fileContent = fs.readFileSync(csvPath, "utf-8");

    const records = parse(fileContent, {
      columns: true,
      skip_empty_lines: true,
      trim: true,
    }) as SearchPhrase[];

    searchPhrasesCache = records.filter(
      (phrase) => phrase.city_slug && phrase.violation_code
    );
    return searchPhrasesCache;
  } catch (error) {
    // TODO: CODE_REVIEW - Consider using proper server-side logging
    console.error("Error loading search phrases:", error);
    return [];
  }
}

/**
 * Get blog post by slug
 */
export function getBlogPostBySlug(slug: string): BlogPost | null {
  const posts = loadBlogPosts();
  return posts.find((post) => post.slug === slug) || null;
}

/**
 * Get all blog post slugs (for static generation)
 */
export function getAllBlogSlugs(): string[] {
  const posts = loadBlogPosts();
  return posts.map((post) => post.slug);
}

/**
 * Get search phrases for a specific city
 */
export function getSearchPhrasesByCity(citySlug: string): SearchPhrase[] {
  const phrases = loadSearchPhrases();
  return phrases.filter((phrase) => phrase.city_slug === citySlug);
}

/**
 * Get search phrases for a specific violation code
 */
export function getSearchPhrasesByViolation(
  violationCode: string
): SearchPhrase[] {
  const phrases = loadSearchPhrases();
  return phrases.filter((phrase) => phrase.violation_code === violationCode);
}

/**
 * Get search phrase by city, violation, and location
 */
export function getSearchPhrase(
  citySlug: string,
  violationCode: string,
  location: string
): SearchPhrase | null {
  const phrases = loadSearchPhrases();
  return (
    phrases.find(
      (phrase) =>
        phrase.city_slug === citySlug &&
        phrase.violation_code === violationCode &&
        phrase.hot_location.toLowerCase() === location.toLowerCase()
    ) || null
  );
}

/**
 * Generate violation code slug from violation code
 */
export function violationCodeToSlug(violationCode: string): string {
  return violationCode
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/**
 * Generate location slug from location name
 */
export function locationToSlug(location: string): string {
  return location
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}
