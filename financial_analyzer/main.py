import logging
from financial_analyzer.cli import analyze

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for PyFinAnalyzer."""
    try:
        company_type, statement_type = analyze()
        logger.info(f"Starting analysis for {company_type} company, {statement_type} statement")
        # Placeholder for further processing (e.g., data fetching, analysis)
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    main()