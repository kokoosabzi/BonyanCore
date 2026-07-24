from sqlalchemy import Column, String, DateTime, BigInteger, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=True)
    username = Column(String(50), nullable=True)
    ip_address = Column(String(45), nullable=True)
    table_name = Column(String(50), nullable=False)
    record_id = Column(BigInteger, nullable=False)
    operation = Column(String(20), nullable=False)  # CREATE, UPDATE, DELETE, SOFT_DELETE
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    module = Column(String(50), nullable=True)