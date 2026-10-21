export interface SubjectMark {
  id?: number;
  subject_code: string;
  subject_name: string;
  internal_marks: number | null;
  external_marks: number | null;
  practical_marks: number | null;
  total_marks: number | null;
  max_marks: number | null;
  grade: string | null;
  grade_points: number | null;
  credits: number | null;
  subject_result: string | null;
  is_pass: boolean;
  confidence?: number;
  provenance?: string;
}

export interface ExtractionIssue {
  id?: number;
  field_name?: string | null;
  issue_type: string;
  severity: "WARNING" | "ERROR" | "INFO";
  message: string;
  is_resolved: boolean;
}

export interface SemesterResult {
  id?: number;
  student_id?: number;
  document_id?: number;
  semester: string;
  regulation?: string | null;
  examination_name?: string | null;
  examination_month_year?: string | null;
  date_of_issue?: string | null;
  sgpa: number | null;
  cgpa: number | null;
  total_credits: number | null;
  subjects_count: number;
  passed_count: number;
  failed_count: number;
  backlog_count: number;
  overall_result: string | null;
  verification_status: "VERIFIED" | "NEEDS_REVIEW" | "PENDING";
  raw_text?: string | null;
  source_filename?: string;
  subject_marks: SubjectMark[];
  issues: ExtractionIssue[];
  created_at?: string;
}

export interface Student {
  id: number;
  roll_number: string;
  name: string;
  college_name?: string | null;
  college_id?: number | null;
  course?: string | null;
  branch?: string | null;
  batch?: string | null;
  latest_cgpa?: number | null;
  total_backlogs: number;
  semesters_count: number;
  created_at: string;
  semester_results?: SemesterResult[];
}

export interface UploadItem {
  id: string;
  file: File;
  name: string;
  size: number;
  status: "pending" | "uploading" | "processing" | "completed" | "needs_review" | "failed";
  progress: number;
  error?: string;
  result?: Record<string, unknown>;
}

export interface AnalyticsOverview {
  total_students: number;
  total_memos_processed: number;
  total_subject_records: number;
  records_requiring_verification: number;
  total_passed_records: number;
  total_failed_records: number;
  overall_pass_rate: number;
  students_with_backlogs: number;
  average_cgpa: number | null;
  processing_success_rate: number;
}

export interface BranchPerformance {
  branch: string;
  student_count: number;
  pass_rate: number;
  avg_cgpa: number | null;
}

export interface SemesterPerformance {
  semester: string;
  total_students: number;
  passed_students: number;
  pass_percentage: number;
  avg_sgpa: number | null;
}

export interface GradeDistribution {
  grade: string;
  count: number;
}

export interface TopStudent {
  roll_number: string;
  name: string;
  branch?: string | null;
  cgpa?: number | null;
  backlogs: number;
}

export interface AnalyticsFull {
  overview: AnalyticsOverview;
  branch_performance: BranchPerformance[];
  semester_performance: SemesterPerformance[];
  grade_distribution: GradeDistribution[];
  top_students: TopStudent[];
}

export interface SystemHealth {
  status: string;
  app_name: string;
  version: string;
  mode: "local" | "online";
  database_connected: boolean;
  tesseract_ocr_available: boolean;
  tesseract_path: string;
  registered_parsers: { name: string; description: string }[];
}

export interface AppSettings {
  mode: "local" | "online";
  app_name: string;
  app_version: string;
  tesseract_cmd: string;
  tesseract_available: boolean;
  max_file_size_mb: number;
  max_batch_size: number;
  database_url: string;
}

export interface ReviewQueueIssue {
  field: string | null;
  type: string;
  severity: "WARNING" | "ERROR" | "INFO";
  message: string;
}

export interface ReviewQueueItem {
  result_id: number;
  roll_number: string;
  student_name: string;
  branch: string | null;
  semester: string;
  sgpa: number | null;
  source_filename: string | null;
  issues_count: number;
  issues: ReviewQueueIssue[];
  created_at: string;
}

export interface ReviewDetail {
  result_id: number;
  document: {
    id: number | null;
    filename: string | null;
    file_size: number;
    ocr_used: boolean;
  };
  student: {
    id: number | null;
    roll_number: string;
    name: string;
    branch: string;
    batch: string;
  };
  semester_info: {
    semester: string;
    regulation: string | null;
    examination_name: string | null;
    examination_month_year: string | null;
    sgpa: number | null;
    cgpa: number | null;
    total_credits: number | null;
    overall_result: string | null;
    verification_status: "VERIFIED" | "NEEDS_REVIEW" | "PENDING";
    raw_text: string | null;
  };
  subjects: SubjectMark[];
  issues: ExtractionIssue[];
}

export interface AuditLogItem {
  id: number;
  entity_type: string;
  entity_id: number;
  action: string;
  field_name: string | null;
  old_value: string | null;
  new_value: string | null;
  actor: string;
  timestamp: string | null;
}

export interface BatchResolveResponse {
  message: string;
  resolved_count: number;
}
