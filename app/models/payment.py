from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
from app.models.base import BaseModel
import enum

class PaymentStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Payment(BaseModel):
    __tablename__ = "payments"

    payment_no = Column(String(50), nullable=False, unique=True, index=True)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    payee_name = Column(String(200), nullable=False)
    amount = Column(BigInteger, nullable=False)
    payment_date = Column(Date, nullable=False)
    bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=True)
    cheque_no = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(PaymentStatus), default=PaymentStatus.DRAFT)
    operator_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(Date, nullable=True)
    journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"), nullable=True)
    category = Column(String(50), nullable=True)