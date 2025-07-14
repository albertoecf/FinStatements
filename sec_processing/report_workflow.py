import settings
from sec_processing.utils import *
from typing import List, Dict


def main(ticker_, report_type_):
    df = fetch_report_to_df(ticker_, report_type_)
    print(df)


if __name__ == "__main__":
    ticker = "MSFT"
    report_type = "cash_flow_statement"
    main(ticker, report_type)
