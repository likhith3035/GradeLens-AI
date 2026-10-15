import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import text

from ..database import get_db, Base, engine
from ..config import settings
from ..extractor.ocr_processor import ocr_processor

router = APIRouter(prefix="/api/settings", tags=["Application Settings"])

@router.get("")
def get_app_settings():
    return {
        "mode": settings.MODE,
        "app_name": settings.APP_NAME,
        "app_version": settings.APP_VERSION,
        "tesseract_cmd": settings.TESSERACT_CMD,
        "tesseract_available": ocr_processor.is_available(),
        "max_file_size_mb": settings.MAX_FILE_SIZE_BYTES // (1024 * 1024),
        "max_batch_size": settings.MAX_BATCH_SIZE,
        "database_url": "sqlite:///data/memoscan.db" if "sqlite" in settings.DATABASE_URL else "PostgreSQL / Supabase Persistent DB"
    }

@router.post("/mode")
def update_mode(mode: str = Body(..., embed=True)):
    if mode not in ("local", "online"):
        raise HTTPException(status_code=400, detail="Mode must be either 'local' or 'online'.")
    settings.MODE = mode
    return {"message": f"Operating mode switched to '{mode}'.", "mode": settings.MODE}

@router.post("/tesseract-path")
def update_tesseract_path(path: str = Body(..., embed=True)):
    if not os.path.exists(path):
        raise HTTPException(status_code=400, detail=f"The specified path does not exist on this machine: {path}")
    
    settings.TESSERACT_CMD = path
    ocr_processor._configure_tesseract()
    available = ocr_processor.is_available()
    
    return {
        "message": "Tesseract path updated successfully." if available else "Path saved but Tesseract executable failed test.",
        "path": settings.TESSERACT_CMD,
        "is_available": available
    }

@router.post("/purge-data")
def purge_all_data(confirm: bool = Body(..., embed=True), db: Session = Depends(get_db)):
    """User-controlled full data deletion for privacy and retention control."""
    if not confirm:
        raise HTTPException(status_code=400, detail="Confirmation required to purge records.")

    # Drop and recreate all tables
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # Clean up uploaded files
    for f in settings.UPLOAD_PATH.glob("*"):
        try:
            if f.is_file():
                f.unlink()
        except Exception:
            pass

    # Clean up exported files
    if hasattr(settings, "EXPORT_PATH") and settings.EXPORT_PATH.exists():
        for f in settings.EXPORT_PATH.glob("*"):
            try:
                if f.is_file():
                    f.unlink()
            except Exception:
                pass

    return {"message": "All database records, recent processing documents, and uploaded files have been safely purged."}

