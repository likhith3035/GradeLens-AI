import re
from typing import Dict, Any, List, Optional
from .base_parser import BaseMemoParser

class GeneralMemoParser(BaseMemoParser):
    name = "general"
    description = "Universal Academic Marks Memo Parser"

    # Common regex patterns for academic headers
    ROLL_PATTERNS = [
        re.compile(r'(?:H\.?T\.?\s*(?:NO|NUMBER)|HALL\s*TICKET\s*NO|ROLL\s*(?:NO|NUMBER)|REG(?:ISTRATION)?\s*(?:NO|NUMBER)|ENROLLMENT\s*NO|STUDENT\s*ID)[\s:\.\-]*([A-Z0-9\-_]{5,20})', re.IGNORECASE),
        re.compile(r'\b([0-9]{2}[A-Z0-9]{2}[0-9A-Z]{5,7})\b'),  # Standard 10-digit Indian roll number format
    ]

    NAME_PATTERNS = [
        re.compile(r'(?:NAME\s*OF\s*THE\s*CANDIDATE|NAME\s*OF\s*THE\s*STUDENT|STUDENT(?:\'?S)?\s*NAME|CANDIDATE\s*NAME|NAME)[\s:\.\-]*([A-Z\s\.\']{3,50})', re.IGNORECASE),
    ]

    COLLEGE_PATTERNS = [
        re.compile(r'(?:COLLEGE|INSTITUTE|ACADEMY|UNIVERSITY)[\s:\.\-]*([A-Za-z0-9\s,\.\(\)\-]{4,100})', re.IGNORECASE),
    ]

    COURSE_BRANCH_PATTERNS = [
        re.compile(r'(?:COURSE|DEGREE|PROGRAM(?:ME)?)[\s:\.\-]*([A-Za-z0-9\s\.\(\)\-]{2,40})', re.IGNORECASE),
        re.compile(r'(?:BRANCH|DEPARTMENT|SPECIALIZATION)[\s:\.\-]*([A-Za-z0-9\s\.\(\)\-]{2,60})', re.IGNORECASE),
    ]

    SEMESTER_PATTERNS = [
        re.compile(r'(?:SEMESTER|SEM|YEAR\s*&\s*SEM)[\s:\.\-]*([I|V|X|0-9]+(?:\s*-\s*[I|V|X|0-9]+)?|[0-9](?:st|nd|rd|th)?(?:\s*Sem(?:ester)?)?)', re.IGNORECASE),
        re.compile(r'\b([I|V|X]+(?:\s*Year)?\s*[I|V|X]+\s*Sem(?:ester)?)\b', re.IGNORECASE),
    ]

    REGULATION_PATTERNS = [
        re.compile(r'(?:REGULATION|REGN)[\s:\.\-]*([A-Z0-9\-]+)', re.IGNORECASE),
    ]

    EXAM_PATTERNS = [
        re.compile(r'(?:EXAMINATION|EXAM)[\s:\.\-]*([^\n\r]{4,80})', re.IGNORECASE),
        re.compile(r'(?:MONTH\s*&?\s*YEAR|HELD\s*IN)[\s:\.\-]*([A-Za-z]{3,10}\s*[0-9]{4})', re.IGNORECASE),
    ]

    SGPA_PATTERNS = [
        re.compile(r'(?:SGPA|SEMESTER\s*GPA|GPA)[\s:\.\-=]*([0-9]\.[0-9]{1,3})', re.IGNORECASE),
    ]

    CGPA_PATTERNS = [
        re.compile(r'(?:CGPA|CUMULATIVE\s*GPA)[\s:\.\-=]*([0-9]\.[0-9]{1,3})', re.IGNORECASE),
    ]

    def can_parse(self, text: str, metadata: Dict[str, Any]) -> float:
        # General parser is always applicable as a fallback or baseline
        return 0.5

    def parse(self, text: str, tables: List[List[List[str]]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        issues = []
        
        # 1. Extract Student Info
        roll_number = self._extract_first(self.ROLL_PATTERNS, text)
        if not roll_number:
            # Fallback search for a standalone token matching typical roll numbers
            m = re.search(r'\b([0-9]{2}[A-Z][0-9]{2}[A-Z0-9]{4,6})\b', text)
            if m:
                roll_number = m.group(1).upper()

        name = self._extract_first(self.NAME_PATTERNS, text)
        if name:
            # Clean unwanted header words from name if captured
            name = re.sub(r'(?:FATHER|MOTHER|ROLL|HTNO|REGNO|COLLEGE|BRANCH).*$', '', name, flags=re.IGNORECASE).strip()
            name = " ".join(name.split())
        else:
            issues.append(self.create_issue("name", "MISSING_MANDATORY_FIELD", "WARNING", "Student name could not be automatically identified."))

        if not roll_number:
            issues.append(self.create_issue("roll_number", "MISSING_MANDATORY_FIELD", "ERROR", "Roll / Registration Number not detected."))
        else:
            roll_number = roll_number.strip().upper()

        college_name = self._extract_first(self.COLLEGE_PATTERNS, text)
        if college_name:
            college_name = college_name.strip()
            # Clean up trailing words
            college_name = college_name.split('\n')[0].strip()

        course = self._extract_pattern(r'(?:B\.?TECH|B\.?E\.?|M\.?TECH|MCA|MBA|B\.?SC|M\.?SC|B\.?COM|BBA)', text)
        branch = self._extract_pattern(r'(?:COMPUTER\s*SCIENCE|INFORMATION\s*TECHNOLOGY|MECHANICAL|CIVIL|ELECTRONICS(?:\s*&?\s*COMMUNICATION)?|ELECTRICAL(?:\s*&?\s*ELECTRONICS)?|CSE|ECE|EEE|MECH|IT|CIVIL)', text)

        # 2. Semester & Exam Info
        semester = self._extract_first(self.SEMESTER_PATTERNS, text) or "I"
        regulation = self._extract_first(self.REGULATION_PATTERNS, text)
        exam_month_year = self._extract_pattern(r'(?:JAN(?:UARY)?|FEB(?:RUARY)?|MAR(?:CH)?|APR(?:IL)?|MAY|JUNE?|JULY?|AUG(?:UST)?|SEP(?:TEMBER)?|OCT(?:OBER)?|NOV(?:EMBER)?|DEC(?:EMBER)?)\s*[-/,\s]?\s*(?:20[0-9]{2})', text)
        exam_name = self._extract_first(self.EXAM_PATTERNS, text)

        sgpa = self._extract_float(self.SGPA_PATTERNS, text)
        cgpa = self._extract_float(self.CGPA_PATTERNS, text)

        # 3. Subject Extraction
        subjects = self._extract_subjects_from_tables_or_text(text, tables, issues)

        return {
            "student": {
                "name": name or "UNKNOWN",
                "roll_number": roll_number or "UNKNOWN",
                "college_name": college_name,
                "course": course,
                "branch": branch,
                "batch": None
            },
            "semester_info": {
                "semester": semester.strip().upper(),
                "regulation": regulation.strip().upper() if regulation else None,
                "examination_name": exam_name.strip() if exam_name else None,
                "examination_month_year": exam_month_year.strip() if exam_month_year else None,
                "date_of_issue": None,
                "sgpa": sgpa,
                "cgpa": cgpa
            },
            "subjects": subjects,
            "issues": issues
        }

    def _extract_first(self, patterns: List[re.Pattern], text: str) -> Optional[str]:
        for pat in patterns:
            m = pat.search(text)
            if m:
                val = m.group(1).strip()
                if val:
                    return val
        return None

    def _extract_pattern(self, pattern_str: str, text: str) -> Optional[str]:
        m = re.search(pattern_str, text, re.IGNORECASE)
        return m.group(0).strip().upper() if m else None

    def _extract_float(self, patterns: List[re.Pattern], text: str) -> Optional[float]:
        val_str = self._extract_first(patterns, text)
        if val_str:
            try:
                f = float(val_str)
                if 0 <= f <= 10.0:
                    return round(f, 2)
            except ValueError:
                pass
        return None

    def _extract_subjects_from_tables_or_text(self, text: str, tables: List[List[List[str]]], issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        subjects = []
        
        # 1. Try table extraction first if structured tables exist
        if tables:
            for table in tables:
                table_subjects = self._parse_structured_table(table)
                if table_subjects:
                    subjects.extend(table_subjects)

        # 2. Fallback to line-by-line regex if no subjects found in tables
        if not subjects:
            subjects = self._parse_text_lines(text)

        if not subjects:
            issues.append(self.create_issue("subjects", "NO_SUBJECTS_FOUND", "ERROR", "Could not parse any subject mark rows from document."))

        return subjects

    def _parse_structured_table(self, table: List[List[str]]) -> List[Dict[str, Any]]:
        results = []
        if len(table) < 2:
            return results

        # Identify header row
        header_idx = -1
        col_map = {}
        for idx, row in enumerate(table[:5]):
            row_str = " ".join(str(c).lower() for c in row)
            if any(k in row_str for k in ("subject", "course", "sub code", "grade", "credits", "marks")):
                header_idx = idx
                for c_idx, cell in enumerate(row):
                    clean = str(cell).strip().lower()
                    if "code" in clean:
                        col_map["code"] = c_idx
                    elif "name" in clean or "title" in clean or "subject" in clean:
                        col_map["name"] = c_idx
                    elif "int" in clean:
                        col_map["int"] = c_idx
                    elif "ext" in clean:
                        col_map["ext"] = c_idx
                    elif "tot" in clean:
                        col_map["tot"] = c_idx
                    elif "max" in clean:
                        col_map["max"] = c_idx
                    elif "grade point" in clean:
                        col_map["points"] = c_idx
                    elif "grade" in clean:
                        col_map["grade"] = c_idx
                    elif "credit" in clean:
                        col_map["credits"] = c_idx
                    elif "result" in clean or "status" in clean:
                        col_map["result"] = c_idx
                break

        if header_idx != -1 and ("code" in col_map or "name" in col_map):
            for row in table[header_idx + 1:]:
                if len(row) <= max(col_map.values(), default=0):
                    continue
                code = str(row[col_map.get("code", 0)]).strip() if "code" in col_map else ""
                name = str(row[col_map.get("name", 1)]).strip() if "name" in col_map else ""
                
                # Skip header repetitions or empty lines
                if not name or name.lower() in ("subject name", "course title", "total"):
                    continue

                sub = self._create_subject_dict(
                    code=code,
                    name=name,
                    int_marks=row[col_map["int"]] if "int" in col_map else None,
                    ext_marks=row[col_map["ext"]] if "ext" in col_map else None,
                    tot_marks=row[col_map["tot"]] if "tot" in col_map else None,
                    grade=row[col_map["grade"]] if "grade" in col_map else None,
                    credits=row[col_map["credits"]] if "credits" in col_map else None,
                    points=row[col_map["points"]] if "points" in col_map else None,
                    result=row[col_map["result"]] if "result" in col_map else None
                )
                results.append(sub)

        return results

    def _parse_text_lines(self, text: str) -> List[Dict[str, Any]]:
        results = []
        lines = text.split('\n')
        # Typical pattern: SubCode [space] SubName [space] [Internal] [External] [Total] [Grade] [Credits] [Result]
        # Example: 18CS301 DATA STRUCTURES & ALGORITHMS 25 50 75 A 4 P
        # Example: CS601 DATABASE MANAGEMENT SYSTEMS O 4 PASSED
        # Example: HS101 PROFESSIONAL ENGLISH 88 100 A+ 3 PASS
        
        row_re = re.compile(
            r'^\s*([A-Z0-9]{4,10})\s+([A-Z0-9\s&/\-\(\)]{4,45})\s+([0-9]{1,3})?\s*([0-9]{1,3})?\s*([0-9]{1,3})?\s*([O|S|A|B|C|D|P|F|AB][\+]?)\s+([0-9](?:\.[0-9])?)\s*([A-Z]+)?\s*$',
            re.IGNORECASE
        )

        simple_re = re.compile(
            r'^\s*([A-Z0-9]{4,10})\s+([A-Za-z0-9\s&/\-\(\)]{4,50})\s+([O|S|A|B|C|D|P|F|AB][\+]?)\s+([0-9](?:\.[0-9])?)\s*([A-Z]+)?\s*$',
            re.IGNORECASE
        )

        for line in lines:
            line_str = line.strip()
            if not line_str or len(line_str) < 10:
                continue

            m = row_re.match(line_str)
            if m:
                code, name, val1, val2, val3, grade, credits, result = m.groups()
                # Determine int, ext, tot marks based on available captured numbers
                nums = [float(v) for v in (val1, val2, val3) if v is not None]
                int_m, ext_m, tot_m = None, None, None
                if len(nums) == 3:
                    int_m, ext_m, tot_m = nums[0], nums[1], nums[2]
                elif len(nums) == 2:
                    int_m, tot_m = nums[0], nums[1]
                elif len(nums) == 1:
                    tot_m = nums[0]

                sub = self._create_subject_dict(
                    code=code,
                    name=name.strip(),
                    int_marks=int_m,
                    ext_marks=ext_m,
                    tot_marks=tot_m,
                    grade=grade,
                    credits=credits,
                    points=None,
                    result=result
                )
                results.append(sub)
                continue

            m2 = simple_re.match(line_str)
            if m2:
                code, name, grade, credits, result = m2.groups()
                sub = self._create_subject_dict(
                    code=code,
                    name=name.strip(),
                    int_marks=None,
                    ext_marks=None,
                    tot_marks=None,
                    grade=grade,
                    credits=credits,
                    points=None,
                    result=result
                )
                results.append(sub)

        return results

    def _create_subject_dict(
        self,
        code: str,
        name: str,
        int_marks: Any = None,
        ext_marks: Any = None,
        tot_marks: Any = None,
        max_marks: Any = None,
        grade: Any = None,
        credits: Any = None,
        points: Any = None,
        result: Any = None
    ) -> Dict[str, Any]:
        
        def safe_float(val: Any) -> Optional[float]:
            if val is None or str(val).strip() in ("", "-", "NA", "N/A", "AB"):
                return None
            try:
                return round(float(str(val).strip()), 2)
            except ValueError:
                return None

        c_int = safe_float(int_marks)
        c_ext = safe_float(ext_marks)
        c_tot = safe_float(tot_marks)
        c_max = safe_float(max_marks) or (100.0 if c_tot is not None and c_tot <= 100 else None)
        c_credits = safe_float(credits)
        c_points = safe_float(points)

        clean_grade = str(grade).strip().upper() if grade and str(grade).strip() not in ("", "-") else None
        clean_res = str(result).strip().upper() if result and str(result).strip() not in ("", "-") else None

        # Determine pass/fail
        is_pass = True
        if clean_grade in ("F", "FAIL", "AB", "ABSENT"):
            is_pass = False
        elif clean_res in ("F", "FAIL", "FAILED", "AB"):
            is_pass = False

        return {
            "subject_code": code.strip().upper(),
            "subject_name": name.strip(),
            "internal_marks": c_int,
            "external_marks": c_ext,
            "practical_marks": None,
            "total_marks": c_tot,
            "max_marks": c_max,
            "grade": clean_grade,
            "grade_points": c_points,
            "credits": c_credits,
            "subject_result": clean_res or ("P" if is_pass else "F"),
            "is_pass": is_pass,
            "confidence": 0.95,
            "provenance": "EXTRACTED"
        }
