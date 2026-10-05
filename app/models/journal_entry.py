from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class JournalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"

class JournalEntryType(str, enum.Enum):
    GENERAL = "GENERAL"
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"
    ADJUSTMENT = "ADJUSTMENT"
    RECEIPT = "RECEIPT"
    PAYMENT = "PAYMENT"
    TRANSFER = "TRANSFER"
    REVERSAL = "REVERSAL"

class JournalEntry(BaseModel):
    __tablename__ = "journal_entries"

    journal_no = Column(String(50), nullable=False, unique=True, index=True)
    journal_date = Column(Date, nullable=False)
    entry_type = Column(
        Enum(JournalEntryType),
        nullable=False,
        default=JournalEntryType.GENERAL,
    )
    status = Column(Enum(JournalStatus), default=JournalStatus.DRAFT)
    description = Column(Text, nullable=True)
    posted_by = Column(String(50), nullable=True)
    posted_at = Column(DateTime, nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(BigInteger, nullable=True)

    lines = relationship(
        "JournalLine",
        back_populates="journal",
        cascade="all, delete-orphan",
    )
