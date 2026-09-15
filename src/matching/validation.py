"""التحقق من صحة بيانات البطاقة الوطنية الجزائرية."""
import re
from datetime import datetime
from typing import Dict, Tuple


def validate_nin(nin: str) -> Tuple[bool, str]:
    """التحقق من رقم التعريف الوطني (18 رقماً)."""
    cleaned = re.sub(r"\D", "", nin)
    if len(cleaned) == 18:
        return True, cleaned
    return False, "رقم التعريف الوطني يجب أن يكون 18 رقماً"


def validate_date(date_str: str) -> Tuple[bool, str]:
    """التحقق من صيغة التاريخ DD/MM/YYYY."""
    try:
        datetime.strptime(date_str, "%d/%m/%Y")
        return True, date_str
    except ValueError:
        return False, f"تاريخ غير صالح: {date_str}"


def validate_name(name: str) -> Tuple[bool, str]:
    """التحقق من الأسماء (عربي/لاتيني)."""
    cleaned = name.strip()
    if len(cleaned) < 2:
        return False, "الاسم قصير جداً"
    pattern = r"^[\u0600-\u06FFa-zA-Z\s\-']+$"
    if re.match(pattern, cleaned):
        return True, cleaned
    return False, "الاسم يحتوي على رموز غير صالحة"


def validate_card(extracted: Dict[str, str]) -> Dict[str, Dict]:
    """التحقق الشامل للبطاقة."""
    validators = {
        "nin": validate_nin,
        "date_of_birth": validate_date,
        "issue_date": validate_date,
        "expiry_date": validate_date,
        "first_name": validate_name,
        "last_name": validate_name,
    }
    report: Dict[str, Dict] = {}
    for field, validator in validators.items():
        if field in extracted:
            is_valid, result = validator(extracted[field])
            report[field] = {"valid": is_valid, "message": result}
    return report