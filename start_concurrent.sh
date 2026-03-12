#!/bin/bash
# Steam Store Crawler - 并发启动脚本 (Linux/Mac)

# 配置
WORKERS=5

# 从 .env 加载 API Key（若存在）
if [ -f .env ]; then
    STEAM_API_KEY=$(grep '^STEAM_API_KEY=' .env | cut -d'=' -f2-)
    export STEAM_API_KEY
fi

if [ -z "$STEAM_API_KEY" ] || [ "$STEAM_API_KEY" = "YOUR_API_KEY_HERE" ]; then
    echo "错误: 请先配置 Steam API Key!"
    echo "  1. 复制 .env.example 为 .env"
    echo "  2. 在 .env 中填入 STEAM_API_KEY=你的Key"
    echo "  获取地址: https://steamcommunity.com/dev/apikey"
    exit 1
fi

echo "====================================="
echo "Steam Crawler - Multi-Process Mode"
echo "Workers: $WORKERS"
echo "====================================="

# 启动多个进程（后台运行）
for i in $(seq 1 $WORKERS); do
    echo "Starting Worker $i..."
    nohup python -m src.main > logs/worker_$i.log 2>&1 &
    sleep 2
done

echo ""
echo "All workers started in background!"
echo "Check logs/worker_*.log for output"
echo "Use 'pkill -f src.main' to stop all workers"
