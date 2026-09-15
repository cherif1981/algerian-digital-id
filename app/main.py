"""واجهة API باستخدام FastAPI."""
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from src.pipelines.inference_pipeline import InferencePipeline
from src.utils.logger import logger

app = FastAPI(
    title="Algerian Digital ID API",
    description="نظام التعرف الضوئي على البطاقة الوطنية الجزائرية",
    version="0.1.0",
)

pipeline = InferencePipeline()


@app.get("/")
async def root():
    return {"app": "Algerian Digital ID", "status": "running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.post("/api/v1/extract")
async def extract(file: UploadFile = File(...)):
    """استخراج البيانات من صورة البطاقة."""
    try:
        contents = await file.read()
        import numpy as np
        import cv2

        arr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(arr, cv2.IMREAD_COLOR)

        if image is None:
            return JSONResponse(
                status_code=400,
                content={"error": "صورة غير صالحة"},
            )

        result = pipeline.run(image)
        return {"success": True, "data": result}
    except Exception as e:
        logger.exception("فشل الاستخراج")
        return JSONResponse(
            status_code=500,
            content={"error": str(e)},
        )