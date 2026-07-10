# Hong Kong Education Update Monitor

自動監察香港教育相關更新，並透過 Telegram / WhatsApp 通知。

## 監察範圍

- STEAM 中學／小學比賽（香港多個網站）
- 教師培訓行事曆（TCS）
- 優質教育基金（QEF）
- 教育局通函

## 快速開始

```bash
pip install -r requirements.txt
cp config.example.env .env
# 編輯 .env 填入通知設定
python -m monitor.main --dry-run
python -m monitor.main
```

## 網頁儀表板

```bash
run_web.bat
# 開啟 http://127.0.0.1:8080
```

## GitHub Actions

在 Repository Secrets 設定：

- `NOTIFY_CHANNELS` = `telegram,callmebot`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `WHATSAPP_PHONE`
- `CALLMEBOT_APIKEY`

## 通知渠道

`telegram` | `callmebot` | `email` | `twilio`（見 `config.example.env`）
