from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

# --- Subject Mark Schemas ---
class SubjectMarkBase(BaseModel):
    subject_code: str
    subject_name: str
    internal_marks: Optional[float] = None
    external_marks: Optional[float] = None
    practical_marks: Optional[float] = None
    total_marks: Optional[float] = None
    max_marks: Optional[float] = None
    grade: Optional[str] = None
    grade_points: Optional[float] = None
    credits: Optional[float] = None
    subject_result: Optional[str] = None
    is_pass: bool = True
    confidence: float = 1.0
    provenance: str = "EXTRACTED"

class SubjectMarkCreate(SubjectMarkBase):
    pass

class SubjectMarkUpdate(BaseModel):
    subject_code: Optional[str] = None
    subject_name: Optional[str] = None
    internal_marks: Optional[float] = None
    external_marks: Optional[float] = None
    practical_marks: Optional[float] = None
    total_marks: Optional[float] = None
    max_marks: Optional[float] = None
    grade: Optional[str] = None
    grade_points: Optional[float] = None
    credits: Optional[float] = None
    subject_result: Optional[str] = None
    is_pass: Optional[bool] = None

class SubjectMarkResponse(SubjectMarkBase):
    id: int
    semester_result_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Extraction Issues ---
class ExtractionIssueResponse(BaseModel):
    id: int
    field_name: Optional[str] = None
    issue_type: str
    severity: str
    message: str
    is_resolved: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Semester Result Schemas ---
class SemesterResultBase(BaseModel):
    semester: str
    regulation: Optional[str] = None
    examination_name: Optional[str] = None
    examination_month_year: Optional[str] = None
    date_of_issue: Optional[str] = None
    sgpa: Optional[float] = None
    cgpa: Optional[float] = None
    total_credits: Optional[float] = None
    subjects_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    backlog_count: int = 0
    overall_result: Optional[str] = None
    percentage: Optional[float] = None
    verification_status: str = "PENDING"
    extraction_profile: str = "general"

class SemesterResultUpdate(BaseModel):
    semester: Optional[str] = None
    regulation: Optional[str] = None
    examination_name: Optional[str] = None
    examination_month_year: Optional[str] = None
    sgpa: Optional[float] = None
    cgpa: Optional[float] = None
    total_credits: Optional[float] = None
    overall_result: Optional[str] = None
    verification_status: Optional[str] = None

class SemesterResultResponse(SemesterResultBase):
    id: int
    student_id: Optional[int] = None
    document_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    subject_marks: List[SubjectMarkResponse] = []
    issues: List[ExtractionIssueResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- College Schemas ---
class CollegeResponse(BaseModel):
    id: int
    name: str
    code: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


# --- Student Schemas ---
class StudentBase(BaseModel):
    roll_number: str
    name: str
    course: Optional[str] = None
    branch: Optional[str] = None
    batch: Optional[str] = None

class StudentCreate(StudentBase):
    college_name: Optional[str] = None
    college_code: Optional[str] = None

class StudentUpdate(BaseModel):
    name: Optional[str] = None
    course: Optional[str] = None
    branch: Optional[str] = None
    batch: Optional[str] = None
    college_name: Optional[str] = None

class StudentResponse(StudentBase):
    id: int
    college_id: Optional[int] = None
    college: Optional[CollegeResponse] = None
    created_at: datetime
    updated_at: datetime
    latest_cgpa: Optional[float] = None
    total_backlogs: int = 0
    semesters_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class StudentDetailResponse(StudentResponse):
    semester_results: List[SemesterResultResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Document & Batch Schemas ---
class UploadedDocumentResponse(BaseModel):
    id: int
    batch_id: Optional[str] = None
    filename: str
    file_size: int
    mime_type: str
    status: str
    error_message: Optional[str] = None
    ocr_used: bool = False
    processing_time_ms: int = 0
    created_at: datetime
    issues_count: int = 0

    model_config = ConfigDict(from_attributes=True)

class ProcessingBatchResponse(BaseModel):
    id: str
    mode: str
    total_files: int
    processed_files: int
    failed_files: int
    needs_review_files: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    documents: List[UploadedDocumentResponse] = []

    model_config = ConfigDict(from_attributes=True)


# --- Analytics Schemas ---
class AnalyticsOverviewResponse(BaseModel):
    total_students: int
    total_memos_processed: int
    total_subject_records: int
    records_requiring_verification: int
    total_passed_records: int
    total_failed_records: int
    overall_pass_rate: float
    students_with_backlogs: int
    average_cgpa: Optional[float] = None
    processing_success_rate: float

class BranchPerformance(BaseModel):
    branch: str
    student_count: int
    pass_rate: float
    avg_cgpa: Optional[float] = None

class SemesterPerformance(BaseModel):
    semester: str
    total_students: int
    passed_students: int
    pass_percentage: float
    avg_sgpa: Optional[float] = None

class GradeCount(BaseModel):
    grade: str
    count: int

class TopStudent(BaseModel):
    roll_number: str
    name: str
    branch: Optional[str] = None
    cgpa: Optional[float] = None
    backlogs: int = 0

class AnalyticsFullResponse(BaseModel):
    overview: AnalyticsOverviewResponse
    branch_performance: List[BranchPerformance]
    semester_performance: List[SemesterPerformance]
    grade_distribution: List[GradeCount]
    top_students: List[TopStudent]


# --- Review & Verification ---
class ManualCorrectionRequest(BaseModel):
    student_name: Optional[str] = None
    roll_number: Optional[str] = None
    branch: Optional[str] = None
    semester: Optional[str] = None
    sgpa: Optional[float] = None
    cgpa: Optional[float] = None
    subject_updates: Optional[List[Dict[str, Any]]] = None
    verification_status: str = "VERIFIED"
    actor: str = "User"


# --- Excel Export Filter Request ---
class ExcelExportFilter(BaseModel):
    college_id: Optional[int] = None
    branch: Optional[str] = None
    batch: Optional[str] = None
    semester: Optional[str] = None
    examination: Optional[str] = None
    selected_roll_numbers: Optional[List[str]] = None
    verified_only: bool = False
