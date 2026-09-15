from typing import Optional


class MinistryClient:
    """
    واجهة مزوّد المصدر الموثوق (وزارة الداخلية).
    في الإنتاج: REST/SOAP API + mTLS + توقيع متبادل.
    في التطوير: mock.
    """

    async def verify_identity(self, nin: str, person) -> bool:
        # TODO: استبدال بـ API حقيقي
        # - مقارنة fuzzy على الأسماء (عربي/فرنسي)
        # - مقارنة تاريخ الميلاد
        # - التحقق من تطابق NIN
        return False  # mock