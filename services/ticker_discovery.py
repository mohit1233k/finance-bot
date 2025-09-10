# services/ticker_discovery.py
import pandas as pd
from typing import List
import requests
from io import StringIO

WIKI_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

def fetch_sp500_table() -> pd.DataFrame:
    """
    Fetch the S&P 500 constituents table from Wikipedia and return a DataFrame.
    Columns include: Symbol, Security, SEC filings, GICS Sector, GICS Sub Industry, Headquarters Location, Date first added, CIK, Founded
    """
    # pandas.read_html handles this well; fallback to requests if needed
    tables = pd.read_html(WIKI_SP500_URL)
    # The first table is generally the S&P500 list
    if not tables:
        raise ValueError("Could not fetch S&P 500 table from Wikipedia")
    df = tables[0]
    # Normalize column names (some locale differences may exist)
    df.columns = [c if isinstance(c, str) else str(c) for c in df.columns]
    # Ensure expected columns exist
    if 'Symbol' not in df.columns:
        # try alternative column names
        possible = [c for c in df.columns if 'Symbol' in c or 'Ticker' in c]
        if possible:
            df.rename(columns={possible[0]: 'Symbol'}, inplace=True)
    return df

def discover_tickers_by_sector(sector_query: str, limit: int = 50) -> List[str]:
    """
    Discover tickers from S&P 500 that match sector_query in their GICS Sector.
    sector_query: e.g., 'Information Technology', 'Health Care', 'Technology', 'Healthcare', 'IT'
    Returns a list of tickers (symbols).
    """
    df = fetch_sp500_table()
    # GICS Sector column can be 'GICS Sector' or 'Sector'
    sector_cols = [c for c in df.columns if 'GICS' in c and 'Sector' in c or c.lower() == 'sector']
    if sector_cols:
        sector_col = sector_cols[0]
    else:
        # guess fallback
        sector_col = df.columns[3] if len(df.columns) > 3 else df.columns[0]

    # Normalize and filter
    s = df[[ 'Symbol', sector_col ]].copy()
    s.columns = ['Symbol', 'Sector']
    # Case-insensitive match (substring)
    mask = s['Sector'].str.contains(sector_query, case=False, na=False)
    filtered = s[mask]
    tickers = filtered['Symbol'].str.replace('.', '-', regex=False).tolist()  # convert BRK.B style if needed
    return tickers[:limit]
