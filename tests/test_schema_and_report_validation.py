from datetime import date
import inspect

import pytest


pytest.importorskip("pydantic")
pytest.importorskip("sqlalchemy")

from pydantic import ValidationError

from app.schemas.bulk_import import BulkImportRow
from app.services.report_service import ReportService


def test_bulk_import_row_converts_jalali_spreadsheet_date():
    row = BulkImportRow(member_no="010001", date="۱۴۰۴/۰۵/۰۳")
    assert row.date == date(2025, 7, 25)


def test_bulk_import_row_rejects_invalid_jalali_spreadsheet_date():
    with pytest.raises(ValidationError):
        BulkImportRow(member_no="010001", date="1404/13/01")


def test_report_date_range_is_validated_in_service_layer():
    with pytest.raises(ValueError, match="شروع"):
        ReportService._validate_date_range(date(2025, 7, 26), date(2025, 7, 25))

    with pytest.raises(ValueError, match="معتبر نیست"):
        ReportService._validate_date_range("2025-07-25", None)


def test_customer_statement_source_uses_opening_balance_and_posted_statuses():
    source = inspect.getsource(ReportService.get_customer_statement)
    assert "opening_balance" in source
    assert "opening_debit" in source
    assert "opening_credit" in source
    assert "ObligationStatus.CANCELLED" in source
    assert "CreditStatus.APPROVED" in source


def test_bank_report_and_reconciliation_source_require_confirmed_movements():
    assert "ReceiptStatus.CONFIRMED" in inspect.getsource(ReportService.get_bank_report)
    assert "PaymentStatus.CONFIRMED" in inspect.getsource(ReportService.get_bank_report)

    source = inspect.getsource(ReportService.get_bank_reconciliation)
    assert "order_by" in source
    assert "matched_count" in source
    assert "system_unmatched" in source
    assert "bank_unmatched" in source
