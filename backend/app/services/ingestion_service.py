"""
LexMatter AI — Document Ingestion Orchestrator Service
Coordinates file storage, PDF parsing, OCR fallback, SourceSpan chunking, classification, and database persistence.
"""

from typing import Any, Dict
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.source import Document, DocumentVersion, Page, SourceSpan
from backend.app.models.audit import AuditEvent
from backend.app.services.chunking_service import chunking_service
from backend.app.services.classifier_service import classifier_service
from backend.app.services.pdf_service import pdf_service
from backend.app.services.storage_service import storage_service


class IngestionService:
    """Orchestrates end-to-end deterministic document ingestion."""

    async def ingest_document(
        self,
        db: AsyncSession,
        matter_id: str,
        file_name: str,
        file_bytes: bytes,
    ) -> Dict[str, Any]:
        """Ingest a PDF document into a matter, creating all Source Layer ORM records.
        
        Returns:
            Dict containing processing metrics and database record IDs.
        """
        # 1. Save file bytes to disk and compute SHA-256 hash
        file_path, file_hash, file_size = storage_service.save_uploaded_file(matter_id, file_name, file_bytes)

        # 2. Create Document record
        document = Document(
            matter_id=matter_id,
            title=file_name,
            document_type="UNKNOWN",
            status="PROCESSING",
        )
        db.add(document)
        await db.flush()

        # 3. Create DocumentVersion record
        doc_version = DocumentVersion(
            document_id=document.id,
            version_number=1,
            file_path=file_path,
            file_size_bytes=file_size,
            file_hash_sha256=file_hash,
            mime_type="application/pdf",
            page_count=0,
        )
        db.add(doc_version)
        await db.flush()

        # 4. Extract PDF pages and layout data via PyMuPDF + OCR fallback
        extracted_pdf = pdf_service.extract_pdf_data(file_path)
        doc_version.page_count = extracted_pdf["page_count"]

        full_document_text = []
        total_spans_created = 0

        # 5. Process each page
        for page_info in extracted_pdf["pages"]:
            page_text = page_info["raw_text"]
            full_document_text.append(page_text)

            page = Page(
                document_version_id=doc_version.id,
                page_number=page_info["page_number"],
                raw_text=page_text,
                ocr_applied=page_info["ocr_applied"],
                width=page_info["width"],
                height=page_info["height"],
            )
            db.add(page)
            await db.flush()

            # Render PNG preview thumbnail
            preview_path = storage_service.get_preview_image_path(page.id)
            pdf_service.render_page_image(file_path, page.page_number, preview_path)
            page.image_path = preview_path

            # 6. Extract provenance-aware SourceSpans
            span_payloads = chunking_service.create_spans_from_page(
                raw_text=page_text,
                layout_blocks=page_info.get("layout_blocks"),
            )

            for payload in span_payloads:
                span = SourceSpan(
                    page_id=page.id,
                    start_char=payload["start_char"],
                    end_char=payload["end_char"],
                    text_snippet=payload["text_snippet"],
                    bounding_box=payload["bounding_box"],
                    text_hash=payload["text_hash"],
                )
                db.add(span)
                total_spans_created += 1

        # 7. Perform document classification
        doc_type, confidence = classifier_service.classify_document(file_name, "\n".join(full_document_text))
        document.document_type = doc_type
        document.classification_confidence = confidence
        document.status = "PROCESSED"

        # 8. Log Audit Event
        audit_event = AuditEvent(
            matter_id=matter_id,
            actor_type="SYSTEM",
            actor_id="ingestion_engine",
            action="DOCUMENT_INGESTED",
            entity_type="Document",
            entity_id=document.id,
            payload={
                "file_name": file_name,
                "file_hash": file_hash,
                "page_count": doc_version.page_count,
                "spans_created": total_spans_created,
                "document_type": doc_type,
                "confidence": confidence,
            }
        )
        db.add(audit_event)

        return {
            "document_id": document.id,
            "document_version_id": doc_version.id,
            "file_name": file_name,
            "file_hash": file_hash,
            "page_count": doc_version.page_count,
            "total_spans": total_spans_created,
            "document_type": doc_type,
            "classification_confidence": confidence,
            "status": "PROCESSED",
        }


ingestion_service = IngestionService()
