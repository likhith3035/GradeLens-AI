import os
import io
import time
import uuid
import zipfile
from pathlib import Path
from typing import List, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from ..database import get_db
from ..config import settings
from ..models import ProcessingBatch, UploadedDocument, Student, College, SemesterResult, SubjectMark, ExtractionIssue, AuditLog
from ..utils.security import sanitize_filename, validate_uploaded_file
from ..extractor.engine import extraction_engine
from ..analytics.calculator import compute_cumulative_gpa

router = APIRouter(prefix="/api/upload", tags=["Upload & Processing"])

def _save_single_memo_result(db: Session, doc: UploadedDocument, result: dict) -> dict:
    """Helper to persist an extracted marks memo record into database models."""
    stud_data = result["student"]
    sem_data = result["semester_info"]
    subjects = result["subjects"]
    issues = result["issues"]
    ver_status = result["verification_status"]

    # 1. College
    college_id = None
    if stud_data.get("college_name"):
        col = db.query(College).filter(College.name == stud_data["college_name"]).first()
        if not col:
            col = College(name=stud_data["college_name"])
            db.add(col)
            db.commit()
            db.refresh(col)
        college_id = col.id

    # 2. Student (search by roll number)
    roll_no = stud_data.get("roll_number") or f"UNKNOWN_{doc.id}_{uuid.uuid4().hex[:6]}"
    student = db.query(Student).filter(Student.roll_number == roll_no).first()
    if not student:
        student = Student(
            roll_number=roll_no,
            name=stud_data.get("name") or "Unknown Student",
            college_id=college_id,
            course=stud_data.get("course"),
            branch=stud_data.get("branch"),
            batch=stud_data.get("batch")
        )
        db.add(student)
        db.commit()
        db.refresh(student)
    else:
        # Update missing fields
        if (not student.branch or student.branch == "Unknown") and stud_data.get("branch"):
            student.branch = stud_data["branch"]
        if not student.course and stud_data.get("course"):
            student.course = stud_data["course"]
        if not student.batch and stud_data.get("batch"):
            student.batch = stud_data["batch"]
        db.commit()

    # 3. Semester Result
    sem_result = SemesterResult(
        student_id=student.id,
        document_id=doc.id,
        semester=sem_data.get("semester") or "I",
        regulation=sem_data.get("regulation"),
        examination_name=sem_data.get("examination_name"),
        examination_month_year=sem_data.get("examination_month_year"),
        date_of_issue=sem_data.get("date_of_issue"),
        sgpa=sem_data.get("sgpa"),
        cgpa=sem_data.get("cgpa"),
        total_credits=sem_data.get("total_credits"),
        subjects_count=sem_data.get("subjects_count", len(subjects)),
        passed_count=sem_data.get("passed_count", 0),
        failed_count=sem_data.get("failed_count", 0),
        backlog_count=sem_data.get("backlog_count", 0),
        overall_result=sem_data.get("overall_result"),
        verification_status=ver_status,
        raw_text=result.get("raw_text"),
        extraction_profile=result.get("parser_used", "general")
    )
    db.add(sem_result)
    db.commit()
    db.refresh(sem_result)

    # 4. Subject Marks
    for sub in subjects:
        sub_mark = SubjectMark(
            semester_result_id=sem_result.id,
            subject_code=sub["subject_code"],
            subject_name=sub["subject_name"],
            internal_marks=sub.get("internal_marks"),
            external_marks=sub.get("external_marks"),
            practical_marks=sub.get("practical_marks"),
            total_marks=sub.get("total_marks"),
            max_marks=sub.get("max_marks"),
            grade=sub.get("grade"),
            grade_points=sub.get("grade_points"),
            credits=sub.get("credits"),
            subject_result=sub.get("subject_result"),
            is_pass=sub.get("is_pass", True),
            confidence=sub.get("confidence", 1.0),
            provenance=sub.get("provenance", "EXTRACTED")
        )
        db.add(sub_mark)

    # 5. Extraction Issues
    for iss in issues:
        db_issue = ExtractionIssue(
            document_id=doc.id,
            semester_result_id=sem_result.id,
            field_name=iss.get("field_name"),
            issue_type=iss.get("issue_type", "GENERAL"),
            severity=iss.get("severity", "WARNING"),
            message=iss.get("message", "")
        )
        db.add(db_issue)

    db.commit()

    return {
        "student_id": student.id,
        "roll_number": student.roll_number,
        "student_name": student.name,
        "semester": sem_result.semester,
        "sgpa": sem_result.sgpa,
        "subjects_extracted": len(subjects),
        "issues_count": len(issues),
        "verification_status": ver_status
    }

