import pandas as pd
import requests
import sys, os
import calendar
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings

headers = {"User-Agent": settings.email_address}

statement_keys_map = {
    "balance_sheet": [
        "balance sheet",
        "balance sheets",
        "statement of financial position",
        "consolidated balance sheets",
        "consolidated balance sheet",
        "consolidated financial position",
        "consolidated balance sheets - southern",
        "consolidated statements of financial position",
        "consolidated statement of financial position",
        "consolidated statements of financial condition",
        "combined and consolidated balance sheet",
        "condensed consolidated balance sheets",
        "consolidated balance sheets, as of december 31",
        "dow consolidated balance sheets",
        "consolidated balance sheets (unaudited)",
    ],
    "income_statement": [
        "income statement",
        "income statements",
        "statement of earnings (loss)",
        "statements of consolidated income",
        "consolidated statements of operations",
        "consolidated statement of operations",
        "consolidated statements of earnings",
        "consolidated statement of earnings",
        "consolidated statements of income",
        "consolidated statement of income",
        "consolidated income statements",
        "consolidated income statement",
        "condensed consolidated statements of earnings",
        "consolidated results of operations",
        "consolidated statements of income (loss)",
        "consolidated statements of income - southern",
        "consolidated statements of operations and comprehensive income",
        "consolidated statements of comprehensive income",
    ],
    "cash_flow_statement": [
        "cash flows statement",
        "cash flows statements",
        "statement of cash flows",
        "statements of consolidated cash flows",
        "consolidated statements of cash flows",
        "consolidated statement of cash flows",
        "consolidated statement of cash flow",
        "consolidated cash flows statements",
        "consolidated cash flow statements",
        "condensed consolidated statements of cash flows",
        "consolidated statements of cash flows (unaudited)",
        "consolidated statements of cash flows - southern",
    ],
}


def cik_matching_ticker(ticker, headers=headers):
    ticker = ticker.upper().replace(".", "_")
    ticker_json = requests.get("https://www.sec.gov/files/company_tickers.json", headers=headers).json()
    for company in ticker_json.values():
        if company["ticker"] == ticker:
            cik = str(company["cik_str"]).zfill(10)
            return cik
    raise ValueError(f'Ticker: {ticker} not found".format(ticker=ticker)')


def get_submission_data_for_ticker(ticker, headers=headers, only_fillings_df=False):
    cik = cik_matching_ticker(ticker, headers=headers)
    headers = headers.copy()
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    company_json = requests.get(url, headers=headers).json()
    if only_fillings_df:
        return pd.DataFrame(company_json["filings"]["recent"])
    else:
        return company_json


def get_filtered_filings(ticker, form_type='10-K', just_accession_numbers=False, headers=headers):
    company_filings_df = get_submission_data_for_ticker(ticker, only_fillings_df=True, headers=headers)
    if form_type is not None:
        df = company_filings_df[company_filings_df["form"] == form_type]
        if just_accession_numbers:
            accession_df = df.set_index('reportDate')['accessionNumber']
            return accession_df
        else:
            return df
    else:
        raise ValueError("Must provide form_type")


def get_facts(ticker, headers=headers):
    cik = cik_matching_ticker(ticker, headers=headers)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    company_facts = requests.get(url, headers=headers).json()
    return company_facts


def get_facts_df(ticker, headers=headers):
    facts = get_facts(ticker, headers=headers)
    us_gaap_data = facts["facts"]["us-gaap"]
    df_data = []
    for fact, details in us_gaap_data.items():
        for unit in details["units"]:
            for item in details["units"][unit]:
                row = item.copy()
                row["fact"] = fact
                df_data.append(row)

    df = pd.DataFrame(df_data)
    df["end"] = pd.to_datetime(df["end"])
    df["start"] = pd.to_datetime(df["start"])
    df.drop_duplicates(subset=["fact", "start", "end"], inplace=True)
    df.set_index("end", inplace=True)
    labels_dict = {fact: details["label"] for fact, details in us_gaap_data.items()}
    return df, labels_dict


def annual_facts(ticker, headers=headers):
    accession_nums = get_filtered_filings(ticker, form_type='10-K', just_accession_numbers=True)
    df, label_dict = get_facts_df(ticker, headers)
    ten_k = df[df["accn"].isin(accession_nums)]
    ten_k = ten_k[ten_k.index.isin(accession_nums.index)]
    pivot = ten_k.pivot_table(values="val", columns="fact", index="end")
    pivot.rename(columns=label_dict, inplace=True)
    return pivot.T


