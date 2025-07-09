import logging
from handlers.income_handler import handle_private_income_statement

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


def process_selection(company_type, statement_type):
    """Dispatch processing based on company and statement type."""
    try:
        if company_type == "private":
            if statement_type == "income":
                handle_private_income_statement()
            elif statement_type == "balance":
                logger.info("Private Balance Sheet analysis not yet implemented.")
            elif statement_type == "cash_flow":
                logger.info("Private Cash Flow analysis not yet implemented.")
        elif company_type == "public":
            if statement_type == "income":
                logger.info("Public Income Statement analysis not yet implemented.")
            elif statement_type == "balance":
                logger.info("Public Balance Sheet analysis not yet implemented.")
            elif statement_type == "cash_flow":
                logger.info("Public Cash Flow analysis not yet implemented.")
        else:
            logger.error("Invalid company type selected.")

    except Exception as e:
        logger.error(f"An error occurred during processing: {str(e)}")
        raise


def main():
    """Main entry point for PyFinAnalyzer."""
    # CLI entry point now calls process_selection via analyze command
    pass


if __name__ == "__main__":
    main()
