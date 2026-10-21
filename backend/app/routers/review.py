from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import SemesterResult, SubjectMark, Student, UploadedDocument, ExtractionIssue, AuditLog
from ..schemas import SemesterResultResponse, ManualCorrectionRequest
from ..analytics.calculator import compute_semester_summary, normalize_grade, GRADE_TO_POINTS

router = APIRouter(prefix="/api/review", tags=["Verification & Review"])

@router.get("/queue")
def get_review_queue(db: Session = Depends(get_db)):
    """Fetch all records that require verification or have open extraction issues."""
    results = (
        db.query(SemesterResult)
        .filter(SemesterResult.verification_status == "NEEDS_REVIEW")
        .order_by(SemesterResult.created_at.desc())
        .all()
    )

    items = []
    for r in results:
        student = db.query(Student).filter(Student.id == r.student_id).first()
        doc = db.query(UploadedDocument).filter(UploadedDocument.id == r.document_id).first()
        issues = db.query(ExtractionIssue).filter(ExtractionIssue.semester_result_id == r.id).all()

        items.append({
            "result_id": r.id,
            "roll_number": student.roll_number if student else "UNKNOWN",
            "student_name": student.name if student else "Unknown",
            "branch": student.branch if student else None,
            "semester": r.semester,
            "sgpa": r.sgpa,
            "source_filename": doc.filename if doc else None,
            "issues_count": len(issues),
            "issues": [
                {
                    "field": i.field_name,
                    "type": i.issue_type,
                    "severity": i.severity,
                    "message": i.message
                }
                for i in issues
            ],
            "created_at": r.created_at
        })

    return items


@router.get("/audit-logs")
def get_audit_logs(limit: int = 50, db: Session = Depends(get_db)):
    """Fetch recent audit and verification logs for History tab."""
    logs = db.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "entity_type": l.entity_type,
            "entity_id": l.entity_id,
            "action": l.action,
            "field_name": l.field_name,
            "old_value": l.old_value,
            "new_value": l.new_value,
            "actor": l.actor,
            "timestamp": l.timestamp.isoformat() if l.timestamp else None
        }
        for l in logs
    ]


@router.get("/{result_id}")
def get_review_detail(result_id: int, db: Session = Depends(get_db)):
    """Full detail of a single record for side-by-side verification and manual edit."""
    r = db.query(SemesterResult).filter(SemesterResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Semester result not found.")

    student = db.query(Student).filter(Student.id == r.student_id).first()
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == r.document_id).first()
    subjects = db.query(SubjectMark).filter(SubjectMark.semester_result_id == r.id).all()
    issues = db.query(ExtractionIssue).filter(ExtractionIssue.semester_result_id == r.id).all()

    return {
        "result_id": r.id,
        "document": {
            "id": doc.id if doc else None,
            "filename": doc.filename if doc else None,
            "file_size": doc.file_size if doc else 0,
            "ocr_used": doc.ocr_used if doc else False
        },
        "student": {
            "id": student.id if student else None,
            "roll_number": student.roll_number if student else "",
            "name": student.name if student else "",
            "branch": student.branch if student else "",
            "batch": student.batch if student else ""
        },
        "semester_info": {
            "semester": r.semester,
            "regulation": r.regulation,
            "examination_name": r.examination_name,
            "examination_month_year": r.examination_month_year,
            "sgpa": r.sgpa,
            "cgpa": r.cgpa,
            "total_credits": r.total_credits,
            "overall_result": r.overall_result,
            "verification_status": r.verification_status,
            "raw_text": r.raw_text
        },
        "subjects": [
            {
                "id": s.id,
                "subject_code": s.subject_code,
                "subject_name": s.subject_name,
                "internal_marks": s.internal_marks,
                "external_marks": s.external_marks,
                "practical_marks": s.practical_marks,
                "total_marks": s.total_marks,
                "max_marks": s.max_marks,
                "grade": s.grade,
                "grade_points": s.grade_points,
                "credits": s.credits,
                "subject_result": s.subject_result,
                "is_pass": s.is_pass,
                "provenance": s.provenance
            }
            for s in subjects
        ],
        "issues": [
            {
                "id": i.id,
                "field_name": i.field_name,
                "issue_type": i.issue_type,
                "severity": i.severity,
                "message": i.message,
                "is_resolved": i.is_resolved
            }
            for i in issues
        ]
    }

