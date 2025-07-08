import logging
import sys


def setup_logging():
    """Configure logging for PyFinAnalyzer."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler(sys.stdout)],
        force=True
    )
    logger = logging.getLogger(__name__)
    # Ensure logs are flushed immediately
    logger.handlers[0].flush = sys.stdout.flush
    return logger
