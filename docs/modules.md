# Module Documentation

## 1. Configuration
- **File**: `src/config.py`
- **Responsibility**: Load and validate settings. Centralizes paths, API URLs, and rate limits.
- **Inputs**: `.env` file, environment variables.
- **Outputs**: `settings` object (Singleton).
- **Key Parameters**:
    - `DATA_DIR`: Path to data storage.
    - `LOG_DIR`: Path to logs.
    - `RATE_LIMIT_DELAY`: Delay between requests.

## 2. Logging
- **File**: `src/logger.py`
- **Responsibility**: Consistent logging to file and console using `loguru`.
- **Outputs**:
    - Console (INFO+)
    - `logs/app_YYYY-MM-DD.log` (DEBUG+, 10 days retention)
    - `logs/error_YYYY-MM-DD.log` (ERROR+, 30 days retention)

## 3. AppID Fetcher
- **File**: `src/fetcher/app_list.py`
- **Responsibility**: Fetch and store the complete list of Steam AppIDs.
- **Inputs**: 
    - `IStoreService/GetAppList/v1` (with API Key, Primary)
    - `ISteamApps/GetAppList/v2` (Legacy fallback)
- **Outputs**: 
    - JSON Snapshot: `data/app_list_YYYYMMDD_HHMMSS.json`
    - List of AppID dictionaries in memory.
- **Key Methods**:
    - `fetch_all()`: Orchestrates fetching strategy.
    - `_fetch_with_key()`: Paginates through official API.
    - `save_snapshot()`: Persists data to disk.
    - `get_latest_snapshot()`: Retrieves most recent local data.

## 4. Scheduler
- **File**: `src/scheduler/manager.py`
- **Responsibility**: Manage task queue using SQLite.
- **Inputs**: JSON Snapshot from AppID Fetcher.
- **Outputs**: Batch of `Task` objects.
- **Key Methods**:
    - `load_from_snapshot()`: Import new AppIDs.
    - `get_next_batch()`: Retrieve pending tasks.
    - `update_task()`: Save task result.
    - `reset_failed_tasks()`: Retry logic.

## 5. Detail Fetcher
- **File**: `src/fetcher/detail.py`
- **Responsibility**: Fetch individual game data from Steam Store API.
- **Inputs**: AppID.
- **Outputs**: Parsed game dictionary (or `None` if skipped/failed).
- **Key Features**:
    - Integrated `RateLimiter`.
    - Filters non-game types (e.g., videos, hardware).
    - Parses JSON to flat/clean structure.

## 6. Storage
- **File**: `src/storage/database.py`
- **Responsibility**: Store structured game data.
- **Backing**: SQLite (`steam_data.db`).
- **Schema**: `games` table with hybrid approach (SQL columns for queryable fields + JSON blob for full data).
- **Key Fields** (as of 2026-01-21):
    - `steam_appid`, `name`, `type`, `is_free`, `release_date`, `price_final`, `currency`
    - `categories_json`: Steam categories (Single-player, Achievements, etc.) - **NEW**
    - `genres_json`: Official genres (Action, RPG, etc.) - **NEW**
    - `tags_json`: User-defined tags (~20 items)
    - `raw_json`: Full API response
- **Key Methods**:
    - `save_game()`: Upsert (Insert or Update) logic.
    - `get_game()`: Retrieve by ID.
    - `save_reviews()`: Upsert review stats.

## 7. Main Service
- **File**: `src/main.py`
- **Responsibility**: Orchestrate the entire crawling process.
- **Key Features**:
    - Initializes AppID list (fetch if missing).
    - Cyclic loop: Get Batch -> Process -> Save -> Update Status.
    - Graceful shutdown on `SIGINT` (Ctrl+C).

## 8. Review Fetcher
- **File**: `src/fetcher/reviews.py`
- **Responsibility**: Fetch review statistics (score, positive/negative counts).
- **Endpoint**: `store.steampowered.com/appreviews/`

## 9. Tag Fetcher
- **File**: `src/fetcher/tags.py`
- **Responsibility**: Scrape User Tags from Store HTML.
- **Source**: `store.steampowered.com/app/{appid}`

## 10. Rate Limiter
- **File**: `src/utils/rate_limiter.py`
- **Responsibility**: Control outgoing request frequency.
- **Mechanism**: Sleep-based with random jitter.

(More to be added as implemented)
