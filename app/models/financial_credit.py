from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class CreditType(str, enum.Enum):
    PAYMENT = "PAYMENT"
    LOAN = "LOAN"
    SUBSIDY = "SUBSIDY"
    DISCOUNT = "DISCOUNT"
    DECREASE_ADJUSTMENT = "DECREASE_ADJUSTMENT"
    OTHER = "OTHER"

class CreditStatus(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REVERSED = "REVERSED"

class FinancialCredit(BaseModel):
    __tablename__ = "financial_credits"

    credit_no = Column(String(50), nullable=False, unique=True, index=True)
    customer_id = Column(BigInteger, ForeignKey("customers.id"), nullable=False)
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=False)
    contract_id = Column(BigInteger, ForeignKey("contracts.id"), nullable=True)
    credit_type = Column(Enum(CreditType), nullable=False)
    amount = Column(BigInteger, nullable=False)
    status = Column(Enum(CreditStatus), default=CreditStatus.PENDING)
    credit_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    reference_id = Column(String(100), nullable=True)
    bank_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=True)
    cheque_no = Column(String(50), nullable=True)

    # Relationships
    customer = relationship("Customer")
    project = relationship("Project")
    contract = relationship("Contract")
    bank_account = relationship("BankAccount")