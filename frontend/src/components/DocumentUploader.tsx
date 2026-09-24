/**
 * LexMatter AI — Drag-and-Drop Document Uploader Component
 * Phase 12: Frontend Integration & UI
 */

"use client";

import React, { useState } from "react";
import { Upload, FileText, CheckCircle2, AlertCircle, Loader2, Trash2 } from "lucide-react";
import { uploadDocument, clearMatterDocuments, DocumentItem } from "../lib/api";

interface DocumentUploaderProps {
  matterId: string;
  onUploadSuccess?: (doc: DocumentItem) => void;
  onClearSuccess?: () => void;
}

export const DocumentUploader: React.FC<DocumentUploaderProps> = ({
  matterId,
  onUploadSuccess,
  onClearSuccess,
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [clearing, setClearing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [docType, setDocType] = useState<string>("SUPPORT_LETTER");

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const processFile = async (file: File) => {
    if (!file) return;
    setUploading(true);
    setError(null);
    setSuccessMsg(null);

    try {
      const doc = await uploadDocument(matterId, file, docType);
      setSuccessMsg(`Successfully uploaded & ingested "${doc.title}"`);
      if (onUploadSuccess) onUploadSuccess(doc);
    } catch (err: any) {
      setError(err.message || "Failed to upload document");
    } finally {
      setUploading(false);
      setIsDragging(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      processFile(files[0]);
    }
  };

  const handleClearAll = async () => {
    if (!confirm("Are you sure you want to delete all uploaded documents for this matter?")) return;
    setClearing(true);
    setError(null);
    try {
      await clearMatterDocuments(matterId);
      setSuccessMsg("Cleared all matter documents successfully.");
      if (onClearSuccess) onClearSuccess();
    } catch (err: any) {
      setError(err.message || "Failed to clear matter documents");
    } finally {
      setClearing(false);
    }
  };

  return (
    <div className="w-full p-4 bg-white rounded-lg border border-slate-200 shadow-sm">
      <div className="flex justify-between items-center mb-3">
        <h3 className="text-sm font-semibold text-slate-800 flex items-center gap-2">
          <FileText className="w-4 h-4 text-blue-600" /> Upload Matter Document
        </h3>

        <div className="flex items-center gap-2">
          <select
            value={docType}
            onChange={(e) => setDocType(e.target.value)}
            className="text-xs bg-slate-50 border border-slate-200 rounded px-2 py-1 text-slate-700 font-medium"
          >
            <option value="SUPPORT_LETTER">Petition Support Letter</option>
            <option value="FORM_I129">Form I-129 Petition</option>
            <option value="PAY_STUB">Pay Stubs / Salary Proof</option>
            <option value="RESUME">Beneficiary Resume / CV</option>
            <option value="ORGANIZATIONAL_CHART">Org Chart</option>
          </select>

          <button
            onClick={handleClearAll}
            disabled={clearing}
            title="Delete all uploaded documents for this matter"
            className="px-2.5 py-1 text-xs text-red-600 hover:text-red-700 bg-red-50 hover:bg-red-100 rounded border border-red-200 font-medium transition-colors flex items-center gap-1"
          >
            {clearing ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <Trash2 className="w-3.5 h-3.5" />}
            Clear All
          </button>
        </div>
      </div>

      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        className={`relative flex flex-col items-center justify-center p-6 border-2 border-dashed rounded-lg transition-colors ${
          isDragging ? "border-blue-500 bg-blue-50/50" : "border-slate-300 hover:border-blue-400 bg-slate-50/50"
        }`}
      >
        <input
          type="file"
          accept=".pdf,.txt,.docx"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />

        {uploading ? (
          <div className="flex flex-col items-center gap-2 text-blue-600">
            <Loader2 className="w-8 h-8 animate-spin" />
            <p className="text-xs font-medium">Extracting text & computing vector spans...</p>
          </div>
        ) : (
          <div className="flex flex-col items-center gap-2 text-center">
            <div className="p-3 bg-blue-100 rounded-full text-blue-600">
              <Upload className="w-6 h-6" />
            </div>
            <div>
              <p className="text-xs font-medium text-slate-700">
                <span className="font-semibold text-blue-600">Click to upload</span> or drag and drop
              </p>
              <p className="text-[11px] text-slate-400 mt-1">PDF, TXT, or DOCX (Max 25MB)</p>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-3 p-2 bg-red-50 text-red-700 rounded text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 shrink-0" /> {error}
        </div>
      )}

      {successMsg && (
        <div className="mt-3 p-2 bg-emerald-50 text-emerald-700 rounded text-xs flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 shrink-0" /> {successMsg}
        </div>
      )}
    </div>
  );
};
