from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime
from app.schemas.jalali import JalaliDateInput, OptionalJalaliDateInput
from enum import Enum

class ChequeStatus(str, Enum):
    AVAILABLE = "AVAILABLE"
    USED = "USED"
    CANCELLED = "CANCELLED"

class ChequeBase(BaseModel):
    cheque_no: str = Field(..., max_length=20)
    amount: Optional[int] = None
    due_date: OptionalJalaliDateInput = None
    payee: Optional[str] = Field(None, max_length=200)
    status: Optional[ChequeStatus] = ChequeStatus.AVAILABLE
    description: Optional[str] = None

class ChequeCreate(ChequeBase):
    pass

class ChequeResponse(ChequeBase):
    id: int
    cheque_book_id: int
    receipt_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ChequeBookBase(BaseModel):
    bank_account_id: int
    serial_no: str = Field(..., max_length=20)
    serial_number: str = Field(..., max_length=20)
    total_pages: int = Field(..., gt=0)
    min_pages: Optional[int] = 0
    title: Optional[str] = Field(None, max_length=200)
    receive_date: OptionalJalaliDateInput = None
    signatories: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None

class ChequeBookCreate(ChequeBookBase):
    cheques: List[ChequeCreate] = Field(default_factory=list)

class ChequeBookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=200)
    receive_date: OptionalJalaliDateInput = None
    signatories: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    status: Optional[str] = None

class ChequeBookResponse(ChequeBookBase):
    id: int
    status: str
    created_at: datetime
    updated_at: datetime
    cheques: List[ChequeResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True