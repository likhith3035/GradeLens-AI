from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from ..database import get_db
from ..models import Student, College, SemesterResult, SubjectMark, AuditLog
from ..schemas import StudentResponse, StudentDetailResponse, StudentUpdate
from ..analytics.calculator import compute_cumulative_gpa

router = APIRouter(prefix="/api/students", tags=["Student Management"])

@router.get("", response_model=List[StudentResponse])
def get_students(
    search: Optional[str] = Query(None, description="Search by student name or roll number"),
    branch: Optional[str] = Query(None),
    batch: Optional[str] = Query(None),
    college_id: Optional[int] = Query(None),
    has_backlogs: Optional[bool] = Query(None),
    sort_by: str = Query("roll_number", pattern="^(roll_number|name|created_at|cgpa)$"),
    sort_order: str = Query("asc", pattern="^(asc|desc)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    query = db.query(Student)

    if search:
        s_term = f"%{search.strip()}%"
        query = query.filter(or_(Student.name.ilike(s_term), Student.roll_number.ilike(s_term)))

    if branch:
        query = query.filter(Student.branch == branch)

    if batch:
        query = query.filter(Student.batch == batch)

    if college_id:
        query = query.filter(Student.college_id == college_id)

    order_col = Student.roll_number
    if sort_by == "name":
        order_col = Student.name
    elif sort_by == "created_at":
        order_col = Student.created_at

    if sort_order == "desc":
        query = query.order_by(desc(order_col))
    else:
        query = query.order_by(asc(order_col))

    students = query.offset(skip).limit(limit).all()

    # Enrich students with aggregated statistics
    result = []
    for s in students:
        semesters = db.query(SemesterResult).filter(SemesterResult.student_id == s.id).all()
        sem_dicts = [{"sgpa": sem.sgpa, "total_credits": sem.total_credits} for sem in semesters]
        cgpa = compute_cumulative_gpa(sem_dicts)
        total_backlogs = sum(sem.backlog_count for sem in semesters)

        if has_backlogs is not None:
            if has_backlogs and total_backlogs == 0:
                continue
            if not has_backlogs and total_backlogs > 0:
                continue

        resp = StudentResponse.model_validate(s)
        resp.latest_cgpa = cgpa
        resp.total_backlogs = total_backlogs
        resp.semesters_count = len(semesters)
        result.append(resp)

    # Sort by calculated CGPA if requested
    if sort_by == "cgpa":
        result.sort(key=lambda x: (x.latest_cgpa or 0.0), reverse=(sort_order == "desc"))

    return result

@router.get("/{roll_number}", response_model=StudentDetailResponse)
def get_student_by_roll_number(roll_number: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.roll_number == roll_number).first()
    if not student:
        raise HTTPException(status_code=404, detail=f"Student with roll number '{roll_number}' not found.")

    semesters = db.query(SemesterResult).filter(SemesterResult.student_id == student.id).order_by(SemesterResult.semester).all()
    sem_dicts = [{"sgpa": sem.sgpa, "total_credits": sem.total_credits} for sem in semesters]
    cgpa = compute_cumulative_gpa(sem_dicts)
    total_backlogs = sum(sem.backlog_count for sem in semesters)

    resp = StudentDetailResponse.model_validate(student)
    resp.latest_cgpa = cgpa
    resp.total_backlogs = total_backlogs
    resp.semesters_count = len(semesters)
    return resp

@router.put("/{student_id}")
def update_student(student_id: int, update_data: StudentUpdate, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    changes = []
    if update_data.name and update_data.name != student.name:
        changes.append(("name", student.name, update_data.name))
        student.name = update_data.name

    if update_data.branch and update_data.branch != student.branch:
        changes.append(("branch", student.branch, update_data.branch))
        student.branch = update_data.branch

    if update_data.batch and update_data.batch != student.batch:
        changes.append(("batch", student.batch, update_data.batch))
        student.batch = update_data.batch

    if update_data.course and update_data.course != student.course:
        changes.append(("course", student.course, update_data.course))
        student.course = update_data.course

    # Record audit log
    for field, old_val, new_val in changes:
        log = AuditLog(
            entity_type="Student",
            entity_id=student.id,
            action="UPDATE",
            field_name=field,
            old_value=str(old_val),
            new_value=str(new_val),
            actor="User"
        )
        db.add(log)

    db.commit()
    db.refresh(student)
    return {"message": "Student updated successfully", "student_id": student.id}

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found.")

    roll = student.roll_number
    db.delete(student)
    
    # Audit log
    db.add(AuditLog(
        entity_type="Student",
        entity_id=student_id,
        action="DELETE",
        field_name="student",
        old_value=roll,
        actor="User"
    ))
    db.commit()

    return {"message": f"Student with roll number {roll} deleted successfully."}
