import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    # Project Paths
    BASE_DIR = Path(__file__).resolve().parent.parent
    DATA_DIR = BASE_DIR / os.getenv("DATA_DIR", "data")
    LOG_DIR = BASE_DIR / os.getenv("LOG_DIR", "logs")

    # Ensure directories exist
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    # Steam API Settings
    STEAM_API_KEY = os.getenv("STEAM_API_KEY")
    STEAM_APP_LIST_URL_V2 = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
    STEAM_STORE_SERVICE_URL = "https://api.steampowered.com/IStoreService/GetAppList/v1/"
    STEAM_STORE_API_URL = "https://store.steampowered.com/api/appdetails"

    # Rate Limiting & Retry
    REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", 10))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
    RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", 1.5))  # Seconds between requests

    # Storage
    DB_PATH = DATA_DIR / "steam_data.db"
    
    # Validation
    @classmethod
    def validate(cls):
        """Check critical configuration"""
        if not os.access(cls.DATA_DIR, os.W_OK):
            raise PermissionError(f"Data directory {cls.DATA_DIR} is not writable")
        if not os.access(cls.LOG_DIR, os.W_OK):
            raise PermissionError(f"Log directory {cls.LOG_DIR} is not writable")

# Global instance
settings = Config()
