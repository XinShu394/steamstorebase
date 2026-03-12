import sqlite3
import sys
import shutil
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.config import settings
from src.logger import logger

def hard_reset():
    """
    Completely wipes ALL data and tasks.
    Deletes the database files and snapshots to force a fresh fetch from Steam API.
    """
    data_dir = settings.DATA_DIR
    
    logger.warning(f"🚨 HARD RESET: This will delete ALL files in {data_dir} (DBs, Snapshots).")
    logger.warning("Are you sure? (Run with --force to skip prompt)")
    
    if "--force" not in sys.argv:
        confirm = input("Type 'yes' to confirm: ")
        if confirm != "yes":
            logger.info("Operation cancelled.")
            return

    try:
        # Delete specific files
        for pattern in ["*.db", "*.json", "*.db-wal", "*.db-shm"]:
            for f in data_dir.glob(pattern):
                try:
                    f.unlink()
                    logger.info(f"Deleted: {f.name}")
                except Exception as e:
                    logger.error(f"Failed to delete {f.name}: {e}")
        
        logger.info("✅ Hard reset complete. System will now re-fetch AppList from Steam.")
        
    except Exception as e:
        logger.error(f"Failed to reset: {e}")

if __name__ == "__main__":
    hard_reset()
