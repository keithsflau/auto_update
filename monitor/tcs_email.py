from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from zoneinfo import ZoneInfo

from monitor.config import (
    EMAIL_SMTP_PASSWORD,
    EMAIL_SMTP_USER,
    TCS_DAILY_EMAIL_ENABLED,
    TCS_DAILY_EMAIL_TO,
)
from monitor.filters import TCS_SUBCATEGORY_LABELS
from monitor.models import UpdateItem
from monitor.notify import send_email_to
from monitor.state import log
from monitor.text_util import format_display_date, parse_item_date

HK_TZ = ZoneInfo("Asia/Hong_Kong")

TCS_SUBCATEGORY_ORDER = (
    "steam",
    "ai",
    "admin",
    "self_review",
    "exchange",
    "guidance",
    "promotion",
    "other",
)


def _today_hk() -> str:
    return datetime.now(HK_TZ).strftime("%Y-%m-%d")


def _sort_courses(items: list[UpdateItem]) -> list[UpdateItem]:
    return sorted(
        items,
        key=lambda item: (
            parse_item_date(item.date, item.title) or datetime.min,
            item.title,
        ),
        reverse=True,
    )


def format_tcs_daily_email(
    courses: list[UpdateItem],
    *,
    new_courses: list[UpdateItem],
) -> str:
    today = datetime.now(HK_TZ).strftime("%Y年%m月%d日")
    lines = [
        f"香港教師培訓 (TCS) 每日課程更新 — {today}",
        f"共 {len(courses)} 項課程",
        "",
    ]

    if new_courses:
        lines.append(f"【今日新增 / 更新】（{len(new_courses)} 項）")
        for item in _sort_courses(new_courses):
            label = TCS_SUBCATEGORY_LABELS.get(item.subcategory, "其他")
            date_text = format_display_date(parse_item_date(item.date, item.title), item.date)
            lines.append(f"• [{label}] {item.title}")
            if date_text:
                lines.append(f"  日期：{date_text}")
            if item.url:
                lines.append(f"  連結：{item.url}")
        lines.append("")

    lines.append("【全部課程（按分類）】")
    grouped: dict[str, list[UpdateItem]] = defaultdict(list)
    for item in courses:
        grouped[item.subcategory or "other"].append(item)

    for key in TCS_SUBCATEGORY_ORDER:
        bucket = grouped.get(key)
        if not bucket:
            continue
        label = TCS_SUBCATEGORY_LABELS.get(key, key)
        lines.append("")
        lines.append(f"■ {label}（{len(bucket)} 項）")
        for item in _sort_courses(bucket):
            date_text = format_display_date(parse_item_date(item.date, item.title), item.date)
            suffix = f" | {date_text}" if date_text else ""
            lines.append(f"- {item.title}{suffix}")
            if item.url:
                lines.append(f"  {item.url}")

    return "\n".join(lines)


def maybe_send_tcs_daily_email(
    courses: list[UpdateItem],
    state: dict,
    *,
    dry_run: bool = False,
) -> bool:
    if not TCS_DAILY_EMAIL_ENABLED or not TCS_DAILY_EMAIL_TO:
        return False
    if not EMAIL_SMTP_USER or not EMAIL_SMTP_PASSWORD:
        log("TCS 每日電郵略過：未設定 EMAIL_SMTP_USER / EMAIL_SMTP_PASSWORD")
        return False

    today = _today_hk()
    if state.get("last_tcs_daily_email") == today:
        return False

    previous_fps = set(state.get("tcs_daily_seen", []))
    current_fps = {item.fingerprint() for item in courses}
    new_courses = [item for item in courses if item.fingerprint() not in previous_fps]

    message = format_tcs_daily_email(courses, new_courses=new_courses)
    subject = f"TCS 教師培訓每日更新 — {datetime.now(HK_TZ).strftime('%Y-%m-%d')}"

    if dry_run:
        log(f"[DRY RUN] TCS 每日電郵 → {TCS_DAILY_EMAIL_TO}（{len(courses)} 項，新增 {len(new_courses)} 項）")
        return True

    send_email_to(TCS_DAILY_EMAIL_TO, subject, message)
    log(f"已發送 TCS 每日電郵至 {TCS_DAILY_EMAIL_TO}（{len(courses)} 項，新增 {len(new_courses)} 項）")

    state["last_tcs_daily_email"] = today
    state["tcs_daily_seen"] = sorted(current_fps)
    return True
