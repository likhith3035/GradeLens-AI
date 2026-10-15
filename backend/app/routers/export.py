import io
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ..database import get_db
from ..models import Student, College, SemesterResult, SubjectMark, UploadedDocument, ExtractionIssue
from ..export.excel_generator import excel_generator
from ..analytics.calculator import compute_cumulative_gpa

router = APIRouter(prefix="/api/export", tags=["Excel Export Engine"])

@router.get("/excel")
def export_academic_excel(
    branch: Optional[str] = Query(None),
    batch: Optional[str] = Query(None),
    semester: Optional[str] = Query(None),
    verified_only: bool = Query(False),
    roll_numbers: Optional[str] = Query(None, description="Comma-separated list of roll numbers"),
    db: Session = Depends(get_db)
):
    query = db.query(Student)

    if branch:
        query = query.filter(Student.branch == branch)
    if batch:
        query = query.filter(Student.batch == batch)
    if roll_numbers:
        r_list = [r.strip() for r in roll_numbers.split(",") if r.strip()]
        query = query.filter(Student.roll_number.in_(r_list))

    students = query.all()
    student_records = []

    for s in students:
        college = db.query(College).filter(College.id == s.college_id).first() if s.college_id else None
        sem_query = db.query(SemesterResult).filter(SemesterResult.student_id == s.id)
        if semester:
            sem_query = sem_query.filter(SemesterResult.semester == semester)
        if verified_only:
            sem_query = sem_query.filter(SemesterResult.verification_status == "VERIFIED")

        semesters = sem_query.order_by(SemesterResult.semester).all()
        if not semesters and (semester or verified_only):
            continue

        sem_list = []
        for sem in semesters:
            doc = db.query(UploadedDocument).filter(UploadedDocument.id == sem.document_id).first() if sem.document_id else None
            subs = db.query(SubjectMark).filter(SubjectMark.semester_result_id == sem.id).all()
            issues = db.query(ExtractionIssue).filter(ExtractionIssue.semester_result_id == sem.id).all()

            sem_list.append({
                "semester": sem.semester,
                "regulation": sem.regulation,
                "examination_name": sem.examination_name,
                "examination_month_year": sem.examination_month_year,
                "sgpa": sem.sgpa,
                "cgpa": sem.cgpa,
                "backlog_count": sem.backlog_count,
                "overall_result": sem.overall_result,
                "verification_status": sem.verification_status,
                "source_filename": doc.filename if doc else "N/A",
                "subject_marks": [
                    {
                        "subject_code": sm.subject_code,
                        "subject_name": sm.subject_name,
                        "internal_marks": sm.internal_marks,
                        "external_marks": sm.external_marks,
                        "practical_marks": sm.practical_marks,
                        "total_marks": sm.total_marks,
                        "max_marks": sm.max_marks,
                        "grade": sm.grade,
                        "grade_points": sm.grade_points,
                        "credits": sm.credits,
                        "subject_result": sm.subject_result,
                        "is_pass": sm.is_pass
                    }
                    for sm in subs
                ],
                "issues": [
                    {
                        "field_name": iss.field_name,
                        "issue_type": iss.issue_type,
                        "severity": iss.severity,
                        "message": iss.message,
                        "is_resolved": iss.is_resolved
                    }
                    for iss in issues
                ]
            })

        sem_dicts = [{"sgpa": sm.sgpa, "total_credits": sm.total_credits} for sm in semesters]
        cgpa = compute_cumulative_gpa(sem_dicts)

        student_records.append({
            "name": s.name,
            "roll_number": s.roll_number,
            "college_name": college.name if college else "Autonomous Institution",
            "course": s.course or "B.Tech",
            "branch": s.branch or "General",
            "batch": s.batch or "2020-2024",
            "latest_cgpa": cgpa,
            "semester_results": sem_list
        })

    excel_bytes = excel_generator.generate_workbook(student_records)
    
    filename = f"memoscan_report_{branch or 'all'}_{datetime_str()}.xlsx"
    return StreamingResponse(
        io.BytesIO(excel_bytes),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )

def datetime_str():
    from datetime import datetime
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")
