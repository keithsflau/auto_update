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

PRIMARY_KEYWORDS = (r"小學", r"primary", r"小一", r"幼稚園")
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


COMPETITION_TYPE_LABELS = {
    "steam": "STEAM / 創科",
    "science": "科學 / 數學",
    "arts": "藝術 / 文化",
    "sports": "體育",
    "language": "語文 / 辯論",
    "social": "公民 / 服務",
    "general": "其他比賽",
}

SCHOLARSHIP_TYPE_LABELS = {
    "primary": "小學",
    "secondary": "中學",
    "university": "升學 / 大專",
    "general": "其他獎學金",
}

LEVEL_LABELS = {
    "primary": "小學",
    "secondary": "中學",
    "both": "小學及中學",
}

STUDENT_CONTEXT_KEYWORDS = (
    r"學生",
    r"學界",
    r"學校",
    r"小學",
    r"中學",
    r"青少年",
    r"香港",
    r"校本",
    r"校際",
    r"同學",
    r"學員",
    r"參賽",
)

COMPETITION_NOISE_KEYWORDS = (
    r"職業賽",
    r"世界盃",
    r"英超",
    r"奧運代表",
    r"車手",
    r"賽車",
    r"演唱會",
    r"票房",
    r"藝人",
    r"明星",
    r"選美",
)

SCHOLARSHIP_KEYWORDS = (
    r"獎學金",
    r"助學金",
    r"scholarship",
    r"資助計劃",
    r"獎助學金",
    r"獎助金",
    r"助學",
    r"全額資助",
    r"免費修讀",
    r"資助額",
    r"申請資助",
)

COMPETITION_TYPE_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "steam",
        (
            r"steam",
            r"stem",
            r"編程",
            r"機械人",
            r"人工智能",
            r"\bai\b",
            r"創科",
            r"創新科技",
            r"科普",
            r"資訊科技",
            r"運算思維",
        ),
    ),
    (
        "science",
        (r"科學", r"數學", r"奧數", r"物理", r"化學", r"生物", r"天文", r"科研", r"實驗"),
    ),
    (
        "arts",
        (
            r"藝術",
            r"音樂",
            r"視覺",
            r"朗誦",
            r"朗讀",
            r"話劇",
            r"舞蹈",
            r"書法",
            r"攝影",
            r"設計",
            r"繪畫",
            r"合唱",
        ),
    ),
    ("sports", (r"體育", r"運動", r"田徑", r"游泳", r"足球", r"籃球", r"排球", r"羽毛球", r"乒乓球", r"馬拉松")),
    (
        "language",
        (r"英文", r"語文", r"普通話", r"寫作", r"辯論", r"演講", r"朗誦", r"閱讀", r"作文"),
    ),
    ("social", (r"公民", r"社會服務", r"德育", r"公益", r"關愛", r"義工", r"環保", r"社創")),
)


def is_student_competition(text: str, *, trusted_source: bool = False) -> bool:
    if is_non_education_noise(text) or _matches_any(text, COMPETITION_NOISE_KEYWORDS):
        return False
    if not _matches_any(text, COMPETITION_KEYWORDS):
        return False
    if trusted_source:
        return True
    return _matches_any(text, STUDENT_CONTEXT_KEYWORDS)


def classify_competition_type(title: str, summary: str = "") -> str:
    blob = " ".join([title, summary])
    for key, patterns in COMPETITION_TYPE_RULES:
        if _matches_any(blob, patterns):
            return key
    return "general"


def classify_school_level(title: str, summary: str = "", school_types: str = "") -> str:
    blob = " ".join([title, summary, school_types])
    primary = is_primary_level(blob)
    secondary = is_secondary_level(blob)
    if primary and secondary:
        return "both"
    if primary:
        return "primary"
    if secondary:
        return "secondary"
    return ""


def is_scholarship_opportunity(text: str) -> bool:
    if is_non_education_noise(text):
        return False
    if not _matches_any(text, SCHOLARSHIP_KEYWORDS):
        return False
    return _matches_any(text, STUDENT_CONTEXT_KEYWORDS) or _matches_any(
        text,
        (r"升學", r"大學", r"教育", r"學生", r"學校", r"香港"),
    )


def classify_scholarship_level(title: str, summary: str = "") -> str:
    blob = " ".join([title, summary])
    if _matches_any(blob, (r"大學", r"升學", r"大專", r"degree", r"university", r"本科")):
        return "university"
    if is_secondary_level(blob):
        return "secondary"
    if is_primary_level(blob):
        return "primary"
    return "general"


def is_tcs_teacher_course(title: str, course_id: str = "") -> bool:
    blob = f"{course_id} {title}"
    upper_id = course_id.upper()
    if upper_id.startswith(TCS_COURSE_ID_PREFIXES):
        return True
    if _matches_any(blob, TCS_CORE_KEYWORDS):
        return True
    return _matches_any(blob, TCS_EXCHANGE_KEYWORDS)


