# ADR-003: Document Ingestion & Structural Parsing Strategy

* **Status:** Accepted
* **Date:** 2026-09-20
* **Deciders:** LexMatter AI Core Architecture Team

---

## 1. Context

USCIS legal petitions (such as L-1B specialized knowledge filings) consist of heterogeneous document types: Form I-129 petitions, employer support letters, foreign employment verifications, organizational charts, tax returns, and technical credentials. Standard plain-text PDF extraction discards page layouts, header hierarchy, table structures, and bounding boxes, making pinpoint audit citation impossible.

---

## 2. Decision

We implement a layout-aware document ingestion and structural parsing pipeline:

1. **PyMuPDF Ingestion (`pdf_service.py`):** Extract text blocks while retaining structural block classifications (`heading`, `paragraph`, `table`, `list_item`, `salutation`), exact page numbers, and 4-point bounding box coordinates ($x_0, y_0, x_1, y_1$).
2. **Sliding-Window Chunking (`chunking_service.py`):** Generate overlapping chunks (e.g. 500 characters with 50-character overlap) while embedding global character offsets (`start_char`, `end_char`) within the document.
3. **Exhibit Classification (`classifier_service.py`):** Automatically classify uploaded PDF exhibits into canonical legal document types (e.g., `FORM_I129`, `SUPPORT_LETTER`, `TAX_RETURN`, `EMPLOYMENT_VERIFICATION`).

---

## 3. Consequences

### Positive
* **Exact Coordinate Provenance:** Enables pinpoint UI visual highlighting of cited evidence on the original PDF pages.
* **Layout Context Preservation:** Heading hierarchies and structural classifications prevent text chunk fragmentation across logical boundaries.

### Trade-offs
* Increased storage overhead per document to persist exact bounding box coordinates and character offsets for every extracted span.
