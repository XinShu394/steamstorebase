import requests
import re
from bs4 import BeautifulSoup

def probe_store_page(appid):
    url = f"https://store.steampowered.com/app/{appid}"
    cookies = {'birthtime': '0', 'mature_content': '1'} # Bypass age gate
    
    print(f"Probing Store Page: {url}")
    try:
        resp = requests.get(url, cookies=cookies, timeout=10)
        if resp.status_code != 200:
            print(f"Failed: {resp.status_code}")
            return
            
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Method 1: Look for 'glance_tags' class
        tags_container = soup.find('div', class_='glance_tags')
        if tags_container:
            tags = [a.get_text(strip=True) for a in tags_container.find_all('a', class_='app_tag')]
            print(f"Found Tags (HTML): {tags}")
        else:
            print("No tags found in HTML")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    probe_store_page(10) # Counter-Strike
