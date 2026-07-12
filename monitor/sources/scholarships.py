from __future__ import annotations

import re
from datetime import datetime, timedelta

import requests

from monitor.config import USER_AGENT
from monitor.filters import SCHOLARSHIP_TYPE_LABELS, classify_scholarship_level, is_scholarship_opportunity
from monitor.models import UpdateItem
from monitor.sources.hk_opportunity_feeds import SCHOLARSHIP_FEEDS
from monitor.sources.rss_util import fetch_feed_rows
from monitor.state import normalize_text
from monitor.text_util import parse_item_date, strip_html

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

LOOKBACK_DAYS = 365


def _cutoff_date() -> datetime:
    return datetime.now() - timedelta(days=LOOKBACK_DAYS)


def _build_summary(source: str, description: str, media_source: str = "", level: str = "") -> str:
    label = media_source or source
    body = strip_html(description).strip()
    level_label = SCHOLARSHIP_TYPE_LABELS.get(level, "")
    prefix = f"[{label}]"
    if level_label:
        prefix = f"[{label} · {level_label}]"
    if body:
        return f"{prefix} {body[:180]}"
    return prefix


def fetch_scholarship_items() -> list[UpdateItem]:
    found: dict[str, UpdateItem] = {}
    cutoff = _cutoff_date()
    seen_titles: set[str] = set()

    for row in fetch_feed_rows(SESSION, SCHOLARSHIP_FEEDS):
        title = normalize_text(row["title"])
        summary_text = strip_html(row.get("summary", ""))
        blob = f"{title} {summary_text}"
        if not is_scholarship_opportunity(blob):
            continue

        parsed = parse_item_date(row.get("date", ""), title)
        if parsed is not None and parsed < cutoff:
            continue

        dedup_key = re.sub(r"\s+", "", title.lower())[:120]
        if dedup_key in seen_titles:
            continue
        seen_titles.add(dedup_key)

        subcategory = classify_scholarship_level(title, summary_text)
        source = str(row.get("source", ""))
        media_source = str(row.get("media_source", ""))
        summary = _build_summary(source, summary_text, media_source, subcategory)

        item = UpdateItem(
            category="scholarship",
            item_id=row["id"],
            title=title,
            url=row["url"],
            date=row.get("date", ""),
            summary=summary,
            subcategory=subcategory,
        )
        found[item.fingerprint()] = item

    return list(found.values())
