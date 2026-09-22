"""
LexMatter AI — File Storage & Integrity Service
Handles file saving, SHA-256 hash generation, and directory management.
"""

import hashlib
import os
from pathlib import Path
from typing import Tuple

from backend.app.core.config import settings


class StorageService:
    """Manages physical disk storage and file hash integrity verification."""

    def __init__(self, base_upload_path: str = None, base_preview_path: str = None):
        self.upload_dir = Path(base_upload_path or settings.UPLOAD_STORAGE_PATH)
        self.preview_dir = Path(base_preview_path or settings.PREVIEW_STORAGE_PATH)
        self._ensure_directories()

    def _ensure_directories(self) -> None:
        """Create storage directories if they do not already exist."""
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.preview_dir.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def compute_sha256(file_bytes: bytes) -> str:
        """Compute SHA-256 hash of raw file bytes for integrity and deduplication."""
        return hashlib.sha256(file_bytes).hexdigest()

    def save_uploaded_file(self, matter_id: str, file_name: str, file_bytes: bytes) -> Tuple[str, str, int]:
        """Save raw uploaded file bytes to disk using matter ID and file SHA-256.
        
        Returns:
            Tuple[file_path, sha256_hash, file_size_bytes]
        """
        file_hash = self.compute_sha256(file_bytes)
        file_size = len(file_bytes)

        # Create matter-specific upload subfolder
        matter_upload_dir = self.upload_dir / matter_id
        matter_upload_dir.mkdir(parents=True, exist_ok=True)

        # File extension
        ext = Path(file_name).suffix or ".pdf"
        target_path = matter_upload_dir / f"{file_hash}{ext}"

        # Save to disk
        with open(target_path, "wb") as f:
            f.write(file_bytes)

        return str(target_path.resolve()), file_hash, file_size

    def get_preview_image_path(self, page_id: str) -> str:
        """Generate a deterministic file path for a rendered page preview image."""
        return str((self.preview_dir / f"{page_id}.png").resolve())


storage_service = StorageService()
