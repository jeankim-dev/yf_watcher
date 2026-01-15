import pandas as pd


def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    delta = series.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return float(rsi.iloc[-1])


def calculate_macd(series: pd.Series) -> float:
    ema12 = series.ewm(span=12).mean()
    ema26 = series.ewm(span=26).mean()
    macd = ema12 - ema26

    return float(macd.iloc[-1])


def calc_return(df: pd.DataFrame):
    start = df["Close"].iloc[0]
    end = df["Close"].iloc[-1]
    return (end / start) - 1


import pandas as pd


def calculate_rs(
    stock_close: pd.Series,
    benchmark_close: pd.Series,
    window: int = 63,  # 기본 3개월 (거래일 기준)
) -> float:
    """
    Relative Strength (RS)
    RS = stock_return - benchmark_return
    """

    aligned = pd.concat(
        [stock_close, benchmark_close],
        axis=1,
        join="inner"
    )

    aligned.columns = ["stock", "benchmark"]

    if len(aligned) < window:
        return 0.0

    recent = aligned.iloc[-window:]

    stock_return = recent["stock"].iloc[-1] / recent["stock"].iloc[0] - 1
    benchmark_return = recent["benchmark"].iloc[-1] / recent["benchmark"].iloc[0] - 1

    return float(stock_return - benchmark_return)
