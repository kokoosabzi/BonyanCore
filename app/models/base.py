from sqlalchemy import Column, BigInteger, DateTime, Boolean, String, Integer
from sqlalchemy.sql import func
from app.core.database import Base

class BaseModel(Base):
    __abstract__ = True

    # SQLite needs INTEGER for implicit autoincrement; PostgreSQL keeps BIGINT.
    id = Column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        index=True,
        autoincrement=True,
    )
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(DateTime, nullable=True)
    is_deleted = Column(Boolean, default=False)
    created_by = Column(String(50), nullable=True)
    updated_by = Column(String(50), nullable=True)
    deleted_by = Column(String(50), nullable=True)
