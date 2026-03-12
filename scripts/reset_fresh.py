import sqlite3
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.logger import logger

def reset_database():
    """
    Clears all scraped data (games, reviews) and resets all tasks to PENDING.
    Keeps the AppID list in the tasks table but wipes their progress.
    """
    # Tasks are in tasks.db (controlled by Scheduler), games are in steam_data.db
    # BUT, in src/scheduler/manager.py, we default to "tasks.db"
    # Wait, in src/config.py, DB_PATH is "steam_data.db"
    # Let's check where tasks table actually is.
    # Scheduler init: self.db_path = db_path or settings.DATA_DIR / "tasks.db"
    
    # So we need to clean TWO databases:
    # 1. steam_data.db (Games, Reviews)
    # 2. tasks.db (Tasks)
    
    data_db_path = settings.DATA_DIR / "steam_data.db"
    tasks_db_path = settings.DATA_DIR / "tasks.db"

    logger.warning(f"⚠️  WARNING: This will WIPE scraped data in {data_db_path} and reset tasks in {tasks_db_path}.")
    logger.warning("Are you sure? (Run with --force to skip prompt)")
    
    if "--force" not in sys.argv:
        confirm = input("Type 'yes' to confirm: ")
        if confirm != "yes":
            logger.info("Operation cancelled.")
            return

    try:
        # 1. Clear Data DB
        if data_db_path.exists():
            with sqlite3.connect(data_db_path) as conn:
                logger.info("Truncating 'games' table...")
                conn.execute("DELETE FROM games")
                logger.info("Truncating 'reviews' table...")
                conn.execute("DELETE FROM reviews")
            
            # Vacuum must be outside transaction (autocommit mode)
            with sqlite3.connect(data_db_path, isolation_level=None) as conn:
                conn.execute("VACUUM")
        
        # 2. Reset Tasks DB
        if tasks_db_path.exists():
            with sqlite3.connect(tasks_db_path) as conn:
                logger.info("Resetting all tasks to 'pending'...")
                conn.execute("""
                    UPDATE tasks 
                    SET status = 'pending', 
                        retries = 0, 
                        last_updated = 0, 
                        error_msg = NULL
                """)
            
            with sqlite3.connect(tasks_db_path, isolation_level=None) as conn:
                conn.execute("VACUUM")
            
        logger.info("✅ Database reset complete. Ready for fresh crawl.")
        
    except Exception as e:
        logger.error(f"Failed to reset database: {e}")

if __name__ == "__main__":
    reset_database()
