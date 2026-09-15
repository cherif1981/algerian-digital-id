"""محرك OCR باستخدام PaddleOCR (بديل أو مكمل)."""
from typing import Dict, List, Optional

import numpy as np

from src.utils.logger import logger

try:
    from paddleocr import PaddleOCR
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    logger.warning("PaddleOCR غير مثبت")


class PaddleOCREngine:
    def __init__(self, lang: str = "ar", use_angle_cls: bool = True):
        if not PADDLE_AVAILABLE:
            raise ImportError("PaddleOCR غير مثبت")
        self.lang = lang
        self.ocr = PaddleOCR(use_angle_cls=use_angle_cls, lang=lang, show_log=False)
        logger.info(f"تهيئة PaddleOCR | اللغة: {lang}")

    def extract_text(self, image: np.ndarray) -> str:
        result = self.ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return ""
        lines = [item[1][0] for item in result[0]]
        return "\n".join(lines)

    def extract_data(self, image: np.ndarray) -> Dict:
        result = self.ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return {"text": "", "words": []}
        words: List[Dict] = []
        for item in result[0]:
            bbox, (text, conf) = item
            words.append({
                "text": text,
                "confidence": float(conf),
                "bbox": bbox,
            })
        return {"text": "\n".join(w["text"] for w in words), "words": words}