from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone

from monitor.config import BASE_DIR, CATEGORY_LABELS
from monitor.filters import (
    COMPETITION_TYPE_LABELS,
    LEVEL_LABELS,
    SCHOLARSHIP_TYPE_LABELS,
    TCS_SUBCATEGORY_LABELS,
)
from monitor.models import UpdateItem
from monitor.state import load_state, normalize_text
from monitor.text_util import format_display_date, parse_item_date, within_last_year

DASHBOARD_FILE = BASE_DIR / "data" / "dashboard.json"
LOOKBACK_DAYS = 365


def _subcategory_label(item: UpdateItem) -> str:
    if item.category == "tcs_teacher":
        return TCS_SUBCATEGORY_LABELS.get(item.subcategory, "")
    if item.category == "competition":
        return COMPETITION_TYPE_LABELS.get(item.subcategory, "")
    if item.category == "scholarship":
        return SCHOLARSHIP_TYPE_LABELS.get(item.subcategory, "")
    return ""


def item_to_dict(item: UpdateItem, *, is_new: bool) -> dict:
    title = normalize_text(item.title)
    summary = normalize_text(item.summary)
    date_raw = normalize_text(item.date)
    parsed = parse_item_date(date_raw, title)

    return {
        "id": item.item_id,
        "category": item.category,
        "category_label": CATEGORY_LABELS.get(item.category, item.category),
        "title": title,
        "url": item.url,
        "date": format_display_date(parsed, date_raw),
        "date_raw": date_raw,
        "date_sort": parsed.strftime("%Y-%m-%d") if parsed else "",
        "summary": summary,
        "subcategory": item.subcategory,
        "subcategory_label": _subcategory_label(item),
        "level": item.level,
        "level_label": LEVEL_LABELS.get(item.level, ""),
        "is_new": is_new,
        "fingerprint": item.fingerprint(),
    }


def build_snapshot(
    all_items: list[UpdateItem],
    new_items: list[UpdateItem] | None = None,
) -> dict:
    state = load_state()
    seen = set(state.get("seen", []))
    new_fps = {item.fingerprint() for item in (new_items or [])}
    if not new_items:
        new_fps = {item.fingerprint() for item in all_items if item.fingerprint() not in seen}

    items = [
        item_to_dict(item, is_new=item.fingerprint() in new_fps)
        for item in all_items
    ]

    items = [
        row
        for row in items
        if within_last_year(parse_item_date(row["date_raw"], row["title"]), days=LOOKBACK_DAYS)
    ]

    items.sort(
        key=lambda row: (
            row["date_sort"] or "0000-01-01",
            row["title"],
        ),
        reverse=True,
    )

    counts = Counter(row["category"] for row in items)
    new_counts = Counter(row["category"] for row in items if row["is_new"])

    return {
        "updated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "lookback_days": LOOKBACK_DAYS,
        "total": len(items),
        "new_total": sum(1 for row in items if row["is_new"]),
        "counts": {key: counts.get(key, 0) for key in CATEGORY_LABELS},
        "new_counts": {key: new_counts.get(key, 0) for key in CATEGORY_LABELS},
        "category_labels": CATEGORY_LABELS,
        "items": items,
    }


def save_snapshot(snapshot: dict) -> None:
    DASHBOARD_FILE.parent.mkdir(parents=True, exist_ok=True)
    DASHBOARD_FILE.write_text(
        json.dumps(snapshot, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def load_snapshot() -> dict | None:
    if not DASHBOARD_FILE.exists():
        return None
    return json.loads(DASHBOARD_FILE.read_text(encoding="utf-8"))
