# Project Breakdown Methodology & Reusable Prompt

This document captures **how** we broke down the FightSFTickets project so you can apply the same approach to **any project**. Use the methodology to plan the work, and the meta-prompt below to have an AI (or a human) produce a full spec in one go.

---

## 1. Methodology: How We Broke Down the Project

### Order of breakdown

1. **Product & ops** — What the product is, core guardrails, environments, external services (env vars), observability, compliance. No code yet; intent and boundaries only.
2. **Backend platform** — Framework, boot sequence, middleware order, route layout, error-handling convention. One section.
3. **Backend config** — Single source of config (e.g. env), list of fields, validation rules, helpers.
4. **Data & persistence** — Entities, relationships, storage tech, patterns (e.g. “database-first”), key files.
5. **Feature domains** — One section per major capability. Each has:
   - Purpose / responsibilities
   - Endpoints or entry points
   - Flow (step-by-step)
   - Data contracts (request/response shapes or key fields)
   - Key files or modules
   - Config / env used
   - Error handling and idempotency
   - Rebuild checklist (what to preserve when recreating)
6. **Frontend architecture** — Stack, routing structure, layout, error boundaries, styling.
7. **Frontend user flows** — Page-by-page or screen-by-screen journey; where state lives; handoff between steps.
8. **Frontend state & data** — How client state is stored (context, storage, API client), sync with backend.
9. **Frontend integrations** — Third-party SDKs, optional vs required, env vars.
10. **Compliance / UX** — Disclaimers, accessibility, regional rules, copy that must appear.
11. **SEO & content** — If applicable: blog, metadata, sitemap, robots.
12. **Testing & QA** — What’s automated, how to run it, manual checklist.
13. **Tooling & deploy** — How to run locally, deploy, scripts, env setup.
14. **Infrastructure** — If applicable: reverse proxy, SSL, hosting, maintenance mode.
15. **Summary of priorities** — 3–5 non-negotiable rules the rebuild must respect.
16. **Closing instruction** — “Recreate the product as described; if simplifying, prioritize X, Y, Z.”

### What each “system” or section contains

- **Purpose** — Why this part exists; what would break if it were missing.
- **Responsibilities** — Bullet list of what this part does (and does not do).
- **Flow** — Numbered steps or sequence so someone can reimplement the logic.
- **Data contracts** — Request/response shapes, key IDs, or “conceptual” fields so APIs or storage can be recreated.
- **Key files / modules** — Paths or names so the builder knows where to put logic.
- **Config / env** — Which env vars or config keys this part uses.
- **Error handling** — What fails, how it’s surfaced, idempotency or retries.
- **Rebuild checklist** — Short list of “must preserve” when recreating.

### Principles

- **One section per system or domain** — Avoid mixing “citation validation” with “payments” so each can be rebuilt or handed off independently.
- **Stack-agnostic where possible** — Describe flows and data first; then pin tech (e.g. “Express + PocketBase” or “FastAPI + PostgreSQL”) so the same spec can be adapted to another stack.
- **Guardrails and priorities up front** — Compliance, security, and “must-have” behaviors are stated early and repeated in the summary.
- **Copy-paste ready for the builder** — The output should be pastable into a no-code builder (e.g. Horizons) or handed to another AI with “build this.”

---

## 2. Meta-Prompt: Use This for Any Project

Copy the block below, replace the bracketed parts with your project details, and send it to an AI (or use it yourself) to generate a full spec in the same structure.

---

