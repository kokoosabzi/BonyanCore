from sqlalchemy import Column, String, Boolean, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Bank(BaseModel):
    __tablename__ = "banks"

    bank_name = Column(String(100), nullable=False)
    bank_code = Column(String(10), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    accounts = relationship("BankAccount", back_populates="bank")
