# Frontend Architecture (Next.js 15)

Purpose: describe app structure, routing, providers, and styling conventions.

## Responsibilities
- Provide user-facing flow for appeals, static legal pages, and SEO blog.
- Handle routing with Next.js App Router and dynamic segments.
- Supply global providers (theme, context), error boundaries, and global styles.

## Key files/dirs
- `frontend/app/layout.tsx` — root layout.
- `frontend/app/page.tsx` — homepage.
- `frontend/app/error.tsx`, `global-error.tsx`, `not-found.tsx` — error boundaries.
- `frontend/app/providers.tsx` — wraps app in contexts.
- `frontend/app/globals.css` — Tailwind + custom styles.
- Dynamic routes: `app/[city]/`, `app/appeal/`, `app/blog/`, etc.
- Config: `tailwind.config.js`, `postcss.config.js`, `next.config.js`.

## Routing highlights
- `[city]/` dynamic segment for city-specific entry.
- `appeal/` folder contains multi-step workflow pages.
- `blog/[slug]/` for SEO content.
- Static legal pages: `terms`, `privacy`, `refund`, `what-we-are`, `contact`.

## Error handling
- `error.tsx` (route-level) and `global-error.tsx` handle unexpected failures with reset UI.
- `components/ErrorBoundary.tsx` for client-only boundary where needed.

## Styling
- TailwindCSS across pages; global styles in `globals.css`.
- Components prefer functional, client components where interactivity is needed.

## Rebuild checklist
- Use Next.js App Router with React 19 compatibility.
- Preserve dynamic segments and file names to keep route contract.
- Ensure providers include appeal context and any theme/state wrappers.
