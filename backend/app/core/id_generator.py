"""
Prefix-typed ULID identifier generator for LexMatter AI domain models.
Example: generate_id("mat") -> "mat_01J8K3M90A1B2C3D4E5F6G7H8J"
"""

import time
import ulid


def generate_id(prefix: str) -> str:
    """Generate a prefixed ULID string.
    
    ULIDs are 128-bit identifiers formatted as 26 Crockford Base32 characters.
    They are sortable by timestamp and contain 80 bits of cryptographic randomness.
    """
    return f"{prefix}_{ulid.new().str}"


# Standard typed prefix constants
PREFIX_MATTER = "mat"
PREFIX_DOCUMENT = "doc"
PREFIX_DOCUMENT_VERSION = "docv"
PREFIX_PAGE = "page"
PREFIX_SOURCE_SPAN = "span"

PREFIX_ENTITY = "ent"
PREFIX_SOURCE_ASSERTION = "asrt"
PREFIX_EVENT = "evt"

PREFIX_CANONICAL_FACT = "fact"
PREFIX_RELATIONSHIP = "rel"
PREFIX_CONFLICT = "conf"

PREFIX_AUTHORITY = "auth"
PREFIX_REQUIREMENT = "req"
PREFIX_REQUIREMENT_VERSION = "reqv"
PREFIX_REQUIREMENT_APPLICABILITY = "reqapp"

PREFIX_EVIDENCE_MAPPING = "evm"
PREFIX_FINDING = "find"
PREFIX_EVIDENCE_GAP = "gap"
PREFIX_RESEARCH_ISSUE = "riss"

PREFIX_AGENT_RUN = "run"
PREFIX_HUMAN_REVIEW = "rev"
PREFIX_AUDIT_EVENT = "aud"
