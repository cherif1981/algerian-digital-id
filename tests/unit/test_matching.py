from src.matching.fuzzy_match import match_field


def test_match_field_exact():
    matched, score = match_field("محمد", ["محمد", "أحمد"], threshold=80)
    assert matched == "محمد"
    assert score == 100.0


def test_match_field_fuzzy():
    matched, score = match_field("محمد", ["محمذ"], threshold=60)
    assert score > 0


def test_match_field_empty():
    matched, score = match_field("", ["محمد"])
    assert matched == ""
    assert score == 0.0