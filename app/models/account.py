from sqlalchemy import Column, String, Boolean, BigInteger, Text, Enum, ForeignKey
from app.models.base import BaseModel
import enum

class AccountType(str, enum.Enum):
    BANK = "BANK"
    CASH = "CASH"
    TREASURY = "TREASURY"
    MEMBER = "MEMBER"
    PROJECT = "PROJECT"
    SUSPENSE = "SUSPENSE"

class Account(BaseModel):
    __tablename__ = "accounts"

    account_code = Column(String(20), nullable=False, unique=True, index=True)
    account_name = Column(String(200), nullable=False)
    account_type = Column(Enum(AccountType), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)