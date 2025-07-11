from utils import *
import calendar


def main(ticker: str, report_type: str) -> pd.DataFrame:
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

    statement = process_one_statement(ticker, acc_num, report_type)
    label_dict = get_label_dictionary(ticker, headers)
    statement_df = rename_statement(statement, label_dict)
    print(statement_df)
    return statement_df


if __name__ == "__main__":
    ticker = "GOOG"
    report_type = "cash_flow_statement"

    main(ticker, report_type)
