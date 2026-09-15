from fastapi import APIRouter, UploadFile, File, Depends
from app.api.deps import get_enrollment_service
from app.schemas.enrollment import EnrollmentResponse

router = APIRouter(prefix="/enrollment", tags=["Enrollment"])


@router.post("/from-document", response_model=EnrollmentResponse)
async def enroll_from_document(
    file: UploadFile = File(...),
    service = Depends(get_enrollment_service),
):
    """
    التسجيل من وثيقة:
    1. OCR (Phase 1)
    2. Validation
    3. Ministry verification
    4. Identity creation
    5. VC issuance
    """
    # 1. OCR
    ocr_result = await run_ocr(file)
    # 2. تسجيل
    identity = await service.enroll_from_ocr(ocr_result)
    return EnrollmentResponse(
        identity_id=identity.identity_id,
        status=identity.status.value,
        verification_level=identity.verification_level.value,
    )