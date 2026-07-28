from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, datetime
from enum import Enum

class JournalStatus(str, Enum):
    DRAFT = "DRAFT"
    POSTED = "POSTED"
    CANCELLED = "CANCELLED"

class JournalLineBase(BaseModel):
    account_id: int
    debit: Optional[int] = None
    credit: Optional[int] = None
    description: Optional[str] = None
    analytic_account_id: Optional[int] = None

class JournalLineCreate(JournalLineBase):
    pass

class JournalLineResponse(JournalLineBase):
    id: int
    journal_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JournalEntryBase(BaseModel):
    journal_date: str = Field(..., description="تاریخ سند به شمسی (مثال: 1404/05/03)")
    status: Optional[JournalStatus] = JournalStatus.DRAFT
    description: Optional[str] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None

    @field_validator('journal_date')
    @classmethod
    def validate_jalali_date(cls, v: str) -> str:
        """اعتبارسنجی ساده تاریخ شمسی"""
        import re
        if not re.match(r'^\d{4}/\d{2}/\d{2}$', v):
            raise ValueError('فرمت تاریخ باید YYYY/MM/DD باشد')
        return v

class JournalEntryCreate(JournalEntryBase):
    lines: List[JournalLineCreate] = Field(default_factory=list)

class JournalEntryUpdate(BaseModel):
    journal_date: Optional[str] = None
    status: Optional[JournalStatus] = None
    description: Optional[str] = None

class JournalEntryResponse(JournalEntryBase):
    id: int
    journal_no: str
    created_at: datetime
    updated_at: datetime
    lines: List[JournalLineResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True