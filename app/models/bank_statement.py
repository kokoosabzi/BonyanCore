from sqlalchemy import Column, Integer, BigInteger, String, Date, Boolean, Text, Float, Numeric, Enum, ForeignKey, JSON, UniqueConstraint
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
    balance = Column(BigInteger, nullable=True)  # مانده بعد از تراکنش
    reference_no = Column(String(50), nullable=True)  # شماره مرجع بانکی
    is_reconciled = Column(Boolean, default=False)
    import_batch_id = Column(String(50), nullable=True)  # شناسه دسته Import

# اتصال قطعی رکورد صورت‌حساب به سند سیستم پس از تأیید دستی.
BankStatement.receipt_id = Column(BigInteger, ForeignKey("receipts.id"), nullable=True)
BankStatement.payment_id = Column(BigInteger, ForeignKey("payments.id"), nullable=True)
BankStatement.__table_args__ = (
    UniqueConstraint("receipt_id", name="uq_bank_statement_receipt"),
    UniqueConstraint("payment_id", name="uq_bank_statement_payment"),
)
