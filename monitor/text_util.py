from __future__ import annotations

import html
import re
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime

MOJIBAKE_MARKERS = ("æ", "å", "ä", "Ã", "â€", "ï¼", "è", "é")


def strip_html(text: str) -> str:
    if not text:
        return ""

    cleaned = re.sub(r"(?is)<(script|style)\b.*?>.*?</\1>", " ", text)
    cleaned = re.sub(r"(?s)<[^>]+>", " ", cleaned)
    cleaned = html.unescape(cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return fix_mojibake(cleaned)


def fix_mojibake(text: str) -> str:
    if not text:
        return text

    if re.search(r"[\u4e00-\u9fff]", text) and not any(marker in text for marker in MOJIBAKE_MARKERS[:4]):
        return text

    for encoding in ("latin-1", "cp1252"):
        try:
            fixed = text.encode(encoding).decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            continue
        if re.search(r"[\u4e00-\u9fff]", fixed):
            return fixed
    return text


def parse_item_date(date_text: str = "", title: str = "") -> datetime | None:
    for source in (date_text, title):
        if not source:
            continue

        parsed = _parse_one_date(source)
        if parsed:
            return parsed
    return None


def _parse_one_date(text: str) -> datetime | None:
    text = text.strip()

    match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", text)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    match = re.search(r"(\d{4})年(\d{1,2})月", text)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), 1)

    match = re.search(r"(\d{2})/(\d{2})/(\d{4})", text)
    if match:
        return datetime(int(match.group(3)), int(match.group(2)), int(match.group(1)))

    match = re.search(r"(\d{4})-(\d{2})-(\d{2})", text)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    match = re.search(r"(\d{4})/(\d{2})/(\d{2})", text)
    if match:
        return datetime(int(match.group(1)), int(match.group(2)), int(match.group(3)))

    match = re.search(r"(20\d{2})年", text)
    if match:
        return datetime(int(match.group(1)), 1, 1)

    if re.search(r"[A-Za-z]{3},", text):
        try:
            return parsedate_to_datetime(text).replace(tzinfo=None)
        except (TypeError, ValueError, IndexError):
            pass

    return None


def within_last_year(parsed: datetime | None, *, days: int = 365) -> bool:
    if parsed is None:
        return False
    cutoff = datetime.now() - timedelta(days=days)
    return parsed >= cutoff


def format_display_date(parsed: datetime | None, raw: str = "") -> str:
    if parsed:
        return parsed.strftime("%Y年%m月%d日")
    return raw
