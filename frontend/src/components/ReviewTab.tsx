"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  AlertTriangle,
  CheckCircle2,
  FileText,
  Check,
  Eye,
  RotateCcw,
  CheckCheck,
  Calculator,
  Sparkles
} from "lucide-react";
import {
  fetchReviewQueue,
  fetchReviewDetail,
  submitCorrection,
  resolveAllReviewItems,
  getDocumentFileUrl
} from "../lib/api";
import { ReviewQueueItem, ReviewDetail, SubjectMark } from "../lib/types";

interface ReviewTabProps {
  onReviewResolved: () => void;
}

interface EditFormState {
  student_name: string;
  roll_number: string;
  branch: string;
  semester: string;
  sgpa: string | number;
  cgpa: string | number;
  subjects: SubjectMark[];
}

export default function ReviewTab({ onReviewResolved }: ReviewTabProps) {
  const [queue, setQueue] = useState<ReviewQueueItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedRecord, setSelectedRecord] = useState<ReviewDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [editState, setEditState] = useState<EditFormState>({
    student_name: "",
    roll_number: "",
    branch: "",
    semester: "",
    sgpa: "",
    cgpa: "",
    subjects: [],
  });
  const [saving, setSaving] = useState(false);
  const [batchResolving, setBatchResolving] = useState(false);
  const [statusMessage, setStatusMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);
  const [showRawText, setShowRawText] = useState(false);
  const [showDocPreview, setShowDocPreview] = useState(false);

  const loadQueue = useCallback(async () => {
    try {
      const data = await fetchReviewQueue();
      setQueue(data);
    } catch (err) {
      console.error("Failed to load review queue:", err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let ignore = false;
    void fetchReviewQueue()
      .then((data) => {
        if (!ignore) {
          setQueue(data);
          setLoading(false);
        }
      })
      .catch((err) => {
        console.error("Failed to load review queue:", err);
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, []);

  const openRecord = async (resultId: number) => {
    setDetailLoading(true);
    setStatusMessage(null);
    try {
      const detail = await fetchReviewDetail(resultId);
      setSelectedRecord(detail);
      setEditState({
        student_name: detail.student.name || "",
        roll_number: detail.student.roll_number || "",
        branch: detail.student.branch || "",
        semester: detail.semester_info.semester || "",
        sgpa: detail.semester_info.sgpa ?? "",
        cgpa: detail.semester_info.cgpa ?? "",
        subjects: detail.subjects.map((s) => ({ ...s })),
      });
    } catch {
      setStatusMessage({ type: "error", text: "Failed to load record details" });
    } finally {
      setDetailLoading(false);
    }
  };

  const handleSubjectChange = (
    idx: number,
    field: keyof SubjectMark,
    val: string | number | boolean | null
  ) => {
    setEditState((prev) => {
      const newSubs = [...prev.subjects];
      newSubs[idx] = { ...newSubs[idx], [field]: val };
      return { ...prev, subjects: newSubs };
    });
  };

  // Helper to compute calculated SGPA on the fly from current subjects in edit state
  const computeCalculatedSgpa = () => {
    const GRADE_MAP: Record<string, number> = {
      O: 10,
      "A+": 9,
      A: 8,
      "B+": 7,
      B: 6,
      C: 5,
      P: 4,
      F: 0,
      AB: 0,
    };
    let totalPoints = 0;
    let totalCredits = 0;

    for (const sub of editState.subjects) {
      const credits = sub.credits ?? 0;
      if (credits <= 0) continue;
      const g = (sub.grade || "").trim().toUpperCase();
      const pts = sub.grade_points ?? GRADE_MAP[g] ?? 0;
      totalCredits += credits;
      totalPoints += credits * pts;
    }

    if (totalCredits === 0) return null;
    return (totalPoints / totalCredits).toFixed(2);
  };

  const handleAutoFillCalculatedSgpa = () => {
    const calc = computeCalculatedSgpa();
    if (calc !== null) {
      setEditState((prev) => ({ ...prev, sgpa: calc }));
      setStatusMessage({ type: "success", text: `Updated SGPA to calculated value: ${calc}` });
    }
  };

  const handleSaveCorrection = async () => {
    if (!selectedRecord) return;
    setSaving(true);
    setStatusMessage(null);
    try {
      await submitCorrection(selectedRecord.result_id, {
        student_name: editState.student_name,
        roll_number: editState.roll_number,
        branch: editState.branch,
        semester: editState.semester,
        sgpa: editState.sgpa !== "" ? parseFloat(String(editState.sgpa)) : null,
        cgpa: editState.cgpa !== "" ? parseFloat(String(editState.cgpa)) : null,
        subject_updates: editState.subjects,
        verification_status: "VERIFIED",
        actor: "Academic Reviewer",
      });

      setStatusMessage({ type: "success", text: "Record successfully verified and updated with audit log!" });
      setSelectedRecord(null);
      await loadQueue();
      onReviewResolved();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Error saving correction";
      setStatusMessage({ type: "error", text: msg });
    } finally {
      setSaving(false);
    }
  };

  const handleResolveAll = async () => {
    if (queue.length === 0) return;
    const confirmResolve = window.confirm(
      `Are you sure you want to Auto-Resolve all ${queue.length} flagged records?\n\nThis will automatically recalculate academic summaries, accept verified subject grades, clear issues, and mark records as VERIFIED.`
    );
    if (!confirmResolve) return;

    setBatchResolving(true);
    setStatusMessage(null);
    try {
      const res = await resolveAllReviewItems("Academic Reviewer (Batch Fix)");
      setStatusMessage({
        type: "success",
        text: res.message || `Successfully auto-resolved ${res.resolved_count} records.`,
      });
      setSelectedRecord(null);
      await loadQueue();
      onReviewResolved();
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Failed to auto-resolve queue records";
      setStatusMessage({ type: "error", text: msg });
    } finally {
      setBatchResolving(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-[#0c1524] text-white flex items-center justify-center shadow-xs">
            <AlertTriangle className="w-5 h-5 text-amber-400" />
          </div>
          <div>
            <h2 className="text-base font-bold text-slate-800 tracking-tight">
              Extraction Verification & Review Queue
            </h2>
            <p className="text-xs text-slate-500 mt-0.5">
              Side-by-side review for marks memos with calculation mismatches, low OCR confidence, or missing mandatory fields.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          {queue.length > 0 && (
            <button
              id="fix-all-btn"
              onClick={handleResolveAll}
              disabled={batchResolving}
              className="px-4 py-2 rounded-xl bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-700 hover:to-teal-700 text-white text-xs font-bold shadow-sm transition-all flex items-center gap-2 cursor-pointer disabled:opacity-50"
            >
              <CheckCheck className="w-4 h-4 text-emerald-100" />
              <span>{batchResolving ? "Resolving All..." : `Fix & Approve All (${queue.length})`}</span>
            </button>
          )}

          <button
            onClick={loadQueue}
            className="px-3.5 py-2 rounded-xl border border-slate-200 text-xs font-semibold text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Refresh Queue
          </button>
        </div>
      </div>

      {statusMessage && (
        <div
          className={`p-3.5 rounded-xl text-xs font-medium flex items-center gap-2 border ${
            statusMessage.type === "success"
              ? "bg-emerald-50 text-emerald-800 border-emerald-200"
              : "bg-rose-50 text-rose-800 border-rose-200"
          }`}
        >
          {statusMessage.type === "success" ? (
            <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          ) : (
            <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
          )}
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* Main Container */}
      {loading ? (
        <div className="bg-white rounded-xl p-12 border border-slate-200 text-center text-slate-400 text-sm">
          Loading verification queue...
        </div>
      ) : queue.length === 0 ? (
        <div className="bg-white rounded-xl p-12 border border-slate-200 text-center">
          <div className="w-12 h-12 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center mx-auto mb-3">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <h3 className="font-bold text-slate-800 text-base mb-1">All Records Verified</h3>
          <p className="text-xs text-slate-500 max-w-md mx-auto">
            There are currently no records flagged for review. All uploaded memos have satisfied data integrity and calculation checks.
          </p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Queue List Column */}
          <div className="lg:col-span-1 space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                Flagged Items ({queue.length})
              </h3>
              <span className="text-[11px] text-slate-400">Select to inspect</span>
            </div>

            <div className="space-y-2">
              {queue.map((item) => {
                const isSelected = selectedRecord?.result_id === item.result_id;
                return (
                  <div
                    key={item.result_id}
                    onClick={() => openRecord(item.result_id)}
                    className={`p-4 rounded-xl border transition-all cursor-pointer ${
                      isSelected
                        ? "bg-blue-50/50 border-blue-500 shadow-sm ring-1 ring-blue-500"
                        : "bg-white border-slate-200 hover:border-slate-300 hover:shadow-sm"
                    }`}
                  >
                    <div className="flex items-center justify-between mb-1">
                      <span className="font-mono font-bold text-xs text-blue-700">{item.roll_number}</span>
                      <span className="text-[11px] px-2 py-0.5 rounded-full font-bold bg-amber-50 text-amber-700 border border-amber-300">
                        {item.issues_count} Issues
                      </span>
                    </div>
                    <div className="font-semibold text-xs text-slate-800 truncate mb-1">
                      {item.student_name}
                    </div>
                    <div className="text-[11px] text-slate-500 flex items-center justify-between">
                      <span>Sem: {item.semester}</span>
                      <span className="truncate max-w-[140px]">Source: {item.source_filename}</span>
                    </div>
                    {item.issues && item.issues.length > 0 && (
                      <div className="mt-2 text-[11px] text-amber-800 bg-amber-50/80 p-2 rounded-lg border border-amber-200/60 leading-tight">
                        <strong>{item.issues[0].type}:</strong> {item.issues[0].message}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          {/* Verification Editor Column */}
          <div className="lg:col-span-2">
            {detailLoading ? (
              <div className="bg-white rounded-xl p-12 border border-slate-200 text-center text-slate-400 text-sm">
                Loading record for verification...
              </div>
            ) : selectedRecord ? (
              <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden space-y-5 p-5">
                {/* Header Action Bar */}
                <div className="flex flex-wrap items-center justify-between border-b border-slate-100 pb-4 gap-3">
                  <div>
                    <h3 className="font-bold text-slate-800 text-base">Record Correction & Approval</h3>
                    <p className="text-xs text-slate-500">
                      Source Document: <span className="font-medium text-slate-700">{selectedRecord.document.filename}</span>
                    </p>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowDocPreview(!showDocPreview)}
                      className={`px-3 py-1.5 rounded-lg border text-xs font-medium transition-colors flex items-center gap-1.5 cursor-pointer ${
                        showDocPreview
                          ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                          : "bg-white border-slate-300 text-slate-700 hover:bg-slate-50"
                      }`}
                    >
                      <FileText className="w-3.5 h-3.5" />
                      {showDocPreview ? "Hide Original Memo" : "View Original Memo PDF"}
                    </button>
                    <button
                      onClick={() => setShowRawText(!showRawText)}
                      className="px-3 py-1.5 rounded-lg border border-slate-300 text-xs font-medium text-slate-700 hover:bg-slate-50 transition-colors flex items-center gap-1.5 cursor-pointer"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      {showRawText ? "Hide Raw Text" : "View Raw Text"}
                    </button>
                    <button
                      onClick={handleSaveCorrection}
                      disabled={saving}
                      className="px-4 py-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-sm transition-all flex items-center gap-1.5 cursor-pointer"
                    >
                      <Check className="w-3.5 h-3.5" />
                      {saving ? "Saving..." : "Verify & Save"}
                    </button>
                  </div>
                </div>

                {/* Original Document PDF Viewer (collapsible) */}
                {showDocPreview && selectedRecord.document?.id && (
                  <div className="border border-slate-300 rounded-xl overflow-hidden shadow-sm bg-slate-900">
                    <div className="px-3 py-2 bg-slate-800 text-slate-300 text-xs font-medium flex items-center justify-between border-b border-slate-700">
                      <span>Live Document Viewer: {selectedRecord.document.filename}</span>
                      <a
                        href={getDocumentFileUrl(selectedRecord.document.id)}
                        target="_blank"
                        rel="noreferrer"
                        className="text-blue-400 hover:underline flex items-center gap-1"
                      >
                        Open in New Tab ↗
                      </a>
                    </div>
                    <iframe
                      src={getDocumentFileUrl(selectedRecord.document.id)}
                      className="w-full h-80 border-0 bg-white"
                      title="Original Marks Memorandum PDF"
                    />
                  </div>
                )}

                {/* Raw Text View (collapsible) */}
                {showRawText && (
                  <div className="bg-slate-900 text-slate-200 p-4 rounded-xl text-xs font-mono max-h-48 overflow-y-auto whitespace-pre-wrap border border-slate-800">
                    <div className="text-[10px] uppercase font-bold text-slate-400 mb-2">Original Extracted Text:</div>
                    {selectedRecord.semester_info.raw_text || "No raw text recorded."}
                  </div>
                )}

                {/* Student Info Form Fields */}
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-50/70 p-4 rounded-xl border border-slate-200">
                  <div>
                    <label className="text-[11px] font-bold uppercase text-slate-500 mb-1 block">Roll Number</label>
                    <input
                      type="text"
                      value={editState.roll_number || ""}
                      onChange={(e) => setEditState({ ...editState, roll_number: e.target.value })}
                      className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-mono font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-bold uppercase text-slate-500 mb-1 block">Student Name</label>
                    <input
                      type="text"
                      value={editState.student_name || ""}
                      onChange={(e) => setEditState({ ...editState, student_name: e.target.value })}
                      className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-bold uppercase text-slate-500 mb-1 block">Branch</label>
                    <input
                      type="text"
                      value={editState.branch || ""}
                      onChange={(e) => setEditState({ ...editState, branch: e.target.value })}
                      className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-bold uppercase text-slate-500 mb-1 block">Semester</label>
                    <input
                      type="text"
                      value={editState.semester || ""}
                      onChange={(e) => setEditState({ ...editState, semester: e.target.value })}
                      className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
                    />
                  </div>
                  <div>
                    <div className="flex items-center justify-between mb-1">
                      <label className="text-[11px] font-bold uppercase text-slate-500 block">SGPA</label>
                      <button
                        type="button"
                        onClick={handleAutoFillCalculatedSgpa}
                        className="text-[10px] text-blue-600 hover:text-blue-800 flex items-center gap-1 font-semibold cursor-pointer"
                        title="Auto-calculate SGPA from credits and grade points"
                      >
                        <Sparkles className="w-2.5 h-2.5" />
                        Auto-calc
                      </button>
                    </div>
                    <input
                      type="number"
                      step="0.01"
                      value={editState.sgpa ?? ""}
                      onChange={(e) => setEditState({ ...editState, sgpa: e.target.value })}
                      className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
                    />
                  </div>
                  <div>
                    <label className="text-[11px] font-bold uppercase text-slate-500 mb-1 block">CGPA</label>
                    <input
                      type="number"
                      step="0.01"
                      value={editState.cgpa ?? ""}
                      onChange={(e) => setEditState({ ...editState, cgpa: e.target.value })}
                      className="w-full bg-white border border-slate-300 rounded-lg px-2.5 py-1.5 text-xs font-medium focus:outline-none focus:ring-2 focus:ring-blue-500 text-slate-800"
                    />
                  </div>
                </div>

                {/* Editable Subjects Table */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-bold text-slate-700 text-xs uppercase tracking-wider">
                      Subject Marks ({editState.subjects?.length || 0})
                    </h4>
                    {computeCalculatedSgpa() !== null && (
                      <span className="text-[11px] text-slate-500 flex items-center gap-1">
                        <Calculator className="w-3 h-3 text-slate-400" />
                        Calculated SGPA: <strong className="text-slate-700">{computeCalculatedSgpa()}</strong>
                      </span>
                    )}
                  </div>
                  <div className="overflow-x-auto border border-slate-200 rounded-xl">
                    <table className="w-full text-left text-xs">
                      <thead className="bg-slate-50 text-slate-600 font-semibold border-b border-slate-200">
                        <tr>
                          <th className="py-2 px-3">Sub Code</th>
                          <th className="py-2 px-3">Subject Name</th>
                          <th className="py-2 px-2 text-center w-16">Total</th>
                          <th className="py-2 px-2 text-center w-16">Grade</th>
                          <th className="py-2 px-2 text-center w-16">Credits</th>
                          <th className="py-2 px-2 text-center w-16">Pass?</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100">
                        {editState.subjects?.map((sub, sIdx) => (
                          <tr key={sIdx} className="hover:bg-slate-50/50">
                            <td className="p-2">
                              <input
                                type="text"
                                value={sub.subject_code}
                                onChange={(e) => handleSubjectChange(sIdx, "subject_code", e.target.value)}
                                className="w-full font-mono bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none font-medium text-blue-700"
                              />
                            </td>
                            <td className="p-2">
                              <input
                                type="text"
                                value={sub.subject_name}
                                onChange={(e) => handleSubjectChange(sIdx, "subject_name", e.target.value)}
                                className="w-full bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none font-medium text-slate-800"
                              />
                            </td>
                            <td className="p-2 text-center">
                              <input
                                type="number"
                                value={sub.total_marks ?? ""}
                                onChange={(e) =>
                                  handleSubjectChange(
                                    sIdx,
                                    "total_marks",
                                    e.target.value ? parseFloat(e.target.value) : null
                                  )
                                }
                                className="w-14 text-center bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none"
                              />
                            </td>
                            <td className="p-2 text-center">
                              <input
                                type="text"
                                value={sub.grade ?? ""}
                                onChange={(e) => handleSubjectChange(sIdx, "grade", e.target.value.toUpperCase())}
                                className="w-12 text-center font-bold uppercase bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none text-slate-800"
                              />
                            </td>
                            <td className="p-2 text-center">
                              <input
                                type="number"
                                step="0.5"
                                value={sub.credits ?? ""}
                                onChange={(e) =>
                                  handleSubjectChange(
                                    sIdx,
                                    "credits",
                                    e.target.value ? parseFloat(e.target.value) : null
                                  )
                                }
                                className="w-12 text-center bg-transparent border-b border-transparent focus:border-blue-500 focus:outline-none"
                              />
                            </td>
                            <td className="p-2 text-center">
                              <input
                                type="checkbox"
                                checked={sub.is_pass}
                                onChange={(e) => handleSubjectChange(sIdx, "is_pass", e.target.checked)}
                                className="rounded text-blue-600 focus:ring-blue-500"
                              />
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-xl p-12 border border-slate-200 text-center text-slate-400 text-sm">
                Select a record from the queue to start verification and correction.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
