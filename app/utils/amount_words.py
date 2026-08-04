_ONES = [
    "",
    "یک",
    "دو",
    "سه",
    "چهار",
    "پنج",
    "شش",
    "هفت",
    "هشت",
    "نه",
]
_TEENS = [
    "ده",
    "یازده",
    "دوازده",
    "سیزده",
    "چهارده",
    "پانزده",
    "شانزده",
    "هفده",
    "هجده",
    "نوزده",
]
_TENS = [
    "",
    "",
    "بیست",
    "سی",
    "چهل",
    "پنجاه",
    "شصت",
    "هفتاد",
    "هشتاد",
    "نود",
]
_HUNDREDS = [
    "",
    "یکصد",
    "دویست",
    "سیصد",
    "چهارصد",
    "پانصد",
    "ششصد",
    "هفتصد",
    "هشتصد",
    "نهصد",
]
_SCALES = ["", "هزار", "میلیون", "میلیارد", "تریلیون", "کوادریلیون"]


def _under_thousand(value: int) -> str:
    parts: list[str] = []
    hundreds, remainder = divmod(value, 100)
    if hundreds:
        parts.append(_HUNDREDS[hundreds])
    if 10 <= remainder <= 19:
        parts.append(_TEENS[remainder - 10])
    else:
        tens, ones = divmod(remainder, 10)
        if tens:
            parts.append(_TENS[tens])
        if ones:
            parts.append(_ONES[ones])
    return " و ".join(parts)


def number_to_persian_words(value: int) -> str:
    if not isinstance(value, int):
        raise TypeError("value must be an integer")
    if value == 0:
        return "صفر"
    if value < 0:
        return f"منفی {number_to_persian_words(abs(value))}"

    groups: list[str] = []
    scale_index = 0
    while value:
        value, group = divmod(value, 1000)
        if group:
            words = _under_thousand(group)
            scale = _SCALES[scale_index]
            groups.append(f"{words} {scale}".strip())
        scale_index += 1
        if scale_index >= len(_SCALES) and value:
            raise ValueError("amount is too large")
    return " و ".join(reversed(groups))


def amount_in_words(value: int, currency: str = "ریال") -> str:
    return f"{number_to_persian_words(value)} {currency}"
