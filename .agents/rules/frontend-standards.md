# Rule: Frontend Standards & UI Architecture

## 1. Next.js 14 App Router
* Keep server and client components explicitly marked (`"use client"` for interactive state).
* Route structure: `frontend/src/app/matters/[id]/page.tsx`.

## 2. API Client & Typing
* Centralize all API network calls in `frontend/src/lib/api.ts`.
* Maintain exact TypeScript type interfaces mirroring backend Pydantic responses.
* Handle empty states, loading indicators, and error banners gracefully across all views.

## 3. Tailwind CSS & UI Components
* Use standard utility classes with `clsx` and `tailwind-merge` (`cn` helper).
* Interactive attorney decision banners (`HumanReviewBanner.tsx`) must preserve state across evaluations.
