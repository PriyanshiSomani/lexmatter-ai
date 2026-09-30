# ADR-008: Frontend Architecture & Client State Management

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

Attorneys and legal assistants require a responsive, intuitive interface to monitor multi-agent matter processing, inspect evidence gap findings, review cross-document conflicts, view PDF document previews with highlighted source text, and interact with human-in-the-loop review gates.

---

## 2. Decision

We implement a modern web application frontend using **Next.js 14 App Router**, **React**, **Tailwind CSS**, and **TanStack React Query**:

1. **Framework:** Next.js 14 App Router (`frontend/src/app`) providing server-rendered layout speed and client-side interactivity (`src/app/matters/[id]/page.tsx`).
2. **API Communication Layer (`src/lib/api.ts`):** Centralized REST API client wrapper invoking FastAPI backend endpoints (`/api/v1/...`).
3. **Async State Management:** TanStack React Query handling asynchronous polling for long-running agent workflows, automatic cache invalidation, and background state refetching.
4. **Visual UI Components (`src/components/`):** Custom UI components for matter summary cards, requirement progress bars, evidence mapping tables, conflict flags, and interactive review modal dialogs.

---

## 3. Consequences

### Positive
* **Decoupled Architecture:** Clean separation of concerns between backend Python AI engines and React client presentation layers.
* **Responsive Workflow Feedback:** Real-time polling and cached state updates provide instantaneous feedback as agent steps complete.

### Trade-offs
* Requires maintaining TypeScript API client definitions synchronized with backend Pydantic models.
