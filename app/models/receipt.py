from sqlalchemy import CheckConstraint, Column, String, Date, DateTime, BigInteger, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class PaymentMethod(str, enum.Enum):
    CASH = "CASH"
    CHEQUE = "CHEQUE"
    DEPOSIT_SLIP = "DEPOSIT_SLIP"
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
    project_member_id = Column(BigInteger, ForeignKey("project_members.id"), nullable=True)
    contract_id = Column(BigInteger, ForeignKey("contracts.id"), nullable=True)
    amount = Column(BigInteger, nullable=False)
    amount_in_words = Column(String(500), nullable=False, default="")
    receipt_date = Column(Date, nullable=False)
    payment_method = Column(Enum(PaymentMethod), nullable=False)
    bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=True)
    cheque_no = Column(String(50), nullable=True)
    cheque_due_date = Column(Date, nullable=True)
    bank_name = Column(String(100), nullable=True)
    bank_branch = Column(String(150), nullable=True)
    drawer_name = Column(String(200), nullable=True)
    payee_name = Column(String(200), nullable=True)
    deposit_document_type = Column(String(100), nullable=True)
    depositor_name = Column(String(200), nullable=True)
    reference_no = Column(String(100), nullable=True)
    description = Column(Text, nullable=True)
    status = Column(Enum(ReceiptStatus), default=ReceiptStatus.DRAFT)
    operator_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(DateTime, nullable=True)
    journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"), nullable=True)

    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    project_member = relationship("ProjectMember")
    contract = relationship("Contract")
    bank_account = relationship("BankAccount")
    journal_entry = relationship("JournalEntry")
    financial_credit = relationship(
        "FinancialCredit",
        back_populates="receipt",
        uselist=False,
    )
    allocations = relationship(
        "ReceiptAllocation",
        back_populates="receipt",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_receipt_amount_positive"),
    )
