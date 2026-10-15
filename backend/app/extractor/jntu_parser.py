import re
from typing import Dict, Any, List
from .base_parser import BaseMemoParser
from .general_parser import GeneralMemoParser

class JNTUMemoParser(GeneralMemoParser):
    name = "jntu_autonomous"
    description = "JNTU & Autonomous Engineering College Marks Memo Parser"

    # Specific JNTU / Autonomous patterns
    JNTU_KEYWORDS = [
        "JAWAHARLAL NEHRU TECHNOLOGICAL UNIVERSITY",
        "JNTUH", "JNTUK", "JNTUA",
        "AUTONOMOUS", "GRADE CARD", "MARKS MEMORANDUM",
        "COLLEGE OF ENGINEERING"
    ]

    def can_parse(self, text: str, metadata: Dict[str, Any]) -> float:
        upper_text = text.upper()
        matches = sum(1 for kw in self.JNTU_KEYWORDS if kw in upper_text)
        if matches >= 2:
            return 0.95
        if matches == 1:
            return 0.75
        # Check standard 10-character Hall Ticket format: e.g. 20671A0512 or 19A51A0440
        if re.search(r'\b[0-9]{2}[A-Z0-9]{2}[1-5][A-Z0-9]{4}\b', upper_text):
            return 0.8
        return 0.3

    def parse(self, text: str, tables: List[List[List[str]]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        result = super().parse(text, tables, metadata)
        
        # Additional JNTU-specific enhancements
        # Often JNTU lists regulation like "R18", "R16", "R20", "R22"
        reg_m = re.search(r'\b(R(?:16|18|19|20|22|23))\b', text, re.IGNORECASE)
        if reg_m and not result["semester_info"]["regulation"]:
            result["semester_info"]["regulation"] = reg_m.group(1).upper()

        # Often JNTU roll numbers are explicitly 10 characters
        roll = result["student"]["roll_number"]
        if roll and roll != "UNKNOWN":
            m = re.search(r'\b([0-9]{2}[A-Z0-9]{2}[1-5][A-Z0-9]{4})\b', roll)
            if m:
                result["student"]["roll_number"] = m.group(1).upper()
                # Derive admission batch from first 2 digits e.g. 20 -> 2020-2024
                try:
                    yy = int(m.group(1)[:2])
                    start_year = 2000 + yy if yy < 50 else 1900 + yy
                    result["student"]["batch"] = f"{start_year}-{start_year + 4}"
                except ValueError:
                    pass

        return result
