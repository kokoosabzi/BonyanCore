from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    full_name: str = Field(..., max_length=200)
    phone: Optional[str] = Field(None, max_length=20)

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=72)
    role_id: Optional[int] = None

    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError('رمز عبور نباید بیشتر از ۷۲ بایت باشد')
        return v

class UserLogin(BaseModel):
    username: str
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, max_length=200)
    phone: Optional[str] = Field(None, max_length=20)
    is_active: Optional[bool] = None
    role_id: Optional[int] = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    role_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ChangePassword(BaseModel):
    old_password: str
    new_password: str = Field(..., min_length=6, max_length=72)
    confirm_password: str

    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v.encode("utf-8")) > 72:
            raise ValueError('رمز عبور نباید بیشتر از ۷۲ بایت باشد')
        return v

    @model_validator(mode="after")
    def validate_confirmation(self):
        if self.new_password != self.confirm_password:
            raise ValueError('رمز عبور و تکرار آن مطابقت ندارند')
        return self
