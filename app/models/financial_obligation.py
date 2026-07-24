from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
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
    contract_id = Column(BigInteger, ForeignKey("contracts.id"), nullable=True)
    obligation_type = Column(Enum(ObligationType), nullable=False)
    amount = Column(BigInteger, nullable=False)
    paid_amount = Column(BigInteger, default=0)
    status = Column(Enum(ObligationStatus), default=ObligationStatus.PENDING)
    due_date = Column(Date, nullable=True)
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)

    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    contract = relationship("Contract")