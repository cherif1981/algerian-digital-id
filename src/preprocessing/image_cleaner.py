"""تنظيف الصور وتحسينها قبل OCR."""
import cv2
import numpy as np


def to_grayscale(image: np.ndarray) -> np.ndarray:
    """تحويل الصورة إلى تدرج رمادي."""
    if len(image.shape) == 3:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image


def denoise(image: np.ndarray) -> np.ndarray:
    """إزالة الضوضاء."""
    return cv2.fastNlMeansDenoising(image, h=10)


def binarize(image: np.ndarray, method: str = "otsu") -> np.ndarray:
    """تحويل الصورة إلى أبيض وأسود."""
    if method == "otsu":
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    elif method == "adaptive":
        binary = cv2.adaptiveThreshold(
            image, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
        )
    else:
        raise ValueError(f"طريقة غير مدعومة: {method}")
    return binary


def deskew(image: np.ndarray) -> np.ndarray:
    """تصحيح ميل الصورة."""
    coords = np.column_stack(np.where(image < 128))
    if len(coords) == 0:
        return image
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    return cv2.warpAffine(
        image, matrix, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE
    )


def clean_image(image: np.ndarray, method: str = "otsu") -> np.ndarray:
    """سلسلة التنظيف الكاملة."""
    image = to_grayscale(image)
    image = denoise(image)
    image = binarize(image, method=method)
    image = deskew(image)
    return image