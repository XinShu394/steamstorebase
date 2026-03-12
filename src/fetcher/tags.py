import requests
from typing import Optional, List
from bs4 import BeautifulSoup
from src.config import settings
from src.logger import logger
from src.utils.rate_limiter import rate_limiter

class TagFetcher:
    """
    Fetches User Tags from the Steam Store page HTML.
    """
    
    def fetch_tags(self, app_id: int) -> List[str]:
        """
        Scrape user tags from the store page.
        Returns empty list if failed or no tags found.
        """
        url = f"https://store.steampowered.com/app/{app_id}"
        # Cookie to bypass age check
        cookies = {'birthtime': '0', 'mature_content': '1'}
        
        # Enforce rate limit (Store pages are heavy, maybe respect rate limit strictly)
        rate_limiter.wait()
        
        try:
            response = requests.get(url, cookies=cookies, timeout=settings.REQUEST_TIMEOUT)
            
            # 404 means page doesn't exist (maybe removed or region locked)
            if response.status_code == 404:
                logger.warning(f"Store page not found (404) for AppID {app_id}")
                return []
                
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Steam store usually puts tags in a div with class 'glance_tags'
            tags_container = soup.find('div', class_='glance_tags')
            
            if tags_container:
                # Tags are in <a> tags with class 'app_tag'
                tags = [
                    tag.get_text(strip=True) 
                    for tag in tags_container.find_all('a', class_='app_tag')
                ]
                # Filter out the '+' add button text if present
                tags = [t for t in tags if t != '+']
                
                return tags
            
            return []
            
        except requests.RequestException as e:
            logger.error(f"Network error fetching tags for {app_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error parsing tags for {app_id}: {e}")
            return []

tag_fetcher = TagFetcher()
