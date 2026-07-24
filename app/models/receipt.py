from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CHEQUE = "CHEQUE"
    TRANSFER = "TRANSFER"
    POS = "POS"
    OTHER = "OTHER"

class ReceiptStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Receipt(BaseModel):
    __tablename__ = "receipts"

    receipt_no = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    contract_id = Column(BigInteger, ForeignKey("contracts.id"), nullable=True)
    amount = Column(BigInteger, nullable=False)
    receipt_date = Column(Date, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=True)
    cheque_no = Column(String(50), nullable=True)
    cheque_due_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.DRAFT)
    operator_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(Date, nullable=True)
    journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"), nullable=True)

    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    contract = relationship("Contract")
    bank_account = relationship("BankAccount")