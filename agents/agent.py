from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_qdrant import Qdrant
from langchain.chains import RetrievalQA
from langchain.schema import Document
import os


QDRANT_URL = os.getenv('QDRANT_URL', 'http://localhost:6333')
QDRANT_COLLECTION = os.getenv('QDRANT_COLLECTION', 'finance_mvp')




def research_query(sector: str, query: str) -> dict:
# prepare retriever for sector
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    collection_name = f"{QDRANT_COLLECTION}_{sector.lower()}"
    store = Qdrant.from_existing_collection(embedding=embeddings, collection_name=collection_name, url=QDRANT_URL)
    retriever = store.as_retriever(search_type='similarity', search_kwargs={"k":5})


    llm = GoogleGenerativeAI(model="gemini-2.0-flash")
    qa = RetrievalQA.from_chain_type(llm=llm, chain_type='stuff',  retriever=retriever)


    system_preface = (
    "You are a finance research assistant. Answer ONLY finance-related queries. Use  retrieved documents and provide sources. "
    "If the question is outside finance, state you cannot answer."
    )
    prompt = system_preface + "\n\n" + query
    answer = qa.invoke({"query": prompt})


    # NOTE: RetrievalQA doesn't always return sources in this simple setup. We return answer and a placeholder.
    return {"answer": answer.result, "sources": ["retriever results available in Qdrant collection"]}