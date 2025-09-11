from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from ingest.ingest import ingest_urls
from agents.agent import research_query
from services.market import get_price, top_stocks_for_sector
from services.intent_llm import detect_sector_and_intent_llm
from agents.unified_agents import run_agent
router = APIRouter()


class IngestReq(BaseModel):
    sector: str
    urls: List[str]


class ResearchReq(BaseModel):
    sector: str
    query: str


@router.post('/ingest')
async def ingest(req: IngestReq):
    inserted = ingest_urls(req.sector, req.urls)
    if inserted == 0:
        raise HTTPException(status_code=400, detail="No documents ingested")
    return {"ingested": inserted, "sector": req.sector}


@router.get('/price')
async def price(ticker: str):
    try:
        p = get_price(ticker)
        return p
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/top-stocks')
async def top_stocks(sector: str = 'Tech', n: Optional[int] = 5):
    try:
        result = top_stocks_for_sector(sector, n)
        return {"sector": sector, "top": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/research')
async def research(req: ResearchReq):
# research_query returns a dict {answer: str, sources: [..]}
    return research_query(req.sector, req.query)


@router.get('/health')
async def health():
    return {"status":"ok"}

@router.post('/research_auto')
async def research_auto(payload: dict):
    query = payload.get("query") or payload.get("q") or ""
    if not query:
        raise HTTPException(status_code=400, detail="query field required")

    det = detect_sector_and_intent_llm(query)
    sector = det.get("sector")
    intent = det.get("intent")
    confidence = det.get("confidence")
    source = det.get("source")
    print(f"Detected sector={sector} intent={intent} confidence={confidence} source={source}")
    # If sector unknown, fallback to both Sectors (old behavior)
    if not sector:
        # run both sectors and combine
        sectors_to_run = ["tech", "healthcare"]
        combined = {"answers": [], "meta": {"detector_source": source, "confidence": confidence}}
        for s in sectors_to_run:
            r = research_query(s, query) if intent != "top_stocks" else {"top": top_stocks_for_sector(s, n=5)}
            combined["answers"].append({"sector": s, "result": r})
        return {"detected_sector": None, "combined": combined}

    # Otherwise route based on intent
    if intent == "top_stocks":
        top = top_stocks_for_sector(sector, n=5)
        return {"detected_sector": sector, "intent": intent, "confidence": confidence, "source": source, "result": {"top": top}}
    else:
        # research path
        r = research_query(sector, query)
        return {"detected_sector": sector, "intent": intent, "confidence": confidence, "source": source, "result": r}
    

    
@router.post("/ask_agent")
async def ask_agent(payload: dict):
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="Missing query")
    result = run_agent(query)
    return {"query": query, "answer": result}