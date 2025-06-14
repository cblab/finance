import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np

def get_stock_data(tickers, start_date, end_date, timeframe):
    data = {}
    for ticker in tickers:
        try:
            ticker_data = yf.download(ticker, start=start_date, end=end_date, interval=timeframe)
            print(f"Available columns for {ticker}: {ticker_data.columns}")
            data[ticker] = ticker_data  # Alle Spalten für die Verarbeitung beibehalten
        except Exception as e:
            print(f"Error for {ticker}: {e}")
    return pd.concat(data, axis=1) if data else pd.DataFrame()

# Benutzereingaben
start_date_input = input("Enter start date (DD.MM.YYYY): ")
end_date_input = input("Enter end date (DD.MM.YYYY): ")
timeframe_input = input("Enter timeframe (daily, weekly, monthly): ").lower()
tickers = input("Enter ticker symbols (space-separated): ").split()
price_types = input("Enter price types (Open High Low Close Adj Close): ").split()

# Daten in erforderliches Format konvertieren
start_date = datetime.strptime(start_date_input, "%d.%m.%Y").strftime("%Y-%m-%d")
end_date = datetime.strptime(end_date_input, "%d.%m.%Y").strftime("%Y-%m-%d")

# Timeframe-Zuordnung
timeframe_map = {"daily": "1d", "weekly": "1wk", "monthly": "1mo"}
interval = timeframe_map.get(timeframe_input, "1d")

# Preisarten formatieren
price_types = [p.capitalize() for p in price_types]
if "Adj" in price_types:
    price_types[price_types.index("Adj")] = "Adj Close"


# Daten abrufen
df = get_stock_data(tickers, start_date, end_date, interval)

# Falls mehrere Ticker abgefragt wurden, besitzt der DataFrame eine
# MultiIndex-Spalte ohne Namen.  Wir benennen die Ebenen, damit die
# spaetere Auswahl nach Preistyp funktioniert.
if isinstance(df.columns, pd.MultiIndex):
    df.columns.names = ["Ticker", "Price"]

if not df.empty:
    # Zeitzoneninformationen entfernen
    df.index = df.index.tz_localize(None)

    # Gewünschte Preistypen für die Excel-Datei auswählen
    if df.columns.nlevels == 1:
        df_selected = df.loc[:, df.columns.isin(price_types)]
    else:
        df_selected = df.loc[:, df.columns.get_level_values("Price").isin(price_types)]

    # Ausgabeordner erstellen
    output_folder = r"E:\\code"
    os.makedirs(output_folder, exist_ok=True)

    # In Excel speichern
    output_file = os.path.join(output_folder, "Historical_ITPM_Prices.xlsx")
    df_selected.to_excel(output_file)
    print(f"Data saved to {output_file}")

    # Volatilität berechnen und visualisieren
    for ticker in tickers:
        # Preisdaten extrahieren
        try:
            if 'Adj Close' in df[ticker].columns:
                price_data = df[ticker]['Adj Close']
            elif 'Close' in df[ticker].columns:
                price_data = df[ticker]['Close']
            else:
                print(f"Price data not found for {ticker}")
                continue
        except KeyError:
            print(f"Price data not found for {ticker}")
            continue

        # Renditen berechnen
        returns = price_data.pct_change()

        # Fenstergröße basierend auf dem Intervall definieren
        if interval == '1d':
            window = 20  # 20 Tage
        elif interval == '1wk':
            window = 4   # 4 Wochen
        elif interval == '1mo':
            window = 12  # 12 Monate
        else:
            window = 20  # Standardwert

        # Rollierende Volatilität berechnen
        volatility = returns.rolling(window=window).std() * np.sqrt(window)

        # Kurs und Volatilität plotten
        fig, ax1 = plt.subplots(figsize=(12,6))

        color = 'tab:blue'
        ax1.set_xlabel('Date')
        ax1.set_ylabel('Price', color=color)
        ax1.plot(price_data.index, price_data, color=color)
        ax1.tick_params(axis='y', labelcolor=color)

        ax2 = ax1.twinx()
        color = 'tab:red'
        ax2.set_ylabel('Volatility', color=color)
        ax2.plot(volatility.index, volatility, color=color)
        ax2.tick_params(axis='y', labelcolor=color)

        plt.title(f'{ticker} Price and Volatility')

        # Plot speichern
        plot_file = os.path.join(output_folder, f"{ticker}_price_volatility.png")
        plt.savefig(plot_file)
        plt.close()
        print(f"Plot saved to {plot_file}")

else:
    print("No data was retrieved. Please check your inputs and try again.")
