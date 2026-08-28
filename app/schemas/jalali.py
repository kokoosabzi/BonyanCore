from datetime import date
from typing import Annotated, Any, Optional

from pydantic import BeforeValidator, GetCoreSchemaHandler, GetJsonSchemaHandler
from pydantic.json_schema import JsonSchemaValue
from pydantic_core import CoreSchema, core_schema

from app.utils.jalali import parse_jalali_date, to_jalali
from app.utils.jalali_date import JalaliDate


def parse_date_input(value: Any) -> Optional[date]:
    """Pydantic pre-validator accepting Jalali strings and Python dates."""
    return parse_jalali_date(value)


JalaliDateInput = Annotated[date, BeforeValidator(parse_date_input)]
OptionalJalaliDateInput = Annotated[Optional[date], BeforeValidator(parse_date_input)]


class JalaliDateType:
    """Pydantic custom type for keeping a JalaliDate object in schemas."""

    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, handler: GetCoreSchemaHandler) -> CoreSchema:
        return core_schema.no_info_after_validator_function(
            cls.validate,
            core_schema.union_schema([
                core_schema.is_instance_schema(JalaliDate),
                core_schema.str_schema(),
                core_schema.date_schema(),
            ]),
        )

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


def serialize_jalali(value: date | None) -> str:
    return to_jalali(value)
