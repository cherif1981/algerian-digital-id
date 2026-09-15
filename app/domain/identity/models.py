from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
from ulid import ULID


class IdentityStatus(str, Enum):
    PENDING = "pending"          # بانتظار التحقق
    ACTIVE = "active"            # مفعّل
    SUSPENDED = "suspended"      # موقوف
    REVOKED = "revoked"          # ملغى


class VerificationLevel(str, Enum):
    """مستويات الثقة (مشابه لـ eIDAS LoA)."""
    LOW = "low"                  # بيانات مستخرجة من OCR فقط
    SUBSTANTIAL = "substantial"  # بيانات مطابقة مع Ministry DB
    HIGH = "high"                # تحقق بيومتري حضوريا


@dataclass
class Person:
    """البيانات الشخصية الأساسية — مفصولة عن البيومترية."""
    first_name_ar: str
    last_name_ar: str
    first_name_fr: str
    last_name_fr: str
    date_of_birth: date
    place_of_birth: str
    gender: str


@dataclass
class Identity:
    """كيان الهوية الرقمية — المصدر الموثوق."""
    identity_id: str = field(default_factory=lambda: str(ULID()))
    nin: Optional[str] = None                    # رقم التعريف الوطني
    person: Optional[Person] = None
    status: IdentityStatus = IdentityStatus.PENDING
    verification_level: VerificationLevel = VerificationLevel.LOW
    enrolled_at: datetime = field(default_factory=datetime.utcnow)
    verified_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    metadata: dict = field(default_factory=dict)  # audit, source, etc.