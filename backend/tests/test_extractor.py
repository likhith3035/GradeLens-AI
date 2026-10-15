import pytest
from pathlib import Path
from app.extractor.engine import extraction_engine

SAMPLE_DIR = Path(__file__).resolve().parent.parent.parent / "sample_memos"

def test_extract_jntu_passed_memo():
    pdf_path = SAMPLE_DIR / "memo_1_jntu_passed.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        content = f.read()

    result = extraction_engine.process_file(content, pdf_path.name)
    assert result["student"]["roll_number"] == "20671A0512"
    assert "RAHUL REDDY" in result["student"]["name"].upper()
    assert result["semester_info"]["backlog_count"] == 0
    assert result["semester_info"]["overall_result"] == "PASSED"
    assert len(result["subjects"]) == 8
    assert result["verification_status"] == "VERIFIED"

def test_extract_jntu_backlog_memo():
    pdf_path = SAMPLE_DIR / "memo_2_jntu_backlog.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        content = f.read()

    result = extraction_engine.process_file(content, pdf_path.name)
    assert result["student"]["roll_number"] == "20671A0545"
    assert "PRIYA SHARMA" in result["student"]["name"].upper()
    assert result["semester_info"]["backlog_count"] == 1
    assert result["semester_info"]["overall_result"] == "FAILED"
    # Verify compiler design has F grade
    cd_sub = next((s for s in result["subjects"] if "COMPILER" in s["subject_name"].upper()), None)
    assert cd_sub is not None
    assert cd_sub["grade"] == "F"
    assert cd_sub["is_pass"] is False

def test_extract_anna_univ_memo():
    pdf_path = SAMPLE_DIR / "memo_3_anna_univ.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        content = f.read()

    result = extraction_engine.process_file(content, pdf_path.name)
    assert result["student"]["roll_number"] == "312218104001"
    assert "KARTHIK" in result["student"]["name"].upper()
    assert result["semester_info"]["overall_result"] == "PASSED"
    assert len(result["subjects"]) == 7

def test_extract_flagged_review_memo():
    pdf_path = SAMPLE_DIR / "memo_4_flagged_review.pdf"
    assert pdf_path.exists()

    with open(pdf_path, "rb") as f:
        content = f.read()

    result = extraction_engine.process_file(content, pdf_path.name)
    assert result["student"]["roll_number"] == "20B91A0499"
    # Should be flagged for review due to missing name and calculation discrepancy
    assert result["verification_status"] == "NEEDS_REVIEW"
    assert len(result["issues"]) > 0
