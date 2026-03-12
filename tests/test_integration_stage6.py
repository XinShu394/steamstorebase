import unittest
import sqlite3
import json
import time
import tempfile
import shutil
import gc
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.scheduler.manager import Scheduler
from src.scheduler.task import Task, TaskStatus
from src.fetcher.detail import DetailFetcher
from src.storage.database import GameStorage
from src.utils.rate_limiter import RateLimiter
from src.config import settings

class TestStage6Integration(unittest.TestCase):
    def setUp(self):
        # Create temp directory
        self.test_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.test_dir)
        
        # Override settings paths
        self.original_data_dir = settings.DATA_DIR
        settings.DATA_DIR = self.temp_path
        
        # DB Paths
        self.tasks_db = self.temp_path / "tasks.db"
        self.games_db = self.temp_path / "steam_data.db"

    def tearDown(self):
        settings.DATA_DIR = self.original_data_dir
        # Force garbage collection to close any lingering DB connections
        gc.collect()
        
        # Retry removal for Windows file locking issues
        retries = 5
        for i in range(retries):
            try:
                if os.path.exists(self.test_dir):
                    shutil.rmtree(self.test_dir)
                break
            except PermissionError:
                if i < retries - 1:
                    time.sleep(0.2)
                else:
                    print(f"Warning: Could not remove temp dir {self.test_dir}")

    def test_scheduler_lifecycle(self):
        """Test Scheduler: Init -> Load -> Get Batch -> Update"""
        scheduler = Scheduler(db_path=self.tasks_db)
        
        # 1. Create a dummy snapshot
        snapshot_file = self.temp_path / "app_snapshot.json"
        mock_apps = [
            {"appid": 10, "name": "Game 1"},
            {"appid": 20, "name": "Game 2"},
            {"appid": 30, "name": "Game 3"}
        ]
        with open(snapshot_file, "w") as f:
            json.dump(mock_apps, f)
            
        # 2. Load Snapshot
        scheduler.load_from_snapshot(snapshot_file)
        stats = scheduler.get_stats()
        self.assertEqual(stats["pending"], 3)
        
        # 3. Get Batch
        batch = scheduler.get_next_batch(batch_size=2)
        self.assertEqual(len(batch), 2)
        self.assertEqual(batch[0].app_id, 10)
        
        # 4. Update Task
        task = batch[0]
        task.mark_success()
        scheduler.update_task(task)
        
        # Verify update
        stats = scheduler.get_stats()
        self.assertEqual(stats["success"], 1)
        self.assertEqual(stats["pending"], 2)
        
        # Verify persistence
        scheduler2 = Scheduler(db_path=self.tasks_db)
        batch2 = scheduler2.get_next_batch(batch_size=10)
        self.assertEqual(len(batch2), 2) # Only 2 pending left (20 and 30)
        self.assertEqual(batch2[0].app_id, 20)

    @patch('src.fetcher.detail.requests.get')
    def test_detail_fetcher(self, mock_get):
        """Test DetailFetcher: Network -> Parse -> Filter"""
        fetcher = DetailFetcher()
        
        # Mock Response for a valid game
        mock_response = MagicMock()
        mock_data = {
            "10": {
                "success": True,
                "data": {
                    "type": "game",
                    "name": "Counter-Strike",
                    "steam_appid": 10,
                    "is_free": False,
                    "price_overview": {"final": 999, "currency": "USD"}
                }
            }
        }
        mock_response.json.return_value = mock_data
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        
        # Test Valid Game
        # Patch RateLimiter to avoid waiting during tests
        with patch('src.utils.rate_limiter.time.sleep'):
            result = fetcher.fetch_details(10)
            
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Counter-Strike")
        self.assertEqual(result["price_overview"]["final"], 999)
        
        # Test Non-Game Filter
        mock_data_dlc = {
            "20": {
                "success": True,
                "data": {
                    "type": "dlc",
                    "name": "CS DLC",
                    "steam_appid": 20
                }
            }
        }
        mock_response.json.return_value = mock_data_dlc
        
        with patch('src.utils.rate_limiter.time.sleep'):
            result_dlc = fetcher.fetch_details(20)
            
        self.assertIsNone(result_dlc) # Should filter out DLC

    def test_game_storage(self):
        """Test GameStorage: Save -> Retrieve -> Update"""
        storage = GameStorage(db_path=self.games_db)
        
        game_data = {
            "steam_appid": 10,
            "name": "Test Game",
            "type": "game",
            "is_free": True,
            "release_date": "2020-01-01",
            "price_overview": {"final": 0, "currency": "USD"},
            "developers": ["Valve"]
        }
        
        # 1. Save
        storage.save_game(game_data)
        self.assertEqual(storage.get_count(), 1)
        
        # 2. Retrieve
        loaded = storage.get_game(10)
        self.assertEqual(loaded["name"], "Test Game")
        self.assertEqual(loaded["developers"], ["Valve"])
        
        # 3. Update (Upsert)
        game_data["name"] = "Test Game Updated"
        storage.save_game(game_data)
        
        loaded_v2 = storage.get_game(10)
        self.assertEqual(loaded_v2["name"], "Test Game Updated")
        self.assertEqual(storage.get_count(), 1) # Count should remain 1

    @patch('src.utils.rate_limiter.time.sleep')
    @patch('src.utils.rate_limiter.time.time')
    def test_rate_limiter(self, mock_time, mock_sleep):
        """Test RateLimiter logic"""
        limiter = RateLimiter()
        limiter.delay = 1.0
        
        # First call: last_request_time is 0, should wait
        mock_time.return_value = 100.0 # Current time
        limiter.last_request_time = 99.5 # 0.5s ago
        
        limiter.wait()
        
        # Expected wait: 1.0 - 0.5 = 0.5s (plus jitter)
        self.assertTrue(mock_sleep.called)
        # Check if sleep was called with value > 0.5
        args, _ = mock_sleep.call_args
        self.assertGreaterEqual(args[0], 0.5)

if __name__ == '__main__':
    unittest.main()
