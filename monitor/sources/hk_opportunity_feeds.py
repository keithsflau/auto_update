from __future__ import annotations

# Google News RSS — 每日全面搜尋香港學界比賽及獎學金

COMPETITION_FEEDS: tuple[dict[str, str], ...] = (
    {
        "key": "comp_hk_students",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E5%AD%B8%E7%94%9F+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_hk_school",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E5%AD%B8%E7%95%8C+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_primary",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E5%B0%8F%E5%AD%B8+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_secondary",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E4%B8%AD%E5%AD%B8+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_steam",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+STEAM+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_science",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E7%A7%91%E5%AD%B8+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_math",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E6%95%B8%E5%AD%B8+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_english",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E8%8B%B1%E6%96%87+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_arts",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E8%97%9D%E8%A1%93+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_sports",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E5%AD%B8%E7%95%8C+%E9%AB%94%E8%82%B2"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_debate",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E8%BE%A6%E8%AB%96+%E6%AF%94%E8%B3%BD"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_edb",
        "source": "教育局",
        "url": (
            "https://news.google.com/rss/search?q=site:edb.gov.hk+"
            "%E6%AF%94%E8%B3%BD&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_edcity",
        "source": "香港教育城",
        "url": (
            "https://news.google.com/rss/search?q=site:edcity.hk+"
            "%E6%AF%94%E8%B3%BD&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_hk01",
        "source": "HK01",
        "url": (
            "https://news.google.com/rss/search?q=site:hk01.com+"
            "%E5%AD%B8%E7%95%8C+%E6%AF%94%E8%B3%BD&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "comp_mingpao",
        "source": "明報",
        "url": (
            "https://news.google.com/rss/search?q=site:mingpao.com+"
            "%E5%AD%B8%E7%95%8C+%E6%AF%94%E8%B3%BD&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
)

SCHOLARSHIP_FEEDS: tuple[dict[str, str], ...] = (
    {
        "key": "sch_hk",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E7%8D%8E%E5%AD%B8%E9%87%91"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_apply",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E7%8D%8E%E5%AD%B8%E9%87%91+%E7%94%B3%E8%AB%8B"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_secondary",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E4%B8%AD%E5%AD%B8+%E7%8D%8E%E5%AD%B8%E9%87%91"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_primary",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E5%B0%8F%E5%AD%B8+%E7%8D%8E%E5%AD%B8%E9%87%91"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_university",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E9%A6%99%E6%B8%AF+%E5%8D%87%E5%AD%B8+%E7%8D%8E%E5%AD%B8%E9%87%91"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_en",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "Hong+Kong+scholarship+student"
            "&hl=en-HK&gl=HK&ceid=HK:en"
        ),
    },
    {
        "key": "sch_edb",
        "source": "教育局",
        "url": (
            "https://news.google.com/rss/search?q=site:edb.gov.hk+"
            "%E7%8D%8E%E5%AD%B8%E9%87%91&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_hket",
        "source": "香港經濟日報",
        "url": (
            "https://news.google.com/rss/search?q=site:hket.com+"
            "%E7%8D%8E%E5%AD%B8%E9%87%91&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_hk01",
        "source": "HK01",
        "url": (
            "https://news.google.com/rss/search?q=site:hk01.com+"
            "%E7%8D%8E%E5%AD%B8%E9%87%91&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
    {
        "key": "sch_qef",
        "source": "優質教育基金",
        "url": (
            "https://news.google.com/rss/search?q=site:qef.org.hk+"
            "%E8%B3%87%E5%8A%A9&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
    },
)
