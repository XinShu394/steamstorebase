import requests
from typing import Optional, Dict, Any
from src.config import settings
from src.logger import logger
from src.utils.rate_limiter import rate_limiter

class DetailFetcher:
    """
    Fetches game details from Steam Store API.
    """
    
    def fetch_details(self, app_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch details for a specific AppID.
        
        Args:
            app_id: The Steam Application ID.
            
        Returns:
            Dict containing game details if successful and valid game, None otherwise.
            Raises requests.RequestException for network issues.
        """
        url = settings.STEAM_STORE_API_URL
        params = {
            "appids": app_id,
            "cc": "us",  # Country code for consistent pricing/currency
            "l": "english" # Language
        }
        
        # Enforce rate limit before request
        rate_limiter.wait()
        
        try:
            logger.debug(f"Fetching details for AppID {app_id}")
            response = requests.get(url, params=params, timeout=settings.REQUEST_TIMEOUT)
            
            # Handle rate limiting (429) specifically if needed, 
            # though requests.raise_for_status() catches 4xx.
            if response.status_code == 429:
                logger.warning(f"Rate limited (429) for AppID {app_id}")
                raise requests.exceptions.HTTPError("429 Client Error: Too Many Requests", response=response)

            response.raise_for_status()
            
            data = response.json()
            
            # Steam Store API returns { "appid": { "success": bool, "data": ... } }
            app_data_wrapper = data.get(str(app_id), {})
            
            if not app_data_wrapper.get("success"):
                logger.warning(f"Steam API reported failure for AppID {app_id}")
                return None
                
            game_data = app_data_wrapper.get("data", {})
            return self._parse_game_data(game_data)
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching AppID {app_id}: {e}")
            raise
        except ValueError as e:
            logger.error(f"Invalid JSON response for AppID {app_id}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error fetching AppID {app_id}: {e}")
            raise

    def _parse_game_data(self, data: Dict) -> Optional[Dict]:
        """
        Parse and filter the raw API response.
        Returns None if the app is not a game (or logic to skip).
        """
        app_type = data.get("type", "unknown")
        
        # Filter: We only want games (and maybe dlc/hardware if needed, but per plan: "Identify real games")
        # Let's keep 'game' and maybe 'dlc' if requested later. For now, strictly 'game'.
        if app_type != "game":
            logger.info(f"Skipping non-game type '{app_type}'")
            return None

        parsed = {
            "steam_appid": data.get("steam_appid"),
            "name": data.get("name"),
            "type": app_type,
            "is_free": data.get("is_free"),
            "short_description": data.get("short_description"),
            "release_date": data.get("release_date", {}).get("date"),
            "developers": data.get("developers", []),
            "publishers": data.get("publishers", []),
            "price_overview": data.get("price_overview", {}),
            "categories": [c["description"] for c in data.get("categories", [])],
            "genres": [g["description"] for g in data.get("genres", [])],
            # Extract tags safely if they exist (sometimes not in standard response without extra params, 
            # but categories/genres are usually there)
        }
        
        return parsed

detail_fetcher = DetailFetcher()
