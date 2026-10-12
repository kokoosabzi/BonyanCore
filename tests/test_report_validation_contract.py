from datetime import date, datetime
import inspect

import pytest

from app.services.report_service import ReportService


def test_report_date_range_rejects_start_after_end():
    with pytest.raises(ValueError, match="شروع"):
        ReportService._validate_date_range(date(2025, 7, 26), date(2025, 7, 25))


def test_report_date_range_rejects_non_date_inputs():
    with pytest.raises(ValueError, match="معتبر نیست"):
        ReportService._validate_date_range("2025-07-25", None)


def test_customer_statement_uses_opening_balance_and_posted_statuses():
    source = inspect.getsource(ReportService.get_customer_statement)
    assert "opening_balance" in source
    assert "ObligationStatus.CANCELLED" in source
    assert "CreditStatus.APPROVED" in source
    assert "FinancialCredit.credit_date" in source


def test_bank_report_counts_confirmed_movements_only():
    source = inspect.getsource(ReportService.get_bank_report)
    assert "ReceiptStatus.CONFIRMED" in source
    assert "PaymentStatus.CONFIRMED" in source
    assert "source_id" in source


def test_report_date_range_rejects_datetime_for_date_only_filters():
    with pytest.raises(ValueError, match="معتبر نیست"):
        ReportService._validate_date_range(datetime(2025, 7, 25, 12, 0), None)
