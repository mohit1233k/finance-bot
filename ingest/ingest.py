import requests
from bs4 import BeautifulSoup
from langchain.schema import Document
from typing import List
from qdrant_client import QdrantClient
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_qdrant import Qdrant
import os
import getpass
QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION', 'finance_mvp')

# if "GOOGLE_API_KEY" not in os.environ:
#     os.environ["GOOGLE_API_KEY"] = getpass.getpass("Enter your Google AI API key: ")
def _extract_text(url: str) -> str:
    try:
        r = requests.get(url, timeout=10, headers={"User-Agent":"finance-mvp/1.0"})
        r.raise_for_status()
    except Exception as e:
        return ''
    soup = BeautifulSoup(r.text, 'html.parser')
    # print(soup)
    paragraphs = [p.get_text(separator=' ', strip=True) for p in soup.find_all('p')]
    return '\n\n'.join(paragraphs)[:120000]

def ingest_urls(sector: str, urls: List[str]) -> int:
    docs = []
    for u in urls:
        text = _extract_text(u)
        if not text:
            print(f"Failed to extract text from {u}")
            continue
        docs.append(Document(page_content=text, metadata={"source": u, "sector": sector}))
    if not docs:
        print("No documents to ingest.")
        return 0

    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001", google_api_key=os.getenv('GOOGLE_API_KEY'))
    collection_name = f"{QDRANT_COLLECTION}_{sector.lower()}"

    try:
        # Try to connect to existing collection, or create if not exists
        vector_store = Qdrant.from_documents(
            embedding=embeddings,
            documents=docs,
            collection_name=collection_name,
            url=QDRANT_URL
        )
        vector_store.add_documents(docs)
        print(f"Ingested {len(docs)} documents into {collection_name}")
        return len(docs)
    except Exception as e:
        print(f"Error during ingestion: {e}")
        return 0
