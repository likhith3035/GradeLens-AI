import io
import re
from pathlib import Path
from typing import Dict, Any, Optional, List
from PIL import Image

from .pdf_processor import PDFProcessor
from .ocr_processor import ocr_processor
from .registry import parser_registry
from ..analytics.calculator import compute_semester_summary

class ExtractionEngine:
    def _parse_single_block(
        self,
        text: str,
        tables: List[Any],
        filename: str,
        ocr_used: bool,
        ocr_confidence: float,
        preferred_profile: Optional[str] = None,
        page_info: Optional[str] = None
    ) -> Dict[str, Any]:
        """Parses a single marks memorandum text and table block."""
        issues = []

        # Choose parser
        if preferred_profile and preferred_profile != "auto":
            parser = parser_registry.get_parser_by_name(preferred_profile) or parser_registry.select_best_parser(text, {"filename": filename})
        else:
            parser = parser_registry.select_best_parser(text, {"filename": filename})

        # Parse text and tables
        parsed_data = parser.parse(text, tables, {"filename": filename})
        issues.extend(parsed_data.get("issues", []))

        # Check OCR confidence
        if ocr_used and ocr_confidence < 0.60:
            issues.append({
                "field_name": "ocr_confidence",
                "issue_type": "LOW_OCR_CONFIDENCE",
                "severity": "WARNING",
                "message": f"Average OCR confidence is low ({int(ocr_confidence * 100)}%). Manual review recommended.",
                "is_resolved": False
            })

        # Academic summary calculation
        extracted_sgpa = parsed_data["semester_info"].get("sgpa")
        summary = compute_semester_summary(parsed_data["subjects"], extracted_sgpa=extracted_sgpa)

        # Cross-validation: Check for discrepancies
        calc_sgpa = summary.get("calculated_sgpa")
        if extracted_sgpa is not None and calc_sgpa is not None:
            if abs(extracted_sgpa - calc_sgpa) > 0.05:
                issues.append({
                    "field_name": "sgpa",
                    "issue_type": "CALCULATION_MISMATCH",
                    "severity": "WARNING",
                    "message": f"Extracted SGPA ({extracted_sgpa}) differs from calculated SGPA ({calc_sgpa}) based on subject credits and grades.",
                    "is_resolved": False
                })

        # Merge summary into semester info
        parsed_data["semester_info"]["subjects_count"] = summary["total_subjects"]
        parsed_data["semester_info"]["passed_count"] = summary["subjects_passed"]
        parsed_data["semester_info"]["failed_count"] = summary["subjects_failed"]
        parsed_data["semester_info"]["backlog_count"] = summary["backlog_count"]
        parsed_data["semester_info"]["total_credits"] = summary["total_credits"]
        parsed_data["semester_info"]["overall_result"] = summary["overall_result"]
        if parsed_data["semester_info"]["sgpa"] is None:
            parsed_data["semester_info"]["sgpa"] = summary["sgpa"]

        # If page info provided, record it
        if page_info:
            parsed_data["semester_info"]["page_source"] = page_info

        # Determine verification status
        has_errors = any(i.get("severity") == "ERROR" for i in issues)
        has_warnings = any(i.get("severity") == "WARNING" for i in issues)
        verification_status = "NEEDS_REVIEW" if (has_errors or has_warnings) else "VERIFIED"

        return {
            "student": parsed_data["student"],
            "semester_info": parsed_data["semester_info"],
            "subjects": parsed_data["subjects"],
            "issues": issues,
            "raw_text": text,
            "ocr_used": ocr_used,
            "ocr_confidence": ocr_confidence,
            "parser_used": parser.name,
            "verification_status": verification_status
        }

    def process_document(
        self,
        file_bytes: bytes,
        filename: str,
        preferred_profile: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Processes a file and returns ALL extracted marks memorandum records.
        Supports:
        - Single memo per file
        - Multi-page multi-semester PDFs (e.g. Sem I, II, III in 1 file)
        - Multi-page class gazettes (multiple students across pages)
        """
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            pdf_data = PDFProcessor.extract_content(file_bytes)
            pages = pdf_data.get("pages", [])
            total_pages = pdf_data.get("total_pages", 1)

            # Check if this multi-page PDF contains multiple distinct memos
            if total_pages > 1 and len(pages) > 1:
                # Group pages into distinct memos
                memo_groups = []
                current_group = []

                roll_re = re.compile(r'(?:H\.?T\.?\s*No|Roll\s*No|Register\s*No|Registration\s*No|H\.T\.NO)[\s:\.]*([A-Za-z0-9]+)', re.IGNORECASE)
                univ_re = re.compile(r'GRADE\s+CARD|MARKS\s+MEMORANDUM|PROVISIONAL|UNIVERSITY|INSTITUTE|AUTONOMOUS', re.IGNORECASE)

                for p in pages:
                    has_roll = bool(roll_re.search(p["text"]))
                    has_univ = bool(univ_re.search(p["text"]))
                    has_tables = len(p["tables"]) > 0 or "Grade" in p["text"] or "Marks" in p["text"]

                    # If this page starts a new student or new memo header
                    if (has_roll or has_univ) and has_tables and len(current_group) > 0:
                        memo_groups.append(current_group)
                        current_group = [p]
                    else:
                        current_group.append(p)

                if current_group:
                    memo_groups.append(current_group)

                # If we successfully split into multiple distinct memos
                if len(memo_groups) > 1:
                    extracted_records = []
                    for g_idx, grp in enumerate(memo_groups):
                        grp_text = "\n\n".join(p["text"] for p in grp).strip()
                        grp_tables = [tbl for p in grp for tbl in p["tables"]]
                        page_nums = ", ".join(str(p["page_number"]) for p in grp)
                        page_label = f"Page {page_nums}"

                        record = self._parse_single_block(
                            text=grp_text,
                            tables=grp_tables,
                            filename=filename,
                            ocr_used=False,
                            ocr_confidence=1.0,
                            preferred_profile=preferred_profile,
                            page_info=page_label
                        )
                        # Only add if it actually extracted student or subjects
                        if record["subjects"] or record["student"].get("roll_number"):
                            extracted_records.append(record)

                    if extracted_records:
                        return extracted_records

            # Fallback for standard PDF (single memo or continuation)
            text = pdf_data["text"]
            tables = pdf_data["tables"]
            ocr_used = False
            ocr_confidence = 1.0

            if pdf_data["is_scanned"]:
                if ocr_processor.is_available():
                    ocr_used = True
                    ocr_texts = []
                    conf_scores = []
                    for img in pdf_data["rendered_images"]:
                        page_ocr_text, conf = ocr_processor.extract_text_from_image(img)
                        ocr_texts.append(page_ocr_text)
                        conf_scores.append(conf)
                    text = "\n\n--- OCR Page ---\n\n".join(ocr_texts)
                    ocr_confidence = round(sum(conf_scores) / len(conf_scores), 2) if conf_scores else 0.5

            single_rec = self._parse_single_block(
                text=text,
                tables=tables,
                filename=filename,
                ocr_used=ocr_used,
                ocr_confidence=ocr_confidence,
                preferred_profile=preferred_profile
            )
            return [single_rec]

        elif ext in {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp"}:
            if ocr_processor.is_available():
                img = Image.open(io.BytesIO(file_bytes))
                text, ocr_confidence = ocr_processor.extract_text_from_image(img)
                single_rec = self._parse_single_block(
                    text=text,
                    tables=[],
                    filename=filename,
                    ocr_used=True,
                    ocr_confidence=ocr_confidence,
                    preferred_profile=preferred_profile
                )
                return [single_rec]
            else:
                raise RuntimeError(
                    "Uploaded an image marks memo, but Tesseract OCR engine is not configured."
                )
        else:
            raise ValueError(f"Unsupported file format: {ext}")

    def process_file(
        self,
        file_bytes: bytes,
        filename: str,
        preferred_profile: Optional[str] = None
    ) -> Dict[str, Any]:
        """Backward-compatible method returning primary memo record with all_memos list."""
        all_results = self.process_document(file_bytes, filename, preferred_profile)
        if not all_results:
            raise ValueError("No marks memo data could be extracted from document.")
        primary = all_results[0]
        primary["all_memos"] = all_results
        primary["multi_memo_count"] = len(all_results)
        return primary

extraction_engine = ExtractionEngine()
