# LexMatter AI — Agentic Legal-Matter Intelligence Platform

## 🚀 Pre-Flight Directive
Before proposing code changes or executing commands, always follow this routing protocol:
1. Check `.agents/memory/memory.md` (the master index).
2. Load only the specific topic files relevant to your active task:
   - **Running/Testing/Building:** `.agents/memory/tools/run-commands.md`
   - **Docker & DB Engines:** `.agents/memory/tools/docker-and-db.md`
   - **LangGraph Agents & State:** `.agents/memory/domain/langgraph-orchestrator.md`
   - **Legal Ontology & L-1B Schemas:** `.agents/memory/domain/legal-ontology-and-l1b.md`
3. Abide by global rules in `.agents/rules/` (`architecture-conventions.md`, `backend-async.md`, `frontend-standards.md`).

---

## 🛡️ Mandatory Safety & Guardrail Rules
1. **Non-Adjudicative Guardrails:** LexMatter AI assists legal professionals—it never provides formal legal advice or guarantees petition approval. All evidentiary reporting must use guarded, conditional phrasing (e.g., *"Potential evidence gap detected..."* per ADR-010).
2. **Two-World Architecture:** World 1 entities (`SourceSpan`, `SourceAssertion`, `DocumentChunk`) are strictly immutable. World 2 entities (`CanonicalFact`, `Conflict`, `EvidenceMapping`) represent synthesized intelligence (ADR-002).
3. **Typed ULIDs:** Always generate entity IDs using `app.core.id_generator` with standard prefixes (`mat_`, `doc_`, `span_`, `fact_`, `hrev_`, etc.) (ADR-009).

---

## 🧹 Memory Maintenance
When instructed to **"reorganize memory"**:
1. Read all files under `.agents/memory/`.
2. Deduplicate and merge related notes.
3. Keep individual entries concise: `Date | What | Why`.
4. Update the index table and timestamps in `.agents/memory/memory.md`.
5. Display a summary of changes to the user.
