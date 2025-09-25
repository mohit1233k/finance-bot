import requests
from bs4 import BeautifulSoup
from langchain.tools import tool
import yfinance as yf

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FinanceMVP/1.0)"}

@tool("search_tech_data", return_direct=False)
def search_tech_data(query: str) -> str:
    """Fetches latest Tech sector headlines from Yahoo Finance."""
    url = "https://finance.yahoo.com/sectors/technology/"
    html = requests.get(url, headers=HEADERS, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    headlines = [h.get_text() for h in soup.find_all("h3")[:5]]
    return "Tech headlines: " + "; ".join(headlines)

@tool("search_healthcare_data", return_direct=False)
def search_healthcare_data(query: str) -> str:
    """Fetches latest Healthcare sector headlines from Yahoo Finance."""
    url = "https://finance.yahoo.com/sector/healthcare"
    html = requests.get(url, headers=HEADERS, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    headlines = [h.get_text() for h in soup.find_all("h3")[:5]]
    return "Healthcare headlines: " + "; ".join(headlines)


@tool("get_stock_fundamentals", return_direct=False)
def get_stock_fundamentals(ticker: str) -> str:
    """Fetches key fundamental data (PE, Market Cap, Dividend Yield)."""
    stock = yf.Ticker(ticker)
    info = stock.info
    fundamentals = {
        "Market Cap": info.get("marketCap"),
        "PE Ratio": info.get("trailingPE"),
        "Forward PE": info.get("forwardPE"),
        "Dividend Yield": info.get("dividendYield")
    }
    return f"{ticker} fundamentals: {fundamentals}"