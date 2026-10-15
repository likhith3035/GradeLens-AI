from typing import List, Dict, Type, Optional
from .base_parser import BaseMemoParser
from .general_parser import GeneralMemoParser
from .jntu_parser import JNTUMemoParser
from .anna_parser import AnnaUniversityParser

class ParserRegistry:
    def __init__(self):
        self._parsers: List[BaseMemoParser] = [
            JNTUMemoParser(),
            AnnaUniversityParser(),
            GeneralMemoParser(),
        ]

    def register_parser(self, parser: BaseMemoParser):
        self._parsers.insert(0, parser)

    def select_best_parser(self, text: str, metadata: Dict) -> BaseMemoParser:
        best_parser = self._parsers[-1]  # General fallback
        best_score = -1.0

        for parser in self._parsers:
            score = parser.can_parse(text, metadata)
            if score > best_score:
                best_score = score
                best_parser = parser

        return best_parser

    def get_parser_by_name(self, name: str) -> Optional[BaseMemoParser]:
        for parser in self._parsers:
            if parser.name.lower() == name.lower():
                return parser
        return None

    def list_available_parsers(self) -> List[Dict[str, str]]:
        return [
            {"name": p.name, "description": p.description}
            for p in self._parsers
        ]

parser_registry = ParserRegistry()
