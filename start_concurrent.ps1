# Steam Store Crawler - 并发启动脚本

# 配置
$WORKERS = 5  # 并发进程数

# 从 .env 加载 API Key（若存在）
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^\s*STEAM_API_KEY\s*=\s*(.+)\s*$') {
            $env:STEAM_API_KEY = $matches[1].Trim()
        }
    }
}

if (-not $env:STEAM_API_KEY -or $env:STEAM_API_KEY -eq "YOUR_API_KEY_HERE") {
    Write-Host "错误: 请先配置 Steam API Key!" -ForegroundColor Red
    Write-Host "  1. 复制 .env.example 为 .env" -ForegroundColor Yellow
    Write-Host "  2. 在 .env 中填入 STEAM_API_KEY=你的Key" -ForegroundColor Yellow
    Write-Host "  获取地址: https://steamcommunity.com/dev/apikey" -ForegroundColor Cyan
    exit 1
}

Write-Host "=====================================" -ForegroundColor Green
Write-Host "Steam Crawler - Multi-Process Mode" -ForegroundColor Green
Write-Host "Workers: $WORKERS" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# 启动多个进程
for ($i = 1; $i -le $WORKERS; $i++) {
    Write-Host "Starting Worker $i..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "`$env:STEAM_API_KEY='$($env:STEAM_API_KEY)'; python -m src.main"
    Start-Sleep -Seconds 2
}

Write-Host ""
Write-Host "All workers started!" -ForegroundColor Green
Write-Host "Press Ctrl+C in each window to stop." -ForegroundColor Yellow
