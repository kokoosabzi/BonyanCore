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

def test_customer_statement_uses_full_obligation_amount_as_debit():
    source = inspect.getsource(ReportService.get_customer_statement)
    assert '"debit": obligation.amount,' in source
    assert '"debit": obligation.amount - (obligation.paid_amount or 0),' not in source

def test_project_summary_uses_full_obligations_and_approved_credits():
    source = inspect.getsource(ReportService.get_project_financial_summary)
    assert "total_obligation = sum(o.amount for o in obligations)" in source
    assert "FinancialCredit.status == CreditStatus.APPROVED" in source

def test_customer_statement_balance_matches_obligation_and_payment_ledger():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.core.database import Base
    from app.models import Customer, FinancialObligation, FinancialCredit
    from app.models.financial_obligation import ObligationStatus, ObligationType
    from app.models.financial_credit import CreditStatus, CreditType

    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as db:
        customer = Customer(customer_no="000101", full_name="Test Customer")
        db.add(customer)
        db.flush()

        db.add(FinancialObligation(
            obligation_no="OBL-TEST-1",
            customer_id=customer.id,
            project_id=1,
            obligation_type=ObligationType.PROJECT_PLAN,
            amount=100,
            paid_amount=40,
            status=ObligationStatus.PARTIAL,
            due_date=date(2025, 7, 25),
            description="Test obligation",
        ))
        db.add(FinancialCredit(
            credit_no="CR-TEST-1",
            customer_id=customer.id,
            project_id=1,
            credit_type=CreditType.PAYMENT,
            amount=40,
            status=CreditStatus.APPROVED,
            credit_date=date(2025, 7, 25),
            description="Partial payment",
        ))
        db.commit()

        statement = ReportService.get_customer_statement(db, customer.id)

        assert statement["total_obligations"] == 100
        assert statement["total_credits"] == 40
        assert statement["period_balance"] == 60
        assert statement["net_balance"] == 60
        assert statement["total_debit"] == 100
        assert statement["total_credit"] == 40
        assert [item["balance"] for item in statement["transactions"]] == [100, 60]

    engine.dispose()
