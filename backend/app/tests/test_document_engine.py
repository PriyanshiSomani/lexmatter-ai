"""
LexMatter AI — Phase 3 Document Engine Unit Tests
Verifies PDF text layout extraction, provenance span offsets, SHA-256 hashing, and document classification.
"""

import fitz  # PyMuPDF
import pytest
from backend.app.services.chunking_service import chunking_service
from backend.app.services.classifier_service import classifier_service
from backend.app.services.storage_service import storage_service


def test_sha256_computation():
    """Verify SHA-256 byte hashing produces consistent 64-char hex string."""
    payload = b"LexMatter AI Document Engine Test Payload"
    hash1 = storage_service.compute_sha256(payload)
    hash2 = storage_service.compute_sha256(payload)

    assert len(hash1) == 64
    assert hash1 == hash2


def test_chunking_provenance_offsets():
    """Verify that SourceSpan character offsets strictly match string indexing."""
    raw_text = (
        "APEX TECHNOLOGIES INC.\n\n"
        "Specialized Knowledge Statement:\n"
        "The Beneficiary possesses proprietary knowledge of the Apex Titan Risk Engine, "
        "having led its core architecture development at Apex India Pvt. Ltd."
    )

    spans = chunking_service.create_spans_from_page(raw_text)
    assert len(spans) > 0

    for span in spans:
        start = span["start_char"]
        end = span["end_char"]
        snippet = span["text_snippet"]

        # Provenance Invariant Check: page_raw_text[start:end] MUST equal snippet
        assert raw_text[start:end] == snippet
        assert len(span["text_hash"]) == 64


def test_heuristic_document_classification():
    """Verify heuristic document classification patterns."""
    text1 = "In Support of Petition for L-1B Intracompany Transferee Specialized Knowledge"
    doc_type1, conf1 = classifier_service.classify_document("Support_Letter.pdf", text1)
    assert doc_type1 == "PETITION_LETTER"
    assert conf1 == 0.95

    text2 = "Curriculum Vitae of Rajesh Sharma. Professional Experience: Senior Architect..."
    doc_type2, conf2 = classifier_service.classify_document("Rajesh_Resume.pdf", text2)
    assert doc_type2 == "RESUME"
    assert conf2 == 0.95

    text3 = "Department of Homeland Security. Form I-129 Petition for Nonimmigrant Worker."
    doc_type3, conf3 = classifier_service.classify_document("I129_Form.pdf", text3)
    assert doc_type3 == "USCIS_FORM"
    assert conf3 == 0.95


def test_pdf_generation_and_extraction(tmp_path):
    """Generate a synthetic PDF on the fly and verify PyMuPDF page text extraction."""
    pdf_path = tmp_path / "synthetic_test.pdf"

    # Create synthetic PDF using PyMuPDF
    doc = fitz.open()
    page = doc.new_page(width=612, height=792)
    page.insert_text((72, 100), "Apex Technologies L-1B Petition Support Document.")
    doc.save(str(pdf_path))
    doc.close()

    # Extract back using PDFService
    from backend.app.services.pdf_service import pdf_service
    result = pdf_service.extract_pdf_data(str(pdf_path))

    assert result["page_count"] == 1
    assert "Apex Technologies L-1B Petition Support Document." in result["pages"][0]["raw_text"]
