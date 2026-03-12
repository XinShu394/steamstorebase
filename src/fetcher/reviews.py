import requests
from typing import Optional, Dict
from src.config import settings
from src.logger import logger
from src.utils.rate_limiter import rate_limiter

class ReviewFetcher:
    """
    Fetches review statistics (positive/negative counts, score) from Steam.
    Uses store.steampowered.com/appreviews/ endpoint.
    """
    
    def fetch_reviews(self, app_id: int) -> Optional[Dict]:
        """
        Fetch review summary for a given AppID.
        """
        url = f"https://store.steampowered.com/appreviews/{app_id}"
        params = {
            "json": 1,
            "language": "all",
            "purchase_type": "all",  # steam or non_steam_purchase
            "num_per_page": 0        # We only want the summary, not the text reviews
        }
        
        # Enforce rate limit
        rate_limiter.wait()
        
        try:
            response = requests.get(url, params=params, timeout=settings.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            if data.get("success") != 1:
                logger.warning(f"Review API success!=1 for AppID {app_id}")
                return None
                
            query_summary = data.get("query_summary", {})
            
            return {
                "review_score": query_summary.get("review_score"),
                "review_score_desc": query_summary.get("review_score_desc"),
                "total_positive": query_summary.get("total_positive"),
                "total_negative": query_summary.get("total_negative"),
                "total_reviews": query_summary.get("total_reviews"),
            }
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching reviews for {app_id}: {e}")
            raise
        except ValueError:
            logger.error(f"Invalid JSON for review fetch {app_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching reviews for {app_id}: {e}")
            raise

review_fetcher = ReviewFetcher()
