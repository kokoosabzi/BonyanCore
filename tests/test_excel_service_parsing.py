import io
from datetime import date

import pytest

pd = pytest.importorskip("pandas", reason="pandas is required for Excel parsing tests")
pytest.importorskip("openpyxl", reason="openpyxl is required for Excel parsing tests")

from app.services.excel_service import ExcelService


def _xlsx(rows):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        pd.DataFrame(rows).to_excel(writer, index=False)
    return output.getvalue()


def test_parse_bank_statement_jalali_text_dates_with_persian_digits():
    content = _xlsx([
        {
            "تاریخ": "۱۴۰۴/۰۵/۰۳",
            "شماره حساب": "1234567890",
            "مبلغ (ریال)": "50,000",
            "نوع": "DEPOSIT",
            "شماره مرجع": "REF-1",
            "شرح": "واریز",
        }
    ])

    rows, errors = ExcelService.parse_excel(content, date_calendar="jalali")

    assert errors == []
    assert rows[0]["date"] == date(2025, 7, 25)
    assert rows[0]["amount"] == 50000
    assert rows[0]["reference_no"] == "REF-1"


def test_parse_bank_statement_gregorian_requires_iso_text_dates():
    content = _xlsx([{"تاریخ": "2025/07/25", "مبلغ (ریال)": 50000}])

    rows, errors = ExcelService.parse_excel(content, date_calendar="gregorian")

    assert rows[0]["date"] is None
    assert errors == ["ردیف 2: تاریخ میلادی باید به شکل YYYY-MM-DD باشد"]


def test_parse_bank_statement_gregorian_accepts_iso_text_dates():
    content = _xlsx([{"تاریخ": "2025-07-25", "مبلغ (ریال)": 50000}])

    rows, errors = ExcelService.parse_excel(content, date_calendar="gregorian")

    assert errors == []
    assert rows[0]["date"] == date(2025, 7, 25)


def test_parse_excel_reports_row_level_amount_errors():
    content = _xlsx([{"تاریخ": "1404/05/03", "مبلغ (ریال)": "abc"}])

    rows, errors = ExcelService.parse_excel(content, date_calendar="jalali")

    assert rows[0]["amount"] is None
    assert errors == ["ردیف 2: مبلغ نامعتبر است"]
