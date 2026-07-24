from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UnitBase(BaseModel):
    unit_code: str
    project_id: int
    building: Optional[str] = None
    floor: Optional[int] = None
    unit_number: str
    area: Optional[float] = None
    price: Optional[int] = None
    status: Optional[str] = "AVAILABLE"

class UnitCreate(UnitBase):
    pass

class UnitUpdate(BaseModel):
    unit_code: Optional[str] = None
    building: Optional[str] = None
    floor: Optional[int] = None
    unit_number: Optional[str] = None
    area: Optional[float] = None
    price: Optional[int] = None
    status: Optional[str] = None

class UnitResponse(UnitBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True