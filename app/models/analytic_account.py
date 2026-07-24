from sqlalchemy import Column, String, Boolean, BigInteger, ForeignKey, Text
from app.models.base import BaseModel

class AnalyticAccount(BaseModel):
    __tablename__ = "analytic_accounts"

    code = Column(String(20), nullable=False, unique=True, index=True)
    name = Column(String(200), nullable=False)
    parent_id = Column(BigInteger, ForeignKey("analytic_accounts.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    description = Column(Text, nullable=True)
    reference_type = Column(String(50), nullable=True)
    reference_id = Column(BigInteger, nullable=True)