@router.post("")
async def upload_marks_memos(
    files: List[UploadFile] = File(...),
    batch_id: Optional[str] = Form(None),
    profile: Optional[str] = Form("auto"),
    db: Session = Depends(get_db)
):
    if not files:
        raise HTTPException(status_code=400, detail="No files provided for upload.")

    if len(files) > settings.MAX_BATCH_SIZE:
        raise HTTPException(status_code=400, detail=f"Maximum allowed batch size is {settings.MAX_BATCH_SIZE} files.")

    # Expand any ZIP archives into constituent files
    file_queue = []
    for file in files:
        raw_name = file.filename or "memo.pdf"
        safe_name = sanitize_filename(raw_name)
        content = await file.read()

        if safe_name.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(content)) as z:
                    for zinfo in z.infolist():
                        if zinfo.is_dir() or zinfo.filename.startswith("__MACOSX"):
                            continue
                        z_ext = Path(zinfo.filename).suffix.lower()
                        if z_ext in settings.ALLOWED_EXTENSIONS and z_ext != ".zip":
                            z_bytes = z.read(zinfo.filename)
                            z_safe = sanitize_filename(Path(zinfo.filename).name)
                            mime = "application/pdf" if z_ext == ".pdf" else "image/jpeg"
                            file_queue.append((z_safe, z_bytes, mime))
            except Exception as e:
                # Still queue the zip so failure can be recorded
                file_queue.append((safe_name, content, file.content_type or "application/zip"))
        else:
            file_queue.append((safe_name, content, file.content_type or "application/octet-stream"))

    active_batch_id = batch_id or str(uuid.uuid4())
    batch = db.query(ProcessingBatch).filter(ProcessingBatch.id == active_batch_id).first()
    if not batch:
        batch = ProcessingBatch(
            id=active_batch_id,
            mode=settings.MODE,
            total_files=len(file_queue),
            processed_files=0,
            failed_files=0,
            needs_review_files=0,
            status="PROCESSING"
        )
        db.add(batch)
        db.commit()

    processed_summary = []

    for item_name, item_bytes, item_mime in file_queue:
        start_time = time.time()
        file_size = len(item_bytes)

        # Validate
        is_valid, err_msg = validate_uploaded_file(item_name, file_size)
        doc = UploadedDocument(
            batch_id=active_batch_id,
            filename=item_name,
            file_size=file_size,
            mime_type=item_mime,
            status="PROCESSING"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        if not is_valid:
            doc.status = "FAILED"
            doc.error_message = err_msg
            batch.failed_files += 1
            db.commit()
            processed_summary.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "status": "FAILED",
                "error": err_msg
            })
            continue

        # Save to disk
        save_path = settings.UPLOAD_PATH / f"{doc.id}_{item_name}"
        with open(save_path, "wb") as f:
            f.write(item_bytes)
        doc.file_path = str(save_path)
        db.commit()

        # Run Extraction
        try:
            extracted_results = extraction_engine.process_document(
                file_bytes=item_bytes,
                filename=item_name,
                preferred_profile=profile
            )

            memos_meta = []
            has_review = False
            ocr_used = False

            for res in extracted_results:
                m_info = _save_single_memo_result(db, doc, res)
                memos_meta.append(m_info)
                if res.get("verification_status") == "NEEDS_REVIEW":
                    has_review = True
                if res.get("ocr_used"):
                    ocr_used = True

            elapsed_ms = int((time.time() - start_time) * 1000)
            doc.status = "NEEDS_REVIEW" if has_review else "COMPLETED"
            doc.ocr_used = ocr_used
            doc.processing_time_ms = elapsed_ms

            if has_review:
                batch.needs_review_files += 1
            else:
                batch.processed_files += 1

            db.commit()

            first_m = memos_meta[0] if memos_meta else {}
            processed_summary.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "status": doc.status,
                "memos_extracted": len(extracted_results),
                "roll_number": first_m.get("roll_number", "N/A"),
                "student_name": first_m.get("student_name", "N/A"),
                "semester": first_m.get("semester", "N/A"),
                "sgpa": first_m.get("sgpa"),
                "subjects_extracted": sum(m.get("subjects_extracted", 0) for m in memos_meta),
                "issues_count": sum(m.get("issues_count", 0) for m in memos_meta),
                "ocr_used": doc.ocr_used,
                "memos": memos_meta
            })

        except Exception as e:
            elapsed_ms = int((time.time() - start_time) * 1000)
            doc.status = "FAILED"
            doc.error_message = str(e)
            doc.processing_time_ms = elapsed_ms
            batch.failed_files += 1
            db.commit()

            processed_summary.append({
                "document_id": doc.id,
                "filename": doc.filename,
                "status": "FAILED",
                "error": str(e)
            })

    # Update batch status
    if batch.failed_files == batch.total_files:
        batch.status = "FAILED"
    else:
        batch.status = "COMPLETED"
    db.commit()

    return {
        "batch_id": active_batch_id,
        "batch_status": batch.status,
        "total_files": batch.total_files,
        "processed_files": batch.processed_files,
        "needs_review_files": batch.needs_review_files,
        "failed_files": batch.failed_files,
        "items": processed_summary
    }

