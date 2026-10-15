from abc import ABC, abstractmethod
from typing import Dict, Any, List, Tuple

class BaseMemoParser(ABC):
    """
    Abstract base class for college/board marks memo parsers.
    Allows easy addition of new university formats without touching core logic.
    """
    name: str = "base"
    description: str = "Base Marks Memo Parser"

    @abstractmethod
    def can_parse(self, text: str, metadata: Dict[str, Any]) -> float:
        """
        Returns a confidence score from 0.0 to 1.0 indicating how likely
        this parser can accurately handle the provided memo text.
        """
        pass

    @abstractmethod
    def parse(self, text: str, tables: List[List[List[str]]], metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Parses text and tables, returning structured student, semester, and subject records.
        """
        pass

    def create_issue(self, field_name: str, issue_type: str, severity: str, message: str) -> Dict[str, Any]:
        return {
            "field_name": field_name,
            "issue_type": issue_type,
            "severity": severity,
            "message": message,
            "is_resolved": False
        }
