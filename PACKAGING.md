# 🎁 Steam Crawler - 完整打包清单

## 📦 需要复制的文件/目录

### ✅ 必须包含
```
steamstoreCT/
├── src/                         # 完整源代码
│   ├── __init__.py
│   ├── config.py
│   ├── logger.py
│   ├── main.py
│   ├── fetcher/
│   │   ├── __init__.py
│   │   ├── app_list.py
│   │   ├── detail.py
│   │   ├── reviews.py
│   │   └── tags.py
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── manager.py
│   │   └── task.py
│   ├── storage/
│   │   ├── __init__.py
│   │   └── database.py
│   └── utils/
│       ├── __init__.py
│       └── rate_limiter.py
│
├── docs/                        # 完整文档
│   ├── architecture.md
│   ├── modules.md
│   ├── changes.md
│   └── predata_reference.md
│
├── scripts/                     # 工具脚本
│   ├── hard_reset.py
│   ├── reset_fresh.py
│   └── import_predata.py
│
├── tests/                       # 单元测试（可选）
│
├── requirements.txt             # Python 依赖
├── start_concurrent.ps1         # Windows 并发启动
├── start_concurrent.sh          # Linux 并发启动
├── README_DEPLOY.md             # 部署指南
├── PROJECT_SUMMARY.md           # 项目总结
├── PACKAGING.md                 # 本文件
└── .gitignore                   # Git 忽略规则
```

### 🔸 可选包含（如果要保留进度）
```
data/                            # 如果要续传
├── app_list_*.json              # AppID 快照
├── steam_data.db                # 已抓取的游戏数据
└── tasks.db                     # 任务队列状态
```

### ❌ 不要包含
```
.env                             # 包含 API Key（保密）
logs/                            # 日志文件（太大且无用）
__pycache__/                     # Python 缓存
*.pyc, *.pyo                     # 编译文件
.git/                            # Git 仓库（如果需要版本控制，重新 init）
predata/                         # 历史参考数据（仅用于参考，不是实际数据）
```

## 📤 打包步骤

### Windows (PowerShell)
```powershell
# 1. 创建打包目录
New-Item -ItemType Directory -Path ".\steamcrawler_pack"

# 2. 复制核心文件
Copy-Item -Recurse -Path "src", "docs", "scripts" -Destination ".\steamcrawler_pack\"
Copy-Item -Path "requirements.txt", "*.md", "start_concurrent.*", ".gitignore" -Destination ".\steamcrawler_pack\"

# 3. (可选) 复制进度数据
# Copy-Item -Recurse -Path "data" -Destination ".\steamcrawler_pack\"

# 4. 压缩
Compress-Archive -Path ".\steamcrawler_pack\*" -DestinationPath "steamcrawler.zip"
```

### Linux/Mac (Bash)
```bash
# 1. 创建打包目录
mkdir steamcrawler_pack

# 2. 复制核心文件
cp -r src docs scripts steamcrawler_pack/
cp requirements.txt *.md start_concurrent.* .gitignore steamcrawler_pack/

# 3. (可选) 复制进度数据
# cp -r data steamcrawler_pack/

# 4. 压缩
tar -czf steamcrawler.tar.gz steamcrawler_pack/
```

## 🚀 在新机器上部署

### 1. 解压
```bash
# Windows
Expand-Archive steamcrawler.zip -DestinationPath "D:\Projects\"

# Linux/Mac
tar -xzf steamcrawler.tar.gz -C ~/projects/
```

### 2. 安装 Python 环境
```bash
# 检查 Python 版本（需要 3.9+）
python --version

# 安装依赖
cd steamcrawler_pack
pip install -r requirements.txt
```

### 3. 配置 API Key
**方式A：修改启动脚本** (推荐)
编辑 `start_concurrent.ps1` 或 `.sh`，填入你的 API Key：
```powershell
$API_KEY = "你的Steam_API_Key"  # Windows
```
```bash
API_KEY="你的Steam_API_Key"  # Linux/Mac
```

**方式B：创建 .env 文件**
```bash
STEAM_API_KEY=你的Steam_API_Key
DATA_DIR=data
LOG_DIR=logs
REQUEST_TIMEOUT=10
RATE_LIMIT_DELAY=1.5
```

### 4. 创建必要目录
```bash
mkdir data logs
```

### 5. 启动爬虫
```bash
# Windows
.\start_concurrent.ps1

# Linux/Mac
chmod +x start_concurrent.sh
./start_concurrent.sh
```

## 🔐 安全检查清单

在分享或迁移前，确认以下事项：

- [ ] `.env` 文件**未被包含**（或已替换为 `.env.example`）。
- [ ] 启动脚本中的 `API_KEY` 已替换为**占位符**或**你的新Key**。
- [ ] `logs/` 目录未被打包（避免暴露历史爬取记录）。
- [ ] 如果使用 Git，确认 `.gitignore` 正确配置。

## 📝 版本信息

**打包日期**：2026-01-21  
**版本**：v1.0 - Production Ready  
**支持平台**：Windows 10+, Linux, macOS

---

**完成后，整个项目即可在任何机器上运行！** 🎉
