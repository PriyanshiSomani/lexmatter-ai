/**
 * LexMatter AI — Document Viewer & SourceSpan Highlighter Component
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState, useEffect } from "react";
import { FileText, Eye, Bookmark, Trash2, Loader2, Target } from "lucide-react";
import { DocumentItem, SourceSpanItem, fetchDocumentSpans, deleteDocument } from "../lib/api";

interface DocumentViewerProps {
  matterId: string;
  documents: DocumentItem[];
  selectedDocId?: string | null;
  selectedSpanId?: string | null;
  onSelectDocument?: (doc: DocumentItem) => void;
  onDocumentDeleted?: () => void;
}

export const DocumentViewer: React.FC<DocumentViewerProps> = ({
  matterId,
  documents,
  selectedDocId,
  selectedSpanId,
  onSelectDocument,
  onDocumentDeleted,
}) => {
  const [activeDoc, setActiveDoc] = useState<DocumentItem | null>(documents[0] || null);
  const [spans, setSpans] = useState<SourceSpanItem[]>([]);
  const [loadingSpans, setLoadingSpans] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    if (documents.length > 0) {
      if (selectedDocId) {
        const found = documents.find((d) => d.id === selectedDocId);
        if (found) {
          setActiveDoc(found);
          return;
        }
      }
      if (!activeDoc || !documents.some((d) => d.id === activeDoc.id)) {
        setActiveDoc(documents[0]);
      }
    } else {
      setActiveDoc(null);
      setSpans([]);
    }
  }, [documents, selectedDocId]);

  useEffect(() => {
    if (!activeDoc) {
      setSpans([]);
      return;
    }
    const loadSpans = async () => {
      setLoadingSpans(true);
      try {
        const fetchedSpans = await fetchDocumentSpans(matterId, activeDoc.id);
        setSpans(fetchedSpans);
      } catch (err) {
        console.error("Failed to load document spans:", err);
      } finally {
        setLoadingSpans(false);
      }
    };
    loadSpans();
  }, [activeDoc, matterId]);

  useEffect(() => {
    if (selectedSpanId && spans.length > 0) {
      setTimeout(() => {
        const el = document.getElementById(`span-${selectedSpanId}`);
        if (el) {
          el.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 100);
    }
  }, [selectedSpanId, spans]);

  const handleDocClick = (doc: DocumentItem) => {
    setActiveDoc(doc);
    if (onSelectDocument) onSelectDocument(doc);
  };

  const handleDelete = async (e: React.MouseEvent, docId: string) => {
    e.stopPropagation();
    if (!confirm("Are you sure you want to delete this document?")) return;
    setDeletingId(docId);
    try {
      await deleteDocument(matterId, docId);
      if (onDocumentDeleted) onDocumentDeleted();
    } catch (err) {
      console.error("Failed to delete document:", err);
      alert("Failed to delete document");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="flex flex-col h-full bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
      {/* Header */}
      <div className="p-3 bg-slate-50 border-b border-slate-200 flex justify-between items-center">
        <h3 className="text-xs font-semibold text-slate-800 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-600" /> Document Viewer & Source Spans
        </h3>
        <span className="text-[11px] font-medium text-slate-500 bg-slate-200 px-2 py-0.5 rounded">
          {documents.length} Files Ingested
        </span>
      </div>

      {/* Document Selector Bar */}
      <div className="flex border-b border-slate-200 bg-slate-100/60 overflow-x-auto p-1.5 gap-1.5 scrollbar-thin">
        {documents.length === 0 ? (
          <span className="text-xs text-slate-400 p-1">No documents uploaded yet</span>
        ) : (
          documents.map((doc) => {
            const isSelected = activeDoc?.id === doc.id;
            const isDeleting = deletingId === doc.id;
            return (
              <div
                key={doc.id}
                onClick={() => handleDocClick(doc)}
                className={`group flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium cursor-pointer transition-all ${
                  isSelected
                    ? "bg-white text-blue-700 shadow-sm border border-slate-200"
                    : "text-slate-600 hover:text-slate-900 hover:bg-slate-200/50"
                }`}
              >
                <FileText className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-500" />
                <span className="truncate max-w-[140px]">{doc.title}</span>

                <button
                  onClick={(e) => handleDelete(e, doc.id)}
                  title="Delete Document"
                  disabled={isDeleting}
                  className="p-0.5 text-slate-400 hover:text-red-600 rounded transition-colors opacity-70 hover:opacity-100 ml-1"
                >
                  {isDeleting ? (
                    <Loader2 className="w-3 h-3 animate-spin text-red-500" />
                  ) : (
                    <Trash2 className="w-3 h-3" />
                  )}
                </button>
              </div>
            );
          })
        )}
      </div>

      {/* Main Document Content Workspace */}
      <div className="flex-1 p-4 overflow-y-auto bg-slate-50/30">
        {activeDoc ? (
          <div className="space-y-4">
            {/* Meta bar */}
            <div className="flex items-center justify-between text-xs text-slate-500 bg-white p-2.5 rounded border border-slate-200 shadow-xs">
              <span className="font-semibold text-slate-700">Classification: {activeDoc.document_type}</span>
              <div className="flex items-center gap-2">
                <span className="text-[11px] bg-blue-50 text-blue-700 font-mono font-medium px-2 py-0.5 rounded border border-blue-200">
                  {spans.length} Text Spans
                </span>
                <span className="text-[11px] bg-emerald-50 text-emerald-700 font-medium px-2 py-0.5 rounded border border-emerald-200">
                  {activeDoc.status}
                </span>
              </div>
            </div>

            {/* Document Spans Workspace */}
            {loadingSpans ? (
              <div className="p-8 text-center text-xs text-slate-400 flex items-center justify-center gap-2">
                <Loader2 className="w-4 h-4 animate-spin text-blue-500" /> Loading extracted text spans...
              </div>
            ) : spans.length > 0 ? (
              <div className="space-y-3 font-mono text-xs text-slate-700">
                {spans.map((span, idx) => {
                  const isHighlighted = selectedSpanId && (span.id === selectedSpanId || selectedSpanId.includes(span.id));

                  return (
                    <div
                      key={span.id}
                      id={`span-${span.id}`}
                      className={`p-3 bg-white rounded border transition-all space-y-2 ${
                        isHighlighted
                          ? "border-blue-500 ring-2 ring-blue-400/50 bg-blue-50/40 shadow-sm"
                          : "border-slate-200 hover:border-blue-300 shadow-2xs"
                      }`}
                    >
                      <div className="flex justify-between items-center text-[11px] text-blue-800 bg-blue-50/80 px-2.5 py-1 rounded font-sans">
                        <span className="font-semibold flex items-center gap-1.5">
                          {isHighlighted ? (
                            <Target className="w-3.5 h-3.5 text-blue-600 animate-pulse" />
                          ) : (
                            <Bookmark className="w-3.5 h-3.5 text-blue-600" />
                          )}
                          Span #{idx + 1} • Page {span.page_number}
                          {isHighlighted && (
                            <span className="ml-2 text-[10px] bg-blue-600 text-white px-1.5 py-0.2 rounded font-sans">
                              Active Target Citation
                            </span>
                          )}
                        </span>
                        <span className="font-mono text-[10px] text-slate-500">
                          Chars [{span.start_char}..{span.end_char}]
                        </span>
                      </div>

                      <p className="whitespace-pre-wrap leading-relaxed text-slate-800 bg-slate-50/60 p-2.5 rounded border border-slate-100 font-sans">
                        {span.text_snippet}
                      </p>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="p-8 text-center text-xs text-slate-400 bg-white rounded border border-slate-200">
                No text spans extracted for this document.
              </div>
            )}
          </div>
        ) : (
          <div className="h-full flex flex-col items-center justify-center text-slate-400 py-12">
            <Eye className="w-8 h-8 mb-2 opacity-50 text-slate-400" />
            <p className="text-xs font-medium">Select an ingested document to view text spans</p>
          </div>
        )}
      </div>
    </div>
  );
};
