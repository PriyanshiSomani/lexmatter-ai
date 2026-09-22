"""
LexMatter AI — Provenance-Aware SourceSpan Chunker Service
Splits page text into SourceSpan snippets while recording exact start_char/end_char indices, text hashes, and bounding box coordinates.
"""

import hashlib
import re
from typing import Any, Dict, List


class ChunkingService:
    """Chunks page text into paragraph-level SourceSpan objects with verified character indices."""

    MIN_SPAN_LENGTH = 15  # Minimum character count to form a valid SourceSpan

    @staticmethod
    def compute_snippet_hash(snippet_text: str) -> str:
        """Compute SHA-256 hash of verbatim snippet text."""
        return hashlib.sha256(snippet_text.encode("utf-8")).hexdigest()

    def create_spans_from_page(
        self,
        raw_text: str,
        layout_blocks: List[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """Extract provenance-backed SourceSpan payloads from raw page text and layout blocks.
        
        Returns:
            List of dicts: [
                {
                    "start_char": int,
                    "end_char": int,
                    "text_snippet": str,
                    "text_hash": str,
                    "bounding_box": {"x1": float, "y1": float, "x2": float, "y2": float}
                }
            ]
        """
        if not raw_text or len(raw_text.strip()) < self.MIN_SPAN_LENGTH:
            return []

        spans: List[Dict[str, Any]] = []

        # Strategy 1: Use layout blocks if available (preserves PDF bounding boxes)
        if layout_blocks:
            search_offset = 0
            for block in layout_blocks:
                block_text = block.get("text", "").strip()
                bbox = block.get("bbox")

                if len(block_text) < self.MIN_SPAN_LENGTH:
                    continue

                # Locate starting character offset in raw page text
                idx = raw_text.find(block_text, search_offset)
                if idx == -1:
                    idx = raw_text.find(block_text)  # Fallback search from start

                if idx != -1:
                    start_char = idx
                    end_char = idx + len(block_text)
                    search_offset = end_char

                    spans.append({
                        "start_char": start_char,
                        "end_char": end_char,
                        "text_snippet": block_text,
                        "text_hash": self.compute_snippet_hash(block_text),
                        "bounding_box": bbox,
                    })

        # Strategy 2: Fallback paragraph splitting if layout blocks were missing or unparseable
        if not spans:
            paragraphs = [p.strip() for p in re.split(r"\n\s*\n", raw_text) if len(p.strip()) >= self.MIN_SPAN_LENGTH]
            search_offset = 0
            for p in paragraphs:
                idx = raw_text.find(p, search_offset)
                if idx != -1:
                    start_char = idx
                    end_char = idx + len(p)
                    search_offset = end_char

                    spans.append({
                        "start_char": start_char,
                        "end_char": end_char,
                        "text_snippet": p,
                        "text_hash": self.compute_snippet_hash(p),
                        "bounding_box": None,
                    })

        return spans


chunking_service = ChunkingService()
