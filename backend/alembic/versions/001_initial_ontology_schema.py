"""initial ontology schema (21 tables and pgvector extension)

Revision ID: 001_initial_ontology_schema
Revises: 
Create Date: 2026-09-22 10:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

revision: str = '001_initial_ontology_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    # 2. Layer 1: Source Layer
    op.create_table(
        'matters',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('matter_type', sa.String(length=50), nullable=False, server_default='IMMIGRATION'),
        sa.Column('case_type', sa.String(length=50), nullable=False, server_default='L1B'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='DRAFT'),
        sa.Column('filing_type', sa.String(length=50), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_matters_type_status', 'matters', ['matter_type', 'case_type', 'status'])
    op.create_index('idx_matters_metadata_gin', 'matters', ['metadata'], postgresql_using='gin')

    op.create_table(
        'documents',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('document_type', sa.String(length=50), nullable=False, server_default='UNKNOWN'),
        sa.Column('classification_confidence', sa.Float(), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_documents_matter_type', 'documents', ['matter_id', 'document_type'])

    op.create_table(
        'document_versions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_id', sa.String(length=36), sa.ForeignKey('documents.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('file_path', sa.String(length=1024), nullable=False),
        sa.Column('file_size_bytes', sa.BigInteger(), nullable=False),
        sa.Column('file_hash_sha256', sa.String(length=64), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False, server_default='application/pdf'),
        sa.Column('page_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('uploaded_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('document_id', 'version_number', name='uq_document_versions_num'),
    )
    op.create_index('idx_document_versions_hash', 'document_versions', ['file_hash_sha256'])

    op.create_table(
        'pages',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('document_version_id', sa.String(length=36), sa.ForeignKey('document_versions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('page_number', sa.Integer(), nullable=False),
        sa.Column('raw_text', sa.Text(), nullable=False, server_default=''),
        sa.Column('ocr_applied', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('width', sa.Float(), nullable=False, server_default='612.0'),
        sa.Column('height', sa.Float(), nullable=False, server_default='792.0'),
        sa.Column('image_path', sa.String(length=1024), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('document_version_id', 'page_number', name='uq_pages_version_num'),
    )

    op.create_table(
        'source_spans',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('page_id', sa.String(length=36), sa.ForeignKey('pages.id', ondelete='CASCADE'), nullable=False),
        sa.Column('start_char', sa.Integer(), nullable=False),
        sa.Column('end_char', sa.Integer(), nullable=False),
        sa.Column('text_snippet', sa.Text(), nullable=False),
        sa.Column('bounding_box', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('text_hash', sa.String(length=64), nullable=False),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_source_spans_hash', 'source_spans', ['text_hash'])
    op.execute(
        "CREATE INDEX idx_source_spans_vector_hnsw ON source_spans "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
    )

    # 3. Layer 2: Extraction Layer
    op.create_table(
        'entities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('canonical_name', sa.String(length=255), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_entities_canonical', 'entities', ['matter_id', 'entity_type', 'canonical_name'])
    op.create_index('idx_entities_attrs_gin', 'entities', ['attributes'], postgresql_using='gin')

    op.create_table(
        'source_assertions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_span_id', sa.String(length=36), sa.ForeignKey('source_spans.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('subject_entity_id', sa.String(length=36), sa.ForeignKey('entities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('predicate', sa.String(length=100), nullable=False),
        sa.Column('object_value', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('confidence', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('extraction_method', sa.String(length=50), nullable=False, server_default='LLM_STRUCTURED'),
        sa.Column('is_immutable', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('extracted_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_assertions_lookup', 'source_assertions', ['matter_id', 'predicate', 'subject_entity_id'])
    op.create_index('idx_assertions_value_gin', 'source_assertions', ['object_value'], postgresql_using='gin')

    op.create_table(
        'events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('event_date', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('participants', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('supporting_assertion_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_events_timeline', 'events', ['matter_id', 'event_date', 'event_type'])
    op.create_index('idx_events_participants_gin', 'events', ['participants'], postgresql_using='gin')
    op.create_index('idx_events_assertions_gin', 'events', ['supporting_assertion_ids'], postgresql_using='gin')

    # 4. Layer 3: Knowledge Layer
    op.create_table(
        'canonical_facts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subject_entity_id', sa.String(length=36), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('predicate', sa.String(length=100), nullable=False),
        sa.Column('canonical_value', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('candidate_values', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='UNCONTESTED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('matter_id', 'subject_entity_id', 'predicate', name='uq_canonical_facts_subject_pred'),
    )
    op.create_index('idx_canonical_facts_status', 'canonical_facts', ['matter_id', 'status'])

    op.create_table(
        'relationships',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_entity_id', sa.String(length=36), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_entity_id', sa.String(length=36), sa.ForeignKey('entities.id', ondelete='CASCADE'), nullable=False),
        sa.Column('relationship_type', sa.String(length=50), nullable=False),
        sa.Column('attributes', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('supporting_assertion_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PROPOSED'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_relationships_pair', 'relationships', ['matter_id', 'source_entity_id', 'relationship_type', 'target_entity_id'])
    op.create_index('idx_relationships_assertions_gin', 'relationships', ['supporting_assertion_ids'], postgresql_using='gin')

    op.create_table(
        'conflicts',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('subject_entity_id', sa.String(length=36), sa.ForeignKey('entities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('predicate', sa.String(length=100), nullable=False),
        sa.Column('conflict_type', sa.String(length=50), nullable=False),
        sa.Column('conflicting_assertion_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='UNRESOLVED'),
        sa.Column('resolution_notes', sa.Text(), nullable=True),
        sa.Column('detected_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_conflicts_status_severity', 'conflicts', ['matter_id', 'status', 'severity'])
    op.create_index('idx_conflicts_assertions_gin', 'conflicts', ['conflicting_assertion_ids'], postgresql_using='gin')

    # 5. Layer 4: Legal Knowledge Layer
    op.create_table(
        'authorities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('authority_type', sa.String(length=50), nullable=False),
        sa.Column('citation_title', sa.String(length=255), nullable=False),
        sa.Column('jurisdiction', sa.String(length=50), nullable=False, server_default='US_FEDERAL'),
        sa.Column('source_url', sa.String(length=1024), nullable=True),
        sa.Column('full_text', sa.Text(), nullable=False),
        sa.Column('effective_date', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_authorities_type_citation', 'authorities', ['authority_type', 'citation_title'])

    op.create_table(
        'requirements',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('code', sa.String(length=50), nullable=False, unique=True),
        sa.Column('case_type', sa.String(length=50), nullable=False, server_default='L1B'),
        sa.Column('category', sa.String(length=50), nullable=False, server_default='ELIGIBILITY'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_requirements_case_cat', 'requirements', ['case_type', 'category'])

    op.create_table(
        'requirement_versions',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('requirement_id', sa.String(length=36), sa.ForeignKey('requirements.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version_number', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('authority_id', sa.String(length=36), sa.ForeignKey('authorities.id', ondelete='SET NULL'), nullable=True),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('evaluation_dimensions', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=False, server_default='2020-01-01'),
        sa.Column('effective_to', sa.Date(), nullable=True),
        sa.UniqueConstraint('requirement_id', 'version_number', name='uq_req_versions_num'),
    )
    op.execute(
        "CREATE INDEX idx_req_versions_vector_hnsw ON requirement_versions "
        "USING hnsw (embedding vector_cosine_ops) WITH (m = 16, ef_construction = 64);"
    )

    op.create_table(
        'requirement_applicabilities',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requirement_version_id', sa.String(length=36), sa.ForeignKey('requirement_versions.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='NOT_EVALUATED'),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.UniqueConstraint('matter_id', 'requirement_version_id', name='uq_reqapp_matter_version'),
    )
    op.create_index('idx_reqapp_status', 'requirement_applicabilities', ['matter_id', 'status'])

    # 6. Layer 5: Analysis Layer
    op.create_table(
        'evidence_mappings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('source_assertion_id', sa.String(length=36), sa.ForeignKey('source_assertions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requirement_version_id', sa.String(length=36), sa.ForeignKey('requirement_versions.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('relationship', sa.String(length=50), nullable=False),
        sa.Column('target_dimension', sa.String(length=100), nullable=True),
        sa.Column('relevance_score', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('analysis_notes', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_evm_lookup', 'evidence_mappings', ['matter_id', 'requirement_version_id', 'relationship'])

    op.create_table(
        'findings',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=20), nullable=False, server_default='MEDIUM'),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('supporting_span_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('impacted_requirement_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='PENDING_REVIEW'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_findings_matter_status', 'findings', ['matter_id', 'status', 'severity'])
    op.create_index('idx_findings_spans_gin', 'findings', ['supporting_span_ids'], postgresql_using='gin')

    op.create_table(
        'evidence_gaps',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('requirement_version_id', sa.String(length=36), sa.ForeignKey('requirement_versions.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('dimension', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='POTENTIAL_GAP'),
        sa.Column('observation', sa.Text(), nullable=False),
        sa.Column('searched_document_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_gaps_status', 'evidence_gaps', ['matter_id', 'status'])

    op.create_table(
        'research_issues',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('triggered_by_gap_id', sa.String(length=36), sa.ForeignKey('evidence_gaps.id', ondelete='SET NULL'), nullable=True),
        sa.Column('question', sa.Text(), nullable=False),
        sa.Column('preferred_authorities', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='OPEN'),
        sa.Column('synthesis_result', sa.Text(), nullable=True),
        sa.Column('cited_authority_ids', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='[]'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_riss_status', 'research_issues', ['matter_id', 'status'])

    # 7. Layer 6: Workflow & Audit Layer
    op.create_table(
        'agent_runs',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('agent_name', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='QUEUED'),
        sa.Column('input_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('output_payload', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('model_used', sa.String(length=100), nullable=False),
        sa.Column('prompt_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('completion_tokens', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('latency_ms', sa.Integer(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('idx_agent_runs_status', 'agent_runs', ['matter_id', 'agent_name', 'status'])

    op.create_table(
        'human_reviews',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('target_type', sa.String(length=50), nullable=False),
        sa.Column('target_id', sa.String(length=36), nullable=False),
        sa.Column('decision', sa.String(length=50), nullable=False),
        sa.Column('reviewer_comment', sa.Text(), nullable=True),
        sa.Column('reviewer_id', sa.String(length=100), nullable=False),
        sa.Column('reviewed_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_human_reviews_target', 'human_reviews', ['target_type', 'target_id'])
    op.create_index('idx_human_reviews_matter', 'human_reviews', ['matter_id', 'decision'])

    op.create_table(
        'audit_events',
        sa.Column('id', sa.String(length=36), primary_key=True),
        sa.Column('matter_id', sa.String(length=36), sa.ForeignKey('matters.id', ondelete='CASCADE'), nullable=False),
        sa.Column('actor_type', sa.String(length=50), nullable=False),
        sa.Column('actor_id', sa.String(length=100), nullable=False),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.String(length=36), nullable=False),
        sa.Column('payload', postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default='{}'),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('now()')),
    )
    op.create_index('idx_audit_events_matter_time', 'audit_events', ['matter_id', 'timestamp'])


def downgrade() -> None:
    # Drop in reverse order of creation to satisfy foreign key constraints
    op.drop_table('audit_events')
    op.drop_table('human_reviews')
    op.drop_table('agent_runs')
    op.drop_table('research_issues')
    op.drop_table('evidence_gaps')
    op.drop_table('findings')
    op.drop_table('evidence_mappings')
    op.drop_table('requirement_applicabilities')
    op.drop_table('requirement_versions')
    op.drop_table('requirements')
    op.drop_table('authorities')
    op.drop_table('conflicts')
    op.drop_table('relationships')
    op.drop_table('canonical_facts')
    op.drop_table('events')
    op.drop_table('source_assertions')
    op.drop_table('entities')
    op.drop_table('source_spans')
    op.drop_table('pages')
    op.drop_table('document_versions')
    op.drop_table('documents')
    op.drop_table('matters')
    op.execute("DROP EXTENSION IF EXISTS vector;")
