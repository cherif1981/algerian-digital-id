from datetime import datetime
from .models import Identity, Person, IdentityStatus, VerificationLevel
from .store import IdentityStore
from app.infra.external.ministry_client import MinistryClient
from app.domain.credentials.issuer import CredentialIssuer


class EnrollmentService:
    """
    خدمة التسجيل: تأخذ نتيجة OCR (Phase 1) وتنشئ هوية رقمية (Phase 2).
    """

    def __init__(
        self,
        store: IdentityStore,
        ministry: MinistryClient,
        issuer: CredentialIssuer,
    ):
        self.store = store
        self.ministry = ministry
        self.issuer = issuer

    async def enroll_from_ocr(self, ocr_result: dict) -> Identity:
        """
        نقطة الدخول الرئيسية:
        1. استقبال نتيجة OCR
        2. التحقق مع وزارة الداخلية (Source of Truth)
        3. إنشاء Identity في المخزن
        4. إصدار SD-JWT VC للمواطن
        """
        # 1. بناء كيان الهوية المبدئي
        person = Person(
            first_name_ar=ocr_result["first_name_ar"],
            last_name_ar=ocr_result["last_name_ar"],
            first_name_fr=ocr_result["first_name_fr"],
            last_name_fr=ocr_result["last_name_fr"],
            date_of_birth=ocr_result["date_of_birth"],
            place_of_birth=ocr_result["place_of_birth"],
            gender=ocr_result["gender"],
        )

        identity = Identity(
            nin=ocr_result.get("nin"),
            person=person,
            status=IdentityStatus.PENDING,
            verification_level=VerificationLevel.LOW,
        )

        # 2. التحقق مع المصدر الموثوق
        verified = await self.ministry.verify_identity(
            nin=identity.nin, person=person
        )

        if verified:
            identity.status = IdentityStatus.ACTIVE
            identity.verification_level = VerificationLevel.SUBSTANTIAL
            identity.verified_at = datetime.utcnow()

        # 3. حفظ في المخزن
        identity = await self.store.create(identity)

        # 4. إصدار VC (فقط إذا كان التحقق ناجحًا)
        if identity.status == IdentityStatus.ACTIVE:
            vc = await self.issuer.issue_identity_credential(identity)
            identity.metadata["issued_credential_id"] = vc["id"]

        return identity