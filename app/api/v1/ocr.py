"""Phase 1 — OCR endpoints."""
import cv2
import numpy as np
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from app.api.deps import get_pipeline
from app.core.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/extract")
async def extract(
    file: UploadFile = File(...),
    pipeline = Depends(get_pipeline),
):
    """
    استخراج البيانات من صورة البطاقة (Phase 1).
    متوافق خلفيًا مع v0.1.0.
    """
    try:
        contents = await file.read()
        arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(status_code=400, detail="صورة غير صالحة")

        result = pipeline.run(image)
        return {"success": True, "data": result}

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("ocr.extract_failed")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )