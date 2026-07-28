from pydantic import GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema
from typing import Any, Optional
from datetime import date
from app.utils.jalali_date import JalaliDate

class JalaliDateType:
    """نوع Pydantic برای تاریخ شمسی"""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.union_schema([
            core_schema.is_instance_schema(JalaliDate),
            core_schema.str_schema(),
        ], custom_error_type="jalali_date_type")

    @classmethod
    def __get_pydantic_json_schema__(cls, core_schema: CoreSchema, handler: GetJsonSchemaHandler) -> JsonSchemaValue:
        return {"type": "string", "format": "jalali-date", "example": "1404/05/03"}

    @classmethod
    def validate(cls, value: Any) -> Optional[JalaliDate]:
        if value is None:
            return None
        if isinstance(value, JalaliDate):
            return value
        if isinstance(value, str):
            return JalaliDate.from_string(value)
        if isinstance(value, date):
            return JalaliDate.from_gregorian(value)
        raise ValueError(f"Cannot convert {value} to JalaliDate")