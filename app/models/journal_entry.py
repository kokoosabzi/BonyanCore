from sqlalchemy import Column, String, Date, BigInteger, ForeignKey, Text, Enum, DateTime
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class JournalStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"

class JournalEntry(BaseModel):
    __tablename__ = "journal_entries"

    journal_no = Column(String(50), nullable=False, unique=True, index=True)
    journal_date = Column(Date, nullable=False)
    status = Column(Enum(JournalStatus), default=JournalStatus.DRAFT)
    description = Column(Text, nullable=True)
    posted_by = Column(String(50), nullable=True)
    posted_at = Column(DateTime, nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(BigInteger, nullable=True)

    lines = relationship("JournalLine", back_populates="journal")