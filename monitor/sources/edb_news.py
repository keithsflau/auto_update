from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests

from monitor.filters import classify_news_levels, is_education_news
from monitor.models import UpdateItem
from monitor.sources.hk_media_feeds import HK_MEDIA_FEEDS
from monitor.state import normalize_text
from monitor.text_util import parse_item_date

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
    }
)

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


def news_cutoff_date() -> datetime:
    today = datetime.now()
    first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (first_of_this_month - timedelta(days=1)).replace(day=1)
    retention_start = today - timedelta(days=365)
    return max(last_month_start, retention_start)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _child_text(node: ET.Element, name: str) -> str:
    for child in node:
        if _local_name(child.tag) == name:
            return (child.text or "").strip()
    return ""


def _child_attr(node: ET.Element, name: str, attr: str) -> str:
    for child in node:
        if _local_name(child.tag) == name:
            return (child.attrib.get(attr) or "").strip()
    return ""


def _parse_feed_items(xml_bytes: bytes, *, feed_key: str) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    nodes = root.findall(".//item")
    if not nodes:
        nodes = root.findall(".//atom:entry", ATOM_NS)

    items: list[dict] = []
    for node in nodes:
        title = normalize_text(_child_text(node, "title"))
        link = _child_text(node, "link")
        if not link:
            link = _child_attr(node, "link", "href")
        pub_date = normalize_text(
            _child_text(node, "pubDate")
            or _child_text(node, "published")
            or _child_text(node, "updated")
        )
        guid = (
            _child_text(node, "guid")
            or _child_text(node, "id")
            or link
            or title
        ).strip()
        description = normalize_text(
            _child_text(node, "description") or _child_text(node, "summary")
        )
        if not title:
            continue

        title, media_source = _split_google_news_title(title)
        item_id = hashlib.sha1(f"{feed_key}:{guid}".encode("utf-8")).hexdigest()[:20]
        items.append(
            {
                "id": f"{feed_key}-{item_id}",
                "title": title,
                "url": link,
                "date": pub_date,
                "summary": description,
                "media_source": media_source,
            }
        )
    return items


def _split_google_news_title(title: str) -> tuple[str, str]:
    match = re.match(r"^(.*)\s+-\s+([^\-]+)$", title)
    if match:
        return normalize_text(match.group(1)), normalize_text(match.group(2))
    return title, ""


def _build_summary(source: str, description: str, media_source: str = "") -> str:
    label = media_source or source
    body = description.strip()
    if body:
        return f"[{label}] {body[:300]}"
    return f"[{label}]"


def fetch_edb_news_items() -> list[UpdateItem]:
    cutoff = news_cutoff_date()
    raw_items: dict[str, dict] = {}

    for feed in HK_MEDIA_FEEDS:
        feed_key = str(feed["key"])
        source = str(feed["source"])
        url = str(feed["url"])
        education_only = bool(feed.get("education_only", False))

        try:
            response = SESSION.get(url, timeout=60)
            response.raise_for_status()
            rows = _parse_feed_items(response.content, feed_key=feed_key)
        except (requests.RequestException, ET.ParseError):
            continue

        for row in rows:
            blob = f"{row['title']} {row['summary']}"
            if education_only and not is_education_news(blob):
                continue

            row["source"] = source
            row["level_hint"] = str(feed.get("level_hint") or "")
            row["include_general"] = bool(feed.get("include_general", False))
            row["summary"] = _build_summary(source, row["summary"], row.get("media_source", ""))
            raw_items[row["id"]] = row

    found: dict[str, UpdateItem] = {}
    seen_titles: set[str] = set()
    for row in raw_items.values():
        parsed = parse_item_date(row["date"], row["title"])
        if parsed is None or parsed < cutoff:
            continue

        dedup_key = re.sub(r"\s+", "", row["title"].lower())[:120]
        if dedup_key in seen_titles:
            continue
        seen_titles.add(dedup_key)

        for category in classify_news_levels(
            row["title"],
            row["summary"],
            level_hint=row.get("level_hint") or None,
            include_general=bool(row.get("include_general")),
        ):
            item = UpdateItem(
                category=category,
                item_id=row["id"],
                title=row["title"],
                url=row["url"],
                date=row["date"],
                summary=row["summary"],
            )
            found[item.fingerprint()] = item

    return list(found.values())
