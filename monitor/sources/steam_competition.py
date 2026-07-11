from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from monitor.config import USER_AGENT
from monitor.filters import classify_competition
from monitor.models import UpdateItem
from monitor.sources.edb_circular import (
    fetch_circular_html,
    fetch_circular_keyword_html,
    parse_circulars,
)
from monitor.sources.hk_steam_sites import fetch_hk_competitions

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

RSS_URL = "https://www.edb.gov.hk/tc/whats_new_rss.xml"

EDB_SEARCH_KEYWORDS = (
    "STEAM",
    "STEM",
    "比賽",
    "競賽",
    "創新大賽",
    "科學比賽",
    "機械人",
    "編程",
    "人工智能",
    "學生活動",
)


def _parse_rss_items(xml_text: str) -> list[dict]:
    root = ET.fromstring(xml_text)
    channel = root.find("channel")
    if channel is None:
        return []

    items: list[dict] = []
    for node in channel.findall("item"):
        title = (node.findtext("title") or "").strip()
        link = (node.findtext("link") or "").strip()
        pub_date = (node.findtext("pubDate") or node.findtext("guid") or "").strip()
        guid = (node.findtext("guid") or link or title).strip()
        items.append(
            {
                "id": guid,
                "title": title,
                "url": link,
                "date": pub_date,
                "summary": title,
                "school_types": "",
            }
        )
    return items


def _fetch_circular_html_safe(fetcher) -> str | None:
    try:
        return fetcher()
    except requests.RequestException:
        return None


def _collect_circulars() -> list[dict]:
    merged: dict[str, dict] = {}
    fetchers = [fetch_circular_html, *[lambda kw=kw: fetch_circular_keyword_html(kw) for kw in EDB_SEARCH_KEYWORDS]]
    html_sources: list[str] = []

    with ThreadPoolExecutor(max_workers=6) as pool:
        futures = [pool.submit(_fetch_circular_html_safe, fetcher) for fetcher in fetchers]
        for future in as_completed(futures):
            html = future.result()
            if html:
                html_sources.append(html)

    for html in html_sources:
        for circular in parse_circulars(html):
            merged[circular["id"]] = circular
    return list(merged.values())


def _add_item(
    found: dict[str, UpdateItem],
    *,
    category: str,
    item_id: str,
    title: str,
    url: str,
    date: str = "",
    summary: str = "",
) -> None:
    key = f"{category}:{item_id}"
    found[key] = UpdateItem(
        category=category,
        item_id=item_id,
        title=title,
        url=url,
        date=date,
        summary=summary,
    )


def fetch_steam_competition_items() -> list[UpdateItem]:
    found: dict[str, UpdateItem] = {}

    # 1) 香港網站：eduai、hknetea、新一代文化協會等
    for comp in fetch_hk_competitions():
        for category in classify_competition(
            comp.title,
            comp.summary,
            level_hint=comp.level_hint,
            trusted_source=True,
        ):
            _add_item(
                found,
                category=category,
                item_id=comp.item_id,
                title=comp.title,
                url=comp.url,
                date=comp.date,
                summary=comp.summary or comp.source,
            )

    # 2) 教育局通函
    for circular in _collect_circulars():
        for category in classify_competition(
            circular["title"],
            circular["summary"],
            circular["school_types"],
        ):
            _add_item(
                found,
                category=category,
                item_id=circular["id"],
                title=circular["title"],
                url=circular["url"],
                date=circular["date"],
                summary=circular["summary"],
            )

    # 3) 教育局最新消息 RSS
    try:
        rss_xml = SESSION.get(RSS_URL, timeout=30).text
        for item in _parse_rss_items(rss_xml):
            for category in classify_competition(item["title"], item["summary"]):
                rss_id = f"rss-{re.sub(r'[^a-zA-Z0-9_-]+', '-', item['id'])[:80]}"
                _add_item(
                    found,
                    category=category,
                    item_id=rss_id,
                    title=item["title"],
                    url=item["url"],
                    date=item["date"],
                    summary=item["summary"],
                )
    except requests.RequestException:
        pass

    return list(found.values())
