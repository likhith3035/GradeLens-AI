import os
import shutil
from typing import Dict, Any, Tuple, Optional
import numpy as np
import cv2
from PIL import Image
import pytesseract
from ..config import settings

class OCRProcessor:
    def __init__(self):
        self._tesseract_available = None
        self._configure_tesseract()

    def _configure_tesseract(self):
        """Configure and verify Tesseract OCR binary path."""
        # 1. Check user configured setting or env var
        if os.path.exists(settings.TESSERACT_CMD):
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD
            self._tesseract_available = True
            return

        # 2. Check standard Windows paths if on Windows
        if os.name == "nt":
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                os.path.expandvars(r"%LOCALAPPDATA%\Programs\Tesseract-OCR\tesseract.exe")
            ]
            for p in common_paths:
                if os.path.exists(p):
                    pytesseract.pytesseract.tesseract_cmd = p
                    self._tesseract_available = True
                    return

        # 3. Check system PATH
        if shutil.which("tesseract"):
            pytesseract.pytesseract.tesseract_cmd = "tesseract"
            self._tesseract_available = True
            return

        self._tesseract_available = False

    def is_available(self) -> bool:
        if self._tesseract_available is None:
            self._configure_tesseract()
        return bool(self._tesseract_available)

    def preprocess_image(self, pil_image: Image.Image) -> np.ndarray:
        """
        OpenCV pipeline to enhance text legibility on scanned marks memos:
        - Grayscale conversion
        - Bilateral filter / Gaussian blur to reduce scan noise while preserving text edges
        - Adaptive / Otsu thresholding
        """
        img_np = np.array(pil_image.convert("RGB"))
        gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

        # Contrast enhancement with CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)

        # Bilateral filter for smoothing noise while keeping sharp edges
        denoised = cv2.bilateralFilter(enhanced, 9, 75, 75)

        # Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )

        return thresh

    def extract_text_from_image(self, pil_image: Image.Image) -> Tuple[str, float]:
        """
        Runs Tesseract OCR on a PIL image and returns (extracted_text, average_confidence).
        """
        if not self.is_available():
            raise RuntimeError(
                "Tesseract OCR is not installed or not found at the configured path. "
                "Please configure the Tesseract executable path in Settings or install Tesseract OCR."
            )

        processed = self.preprocess_image(pil_image)

        # Run OCR with detailed data output for confidence scoring
        try:
            data = pytesseract.image_to_data(processed, output_type=pytesseract.Output.DICT)
            text_chunks = []
            confidences = []

            for idx, word in enumerate(data.get("text", [])):
                conf = float(data.get("conf", [0])[idx])
                clean_word = word.strip()
                if clean_word:
                    text_chunks.append(clean_word)
                    if conf > 0:
                        confidences.append(conf)

            full_text = pytesseract.image_to_string(processed)
            avg_conf = (sum(confidences) / len(confidences)) / 100.0 if confidences else 0.5
            return full_text, round(avg_conf, 2)
        except Exception as e:
            raise RuntimeError(f"OCR processing failed: {str(e)}")

ocr_processor = OCRProcessor()
