import json
import sqlite3
from typing import Dict, Optional
from pathlib import Path
from src.config import settings
from src.logger import logger

class GameStorage:
    """
    Handles storage of game detail data.
    Uses SQLite for structured data and efficiency.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or settings.DATA_DIR / "steam_data.db"
        self._init_db()

    def _init_db(self):
        """Initialize the games table."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Main games table with common query fields extracted
                # and full data stored as JSON blob for flexibility
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS games (
                        steam_appid INTEGER PRIMARY KEY,
                        name TEXT,
                        type TEXT,
                        is_free BOOLEAN,
                        release_date TEXT,
                        price_final INTEGER,
                        currency TEXT,
                        categories_json TEXT,
                        genres_json TEXT,
                        tags_json TEXT,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        raw_json TEXT
                    )
                """)
                
                # Review stats table
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS reviews (
                        steam_appid INTEGER PRIMARY KEY,
                        review_score INTEGER,
                        review_score_desc TEXT,
                        total_positive INTEGER,
                        total_negative INTEGER,
                        total_reviews INTEGER,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Indexes for common lookups
                conn.execute("CREATE INDEX IF NOT EXISTS idx_games_type ON games(type)")
                conn.execute("CREATE INDEX IF NOT EXISTS idx_games_free ON games(is_free)")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize storage DB: {e}")
            raise

    def save_game(self, game_data: Dict):
        """
        Save or update a game record.
        """
        try:
            # Extract fields for columns
            appid = game_data.get("steam_appid")
            name = game_data.get("name")
            gtype = game_data.get("type")
            is_free = game_data.get("is_free")
            release_date = game_data.get("release_date")
            
            price_overview = game_data.get("price_overview") or {}
            price_final = price_overview.get("final")
            currency = price_overview.get("currency")
            
            # Categories, Genres, Tags (optional)
            categories = game_data.get("categories", [])
            categories_json = json.dumps(categories, ensure_ascii=False) if categories else None
            
            genres = game_data.get("genres", [])
            genres_json = json.dumps(genres, ensure_ascii=False) if genres else None
            
            tags = game_data.get("tags", [])
            tags_json = json.dumps(tags, ensure_ascii=False) if tags else None
            
            # Serialize full data for raw_json column
            raw_json = json.dumps(game_data, ensure_ascii=False)

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO games (
                        steam_appid, name, type, is_free, release_date, 
                        price_final, currency, categories_json, genres_json, 
                        tags_json, raw_json, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(steam_appid) DO UPDATE SET
                        name=excluded.name,
                        type=excluded.type,
                        is_free=excluded.is_free,
                        release_date=excluded.release_date,
                        price_final=excluded.price_final,
                        currency=excluded.currency,
                        categories_json=excluded.categories_json,
                        genres_json=excluded.genres_json,
                        tags_json=excluded.tags_json,
                        raw_json=excluded.raw_json,
                        updated_at=CURRENT_TIMESTAMP
                """, (appid, name, gtype, is_free, release_date, price_final, currency, 
                      categories_json, genres_json, tags_json, raw_json))
                
            logger.debug(f"Saved game {appid}: {name}")
            
        except sqlite3.Error as e:
            logger.error(f"Database error saving game {game_data.get('steam_appid')}: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error saving game: {e}")
            raise
            
    def save_reviews(self, appid: int, review_data: Dict):
        """Save review statistics."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO reviews (
                        steam_appid, review_score, review_score_desc, 
                        total_positive, total_negative, total_reviews, updated_at
                    ) VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(steam_appid) DO UPDATE SET
                        review_score=excluded.review_score,
                        review_score_desc=excluded.review_score_desc,
                        total_positive=excluded.total_positive,
                        total_negative=excluded.total_negative,
                        total_reviews=excluded.total_reviews,
                        updated_at=CURRENT_TIMESTAMP
                """, (
                    appid,
                    review_data.get("review_score"),
                    review_data.get("review_score_desc"),
                    review_data.get("total_positive"),
                    review_data.get("total_negative"),
                    review_data.get("total_reviews")
                ))
        except Exception as e:
            logger.error(f"Error saving reviews for {appid}: {e}")
            raise

    def get_game(self, appid: int) -> Optional[Dict]:
        """Retrieve full game data by AppID."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("SELECT raw_json FROM games WHERE steam_appid = ?", (appid,))
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
        except Exception as e:
            logger.error(f"Error retrieving game {appid}: {e}")
            return None

    def get_count(self) -> int:
        """Get total number of stored games."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM games")
            return cursor.fetchone()[0]

# Singleton
game_storage = GameStorage()
