"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  ListOrdered,
  CheckCircle2,
  RotateCcw,
  Eye,
  Image as ImageIcon
} from "lucide-react";
import { fetchRecentDocuments, getDocumentFileUrl } from "../lib/api";

interface ProcessingQueueTabProps {
  setActiveTab: (tab: string) => void;
}

interface DocumentItem {
  id: number;
  filename: string;
  file_size: number;
  mime_type?: string;
  status: string;
  error_message?: string | null;
  ocr_used: boolean;
  processing_time_ms?: number | null;
  created_at?: string | null;
}

export default function ProcessingQueueTab({ setActiveTab }: ProcessingQueueTabProps) {
  const [docs, setDocs] = useState<DocumentItem[]>([]);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const data = await fetchRecentDocuments(25);
      setDocs(data);
    } catch (err) {
      console.error("Failed to load documents:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    void fetchRecentDocuments(25)
      .then((data) => {
        if (!ignore) {
          setDocs(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load documents:", err);
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#0c1524] text-white flex items-center justify-center shadow-xs">
            <ListOrdered className="w-5 h-5 text-emerald-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800 tracking-tight">Processing Queue & Ingestion Monitor</h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Live status of marks memo extraction batches, OCR processing times, and ingestion health.
            </p>
          </div>
        </div>

        <button
          onClick={loadData}
          className="px-3.5 py-1.5 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1.5"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          Refresh Queue
        </button>
      </div>

      {/* Queue Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading queue items...</div>
        ) : docs.length === 0 ? (
          <div className="p-12 text-center">
            <CheckCircle2 className="w-10 h-10 text-emerald-500 mx-auto mb-2" />
            <h3 className="text-sm font-bold text-slate-800">Queue is Clear</h3>
            <p className="text-xs text-slate-500 mt-1 max-w-sm mx-auto">
              No files currently waiting or processing. Upload marks memos to initiate extraction.
            </p>
            <button
              onClick={() => setActiveTab("upload")}
              className="mt-4 px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-bold text-xs"
            >
              Upload Memos
            </button>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-slate-50/70 border-b border-slate-200/60 text-[11px] font-bold text-slate-500 uppercase tracking-wider">
                  <th className="py-3 px-5">File</th>
                  <th className="py-3 px-5">Size</th>
                  <th className="py-3 px-5">Engine</th>
                  <th className="py-3 px-5">Duration</th>
                  <th className="py-3 px-5">Status</th>
                  <th className="py-3 px-5 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-xs">
                {docs.map((doc) => {
                  const isPdf = doc.filename.toLowerCase().endsWith(".pdf");
                  const mb = (doc.file_size / (1024 * 1024)).toFixed(2);
                  const isSuccess = doc.status === "COMPLETED";
                  const isNeedsReview = doc.status === "NEEDS_REVIEW";
                  const isFailed = doc.status === "FAILED";

                  return (
                    <tr key={doc.id} className="hover:bg-slate-50/70 transition-colors">
                      <td className="py-3.5 px-5 font-semibold text-slate-800 flex items-center gap-2.5">
                        <div
                          className={`w-7 h-7 rounded-lg flex items-center justify-center shrink-0 text-white text-[10px] font-bold ${
                            isPdf ? "bg-rose-500" : "bg-sky-500"
                          }`}
                        >
                          {isPdf ? "PDF" : <ImageIcon className="w-3.5 h-3.5" />}
                        </div>
                        <span className="truncate max-w-xs">{doc.filename}</span>
                      </td>
                      <td className="py-3.5 px-5 text-slate-600">{mb} MB</td>
                      <td className="py-3.5 px-5">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-bold bg-slate-100 text-slate-700 border border-slate-200">
                          {doc.ocr_used ? "Tesseract OCR" : "Digital Text"}
                        </span>
                      </td>
                      <td className="py-3.5 px-5 text-slate-600 font-mono">
                        {doc.processing_time_ms ? `${doc.processing_time_ms} ms` : "—"}
                      </td>
                      <td className="py-3.5 px-5">
                        <span
                          className={`px-2.5 py-0.5 rounded-full text-[11px] font-bold ${
                            isSuccess
                              ? "bg-emerald-50 text-emerald-700 border border-emerald-300"
                              : isNeedsReview
                              ? "bg-amber-50 text-amber-700 border border-amber-300"
                              : isFailed
                              ? "bg-rose-50 text-rose-700 border border-rose-300"
                              : "bg-blue-50 text-blue-700 border border-blue-300"
                          }`}
                        >
                          {doc.status}
                        </span>
                      </td>
                      <td className="py-3.5 px-5 text-right">
                        <a
                          href={getDocumentFileUrl(doc.id)}
                          target="_blank"
                          rel="noreferrer"
                          className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 hover:text-blue-700 p-1 rounded-lg hover:bg-slate-100"
                        >
                          <Eye className="w-4 h-4" />
                          View
                        </a>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
