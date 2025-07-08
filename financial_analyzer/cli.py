import click
from financial_analyzer.logging_config import setup_logging
from financial_analyzer.main import process_selection

logger = setup_logging()


@click.group()
def cli():
    """PyFinAnalyzer CLI for analyzing financial statements."""
    pass


@cli.command()
@click.pass_context
def analyze(ctx):
    """
    Prompt for company type and statement type with validation.
    Calls handler based on selection.
    """
    valid_company_types = ["public", "private"]
    valid_statement_types = ["balance", "income", "cash_flow"]

    company_type = click.prompt("Enter company type (public/private)", type=click.Choice(valid_company_types))
    statement_type = click.prompt("Enter statement type (balance/income/cash_flow)",
                                  type=click.Choice(valid_statement_types))

    logger.info(f"Company type selected: {company_type}, Statement type selected: {statement_type}")

    # Call main process function with inputs
    process_selection(company_type, statement_type)


if __name__ == '__main__':
    cli()
