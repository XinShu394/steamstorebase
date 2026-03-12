# Steam Store Crawler - 部署指南

## 📦 快速开始

### 1. 环境要求
- Python 3.9+
- pip
- 稳定的网络连接

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 API Key
创建 `.env` 文件（或通过环境变量设置）：
```bash
STEAM_API_KEY=你的Steam_API_Key
DATA_DIR=data
LOG_DIR=logs
REQUEST_TIMEOUT=10
MAX_RETRIES=3
RATE_LIMIT_DELAY=1.5
```

**获取 API Key**：访问 https://steamcommunity.com/dev/apikey

### 4. 运行爬虫

#### 单进程模式（测试用）
```bash
# Windows PowerShell
$env:STEAM_API_KEY="你的Key"; python -m src.main --max-tasks 50

# Linux/Mac
export STEAM_API_KEY="你的Key"
python -m src.main --max-tasks 50
```

#### 多进程模式（生产环境，5倍速）
```bash
# Windows
.\start_concurrent.ps1

# Linux/Mac
chmod +x start_concurrent.sh
./start_concurrent.sh
```

## 🚀 性能预估

| 模式 | 速度 | 完成时间（21万任务） |
|------|------|---------------------|
| 单进程 | ~450 任务/小时 | 19-20 天 |
| 5进程并发 | ~2250 任务/小时 | 4 天 |

## 📊 监控进度

### 查看日志
```bash
# 实时查看主日志
tail -f logs/app_$(date +%Y-%m-%d).log

# 查看错误日志
tail -f logs/error_$(date +%Y-%m-$d).log
```

### 查看数据库统计
```bash
python -c "from src.storage.database import game_storage; print(f'已抓取: {game_storage.get_count()} 个游戏')"
```

### 查看任务队列状态
```bash
python -c "from src.scheduler.manager import scheduler; import json; print(json.dumps(scheduler.get_stats(), indent=2))"
```

## 🛠 故障排除

### 1. 429 Too Many Requests
- 增加 `RATE_LIMIT_DELAY`（例如改为 2.0）。
- 减少并发进程数。

### 2. 网络超时
- 增加 `REQUEST_TIMEOUT`（例如改为 15）。
- 检查网络稳定性。

### 3. SQLite database is locked
- 这是正常的多进程竞争，代码有重试机制。
- 如果频繁出现，减少并发数。

## 📁 目录结构
```
steamstoreCT/
├── data/                   # 数据库和快照
│   ├── app_list_*.json     # AppID 列表快照
│   ├── steam_data.db       # 游戏详情数据
│   └── tasks.db            # 任务队列
├── logs/                   # 日志文件
├── src/                    # 源代码
├── requirements.txt        # Python 依赖
├── start_concurrent.ps1    # Windows 并发启动
├── start_concurrent.sh     # Linux 并发启动
└── README_DEPLOY.md        # 本文件
```

## ⚠️ 注意事项
1.  **API Key 保密**：不要提交到公开仓库。
2.  **磁盘空间**：21万游戏约需 10-15GB 存储空间。
3.  **长期运行**：建议使用 `tmux` 或 `screen` 防止SSH断开。

## 🔄 迁移到新电脑
1.  复制整个项目文件夹。
2.  在新机器上安装Python和依赖。
3.  复制 `data/` 目录（保留进度）。
4.  运行 `start_concurrent.ps1` 或 `.sh`。

爬虫会自动从上次断点继续。
