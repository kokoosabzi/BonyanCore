from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime
from app.schemas.jalali import JalaliDateInput, OptionalJalaliDateInput
from enum import Enum

class ContractType(str, Enum):
    MEMBERSHIP = "MEMBERSHIP"
    FINAL_UNIT = "FINAL_UNIT"

class ContractStatus(str, Enum):
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"

class ContractBase(BaseModel):
    project_member_id: int
    contract_type: ContractType
    status: Optional[ContractStatus] = ContractStatus.DRAFT
    start_date: JalaliDateInput
    end_date: OptionalJalaliDateInput = None
    unit_id: Optional[int] = None
    final_price: Optional[int] = None
    description: Optional[str] = None
    signed_by: Optional[str] = None
    signed_date: OptionalJalaliDateInput = None

class ContractCreate(ContractBase):
    pass

class ContractUpdate(BaseModel):
    status: Optional[ContractStatus] = None
    end_date: OptionalJalaliDateInput = None
    unit_id: Optional[int] = None
    final_price: Optional[int] = None
    description: Optional[str] = None
    signed_by: Optional[str] = None
    signed_date: OptionalJalaliDateInput = None

class ContractResponse(ContractBase):
    id: int
    contract_no: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True