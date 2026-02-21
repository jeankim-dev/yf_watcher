import yfinance as yf
import json

def test_search(name, market):
    print(f"Searching for '{name}' in market '{market}'...")
    try:
        search = yf.Search(name, max_results=10)
        quotes = search.quotes
        print(f"Found {len(quotes)} results.")
        for i, q in enumerate(quotes):
            print(f"[{i}] Symbol: {q.get('symbol')}, Name: {q.get('shortname')}, Exchange: {q.get('exchange')}")
    except Exception as e:
        print(f"Error: {e}")

test_search("삼성전자", "KR")
test_search("Samsung Electronics", "KR")
