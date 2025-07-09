import logfire
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
    return logger
