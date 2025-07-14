import settings
from sec_processing.utils import *
import settings
import re

debt_mapping = {
    "Long-term Debt": "long_term_debt",
    "Long-term Debt and Lease Obligation": "long_term_debt",
    "Long-term Debt and Lease Obligation, Current": "current_portion_long_term_debt",
    "Short-term Debt": "short_term_debt",
}

debt_patterns = [
    r".*long[- ]?term.*debt.*",
    r".*short[- ]?term.*debt.*",
    r".*debt.*obligation.*",
    r".*lease.*obligation.*",
]

def detect_debt_columns(columns, debt_mapping, debt_patterns):
    detected = {}

    for col in columns:
        if col is None:
            continue
        col_lower = col.lower()
        for mapped_key, mapped_value in debt_mapping.items():
            if mapped_key.lower() == col_lower:
                detected[mapped_value] = col

    for col in columns:
        if col is None:
            continue
        col_lower = col.lower()
        for pattern in debt_patterns:
            if re.search(pattern, col_lower, re.IGNORECASE):
                key = "debt_regex_match"
                if key not in detected:
                    detected[key] = []
                detected[key].append(col)

    return detected

def main(tickers_):

    metric_ = "avg_total_debt"
    report_type = "balance_sheet"

    for ticker in tickers_:
        report_df = fetch_report_to_df(ticker, report_type)
        cols = list(report_df.transpose().columns)

        try:
            detected_debt_cols = detect_debt_columns(cols, debt_mapping, debt_patterns)

            # Aggregate all found debt columns
            debt_cols = []

            # Add mapped debt columns
            for key in ["long_term_debt", "current_portion_long_term_debt", "short_term_debt"]:
                if key in detected_debt_cols:
                    debt_cols.append(detected_debt_cols[key])

            # Add regex matched columns (if any)
            if "debt_regex_match" in detected_debt_cols:
                debt_cols.extend(detected_debt_cols["debt_regex_match"])

            # Flatten in case some are lists
            flat_debt_cols = []
            for col in debt_cols:
                if isinstance(col, list):
                    flat_debt_cols.extend(col)
                else:
                    flat_debt_cols.append(col)

            if not flat_debt_cols:
                raise ValueError("No debt columns found")

            metric_df = report_df.transpose().loc[:, flat_debt_cols]

            # Sum debt columns row-wise
            metric_df["TotalDebt"] = metric_df.sum(axis=1)
            metric_value = metric_df["TotalDebt"].mean()

            print(f'Ticker: {ticker} , {metric_} : {metric_value}')

        except Exception as e:
            settings.logger.error(f"Could not find {metric_} in: {report_type} for {ticker} : {e}")

if __name__ == "__main__":
    tickers = ["MSFT", "JNJ", "HD", "GOOGL", "TSLA", "HD", "JNJ"]
    main(tickers)