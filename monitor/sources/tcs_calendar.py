from __future__ import annotations

import re

import requests
from bs4 import BeautifulSoup

from monitor.config import USER_AGENT
from monitor.filters import classify_tcs_subcategory
from monitor.models import UpdateItem
from monitor.state import normalize_text

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": USER_AGENT})


def _fetch_html(url: str) -> str:
    response = SESSION.get(url, timeout=60)
    response.raise_for_status()
    response.encoding = "utf-8"
    return response.content.decode("utf-8", errors="replace")


def _parse_tcs_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    body = soup.select_one("div.divTableBody")
    if not body:
        return []

    courses: list[dict] = []
    for row in body.select("div.divTableRow"):
        if "head" in (row.get("class") or []):
            continue

        cells = row.select("div.divTableCell")
        if len(cells) < 4:
            continue

        event_date = normalize_text(cells[0].get_text(" ", strip=True))
        course_id_text = normalize_text(cells[1].get_text(" ", strip=True))
        course_id_match = re.match(r"([A-Z0-9]+)", course_id_text)
        if not course_id_match:
            continue
        course_id = course_id_match.group(1)

        title = ""
        title_anchor = cells[3].select_one("a.divTableTitle")
        if title_anchor:
            title_div = title_anchor.select_one("div")
            title_text = title_div.get_text(" ", strip=True) if title_div else title_anchor.get_text(" ", strip=True)
            title_text = normalize_text(title_text)
            embedded = re.match(rf"{re.escape(course_id)}\s+(.+)", title_text)
            title = embedded.group(1) if embedded else title_text
        else:
            title = normalize_text(cells[3].get_text(" ", strip=True))

        if not title:
            continue

        closing_date = normalize_text(cells[5].get_text(" ", strip=True)) if len(cells) > 5 else ""
        date = closing_date.split()[0] if closing_date else event_date

        courses.append(
            {
                "course_id": course_id,
                "title": title,
                "date": date,
                "url": (
                    "https://tcs.edb.gov.hk/tcs/admin/courses/previewCourse/"
                    f"forPortal.htm?courseId={course_id}&lang=zh_TW"
                ),
            }
        )
    return courses


TCS_BASE_URL = (
    "https://tcs.edb.gov.hk/tcs/portal/publiccalendar/searchPublicCal/search.htm"
    "?fromMenu=Y&pdType={pd_type}"
)
TCS_PD_TYPES = ("1", "2")
DIGITAL_EDU_URL = (
    "https://www.edb.gov.hk/tc/edu-system/primary-secondary/"
    "applicable-to-primary-secondary/it-in-edu/pdp-ited.html"
)


def _parse_pdp_ited_html(html: str) -> list[dict]:
    soup = BeautifulSoup(html, "html.parser")
    courses: list[dict] = []
    for row in soup.select("table tr"):
        cells = [normalize_text(cell.get_text(" ", strip=True)) for cell in row.find_all("td")]
        if len(cells) < 2:
            continue
        date_text, title = cells[0], cells[1]
        if not title or title.lower() in {"course title", "課程名稱"}:
            continue
        course_id_match = re.search(r"ITED\d+|QA\d+|CSD\d+", title, re.I)
        course_id = course_id_match.group(0) if course_id_match else title[:40]
        courses.append(
            {
                "course_id": course_id,
                "title": title,
                "date": date_text,
                "url": DIGITAL_EDU_URL,
            }
        )
    return courses


def fetch_tcs_teacher_items() -> list[UpdateItem]:
    items: dict[str, UpdateItem] = {}

    for pd_type in TCS_PD_TYPES:
        try:
            tcs_html = _fetch_html(TCS_BASE_URL.format(pd_type=pd_type))
            for course in _parse_tcs_html(tcs_html):
                items[course["course_id"]] = UpdateItem(
                    category="tcs_teacher",
                    item_id=course["course_id"],
                    title=course["title"],
                    url=course["url"],
                    date=course.get("date", ""),
                    subcategory=classify_tcs_subcategory(course["title"], course["course_id"]),
                )
        except requests.RequestException:
            continue

    try:
        pdp_html = _fetch_html(DIGITAL_EDU_URL)
        for course in _parse_pdp_ited_html(pdp_html):
            items[course["course_id"]] = UpdateItem(
                category="tcs_teacher",
                item_id=course["course_id"],
                title=course["title"],
                url=course["url"],
                date=course.get("date", ""),
                subcategory=classify_tcs_subcategory(course["title"], course["course_id"]),
            )
    except requests.RequestException:
        pass

    return list(items.values())
