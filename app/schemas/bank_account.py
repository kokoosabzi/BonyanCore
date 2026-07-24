from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BankAccountBase(BaseModel):
    bank_id: int
    account_no: str
    sheba: Optional[str] = None
    card_no: Optional[str] = None
    branch: Optional[str] = None
    account_name: Optional[str] = None
    currency: Optional[str] = "IRR"
    description: Optional[str] = None

class BankAccountCreate(BankAccountBase):
    pass

class BankAccountUpdate(BaseModel):
    account_no: Optional[str] = None
    sheba: Optional[str] = None
    card_no: Optional[str] = None
    branch: Optional[str] = None
    account_name: Optional[str] = None
    currency: Optional[str] = None
    description: Optional[str] = None

class BankAccountResponse(BankAccountBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True