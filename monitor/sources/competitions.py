from __future__ import annotations

import re
from datetime import datetime, timedelta

import requests

from monitor.config import USER_AGENT
from monitor.filters import LEVEL_LABELS, classify_competition_type, classify_school_level, is_student_competition
from monitor.models import UpdateItem
from monitor.sources.hk_opportunity_feeds import COMPETITION_FEEDS
from monitor.sources.hk_steam_sites import fetch_hk_competitions
from monitor.sources.rss_util import fetch_feed_rows
from monitor.sources.steam_competition import _collect_circulars, _parse_rss_items
from monitor.state import normalize_text
from monitor.text_util import parse_item_date, strip_html

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

RSS_URL = "https://www.edb.gov.hk/tc/whats_new_rss.xml"
LOOKBACK_DAYS = 365


def _cutoff_date() -> datetime:
    return datetime.now() - timedelta(days=LOOKBACK_DAYS)


def _build_summary(source: str, description: str, media_source: str = "", level: str = "") -> str:
    label = media_source or source
    body = strip_html(description).strip()
    level_label = LEVEL_LABELS.get(level, "")
    prefix = f"[{label}]"
    if level_label:
        prefix = f"[{label} · {level_label}]"
    if body:
        return f"{prefix} {body[:180]}"
    return prefix


def _add_item(
    found: dict[str, UpdateItem],
    *,
    item_id: str,
    title: str,
    url: str,
    date: str = "",
    summary: str = "",
    subcategory: str = "general",
    level: str = "",
) -> None:
    item = UpdateItem(
        category="competition",
        item_id=item_id,
        title=title,
        url=url,
        date=date,
        summary=summary,
        subcategory=subcategory,
        level=level,
    )
    found[item.fingerprint()] = item


def fetch_competition_items() -> list[UpdateItem]:
    found: dict[str, UpdateItem] = {}
    cutoff = _cutoff_date()
    seen_titles: set[str] = set()

    def _accept(
        *,
        item_id: str,
        title: str,
        url: str,
        date: str,
        summary: str,
        subcategory: str,
        level: str,
        trusted_source: bool = False,
    ) -> None:
        blob = f"{title} {summary}"
        if not is_student_competition(blob, trusted_source=trusted_source):
            return

        parsed = parse_item_date(date, title)
        if parsed is not None and parsed < cutoff:
            return

        dedup_key = re.sub(r"\s+", "", title.lower())[:120]
        if dedup_key in seen_titles:
            return
        seen_titles.add(dedup_key)

        if not subcategory:
            subcategory = classify_competition_type(title, summary)
        if not level:
            level = classify_school_level(title, summary)

        _add_item(
            found,
            item_id=item_id,
            title=title,
            url=url,
            date=date,
            summary=summary,
            subcategory=subcategory,
            level=level,
        )

    for comp in fetch_hk_competitions():
        level = comp.level_hint or classify_school_level(comp.title, comp.summary)
        subcategory = classify_competition_type(comp.title, comp.summary)
        _accept(
            item_id=comp.item_id,
            title=comp.title,
            url=comp.url,
            date=comp.date,
            summary=comp.summary or comp.source,
            subcategory=subcategory,
            level=level if level in {"primary", "secondary", "both"} else "",
            trusted_source=True,
        )

    for circular in _collect_circulars():
        blob = f"{circular['title']} {circular['summary']}"
        if not is_student_competition(blob):
            continue
        _accept(
            item_id=circular["id"],
            title=circular["title"],
            url=circular["url"],
            date=circular["date"],
            summary=circular["summary"],
            subcategory=classify_competition_type(circular["title"], circular["summary"]),
            level=classify_school_level(
                circular["title"],
                circular["summary"],
                circular.get("school_types", ""),
            ),
            trusted_source=True,
        )

    try:
        rss_xml = SESSION.get(RSS_URL, timeout=30).text
        for item in _parse_rss_items(rss_xml):
            rss_id = f"rss-{re.sub(r'[^a-zA-Z0-9_-]+', '-', item['id'])[:80]}"
            _accept(
                item_id=rss_id,
                title=item["title"],
                url=item["url"],
                date=item["date"],
                summary=item["summary"],
                subcategory=classify_competition_type(item["title"], item["summary"]),
                level=classify_school_level(item["title"], item["summary"]),
            )
    except requests.RequestException:
        pass

    for row in fetch_feed_rows(SESSION, COMPETITION_FEEDS):
        source = str(row.get("source", ""))
        media_source = str(row.get("media_source", ""))
        level = classify_school_level(row["title"], row.get("summary", ""))
        subcategory = classify_competition_type(row["title"], row.get("summary", ""))
        summary = _build_summary(source, row.get("summary", ""), media_source, level)
        _accept(
            item_id=row["id"],
            title=normalize_text(row["title"]),
            url=row["url"],
            date=row.get("date", ""),
            summary=summary,
            subcategory=subcategory,
            level=level,
        )

    return list(found.values())
