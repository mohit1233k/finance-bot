# services/market.py
import yfinance as yf
from typing import List
import os
from .ticker_discovery import discover_tickers_by_sector

def get_price(ticker: str) -> dict:
    t = yf.Ticker(ticker)
    hist = t.history(period='1d')
    if hist.empty:
        raise ValueError('No data for ticker')
    price = float(hist['Close'].iloc[-1])
    return {"ticker": ticker.upper(), "price": price}

def top_stocks_for_sector(sector: str, n: int = 5) -> List[dict]:
    """
    Discover tickers dynamically for the given sector (from S&P 500 list),
    then compute percent change over the last trading day and return top N.
    """
    tickers = discover_tickers_by_sector(sector_query=sector, limit=200)
    if not tickers:
        raise ValueError(f"No tickers discovered for sector '{sector}'")

    results = []
    for t in tickers:
        try:
            tk = yf.Ticker(t)
            hist = tk.history(period='2d')  # prev + last
            if hist.empty:
                continue
            # compute percent change from previous close to last close
            if len(hist['Close']) >= 2:
                prev = float(hist['Close'].iloc[-2])
                last = float(hist['Close'].iloc[-1])
            else:
                prev = float(hist['Close'].iloc[0])
                last = prev
            if prev == 0:
                pct = 0.0
            else:
                pct = ((last - prev) / prev) * 100
            results.append({"ticker": t, "price": last, "pct_change": round(pct, 2)})
        except Exception:
            # ignore tickers that fail to fetch
            continue

    # sort and return top n by pct_change desc
    results_sorted = sorted(results, key=lambda x: x['pct_change'], reverse=True)
    return results_sorted[:n]
