from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, Text, DateTime, ForeignKey, Index
)
from sqlalchemy.orm import relationship
from .database import Base

class College(Base):
    __tablename__ = "colleges"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    code = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    students = relationship("Student", back_populates="college")


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    roll_number = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(255), nullable=False, index=True)
    college_id = Column(Integer, ForeignKey("colleges.id"), nullable=True)
    course = Column(String(100), nullable=True)
    branch = Column(String(150), nullable=True, index=True)
    batch = Column(String(50), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    college = relationship("College", back_populates="students")
    semester_results = relationship("SemesterResult", back_populates="student", cascade="all, delete-orphan")


class ProcessingBatch(Base):
    __tablename__ = "processing_batches"

    id = Column(String(100), primary_key=True, index=True)
    mode = Column(String(20), default="local")
    total_files = Column(Integer, default=0)
    processed_files = Column(Integer, default=0)
    failed_files = Column(Integer, default=0)
    needs_review_files = Column(Integer, default=0)
    status = Column(String(30), default="PENDING")  # PENDING, PROCESSING, COMPLETED, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    documents = relationship("UploadedDocument", back_populates="batch", cascade="all, delete-orphan")


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String(100), ForeignKey("processing_batches.id"), nullable=True)
    filename = Column(String(255), nullable=False)
    file_size = Column(Integer, default=0)
    mime_type = Column(String(100), nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(String(30), default="PENDING")  # PENDING, PROCESSING, COMPLETED, NEEDS_REVIEW, FAILED
    error_message = Column(Text, nullable=True)
    ocr_used = Column(Boolean, default=False)
    processing_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

    batch = relationship("ProcessingBatch", back_populates="documents")
    semester_results = relationship("SemesterResult", back_populates="document", cascade="all, delete-orphan")
    issues = relationship("ExtractionIssue", back_populates="document", cascade="all, delete-orphan")


class SemesterResult(Base):
    __tablename__ = "semester_results"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id"), nullable=True)
    
    semester = Column(String(50), nullable=False, index=True)
    regulation = Column(String(50), nullable=True)
    examination_name = Column(String(255), nullable=True)
    examination_month_year = Column(String(100), nullable=True)
    date_of_issue = Column(String(50), nullable=True)
    
    sgpa = Column(Float, nullable=True)
    cgpa = Column(Float, nullable=True)
    total_credits = Column(Float, nullable=True)
    
    subjects_count = Column(Integer, default=0)
    passed_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    backlog_count = Column(Integer, default=0)
    overall_result = Column(String(50), nullable=True)  # PASSED, FAILED, PROMOTED
    percentage = Column(Float, nullable=True)
    
    verification_status = Column(String(30), default="PENDING")  # VERIFIED, NEEDS_REVIEW, PENDING
    raw_text = Column(Text, nullable=True)
    extraction_profile = Column(String(50), default="general")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    student = relationship("Student", back_populates="semester_results")
    document = relationship("UploadedDocument", back_populates="semester_results")
    subject_marks = relationship("SubjectMark", back_populates="semester_result", cascade="all, delete-orphan")
    issues = relationship("ExtractionIssue", back_populates="semester_result", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_student_semester", "student_id", "semester"),
    )


class SubjectMark(Base):
    __tablename__ = "subject_marks"

    id = Column(Integer, primary_key=True, index=True)
    semester_result_id = Column(Integer, ForeignKey("semester_results.id"), nullable=False)
    
    subject_code = Column(String(50), nullable=False, index=True)
    subject_name = Column(String(255), nullable=False)
    
    internal_marks = Column(Float, nullable=True)
    external_marks = Column(Float, nullable=True)
    practical_marks = Column(Float, nullable=True)
    total_marks = Column(Float, nullable=True)
    max_marks = Column(Float, nullable=True)
    
    grade = Column(String(20), nullable=True)
    grade_points = Column(Float, nullable=True)
    credits = Column(Float, nullable=True)
    
    subject_result = Column(String(20), nullable=True)  # P, F, AB, PASSED, FAILED
    is_pass = Column(Boolean, default=True)
    confidence = Column(Float, default=1.0)
    provenance = Column(String(30), default="EXTRACTED")  # EXTRACTED, CALCULATED, MANUAL, UNAVAILABLE
    created_at = Column(DateTime, default=datetime.utcnow)

    semester_result = relationship("SemesterResult", back_populates="subject_marks")


class ExtractionIssue(Base):
    __tablename__ = "extraction_issues"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("uploaded_documents.id"), nullable=True)
    semester_result_id = Column(Integer, ForeignKey("semester_results.id"), nullable=True)
    
    field_name = Column(String(100), nullable=True)
    issue_type = Column(String(100), nullable=False)  # LOW_CONFIDENCE, MISSING_FIELD, CALCULATION_MISMATCH, etc.
    severity = Column(String(20), default="WARNING")  # WARNING, ERROR, INFO
    message = Column(Text, nullable=False)
    is_resolved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    document = relationship("UploadedDocument", back_populates="issues")
    semester_result = relationship("SemesterResult", back_populates="issues")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False)  # Student, SemesterResult, SubjectMark
    entity_id = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)  # CREATE, UPDATE, DELETE, VERIFY
    field_name = Column(String(100), nullable=True)
    old_value = Column(Text, nullable=True)
    new_value = Column(Text, nullable=True)
    actor = Column(String(100), default="User")
    timestamp = Column(DateTime, default=datetime.utcnow)