@router.get("/document/{doc_id}/file")
def get_document_file(doc_id: int, download: bool = False, db: Session = Depends(get_db)):
    """Serves uploaded marks memo file for in-browser visual inspection (inline) or download (attachment)."""
    doc = db.query(UploadedDocument).filter(UploadedDocument.id == doc_id).first()
    if not doc or not doc.file_path or not os.path.exists(doc.file_path):
        raise HTTPException(status_code=404, detail="Document file not found on disk.")
    
    media_type = "application/pdf" if doc.filename.lower().endswith(".pdf") else doc.mime_type
    headers = {}
    if download:
        headers["Content-Disposition"] = f'attachment; filename="{doc.filename}"'
    else:
        headers["Content-Disposition"] = f'inline; filename="{doc.filename}"'

    return FileResponse(doc.file_path, media_type=media_type, headers=headers)

@router.post("/load-sample-batch")
def load_sample_multi_memo_pack(db: Session = Depends(get_db)):
    """
    Instantly populates the database with multi-university sample memos:
    - Multi-semester 3-page student progression
    - Multi-student class tabulation gazette
    - JNTU, Anna University, and Autonomous memos
    """
    from ..config import BASE_DIR
    sample_dir = BASE_DIR.parent / "sample_memos"
    if not sample_dir.exists():
        raise HTTPException(status_code=404, detail="Sample memos directory not found.")

    sample_files = [
        "memo_multi_semester.pdf",
        "memo_class_gazette.pdf",
        "memo_1_jntu_passed.pdf",
        "memo_2_jntu_backlog.pdf",
        "memo_3_anna_univ.pdf",
        "memo_4_flagged_review.pdf"
    ]

    total_memos_extracted = 0
    active_batch_id = str(uuid.uuid4())
    batch = ProcessingBatch(
        id=active_batch_id,
        mode=settings.MODE,
        total_files=len(sample_files),
        status="PROCESSING"
    )
    db.add(batch)
    db.commit()

    for fname in sample_files:
        fpath = sample_dir / fname
        if not fpath.exists():
            continue
        content = fpath.read_bytes()

        doc = UploadedDocument(
            batch_id=active_batch_id,
            filename=fname,
            file_size=len(content),
            mime_type="application/pdf",
            status="PROCESSING"
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)

        save_path = settings.UPLOAD_PATH / f"{doc.id}_{fname}"
        save_path.write_bytes(content)
        doc.file_path = str(save_path)
        db.commit()

        try:
            results = extraction_engine.process_document(content, fname)
            has_review = False
            for res in results:
                _save_single_memo_result(db, doc, res)
                total_memos_extracted += 1
                if res.get("verification_status") == "NEEDS_REVIEW":
                    has_review = True

            doc.status = "NEEDS_REVIEW" if has_review else "COMPLETED"
            if has_review:
                batch.needs_review_files += 1
            else:
                batch.processed_files += 1
            db.commit()
        except Exception as e:
            doc.status = "FAILED"
            doc.error_message = str(e)
            batch.failed_files += 1
            db.commit()

    batch.status = "COMPLETED"
    db.commit()

    return {
        "message": f"Successfully ingested {len(sample_files)} documents extracting {total_memos_extracted} distinct marks memorandum records!",
        "batch_id": active_batch_id,
        "memos_extracted": total_memos_extracted
    }


@router.get("/batch/{batch_id}")
def get_batch_status(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(ProcessingBatch).filter(ProcessingBatch.id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")

    docs = db.query(UploadedDocument).filter(UploadedDocument.batch_id == batch_id).all()
    
    return {
        "batch_id": batch.id,
        "status": batch.status,
        "mode": batch.mode,
        "total_files": batch.total_files,
        "processed_files": batch.processed_files,
        "needs_review_files": batch.needs_review_files,
        "failed_files": batch.failed_files,
        "created_at": batch.created_at,
        "documents": [
            {
                "id": d.id,
                "filename": d.filename,
                "file_size": d.file_size,
                "status": d.status,
                "error_message": d.error_message,
                "ocr_used": d.ocr_used,
                "processing_time_ms": d.processing_time_ms
            }
            for d in docs
        ]
    }


@router.get("/recent")
def get_recent_documents(limit: int = 10, db: Session = Depends(get_db)):
    """Returns the most recent uploaded documents for dashboard feeds."""
    docs = db.query(UploadedDocument).order_by(UploadedDocument.created_at.desc()).limit(limit).all()
    return [
        {
            "id": d.id,
            "filename": d.filename,
            "file_size": d.file_size,
            "mime_type": d.mime_type,
            "status": d.status,
            "error_message": d.error_message,
            "ocr_used": d.ocr_used,
            "processing_time_ms": d.processing_time_ms,
            "created_at": d.created_at.isoformat() if d.created_at else None
        }
        for d in docs
    ]

