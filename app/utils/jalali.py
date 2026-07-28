import jdatetime
from datetime import date, datetime
from typing import Optional

def to_jalali(dt: date) -> str:
    """تبدیل تاریخ میلادی به شمسی"""
    if not dt:
        return ""
    try:
        jd = jdatetime.date.fromgregorian(date=dt)
        return jd.strftime("%Y/%m/%d")
    except:
        return str(dt)

def to_gregorian(jalali_date: str) -> Optional[date]:
    """تبدیل تاریخ شمسی به میلادی"""
    if not jalali_date:
        return None
    try:
        parts = jalali_date.replace('/', '-').split('-')
        if len(parts) == 3:
            jd = jdatetime.date(int(parts[0]), int(parts[1]), int(parts[2]))
            return jd.togregorian()
    except Exception as e:
        print(f"Error converting date: {e}")
        return None
    return None

def get_today_jalali() -> str:
    """دریافت تاریخ امروز به شمسی"""
    try:
        jd = jdatetime.date.today()
        return jd.strftime("%Y/%m/%d")
    except:
        return ""

def get_today_gregorian() -> date:
    """دریافت تاریخ امروز به میلادی"""
    return date.today()