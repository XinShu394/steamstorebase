import json
import requests
import time
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

from src.config import settings
from src.logger import logger
from src.utils.rate_limiter import rate_limiter

class AppListFetcher:
    """
    Module responsible for fetching the complete list of AppIDs from Steam.
    Supports both IStoreService (v1, with Key) and ISteamApps (v2, no Key).
    """
    
    def fetch_all(self) -> List[Dict]:
        """
        Fetch all AppIDs.
        Prioritizes IStoreService if API Key is present.
        """
        if settings.STEAM_API_KEY:
            logger.info("API Key found. Using IStoreService (v1)...")
            return self._fetch_with_key()
        else:
            logger.info("No API Key. Using ISteamApps (v2)...")
            return self._fetch_legacy()

    def _fetch_with_key(self) -> List[Dict]:
        """
        Fetch using IStoreService/GetAppList/v1 (Requires Key).
        This endpoint uses pagination.
        """
        all_apps = []
        last_appid = 0
        has_more = True
        
        url = settings.STEAM_STORE_SERVICE_URL
        batch_size = 10000  # Max allowed by Steam is usually around this or 50k
        
        while has_more:
            params = {
                "key": settings.STEAM_API_KEY,
                "include_games": 1,
                "include_dlc": 1,
                "include_software": 1,
                "include_videos": 0, # Skip videos
                "include_hardware": 0,
                "last_appid": last_appid,
                "max_results": batch_size
            }
            
            success = False
            for attempt in range(settings.MAX_RETRIES):
                try:
                    # rate limit per request page
                    rate_limiter.wait()
                    
                    logger.debug(f"Fetching page starting after AppID {last_appid} (Attempt {attempt + 1})")
                    resp = requests.get(url, params=params, timeout=settings.REQUEST_TIMEOUT)
                    resp.raise_for_status()
                    data = resp.json()
                    
                    response_body = data.get("response", {})
                    apps = response_body.get("apps", [])
                    
                    if not apps:
                        has_more = False
                        success = True
                        break
                        
                    all_apps.extend(apps)
                    last_appid = apps[-1].get("appid")
                    
                    logger.info(f"Fetched {len(apps)} apps (Last AppID: {last_appid}). Total so far: {len(all_apps)}")
                    success = True
                    break
                    
                except requests.RequestException as e:
                    logger.warning(f"Request failed (Attempt {attempt + 1}/{settings.MAX_RETRIES}): {e}")
                    time.sleep(2 * (attempt + 1)) # Exponential backoff
                except Exception as e:
                    logger.error(f"Unexpected error during page fetch: {e}")
                    # For critical parsing errors, maybe stop? Or retry?
                    # Retry usually safest for transient issues.
                    time.sleep(2)
            
            if not success:
                logger.error("Max retries exceeded for AppList page. Aborting fetch.")
                # We could return what we have so far, or raise.
                # Since incomplete list might be misleading, raising is safer to trigger restart.
                raise Exception("Max retries exceeded while fetching AppID list")

        logger.info(f"Finished fetching. Total apps: {len(all_apps)}")
        return all_apps

    def _fetch_legacy(self) -> List[Dict]:
        """
        Fetch using legacy ISteamApps/GetAppList/v2.
        """
        url = settings.STEAM_APP_LIST_URL_V2
        try:
            response = requests.get(url, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return data.get("applist", {}).get("apps", [])
        except Exception as e:
            logger.error(f"Legacy fetch failed: {e}")
            raise

    def save_snapshot(self, apps: List[Dict]) -> Path:
        """
        Save the fetched AppIDs to a JSON snapshot file.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"app_list_{timestamp}.json"
        file_path = settings.DATA_DIR / filename
        
        try:
            logger.info(f"Saving AppID snapshot to {file_path}")
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(apps, f, ensure_ascii=False, indent=2)
            
            logger.info(f"Snapshot saved successfully: {file_path}")
            return file_path
        except Exception as e:
            logger.error(f"Failed to save snapshot: {e}")
            raise

    def get_latest_snapshot(self) -> Optional[Path]:
        """
        Find the most recent AppID snapshot file.
        """
        try:
            files = list(settings.DATA_DIR.glob("app_list_*.json"))
            if not files:
                return None
            latest = sorted(files, key=lambda x: x.name, reverse=True)[0]
            logger.debug(f"Found latest snapshot: {latest}")
            return latest
        except Exception as e:
            logger.error(f"Error finding latest snapshot: {e}")
            return None

app_list_fetcher = AppListFetcher()
