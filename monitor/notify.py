from __future__ import annotations

import smtplib
from email.mime.text import MIMEText

import requests

from monitor.config import (
    CALLMEBOT_APIKEY,
    CATEGORY_LABELS,
    EMAIL_SMTP_HOST,
    EMAIL_SMTP_PASSWORD,
    EMAIL_SMTP_PORT,
    EMAIL_SMTP_USER,
    EMAIL_TO,
    NOTIFY_CHANNELS,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID,
    TWILIO_ACCOUNT_SID,
    TWILIO_AUTH_TOKEN,
    TWILIO_WHATSAPP_FROM,
    WHATSAPP_PHONE,
    WHATSAPP_PROVIDER,
    WHATSAPP_TO,
)
from monitor.models import UpdateItem
from monitor.state import log


def format_message(item: UpdateItem) -> str:
    label = CATEGORY_LABELS.get(item.category, item.category)
    lines = [
        f"🔔 {label} 有新更新",
        f"標題：{item.title}",
    ]
    if item.date:
        lines.append(f"日期：{item.date}")
    if item.summary:
        lines.append(f"摘要：{item.summary[:300]}")
    if item.url:
        lines.append(f"連結：{item.url}")
    return "\n".join(lines)


def send_notification(message: str) -> list[str]:
    if not NOTIFY_CHANNELS:
        raise RuntimeError(
            "請在 .env 設定 NOTIFY_CHANNELS，例如：telegram 或 telegram,email"
        )

    sent: list[str] = []
    errors: list[str] = []

    for channel in NOTIFY_CHANNELS:
        try:
            if channel == "telegram":
                _send_telegram(message)
            elif channel == "email":
                _send_email(message)
            elif channel == "callmebot":
                _send_callmebot(message)
            elif channel == "twilio":
                _send_twilio(message)
            else:
                raise ValueError(f"未知通知渠道：{channel}")
            sent.append(channel)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{channel}: {exc}")

    if not sent:
        raise RuntimeError("所有通知渠道均失敗：" + "; ".join(errors))
    if errors:
        log("部分通知渠道失敗：" + "; ".join(errors))
    return sent


def send_test_notification() -> list[str]:
    return send_notification("✅ 香港教育更新監察 — 通知測試成功！")


def _send_telegram(message: str) -> None:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        raise RuntimeError(
            "請設定 TELEGRAM_BOT_TOKEN 及 TELEGRAM_CHAT_ID。"
            "教學：在 Telegram 找 @BotFather 建立 bot，再找 @userinfobot 取得 chat id。"
        )

    response = requests.post(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        json={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "disable_web_page_preview": False,
        },
        timeout=30,
    )
    response.raise_for_status()
    payload = response.json()
    if not payload.get("ok"):
        raise RuntimeError(payload.get("description", "Telegram 發送失敗"))


def _send_email(message: str) -> None:
    if not EMAIL_TO:
        raise RuntimeError("請設定 EMAIL_TO。")
    send_email_to(EMAIL_TO, "香港教育更新通知", message)


def send_email_to(recipient: str, subject: str, message: str) -> None:
    if not all([EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD, recipient]):
        raise RuntimeError(
            "請設定 EMAIL_SMTP_USER、EMAIL_SMTP_PASSWORD，以及收件人電郵。"
        )

    mail = MIMEText(message, "plain", "utf-8")
    mail["Subject"] = subject
    mail["From"] = EMAIL_SMTP_USER
    mail["To"] = recipient

    with smtplib.SMTP(EMAIL_SMTP_HOST, EMAIL_SMTP_PORT, timeout=30) as server:
        server.starttls()
        server.login(EMAIL_SMTP_USER, EMAIL_SMTP_PASSWORD)
        server.send_message(mail)


def _send_callmebot(message: str) -> None:
    if not WHATSAPP_PHONE or not CALLMEBOT_APIKEY:
        raise RuntimeError(
            "請設定 WHATSAPP_PHONE 及 CALLMEBOT_APIKEY。"
            "若收不到訊息，可向 CallMeBot 發送 Resume，或改用 telegram。"
        )

    response = requests.get(
        "https://api.callmebot.com/whatsapp.php",
        params={
            "phone": WHATSAPP_PHONE,
            "text": message,
            "apikey": CALLMEBOT_APIKEY,
        },
        timeout=30,
    )
    response.raise_for_status()
    if "paused" in response.text.lower() or "stop" in response.text.lower():
        raise RuntimeError("CallMeBot 已暫停，請向 bot 發送 Resume")


def _send_twilio(message: str) -> None:
    if WHATSAPP_PROVIDER != "twilio":
        pass
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_WHATSAPP_FROM, WHATSAPP_TO]):
        raise RuntimeError("請設定 Twilio WhatsApp 相關變數。")

    response = requests.post(
        f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Messages.json",
        auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN),
        data={
            "From": TWILIO_WHATSAPP_FROM,
            "To": WHATSAPP_TO,
            "Body": message,
        },
        timeout=30,
    )
    response.raise_for_status()


NOTIFY_BATCH_SIZE = 20


def _format_batch_message(items: list[UpdateItem], *, total: int) -> str:
    lines = [f"🔔 香港教育更新 — 共 {total} 項新更新", ""]
    for item in items:
        label = CATEGORY_LABELS.get(item.category, item.category)
        lines.append(f"• [{label}] {item.title}")
        if item.url:
            lines.append(f"  {item.url}")
    remaining = total - len(items)
    if remaining > 0:
        lines.append("")
        lines.append(f"… 另有 {remaining} 項，請到網頁查看完整清單。")
    return "\n".join(lines)


def notify_items(items: list[UpdateItem]) -> int:
    if not items:
        return 0

    total = len(items)
    if total <= NOTIFY_BATCH_SIZE:
        sent = 0
        for item in items:
            channels = send_notification(format_message(item))
            log(f"已透過 {', '.join(channels)} 發送：{item.title[:60]}")
            sent += 1
        return sent

    preview = sorted(items, key=lambda item: (item.category, item.title))[:NOTIFY_BATCH_SIZE]
    channels = send_notification(_format_batch_message(preview, total=total))
    log(f"已透過 {', '.join(channels)} 發送摘要（{total} 項，顯示 {len(preview)} 項）")
    return total
