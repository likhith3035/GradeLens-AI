"use client";

import React, { useState, useRef } from "react";
import {
  UploadCloud,
  FileText,
  AlertCircle,
  CheckCircle2,
  Clock,
  RefreshCw,
  X,
  FileCheck2,
  AlertTriangle
} from "lucide-react";
import { uploadFiles, loadSamplePack } from "../lib/api";

interface UploadTabProps {
  onUploadSuccess: () => void;
  setActiveTab: (tab: string) => void;
}

interface FileQueueItem {
  id: string;
  file: File;
  name: string;
  size: number;
  status: "pending" | "uploading" | "processing" | "completed" | "needs_review" | "failed";
  error?: string;
  memosExtracted?: number;
  rollNumber?: string;
  studentName?: string;
  semester?: string;
  sgpa?: number | null;
  issuesCount?: number;
}

export default function UploadTab({ onUploadSuccess, setActiveTab }: UploadTabProps) {
  const [items, setItems] = useState<FileQueueItem[]>([]);
  const [profile, setProfile] = useState<string>("auto");
  const [isDragging, setIsDragging] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [loadingSample, setLoadingSample] = useState(false);
  const [batchSummary, setBatchSummary] = useState<{
    total: number;
    completed: number;
    needsReview: number;
    failed: number;
    memosExtracted?: number;
  } | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFiles = (fileList: FileList | File[]) => {
    const newItems: FileQueueItem[] = [];
    const allowed = [".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp", ".zip"];

    for (let i = 0; i < fileList.length; i++) {
      const f = fileList[i];
      const ext = f.name.substring(f.name.lastIndexOf(".")).toLowerCase();
      if (!allowed.includes(ext)) {
        alert(`File "${f.name}" has an unsupported format. Allowed formats: ${allowed.join(", ")}`);
        continue;
      }

      if (f.size > 100 * 1024 * 1024) {
        alert(`File "${f.name}" exceeds 100 MB limit.`);
        continue;
      }

      newItems.push({
        id: `${f.name}_${Date.now()}_${Math.random().toString(36).substring(2, 7)}`,
        file: f,
        name: f.name,
        size: f.size,
        status: "pending",
      });
    }

    setItems((prev) => [...prev, ...newItems]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleFiles(e.dataTransfer.files);
    }
  };

  const removeItem = (id: string) => {
    setItems((prev) => prev.filter((it) => it.id !== id));
  };

  const clearQueue = () => {
    setItems([]);
    setBatchSummary(null);
  };

  const handleLoadDemoPack = async () => {
    setLoadingSample(true);
    try {
      const res = await loadSamplePack();
      alert(`🎉 ${res.message}`);
      onUploadSuccess();
      setActiveTab("students");
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Could not load sample pack";
      alert(`Could not load sample pack: ${msg}`);
    } finally {
      setLoadingSample(false);
    }
  };

  const startBatchProcessing = async () => {
    const pendingItems = items.filter((it) => it.status === "pending" || it.status === "failed");
    if (pendingItems.length === 0) return;

    setIsProcessing(true);
    setItems((prev) =>
      prev.map((it) =>
        it.status === "pending" || it.status === "failed" ? { ...it, status: "uploading" } : it
      )
    );

    try {
      const filesToUpload = pendingItems.map((it) => it.file);
      const res = await uploadFiles(filesToUpload, profile);

      // Map response to queue items
      const summaryItems = res.items || [];
      const updated = items.map((it) => {
        const match = summaryItems.find((s) => s.filename === it.name);
        if (match) {
          const mappedStatus = match.status.toLowerCase();
          const validStatus: FileQueueItem["status"] =
            mappedStatus === "completed" ||
            mappedStatus === "needs_review" ||
            mappedStatus === "failed" ||
            mappedStatus === "processing" ||
            mappedStatus === "uploading"
              ? mappedStatus
              : "completed";

          return {
            ...it,
            status: validStatus,
            error: (match as { error?: string }).error,
            memosExtracted: (match as { memos_extracted?: number }).memos_extracted || 1,
            rollNumber: match.roll_number,
            studentName: match.student_name,
            semester: match.semester,
            sgpa: match.sgpa,
            issuesCount: match.issues_count,
          };
        }
        return it;
      });

      const totalMemos = summaryItems.reduce(
        (acc: number, cur) => acc + ((cur as { memos_extracted?: number }).memos_extracted || 1),
        0
      );

      setItems(updated);
      setBatchSummary({
        total: res.total_files || 0,
        completed: res.processed_files || 0,
        needsReview: res.needs_review_files || 0,
        failed: res.failed_files || 0,
        memosExtracted: totalMemos,
      });

      onUploadSuccess();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Upload or processing error";
      alert(`Upload or processing error: ${msg}`);
      setItems((prev) =>
        prev.map((it) =>
          it.status === "uploading" || it.status === "processing"
            ? { ...it, status: "failed", error: msg }
            : it
        )
      );
    } finally {
      setIsProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header and Profile Selector */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#0c1524] text-white flex items-center justify-center shadow-xs">
            <UploadCloud className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800 tracking-tight">
              Batch & Multi-Memo Ingestion Center
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Bulk upload dozens of memos, multi-page semester transcripts, class gazettes, or single ZIP archives.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3">
          <label className="text-xs font-semibold text-slate-600">Extraction Profile:</label>
          <select
            value={profile}
            onChange={(e) => setProfile(e.target.value)}
            disabled={isProcessing}
            className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-xl px-3 py-1.5 focus:outline-none focus:ring-1 focus:ring-emerald-500 text-slate-700"
          >
            <option value="auto">Auto-Detect Profile</option>
            <option value="jntu_autonomous">JNTU / Autonomous Engineering (R18/R20)</option>
            <option value="anna_university">Anna University & Affiliated</option>
            <option value="general">Universal Format (Regex & Table)</option>
          </select>
        </div>
      </div>

      {/* Quick Load Multi-Memo Sample Pack Banner */}
      <div className="bg-gradient-to-r from-blue-50 via-indigo-50 to-emerald-50 border border-blue-200 rounded-2xl p-4 flex flex-col sm:flex-row sm:items-center justify-between gap-3 shadow-sm">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-blue-600 text-white flex items-center justify-center font-bold text-sm shadow-md">
            ⚡
          </div>
          <div>
            <div className="font-bold text-xs text-slate-800">
              Need Multi-Memo Test Files? Instant Multi-University Demo Pack
            </div>
            <div className="text-[11px] text-slate-600">
              Loads 6 documents producing 10 marks memos: 3-Page Multi-Semester Progression, 3-Student Class Gazette, JNTU, and Anna Univ.
            </div>
          </div>
        </div>
        <button
          onClick={handleLoadDemoPack}
          disabled={loadingSample || isProcessing}
          className="px-4 py-2 rounded-xl bg-blue-600 hover:bg-blue-700 text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-2 whitespace-nowrap self-start sm:self-auto disabled:opacity-50"
        >
          {loadingSample ? (
            <>
              <RefreshCw className="w-3.5 h-3.5 animate-spin" />
              Ingesting Multi-Memo Batch...
            </>
          ) : (
            <>
              <span>Load 10-Memo Demo Batch</span>
            </>
          )}
        </button>
      </div>

      {/* Drag & Drop Zone */}
      <div
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => fileInputRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-all ${
          isDragging
            ? "border-blue-500 bg-blue-50/70 scale-[0.99]"
            : "border-slate-300 hover:border-blue-400 bg-white hover:bg-slate-50/50"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          multiple
          accept=".pdf,.png,.jpg,.jpeg,.bmp,.tiff,.webp,.zip"
          className="hidden"
          onChange={(e) => {
            if (e.target.files) handleFiles(e.target.files);
          }}
        />
        <div className="max-w-md mx-auto flex flex-col items-center">
          <div className="w-14 h-14 rounded-2xl bg-blue-50 text-blue-600 flex items-center justify-center mb-4 shadow-inner">
            <UploadCloud className="w-8 h-8" />
          </div>
          <h3 className="font-semibold text-slate-800 text-sm mb-1">
            Drag & drop marks memos or <span className="text-blue-600 underline">browse files</span>
          </h3>
          <p className="text-xs text-slate-500 mb-4">
            Supports single memos, multi-page semester transcripts, class gazettes, and .ZIP archives.
          </p>
          <div className="flex flex-wrap items-center justify-center gap-2 text-[11px] text-slate-500 font-medium">
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700">📦 .ZIP Batch Archives</span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700">📄 Multi-Semester PDFs</span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700">👥 Class Gazettes</span>
            <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700">🔍 OCR Auto-Detection</span>
          </div>
        </div>
      </div>

      {/* Batch Summary Alert (if completed) */}
      {batchSummary && (
        <div className="bg-white rounded-xl p-4 border border-slate-200 shadow-sm flex flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center font-bold">
              <FileCheck2 className="w-5 h-5" />
            </div>
            <div>
              <h4 className="font-bold text-slate-800 text-sm">Batch Processing Complete</h4>
              <p className="text-xs text-slate-500">
                {batchSummary.total} documents processed: {batchSummary.completed} verified,{" "}
                {batchSummary.needsReview} awaiting review, {batchSummary.failed} failed.
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {batchSummary.needsReview > 0 && (
              <button
                onClick={() => setActiveTab("review")}
                className="px-3.5 py-1.5 rounded-lg bg-amber-500 hover:bg-amber-600 text-white text-xs font-semibold shadow-sm transition-all flex items-center gap-1.5"
              >
                <AlertTriangle className="w-3.5 h-3.5" />
                Go to Verification Queue ({batchSummary.needsReview})
              </button>
            )}
            <button
              onClick={() => setActiveTab("students")}
              className="px-3.5 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-900 text-white text-xs font-semibold shadow-sm transition-all"
            >
              View Student Records
            </button>
          </div>
        </div>
      )}

      {/* Upload Queue List */}
      {items.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-200 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <h3 className="font-semibold text-slate-800 text-sm">Upload Batch Queue</h3>
              <span className="px-2 py-0.5 rounded-full text-xs font-bold bg-slate-100 text-slate-600">
                {items.length} files
              </span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={clearQueue}
                disabled={isProcessing}
                className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-500 hover:text-slate-800 hover:bg-slate-100 transition-colors"
              >
                Clear Queue
              </button>
              <button
                onClick={startBatchProcessing}
                disabled={isProcessing || !items.some((it) => it.status === "pending" || it.status === "failed")}
                className={`px-4 py-1.5 rounded-lg text-xs font-semibold text-white shadow-sm transition-all flex items-center gap-1.5 ${
                  isProcessing
                    ? "bg-blue-400 cursor-not-allowed"
                    : "bg-blue-600 hover:bg-blue-700"
                }`}
              >
                {isProcessing ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                    Processing Batch...
                  </>
                ) : (
                  <>
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Start Extraction ({items.filter((it) => it.status === "pending" || it.status === "failed").length})
                  </>
                )}
              </button>
            </div>
          </div>

          <div className="divide-y divide-slate-100 max-h-96 overflow-y-auto">
            {items.map((item) => {
              const statusPill = {
                pending: { label: "Pending", bg: "bg-slate-100 text-slate-600", icon: Clock },
                uploading: { label: "Uploading", bg: "bg-blue-50 text-blue-600 animate-pulse", icon: RefreshCw },
                processing: { label: "Processing", bg: "bg-indigo-50 text-indigo-600 animate-pulse", icon: RefreshCw },
                completed: { label: "Verified", bg: "bg-emerald-50 text-emerald-700 border border-emerald-200", icon: CheckCircle2 },
                needs_review: { label: "Needs Review", bg: "bg-amber-50 text-amber-700 border border-amber-300 font-bold", icon: AlertTriangle },
                failed: { label: "Failed", bg: "bg-red-50 text-red-600 border border-red-200", icon: AlertCircle },
              }[item.status];

              const Icon = statusPill.icon;

              return (
                <div key={item.id} className="p-3.5 flex items-center justify-between hover:bg-slate-50 transition-colors">
                  <div className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="w-8 h-8 rounded-lg bg-slate-100 text-slate-600 flex items-center justify-center shrink-0">
                      <FileText className="w-4 h-4" />
                    </div>
                    <div className="min-w-0 flex-1">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-xs text-slate-800 truncate">{item.name}</span>
                        <span className="text-[11px] text-slate-400">
                          ({(item.size / 1024).toFixed(1)} KB)
                        </span>
                      </div>
                      {item.rollNumber && (
                        <div className="text-[11px] text-slate-500 mt-0.5 flex flex-wrap items-center gap-2">
                          {item.memosExtracted && item.memosExtracted > 1 && (
                            <span className="inline-flex items-center px-2 py-0.5 rounded text-[10px] font-bold bg-purple-100 text-purple-700 border border-purple-200">
                              ⚡ {item.memosExtracted} Memos Extracted (Multi-Semester / Gazette)
                            </span>
                          )}
                          <span className="font-mono font-medium text-blue-700">{item.rollNumber}</span>
                          {item.studentName && <span>• {item.studentName}</span>}
                          {item.semester && <span>• {item.semester}</span>}
                          {item.sgpa !== null && item.sgpa !== undefined && <span>• SGPA: {item.sgpa}</span>}
                        </div>
                      )}
                      {item.error && (
                        <div className="text-[11px] text-red-600 mt-0.5 font-medium">{item.error}</div>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center gap-3 shrink-0 ml-4">
                    <span className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold ${statusPill.bg}`}>
                      <Icon className="w-3 h-3" />
                      {statusPill.label}
                    </span>

                    {item.status === "pending" && !isProcessing && (
                      <button
                        onClick={() => removeItem(item.id)}
                        className="text-slate-400 hover:text-red-500 transition-colors"
                      >
                        <X className="w-4 h-4" />
                      </button>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
