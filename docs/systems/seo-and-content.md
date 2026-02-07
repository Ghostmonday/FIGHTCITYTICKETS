# SEO & Content

Purpose: describe SEO surfaces and content assets.

## Pages & content
- Blog index: `frontend/app/blog/page.tsx`.
- Blog detail: `frontend/app/blog/[slug]/page.tsx`.
- Content markdown: `frontend/content/blog/*.md`.
- SEO data helpers: `frontend/app/lib/seo-data.ts`, `frontend/data/seo/parking_blog_posts.csv`.
- Sitemap: `frontend/app/sitemap.ts`.
- Robots: `frontend/app/robots.ts`.

## Behavior
- Blog pages likely statically rendered from markdown/content data.
- Sitemap aggregates main pages and blog posts.
- Robots allows search engines; adjust if staging.

## Rebuild checklist
- Preserve slug structure for existing posts.
- Ensure metadata (title/description) per page via Next.js metadata functions.
- Keep sitemap and robots in sync with routes.
