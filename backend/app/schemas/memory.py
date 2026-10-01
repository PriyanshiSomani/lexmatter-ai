"""
LexMatter AI — Pydantic Schemas for Case Memory
"""

from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict, Field


class CaseMemoryCreate(BaseModel):
    matter_id: str
    memory_key: str = Field(..., max_length=100)
    content: str
    meta_data: Optional[Dict[str, Any]] = None


class CaseMemoryUpdate(BaseModel):
    content: str
    meta_data: Optional[Dict[str, Any]] = None


class CaseMemoryResponse(BaseModel):
    id: str
    matter_id: str
    memory_key: str
    content: str
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
