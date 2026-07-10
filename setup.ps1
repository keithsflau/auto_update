# 安裝依賴並測試監察程式
Set-Location $PSScriptRoot

python -m pip install -r requirements.txt
if (-not (Test-Path .env)) {
    Copy-Item config.example.env .env
    Write-Host "已建立 .env，請先填入 WhatsApp 設定後再執行。"
}

python -m monitor.main --dry-run
