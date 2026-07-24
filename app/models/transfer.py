from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum
from app.models.base import BaseModel
import enum

class TransferStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class Transfer(BaseModel):
    __tablename__ = "transfers"

    transfer_no = Column(String(50), nullable=False, unique=True, index=True)
    from_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=False)
    to_account_id = Column(BigInteger, ForeignKey("bank_accounts.id"), nullable=False)
    amount = Column(BigInteger, nullable=False)
    transfer_date = Column(Date, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TransferStatus), default=TransferStatus.DRAFT)
    operator_id = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_by = Column(BigInteger, ForeignKey("users.id"), nullable=True)
    confirmed_at = Column(Date, nullable=True)
    journal_entry_id = Column(BigInteger, ForeignKey("journal_entries.id"), nullable=True)