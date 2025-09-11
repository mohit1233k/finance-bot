import requests
from bs4 import BeautifulSoup
from langchain.tools import tool

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; FinanceMVP/1.0)"}

@tool("search_tech_data", return_direct=False)
def search_tech_data(query: str) -> str:
    """Fetches latest Tech sector headlines from Yahoo Finance."""
    url = "https://finance.yahoo.com/tech/"
    html = requests.get(url, headers=HEADERS, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    headlines = [h.get_text() for h in soup.find_all("h3")[:5]]
    return "Tech headlines: " + "; ".join(headlines)

@tool("search_healthcare_data", return_direct=False)
def search_healthcare_data(query: str) -> str:
    """Fetches latest Healthcare sector headlines from Yahoo Finance."""
    url = "https://finance.yahoo.com/healthcare/"
    html = requests.get(url, headers=HEADERS, timeout=10).text
    soup = BeautifulSoup(html, "html.parser")
    headlines = [h.get_text() for h in soup.find_all("h3")[:5]]
    return "Healthcare headlines: " + "; ".join(headlines)
