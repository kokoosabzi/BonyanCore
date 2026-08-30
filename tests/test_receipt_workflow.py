from datetime import date

import pytest

pytest.importorskip("sqlalchemy")

from sqlalchemy import BigInteger, create_engine
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker

# SQLite only auto-generates primary keys declared as INTEGER, while production
# uses PostgreSQL BigInteger columns. This keeps the integration test portable.
@compiles(BigInteger, "sqlite")
def compile_big_integer_for_sqlite(_type, _compiler, **_kwargs):
    return "INTEGER"

from app.core.database import Base
import app.models  # noqa: F401
from app.models.customer import Customer
from app.models.project import Project
from app.models.receipt import PaymentMethod, ReceiptStatus
from app.models.journal_line import DebitCredit, JournalLine
from app.schemas.receipt import ReceiptCreate, ReceiptUpdate
from app.services.receipt_service import ReceiptService


@pytest.fixture
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    session.add_all([
        Customer(customer_no="C-1", first_name="علی", last_name="رضایی", national_code="001", mobile="09120000000"),
        Project(project_code="P-1", name="پروژه نمونه", start_date=date(2026, 1, 1)),
    ])
    session.commit()
    yield session
    session.close()


def test_confirming_receipt_posts_one_balanced_journal_and_locks_receipt(db):
    receipt = ReceiptService.create(db, ReceiptCreate(
        customer_id=1, project_id=1, amount=500_000, receipt_date="1404/01/15", payment_method=PaymentMethod.CASH,
    ))
    assert receipt.status == ReceiptStatus.DRAFT

    confirmed = ReceiptService.confirm(db, receipt.id)
    assert confirmed.status == ReceiptStatus.CONFIRMED
    assert confirmed.journal_entry_id is not None
    assert confirmed.confirmed_at == date.today()

    lines = db.query(JournalLine).filter(JournalLine.journal_id == confirmed.journal_entry_id).all()
    assert len(lines) == 2
    assert sum(line.amount for line in lines if line.debit_credit == DebitCredit.DEBIT) == 500_000
    assert sum(line.amount for line in lines if line.debit_credit == DebitCredit.CREDIT) == 500_000

    # Confirmation is idempotent and never creates a second accounting entry.
    assert ReceiptService.confirm(db, receipt.id).journal_entry_id == confirmed.journal_entry_id
    assert db.query(JournalLine).count() == 2

    with pytest.raises(ValueError, match="قابل ویرایش نیست"):
        ReceiptService.update(db, receipt.id, ReceiptUpdate(amount=600_000))
    with pytest.raises(ValueError, match="قابل حذف نیست"):
        ReceiptService.delete(db, receipt.id)


def test_cheque_requires_identification_and_posts_to_receivables(db):
    with pytest.raises(ValueError, match="شماره چک"):
        ReceiptService.create(db, ReceiptCreate(
            customer_id=1, project_id=1, amount=50_000, receipt_date="1404/01/15", payment_method=PaymentMethod.CHEQUE,
        ))


def test_ledger_includes_confirmed_receipts_in_member_balance(db):
    from app.models.financial_obligation import FinancialObligation, ObligationType
    from app.services.ledger_service import LedgerService

    db.add(FinancialObligation(
        obligation_no="OBL-1", customer_id=1, project_id=1,
        obligation_type=ObligationType.PROJECT_PLAN, amount=900_000, paid_amount=0,
    ))
    db.commit()
    receipt = ReceiptService.create(db, ReceiptCreate(
        customer_id=1, project_id=1, amount=500_000, receipt_date="1404/01/15", payment_method=PaymentMethod.CASH,
    ))
    ReceiptService.confirm(db, receipt.id)

    entries = LedgerService.get_entries(db, customer_id=1)
    summary = LedgerService.summarize(entries)
    assert {entry["source_type"] for entry in entries} == {"OBLIGATION", "RECEIPT"}
    assert summary["total_obligations"] == 900_000
    assert summary["total_receipts"] == 500_000
    assert summary["net_balance"] == 400_000

    from app.services.report_service import ReportService
    statement = ReportService.get_customer_statement(db, 1)
    assert statement["total_receipts"] == 500_000
    assert statement["net_balance"] == 400_000
