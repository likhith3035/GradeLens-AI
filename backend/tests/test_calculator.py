import pytest
from app.analytics.calculator import (
    calculate_sgpa,
    determine_subject_pass,
    compute_semester_summary,
    compute_cumulative_gpa
)

def test_sgpa_calculation_standard():
    subjects = [
        {"credits": 3.0, "grade_points": 8.0, "grade": "A"},
        {"credits": 4.0, "grade_points": 10.0, "grade": "O"},
        {"credits": 3.0, "grade_points": 9.0, "grade": "A+"},
    ]
    # Total credit points: (3*8) + (4*10) + (3*9) = 24 + 40 + 27 = 91
    # Total credits: 3 + 4 + 3 = 10
    # SGPA = 91 / 10 = 9.1
    sgpa = calculate_sgpa(subjects)
    assert sgpa == 9.1

def test_sgpa_missing_credits_no_fabrication():
    subjects = [
        {"credits": 3.0, "grade_points": 8.0, "grade": "A"},
        {"credits": None, "grade_points": 9.0, "grade": "A+"}, # Missing credits!
    ]
    # Must NOT fabricate missing credits
    sgpa = calculate_sgpa(subjects)
    assert sgpa is None

def test_determine_subject_pass():
    is_pass, prov = determine_subject_pass(grade="A")
    assert is_pass is True
    assert prov == "EXTRACTED_GRADE"

    is_pass, prov = determine_subject_pass(grade="F")
    assert is_pass is False
    assert prov == "EXTRACTED_GRADE"

    is_pass, prov = determine_subject_pass(grade="AB")
    assert is_pass is False
    assert prov == "EXTRACTED_GRADE"

    is_pass, prov = determine_subject_pass(subject_result="PASS")
    assert is_pass is True

    is_pass, prov = determine_subject_pass(subject_result="FAIL")
    assert is_pass is False

def test_semester_summary_with_backlog():
    subjects = [
        {"grade": "A", "credits": 3.0, "grade_points": 8.0, "is_pass": True},
        {"grade": "F", "credits": 3.0, "grade_points": 0.0, "is_pass": False},
        {"grade": "B+", "credits": 4.0, "grade_points": 7.0, "is_pass": True},
    ]
    summary = compute_semester_summary(subjects)
    assert summary["total_subjects"] == 3
    assert summary["subjects_passed"] == 2
    assert summary["subjects_failed"] == 1
    assert summary["backlog_count"] == 1
    assert summary["overall_result"] == "FAILED"

def test_cumulative_gpa():
    semester_results = [
        {"semester": "I", "sgpa": 8.0, "total_credits": 20.0},
        {"semester": "II", "sgpa": 9.0, "total_credits": 20.0},
    ]
    # CGPA = (8*20 + 9*20) / 40 = 340 / 40 = 8.5
    cgpa = compute_cumulative_gpa(semester_results)
    assert cgpa == 8.5
