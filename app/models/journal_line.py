from sqlalchemy import Column, String, BigInteger, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
import enum

class DebitCredit(str, enum.Enum):
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"

class JournalLine(BaseModel):
    __tablename__ = "journal_lines"

    journal_id = Column(BigInteger, ForeignKey("journal_entries.id"), nullable=False)
    account_id = Column(BigInteger, ForeignKey("accounts.id"), nullable=False)
    debit_credit = Column(Enum(DebitCredit), nullable=False)
    amount = Column(BigInteger, nullable=False)
    description = Column(Text, nullable=True)
    analytic_account_id = Column(BigInteger, ForeignKey("analytic_accounts.id"), nullable=True)

    journal = relationship("JournalEntry", back_populates="lines")
    account = relationship("Account")
    analytic_account = relationship("AnalyticAccount")