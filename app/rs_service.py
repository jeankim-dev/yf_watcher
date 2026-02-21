import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import json
import numpy as np
import requests

# 미국/한국 섹터 매핑 생략 (이미 존재하므로 유지)
US_SECTOR_MAP = {
    "Technology": "XLK", "Healthcare": "XLV", "Financial Services": "XLF",
    "Consumer Cyclical": "XLY", "Communication Services": "XLC", "Industrials": "XLI",
    "Consumer Defensive": "XLP", "Energy": "XLE", "Utilities": "XLU",
    "Real Estate": "XLRE", "Basic Materials": "XLB"
}

KR_SECTOR_MAP = {
    "Technology": "091160.KS", 
    "Healthcare": "105190.KS", 
    "Financial Services": "091170.KS", 
    "Consumer Cyclical": "091180.KS", 
    "Basic Materials": "117460.KS", 
    "Communication Services": "228810.KS", 
}

def find_ticker_by_name(name: str, market: str = "US"):
    """종목명으로 티커 검색 (API 직접 호출 및 최적화)"""
    try:
        # 검색어 최적화: 한국 주식인데 한글이면 뒤에 'stock' 추가
        search_query = name
        if market == "KR":
            # 한글 포함 여부 확인
            if any(ord('가') <= ord(char) <= ord('힣') for char in name):
                search_query = f"{name} stock" # '삼성전자 stock' 형식
            else:
                search_query = name
        
        # 1. yfinance Search 시도
        search = yf.Search(search_query, max_results=10)
        quotes = search.quotes
        
        # 2. yf.Search 결과가 없으면 영어 변환 시도 (주요 종목 예시)
        # (현실적으로 모든 한글명을 영어로 변환하는 사전은 크기가 너무 큼)
        
        if not quotes:
            # 보조 검색: 일반 API 호출 시도
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={search_query}"
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(url, headers=headers)
            if r.status_code == 200:
                quotes = r.json().get('quotes', [])

        if not quotes:
            return None
            
        # 시장에 따른 필터링
        for q in quotes:
            symbol = q.get('symbol', '')
            if market == "KR":
                if symbol.endswith(".KS") or symbol.endswith(".KQ"):
                    # 우선순위: .KS(코스피) > .KQ(코스닥)
                    return symbol
            else:
                if "." not in symbol:
                    return symbol
        
        return quotes[0]['symbol']
    except:
        return None

def _get_rs_base(ticker_symbol, index_symbol, sector_map, index_name):
    try:
        # 데이터 다운로드 및 가공 로직 (이미 잘 작동하므로 유지)
        ticker_obj = yf.Ticker(ticker_symbol)
        info = ticker_obj.info
        
        # symbol 정보가 없으면 직접 다운로드 시도
        symbol = info.get("symbol", ticker_symbol)
        sector = info.get("sector", "Technology")
        sector_etf = sector_map.get(sector, index_symbol)
        
        tickers = list(set([symbol, index_symbol, sector_etf]))
        raw_df = yf.download(tickers, period="2y", auto_adjust=True, progress=False)
        
        if raw_df.empty: return None, "데이터를 불러올 수 없습니다."

        if isinstance(raw_df.columns, pd.MultiIndex):
            if 'Price' in raw_df.columns.names:
                df = raw_df.xs('Close', axis=1, level='Price')
            elif 'Close' in raw_df.columns.levels[0]:
                df = raw_df['Close']
            else:
                df = raw_df.xs(raw_df.columns.levels[0][0], axis=1, level=0)
        else:
            df = raw_df

        df = df.ffill().dropna()

        def calculate_rs_ma(num, den):
            if num not in df.columns or den not in df.columns: return None, None
            ratio = (df[num] / df[den]).replace([np.inf, -np.inf], np.nan).dropna()
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
            fig.update_layout(title=dict(text=title_text, x=0.5), template="plotly_white", height=400,
                              margin=dict(t=60, b=40, l=50, r=20), hovermode="x unified",
                              legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                              yaxis=dict(title="Ratio", autorange=True), xaxis=dict(type='date'))
            return fig.to_json()

        chart1 = create_chart_json(symbol, index_symbol, f"1. {symbol} vs 시장 ({index_name})")
        chart2 = create_chart_json(sector_etf, index_symbol, f"2. 섹터 ({sector_etf}) vs 시장 ({index_name})")
        chart3 = create_chart_json(symbol, sector_etf, f"3. {symbol} vs 섹터 ({sector_etf})")

        if not chart1: return None, "데이터 부족으로 차트를 생성할 수 없습니다."

        return {
            "symbol": symbol, "sector_name": sector, "sector_etf": sector_etf, "index_name": index_name,
            "chart1_json": chart1, "chart2_json": chart2, "chart3_json": chart3
        }, None
        
    except Exception as e:
        return None, f"오류 발생: {str(e)}"

def get_rs_data(ticker_or_name: str):
    ticker = ticker_or_name if "." not in ticker_or_name and len(ticker_or_name) <= 5 else find_ticker_by_name(ticker_or_name, "US")
    if not ticker: ticker = ticker_or_name
    return _get_rs_base(ticker, "SPY", US_SECTOR_MAP, "SPY")

def get_rs_kr_data(ticker_or_name: str):
    if ticker_or_name.isdigit() and len(ticker_or_name) == 6:
        ticker = ticker_or_name + ".KS"
    else:
        # 한국어 검색어 개선: 뒤에 'stock' 추가하여 검색 시도
        ticker = find_ticker_by_name(ticker_or_name, "KR")
        
    if not ticker:
        return None, f"'{ticker_or_name}'에 해당하는 종목을 찾을 수 없습니다."
        
    return _get_rs_base(ticker, "^KS11", KR_SECTOR_MAP, "KOSPI")
