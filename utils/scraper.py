import requests
from bs4 import BeautifulSoup




def extract_text_from_url(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"finance-mvp-bot/1.0"})
        r.raise_for_status()
    except Exception:
        return ''
    soup = BeautifulSoup(r.text, 'html.parser')
    paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
    return '\n\n'.join(paragraphs)[:120000]