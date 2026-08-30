from sqlalchemy import BigInteger, Column, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class ReceiptAllocation(BaseModel):
    __tablename__ = "receipt_allocations"
    __table_args__ = (UniqueConstraint("receipt_id", "obligation_id", name="uq_receipt_obligation"),)
    receipt_id = Column(BigInteger, ForeignKey("receipts.id"), nullable=False)
    obligation_id = Column(BigInteger, ForeignKey("financial_obligations.id"), nullable=False)
    allocated_amount = Column(BigInteger, nullable=False)
    allocated_at = Column(Date, nullable=False)
    receipt = relationship("Receipt")
    obligation = relationship("FinancialObligation")
