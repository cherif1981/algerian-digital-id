from src.matching.validation import validate_date, validate_name, validate_nin


def test_validate_nin_valid():
    is_valid, _ = validate_nin("123456789012345678")
    assert is_valid


def test_validate_nin_invalid():
    is_valid, _ = validate_nin("123")
    assert not is_valid


def test_validate_date_valid():
    is_valid, _ = validate_date("15/06/1990")
    assert is_valid


def test_validate_date_invalid():
    is_valid, _ = validate_date("32/13/2020")
    assert not is_valid


def test_validate_name_valid():
    is_valid, _ = validate_name("محمد")
    assert is_valid


def test_validate_name_too_short():
    is_valid, _ = validate_name("م")
    assert not is_valid