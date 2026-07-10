from __future__ import annotations

import re
from typing import Iterable

STEAM_KEYWORDS = (
    r"steam",
    r"stem",
    r"e-steam",
    r"innotech",
    r"創新科技",
    r"編程",
    r"coding",
    r"科學.{0,6}科技",
    r"機械人",
    r"robot",
    r"人工智能",
    r"\bai\b",
    r"創科",
    r"科普",
    r"運算思維",
    r"科技創新",
    r"資訊科技",
)

COMPETITION_KEYWORDS = (
    r"比賽",
    r"競賽",
    r"挑戰賽",
    r"大賽",
    r"competition",
    r"award",
    r"嘉許",
    r"獎勵計劃",
    r"學生活動",
    r"校外活動",
    r"參加.*活動",
    r"卓越獎",
    r"excellence award",
    r"馬拉松",
    r"盃",
    r"錦標賽",
    r"挑戰",
)

PRIMARY_KEYWORDS = (r"小學", r"primary", r"小一", r"幼兒")
SECONDARY_KEYWORDS = (r"中學", r"secondary", r"初中", r"高中", r"中一")

TCS_CORE_KEYWORDS = (
    r"digital education",
    r"數字教育",
    r"電子學習",
    r"\bai\b",
    r"人工智能",
    r"generative ai",
    r"steam",
)

TCS_EXCHANGE_KEYWORDS = (
    r"study tour",
    r"內地.*交流",
    r"交流.*內地",
    r"mainland.*(tour|exchange|visit)",
    r"sgm",
    r"高級學位教師",
    r"晉升.*sgm",
)

TCS_COURSE_ID_PREFIXES = ("ITED", "QA00", "CSD")


def _matches_any(text: str, patterns: Iterable[str]) -> bool:
    lowered = text.lower()
    for pattern in patterns:
        if re.search(pattern, text, re.IGNORECASE) or re.search(pattern, lowered):
            return True
    return False


def is_steam_competition(text: str) -> bool:
    if _matches_any(text, STEAM_KEYWORDS) and _matches_any(text, COMPETITION_KEYWORDS):
        return True
    return bool(
        re.search(r"(e-)?steam.*(比賽|競賽|award|獎|卓越獎)", text, re.IGNORECASE)
    )


def classify_competition(
    title: str,
    summary: str = "",
    school_types: str = "",
    *,
    level_hint: str | None = None,
    trusted_source: bool = False,
) -> list[str]:
    """Classify into steam_primary / steam_secondary."""
    if level_hint == "primary":
        return ["steam_primary"]
    if level_hint == "secondary":
        return ["steam_secondary"]
    if level_hint == "both":
        return ["steam_primary", "steam_secondary"]

    blob = " ".join([title, summary, school_types])
    if not trusted_source and not is_steam_competition(blob):
        return []

    return _split_by_school_level(blob)


def _split_by_school_level(blob: str) -> list[str]:
    primary = is_primary_level(blob)
    secondary = is_secondary_level(blob)

    if primary and not secondary:
        return ["steam_primary"]
    if secondary and not primary:
        return ["steam_secondary"]
    if primary and secondary:
        return ["steam_primary", "steam_secondary"]
    return ["steam_primary", "steam_secondary"]


def is_primary_level(text: str) -> bool:
    return _matches_any(text, PRIMARY_KEYWORDS)


def is_secondary_level(text: str) -> bool:
    return _matches_any(text, SECONDARY_KEYWORDS)


def classify_steam_competition(title: str, summary: str = "", school_types: str = "") -> list[str]:
    blob = " ".join([title, summary, school_types])
    if not is_steam_competition(blob):
        return []
    return _split_by_school_level(blob)


def is_tcs_teacher_course(title: str, course_id: str = "") -> bool:
    blob = f"{course_id} {title}"
    upper_id = course_id.upper()
    if upper_id.startswith(TCS_COURSE_ID_PREFIXES):
        return True
    if _matches_any(blob, TCS_CORE_KEYWORDS):
        return True
    return _matches_any(blob, TCS_EXCHANGE_KEYWORDS)
