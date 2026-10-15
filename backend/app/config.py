import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = DATA_DIR / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
EXPORT_DIR = DATA_DIR / "exports"
EXPORT_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    APP_NAME: str = "MemoScan AI"
    APP_VERSION: str = "1.0.0"
    MODE: str = os.getenv("MEMOSCAN_MODE", "local")  # "local" or "online"
    
    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{DATA_DIR / 'memoscan.db'}"
    )
    
    # Tesseract configuration
    TESSERACT_CMD: str = os.getenv(
        "TESSERACT_CMD",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe" if os.name == "nt" else "/usr/bin/tesseract"
    )
    
    # File limits
    MAX_FILE_SIZE_BYTES: int = 100 * 1024 * 1024  # 100 MB (supports large batches and zip archives)
    MAX_BATCH_SIZE: int = 200
    ALLOWED_EXTENSIONS: set = {".pdf", ".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".webp", ".zip"}
    
    # Directories
    DATA_PATH: Path = DATA_DIR
    UPLOAD_PATH: Path = UPLOAD_DIR
    EXPORT_PATH: Path = EXPORT_DIR
    
    # CORS
    CORS_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]

settings = Settings()
