# Steam Crawler - 一键打包脚本 (Windows)

$PackName = "steamcrawler_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
$PackDir = ".\$PackName"

Write-Host "=====================================" -ForegroundColor Green
Write-Host "Steam Crawler - Packaging Tool" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green

# 1. 创建打包目录
Write-Host "`n[1/5] Creating package directory..." -ForegroundColor Cyan
New-Item -ItemType Directory -Path $PackDir -Force | Out-Null

# 2. 复制核心文件
Write-Host "[2/5] Copying source code..." -ForegroundColor Cyan
Copy-Item -Recurse -Path "src" -Destination "$PackDir\src"

Write-Host "[3/5] Copying documentation..." -ForegroundColor Cyan
Copy-Item -Recurse -Path "docs" -Destination "$PackDir\docs"

Write-Host "[4/5] Copying scripts and configs..." -ForegroundColor Cyan
Copy-Item -Recurse -Path "scripts" -Destination "$PackDir\scripts"
Copy-Item -Path "requirements.txt" -Destination $PackDir
Copy-Item -Path "*.md" -Destination $PackDir
Copy-Item -Path "start_concurrent.*" -Destination $PackDir
Copy-Item -Path ".gitignore" -Destination $PackDir

# 3. 复制进度数据（可选）
$IncludeData = Read-Host "`n是否包含已抓取的数据和进度? (y/n) [默认: n]"
if ($IncludeData -eq "y") {
    Write-Host "[5/5] Copying data files..." -ForegroundColor Cyan
    if (Test-Path "data") {
        Copy-Item -Recurse -Path "data" -Destination "$PackDir\data"
        Write-Host "  ✓ Data included (断点续传)" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ data/ directory not found, skipping" -ForegroundColor Yellow
    }
} else {
    Write-Host "[5/5] Skipping data files..." -ForegroundColor Cyan
    Write-Host "  ✓ Fresh start (全新开始)" -ForegroundColor Green
}

# 4. 清理敏感信息
Write-Host "`nCleaning sensitive files..." -ForegroundColor Cyan
if (Test-Path "$PackDir\.env") {
    Remove-Item "$PackDir\.env" -Force
    Write-Host "  ✓ Removed .env" -ForegroundColor Green
}

# 5. 创建配置模板
@"
# Steam Crawler Configuration
# 请填入您的 Steam API Key

STEAM_API_KEY=YOUR_API_KEY_HERE
DATA_DIR=data
LOG_DIR=logs
REQUEST_TIMEOUT=10
MAX_RETRIES=3
RATE_LIMIT_DELAY=1.5
"@ | Out-File -FilePath "$PackDir\.env.example" -Encoding utf8

Write-Host "  ✓ Created .env.example" -ForegroundColor Green

# 6. 压缩
Write-Host "`nCompressing package..." -ForegroundColor Cyan
Compress-Archive -Path "$PackDir\*" -DestinationPath "$PackName.zip" -Force

# 7. 清理临时目录
Remove-Item -Recurse -Force $PackDir

# 完成
Write-Host "`n=====================================" -ForegroundColor Green
Write-Host "Package created successfully!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host "`nFile: $PackName.zip" -ForegroundColor Yellow
Write-Host "Size: $((Get-Item "$PackName.zip").Length / 1MB | ForEach-Object { [math]::Round($_, 2) }) MB`n" -ForegroundColor Yellow
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Copy $PackName.zip to target machine" -ForegroundColor White
Write-Host "  2. Extract and run: pip install -r requirements.txt" -ForegroundColor White
Write-Host "  3. Edit start_concurrent.ps1 to add your API Key" -ForegroundColor White
Write-Host "  4. Run: .\start_concurrent.ps1`n" -ForegroundColor White
