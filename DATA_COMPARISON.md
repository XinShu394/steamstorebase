# 当前系统 vs Predata 数据对比

## 📊 当前系统能获取的数据

### ✅ games 表（主表）
| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `steam_appid` | INTEGER | API | 游戏唯一ID |
| `name` | TEXT | API | 游戏名称 |
| `type` | TEXT | API | 类型（game/dlc/demo等） |
| `is_free` | BOOLEAN | API | 是否免费 |
| `release_date` | TEXT | API | 发售日期 |
| `price_final` | INTEGER | API | 当前价格（分） |
| `currency` | TEXT | API | 货币类型 |
| **`tags_json`** | TEXT (JSON) | **HTML爬取** | 用户标签（JSON数组，约20个） |
| `updated_at` | TIMESTAMP | 系统 | 更新时间 |
| `raw_json` | TEXT | API | 完整原始JSON |

**示例数据：**
```json
{
  "steam_appid": 10,
  "name": "Counter-Strike",
  "type": "game",
  "is_free": false,
  "release_date": "Nov 1, 2000",
  "price_final": 999,
  "currency": "USD",
  "tags_json": ["Action", "FPS", "Multiplayer", "Shooter", "Classic"]
}
```

### ✅ reviews 表
| 字段 | 类型 | 来源 | 说明 |
|------|------|------|------|
| `steam_appid` | INTEGER | API | 游戏ID |
| `review_score` | INTEGER | API | 评分（0-10） |
| `review_score_desc` | TEXT | API | 评价描述（如"Overwhelmingly Positive"） |
| `total_positive` | INTEGER | API | 好评数 |
| `total_negative` | INTEGER | API | 差评数 |
| `total_reviews` | INTEGER | API | 总评论数 |
| `updated_at` | TIMESTAMP | 系统 | 更新时间 |

**示例数据：**
```json
{
  "steam_appid": 10,
  "review_score": 9,
  "review_score_desc": "Overwhelmingly Positive",
  "total_positive": 250060,
  "total_negative": 6630,
  "total_reviews": 256690
}
```

---

## 📋 Predata 有但当前系统缺少的数据

### ❌ **1. Categories（分类）**
**Predata 结构：**
```csv
app_id, category
10, "Family Sharing"
10, "Multi-player"
10, "Steam Achievements"
```

**缺失内容：**
- Single-player / Multi-player
- Co-op / Online Co-Op
- Steam Achievements / Trading Cards
- Controller Support
- VR Support

**获取方式：**
- API: `appdetails` 的 `categories` 字段
- 需要解析多对多关系（一个游戏多个分类）

---

### ❌ **2. Genres（类型）**
**Predata 结构：**
```csv
app_id, genre
10, "Action"
10, "Strategy"
```

**缺失内容：**
- Action, Adventure, RPG, Strategy, Simulation 等官方分类
- 与 Tags 的区别：Genres 是官方分类，Tags 是用户定义

**获取方式：**
- API: `appdetails` 的 `genres` 字段
- 需要解析多对多关系

---

### ❌ **3. Descriptions（游戏描述）**
**Predata 结构：**
```csv
app_id, summary, extensive, about
10, "短描述", "详细描述", "关于游戏"
```

**缺失内容：**
- `summary`: 简短摘要
- `extensive`: 详细描述（长文本）
- `about`: 关于游戏内容

**获取方式：**
- API: `appdetails` 的 `short_description`, `detailed_description`, `about_the_game` 字段
- 注意：包含 HTML 标签，需要清理

---

### ❌ **4. Promotional（促销图片等）**
**Predata 结构：**
```csv
app_id, header_image, screenshots, movies, background
```

**缺失内容：**
- 游戏封面图
- 截图链接
- 视频预告片
- 背景图

**获取方式：**
- API: `appdetails` 的 `header_image`, `screenshots`, `movies` 字段

---

### ⚠️ **5. 额外的评论字段**
**Predata 有但当前缺失：**
```csv
metacritic_score           # Metacritic 评分
recommendations            # Steam 推荐数
steamspy_user_score        # SteamSpy 用户评分
steamspy_score_rank        # SteamSpy 排名
steamspy_positive          # SteamSpy 好评
steamspy_negative          # SteamSpy 差评
```

**说明：**
- `metacritic_score`: 来自 Steam API（`appdetails` 的 `metacritic` 字段）
- `recommendations`: Steam 推荐数（API 有提供）
- `steamspy_*`: **需要额外调用 SteamSpy API**（第三方）

---

### ⚠️ **6. 语言支持（详细）**
**Predata 的 games.csv 包含：**
```csv
languages: "English, French, German<strong>*</strong>with full audio"
```

**当前系统：**
- 有 `raw_json` 中包含此数据，但未单独提取

---

## 🎯 数据完整度对比总结