def quarterly_facts(ticker, headers=headers):
    accession_nums = get_filtered_filings(
        ticker, form_type="10-Q", just_accession_numbers=True
    )
    df, label_dict = get_facts_df(ticker, headers)
    ten_q = df[df["accn"].isin(accession_nums)]
    ten_q = ten_q[ten_q.index.isin(accession_nums.index)].reset_index(drop=False)
    ten_q = ten_q.drop_duplicates(subset=["fact", "end"], keep="last")
    pivot = ten_q.pivot_table(values="val", columns="fact", index="end")
    pivot.rename(columns=label_dict, inplace=True)
    return pivot.T


def save_dataframe_to_csv(dataframe, folder_name, ticker, statement_name, frequency):
    directory_path = os.path.join(folder_name, ticker)
    os.makedirs(directory_path, exist_ok=True)
    file_path = os.path.join(directory_path, f"{statement_name}_{frequency}.csv")
    dataframe.to_csv(file_path)
    return None


def get_label_dictionary(ticker, headers):
    facts = get_facts(ticker, headers)
    us_gaap_data = facts["facts"]["us-gaap"]
    labels_dict = {fact: details["label"] for fact, details in us_gaap_data.items()}
    return labels_dict


def rename_statement(statement, label_dictionary):
    # Extract the part after the first "_" and then map it using the label dictionary
    try:
        statement.index = statement.index.map(
            lambda x: label_dictionary.get(x.split("_", 1)[-1], x)
        )
    except ValueError:
        raise ValueError("It was not possible to rename the statement")

    return statement


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


from bs4 import BeautifulSoup


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
        raise ValueError("Failed to get statement soup for accession number: {}".format(accession_number))

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



def fetch_report_to_df(ticker: str, report_type: str) -> pd.DataFrame:
    """Given a ticker and valid report type, this function returns the report for the latest period"""
    ticker = ticker.upper()
    report_type = report_type.lower()

    valid_report_types = ["balance_sheet", "income_statement", "cash_flow_statement"]
    if report_type not in valid_report_types:
        raise ValueError(f"{report_type} is not a valid report type")

    try:
        acc = get_filtered_filings(ticker, form_type="10-Q", just_accession_numbers=True)
        acc_num = acc.iloc[0].replace('-', '')
    except IndexError:
        raise ValueError(f"There was a problem getting filings for {ticker}")

    try:
        statement = process_one_statement(ticker, acc_num, report_type)
    except ValueError:
        print("stop program")
        raise ValueError(f"There was a problem getting filings for {ticker}")

    label_dict = get_label_dictionary(ticker, headers)
    statement_df = rename_statement(statement, label_dict)
    #settings.logger.debug("statement_df: {}".format(statement_df))
    return statement_df


def extract_tax_rate(df_: pd.DataFrame) -> float:
    ebt_ = df_.loc['Income (Loss) from Continuing Operations before Income Taxes, Noncontrolling Interest']
    tax_expense_ = df_.loc['Income Tax Expense (Benefit)']
    tx_raw_ = (tax_expense_ / ebt_)
    tc_ = tx_raw_.apply(lambda x: max(0, x))
    return tc_

def convert_and_group(data_list):
    # Initialize empty list to collect records
    records = []

    # Loop through each dictionary in the input list
    for entry in data_list:
        ticker = entry['ticker']
        tc_series = entry['tc']

        # Convert each series to dataframe and reset index for date-value structure
        df = tc_series.reset_index()
        df.columns = ['date', 'value']
        df['ticker'] = ticker

        # Append to records
        records.append(df)

    # Concatenate all records into one dataframe
    final_df = pd.concat(records, ignore_index=True)

    # Reorder columns
    final_df = final_df[['ticker', 'date', 'value']]
    # Group by ticker and calculate average
    grouped_df = final_df.groupby('ticker')['value'].mean().reset_index()

    return final_df, grouped_df






def workflow(symbol):
    ticker = symbol.upper()
    filings = get_filtered_filings(ticker, form_type='10-K')
    print(filings)

    facts, labels = get_facts_df(ticker)

    print("facts :", facts)
    print("labels :", labels)

    accession_nums = get_filtered_filings(ticker, form_type="10-K", just_accession_numbers=True)
    print("accession_nums :", accession_nums)

    annual_data = annual_facts(ticker, headers=headers)
    print("annual data :", annual_data)

    quarterly_facts(ticker, headers=headers)
    print("quarterly data :", quarterly_facts)


if __name__ == "__main__":
    workflow("TSLA")
