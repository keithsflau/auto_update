# 建立 Windows 工作排程器：每 6 小時檢查一次
param(
    [string]$TaskName = "HK-Education-Update-Monitor"
)

$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$batPath = Join-Path $scriptRoot "run_monitor.bat"

$action = New-ScheduledTaskAction -Execute $batPath -WorkingDirectory $scriptRoot
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 6) -RepetitionDuration ([TimeSpan]::MaxValue)
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Settings $settings -Force
Write-Host "已建立排程工作：$TaskName（每 6 小時執行）"
