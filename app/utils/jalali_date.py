from datetime import date, datetime
import jdatetime
from typing import Optional, Any

class JalaliDate:
    """نوع داده تاریخ شمسی با قابلیت تبدیل به میلادی"""

    def __init__(self, year: int, month: int, day: int):
        self._jalali = jdatetime.date(year, month, day)
        self._gregorian = self._jalali.togregorian()

    @classmethod
    def from_gregorian(cls, gregorian_date: date):
        jd = jdatetime.date.fromgregorian(date=gregorian_date)
        return cls(jd.year, jd.month, jd.day)

    @classmethod
    def from_string(cls, date_str: str):
        parts = date_str.replace('/', '-').split('-')
        if len(parts) == 3:
            return cls(int(parts[0]), int(parts[1]), int(parts[2]))
        raise ValueError(f"Invalid jalali date: {date_str}")

    @classmethod
    def today(cls):
        jd = jdatetime.date.today()
        return cls(jd.year, jd.month, jd.day)

    @property
    def jalali(self) -> jdatetime.date:
        return self._jalali

    @property
    def gregorian(self) -> date:
        return self._gregorian

    def to_string(self, sep: str = '/') -> str:
        return f"{self._jalali.year:04d}{sep}{self._jalali.month:02d}{sep}{self._jalali.day:02d}"

    def __str__(self):
        return self.to_string()

    def __repr__(self):
        return f"JalaliDate('{self.to_string()}')"

    def __eq__(self, other):
        if isinstance(other, JalaliDate):
            return self._gregorian == other._gregorian
        return False

    def __lt__(self, other):
        if isinstance(other, JalaliDate):
            return self._gregorian < other._gregorian
        return NotImplemented