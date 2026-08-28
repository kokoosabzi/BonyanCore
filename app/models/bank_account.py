from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class BankAccount(BaseModel):
    __tablename__ = "bank_accounts"

    bank_id = Column(BigInteger, ForeignKey("banks.id"), nullable=False)
    account_no = Column(String(30), nullable=False)
    sheba = Column(String(30), nullable=True)
    card_no = Column(String(20), nullable=True)
    branch = Column(String(100), nullable=True)
    account_name = Column(String(200), nullable=True)
    currency = Column(String(3), default="IRR")
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    bank = relationship("Bank", back_populates="accounts")
