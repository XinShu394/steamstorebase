import time
import signal
import sys
import argparse
from typing import Optional

from src.config import settings
from src.logger import logger
from src.fetcher.app_list import app_list_fetcher
from src.scheduler.manager import scheduler
from src.scheduler.task import Task
from src.fetcher.detail import detail_fetcher
from src.fetcher.reviews import review_fetcher
from src.fetcher.tags import tag_fetcher
from src.storage.database import game_storage

class CrawlerService:
    def __init__(self, max_tasks: Optional[int] = None):
        self.running = True
        self.batch_size = 10
        self.max_tasks = max_tasks  # For testing: limit total tasks processed
        self.processed_count = 0
        # Register signal handlers
        signal.signal(signal.SIGINT, self._handle_exit)
        signal.signal(signal.SIGTERM, self._handle_exit)

    def _handle_exit(self, signum, frame):
        logger.info("Shutdown signal received. Stopping crawler gracefully...")
        self.running = False

    def initialize_app_list(self):
        """Ensure we have an AppID list to work with."""
        logger.info("Checking AppID list snapshot...")
        latest_snapshot = app_list_fetcher.get_latest_snapshot()
        
        if not latest_snapshot:
            logger.info("No local snapshot found. Attempting to fetch from Steam...")
            try:
                apps = app_list_fetcher.fetch_all()
                if apps:
                    latest_snapshot = app_list_fetcher.save_snapshot(apps)
                else:
                    logger.error("Fetched app list was empty. Cannot proceed.")
                    sys.exit(1)
            except Exception as e:
                logger.critical(f"Failed to fetch initial AppID list: {e}")
                sys.exit(1)
        
        # Load snapshot into scheduler (idempotent)
        if latest_snapshot:
            scheduler.load_from_snapshot(latest_snapshot)

    def process_task(self, task: Task):
        """Process a single task: Fetch -> Parse -> Save."""
        try:
            logger.info(f"Processing Task: {task.app_id} ({task.name})")
            
            # Fetch details
            details = detail_fetcher.fetch_details(task.app_id)
            
            if details:
                # It's a valid game
                game_storage.save_game(details)
                
                # Fetch reviews if it is a game
                reviews = review_fetcher.fetch_reviews(task.app_id)
                if reviews:
                    game_storage.save_reviews(task.app_id, reviews)
                    logger.debug(f"Saved reviews for {task.app_id}")
                
                # Fetch detailed tags (optional, might be slow)
                tags = tag_fetcher.fetch_tags(task.app_id)
                if tags:
                    details['tags'] = tags
                    # Resave game with tags
                    game_storage.save_game(details)
                    logger.debug(f"Saved tags for {task.app_id}: {len(tags)}")

                task.mark_success()
                logger.info(f"Task SUCCESS: {task.app_id}")
            else:
                # It's skipped (not a game, or data hidden)
                # Note: detail_fetcher returns None for both "error" and "skipped".
                # Ideally detail_fetcher should distinguish, but for now we treat None as 'Skipped/NoData'
                # unless it raised an exception.
                task.mark_skipped("Not a game or no data returned")
                logger.info(f"Task SKIPPED: {task.app_id}")

        except Exception as e:
            logger.error(f"Task FAILED: {task.app_id} - {e}")
            task.mark_failed(str(e))
        finally:
            # Always update task status in DB
            scheduler.update_task(task)

    def run(self):
        """Main Loop."""
        logger.info("Starting Steam Crawler Service...")
        
        self.initialize_app_list()
        
        logger.info("Entering main crawl loop...")
        
        while self.running:
            try:
                # 1. Get Batch
                batch = scheduler.get_next_batch(self.batch_size)
                
                if not batch:
                    logger.info("No pending tasks found. Queue empty.")
                    stats = scheduler.get_stats()
                    logger.info(f"Current Stats: {stats}")
                    
                    # Wait a bit before checking again (or exit if one-pass mode)
                    # For long-running, we might want to check for new AppID updates here eventually
                    logger.info("Sleeping for 60 seconds...")
                    for _ in range(60):
                        if not self.running: break
                        time.sleep(1)
                    continue

                # 2. Process Batch
                for task in batch:
                    if not self.running:
                        break
                    
                    # Check if we've hit the task limit (for testing)
                    if self.max_tasks and self.processed_count >= self.max_tasks:
                        logger.info(f"Reached max_tasks limit ({self.max_tasks}). Stopping.")
                        self.running = False
                        break
                    
                    self.process_task(task)
                    self.processed_count += 1
                
                # Log progress
                stats = scheduler.get_stats()
                logger.info(f"Batch completed. Stats: {stats}")

            except Exception as e:
                logger.error(f"Unexpected error in main loop: {e}")
                time.sleep(5) # Prevent tight error loop

        logger.info("Crawler Service stopped.")

def main():
    parser = argparse.ArgumentParser(description="Steam Store Crawler")
    parser.add_argument("--max-tasks", type=int, default=None, 
                        help="Maximum number of tasks to process (for testing)")
    args = parser.parse_args()
    
    service = CrawlerService(max_tasks=args.max_tasks)
    service.run()

if __name__ == "__main__":
    main()
