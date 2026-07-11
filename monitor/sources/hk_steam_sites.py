from __future__ import annotations

import hashlib
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from monitor.config import USER_AGENT
from monitor.state import normalize_text

SESSION = requests.Session()
SESSION.headers.update(
    {
        "User-Agent": USER_AGENT,
        "Accept-Language": "zh-HK,zh;q=0.9,en;q=0.8",
    }
)

NOISE_TITLE_KEYWORDS = (
    "facebook",
    "instagram",
    "youtube",
    "關於我們",
    "關於協會",
    "簡介",
    "聯絡我們",
    "私隱",
    "版權",
    "訂閱",
    "搜索",
    "about us",
    "contact us",
)

PROGRAMME_LINK_KEYWORDS = (
    "science-fair",
    "steam",
    "比賽",
    "競賽",
    "competition",
    "科學",
    "創新大賽",
    "programmes",
    "programme",
    "活動",
)

# 香港 STEAM/STEM 比賽相關網站（盡量涵蓋）
CURATED_PAGES: list[tuple[str, str, str | None]] = [
    ("https://www.eduai.org/competition", "eduai", None),
    ("https://www.hknetea.org/zh/competitions", "hknetea", None),
    ("https://stic.newgen.org.hk/", "page", "both"),
    ("https://asia-ace.org/steam_6th/", "page", "both"),
    ("https://sic.newgen.org.hk/programmes/", "sic_programmes", None),
    (
        "https://hk.science.museum/tc/web/scm/event/scipop/latest.html",
        "page",
        "both",
    ),
    (
        "https://www.edcity.hk/home/zh-hant/25a/sic/202526/introduction/",
        "page",
        "both",
    ),
    ("https://www.hkforyg.org.hk/tc/programmes/science", "page", "both"),
    ("https://www.hkace.org.hk/", "page", "both"),
    ("https://www.peachcp.com/wro-hk/", "wro_hub", None),
    ("https://www.peachcp.com/wro-hk/hk-selection/wro2026/", "page", "both"),
    ("https://www.peachcp.com/wro-hk/hkrc-w-2026/", "page", "both"),
    ("https://www.peachcp.com/wro-hk/hkrc-s-2026/", "page", "both"),
]


@dataclass(frozen=True)
class HkCompetition:
    title: str
    url: str
    source: str
    date: str = ""
    summary: str = ""
    level_hint: str | None = None  # primary | secondary | both

    @property
    def item_id(self) -> str:
        digest = hashlib.sha1(f"{self.source}|{self.url}|{self.title}".encode()).hexdigest()[:16]
        return f"{self.source}-{digest}"


def _fetch(url: str) -> str:
    response = SESSION.get(url, timeout=25)
    response.raise_for_status()
    return response.text


def _is_noise(title: str, url: str) -> bool:
    blob = f"{title} {url}".lower()
    if len(title) < 4:
        return True
    return any(word in blob for word in NOISE_TITLE_KEYWORDS)


def _parse_eduai(html: str) -> list[HkCompetition]:
    soup = BeautifulSoup(html, "html.parser")
    level: str | None = None
    items: list[HkCompetition] = []

    for element in soup.find_all(["h2", "h3", "table"]):
        if element.name in ("h2", "h3"):
            heading = element.get_text(" ", strip=True)
            if "中學" in heading and "比賽" in heading:
                level = "secondary"
            elif "小學" in heading and "比賽" in heading:
                level = "primary"
            continue

        if element.name != "table" or not level:
            continue

        for row in element.select("tr"):
            link = row.select_one('a[href^="http"]')
            if not link:
                continue
            title = normalize_text(link.get_text(" ", strip=True))
            if _is_noise(title, link["href"]):
                continue

            date = ""
            date_el = row.select_one(".date")
            if date_el:
                date = normalize_text(date_el.get_text(" ", strip=True))
            else:
                for cell in row.select("td"):
                    text = normalize_text(cell.get_text(" ", strip=True))
                    if "年" in text and "月" in text:
                        date = text
                        break

            organiser = ""
            cells = row.select("td")
            if len(cells) >= 3:
                organiser = normalize_text(cells[2].get_text(" ", strip=True))

            items.append(
                HkCompetition(
                    title=title,
                    url=link["href"],
                    source="eduai",
                    date=date,
                    summary=organiser,
                    level_hint=level,
                )
            )

    return _dedupe(items)


