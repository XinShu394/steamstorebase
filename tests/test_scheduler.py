import json
import unittest
import time
from pathlib import Path
from src.scheduler.manager import Scheduler
from src.scheduler.task import TaskStatus

class TestScheduler(unittest.TestCase):
    def setUp(self):
        # Use a temporary DB for testing
        self.test_db = Path("test_tasks.db")
        # Ensure clean state
        if self.test_db.exists():
            try:
                self.test_db.unlink()
            except PermissionError:
                pass # Might be held by previous run, ignore for now

        self.scheduler = Scheduler(db_path=self.test_db)
        
        # Create a dummy snapshot
        self.snapshot_path = Path("test_snapshot.json")
        self.mock_data = [
            {"appid": 1, "name": "Game 1"},
            {"appid": 2, "name": "Game 2"},
            {"appid": 3, "name": "Game 3"}
        ]
        with open(self.snapshot_path, "w") as f:
            json.dump(self.mock_data, f)

    def tearDown(self):
        # Force close connections implicitly by not holding refs
        # But sqlite3 connection in Scheduler is context managed in methods, 
        # however __init__ calls _init_db which uses a context manager.
        # The issue is that we don't have a persistent connection in the class,
        # but the file might still be locked by the OS briefly or due to race conditions.
        
        if self.snapshot_path.exists():
            try:
                self.snapshot_path.unlink()
            except PermissionError:
                pass

        # Try to delete DB
        if self.test_db.exists():
            try:
                self.test_db.unlink()
            except PermissionError:
                # Windows file locking can be tricky.
                # In real tests, we might use a temp dir or unique name per test.
                pass

    def test_load_and_retrieve(self):
        # Load snapshot
        self.scheduler.load_from_snapshot(self.snapshot_path)
        
        # Check stats
        stats = self.scheduler.get_stats()
        self.assertEqual(stats["pending"], 3)
        
        # Get batch
        batch = self.scheduler.get_next_batch(batch_size=2)
        self.assertEqual(len(batch), 2)
        self.assertEqual(batch[0].app_id, 1)
        
        # Update task
        task = batch[0]
        task.mark_success()
        self.scheduler.update_task(task)
        
        # Verify update
        stats = self.scheduler.get_stats()
        self.assertEqual(stats["success"], 1)
        self.assertEqual(stats["pending"], 2)

    def test_idempotency(self):
        # Load twice
        self.scheduler.load_from_snapshot(self.snapshot_path)
        self.scheduler.load_from_snapshot(self.snapshot_path)
        
        stats = self.scheduler.get_stats()
        # Should still be 3, not 6.
        # Note: If previous test failed to clean up, this might be affected if DB persists.
        # But we try to clean in setUp.
        self.assertEqual(stats["pending"], 3) 

if __name__ == '__main__':
    unittest.main()
