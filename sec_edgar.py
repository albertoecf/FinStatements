import os
import pandas as pd
from sec_edgar_downloader import Downloader
from bs4 import BeautifulSoup
import numpy as np
import settings
import requests

def get_financial_statement(ticker, statement_type="income_statement"):
    """
    Parse latest 10-K filing for the ticker from SEC EDGAR,
    return requested financial statement as a pandas DataFrame.

    statement_type: 'income_statement', 'balance_sheet', or 'free_cash_flow'
    """
    filing_path = "sec-edgar-filings/AAPL/10-K/0000320193-24-000123/full-submission.txt"

    # Step 3: Parse filing HTML/text
    with open(filing_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f.read(), "lxml")

    # Step 4: Find all tables
    tables = soup.find_all("table")

    # Keywords for identifying statement type (taken from repo and extended)
    keywords_map = {
        "income_statement": [
            "consolidated statements of operations",
            "consolidated statement of operations",
            "consolidated statements of income",
            "consolidated statement of income",
            "statement of operations",
            "income statement"
        ],
        "balance_sheet": [
            "consolidated balance sheets",
            "balance sheet"
        ],
        "free_cash_flow": [
            "consolidated statements of cash flows",
            "statement of cash flows",
            "cash flow statement"
        ]
    }

    def clean_text(text):
        return text.lower().strip()

    def table_contains_keyword(table, keywords):
        # Search the table caption or first rows for keywords
        caption = table.find("caption")
        if caption and any(k in clean_text(caption.text) for k in keywords):
            return True
        # Check first 3 rows for keywords
        for i, row in enumerate(table.find_all("tr")):
            if i > 3:
                break
            row_text = clean_text(row.text)
            if any(k in row_text for k in keywords):
                return True
        return False

    # Step 5: Parse table content into list of lists (unnesting)
    def parse_table_to_rows(table):
        rows = []
        for row in table.find_all("tr"):
            cols = row.find_all(["td", "th"])
            # Get text, preserving empty strings for missing cells
            col_texts = [ele.get_text(separator=" ", strip=True) for ele in cols]
            rows.append(col_texts)
        # Remove empty rows (all empty strings)
        rows = [r for r in rows if any(cell.strip() for cell in r)]
        return rows

    # Step 6: Search for the table matching statement_type keywords
    target_table = None
    for table in tables:
        if table_contains_keyword(table, keywords_map[statement_type]):
            target_table = table
            break

    if target_table is None:
        print(f"Could not find a table for statement type '{statement_type}' in the latest filing.")
        return None

    # Step 7: Parse table rows and convert to DataFrame
    rows = parse_table_to_rows(target_table)

    # Normalize table width by padding rows with fewer columns
    max_cols = max(len(r) for r in rows)
    normalized_rows = [r + [""] * (max_cols - len(r)) for r in rows]

    df = pd.DataFrame(normalized_rows)

    # Step 8: Basic cleaning - set first row as header if suitable
    # Heuristic: if first row contains year or dates, set as header
    header_row = df.iloc[0].tolist()
    if any(any(char.isdigit() for char in cell) for cell in header_row):
        df.columns = header_row
        df = df[1:].reset_index(drop=True)

    return df


def format_financial_df(df):
    """
    Clean and format financial statement DataFrame to look like a finance report:
    - Set first column as index (line item)
    - Convert numeric columns (remove commas, parentheses for negatives)
    - Format numbers with commas
    """
    df = df.copy()
    # Set first column as index (assumes first col contains line item names)
    df.set_index(df.columns[0], inplace=True)

    def to_number(x):
        if isinstance(x, str):
            x = x.replace(",", "").replace("(", "-").replace(")", "").replace("$", "").strip()
            try:
                return float(x)
            except:
                return x
        return x

    for col in df.columns:
        df[col] = df[col].apply(to_number)
        # Format floats with commas, no decimals if integer
        df[col] = df[col].apply(lambda x: f"{int(x):,}" if isinstance(x, float) and x.is_integer() else x)

    # Replace NaN with empty string for clean display
    df.fillna("", inplace=True)
    return df


import numpy as np

