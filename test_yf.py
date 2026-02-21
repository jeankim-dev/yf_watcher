import yfinance as yf
import pandas as pd

tickers = ["AAPL", "SPY", "XLK"]
data = yf.download(tickers, period="1mo", auto_adjust=True)
print("Columns structure:")
print(data.columns)
print("\nFirst few rows:")
print(data.head())