def _parse_hknetea(html: str, base_url: str) -> list[HkCompetition]:
    soup = BeautifulSoup(html, "html.parser")
    titles = [
        normalize_text(node.get_text(" ", strip=True))
        for node in soup.select("h2.font_2, h2.wixui-rich-text__text")
        if len(normalize_text(node.get_text(" ", strip=True))) >= 12
    ]

    links: list[str] = []
    seen: set[str] = set()
    for anchor in soup.find_all("a", href=True):
        if "competitions-1/" not in anchor["href"]:
            continue
        link = urljoin(base_url, anchor["href"])
        if link in seen:
            continue
        seen.add(link)
        links.append(link)

    items: list[HkCompetition] = []
    for index, link in enumerate(links):
        title = titles[index] if index < len(titles) else link.rsplit("/", 1)[-1]
        if _is_noise(title, link):
            continue
        items.append(
            HkCompetition(
                title=title,
                url=link,
                source="hknetea",
                level_hint="both",
            )
        )
    return _dedupe(items)


def _parse_page_competition(html: str, url: str, level_hint: str | None) -> list[HkCompetition]:
    soup = BeautifulSoup(html, "html.parser")
    title_node = soup.find("h1") or soup.find("h2")
    if not title_node:
        return []

    title = normalize_text(title_node.get_text(" ", strip=True))
    if _is_noise(title, url):
        return []

    summary = ""
    meta = soup.find("meta", attrs={"name": "description"})
    if meta and meta.get("content"):
        summary = normalize_text(meta["content"])

    date = ""
    for pattern in (
        r"20\d{2}年\d{1,2}月\d{1,2}日",
        r"\d{1,2}/\d{1,2}/20\d{2}",
    ):
        match = re.search(pattern, soup.get_text(" ", strip=True))
        if match:
            date = match.group(0)
            break

    return [
        HkCompetition(
            title=title,
            url=url,
            source="hk-page",
            date=date,
            summary=summary,
            level_hint=level_hint or "both",
        )
    ]


def _parse_wro_hub(html: str, base_url: str) -> list[HkCompetition]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[HkCompetition] = []
    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        if "/wro-hk/" not in href:
            continue
        title = normalize_text(anchor.get_text(" ", strip=True))
        if len(title) < 6:
            continue
        if not any(key in title for key in ("挑戰賽", "選拔賽", "大賽", "WRO", "機械人", "相撲")):
            continue
        if _is_noise(title, href):
            continue
        link = urljoin(base_url, href)
        level = "both"
        if "小學" in title and "中學" not in title:
            level = "primary"
        elif "中學" in title and "小學" not in title:
            level = "secondary"
        items.append(
            HkCompetition(
                title=title,
                url=link,
                source="wro_hk",
                level_hint=level,
            )
        )
    return _dedupe(items)


def _parse_sic_programmes(html: str, base_url: str) -> list[HkCompetition]:
    soup = BeautifulSoup(html, "html.parser")
    items: list[HkCompetition] = []

    for anchor in soup.find_all("a", href=True):
        href = anchor["href"]
        title = normalize_text(anchor.get_text(" ", strip=True))
        if len(title) < 6:
            continue

        blob = f"{title} {href}".lower()
        if not any(keyword in blob for keyword in PROGRAMME_LINK_KEYWORDS):
            continue
        if _is_noise(title, href):
            continue

        link = urljoin(base_url, href)
        items.append(
            HkCompetition(
                title=title,
                url=link,
                source="sic_newgen",
                level_hint="both",
            )
        )

    return _dedupe(items)


def _dedupe(items: list[HkCompetition]) -> list[HkCompetition]:
    seen: set[tuple[str, str]] = set()
    unique: list[HkCompetition] = []
    for item in items:
        key = (item.title.lower(), item.url.rstrip("/").lower())
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _fetch_page_competitions(url: str, parser: str, level_hint: str | None) -> list[HkCompetition]:
    html = _fetch(url)
    if parser == "eduai":
        return _parse_eduai(html)
    if parser == "hknetea":
        return _parse_hknetea(html, url)
    if parser == "sic_programmes":
        return _parse_sic_programmes(html, url)
    if parser == "wro_hub":
        return _parse_wro_hub(html, url)
    return _parse_page_competition(html, url, level_hint)


def fetch_hk_competitions() -> list[HkCompetition]:
    found: dict[str, HkCompetition] = {}

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {
            pool.submit(_fetch_page_competitions, url, parser, level_hint): (url, parser)
            for url, parser, level_hint in CURATED_PAGES
        }
        for future in as_completed(futures):
            try:
                parsed = future.result()
            except requests.RequestException:
                continue
            for item in parsed:
                found[item.item_id] = item

    return list(found.values())
