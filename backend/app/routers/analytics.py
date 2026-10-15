from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Student, SemesterResult, SubjectMark, UploadedDocument, ExtractionIssue
from ..schemas import AnalyticsFullResponse, AnalyticsOverviewResponse, BranchPerformance, SemesterPerformance, GradeCount, TopStudent
from ..analytics.calculator import compute_cumulative_gpa

router = APIRouter(prefix="/api/analytics", tags=["Academic Analytics"])

@router.get("", response_model=AnalyticsFullResponse)
def get_analytics(db: Session = Depends(get_db)):
    # 1. Totals
    total_students = db.query(func.count(Student.id)).scalar() or 0
    total_memos = db.query(func.count(SemesterResult.id)).scalar() or 0
    total_subjects = db.query(func.count(SubjectMark.id)).scalar() or 0
    needs_review = db.query(func.count(SemesterResult.id)).filter(SemesterResult.verification_status == "NEEDS_REVIEW").scalar() or 0

    # Pass / Fail counts from subject marks
    passed_marks_count = db.query(func.count(SubjectMark.id)).filter(SubjectMark.is_pass == True).scalar() or 0
    failed_marks_count = db.query(func.count(SubjectMark.id)).filter(SubjectMark.is_pass == False).scalar() or 0
    pass_rate = round((passed_marks_count / total_subjects * 100), 2) if total_subjects > 0 else 0.0

    # Total uploaded docs & processing success rate
    total_docs = db.query(func.count(UploadedDocument.id)).scalar() or 0
    failed_docs = db.query(func.count(UploadedDocument.id)).filter(UploadedDocument.status == "FAILED").scalar() or 0
    success_rate = round(((total_docs - failed_docs) / total_docs * 100), 1) if total_docs > 0 else 100.0

    # Students with backlogs & CGPA calculation
    all_students = db.query(Student).all()
    students_with_backlogs = 0
    cgpa_list = []
    student_perf_list = []

    for s in all_students:
        semesters = db.query(SemesterResult).filter(SemesterResult.student_id == s.id).all()
        backlogs = sum(sem.backlog_count for sem in semesters)
        if backlogs > 0:
            students_with_backlogs += 1

        sem_dicts = [{"sgpa": sem.sgpa, "total_credits": sem.total_credits} for sem in semesters]
        cgpa = compute_cumulative_gpa(sem_dicts)
        if cgpa is not None:
            cgpa_list.append(cgpa)

        student_perf_list.append({
            "roll_number": s.roll_number,
            "name": s.name,
            "branch": s.branch,
            "cgpa": cgpa,
            "backlogs": backlogs
        })

    avg_cgpa = round(sum(cgpa_list) / len(cgpa_list), 2) if cgpa_list else None

    # 2. Branch Performance
    branches = db.query(Student.branch).distinct().all()
    branch_performance = []
    for (b_name,) in branches:
        if not b_name:
            continue
        b_studs = [st for st in student_perf_list if st["branch"] == b_name]
        b_cgpas = [st["cgpa"] for st in b_studs if st["cgpa"] is not None]
        b_pass_studs = sum(1 for st in b_studs if st["backlogs"] == 0)
        b_pass_rate = round((b_pass_studs / len(b_studs) * 100), 1) if b_studs else 0.0
        b_avg_cgpa = round(sum(b_cgpas) / len(b_cgpas), 2) if b_cgpas else None

        branch_performance.append(BranchPerformance(
            branch=b_name,
            student_count=len(b_studs),
            pass_rate=b_pass_rate,
            avg_cgpa=b_avg_cgpa
        ))

    # 3. Semester Performance
    sem_rows = db.query(SemesterResult.semester).distinct().all()
    semester_performance = []
    for (sem_name,) in sem_rows:
        if not sem_name:
            continue
        sems = db.query(SemesterResult).filter(SemesterResult.semester == sem_name).all()
        t_count = len(sems)
        p_count = sum(1 for sm in sems if sm.backlog_count == 0)
        pct = round((p_count / t_count * 100), 1) if t_count > 0 else 0.0
        sgpas = [sm.sgpa for sm in sems if sm.sgpa is not None]
        avg_sgpa = round(sum(sgpas) / len(sgpas), 2) if sgpas else None

        semester_performance.append(SemesterPerformance(
            semester=sem_name,
            total_students=t_count,
            passed_students=p_count,
            pass_percentage=pct,
            avg_sgpa=avg_sgpa
        ))

    # 4. Grade Distribution
    grade_counts = (
        db.query(SubjectMark.grade, func.count(SubjectMark.id))
        .filter(SubjectMark.grade.isnot(None))
        .group_by(SubjectMark.grade)
        .all()
    )
    grade_distribution = [
        GradeCount(grade=g, count=cnt)
        for g, cnt in grade_counts if g and g.strip()
    ]
    # Sort grades nicely: O, A+, A, B+, B, C, D, P, F, AB
    grade_order = {"O": 1, "A+": 2, "A": 3, "B+": 4, "B": 5, "C": 6, "D": 7, "P": 8, "F": 9, "AB": 10}
    grade_distribution.sort(key=lambda x: grade_order.get(x.grade.upper(), 99))

    # 5. Top Students
    top_candidates = [st for st in student_perf_list if st["cgpa"] is not None]
    top_candidates.sort(key=lambda x: (x["cgpa"], -x["backlogs"]), reverse=True)
    top_students = [
        TopStudent(
            roll_number=st["roll_number"],
            name=st["name"],
            branch=st["branch"],
            cgpa=st["cgpa"],
            backlogs=st["backlogs"]
        )
        for st in top_candidates[:10]
    ]

    overview = AnalyticsOverviewResponse(
        total_students=total_students,
        total_memos_processed=total_memos,
        total_subject_records=total_subjects,
        records_requiring_verification=needs_review,
        total_passed_records=passed_marks_count,
        total_failed_records=failed_marks_count,
        overall_pass_rate=pass_rate,
        students_with_backlogs=students_with_backlogs,
        average_cgpa=avg_cgpa,
        processing_success_rate=success_rate
    )

    return AnalyticsFullResponse(
        overview=overview,
        branch_performance=branch_performance,
        semester_performance=semester_performance,
        grade_distribution=grade_distribution,
        top_students=top_students
    )
