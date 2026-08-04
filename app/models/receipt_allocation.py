from sqlalchemy import BigInteger, CheckConstraint, Column, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ReceiptAllocation(BaseModel):
    __tablename__ = "receipt_allocations"

    receipt_id = Column(BigInteger, ForeignKey("receipts.id"), nullable=False)
    obligation_id = Column(
        BigInteger,
        ForeignKey("financial_obligations.id"),
        nullable=False,
    )
    amount = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=True)

    receipt = relationship("Receipt", back_populates="allocations")
    obligation = relationship("FinancialObligation", back_populates="allocations")

    __table_args__ = (
        UniqueConstraint(
            "receipt_id",
            "obligation_id",
            name="uq_receipt_allocation_receipt_obligation",
        ),
        CheckConstraint("amount > 0", name="ck_receipt_allocation_amount_positive"),
    )
