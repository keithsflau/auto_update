from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

import requests

from monitor.config import USER_AGENT
from monitor.filters import classify_news_levels
from monitor.models import UpdateItem
from monitor.state import normalize_text
from monitor.text_util import parse_item_date

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

RSS_FEEDS = (
    "https://www.edb.gov.hk/tc/press_release_rss.xml",
    "https://www.edb.gov.hk/tc/whats_new_rss.xml",
)


def news_cutoff_date() -> datetime:
    today = datetime.now()
    first_of_this_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (first_of_this_month - timedelta(days=1)).replace(day=1)
    retention_start = today - timedelta(days=365)
    return max(last_month_start, retention_start)


def _parse_rss_items(xml_text: str, *, feed_key: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return []

    items: list[dict] = []
    for node in channel.findall("item"):
        title = normalize_text(node.findtext("title") or "")
        link = (node.findtext("link") or "").strip()
        pub_date = normalize_text(node.findtext("pubDate") or "")
        guid = (node.findtext("guid") or link or title).strip()
        if not title:
            continue
        item_id = re.sub(r"[^a-zA-Z0-9_-]+", "-", guid)[-120:]
        items.append(
            {
                "id": f"{feed_key}-{item_id}",
                "title": title,
                "url": link,
                "date": pub_date,
                "summary": normalize_text(node.findtext("description") or ""),
            }
        )
    return items


def fetch_edb_news_items() -> list[UpdateItem]:
    cutoff = news_cutoff_date()
    raw_items: dict[str, dict] = {}

    for index, feed_url in enumerate(RSS_FEEDS):
        feed_key = "press" if "press_release" in feed_url else "whatsnew"
        try:
            response = SESSION.get(feed_url, timeout=60)
            response.raise_for_status()
            for row in _parse_rss_items(response.content, feed_key=feed_key):
                raw_items[row["id"]] = row
        except (requests.RequestException, ET.ParseError):
            continue

    found: dict[str, UpdateItem] = {}
    for row in raw_items.values():
        parsed = parse_item_date(row["date"], row["title"])
        if parsed is None or parsed < cutoff:
            continue

        for category in classify_news_levels(row["title"], row["summary"]):
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
