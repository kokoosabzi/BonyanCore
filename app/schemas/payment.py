from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.schemas.jalali import JalaliDateInput

class PaymentCreate(BaseModel):
    project_id: int
    payee_name: str
    amount: int = Field(gt=0)
    payment_date: JalaliDateInput
    bank_account_id: Optional[int] = None
    cheque_no: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None

class PaymentResponse(PaymentCreate):
    id: int
    payment_no: str
    status: str
    journal_entry_id: Optional[int] = None
    created_at: datetime
    class Config: from_attributes = True
