from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import date, datetime

class CustomerBase(BaseModel):
    customer_no: str = Field(..., min_length=6, max_length=6, description="شماره مشتری ۶ رقمی")
    full_name: str = Field(..., max_length=200)
    national_code: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    mobile: Optional[str] = Field(None, max_length=11)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    job: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = "ACTIVE"
    dynamic_data: Optional[str] = None

    @field_validator('customer_no')
    @classmethod
    def validate_customer_no(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError('شماره مشتری باید فقط شامل اعداد باشد')
        return v

    @field_validator('national_code')
    @classmethod
    def validate_national_code(cls, v: Optional[str]) -> Optional[str]:
        if v and not v.isdigit():
            raise ValueError('کد ملی باید فقط شامل اعداد باشد')
        return v

class CustomerCreate(CustomerBase):
    pass

class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=200)
    national_code: Optional[str] = Field(None, max_length=10)
    birth_date: Optional[date] = None
    mobile: Optional[str] = Field(None, max_length=11)
    phone: Optional[str] = Field(None, max_length=20)
    address: Optional[str] = None
    job: Optional[str] = Field(None, max_length=100)
    status: Optional[str] = None
    dynamic_data: Optional[str] = None

class CustomerResponse(CustomerBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True