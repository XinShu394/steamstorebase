import unittest
from unittest.mock import patch, MagicMock
import json
import shutil
import tempfile
from pathlib import Path
from src.fetcher.app_list import AppListFetcher
from src.config import settings

class TestAppListFetcher(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for data storage during tests
        self.test_dir = tempfile.mkdtemp()
        self.original_data_dir = settings.DATA_DIR
        # Patch settings.DATA_DIR to use the temp directory
        settings.DATA_DIR = Path(self.test_dir)
        self.fetcher = AppListFetcher()

    def tearDown(self):
        # Restore original DATA_DIR and remove temp directory
        settings.DATA_DIR = self.original_data_dir
        shutil.rmtree(self.test_dir)

    @patch('src.fetcher.app_list.requests.get')
    def test_fetch_all_success(self, mock_get):
        # Mock successful API response
        mock_response = MagicMock()
        mock_data = {
            "applist": {
                "apps": [
                    {"appid": 10, "name": "Counter-Strike"},
                    {"appid": 20, "name": "Team Fortress Classic"}
                ]
            }
        }
        mock_response.json.return_value = mock_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        apps = self.fetcher.fetch_all()
        
        self.assertEqual(len(apps), 2)
        self.assertEqual(apps[0]['appid'], 10)
        self.assertEqual(apps[1]['name'], "Team Fortress Classic")
        mock_get.assert_called_once_with(settings.STEAM_APP_LIST_URL, timeout=settings.REQUEST_TIMEOUT)

    @patch('src.fetcher.app_list.requests.get')
    def test_fetch_all_empty(self, mock_get):
        # Mock empty API response
        mock_response = MagicMock()
        mock_data = {"applist": {"apps": []}}
        mock_response.json.return_value = mock_data
        mock_get.return_value = mock_response

        apps = self.fetcher.fetch_all()
        self.assertEqual(apps, [])

    def test_save_snapshot(self):
        apps = [
            {"appid": 10, "name": "Test App 1"},
            {"appid": 20, "name": "Test App 2"}
        ]
        
        saved_path = self.fetcher.save_snapshot(apps)
        
        self.assertTrue(saved_path.exists())
        self.assertTrue(saved_path.name.startswith("app_list_"))
        self.assertTrue(saved_path.name.endswith(".json"))
        
        with open(saved_path, 'r', encoding='utf-8') as f:
            saved_data = json.load(f)
            self.assertEqual(saved_data, apps)

    def test_get_latest_snapshot(self):
        # Case 1: No files
        self.assertIsNone(self.fetcher.get_latest_snapshot())
        
        # Case 2: Create multiple files with different timestamps
        file1 = settings.DATA_DIR / "app_list_20230101_100000.json"
        file2 = settings.DATA_DIR / "app_list_20230102_100000.json"
        file3 = settings.DATA_DIR / "app_list_20230101_090000.json"
        
        file1.touch()
        file2.touch()
        file3.touch()
        
        latest = self.fetcher.get_latest_snapshot()
        self.assertIsNotNone(latest)
        self.assertEqual(latest.name, "app_list_20230102_100000.json")

    def test_full_workflow(self):
        """Verify the full flow: fetch -> save -> get latest"""
        # 1. Mock Fetch
        with patch('src.fetcher.app_list.requests.get') as mock_get:
            mock_response = MagicMock()
            mock_data = {
                "applist": {
                    "apps": [
                        {"appid": 1, "name": "Flow Test Game"}
                    ]
                }
            }
            mock_response.json.return_value = mock_data
            mock_get.return_value = mock_response
            
            apps = self.fetcher.fetch_all()
            self.assertEqual(len(apps), 1)
            
            # 2. Save
            saved_path = self.fetcher.save_snapshot(apps)
            self.assertTrue(saved_path.exists())
            
            # 3. Get Latest
            latest_path = self.fetcher.get_latest_snapshot()
            self.assertEqual(saved_path, latest_path)
            
            # Verify content
            with open(latest_path, 'r', encoding='utf-8') as f:
                content = json.load(f)
                self.assertEqual(content[0]['name'], "Flow Test Game")

if __name__ == '__main__':
    unittest.main()
