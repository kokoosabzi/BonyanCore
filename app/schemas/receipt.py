from pydantic import BaseModel
from typing import Optional
from datetime import date, datetime
from enum import Enum

class PaymentMethod(str, Enum):
    CASH = "CASH"
    CHEQUE = "CHEQUE"
    TRANSFER = "TRANSFER"
    POS = "POS"
    OTHER = "OTHER"

class ReceiptStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIRMED = "CONFIRMED"
    CANCELLED = "CANCELLED"

class ReceiptBase(BaseModel):
    customer_id: int
    project_id: int
    contract_id: Optional[int] = None
    amount: int
    receipt_date: date
    payment_method: PaymentMethod
    bank_account_id: Optional[int] = None
    cheque_no: Optional[str] = None
    cheque_due_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[ReceiptStatus] = ReceiptStatus.DRAFT

class ReceiptCreate(ReceiptBase):
    pass

class ReceiptUpdate(BaseModel):
    amount: Optional[int] = None
    receipt_date: Optional[date] = None
    payment_method: Optional[PaymentMethod] = None
    bank_account_id: Optional[int] = None
    cheque_no: Optional[str] = None
    cheque_due_date: Optional[date] = None
    description: Optional[str] = None
    status: Optional[ReceiptStatus] = None

class ReceiptResponse(ReceiptBase):
    id: int
    receipt_no: str
    operator_id: Optional[int] = None
    confirmed_by: Optional[int] = None
    confirmed_at: Optional[date] = None
    journal_entry_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True