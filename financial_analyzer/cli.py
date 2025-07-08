import click
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)


@click.group()
def cli():
    """PyFinAnalyzer CLI for analyzing financial statements."""
    pass


@cli.command()
def analyze():
    """Prompt for company type and statement type with validation."""
    valid_company_types = ["public", "private"]
    valid_statement_types = ["balance", "income", "cash_flow"]

    # Prompt for company type
    while True:
        try:
            company_type = click.prompt("Enter company type (public/private)", type=str).lower()
            if company_type in valid_company_types:
                break
            logger.error("Invalid company type. Please enter 'public' or 'private'.")
        except click.Abort:
            logger.error("User aborted the input process.")
            raise

    # Prompt for statement type
    while True:
        try:
            statement_type = click.prompt("Enter statement type (balance/income/cash_flow)", type=str).lower()
            if statement_type in valid_statement_types:
                break
            logger.error("Invalid statement type. Please enter 'balance', 'income', or 'cash_flow'.")
        except click.Abort:
            logger.error("User aborted the input process.")
            raise

    logger.info(f"Company type selected: {company_type}, Statement type selected: {statement_type}")
    return company_type, statement_type


if __name__ == '__main__':
    cli()
