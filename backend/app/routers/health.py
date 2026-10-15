from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..database import get_db
from ..config import settings
from ..extractor.ocr_processor import ocr_processor
from ..extractor.registry import parser_registry

router = APIRouter(prefix="/api/health", tags=["Health & Status"])

@router.get("")
def check_health(db: Session = Depends(get_db)):
    db_ok = False
    try:
        db.execute(text("SELECT 1"))
        db_ok = True
    except Exception:
        db_ok = False

    tesseract_ok = ocr_processor.is_available()

    return {
        "status": "healthy" if db_ok else "degraded",
        "app_name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": settings.MODE,
        "database_connected": db_ok,
        "tesseract_ocr_available": tesseract_ok,
        "tesseract_path": settings.TESSERACT_CMD,
        "registered_parsers": parser_registry.list_available_parsers()
    }