TCS_SUBCATEGORY_LABELS = {
    "steam": "STEAM",
    "ai": "AI",
    "admin": "行政",
    "self_review": "自評",
    "exchange": "交流團",
    "guidance": "訓輔導",
    "promotion": "晉升",
    "online_learning": "網上自學",
    "other": "其他",
}

TCS_SUBCATEGORY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("exchange", (r"交流", r"考察", r"study tour", r"參訪", r"訪學", r"境外", r"新加坡")),
    ("promotion", (r"晉升", r"sgm", r"高級學位教師", r"promotion")),
    ("self_review", (r"自評", r"自我評估", r"校本評估")),
    ("guidance", (r"訓輔", r"輔導", r"學生支援", r"特殊教育", r"senco", r"情緒", r"行為", r"關顧", r"正向")),
    (
        "online_learning",
        (
            r"網上自學",
            r"網上課程",
            r"網上基礎課程",
            r"網上培訓",
            r"網上學習",
            r"網上進修",
            r"網上專業",
            r"網課",
            r"自學課程",
            r"e-learning",
            r"elearning",
            r"online course",
            r"online programme",
            r"online program",
            r"online professional",
            r"online knowledge",
            r"online foundation",
            r"online training",
            r"online induction",
            r"online enrichment",
            r"網上",
        ),
    ),
    ("admin", (r"行政", r"管理", r"領導", r"校長", r"中層", r"電子領導", r"校本管理", r"學校行政")),
    ("ai", (r"人工智能", r"\bai\b", r"生成式", r"generative ai", r"機械學習", r"深度學習")),
    (
        "steam",
        (
            r"steam",
            r"stem",
            r"編程",
            r"創科",
            r"機械人",
            r"科學",
            r"科技",
            r"資訊素養",
            r"運算思維",
            r"數字教育",
            r"資訊科技",
            r"電子學習",
            r"編程教育",
            r"coding",
            r"robot",
        ),
    ),
)


def classify_tcs_subcategory(title: str, course_id: str = "") -> str:
    blob = f"{course_id} {title}"
    for key, patterns in TCS_SUBCATEGORY_RULES:
        if _matches_any(blob, patterns):
            return key
    return "other"


EDUCATION_NEWS_KEYWORDS = (
    r"教育",
    r"學校",
    r"中小學",
    r"小學",
    r"中學",
    r"學生",
    r"教師",
    r"老師",
    r"校園",
    r"教育局",
    r"課程",
    r"考試",
    r"dse",
    r"文憑",
    r"幼稚園",
    r"幼兒",
    r"升學",
    r"家長",
    r"學界",
    r"校長",
    r"校舍",
    r"學位",
    r"放榜",
    r"開學",
    r"校巴",
    r"補習",
    r"私立學校",
    r"資助學校",
    r"官立",
    r"直資",
    r"國際學校",
    r"banding",
    r"學術",
    r"校網",
    r"選校",
    r"統一派位",
    r"自行分配",
    r"education",
    r"school",
    r"university",
    r"college",
    r"student",
    r"teacher",
)


def is_education_news(text: str) -> bool:
    return _matches_any(text, EDUCATION_NEWS_KEYWORDS)


NON_EDUCATION_NEWS_KEYWORDS = (
    r"颱風",
    r"風球",
    r"暴雨",
    r"天氣",
    r"賽車",
    r"電單車",
    r"摩打",
    r"演唱會",
    r"音樂會",
    r"愛回家",
    r"開心速遞",
    r"娛樂",
    r"藝人",
    r"明星",
    r"偶像",
    r"k-pop",
    r"kpop",
    r"足球",
    r"籃球",
    r"英超",
    r"世界盃",
    r"奧運",
    r"股市",
    r"樓市",
    r"金價",
    r"油價",
    r"美食",
    r"火鍋",
    r"自助餐",
    r"旅遊",
    r"酒店",
    r"機票",
)


def is_non_education_noise(text: str) -> bool:
    return _matches_any(text, NON_EDUCATION_NEWS_KEYWORDS)


def is_school_news(text: str) -> bool:
    if is_non_education_noise(text):
        return False
    if not is_education_news(text):
        return False
    return is_primary_level(text) or is_secondary_level(text)


def classify_news_levels(
    title: str,
    summary: str = "",
    *,
    level_hint: str | None = None,
    include_general: bool = False,
) -> list[str]:
    del include_general

    blob = " ".join([title, summary])
    if not is_school_news(blob):
        return []

    if level_hint == "primary":
        return ["news_primary"]
    if level_hint == "secondary":
        return ["news_secondary"]

    primary = is_primary_level(blob)
    secondary = is_secondary_level(blob)
    levels: list[str] = []
    if primary:
        levels.append("news_primary")
    if secondary:
        levels.append("news_secondary")
    return levels
