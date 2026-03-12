# System Architecture

## Overview
Steam Store Crawler is a long-running data collection system designed to fetch and maintain a local database of Steam games.

## Modules

1. **Launcher / Entry Point** (`src/main.py`): Handles startup, shutdown, and high-level orchestration.
2. **Configuration** (`src/config.py`): Manages environment variables and runtime settings.
3. **Logging** (`src/logger.py`): Centralized logging for operations, errors, and statistics.
4. **AppID Fetcher** (`src/fetcher/app_list.py`): Retrieves the complete list of AppIDs from Steam.
5. **Scheduler** (`src/scheduler.py`): Manages the task queue (pending, success, failed, skipped).
6. **Detail Fetcher** (`src/fetcher/detail.py`): Fetches game details for specific AppIDs.
7. **Rate Limiter** (`src/utils/rate_limiter.py`): Enforces request limits and handles backoff strategies.
8. **Storage** (`src/storage/`): Handles data persistence (SQLite/JSON).

## Data Flow

1. **Initialization**: `AppListFetcher` gets AppIDs -> Saves JSON -> `Scheduler` imports to SQLite (`tasks` table).
2. **Crawl Loop**:
   - `Scheduler` provides batch of `pending` AppIDs.
   - `DetailFetcher` requests Steam API (via `RateLimiter`).
   - If Valid Game: `GameStorage` saves to SQLite (`games` table).
   - Task Status Updated: `Scheduler` marks task as `success`, `failed`, or `skipped`.

