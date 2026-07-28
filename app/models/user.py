from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class User(BaseModel):
    __tablename__ = "users"

    username = Column(String(50), nullable=False, unique=True, index=True)
    email = Column(String(100), nullable=True, unique=True)
    full_name = Column(String(200), nullable=False)
    hashed_password = Column(String(200), nullable=False)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime, nullable=True)
    phone = Column(String(20), nullable=True)
    role_id = Column(BigInteger, ForeignKey("roles.id"), nullable=True)
    role = relationship("Role", back_populates="users")