def extract_columns_values_and_dates_from_statement(soup):
    """
    Extracts columns, values, and dates from an HTML soup object representing a financial statement.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the HTML document.

    Returns:
        tuple: Tuple containing columns, values_set, and date_time_index.
    """
    columns = []
    values_set = []
    date_time_index = get_datetime_index_dates_from_statement(soup)

    for table in soup.find_all("table"):
        unit_multiplier = 1
        special_case = False

        # Check table headers for unit multipliers and special cases
        table_header = table.find("th")
        if table_header:
            header_text = table_header.get_text()
            # Determine unit multiplier based on header text
            if "in Thousands" in header_text:
                unit_multiplier = 1
            elif "in Millions" in header_text:
                unit_multiplier = 1000
            # Check for special case scenario
            if "unless otherwise specified" in header_text:
                special_case = True

        # Process each row of the table
        for row in table.select("tr"):
            onclick_elements = row.select("td.pl a, td.pl.custom a")
            if not onclick_elements:
                continue

            # Extract column title from 'onclick' attribute
            onclick_attr = onclick_elements[0]["onclick"]
            column_title = onclick_attr.split("defref_")[-1].split("',")[0]
            columns.append(column_title)

            # Initialize values array with NaNs
            values = [np.nan] * len(date_time_index)

            # Process each cell in the row
            for i, cell in enumerate(row.select("td.text, td.nump, td.num")):
                if "text" in cell.get("class"):
                    continue

                # Clean and parse cell value
                value = keep_numbers_and_decimals_only_in_string(
                    cell.text.replace("$", "")
                    .replace(",", "")
                    .replace("(", "")
                    .replace(")", "")
                    .strip()
                )
                if value:
                    value = float(value)
                    # Adjust value based on special case and cell class
                    if special_case:
                        value /= 1000
                    else:
                        if "nump" in cell.get("class"):
                            values[i] = value * unit_multiplier
                        else:
                            values[i] = -value * unit_multiplier

            values_set.append(values)

    return columns, values_set, date_time_index


def get_datetime_index_dates_from_statement(soup: BeautifulSoup) -> pd.DatetimeIndex:
    """
    Extracts datetime index dates from the HTML soup object of a financial statement.

    Args:
        soup (BeautifulSoup): The BeautifulSoup object of the HTML document.

    Returns:
        pd.DatetimeIndex: A Pandas DatetimeIndex object containing the extracted dates.
    """
    table_headers = soup.find_all("th", {"class": "th"})
    dates = [str(th.div.string) for th in table_headers if th.div and th.div.string]
    dates = [standardize_date(date).replace(".", "") for date in dates]
    index_dates = pd.to_datetime(dates)
    return index_dates


def standardize_date(date: str) -> str:
    """
    Standardizes date strings by replacing abbreviations with full month names.

    Args:
        date (str): The date string to be standardized.

    Returns:
        str: The standardized date string.
    """
    for abbr, full in zip(calendar.month_abbr[1:], calendar.month_name[1:]):
        date = date.replace(abbr, full)
    return date


def keep_numbers_and_decimals_only_in_string(mixed_string: str):
    """
    Filters a string to keep only numbers and decimal points.

    Args:
        mixed_string (str): The string containing mixed characters.

    Returns:
        str: String containing only numbers and decimal points.
    """
    num = "1234567890."
    allowed = list(filter(lambda x: x in num, mixed_string))
    return "".join(allowed)

import numpy as np
def _get_file_name(report):
    html_file_name_tag = report.find("HtmlFileName")
    xml_file_name_tag = report.find("XmlFileName")

    if html_file_name_tag:
        return html_file_name_tag.text
    elif xml_file_name_tag:
        return xml_file_name_tag.text
    else:
        return ""


def _is_statement_file(short_name_tag, long_name_tag, file_name):
    return (
        short_name_tag is not None
        and long_name_tag is not None
        and file_name  # Check if file_name is not an empty string
        and "Statement" in long_name_tag.text
    )


