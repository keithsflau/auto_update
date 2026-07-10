from __future__ import annotations

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from monitor.config import EDB_CIRCULAR_LOOKBACK_DAYS, USER_AGENT
from monitor.models import UpdateItem
from monitor.state import normalize_text

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})

CIRCULAR_BASE = "https://applications.edb.gov.hk/circular/"


def _hidden_fields(html: str) -> dict[str, str]:
    soup = BeautifulSoup(html, "html.parser")
    fields: dict[str, str] = {}
    for tag in soup.select("input[type=hidden]"):
        name = tag.get("name")
        if name:
            fields[name] = tag.get("value", "")
    return fields


def fetch_circular_keyword_html(keyword: str) -> str:
    url = "https://applications.edb.gov.hk/circular/circular.aspx?langno=2"
    html = SESSION.get(url, timeout=60).text
    payload = _hidden_fields(html)
    payload.update(
        {
            "ctl00$MainContentPlaceHolder$ddlSchoolType2": "",
            "ctl00$MainContentPlaceHolder$ddlCircularType": "",
            "ctl00$MainContentPlaceHolder$txtKeyword": keyword,
            "ctl00$MainContentPlaceHolder$txtCircularNumber": "",
            "ctl00$MainContentPlaceHolder$txtPeriodFrom": "",
            "ctl00$MainContentPlaceHolder$txtPeriodTo": "",
            "ctl00$MainContentPlaceHolder$btnSearch2": "搜尋",
        }
    )
    return SESSION.post(url, data=payload, timeout=60).text


def fetch_circular_html(lookback_days: int | None = None) -> str:
    lookback = lookback_days or EDB_CIRCULAR_LOOKBACK_DAYS
    issue_day = "issueDayButton2" if lookback <= 7 else "issueDayButton1"
    url = "https://applications.edb.gov.hk/circular/circular.aspx?langno=2"
    html = SESSION.get(url, timeout=60).text
    payload = _hidden_fields(html)
    payload.update(
        {
            "ctl00$MainContentPlaceHolder$ddlSchoolType": "",
            "ctl00$MainContentPlaceHolder$issueDay": issue_day,
            "ctl00$MainContentPlaceHolder$btnSearch": "搜尋",
        }
    )
    return SESSION.post(url, data=payload, timeout=60).text


def parse_circulars(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[dict] = []
    seen: set[str] = set()

    for row in soup.select("tr"):
        text = row.get_text("\n", strip=True)
        if "EDBC" not in text:
            continue

        number_match = re.search(r"EDBC[MC](\d+)/(\d{4})", text)
        if not number_match:
            continue

        serial, year = number_match.groups()
        item_id = f"EDBC{serial}/{year}"

        if item_id in seen:
            continue
        seen.add(item_id)

        date_match = re.search(r"(\d{2}/\d{2}/\d{4})", text)
        summary_match = re.search(r"摘要：\s*(.+?)(?:學校類別：|$)", text, re.S)
        school_match = re.search(r"學校類別：\s*(.+)$", text, re.S)

        title_cell = row.select_one("td.circularResultRow:nth-of-type(2)")
        title = ""
        if title_cell:
            title_parts = []
            for child in title_cell.stripped_strings:
                if child.startswith("摘要：") or child.startswith("(通告編號"):
                    break
                if child != "主題":
                    title_parts.append(child)
            title = normalize_text(" ".join(title_parts))

        pdf_tag = row.select_one('a[href*="EDBC"][href$=".pdf"]')
        pdf_href = pdf_tag.get("href") if pdf_tag else ""
        url = urljoin(CIRCULAR_BASE, pdf_href) if pdf_href else CIRCULAR_BASE

        items.append(
            {
                "id": item_id,
                "title": title or item_id,
                "date": date_match.group(1) if date_match else "",
                "summary": normalize_text(summary_match.group(1)) if summary_match else "",
                "school_types": normalize_text(school_match.group(1)) if school_match else "",
                "url": url,
                "raw_text": normalize_text(text),
            }
        )

    return items


def fetch_edb_circular_items() -> list[UpdateItem]:
    html = fetch_circular_html()
    return [
        UpdateItem(
            category="edb_circular",
            item_id=item["id"],
            title=item["title"],
            url=item["url"],
            date=item["date"],
            summary=item["summary"] or item["school_types"],
        )
        for item in parse_circulars(html)
    ]
