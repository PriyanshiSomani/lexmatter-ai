"""
LexMatter AI — Document Classification Service
Uses deterministic header heuristics and pattern matching to classify uploaded legal documents.
"""

import re
from typing import Dict, Tuple


class DocumentClassifierService:
    """Classifies document types (e.g., PETITION_LETTER, RESUME, EMPLOYMENT_LETTER, USCIS_FORM)."""

    HEURISTIC_PATTERNS = {
        "USCIS_FORM": [
            r"\bform\s+i-129\b",
            r"\bi-129l\b",
            r"\bdepartment\s+of\s+homeland\s+security\b",
            r"\buscis\b",
        ],
        "PETITION_LETTER": [
            r"\bpetition\s+for\b",
            r"\bl-1b\b",
            r"\bspecialized\s+knowledge\b",
            r"\bsupport\s+letter\b",
            r"\bin\s+support\s+of\b",
            r"\bintracompany\s+transferee\b",
        ],
        "RESUME": [
            r"\bcurriculum\s+vitae\b",
            r"\bresume\b",
            r"\beducation\b.*\bexperience\b",
            r"\bwork\s+history\b",
            r"\bprofessional\s+summary\b",
        ],
        "EMPLOYMENT_LETTER": [
            r"\bemployment\s+verification\b",
            r"\bto\s+whom\s+it\s+may\s+concern\b",
            r"\bthis\s+letter\s+is\s+to\s+confirm\b",
            r"\bforeign\s+employment\b",
            r"\bemployment\s+letter\b",
        ],
        "ORG_CHART": [
            r"\borganizational\s+chart\b",
            r"\borg\s+chart\b",
            r"\breporting\s+structure\b",
        ],
        "PAYROLL_RECORD": [
            r"\bw-2\b",
            r"\bpaystub\b",
            r"\bpayroll\b",
            r"\bannual\b.*\bsalary\b",
        ],
        "TRAINING_RECORD": [
            r"\bcertificate\s+of\s+completion\b",
            r"\btraining\s+record\b",
            r"\bcourse\s+completion\b",
        ],
    }

    def classify_document(self, file_name: str, full_text: str) -> Tuple[str, float]:
        """Classify document type using title and document text patterns.
        
        Returns:
            Tuple[document_type, confidence_score]
        """
        combined_text = f"{file_name}\n{full_text[:3000]}".lower()

        for doc_type, patterns in self.HEURISTIC_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, combined_text, re.IGNORECASE):
                    return doc_type, 0.95

        return "UNKNOWN", 0.50


classifier_service = DocumentClassifierService()
