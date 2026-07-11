from __future__ import annotations

# Hong Kong online media feeds for primary/secondary school news.
# Google News site feeds cover outlets without public RSS (HK01, on.cc, 星島, etc.).

HK_MEDIA_FEEDS: tuple[dict[str, str | bool], ...] = (
    # Official
    {
        "key": "edb_press",
        "source": "教育局",
        "url": "https://www.edb.gov.hk/tc/press_release_rss.xml",
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "edb_whatsnew",
        "source": "教育局",
        "url": "https://www.edb.gov.hk/tc/whats_new_rss.xml",
        "education_only": False,
        "include_general": True,
    },
    # Direct RSS
    {
        "key": "mingpao_edu",
        "source": "明報",
        "url": "https://news.mingpao.com/rss/pns/s00011.xml",
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "mingpao_hk",
        "source": "明報",
        "url": "https://news.mingpao.com/rss/ins/s00001.xml",
        "education_only": True,
    },
    {
        "key": "hket_hk",
        "source": "香港經濟日報",
        "url": "https://www.hket.com/rss/hongkong",
        "education_only": True,
    },
    {
        "key": "yahoo_hk",
        "source": "Yahoo 新聞",
        "url": "https://hk.news.yahoo.com/rss/hong-kong",
        "education_only": True,
    },
    {
        "key": "scmp_hk",
        "source": "南華早報",
        "url": "https://www.scmp.com/rss/2/feed",
        "education_only": True,
    },
    {
        "key": "bastille_hk",
        "source": "巴士的報",
        "url": "https://www.bastillepost.com/hongkong/feed/",
        "education_only": True,
    },
    # Priority HK media: am730 · 星島 · SCMP · unwire.hk
    {
        "key": "am730_school",
        "source": "am730",
        "url": (
            "https://news.google.com/rss/search?q=site:am730.com.hk+"
            "%E5%AD%B8%E6%A0%A1&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "scmp_edu_zh",
        "source": "南華早報",
        "url": (
            "https://news.google.com/rss/search?q=site:scmp.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "singtao_school",
        "source": "星島日報",
        "url": (
            "https://news.google.com/rss/search?q=site:std.stheadline.com+"
            "%E5%AD%B8%E6%A0%A1&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "stheadline_school",
        "source": "星島頭條",
        "url": (
            "https://news.google.com/rss/search?q=site:stheadline.com+"
            "%E5%AD%B8%E6%A0%A1&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "unwire_feed",
        "source": "unwire.hk",
        "url": "https://unwire.hk/feed",
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_unwire",
        "source": "unwire.hk",
        "url": (
            "https://news.google.com/rss/search?q=site:unwire.hk+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    # Google News — aggregates HK online media without public RSS
    {
        "key": "google_edu",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E6%95%99%E8%82%B2+%E9%A6%99%E6%B8%AF+%E5%AD%B8%E6%A0%A1"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_primary",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E5%B0%8F%E5%AD%B8+%E9%A6%99%E6%B8%AF"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "level_hint": "primary",
    },
    {
        "key": "google_secondary",
        "source": "Google 新聞",
        "url": (
            "https://news.google.com/rss/search?q="
            "%E4%B8%AD%E5%AD%B8+%E9%A6%99%E6%B8%AF"
            "&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "level_hint": "secondary",
    },
    {
        "key": "google_hk01",
        "source": "HK01",
        "url": (
            "https://news.google.com/rss/search?q=site:hk01.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_mingpao",
        "source": "明報",
        "url": (
            "https://news.google.com/rss/search?q=site:mingpao.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_oncc",
        "source": "on.cc 東網",
        "url": (
            "https://news.google.com/rss/search?q=site:on.cc+"
            "%E5%AD%B8%E6%A0%A1&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_hket",
        "source": "香港經濟日報",
        "url": (
            "https://news.google.com/rss/search?q=site:hket.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_rthk",
        "source": "香港電台",
        "url": (
            "https://news.google.com/rss/search?q=site:rthk.hk+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_scmp",
        "source": "南華早報",
        "url": (
            "https://news.google.com/rss/search?q=site:scmp.com+"
            "Hong+Kong+education&hl=en-HK&gl=HK&ceid=HK:en"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_stheadline",
        "source": "星島頭條",
        "url": (
            "https://news.google.com/rss/search?q=site:stheadline.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_singtao",
        "source": "星島日報",
        "url": (
            "https://news.google.com/rss/search?q=site:std.stheadline.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_oriental",
        "source": "東方日報",
        "url": (
            "https://news.google.com/rss/search?q=site:orientaldaily.on.cc+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_am730",
        "source": "am730",
        "url": (
            "https://news.google.com/rss/search?q=site:am730.com.hk+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_tvb",
        "source": "TVB 新聞",
        "url": (
            "https://news.google.com/rss/search?q=site:news.tvb.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_now",
        "source": "Now 新聞",
        "url": (
            "https://news.google.com/rss/search?q=site:news.now.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_dotdot",
        "source": "點新聞",
        "url": (
            "https://news.google.com/rss/search?q=site:dotdotnews.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_takungpao",
        "source": "大公報",
        "url": (
            "https://news.google.com/rss/search?q=site:takungpao.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_wenweipo",
        "source": "文匯報",
        "url": (
            "https://news.google.com/rss/search?q=site:wenweipo.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_hkcnews",
        "source": "眾新聞",
        "url": (
            "https://news.google.com/rss/search?q=site:hkcnews.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
    {
        "key": "google_topick",
        "source": "TOPick",
        "url": (
            "https://news.google.com/rss/search?q=site:topick.hket.com+"
            "%E6%95%99%E8%82%B2&hl=zh-HK&gl=HK&ceid=HK:zh-Hant"
        ),
        "education_only": False,
        "include_general": True,
    },
)
