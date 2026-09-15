"""خط أنابيب الاستدلال الكامل: من صورة إلى بيانات منظمة."""
from pathlib import Path
from typing import Dict, Optional

import cv2
import numpy as np

from src.matching.validation import validate_card
from src.ocr.tesseract_engine import TesseractEngine
from src.preprocessing.image_cleaner import clean_image
from src.utils.logger import logger


class InferencePipeline:
    def __init__(self, ocr_engine: Optional[TesseractEngine] = None):
        self.ocr = ocr_engine or TesseractEngine(lang="ara+fra+eng")
        logger.info("تهيئة خط أنابيب الاستدلال")

    def _load_image(self, source) -> np.ndarray:
        if isinstance(source, (str, Path)):
            image = cv2.imread(str(source))
            if image is None:
                raise FileNotFoundError(f"تعذر تحميل الصورة: {source}")
            return image
        if isinstance(source, np.ndarray):
            return source
        raise TypeError("المصدر يجب أن يكون مساراً أو مصفوفة numpy")

    def run(self, source, validate: bool = True) -> Dict:
        """تشغيل خط الأنابيب الكامل."""
        logger.info("بدء معالجة الصورة")
        image = self._load_image(source)
        cleaned = clean_image(image)
        ocr_result = self.ocr.extract_data(cleaned)

        result: Dict = {
            "raw_text": ocr_result["text"],
            "words": ocr_result["words"],
        }

        if validate:
            result["validation"] = validate_card({"nin": ocr_result["text"][:50]})

        logger.info("اكتملت المعالجة")
        return result