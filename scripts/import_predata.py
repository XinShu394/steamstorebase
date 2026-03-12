import csv
import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.storage.database import game_storage
from src.logger import logger
from src.scheduler.manager import scheduler

PREDATA_DIR = Path("d:/腾讯/数据库测试/steamstoreCT/predata")
GAMES_CSV = PREDATA_DIR / "games/games.csv"

def parse_price(price_str):
    try:
        if not price_str or price_str == '\\N':
            return None
        data = json.loads(price_str)
        return data
    except:
        return None

def import_games():
    if not GAMES_CSV.exists():
        logger.error(f"Games CSV not found at {GAMES_CSV}")
        return

    logger.info(f"Starting import from {GAMES_CSV}")
    
    count = 0
    tasks_count = 0
    
    # Increase CSV field limit just in case
    # On Windows, sys.maxsize can be larger than C long
    try:
        csv.field_size_limit(2147483647)
    except OverflowError:
        csv.field_size_limit(sys.maxsize)

    # Connect to tasks DB manually for batch performance
    tasks_db_path = scheduler.db_path
    
    try:
        import sqlite3
        tasks_conn = sqlite3.connect(tasks_db_path)
        tasks_conn.execute("PRAGMA journal_mode = WAL")
        tasks_conn.execute("PRAGMA synchronous = NORMAL")
        
        with open(GAMES_CSV, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # buffer for tasks
            task_buffer = []
            
            for row in reader:
                try:
                    appid = int(row['app_id'])
                    name = row['name']
                    
                    # Parse fields
                    is_free = row['is_free'] == '1'
                    price_data = parse_price(row['price_overview'])
                    
                    game_data = {
                        "steam_appid": appid,
                        "name": name,
                        "type": row['type'],
                        "is_free": is_free,
                        "release_date": row['release_date'],
                        "price_overview": price_data,
                        "languages": row['languages']
                    }
                    
                    # Save to DB (GameStorage handles its own transactions, might be slow for bulk but safer)
                    game_storage.save_game(game_data)
                    
                    # Add to task buffer
                    task_buffer.append((appid, name, 'success', 0, datetime.now().timestamp()))
                    
                    count += 1
                    if count % 1000 == 0:
                        # Flush tasks
                        tasks_conn.executemany(
                            "INSERT OR IGNORE INTO tasks (app_id, name, status, retries, last_updated) VALUES (?, ?, ?, ?, ?)",
                            task_buffer
                        )
                        tasks_conn.commit()
                        task_buffer = []
                        logger.info(f"Imported {count} games...")
                        
                except Exception as e:
                    logger.error(f"Error importing row {row.get('app_id')}: {e}")
                    continue
            
            # Flush remaining
            if task_buffer:
                tasks_conn.executemany(
                    "INSERT OR IGNORE INTO tasks (app_id, name, status, retries, last_updated) VALUES (?, ?, ?, ?, ?)",
                    task_buffer
                )
                tasks_conn.commit()

        tasks_conn.close()
        logger.info(f"Import complete. Total imported: {count}")

    except Exception as e:
        logger.error(f"Fatal error during import: {e}")


if __name__ == "__main__":
    import_games()
