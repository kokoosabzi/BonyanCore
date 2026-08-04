from sqlalchemy import CheckConstraint, Column, String, Date, BigInteger, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class ObligationType(str, enum.Enum):
    PROJECT_PLAN = "PROJECT_PLAN"
    UNIT_DIFFERENCE = "UNIT_DIFFERENCE"
    PENALTY = "PENALTY"
    INCREASE_ADJUSTMENT = "INCREASE_ADJUSTMENT"
    SERVICE_FEE = "SERVICE_FEE"
    OTHER = "OTHER"

class ObligationStatus(str, enum.Enum):
    PENDING = "PENDING"
    PARTIAL = "PARTIAL"
    PAID = "PAID"
    CANCELLED = "CANCELLED"

class FinancialObligation(BaseModel):
    __tablename__ = "financial_obligations"

    obligation_no = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    project_member_id = Column(BigInteger, ForeignKey("project_members.id"), nullable=True)
    contract_id = Column(BigInteger, ForeignKey("contracts.id"), nullable=True)
    obligation_type = Column(Enum(ObligationType), nullable=False)
    amount = Column(BigInteger, nullable=False)
    paid_amount = Column(BigInteger, default=0)
    status = Column(Enum(ObligationStatus), default=ObligationStatus.PENDING)
    due_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)
    journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"), nullable=True)

    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    project_member = relationship("ProjectMember")
    contract = relationship("Contract")
    journal_entry = relationship("JournalEntry")
    allocations = relationship("ReceiptAllocation", back_populates="obligation")

    __table_args__ = (
        CheckConstraint("amount > 0", name="ck_financial_obligation_amount_positive"),
        CheckConstraint(
            "paid_amount >= 0 AND paid_amount <= amount",
            name="ck_financial_obligation_paid_amount",
        ),
    )
