import settings
from sec_processing.utils import *
from typing import List, Dict


def workflow(tickers_: List[str]) -> list[Dict]:
    data = []
    report_type_w = "income_statement"
    for ticker_ in tickers_:
        current_ticker = ticker_  # tickers_list[ticker_]
        try:
            df_w = fetch_report_to_df(current_ticker, report_type_w)
            tc_w = extract_tax_rate(df_w)
            data.append({"ticker": current_ticker, "tc": tc_w})
            settings.logger.info(f"Processed {current_ticker}")
        except Exception as e:
            settings.logger.error(f"Error processing {current_ticker}: {e}")

    return data


def main(tickers_: List[str]):
    tickers_tc = workflow(tickers_)
    summarized_tc_df, stats_per_symbol = convert_and_group(tickers_tc)
    print(stats_per_symbol.sort_values(by=['value'], ascending=False))


if __name__ == "__main__":
    tickers = ["MSFT", "JNJ", "HD", "GOOGL", "TSLA", "HD", "JNJ"]
    main(tickers)
