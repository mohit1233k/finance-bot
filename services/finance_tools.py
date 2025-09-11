import yfinance as yf
from langchain.tools import tool

@tool("get_stock_price", return_direct=False)
def get_stock_price(ticker: str) -> str:
    """Returns the latest stock price for a given ticker symbol."""
    try:
        t = yf.Ticker(ticker)
        price = t.history(period="1d")["Close"].iloc[-1]
        return f"{ticker} price is {price:.2f}"
    except Exception as e:
        return f"Error fetching {ticker}: {str(e)}"