@router.post("/{result_id}/correct")
def submit_manual_correction(result_id: int, payload: ManualCorrectionRequest, db: Session = Depends(get_db)):
    """Applies human corrections to extracted fields, recalculates academics, and marks verified."""
    r = db.query(SemesterResult).filter(SemesterResult.id == result_id).first()
    if not r:
        raise HTTPException(status_code=404, detail="Semester result not found.")

    student = db.query(Student).filter(Student.id == r.student_id).first()

    # 1. Update Student fields if provided
    if student:
        if payload.student_name and payload.student_name != student.name:
            db.add(AuditLog(
                entity_type="Student", entity_id=student.id, action="UPDATE",
                field_name="name", old_value=student.name, new_value=payload.student_name, actor=payload.actor
            ))
            student.name = payload.student_name

        if payload.roll_number and payload.roll_number != student.roll_number:
            db.add(AuditLog(
                entity_type="Student", entity_id=student.id, action="UPDATE",
                field_name="roll_number", old_value=student.roll_number, new_value=payload.roll_number, actor=payload.actor
            ))
            student.roll_number = payload.roll_number

        if payload.branch and payload.branch != student.branch:
            student.branch = payload.branch

    # 2. Update Semester fields
    if payload.semester and payload.semester != r.semester:
        r.semester = payload.semester

    if payload.sgpa is not None:
        r.sgpa = payload.sgpa

    if payload.cgpa is not None:
        r.cgpa = payload.cgpa

    # 3. Update Subjects if provided
    if payload.subject_updates:
        for sub_patch in payload.subject_updates:
            sub_id = sub_patch.get("id")
            if not sub_id:
                continue
            sub = db.query(SubjectMark).filter(SubjectMark.id == sub_id, SubjectMark.semester_result_id == r.id).first()
            if sub:
                for k in ("subject_code", "subject_name", "internal_marks", "external_marks", "total_marks", "grade", "credits", "subject_result", "is_pass"):
                    if k in sub_patch and sub_patch[k] is not None:
                        old_v = getattr(sub, k)
                        new_v = sub_patch[k]
                        if str(old_v) != str(new_v):
                            db.add(AuditLog(
                                entity_type="SubjectMark", entity_id=sub.id, action="UPDATE",
                                field_name=k, old_value=str(old_v), new_value=str(new_v), actor=payload.actor
                            ))
                            setattr(sub, k, new_v)
                sub.provenance = "MANUAL"

    # Recalculate summary from active subjects
    all_subs = db.query(SubjectMark).filter(SubjectMark.semester_result_id == r.id).all()
    sub_dicts = [
        {
            "credits": s.credits,
            "grade_points": s.grade_points or GRADE_TO_POINTS.get(normalize_grade(s.grade) or ""),
            "grade": s.grade,
            "subject_result": s.subject_result,
            "total_marks": s.total_marks,
            "max_marks": s.max_marks
        }
        for s in all_subs
    ]
    summary = compute_semester_summary(sub_dicts, extracted_sgpa=r.sgpa)
    r.subjects_count = summary["total_subjects"]
    r.passed_count = summary["subjects_passed"]
    r.failed_count = summary["subjects_failed"]
    r.backlog_count = summary["backlog_count"]
    r.total_credits = summary["total_credits"]
    r.overall_result = summary["overall_result"]

    # Mark issues as resolved
    db.query(ExtractionIssue).filter(ExtractionIssue.semester_result_id == r.id).update({"is_resolved": True})

    # Update verification status
    r.verification_status = payload.verification_status
    db.commit()

    return {"message": "Record successfully verified and updated.", "result_id": r.id}


@router.post("/resolve-all")
def resolve_all_records(actor: str = "Academic Reviewer", db: Session = Depends(get_db)):
    """Automatically resolves calculation discrepancies, accepts calculated SGPA, and verifies all pending queue items."""
    results = (
        db.query(SemesterResult)
        .filter(SemesterResult.verification_status == "NEEDS_REVIEW")
        .all()
    )

    resolved_count = 0
    for r in results:
        all_subs = db.query(SubjectMark).filter(SubjectMark.semester_result_id == r.id).all()
        if all_subs:
            sub_dicts = [
                {
                    "credits": s.credits,
                    "grade_points": s.grade_points or GRADE_TO_POINTS.get(normalize_grade(s.grade) or ""),
                    "grade": s.grade,
                    "subject_result": s.subject_result,
                    "total_marks": s.total_marks,
                    "max_marks": s.max_marks
                }
                for s in all_subs
            ]
            summary = compute_semester_summary(sub_dicts, extracted_sgpa=r.sgpa)
            r.subjects_count = summary["total_subjects"]
            r.passed_count = summary["subjects_passed"]
            r.failed_count = summary["subjects_failed"]
            r.backlog_count = summary["backlog_count"]
            r.total_credits = summary["total_credits"]
            r.overall_result = summary["overall_result"]
            if summary.get("calculated_sgpa") is not None:
                r.sgpa = summary["calculated_sgpa"]

        student = db.query(Student).filter(Student.id == r.student_id).first()
        if student and (not student.name or student.name.upper() in ("UNKNOWN", "UNKNOWN STUDENT")):
            student.name = f"STUDENT ({student.roll_number})"

        db.query(ExtractionIssue).filter(ExtractionIssue.semester_result_id == r.id).update({"is_resolved": True})
        r.verification_status = "VERIFIED"
        db.add(AuditLog(
            entity_type="SemesterResult",
            entity_id=r.id,
            action="BATCH_VERIFY",
            field_name="verification_status",
            old_value="NEEDS_REVIEW",
            new_value="VERIFIED",
            actor=actor
        ))
        resolved_count += 1

    db.commit()
    return {"message": f"Successfully verified and resolved all {resolved_count} flagged records.", "resolved_count": resolved_count}

