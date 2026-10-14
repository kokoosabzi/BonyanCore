from datetime import date

import pytest

pytest.importorskip("jdatetime")

from app.utils.jalali import parse_jalali_date


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1404/05/03", date(2025, 7, 25)),
        ("۱۴۰۴/۰۵/۰۳", date(2025, 7, 25)),
        ("1404-05-03", date(2025, 7, 25)),
    ],
)
def test_parse_jalali_date_accepts_supported_formats(value, expected):
    assert parse_jalali_date(value) == expected


def test_parse_jalali_date_rejects_invalid_calendar_date():
    with pytest.raises(ValueError, match="معتبر نیست"):
        parse_jalali_date("1404/13/01")
