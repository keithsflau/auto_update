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

**線上版（GitHub Pages，每 6 小時自動更新）：**  
https://keithsflau.github.io/auto_update/

**本機版：**

```bash
run_web.bat
# 開啟 http://127.0.0.1:8080
```

## GitHub Actions

Workflow 會每 **6 小時**自動：

1. 執行監察程式（擷取資料、發送通知）
2. 更新 `dashboard.json`
3. 部署網頁儀表板到 GitHub Pages
4. **每日**發送 TCS 課程摘要電郵至 `lausiufung@kyc.edu.hk`

### TCS 課程分類

STEAM、AI、行政、自評、交流團、訓輔導、晉升、其他

### 中小學新聞

來源包括：**教育局**、**明報**、**香港經濟日報**、**Yahoo 新聞**、**南華早報 (SCMP)**、**am730**、**星島日報／星島頭條**、**unwire.hk**，以及透過 **Google 新聞** 聚合的 HK01、on.cc 東網、TVB、Now 新聞等香港網媒。

由**上個月起**擷取，保留**一年**。

手動測試：Repository → **Actions** → **Education Update Monitor** → **Run workflow**

在 Repository Secrets 設定：

- `NOTIFY_CHANNELS` = `telegram,callmebot`
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`
- `WHATSAPP_PHONE`
- `CALLMEBOT_APIKEY`
- `EMAIL_SMTP_USER` / `EMAIL_SMTP_PASSWORD`（TCS 每日電郵需要）
- `TCS_DAILY_EMAIL_TO`（預設 `lausiufung@kyc.edu.hk`）

## 通知渠道

`telegram` | `callmebot` | `email` | `twilio`（見 `config.example.env`）
