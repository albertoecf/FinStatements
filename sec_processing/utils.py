import pandas as pd
import requests
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import settings

headers = {"User-Agent": settings.email_address}


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
            accession_df = df.set_index('reportDate', inplace=True)['accessionNumber']
            return accession_df
        else:
            return df
    else:
        raise ValueError("Must provide form_type")


def workflow(symbol):
    ticker = symbol.upper()
    filings = get_filtered_filings(ticker, form_type='10-K')
    print(filings)


if __name__ == "__main__":
    workflow("GOOG")
