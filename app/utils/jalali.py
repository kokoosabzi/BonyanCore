from datetime import date, datetime
from typing import Optional

import jdatetime

_PERSIAN_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def normalize_date_text(value: str) -> str:
    """Normalize Persian/Arabic digits and common separators in date strings."""
    return value.strip().translate(_PERSIAN_DIGITS).replace("/", "-").replace(".", "-")


def parse_jalali_date(value: str | date | datetime | None) -> Optional[date]:
    """Convert a Jalali date input to Gregorian ``date``.

    Accepted string forms include ``YYYY/MM/DD``, ``YYYY-MM-DD`` and Persian or
    Arabic digits. Empty values return ``None``; invalid values raise
    ``ValueError`` so API callers receive validation feedback instead of a
    silently stored null.
    """
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if not isinstance(value, str):
        raise ValueError("تاریخ باید به صورت رشته یا date ارسال شود")

    parts = normalize_date_text(value).split("-")
    if len(parts) != 3 or not all(part.isdigit() for part in parts):
        raise ValueError("فرمت تاریخ شمسی باید YYYY/MM/DD باشد")

    year, month, day = (int(part) for part in parts)
    try:
        return jdatetime.date(year, month, day).togregorian()
    except ValueError as exc:
        raise ValueError("تاریخ شمسی معتبر نیست") from exc


def to_jalali(dt: date | datetime | None) -> str:
    """Convert a Gregorian date/datetime to a Jalali date string."""
    if not dt:
        return ""
    if isinstance(dt, datetime):
        dt = dt.date()
    jd = jdatetime.date.fromgregorian(date=dt)
    return jd.strftime("%Y/%m/%d")


def to_gregorian(jalali_date: str | date | datetime | None) -> Optional[date]:
    """Backward-compatible alias for converting Jalali input to Gregorian."""
    return parse_jalali_date(jalali_date)


def get_today_jalali() -> str:
    """Return today's date in Jalali format."""
    return jdatetime.date.today().strftime("%Y/%m/%d")


def get_today_gregorian() -> date:
    """Return today's Gregorian date."""
    return date.today()
