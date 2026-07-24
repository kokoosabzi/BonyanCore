from sqlalchemy import Column, Integer, BigInteger, String, Date, Boolean, Text, Float, Numeric, Enum, ForeignKey, JSON
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