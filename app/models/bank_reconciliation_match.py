from sqlalchemy import BigInteger, Boolean, Column, Date, ForeignKey, String, UniqueConstraint
from app.models.base import BaseModel

class BankReconciliationMatch(BaseModel):
    __tablename__ = "bank_reconciliation_matches"
    __table_args__ = (UniqueConstraint("bank_statement_id", name="uq_bank_statement_match"),)
    bank_statement_id = Column(BigInteger, ForeignKey("bank_statements.id"), nullable=False)
    source_type = Column(String(30), nullable=False)
    source_id = Column(BigInteger, nullable=False)
    matched_at = Column(Date, nullable=False)
    is_confirmed = Column(Boolean, default=False, nullable=False)
