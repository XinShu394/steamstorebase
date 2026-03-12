# Steam Store Crawler - 项目总结

## 🎯 项目目标
构建一个健壮、可长期运行的 Steam 游戏数据采集系统。

## ✅ 已完成功能

### 核心模块
1.  **AppID 获取**：使用官方 API Key，支持分页获取全量列表（211,780+ 游戏）。
2.  **详情抓取**：`appdetails` 接口获取基础信息（名称、价格、发售日期等）。
3.  **评论统计**：`appreviews` 接口获取好评/差评数、总评分。
4.  **标签提取**：HTML 解析获取用户定义的标签（如 "FPS", "RPG"）。
5.  **任务调度**：SQLite 持久化队列，支持断点续跑。
6.  **数据存储**：混合 Schema（SQL 列 + JSON Blob）。

### 高级特性
*   **限速控制**：自适应延迟 + Jitter，避免触发 429。
*   **错误重试**：指数退避，最多 3 次重试。
*   **并发支持**：多进程启动脚本，5x 加速（4天完成）。
*   **完整日志**：按日期滚动，错误单独存储。
*   **可移植性**：一键打包，可迁移至其他机器。

## 📊 当前数据

| 指标 | 数值 |
|------|------|
| 全量 AppID | **211,780** |
| 已抓取游戏 | 325+ |
| 数据完整度 | Details + Reviews + Tags（20个/游戏） |

## 🚀 性能

| 模式 | 速度 | 完成时间 |
|------|------|---------|
| 单进程 | ~450/小时 | 20 天 |
| 5进程并发 | ~2250/小时 | **4 天** |

## 📁 数据结构

### SQLite Schema
```sql
-- games 表
steam_appid (PK), name, type, is_free, release_date, 
price_final, currency, tags_json, updated_at, raw_json

-- reviews 表
steam_appid (PK), review_score, review_score_desc, 
total_positive, total_negative, total_reviews, updated_at

-- tasks 表
app_id (PK), name, status, retries, last_updated, error_msg
```

## 🛠 技术栈
*   **Python 3.9+**
*   **requests** (HTTP 客户端)
*   **BeautifulSoup4** (HTML 解析)
*   **loguru** (日志)
*   **SQLite** (数据持久化)
*   **python-dotenv** (配置管理)

## 📝 文档
*   `README_DEPLOY.md`：部署指南
*   `docs/architecture.md`：系统架构
*   `docs/modules.md`：模块说明
*   `docs/changes.md`：完整变更历史
*   `docs/predata_reference.md`：历史数据说明

## ⚠️ 重要提示
1.  **API Key 保密**：不要提交 `.env` 文件。
2.  **遵守 Steam TOS**：不滥用接口，限速运行。
3.  **监控日志**：定期检查 `logs/error_*.log`。
4.  **备份数据**：`data/` 目录包含所有进度。

## 🔄 下一步优化建议
1.  ~~并发支持~~ ✅ 已完成
2.  增量更新：定期重新拉取 AppID 列表，只处理新增游戏。
3.  数据导出：CSV/JSON 导出工具。
4.  Dashboard：Web 界面实时查看进度。
5.  Docker 化：一键部署容器。

---

**项目状态**：✅ **生产就绪**

可直接部署到其他机器，使用 `start_concurrent.ps1` 或 `.sh` 启动并发爬取。
