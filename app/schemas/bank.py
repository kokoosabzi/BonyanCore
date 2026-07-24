from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BankBase(BaseModel):
    bank_name: str
    bank_code: Optional[str] = None
    description: Optional[str] = None

class BankCreate(BankBase):
    pass

class BankUpdate(BaseModel):
    bank_name: Optional[str] = None
    bank_code: Optional[str] = None
    description: Optional[str] = None

class BankResponse(BankBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True