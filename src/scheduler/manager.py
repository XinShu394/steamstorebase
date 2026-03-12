import json
import sqlite3
from typing import List, Optional, Generator
from pathlib import Path
from src.scheduler.task import Task, TaskStatus
from src.logger import logger
from src.config import settings

class Scheduler:
    """
    Manages the crawling task queue using SQLite for persistence.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATA_DIR / "tasks.db"
        self._init_db()

    def _init_db(self):
        """Initialize SQLite database for tasks."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS tasks (
                        app_id INTEGER PRIMARY KEY,
                        name TEXT,
                        status TEXT DEFAULT 'pending',
                        retries INTEGER DEFAULT 0,
                        last_updated REAL DEFAULT 0,
                        error_msg TEXT
                    )
                """)
                conn.execute("CREATE INDEX IF NOT EXISTS idx_status ON tasks(status)")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize scheduler DB: {e}")
            raise

    def load_from_snapshot(self, snapshot_path: Path):
        """
        Load tasks from an AppID list snapshot JSON.
        Only adds new AppIDs; does not overwrite existing task status.
        """
        logger.info(f"Loading tasks from snapshot: {snapshot_path}")
        try:
            with open(snapshot_path, "r", encoding="utf-8") as f:
                apps = json.load(f)
            
            new_tasks = 0
            with sqlite3.connect(self.db_path) as conn:
                for app in apps:
                    try:
                        # INSERT OR IGNORE to keep existing status for old apps
                        conn.execute(
                            "INSERT OR IGNORE INTO tasks (app_id, name, status) VALUES (?, ?, ?)",
                            (app["appid"], app["name"], TaskStatus.PENDING.value)
                        )
                        if conn.total_changes > 0:
                            new_tasks += 1
                    except KeyError:
                        continue # Skip malformed entries
            
            logger.info(f"Loaded {len(apps)} apps. Added {new_tasks} new tasks.")
            
        except Exception as e:
            logger.error(f"Error loading snapshot: {e}")
            raise

    def get_next_batch(self, batch_size: int = 10) -> List[Task]:
        """Get a batch of pending tasks."""
        tasks = []
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute(
                "SELECT * FROM tasks WHERE status = ? LIMIT ?",
                (TaskStatus.PENDING.value, batch_size)
            )
            for row in cursor:
                tasks.append(Task.from_dict(dict(row)))
        return tasks

    def update_task(self, task: Task):
        """Update a single task's status in DB."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                UPDATE tasks 
                SET status = ?, retries = ?, last_updated = ?, error_msg = ?
                WHERE app_id = ?
                """,
                (task.status.value, task.retries, task.last_updated, task.error_msg, task.app_id)
            )

    def get_stats(self) -> dict:
        """Get counts of tasks by status."""
        stats = {}
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT status, COUNT(*) FROM tasks GROUP BY status")
            for status, count in cursor:
                stats[status] = count
        return stats

    def reset_failed_tasks(self, max_retries: int = 3):
        """Reset failed tasks to pending if they haven't exceeded max retries."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE tasks SET status = ? WHERE status = ? AND retries < ?",
                (TaskStatus.PENDING.value, TaskStatus.FAILED.value, max_retries)
            )
            logger.info(f"Reset failed tasks (retries < {max_retries})")

# Singleton
scheduler = Scheduler()
