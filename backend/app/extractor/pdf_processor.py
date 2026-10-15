import io
from typing import Dict, Any, List, Tuple
from PIL import Image
import pymupdf as fitz

class PDFProcessor:
    @staticmethod
    def extract_content(file_bytes: bytes) -> Dict[str, Any]:
        """
        Inspects PDF, extracts digital text and tables across all pages,
        and determines if the PDF is scanned or digital.
        """
        try:
            doc = fitz.open(stream=file_bytes, filetype="pdf")
        except Exception as e:
            raise ValueError(f"Could not open PDF file. It may be corrupt or encrypted: {str(e)}")

        if doc.is_encrypted:
            raise ValueError("PDF is password-protected or encrypted. Please provide an unencrypted marks memo.")

        total_pages = len(doc)
        full_text_pages = []
        all_tables = []
        is_scanned_candidate = False
        page_images = []

        pages_detail = []
        for page_idx in range(total_pages):
            page = doc[page_idx]
            page_text = page.get_text("text")
            full_text_pages.append(page_text)

            page_tables = []
            # Table extraction using PyMuPDF's built-in table finder
            try:
                tables = page.find_tables()
                if tables and tables.tables:
                    for tbl in tables.tables:
                        extracted_table = tbl.extract()
                        if extracted_table:
                            all_tables.append(extracted_table)
                            page_tables.append(extracted_table)
            except Exception:
                pass

            # Check if page looks like a scanned document (low word count)
            words = page.get_text("words")
            is_page_scanned = len(words) < 25
            page_img = None
            if is_page_scanned:
                is_scanned_candidate = True
                # Render page image at 300 DPI for high-accuracy OCR
                pix = page.get_pixmap(dpi=300)
                page_img = Image.open(io.BytesIO(pix.tobytes("png")))
                page_images.append(page_img)

            pages_detail.append({
                "page_number": page_idx + 1,
                "text": page_text,
                "tables": page_tables,
                "is_scanned": is_page_scanned,
                "rendered_image": page_img
            })

        combined_text = "\n\n--- Page Break ---\n\n".join(full_text_pages).strip()
        doc.close()

        return {
            "total_pages": total_pages,
            "text": combined_text,
            "tables": all_tables,
            "pages": pages_detail,
            "is_scanned": is_scanned_candidate and (len(combined_text) < 100),
            "rendered_images": page_images
        }
