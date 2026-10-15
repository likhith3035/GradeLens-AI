from typing import List, Dict, Any, Optional, Tuple

GRADE_TO_POINTS: Dict[str, float] = {
    "O": 10.0,
    "OUTSTANDING": 10.0,
    "A+": 9.0,
    "S": 9.0,
    "EXCELLENT": 9.0,
    "A": 8.0,
    "VERY GOOD": 8.0,
    "B+": 7.0,
    "GOOD": 7.0,
    "B": 6.0,
    "ABOVE AVERAGE": 6.0,
    "C": 5.0,
    "AVERAGE": 5.0,
    "P": 4.0,
    "PASS": 4.0,
    "D": 4.0,
    "F": 0.0,
    "FAIL": 0.0,
    "AB": 0.0,
    "ABSENT": 0.0,
    "NA": 0.0,
}

FAIL_GRADES = {"F", "FAIL", "AB", "ABSENT", "WH", "WITHHELD", "MALPRACTICE"}

def normalize_grade(grade_str: Optional[str]) -> Optional[str]:
    if not grade_str:
        return None
    cleaned = grade_str.strip().upper()
    return cleaned

def determine_subject_pass(
    grade: Optional[str] = None,
    subject_result: Optional[str] = None,
    total_marks: Optional[float] = None,
    max_marks: Optional[float] = None,
    passing_percentage: float = 40.0
) -> Tuple[bool, str]:
    """
    Determines pass/fail without fabricating.
    Returns (is_pass, provenance).
    """
    if grade:
        norm_grade = normalize_grade(grade)
        if norm_grade in FAIL_GRADES:
            return False, "EXTRACTED_GRADE"
        if norm_grade in GRADE_TO_POINTS and GRADE_TO_POINTS[norm_grade] > 0:
            return True, "EXTRACTED_GRADE"

    if subject_result:
        res = subject_result.strip().upper()
        if res in ("P", "PASS", "PASSED"):
            return True, "EXTRACTED_RESULT"
        if res in ("F", "FAIL", "FAILED", "AB", "ABSENT"):
            return False, "EXTRACTED_RESULT"

    if total_marks is not None and max_marks is not None and max_marks > 0:
        pct = (total_marks / max_marks) * 100.0
        return (pct >= passing_percentage), "CALCULATED_MARKS"

    # Inconclusive - default to True but flag for verification
    return True, "INCONCLUSIVE"


def calculate_sgpa(subjects: List[Dict[str, Any]]) -> Optional[float]:
    """
    Computes SGPA = sum(credits * grade_points) / sum(credits).
    Strict rule: If any subject has undefined credits or grade points, returns None
    to prevent fabrication.
    """
    if not subjects:
        return None

    total_credit_points = 0.0
    total_credits = 0.0

    for sub in subjects:
        credits = sub.get("credits")
        points = sub.get("grade_points")
        grade = sub.get("grade")

        # Derive grade points if grade is known and points is None
        if points is None and grade:
            norm = normalize_grade(grade)
            points = GRADE_TO_POINTS.get(norm)

        if credits is None or points is None:
            # Cannot accurately calculate without guessing credits/points
            return None

        try:
            c = float(credits)
            p = float(points)
            if c < 0:
                return None
            total_credit_points += (c * p)
            total_credits += c
        except (ValueError, TypeError):
            return None

    if total_credits <= 0:
        return None

    return round(total_credit_points / total_credits, 2)


def compute_semester_summary(subjects: List[Dict[str, Any]], extracted_sgpa: Optional[float] = None) -> Dict[str, Any]:
    """
    Summarizes passed, failed, backlog count, SGPA, credits.
    """
    total_subs = len(subjects)
    passed_subs = 0
    failed_subs = 0
    total_credits = 0.0
    has_credit_info = False

    for sub in subjects:
        is_pass, _ = determine_subject_pass(
            grade=sub.get("grade"),
            subject_result=sub.get("subject_result"),
            total_marks=sub.get("total_marks"),
            max_marks=sub.get("max_marks"),
        )
        if is_pass:
            passed_subs += 1
        else:
            failed_subs += 1

        c = sub.get("credits")
        if c is not None:
            try:
                total_credits += float(c)
                has_credit_info = True
            except (ValueError, TypeError):
                pass

    calculated_sgpa = calculate_sgpa(subjects)
    final_sgpa = extracted_sgpa if extracted_sgpa is not None else calculated_sgpa

    overall_result = "PASSED" if failed_subs == 0 and total_subs > 0 else ("FAILED" if failed_subs > 0 else "PENDING")

    return {
        "total_subjects": total_subs,
        "subjects_passed": passed_subs,
        "subjects_failed": failed_subs,
        "backlog_count": failed_subs,  # Current memo failed subjects
        "sgpa": final_sgpa,
        "calculated_sgpa": calculated_sgpa,
        "total_credits": round(total_credits, 2) if has_credit_info else None,
        "overall_result": overall_result
    }


def compute_cumulative_gpa(semester_results: List[Dict[str, Any]]) -> Optional[float]:
    """
    Computes CGPA across multiple semesters using credits and SGPA:
    CGPA = sum(SGPA_i * Credits_i) / sum(Credits_i).
    Fallback to simple average of valid SGPAs if credits are unavailable across all semesters.
    """
    if not semester_results:
        return None

    valid_with_credits = []
    valid_sgpas = []

    for res in semester_results:
        sgpa = res.get("sgpa")
        credits = res.get("total_credits")
        if sgpa is not None:
            try:
                s = float(sgpa)
                if 0 <= s <= 10.0:
                    valid_sgpas.append(s)
                    if credits is not None:
                        c = float(credits)
                        if c > 0:
                            valid_with_credits.append((s, c))
            except (ValueError, TypeError):
                pass

    if valid_with_credits:
        num = sum(s * c for s, c in valid_with_credits)
        den = sum(c for _, c in valid_with_credits)
        return round(num / den, 2) if den > 0 else None

    if valid_sgpas:
        return round(sum(valid_sgpas) / len(valid_sgpas), 2)

    return None
