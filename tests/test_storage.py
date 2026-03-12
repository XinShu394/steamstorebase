import unittest
import sqlite3
import json
from pathlib import Path
from src.storage.database import GameStorage

class TestGameStorage(unittest.TestCase):
    def setUp(self):
        self.test_db = Path("test_games.db")
        if self.test_db.exists():
            try:
                self.test_db.unlink()
            except:
                pass
        self.storage = GameStorage(db_path=self.test_db)
        
        self.sample_game = {
            "steam_appid": 10,
            "name": "Counter-Strike",
            "type": "game",
            "is_free": False,
            "release_date": "2000-11-01",
            "price_overview": {"final": 999, "currency": "USD"},
            "categories": ["Multi-player"]
        }

    def tearDown(self):
        # Close connection implicitly by letting object die
        if self.test_db.exists():
            try:
                self.test_db.unlink()
            except:
                pass

    def test_save_and_get(self):
        # Save
        self.storage.save_game(self.sample_game)
        
        # Verify count
        self.assertEqual(self.storage.get_count(), 1)
        
        # Get
        retrieved = self.storage.get_game(10)
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved['name'], "Counter-Strike")
        self.assertEqual(retrieved['price_overview']['currency'], "USD")

    def test_upsert_update(self):
        self.storage.save_game(self.sample_game)
        
        # Update name
        updated_game = self.sample_game.copy()
        updated_game['name'] = "CS 1.6"
        self.storage.save_game(updated_game)
        
        # Verify update
        self.assertEqual(self.storage.get_count(), 1)
        retrieved = self.storage.get_game(10)
        self.assertEqual(retrieved['name'], "CS 1.6")

    def test_persistence_check(self):
        """Verify SQL columns are populated correctly alongside JSON"""
        self.storage.save_game(self.sample_game)
        
        with sqlite3.connect(self.test_db) as conn:
            cursor = conn.execute("SELECT name, price_final, currency FROM games WHERE steam_appid=10")
            row = cursor.fetchone()
            self.assertEqual(row[0], "Counter-Strike")
            self.assertEqual(row[1], 999)
            self.assertEqual(row[2], "USD")

if __name__ == '__main__':
    unittest.main()
