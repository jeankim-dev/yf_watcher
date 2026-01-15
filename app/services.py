import asyncio
import yfinance as yf
from app.indicators import calculate_rsi, calculate_macd
from app.db import save_result



SYMBOLS = ["AAPL", "MSFT", "NVDA", "TSLA"]


async def fetch_price(symbol: str):
    """
    yfinance는 async 라이브러리가 아니라서
    thread로 감싸서 실행
    """
    return await asyncio.to_thread(_fetch_sync, symbol)


def _fetch_sync(symbol: str):
    ticker = yf.Ticker(symbol)
    return ticker.history(period="3mo")


async def run_screening():
    tasks = [fetch_price(symbol) for symbol in SYMBOLS]
    price_data = await asyncio.gather(*tasks)

    results = []

    for symbol, df in zip(SYMBOLS, price_data):
        if df.empty:
            continue

        rsi = calculate_rsi(df["Close"])
        macd = calculate_macd(df["Close"])

        # 예시 조건
        if rsi < 30:
            result = {
                "symbol": symbol,
                "rsi": round(rsi, 2),
                "macd": round(macd, 2),
            }

            await save_result(result)
            results.append(result)

    return results
