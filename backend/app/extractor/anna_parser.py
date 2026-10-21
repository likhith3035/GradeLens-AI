import re
from typing import Dict, Any, List
from .general_parser import GeneralMemoParser

class AnnaUniversityParser(GeneralMemoParser):
    name = "anna_university"
    description = "Anna University & Affiliated Institutions Parser"

    ANNA_KEYWORDS = [
        "ANNA UNIVERSITY", "CHENNAI", "OFFICE OF THE CONTROLLER OF EXAMINATIONS",
        "CENTRE FOR ACADEMIC COURSES", "AFFILIATED INSTITUTIONS"
    ]

    def can_parse(self, text: str, metadata: Dict[str, Any]) -> float:
        upper = text.upper()
        if "ANNA UNIVERSITY" in upper:
            return 0.95
        if any(kw in upper for kw in self.ANNA_KEYWORDS):
            return 0.85
        # Anna University 12-digit register number: e.g. 312218104001
        if re.search(r'\b[0-9]{12}\b', upper):
            return 0.75
        return 0.2

    def parse(self, text: str, tables: List[List[List[str]]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        result = super().parse(text, tables, metadata)
        
        # Check for 12 digit register number
        m = re.search(r'\b([0-9]{12})\b', text)
        if m:
            result["student"]["roll_number"] = m.group(1)
            # Batch derivation from 5th & 6th digits e.g. 3122 18 104001 -> 2018-2022
            try:
                yy = int(m.group(1)[4:6])
                start_year = 2000 + yy
                result["student"]["batch"] = f"{start_year}-{start_year + 4}"
            except (ValueError, IndexError):
                pass

        return result
