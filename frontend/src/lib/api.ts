/**
 * LexMatter AI — API Client SDK & Type Definitions
 * Phase 12: Frontend Integration & UI
 * Connects Next.js Frontend to FastAPI Backend API (v1)
 */

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// --- TypeScript Domain Interfaces ---

export interface DocumentItem {
  id: str;
  matter_id: string;
  title: string;
  file_type: string;
  document_type: string;
  status: string;
  chunk_count?: number;
  created_at: string;
}

export interface RequirementItem {
  id: string;
  matter_id: string;
  requirement_title: string;
  statutory_reference: string;
  status: "EVIDENCE_LOCATED" | "PARTIAL_SUPPORT" | "POTENTIAL_GAP" | "NOT_EVALUATED";
  evaluation_dimensions: string[];
}

export interface EvidenceMappingItem {
  id: string;
  matter_id: string;
  source_assertion_id: string;
  requirement_version_id: string;
  relationship: string;
  target_dimension: string;
  relevance_score: number;
  analysis_notes: string;
  created_at: string;
}

export interface ConflictItem {
  id: string;
  matter_id: string;
  conflict_type: "DATE_MISMATCH" | "TITLE_MISMATCH" | "SALARY_MISMATCH" | "FACTUAL_CONTRADICTION";
  severity: "HIGH" | "MEDIUM" | "LOW";
  status: "OPEN" | "ATTORNEY_RESOLVED" | "IGNORED";
  description: string;
  assertion1_id: string;
  assertion2_id: string;
}

export interface EvidenceGapItem {
  id: string;
  matter_id: string;
  requirement_version_id: string;
  dimension: string;
  status: "POTENTIAL_GAP" | "RESOLVED_BY_RESEARCH" | "ATTORNEY_DISMISSED";
  observation: string;
  searched_document_count: number;
  created_at: string;
}

export interface AgentOrchestrationResponse {
  matter_id: string;
  status: "COMPLETED" | "PAUSED_FOR_REVIEW";
  phase_completion: {
    evidence_mapping: boolean;
    consistency_check: boolean;
    research: boolean;
    verification: boolean;
  };
  summary_counts: {
    mapped_evidence_count: number;
    identified_conflict_count: number;
    identified_gap_count: number;
    total_iterations: number;
  };
  human_review: {
    required: boolean;
    reasons: string[];
  };
  audit_log_count: number;
}

export interface BriefingReportResponse {
  report_id: string;
  matter_id: string;
  case_type_code: string;
  generated_at: string;
  title: string;
  executive_summary: string;
  full_markdown: string;
  non_adjudicative_disclaimer: string;
  mapped_evidence_count: number;
  identified_conflict_count: number;
  identified_gap_count: number;
}

export interface LineageNodeItem {
  node_id: string;
  node_type: string;
  label: string;
  metadata?: Record<string, any>;
}

export interface LineageEdgeItem {
  source_id: string;
  target_id: string;
  relationship_type: string;
}

export interface LineageResponse {
  root_entity_id: string;
  matter_id: string;
  nodes: LineageNodeItem[];
  edges: LineageEdgeItem[];
  overall_confidence: {
    composite_confidence: number;
    operational_tier: string;
    tier_label: string;
    explanation: string;
  };
  provenance_verified: boolean;
}

// --- API Client Methods ---

export async function uploadDocument(matterId: string, file: File, docType: string = "UNKNOWN"): Promise<DocumentItem> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("matter_id", matterId);
  formData.append("document_type", docType);

  const res = await fetch(`${API_BASE_URL}/documents/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Document upload failed");
  }

  return res.json();
}

export async function fetchMatterDocuments(matterId: string): Promise<DocumentItem[]> {
  const res = await fetch(`${API_BASE_URL}/documents/matter/${matterId}`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchRequirements(matterId: string): Promise<RequirementItem[]> {
  const res = await fetch(`${API_BASE_URL}/requirements/matter/${matterId}`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchEvidenceMappings(matterId: string): Promise<EvidenceMappingItem[]> {
  const res = await fetch(`${API_BASE_URL}/evidence/matters/${matterId}/evidence`);
  if (!res.ok) return [];
  return res.json();
}

export async function fetchConflicts(matterId: string): Promise<ConflictItem[]> {
  const res = await fetch(`${API_BASE_URL}/conflicts/matters/${matterId}`);
  if (!res.ok) return [];
  return res.json();
}

export async function resolveConflict(conflictId: string, resolutionNotes: string): Promise<any> {
  const res = await fetch(`${API_BASE_URL}/conflicts/${conflictId}/resolve`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ resolution_notes: resolutionNotes }),
  });
  if (!res.ok) throw new Error("Failed to resolve conflict");
  return res.json();
}

export async function fetchEvidenceGaps(matterId: string): Promise<EvidenceGapItem[]> {
  const res = await fetch(`${API_BASE_URL}/evidence/matters/${matterId}/gaps`);
  if (!res.ok) return [];
  return res.json();
}

export async function triggerAgentOrchestration(matterId: string, caseTypeCode: string = "L1B"): Promise<AgentOrchestrationResponse> {
  const res = await fetch(`${API_BASE_URL}/matters/${matterId}/orchestration/analyze?case_type_code=${caseTypeCode}`, {
    method: "POST",
  });
  if (!res.ok) {
    const error = await res.json();
    throw new Error(error.detail || "Orchestration execution failed");
  }
  return res.json();
}

export async function generateBriefingReport(matterId: string, caseTypeCode: string = "L1B"): Promise<BriefingReportResponse> {
  const res = await fetch(`${API_BASE_URL}/matters/${matterId}/reports/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ case_type_code: caseTypeCode }),
  });
  if (!res.ok) throw new Error("Report generation failed");
  return res.json();
}

export function getPdfReportDownloadUrl(matterId: string, caseTypeCode: string = "L1B"): string {
  return `${API_BASE_URL}/matters/${matterId}/reports/export?export_format=PDF&case_type_code=${caseTypeCode}`;
}

export async function fetchEntityLineage(entityId: string): Promise<LineageResponse> {
  const res = await fetch(`${API_BASE_URL}/audit/lineage/${entityId}`);
  if (!res.ok) throw new Error("Lineage fetch failed");
  return res.json();
}
