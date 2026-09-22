"""
LexMatter AI — PDF Parsing & OCR Extraction Engine
Uses PyMuPDF (fitz) for high-speed layout text extraction and Tesseract for OCR fallback.
"""

import io
from typing import Any, Dict, List, Optional
import fitz  # PyMuPDF
from PIL import Image
import pytesseract

from backend.app.services.storage_service import storage_service


class PDFService:
    """Handles PDF page text extraction, OCR fallback, and layout bounding box parsing."""

    MIN_TEXT_CHARS_FOR_DIGITAL = 20  # Minimum characters to consider a page digitally rendered vs scanned

    def extract_pdf_data(self, file_path: str, page_id_prefix: str = "page") -> Dict[str, Any]:
        """Extract pages, raw text, layout blocks, and OCR status from a PDF file.
        
        Returns:
            Dict containing page count and list of page dictionaries.
        """
        doc = fitz.open(file_path)
        page_count = len(doc)
        pages_data: List[Dict[str, Any]] = []

        for page_idx in range(page_count):
            page = doc[page_idx]
            page_num = page_idx + 1
            rect = page.rect
            width, height = float(rect.width), float(rect.height)

            # 1. Extract raw digital text
            raw_text = page.get_text("text").strip()
            ocr_applied = False

            # 2. OCR Fallback for scanned pages
            if len(raw_text) < self.MIN_TEXT_CHARS_FOR_DIGITAL:
                ocr_text = self._run_ocr_fallback(page)
                if ocr_text:
                    raw_text = ocr_text
                    ocr_applied = True

            # 3. Extract detailed layout blocks with bounding boxes
            layout_blocks = self._extract_layout_blocks(page)

            pages_data.append({
                "page_number": page_num,
                "raw_text": raw_text,
                "ocr_applied": ocr_applied,
                "width": width,
                "height": height,
                "layout_blocks": layout_blocks,
            })

        doc.close()
        return {
            "page_count": page_count,
            "pages": pages_data,
        }

    def _run_ocr_fallback(self, page: fitz.Page) -> str:
        """Render PDF page to PIL image and run Tesseract OCR."""
        try:
            # Render page at 200 DPI for clear OCR image recognition
            pix = page.get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes("png")))
            ocr_text = pytesseract.image_to_string(img)
            return ocr_text.strip()
        except Exception:
            # Fallback if tesseract is not available in test environment
            return ""

    def _extract_layout_blocks(self, page: fitz.Page) -> List[Dict[str, Any]]:
        """Extract layout text blocks with bounding box coordinates (x1, y1, x2, y2)."""
        blocks = []
        try:
            text_instances = page.get_text("blocks")
            for b in text_instances:
                # b format: (x0, y0, x1, y1, text, block_no, block_type)
                if len(b) >= 5 and isinstance(b[4], str) and b[4].strip():
                    blocks.append({
                        "text": b[4].strip(),
                        "bbox": {
                            "x1": round(float(b[0]), 2),
                            "y1": round(float(b[1]), 2),
                            "x2": round(float(b[2]), 2),
                            "y2": round(float(b[3]), 2),
                        }
                    })
        except Exception:
            pass
        return blocks

    def render_page_image(self, file_path: str, page_number: int, output_image_path: str) -> str:
        """Render a specific PDF page to a PNG preview thumbnail image on disk."""
        doc = fitz.open(file_path)
        if 1 <= page_number <= len(doc):
            page = doc[page_number - 1]
            pix = page.get_pixmap(dpi=150)
            pix.save(output_image_path)
        doc.close()
        return output_image_path


pdf_service = PDFService()
