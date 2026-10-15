import re
import os
from pathlib import Path
from typing import Tuple, Any
from ..config import settings

SAFE_FILENAME_RE = re.compile(r'[^a-zA-Z0-9_\-\.]')

def sanitize_filename(filename: str) -> str:
    """Strip dangerous characters and directory traversal sequences."""
    base = os.path.basename(filename)
    clean = SAFE_FILENAME_RE.sub('_', base)
    if not clean or clean.startswith('.'):
        clean = f"memo_{clean.lstrip('.')}"
    return clean

def validate_uploaded_file(filename: str, content_length: int) -> Tuple[bool, str]:
    """Validate file extension and size constraints."""
    ext = Path(filename).suffix.lower()
    if ext not in settings.ALLOWED_EXTENSIONS:
        return False, f"Unsupported file extension '{ext}'. Allowed: {', '.join(sorted(settings.ALLOWED_EXTENSIONS))}"
    
    if content_length > settings.MAX_FILE_SIZE_BYTES:
        max_mb = settings.MAX_FILE_SIZE_BYTES // (1024 * 1024)
        return False, f"File size exceeds maximum permitted limit ({max_mb} MB)."
        
    return True, ""

def escape_excel_formula(value: Any) -> Any:
    """
    Prevent Spreadsheet Formula Injection (CSV / Excel Injection).
    If a cell value starts with =, +, -, @, \\t, \\r, prepend an apostrophe.
    """
    if isinstance(value, str):
        if value and value[0] in ('=', '+', '-', '@', '\t', '\r'):
            return f"'{value}"
    return value
