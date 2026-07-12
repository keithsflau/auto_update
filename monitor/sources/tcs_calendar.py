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
    courses: list[dict] = []
    for anchor in soup.select("a.divTableTitle"):
        div = anchor.select_one("div")
        if not div:
            continue
        text = normalize_text(div.get_text(" ", strip=True))
        match = re.match(r"([A-Z0-9]+)\s+(.+)", text)
        if not match:
            continue
        course_id, title = match.group(1), match.group(2)
        courses.append(
            {
                "course_id": course_id,
                "title": title,
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
