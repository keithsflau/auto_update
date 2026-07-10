from __future__ import annotations

import json
from collections import Counter
from datetime import datetime, timezone

from monitor.config import BASE_DIR, CATEGORY_LABELS
from monitor.models import UpdateItem
from monitor.state import load_state

DASHBOARD_FILE = BASE_DIR / "data" / "dashboard.json"


def item_to_dict(item: UpdateItem, *, is_new: bool) -> dict:
    return {
        "id": item.item_id,
        "category": item.category,
        "category_label": CATEGORY_LABELS.get(item.category, item.category),
        "title": item.title,
        "url": item.url,
        "date": item.date,
        "summary": item.summary,
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
        for item in sorted(all_items, key=lambda x: (not (x.fingerprint() in new_fps), x.title))
    ]
    # new items first
    items.sort(key=lambda row: (not row["is_new"], row["title"]))

    counts = Counter(row["category"] for row in items)
    new_counts = Counter(row["category"] for row in items if row["is_new"])

    return {
        "updated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
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
