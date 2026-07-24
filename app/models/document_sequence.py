from sqlalchemy import Column, String, Integer, BigInteger
from app.models.base import BaseModel

class DocumentSequence(BaseModel):
    __tablename__ = "document_sequences"

    prefix = Column(String(10), nullable=False, unique=True, index=True)
    year = Column(String(2), nullable=False)
    current_number = Column(Integer, default=0)
    description = Column(String(200), nullable=True)

    def get_next_number(self) -> str:
        self.current_number += 1
        return f"{self.prefix}-{self.year}-{self.current_number:06d}"