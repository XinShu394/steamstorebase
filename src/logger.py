import sys
from loguru import logger
from src.config import settings

def setup_logging():
    """Configure logging for the application"""
    # Remove default handler
    logger.remove()

    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO"
    )

    # Add file handler (Rotating)
    # Log file per day, keep 10 days
    log_file_path = settings.LOG_DIR / "app_{time:YYYY-MM-DD}.log"
    logger.add(
        log_file_path,
        rotation="00:00",
        retention="10 days",
        level="DEBUG",
        encoding="utf-8",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    )

    # Add error specific log file
    error_log_path = settings.LOG_DIR / "error_{time:YYYY-MM-DD}.log"
    logger.add(
        error_log_path,
        rotation="00:00",
        retention="30 days",
        level="ERROR",
        encoding="utf-8",
        backtrace=True,
        diagnose=True
    )

    logger.info("Logging system initialized")

# Initialize logging on module import
setup_logging()
