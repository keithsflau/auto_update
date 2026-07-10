from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from monitor.config import USER_AGENT
from monitor.models import UpdateItem
from monitor.state import normalize_text

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

QEF_PAGES = {
    "press": "https://www.qef.org.hk/tc/aboutus/press_releases.php",
    "consultation": "https://www.qef.org.hk/tc/contactus/consultation_sessions.php",
    "activities": "https://www.qef.org.hk/tc/promotion_dissemination_act/activities.php",
}


def _parse_table_rows(html: str, page_key: str) -> list[UpdateItem]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[UpdateItem] = []

    for row in soup.select("table tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        date_text = normalize_text(cells[0].get_text(" ", strip=True))
        content_cell = cells[1]
        link = content_cell.find("a", href=True)
        title = normalize_text(link.get_text(" ", strip=True) if link else content_cell.get_text(" ", strip=True))
        if not title:
            continue

        url = ""
        if link:
            href = link["href"]
            if href.startswith("http"):
                url = href
            else:
                url = f"https://www.qef.org.hk/tc/{href.lstrip('/')}"

        item_id = f"{page_key}-{re.sub(r'[^0-9]+', '', date_text) or 'nodate'}-{title[:40]}"
        items.append(
            UpdateItem(
                category="qef",
                item_id=item_id,
                title=title,
                url=url or QEF_PAGES[page_key],
                date=date_text,
            )
        )

    return items


def fetch_qef_items() -> list[UpdateItem]:
    found: dict[str, UpdateItem] = {}

    for page_key, url in QEF_PAGES.items():
        try:
            html = SESSION.get(url, timeout=60).text
            for item in _parse_table_rows(html, page_key):
                found[item.fingerprint()] = item
        except requests.RequestException:
            continue

    return list(found.values())
