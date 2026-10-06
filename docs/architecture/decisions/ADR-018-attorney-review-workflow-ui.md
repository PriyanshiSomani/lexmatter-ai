# ADR-018: Interactive Attorney Review UI & State Lifecycle Management

* **Status:** Accepted
* **Date:** 2026-10-06
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

Following the implementation of the backend LangGraph pause/resume mechanism (`interrupt_before=["human_review"]`, `POST /matters/{id}/orchestration/review`), the frontend application presented several usability and state synchronization deficiencies:

1. **Tab-Siloed State Loss:** The agent execution trigger and review status alert were encapsulated solely within the local React state of `AgentWorkflowPanel` on the secondary "Technical Audit" tab. Navigating to the primary "Legal Analysis Workspace" tab unmounted the component, wiping out the active review alert.
2. **Missing Action Controls on Primary Workspace:** The primary legal workspace lacked an attorney review action bar, meaning legal counsel inspecting the compliance matrix had no intuitive mechanism to submit `ACCEPT`, `REJECT`, or `OVERRIDE` decisions to unblock report generation.
3. **Hidden Evaluation Trigger:** Initiating automated multi-agent analysis required switching tabs to the technical audit panel rather than triggering analysis directly from the active case workspace.
4. **Ambiguity in Evidentiary Deficiencies:** While the backend correctly paused when Level 4 statutory threshold warnings occurred (e.g., missing 1-year foreign employment proof), the attorney UI lacked clear contextual instructions connecting the pause reason to the corresponding requirement matrix rows.

---

## 2. Decision

We established a centralized, persistent attorney review lifecycle architecture across the frontend workspace:

1. **Lifted Workspace Lifecycle State:** Lifted `workflowStatus`, `isReviewRequired`, and `reviewReasons` to the root page component (`MatterWorkspace` in `src/app/matters/[id]/page.tsx`), ensuring state persistence across tab transitions.
2. **Persistent `HumanReviewBanner` Component:** Implemented a top-level alert bar rendered directly above the Legal Analysis workspace whenever an evaluation is paused:
   - **Accept & Finalize:** Submits `action: "ACCEPT"`, clears review flags, and resumes the LangGraph graph to completion.
   - **Override with Notes:** Opens a modal dialog allowing the attorney to enter legal justifications (e.g., referencing external corporate affidavits), logging the note permanently in the audit lineage.
   - **Reject Findings:** Submits `action: "REJECT"`, flagging evidentiary deficiencies and highlighting remedial client request checklists.
3. **Primary Header AI Analysis Trigger:** Placed a direct **[⚡ Run AI Analysis]** trigger in the application top navigation bar, enabling one-click multi-agent ingestion, consistency checking, research, and 4-tier verification.
4. **Typed Frontend SDK Integration:** Added `submitHumanReview()` and `HumanReviewDecisionResponse` to `src/lib/api.ts` wired directly to `POST /matters/{matter_id}/orchestration/review`.

---

## 3. Consequences

### Positive
* **Seamless Attorney Experience:** Legal counsel can trigger evaluations, review compliance matrices, and record binding review decisions without navigating away from the case documents.
* **Audit Lineage Integrity:** Every override or review action is captured with reviewer metadata and comments in the PostgreSQL `human_reviews` table.
* **Resilient Workflow State:** Tab transitions and UI re-renders no longer obscure active review gates or audit findings.

### Trade-offs
* Requires careful coordination between page-level refresh callbacks (`loadMatterData()`) to synchronize newly generated evidence mappings and gap statuses upon workflow resumption.
