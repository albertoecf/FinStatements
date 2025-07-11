# FinStatements

Repository to analyse different companies and return financial statements

# Setup

Create new env
python -m venv financial_env

Activate the new env
Linux/Mac:

source financial_env/bin/activate

windows:
financial_env\Scripts\activate

## Features

Fetching any report for any public company
report_workflow.py accepts ticker and report type as inputs. Returns the last report presented.

Potential improvements:

* Returns multiple report_dates
* Return multiple report_type in the same call

* tc_comparison.py receives a list of tickers and returns a pd df with tc stats. (It fetches data from k-10 in the sec
  edgar, process it, and returns a df)