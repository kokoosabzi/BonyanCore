from sqlalchemy import Column, BigInteger, String, Date, Boolean, Text, Enum, ForeignKey, UniqueConstraint
from app.models.base import BaseModel
import enum


class StatementType(str, enum.Enum):
    DEPOSIT = "DEPOSIT"
    WITHDRAWAL = "WITHDRAWAL"


class BankStatement(BaseModel):
    __tablename__ = "bank_statements"

    bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=False)
    statement_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    amount = Column(BigInteger, nullable=False)
    statement_type = Column(Enum(StatementType), nullable=False)
    balance = Column(BigInteger, nullable=True)
    reference_no = Column(String(50), nullable=True)
    is_reconciled = Column(Boolean, default=False, nullable=False)
    import_batch_id = Column(String(50), nullable=True)

    # اتصال قطعی رکورد صورت‌حساب به سند سیستم پس از تأیید دستی.
    receipt_id = Column(BigInteger, ForeignKey("receipts.id"), nullable=True)
    payment_id = Column(BigInteger, ForeignKey("payments.id"), nullable=True)

    __table_args__ = (
        UniqueConstraint("receipt_id", name="uq_bank_statement_receipt"),
        UniqueConstraint("payment_id", name="uq_bank_statement_payment"),
    )
