from sqlalchemy import Column, BigInteger, DateTime, Boolean, String
from sqlalchemy.sql import func
from app.core.database import Base

class BaseModel(Base):
    __abstract__ = True

    id = Column(BigInteger, primary_key=True, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    deleted_by = Column(String(50), nullable=True)