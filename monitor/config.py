from __future__ import annotations

import json
import os
from pathlib import Path


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def _env(name: str, default: str = "") -> str:
    value = os.getenv(name)
    if value is None or value.strip() == "":
        return default
    return value.strip()


BASE_DIR = Path(__file__).resolve().parent.parent
load_env_file(BASE_DIR / ".env")

WHATSAPP_PROVIDER = _env("WHATSAPP_PROVIDER", "callmebot").lower()
WHATSAPP_PHONE = _env("WHATSAPP_PHONE")
CALLMEBOT_APIKEY = _env("CALLMEBOT_APIKEY")
TWILIO_ACCOUNT_SID = _env("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = _env("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_FROM = _env("TWILIO_WHATSAPP_FROM")
WHATSAPP_TO = _env("WHATSAPP_TO")

NOTIFY_CHANNELS = [
    part.strip().lower()
    for part in _env("NOTIFY_CHANNELS", "telegram").split(",")
    if part.strip()
]

TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _env("TELEGRAM_CHAT_ID")

EMAIL_SMTP_HOST = _env("EMAIL_SMTP_HOST", "smtp.gmail.com")
EMAIL_SMTP_PORT = int(_env("EMAIL_SMTP_PORT", "587"))
EMAIL_SMTP_USER = _env("EMAIL_SMTP_USER")
EMAIL_SMTP_PASSWORD = _env("EMAIL_SMTP_PASSWORD")
EMAIL_TO = _env("EMAIL_TO")

TCS_DAILY_EMAIL_TO = _env("TCS_DAILY_EMAIL_TO", "lausiufung@kyc.edu.hk")
TCS_DAILY_EMAIL_ENABLED = _env("TCS_DAILY_EMAIL_ENABLED", "true").lower() in {
    "1",
    "true",
    "yes",
}

INITIAL_RUN_NOTIFY = _env("INITIAL_RUN_NOTIFY", "false").lower() in {
    "1",
    "true",
    "yes",
}
EDB_CIRCULAR_LOOKBACK_DAYS = int(_env("EDB_CIRCULAR_LOOKBACK_DAYS", "90"))

STATE_FILE = BASE_DIR / "data" / "state.json"
LOG_FILE = BASE_DIR / "data" / "monitor.log"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

CATEGORY_LABELS = {
    "competition_primary": "小學比賽",
    "competition_secondary": "中學比賽",
    "scholarship": "獎學金申請",
    "tcs_teacher": "教師培訓 (TCS)",
    "qef": "優質教育基金 (QEF)",
    "edb_circular": "教育局通函",
    "news_primary": "小學新聞",
    "news_secondary": "中學新聞",
}
