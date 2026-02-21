import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np

SECTOR_ETF_MAP = {
    "Technology": "XLK", "Healthcare": "XLV", "Financial Services": "XLF",
    "Consumer Cyclical": "XLY", "Communication Services": "XLC", "Industrials": "XLI",
    "Consumer Defensive": "XLP", "Energy": "XLE", "Utilities": "XLU",
    "Real Estate": "XLRE", "Basic Materials": "XLB"
}

def get_rs_data(ticker_symbol: str):
    try:
        ticker_obj = yf.Ticker(ticker_symbol)
        info = ticker_obj.info
        if not info or 'symbol' not in info:
             return None, f"Ticker '{ticker_symbol}'을 찾을 수 없습니다."

        sector = info.get("sector", "Technology")
        sector_etf = SECTOR_ETF_MAP.get(sector, "SPY")
        
        tickers = list(set([ticker_symbol, "SPY", sector_etf]))
        raw_df = yf.download(tickers, period="2y", auto_adjust=True, progress=False)
        
        if raw_df.empty: return None, "데이터를 불러올 수 없습니다."

        # MultiIndex 컬럼 처리
        if isinstance(raw_df.columns, pd.MultiIndex):
            if 'Price' in raw_df.columns.names:
                df = raw_df.xs('Close', axis=1, level='Price')
            elif 'Close' in raw_df.columns.levels[0]:
                df = raw_df['Close']
            else:
                df = raw_df.xs(raw_df.columns.levels[0][0], axis=1, level=0)
        else:
            df = raw_df

        def calculate_rs_ma(num, den):
            if num not in df.columns or den not in df.columns: return None, None
            ratio = (df[num] / df[den]).replace([np.inf, -np.inf], np.nan).ffill().dropna()
            if ratio.empty: return None, None
            ma = ratio.rolling(window=21).mean()
            return ratio.tail(252), ma.tail(252)

        def create_chart_json(num, den, title_text):
            rs, ma = calculate_rs_ma(num, den)
            if rs is None: return None
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=rs.index.strftime('%Y-%m-%d').tolist(), y=rs.values.tolist(), 
                                     mode='lines', name="RS Line", line=dict(width=2, color='#0071e3')))
            fig.add_trace(go.Scatter(x=ma.index.strftime('%Y-%m-%d').tolist(), y=ma.values.tolist(), 
                                     mode='lines', name="21 MA", line=dict(width=1.5, color='#ff9500', dash='dot')))
            fig.update_layout(
                title=dict(text=title_text, x=0.5),
                template="plotly_white", 
                height=400, # 높이 명시
                margin=dict(t=60, b=40, l=50, r=20), 
                hovermode="x unified",
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                yaxis=dict(title="Ratio", autorange=True), 
                xaxis=dict(type='date')
            )
            return fig.to_json()

        chart1 = create_chart_json(ticker_symbol, "SPY", f"1. {ticker_symbol} vs 시장 (SPY)")
        chart2 = create_chart_json(sector_etf, "SPY", f"2. 섹터 ({sector_etf}) vs 시장 (SPY)")
        chart3 = create_chart_json(ticker_symbol, sector_etf, f"3. {ticker_symbol} vs 섹터 ({sector_etf})")

        if not chart1: return None, "데이터 부족으로 차트를 생성할 수 없습니다."

        return {
            "ticker": ticker_symbol, "sector_name": sector, "sector_etf": sector_etf,
            "chart1_json": chart1, "chart2_json": chart2, "chart3_json": chart3
        }, None
        
    except Exception as e:
        return None, f"오류 발생: {str(e)}"
