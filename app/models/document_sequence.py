from sqlalchemy import Column, String, Integer, BigInteger, UniqueConstraint
from app.models.base import BaseModel

class DocumentSequence(BaseModel):
    __tablename__ = "document_sequences"

    prefix = Column(String(10), nullable=False, index=True)
    year = Column(String(2), nullable=False)
    current_number = Column(Integer, default=0)
    description = Column(String(200), nullable=True)

    __table_args__ = (
        UniqueConstraint("prefix", "year", name="uq_document_sequence_prefix_year"),
    )