```
You are a technical writer and systems architect. Your task is to break down a product into a single, detailed specification that another AI or developer can use to recreate the product end-to-end (including on a different tech stack).

**Project to break down:**
- **Name:** [e.g. "FightCityTickets" or "Acme Inventory"]
- **One-line description:** [e.g. "SaaS that automates parking-ticket appeals for ~15 US cities" or "Internal tool for warehouse stock and reorder alerts"]
- **Tech stack (if known):** [e.g. "Next.js 15, FastAPI, PostgreSQL" or "React 18, Express, PocketBase" or "To be decided — describe logically"]
- **Primary users:** [e.g. "Drivers with parking tickets" or "Warehouse staff and managers"]
- **Core guardrails or compliance:** [e.g. "UPL compliance, no legal advice, database-first, idempotent webhooks" or "SOC2-relevant: audit log all changes"]

**Output format:** Produce one markdown document that another agent can use as a single “build this” prompt. Use the following section structure. For each section, include:
- Purpose and responsibilities
- Flows (numbered steps where relevant)
- Data contracts (request/response shapes or key fields)
- Key files or modules (paths or names)
- Config / env vars used
- Error handling and idempotency (if relevant)
- A short “Rebuild checklist” of what must be preserved when recreating

**Sections to produce:**

1. **Product Overview & Ops**
   - What the product is (workflow in one paragraph or bullet list)
   - Core guardrails (security, compliance, resilience)
   - Environments & URLs
   - External services and their env vars
   - Observability (logging, metrics, health)
   - Any compliance artifacts (disclaimers, audit, regional rules)

2. **Backend Platform**
   - Stack (framework, language, version)
   - Responsibilities (boot, middleware, routes)
   - Boot sequence and middleware order
   - Key structure (main app file, middleware, routes, services)
   - Error-handling convention

3. **Backend Configuration & Settings**
   - How config is loaded (env, file, etc.)
   - List of important fields and env vars
   - Validation rules and helpers

4. **Data Models & Persistence**
   - Storage tech and migration approach
   - Entities and relationships
   - Patterns (e.g. database-first, event-sourced)
   - Rebuild checklist for schema and access

5. **Feature domains (repeat for each major capability)**
   For each domain (e.g. “Citation Validation”, “Payments & Checkout”, “Notifications”):
   - Endpoint or entry point
   - Flow (step-by-step)
   - Data contracts
   - Key files/modules
   - Config / env
   - Error handling and idempotency
   - Rebuild checklist

6. **Frontend Architecture**
   - Stack and routing structure
   - Layout, error boundaries, styling
   - Key files/dirs

7. **Frontend User Flows**
   - Page-by-page or screen-by-screen journey
   - Data handoff between steps (state, storage, API)

8. **Frontend State & Data Layer**
   - How client state is managed (context, storage, API client)
   - Sync with backend and persistence

9. **Frontend Integrations**
   - Third-party SDKs, optional vs required, env vars

10. **Compliance / UX**
    - Required copy, disclaimers, regional rules, accessibility notes

11. **SEO & Content** (if applicable)
    - Blog, metadata, sitemap, robots

12. **Testing & QA**
    - Automated tests and how to run them
    - Manual test checklist

13. **Tooling & Deploy**
    - Local run, deploy, scripts, env setup

14. **Infrastructure** (if applicable)
    - Reverse proxy, SSL, hosting, maintenance

15. **Summary of Priorities**
    - 3–5 non-negotiable rules the rebuild must respect

16. **Closing instruction**
    - One paragraph: “Recreate the product as described. If you need to simplify for an initial build, prioritize: [list order of priorities].”

**Rules:**
- Be specific enough that a builder can implement without guessing (include endpoint paths, field names, error codes where relevant).
- Keep stack-specific details in dedicated sections so the spec can be adapted to another stack (e.g. “Express + PocketBase” instead of “FastAPI + PostgreSQL”).
- State guardrails and compliance clearly; repeat them in the Summary of Priorities.
- Write in clear, imperative language (“Persist intake before payment”, “Return 400 on signature verification failure”).
```

---

## 3. How to Use This on a New Project

1. **Gather:** One-line product description, known stack (or “describe logically”), users, and guardrails.
2. **Paste:** The meta-prompt above into your AI tool, with the bracketed project details filled in.
3. **Generate:** One long spec document (like `HOSTINGER_HORIZONS_PROMPT.md`).
4. **Optional — Per-system READMEs:** If you want separate docs (e.g. in `docs/systems/`), split the generated spec by section into one file per system and add an index README that lists them.
5. **Optional — Platform-specific tweaks:** If the builder uses a different stack (e.g. Horizons: React 18, Express, PocketBase), add a short “Target platform” note at the top of the spec that overrides stack mentions: “Use React 18, Express.js, and PocketBase; no Docker or custom nginx.”

You now have a repeatable way to turn any project into a single, builder-ready specification.
