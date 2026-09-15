"""محرك OCR باستخدام Tesseract."""
from typing import Dict, List, Optional

import numpy as np
import pytesseract
from pytesseract import Output

from src.utils.config import get_env
from src.utils.logger import logger

pytesseract.pytesseract.tesseract_cmd = get_env("TESSERACT_CMD", "tesseract")


class TesseractEngine:
    def __init__(self, lang: str = "ara+fra+eng", config: str = ""):
        self.lang = lang
        self.config = config
        logger.info(f"تهيئة Tesseract | اللغة: {lang}")

    def extract_text(self, image: np.ndarray) -> str:
        """استخراج النص الكامل."""
        return pytesseract.image_to_string(image, lang=self.lang, config=self.config)

    def extract_data(self, image: np.ndarray) -> Dict:
        """استخراج النص مع الإحداثيات ودرجة الثقة."""
        data = pytesseract.image_to_data(
            image, lang=self.lang, output_type=Output.DICT
        )
        results: List[Dict] = []
        for i, text in enumerate(data["text"]):
            if text.strip():
                results.append({
                    "text": text,
                    "confidence": float(data["conf"][i]),
                    "bbox": (
                        data["left"][i], data["top"][i],
                        data["width"][i], data["height"][i],
                    ),
                })
        return {"text": self.extract_text(image), "words": results}