| 数据类别 | Predata | 当前系统 | 状态 |
|---------|---------|----------|------|
| **基础信息** | ✅ | ✅ | **已实现** |
| AppID, 名称, 类型 | ✅ | ✅ | 完全匹配 |
| 发售日期, 价格 | ✅ | ✅ | 完全匹配 |
| **用户标签 (Tags)** | ✅ | ✅ | **已实现（HTML爬取）** |
| **评论统计** | ✅ | ✅ | **已实现（基础字段）** |
| 好评/差评/总数 | ✅ | ✅ | 完全匹配 |
| **分类 (Categories)** | ✅ | ✅ | **✅ 已实现（2026-01-21）** |
| **官方类型 (Genres)** | ✅ | ✅ | **✅ 已实现（2026-01-21）** |
| **游戏描述** | ✅ | ❌ | **缺失（但raw_json有）** |
| **媒体素材** | ✅ | ❌ | **缺失（promotional）** |
| **Metacritic 评分** | ✅ | ❌ | **缺失（但API有）** |
| **SteamSpy 数据** | ✅ | ❌ | **缺失（需第三方API）** |
| **语言支持** | ✅ | 部分 | **raw_json有，未提取** |

---

## 🔧 如何补充缺失数据

### 🟢 **容易实现（API已有数据）**
以下数据可以直接从现有的 `appdetails` API 响应中提取（已在 `raw_json` 中）：

1. **Categories（分类）**
   ```python
   # API 返回示例
   "categories": [
       {"id": 1, "description": "Multi-player"},
       {"id": 2, "description": "Single-player"}
   ]
   ```
   - 实现方式：修改 `src/storage/database.py`，增加 `categories` 表（多对多关系）

2. **Genres（官方类型）**
   ```python
   # API 返回示例
   "genres": [
       {"id": "1", "description": "Action"},
       {"id": "2", "description": "Strategy"}
   ]
   ```
   - 实现方式：增加 `genres` 表

3. **Descriptions（描述）**
   ```python
   "short_description": "..."
   "detailed_description": "..."
   "about_the_game": "..."
   ```
   - 实现方式：在 `games` 表增加 3 列

4. **Metacritic 评分**
   ```python
   "metacritic": {"score": 88}
   ```
   - 实现方式：在 `reviews` 表增加 `metacritic_score` 列

5. **Recommendations（推荐数）**
   ```python
   "recommendations": {"total": 153259}
   ```
   - 实现方式：在 `reviews` 表增加 `recommendations` 列

6. **Promotional（媒体）**
   ```python
   "header_image": "https://..."
   "screenshots": [{"path_thumbnail": "...", "path_full": "..."}]
   "movies": [{"mp4": {"480": "..."}]
   ```
   - 实现方式：增加 `media` 表或在 `games` 表增加列

7. **Languages（语言）**
   ```python
   "supported_languages": "English<strong>*</strong>, French..."
   ```
   - 实现方式：在 `games` 表增加 `languages` 列

### 🟡 **中等难度（需要额外 API）**
8. **SteamSpy 数据**
   - 需要调用：https://steamspy.com/api.php
   - 限速：每秒 1 次请求
   - 字段：`owners`, `average_forever`, `median_forever`, `ccu` 等

---

## 📝 建议实施优先级

### **阶段 1：快速补充（1-2天）**
✅ 已完成：基础信息 + Tags + 评论统计

### **阶段 2：API 数据提取（1天开发）**
1. ✅ **Categories（分类）** - 已完成 2026-01-21
2. ✅ **Genres（官方类型）** - 已完成 2026-01-21
3. ⏳ Descriptions（描述文本）- 待实现
4. ⏳ Metacritic + Recommendations - 待实现
5. ❓ Languages（语言支持）- API 响应中未包含，需进一步调查

**工作量：**
- ✅ 修改 `src/storage/database.py` 增加表/列 - 已完成
- ✅ 无需修改 `src/fetcher/detail.py`（已在提取）- 已确认
- ✅ 无需额外网络请求（数据已在 `raw_json` 中）- 已验证

### **阶段 3：媒体素材（可选）**
6. Promotional（图片/视频链接）
   - 如果只需要链接：简单（API 已有）
   - 如果需要下载图片：复杂（需要大量存储）

### **阶段 4：第三方数据（可选）**
7. SteamSpy 数据
   - 需要额外的爬取模块
   - 会增加 2 倍爬取时间（需要调用第二个 API）

---

## 🎯 最终建议

如果目标是**复刻 Predata 的完整数据**：
1. **立即实施**：阶段 2（API 数据提取）→ 1天开发 + 4天爬取
2. **按需实施**：阶段 3（如果需要图片）
3. **暂时跳过**：阶段 4（SteamSpy 数据价值有限）

**实施阶段 2 后的数据完整度：约 90%**
