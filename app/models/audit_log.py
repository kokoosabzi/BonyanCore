from sqlalchemy import BigInteger, Column, DateTime, Integer, JSON, String
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    user_id = Column(BigInteger, nullable=True, index=True)
    username = Column(String(50), nullable=True, index=True)
    ip_address = Column(String(45), nullable=True)
    table_name = Column(String(50), nullable=False, index=True)
    record_id = Column(BigInteger, nullable=False)
    operation = Column(String(20), nullable=False, index=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False, index=True)
    module = Column(String(50), nullable=True, index=True)
