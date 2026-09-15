"""مطابقة الحقول النصية مع بيانات مرجعية."""
from typing import Dict, List, Tuple
from rapidfuzz import fuzz, process


def match_field(value: str, candidates: List[str], threshold: int = 70) -> Tuple[str, float]:
    """إيجاد أفضل مطابقة لحقل واحد."""
    if not candidates or not value:
        return "", 0.0
    result = process.extractOne(value, candidates, scorer=fuzz.WRatio)
    if result and result[1] >= threshold:
        return result[0], float(result[1])
    return "", 0.0


def match_record(extracted: Dict[str, str], reference: Dict[str, str],
                 threshold: int = 70) -> Dict[str, Dict]:
    """مطابقة سجل كامل مع سجل مرجعي."""
    report: Dict[str, Dict] = {}
    for field, value in extracted.items():
        if field in reference:
            matched, score = match_field(value, [reference[field]], threshold)
            report[field] = {
                "extracted": value,
                "reference": reference[field],
                "match": matched,
                "score": score,
                "is_valid": bool(matched),
            }
    return report