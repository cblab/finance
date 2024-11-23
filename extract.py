import yfinance as yf
import pandas as pd
import os
from datetime import datetime

def get_stock_data(tickers, start_date, end_date, timeframe, price_types):
    data = {}
    for ticker in tickers:
        try:
            ticker_data = yf.download(ticker, start=start_date, end=end_date, interval=timeframe)
            print(f"Available columns for {ticker}: {ticker_data.columns}")
            data[ticker] = ticker_data[price_types]
        except KeyError as e:
            print(f"Error for {ticker}: {e}")
    return pd.concat(data, axis=1) if data else pd.DataFrame()

# User inputs
start_date = input("Enter start date (DD.MM.YYYY): ")
end_date = input("Enter end date (DD.MM.YYYY): ")
timeframe = input("Enter timeframe (daily, weekly, monthly): ").lower()
tickers = input("Enter ticker symbols (space-separated): ").split()
price_types = input("Enter price types (Open High Low Close Adj Close): ").split()

# Convert dates to required format
start_date = datetime.strptime(start_date, "%d.%m.%Y").strftime("%Y-%m-%d")
end_date = datetime.strptime(end_date, "%d.%m.%Y").strftime("%Y-%m-%d")

# Map timeframe input to yfinance interval
timeframe_map = {"daily": "1d", "weekly": "1wk", "monthly": "1mo"}
interval = timeframe_map.get(timeframe, "1d")

# Capitalize price types for column selection
price_types = [p.capitalize() for p in price_types]
if "Adj" in price_types:
    price_types[price_types.index("Adj")] = "Adj Close"

# Fetch data
df = get_stock_data(tickers, start_date, end_date, interval, price_types)

if not df.empty:
    # Remove timezone information
    df.index = df.index.tz_localize(None)

    # Create output folder if it doesn't exist
    output_folder = r"E:\\buffet"
    os.makedirs(output_folder, exist_ok=True)

    # Save to Excel
    output_file = os.path.join(output_folder, "Historical_ITPM_Prices.xlsx")
    df.to_excel(output_file)
    print(f"Data saved to {output_file}")
else:
    print("No data was retrieved. Please check your inputs and try again.")

