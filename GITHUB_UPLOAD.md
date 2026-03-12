# GitHub 上传清单

本文档说明上传到 GitHub 后，他人克隆项目能顺利跑通所需的文件和步骤。

## ✅ 必须上传的文件/目录

| 路径 | 说明 |
|------|------|
| `src/` | 完整源代码 |
| `scripts/` | 工具脚本（reset、import 等） |
| `docs/` | 架构、模块、变更文档 |
| `tests/` | 单元测试 |
| `requirements.txt` | Python 依赖（他人 `pip install -r` 即可） |
| `start_concurrent.ps1` | Windows 并发启动脚本 |
| `start_concurrent.sh` | Linux/Mac 并发启动脚本 |
| `.env.example` | 配置模板（不含真实 Key） |
| `.gitignore` | 忽略规则 |
| `README.md` | 项目说明 |
| `README_DEPLOY.md` | 部署指南 |
| `plan.md` | 项目规划 |
| `data/.keep` | 占位文件，保证空 data 目录被提交 |
| `logs/.keep` | 占位文件，保证空 logs 目录被提交 |

## ❌ 不要上传（已在 .gitignore）

| 路径 | 原因 |
|------|------|
| `.env` | 包含真实 API Key，安全敏感 |
| `*.db` | 数据库文件，体积大且可本地生成 |
| `data/*.json` | AppID 快照，运行时会自动拉取 |
| `logs/*.log` | 日志文件，本地生成 |
| `__pycache__/` | Python 缓存 |
| `venv/`, `env/` | 虚拟环境 |

## 📋 克隆者首次运行步骤

1. **克隆项目**
   ```bash
   git clone <你的仓库地址>
   cd steamstoreCT
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **配置 API Key**
   ```bash
   # Windows
   copy .env.example .env
   # 编辑 .env，将 YOUR_API_KEY_HERE 替换为真实 Key

   # Linux/Mac
   cp .env.example .env
   # 编辑 .env，将 YOUR_API_KEY_HERE 替换为真实 Key
   ```
   API Key 获取：https://steamcommunity.com/dev/apikey

4. **启动爬虫**
   ```bash
   # Windows
   .\start_concurrent.ps1

   # Linux/Mac
   chmod +x start_concurrent.sh
   ./start_concurrent.sh
   ```

## 🔒 安全说明

- 启动脚本已改为从 `.env` 读取 API Key，不再硬编码
- `.env` 已在 `.gitignore` 中，不会被提交
- 上传前请确认没有遗漏的 Key 或密码

## 📦 可选上传

| 路径 | 说明 |
|------|------|
| `predata/` | 历史参考数据，仅 `import_predata.py` 需要，主爬虫不依赖 |
| `PACKAGING.md` | 打包与迁移说明 |
| `PROJECT_SUMMARY.md` | 项目总结 |
| `LICENSE` | 开源协议（README 提到 MIT，建议添加） |
