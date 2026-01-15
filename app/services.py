import pandas as pd
import asyncio
import yfinance as yf
from app.indicators import *
from app.db import save_result
import requests

RS_WINDOW = 63

def load_sp500_symbols() -> list[str]:
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; yf-watcher/1.0)"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    tables = pd.read_html(response.text)
    df = tables[0]

    return df["Symbol"].tolist() 


# def _fetch_sync(symbol: str):
#     ticker = yf.Ticker(symbol)
#     return ticker.history(period="1y")

def _fetch_with_ma(symbol: str) -> pd.DataFrame:
    try:
        

        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y")

        if hist.empty or len(hist) < 200:
            return pd.DataFrame()

        hist["ma5"] = hist["Close"].rolling(5).mean()
        hist["ma200"] = hist["Close"].rolling(200).mean()

        return hist

    except Exception as e:
        print(f"[ERROR] {symbol}: {e}")
        return pd.DataFrame()


async def run_screening():
    SYMBOLS = load_sp500_symbols()
    SEM = asyncio.Semaphore(5)  # 동시에 5개만
    
    async def fetch_price(symbol: str):
        """
        yfinance는 async 라이브러리가 아니라서
        thread로 감싸서 실행
        """
        async with SEM:
            return await asyncio.to_thread(_fetch_with_ma, symbol)
    
    sp500_df = _fetch_with_ma("^GSPC")
    if sp500_df.empty:
        raise RuntimeError("Failed to load S&P500 data")
    
    tasks = [fetch_price(symbol) for symbol in SYMBOLS]
    price_data = await asyncio.gather(*tasks)

    results = []

    for symbol, stock_df in zip(SYMBOLS, price_data):
        if stock_df.empty:
            continue

        rsi = calculate_rsi(stock_df["Close"])
        macd = calculate_macd(stock_df["Close"])
        stock_close = stock_df["Close"].last("3ME")
        sp500_close = sp500_df["Close"].last("3ME")

        rs = calculate_rs(stock_close, sp500_close, window=RS_WINDOW)

        # 예시 조건
        if rs > 0: # rsi < 30 and 
            result = {
                "symbol": symbol,
                "rsi": round(rsi, 2),
                "macd": round(macd, 2),
                "rs": round(rs, 2)
            }

            await save_result(result)
            results.append(result)

    return results
