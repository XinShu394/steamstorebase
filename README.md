# Steam Store Crawler

![Status](https://img.shields.io/badge/Status-Production%20Ready-green)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

**可长期运行、可移植、可断点续传的 Steam 游戏数据采集系统**

## ✨ 特性

*   🚀 **高性能**：5进程并发，4天完成21万游戏数据抓取
*   🔄 **断点续跑**：SQLite 持久化任务队列，随时恢复
*   🛡️ **健壮稳定**：完整的限速、重试、错误处理机制
*   📦 **开箱即用**：一键启动脚本，支持 Windows/Linux/Mac
*   📊 **数据完整**：游戏详情 + 评论统计 + 用户标签（20个/游戏）
*   📝 **完整文档**：架构设计、模块说明、变更日志

## 📊 数据规模

| 指标 | 数值 |
|------|------|
| 全量 Steam AppID | **211,780+** |
| 数据维度 | 详情 + 评论 + 标签 |
| 预计存储空间 | 10-15 GB |

## 🚀 快速开始

### 1. 克隆/下载项目
```bash
git clone <repo-url>
cd steamstoreCT
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置 API Key
编辑 `start_concurrent.ps1` (Windows) 或 `start_concurrent.sh` (Linux/Mac)：
```bash
API_KEY="你的Steam_API_Key"  # 从 https://steamcommunity.com/dev/apikey 获取
```

### 4. 启动爬虫
```bash
# Windows PowerShell
.\start_concurrent.ps1

# Linux/Mac
chmod +x start_concurrent.sh
./start_concurrent.sh
```

## 📖 完整文档

*   **[README_DEPLOY.md](README_DEPLOY.md)** - 部署指南（推荐首先阅读）
*   **[PACKAGING.md](PACKAGING.md)** - 打包与迁移指南
*   **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - 项目总结
*   **[docs/architecture.md](docs/architecture.md)** - 系统架构
*   **[docs/modules.md](docs/modules.md)** - 模块详解
*   **[docs/changes.md](docs/changes.md)** - 完整变更历史

## 🛠 技术架构

```
┌──────────────┐
│   main.py    │  ← 主协调器
└──────┬───────┘
       │
   ┌───┴────┬─────────┬──────────┬──────────┐
   │        │         │          │          │
AppList  Detail   Reviews    Tags      Storage
Fetcher  Fetcher  Fetcher   Fetcher     (SQLite)
   │        │         │          │          │
   └────────┴─────────┴──────────┴──────────┘
              │
       ┌──────┴──────┐
    Scheduler   Rate Limiter
   (Task Queue)  (Token Bucket)
```

## 📁 项目结构

```
steamstoreCT/
├── src/                    # 源代码
│   ├── fetcher/           # 数据抓取模块
│   ├── scheduler/         # 任务调度模块
│   ├── storage/           # 数据存储模块
│   └── utils/             # 工具模块
├── docs/                   # 完整文档
├── scripts/               # 工具脚本
├── tests/                 # 单元测试
├── data/                  # 数据库和快照
├── logs/                  # 日志文件
└── requirements.txt       # Python 依赖
```

## ⚙️ 配置参数

| 参数 | 默认值 | 说明 |
|------|--------|------|
| `STEAM_API_KEY` | **必填** | Steam Web API Key |
| `REQUEST_TIMEOUT` | 10 | 请求超时（秒） |
| `MAX_RETRIES` | 3 | 失败重试次数 |
| `RATE_LIMIT_DELAY` | 1.5 | 请求间隔（秒） |

## 📈 性能

| 模式 | 速度 | 完成时间 |
|------|------|---------|
| 单进程 | ~450 任务/小时 | 20 天 |
| **5进程并发** | **~2250 任务/小时** | **4 天** |

## 🧪 测试

```bash
# 单元测试
python -m unittest discover tests

# 快速测试（只处理 50 个任务）
python -m src.main --max-tasks 50
```

## ⚠️ 注意事项

1.  **遵守 Steam TOS**：请勿滥用接口，遵循限速设置。
2.  **API Key 保密**：不要提交 `.env` 文件到公开仓库。
3.  **网络稳定**：长期运行建议使用稳定的服务器环境。
4.  **磁盘空间**：确保至少有 20GB 可用空间。

## 🔧 故障排除

### 429 Too Many Requests
```bash
# 增加延迟
export RATE_LIMIT_DELAY=2.0  # 或在 .env 中修改
```

### SQLite database is locked
```bash
# 正常现象，代码有自动重试
# 如频繁出现，减少并发进程数
```

### 详细诊断
查看日志文件：
```bash
tail -f logs/error_$(date +%Y-%m-%d).log
```

## 📄 License

MIT License - 详见 [LICENSE](LICENSE)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

**🎯 项目状态：生产就绪，可直接部署使用**
