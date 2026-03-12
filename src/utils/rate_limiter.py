import time
import random
from src.config import settings
from src.logger import logger

class RateLimiter:
    """
    Simple Token Bucket or Sleep-based Rate Limiter.
    Currently implements a sleep-based approach with jitter.
    """
    
    def __init__(self):
        self.delay = settings.RATE_LIMIT_DELAY
        self.last_request_time = 0.0

    def wait(self):
        """
        Block execution until enough time has passed since the last request.
        Adds a small random jitter to avoid fixed-pattern detection.
        """
        now = time.time()
        elapsed = now - self.last_request_time
        
        # Calculate needed wait time
        wait_time = self.delay - elapsed
        
        # Add jitter (0% to 20% extra delay)
        jitter = self.delay * random.uniform(0, 0.2)
        
        if wait_time > 0:
            total_sleep = wait_time + jitter
            time.sleep(total_sleep)
        
        self.last_request_time = time.time()

# Global instance
rate_limiter = RateLimiter()
