import { SystemHealth, AppSettings, AnalyticsFull, Student, SemesterResult } from "./types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export async function fetchHealth(): Promise<SystemHealth> {
  const res = await fetch(`${API_BASE}/api/health`, { cache: "no-store" });
  if (!res.ok) throw new Error("Health check failed");
  return res.json();
}

export async function fetchSettings(): Promise<AppSettings> {
  const res = await fetch(`${API_BASE}/api/settings`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load settings");
  return res.json();
}

export async function updateMode(mode: "local" | "online"): Promise<any> {
  const res = await fetch(`${API_BASE}/api/settings/mode`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ mode }),
  });
  if (!res.ok) throw new Error("Failed to update mode");
  return res.json();
}

export async function updateTesseractPath(path: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/settings/tesseract-path`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to update path" }));
    throw new Error(err.detail || "Failed to update path");
  }
  return res.json();
}

export async function purgeData(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/settings/purge-data`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ confirm: true }),
  });
  if (!res.ok) throw new Error("Failed to purge data");
  return res.json();
}

export async function uploadFiles(files: File[], profile: string = "auto"): Promise<any> {
  const formData = new FormData();
  files.forEach((f) => formData.append("files", f));
  formData.append("profile", profile);

  const res = await fetch(`${API_BASE}/api/upload`, {
    method: "POST",
    body: formData,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || "Upload failed");
  }
  return res.json();
}

export async function loadSamplePack(): Promise<any> {
  const res = await fetch(`${API_BASE}/api/upload/load-sample-batch`, {
    method: "POST",
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Failed to load sample pack" }));
    throw new Error(err.detail || "Failed to load sample pack");
  }
  return res.json();
}

export function getDocumentFileUrl(docId: number, download: boolean = false): string {
  const url = `${API_BASE}/api/upload/document/${docId}/file`;
  return download ? `${url}?download=true` : url;
}

export async function fetchAnalytics(): Promise<AnalyticsFull> {
  const res = await fetch(`${API_BASE}/api/analytics`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch analytics");
  return res.json();
}

export async function fetchStudents(params: {
  search?: string;
  branch?: string;
  batch?: string;
  has_backlogs?: boolean;
  sort_by?: string;
  sort_order?: string;
  limit?: number;
  skip?: number;
} = {}): Promise<Student[]> {
  const url = new URL(`${API_BASE}/api/students`);
  if (params.search) url.searchParams.set("search", params.search);
  if (params.branch) url.searchParams.set("branch", params.branch);
  if (params.batch) url.searchParams.set("batch", params.batch);
  if (params.has_backlogs !== undefined) url.searchParams.set("has_backlogs", String(params.has_backlogs));
  if (params.sort_by) url.searchParams.set("sort_by", params.sort_by);
  if (params.sort_order) url.searchParams.set("sort_order", params.sort_order);
  if (params.limit) url.searchParams.set("limit", String(params.limit));
  if (params.skip) url.searchParams.set("skip", String(params.skip));

  const res = await fetch(url.toString(), { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch students");
  return res.json();
}

export async function fetchStudentDetail(rollNumber: string): Promise<Student> {
  const res = await fetch(`${API_BASE}/api/students/${encodeURIComponent(rollNumber)}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Student not found");
  return res.json();
}

export async function fetchReviewQueue(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/review/queue`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to fetch review queue");
  return res.json();
}

export async function fetchReviewDetail(resultId: number): Promise<any> {
  const res = await fetch(`${API_BASE}/api/review/${resultId}`, { cache: "no-store" });
  if (!res.ok) throw new Error("Failed to load review details");
  return res.json();
}

export async function submitCorrection(resultId: number, data: any): Promise<any> {
  const res = await fetch(`${API_BASE}/api/review/${resultId}/correct`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
  if (!res.ok) throw new Error("Failed to save correction");
  return res.json();
}

export function getExcelExportUrl(params: {
  branch?: string;
  batch?: string;
  semester?: string;
  verified_only?: boolean;
  roll_numbers?: string;
} = {}): string {
  const url = new URL(`${API_BASE}/api/export/excel`);
  if (params.branch) url.searchParams.set("branch", params.branch);
  if (params.batch) url.searchParams.set("batch", params.batch);
  if (params.semester) url.searchParams.set("semester", params.semester);
  if (params.verified_only) url.searchParams.set("verified_only", "true");
  if (params.roll_numbers) url.searchParams.set("roll_numbers", params.roll_numbers);
  return url.toString();
}

export async function fetchRecentDocuments(limit: number = 10): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/api/upload/recent?limit=${limit}`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch (err) {
    console.error("fetchRecentDocuments error:", err);
    return [];
  }
}

export async function fetchAuditLogs(limit: number = 50): Promise<any[]> {
  try {
    const res = await fetch(`${API_BASE}/api/review/audit-logs?limit=${limit}`, { cache: "no-store" });
    if (!res.ok) return [];
    return res.json();
  } catch (err) {
    console.error("fetchAuditLogs error:", err);
    return [];
  }
}

