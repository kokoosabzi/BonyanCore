from sqlalchemy import Column, String, Integer, BigInteger, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.sql import func
from app.models.base import BaseModel

class BulkImportLog(BaseModel):
    __tablename__ = "bulk_import_logs"

    import_type = Column(String(20), nullable=False)  # DEBIT, CREDIT, MEMBER
    project_id = Column(BigInteger, ForeignKey("projects.id"), nullable=True)
    journal_no = Column(String(50), nullable=True)
    total_rows = Column(Integer, default=0)
    total_amount = Column(BigInteger, default=0)
    status = Column(String(20), default="PENDING")  # PENDING, SUCCESS, FAILED
    message = Column(Text, nullable=True)
    errors = Column(Text, nullable=True)  # JSON
    file_name = Column(String(200), nullable=True)
    imported_by = Column(String(50), nullable=True)