def get_statement_file_names_in_filing_summary(
    ticker, accession_number, headers=headers
):
    try:
        session = requests.Session()
        cik = cik_matching_ticker(ticker)
        base_link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}"
        filing_summary_link = f"{base_link}/FilingSummary.xml"
        filing_summary_response = session.get(
            filing_summary_link, headers=headers
        ).content.decode("utf-8")

        filing_summary_soup = BeautifulSoup(filing_summary_response, "lxml-xml")
        statement_file_names_dict = {}

        for report in filing_summary_soup.find_all("Report"):
            file_name = _get_file_name(report)
            short_name, long_name = report.find("ShortName"), report.find("LongName")

            if _is_statement_file(short_name, long_name, file_name):
                statement_file_names_dict[short_name.text.lower()] = file_name

        return statement_file_names_dict

    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return {}


def get_statement_soup(
    ticker,
    accession_number,
    statement_name,
    headers,
    statement_keys_map,
):
    """
    the statement_name should be one of the following:
    'balance_sheet'
    'income_statement'
    'cash_flow_statement'
    """
    session = requests.Session()

    cik = cik_matching_ticker(ticker)
    base_link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession_number}"

    statement_file_name_dict = get_statement_file_names_in_filing_summary(
        ticker, accession_number, headers
    )

    statement_link = None
    for possible_key in statement_keys_map.get(statement_name.lower(), []):
        file_name = statement_file_name_dict.get(possible_key.lower())
        if file_name:
            statement_link = f"{base_link}/{file_name}"
            break

    if not statement_link:
        raise ValueError(f"Could not find statement file name for {statement_name}")

    try:
        statement_response = session.get(statement_link, headers=headers)
        statement_response.raise_for_status()  # Check if the request was successful

        if statement_link.endswith(".xml"):
            return BeautifulSoup(
                statement_response.content, "lxml-xml", from_encoding="utf-8"
            )
        else:
            return BeautifulSoup(statement_response.content, "lxml")

    except requests.RequestException as e:
        raise ValueError(f"Error fetching the statement: {e}")

def create_dataframe_of_statement_values_columns_dates(
    values_set, columns, index_dates
) -> pd.DataFrame:
    """
    Creates a DataFrame from statement values, columns, and index dates.

    Args:
        values_set (list): List of values for each column.
        columns (list): List of column names.
        index_dates (pd.DatetimeIndex): DatetimeIndex for the DataFrame index.

    Returns:
        pd.DataFrame: DataFrame constructed from the given data.
    """
    transposed_values_set = list(zip(*values_set))
    df = pd.DataFrame(transposed_values_set, columns=columns, index=index_dates)
    return df


def process_one_statement(ticker, accession_number, statement_name):
    """
    Processes a single financial statement identified by ticker, accession number, and statement name.

    Args:
        ticker (str): The stock ticker.
        accession_number (str): The SEC accession number.
        statement_name (str): Name of the financial statement.

    Returns:
        pd.DataFrame or None: DataFrame of the processed statement or None if an error occurs.
    """
    try:
        # Fetch the statement HTML soup
        soup = get_statement_soup(
            ticker,
            accession_number,
            statement_name,
            headers=headers,
            statement_keys_map=statement_keys_map,
        )
    except Exception as e:
        settings.logger.error(
            f"Failed to get statement soup: {e} for accession number: {accession_number}"
        )
        return None

    if soup:
        try:
            # Extract data and create DataFrame
            columns, values, dates = extract_columns_values_and_dates_from_statement(
                soup
            )
            df = create_dataframe_of_statement_values_columns_dates(
                values, columns, dates
            )

            if not df.empty:
                # Remove duplicate columns
                df = df.T.drop_duplicates()
            else:
                settings.logger.warning(
                    f"Empty DataFrame for accession number: {accession_number}"
                )
                return None

            return df
        except Exception as e:
            settings.logger.error(f"Error processing statement: {e}")
            return None



if __name__ == "__main__":
    ticker = "TSLA"

    print("\nIncome Statement:\n")
    income_df = get_financial_statement(ticker, "income_statement")
    if income_df is not None:
        income_df = format_financial_df(income_df)
        print(income_df.head(20))

    print("\nBalance Sheet:\n")
    balance_df = get_financial_statement(ticker, "balance_sheet")
    if balance_df is not None:
        balance_df = format_financial_df(balance_df)
        print(balance_df.head(20))

    print("\nCash Flow Statement:\n")
    cashflow_df = get_financial_statement(ticker, "free_cash_flow")
    if cashflow_df is not None:
        cashflow_df = format_financial_df(cashflow_df)
        print(cashflow_df.head(20))
