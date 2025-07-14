from wacc import calculate_wacc
from fetch_fcf import fetch_fcf
from company_growth import forecast_fcf_using_growth
from discount_fcf import discount_fcfs, calculate_npv_from_discounted

ticker = "GOOG"
wacc = calculate_wacc(ticker)
fcf_df = fetch_fcf(ticker)
df_forecasted = forecast_fcf_using_growth(fcf_df)

print(df_forecasted.info())

df_discounted = discount_fcfs(df_forecasted, wacc)
npv = calculate_npv_from_discounted(df_discounted)
print(f"NPV_cash_flow: {npv:,.2f}")
