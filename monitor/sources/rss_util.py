from __future__ import annotations

import hashlib
import re
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

from monitor.state import log, normalize_text
from monitor.text_util import strip_html

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}


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


def split_google_news_title(title: str) -> tuple[str, str]:
    match = re.match(r"^(.*)\s+-\s+([^\-]+)$", title)
    if match:
        return normalize_text(match.group(1)), normalize_text(match.group(2))
    return title, ""


def parse_feed_items(xml_bytes: bytes, *, feed_key: str) -> list[dict]:
    root = ET.fromstring(xml_bytes)
    nodes = root.findall(".//item")
    if not nodes:
        nodes = root.findall(".//atom:entry", ATOM_NS)

    items: list[dict] = []
    for node in nodes:
        title = normalize_text(strip_html(_child_text(node, "title")))
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
        description = strip_html(
            _child_text(node, "description") or _child_text(node, "summary")
        )
        if not title:
            continue

        title, media_source = split_google_news_title(title)
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


def fetch_feed_rows(
    session: requests.Session,
    feeds: tuple[dict[str, str], ...],
    *,
    timeout: int = 20,
    workers: int = 10,
) -> list[dict]:
    feed_by_key = {str(feed["key"]): feed for feed in feeds}
    rows: list[dict] = []

    def _fetch_one(feed: dict) -> tuple[str, list[dict]]:
        feed_key = str(feed["key"])
        url = str(feed["url"])
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return feed_key, parse_feed_items(response.content, feed_key=feed_key)
        except (requests.RequestException, ET.ParseError) as exc:
            log(f"RSS 來源 {feed_key} 跳過: {exc.__class__.__name__}")
            return feed_key, []

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(_fetch_one, feed) for feed in feeds]
        for future in as_completed(futures):
            feed_key, parsed = future.result()
            feed = feed_by_key[feed_key]
            source = str(feed["source"])
            for row in parsed:
                row["source"] = source
                row["feed_key"] = feed_key
                rows.append(row)
    return rows
