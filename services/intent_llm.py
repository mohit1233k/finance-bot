
import os
import json
from typing import Dict, Optional, Tuple

from langchain_google_genai import GoogleGenerativeAI
from langchain.schema import HumanMessage

from dotenv import load_dotenv
load_dotenv()

# Fallback keyword detector (keeps previous behavior in case LLM fails)
from services.intent import detect_sector_from_query as keyword_detect

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "models/gemini-2.0-flash")
CONFIDENCE_THRESHOLD = float(os.getenv("SECTOR_DETECT_CONF", 0.6))

PROMPT_TEMPLATE = """
You are a short, precise assistant that classifies a *single user query* into:
  1) a sector: must be one of these canonical values: "tech", "healthcare", "finance", or "unknown"
  2) an intent: one of "top_stocks" or "research" or "unknown"
  3) a confidence score in [0.0, 1.0]

Return ONLY a single-line JSON object with keys: sector, intent, confidence.

Rules:
- If the query clearly asks "top" or "best" or "top stocks" or "top movers" or "top gainers" treat intent as "top_stocks".
- If the query asks about "trends", "analysis", "outlook", "opportunities", "what to invest", "where to invest", or "why invest", treat intent as "research".
- Map common words to sectors:
    - Tech: tech, technology, it, software, semiconductor, ai, cloud, saas
    - Healthcare: healthcare, health care, health, pharma, biotech, medical, clinical
    - Finance: finance, banking, bank, insurance, portfolio
- If unsure, use "unknown" for sector or intent.
- Confidence should reflect model certainty (0.0 - 1.0).
- Output example exactly like:
  {{ "sector":"tech","intent":"top_stocks","confidence":0.92 }}
- Do not include any extra text, only JSON.

User query:
\"\"\"{query}\"\"\"
""".strip()


def _call_llm(prompt: str, model_name: str = GEMINI_MODEL) -> Optional[str]:
    """
    Call Gemini through LangChain wrapper and return raw text output (string).
    """
    try:
        llm = GoogleGenerativeAI(model=model_name,api_key=os.getenv("GOOGLE_API_KEY"))
        # Use HumanMessage wrapper for safety with generate()
        resp = llm.generate([[HumanMessage(content=prompt)]])
        # resp.generations is a nested list: generations[0][0].text
        text = resp.generations[0][0].text if resp and resp.generations else None
        return text.strip() if text else None
    except Exception as e:
        # LLM call failed
        return None


def detect_sector_and_intent_llm(query: str, threshold: float = CONFIDENCE_THRESHOLD) -> Dict:
    """
    Return a dict:
      {
        "sector": "tech" | "healthcare" | "finance" | "unknown" | None,
        "intent": "top_stocks" | "research" | "unknown",
        "confidence": float,
        "source": "llm" | "keyword-fallback" | "llm-parse-error"
      }
    The function will:
      1) call the LLM and try to parse JSON
      2) if parse/llm fails or confidence < threshold, fall back to keyword detector
    """
    prompt = PROMPT_TEMPLATE.format(query=query)
    raw = _call_llm(prompt)
    if raw:
        # try parse JSON
        try:
            parsed = json.loads(raw)
            sector = parsed.get("sector", "unknown")
            intent = parsed.get("intent", "unknown")
            confidence = float(parsed.get("confidence", 0.0))
            # if confidence high enough, accept
            if confidence >= threshold and sector in ("tech", "healthcare", "finance"):
                return {"sector": sector, "intent": intent, "confidence": confidence, "source": "llm"}
            # else treat as low-confidence and fallback
            else:
                # fallback to keyword detector
                fallback_sector = keyword_detect(query)
                # keyword_detect returns str or None; normalize to canonical keys
                canonical = _normalize_keyword_sector(fallback_sector)
                return {
                    "sector": canonical,
                    "intent": intent if confidence >= 0.3 else _heuristic_intent(query),
                    "confidence": confidence,
                    "source": "llm-low-confidence-fallback-keyword"
                }
        except Exception:
            # parsing error -> fallback to keyword
            fallback_sector = keyword_detect(query)
            canonical = _normalize_keyword_sector(fallback_sector)
            return {"sector": canonical, "intent": _heuristic_intent(query), "confidence": 0.0, "source": "llm-parse-error"}
    else:
        # llm call failed entirely -> fallback
        fallback_sector = keyword_detect(query)
        canonical = _normalize_keyword_sector(fallback_sector)
        return {"sector": canonical, "intent": _heuristic_intent(query), "confidence": 0.0, "source": "llm-call-failed"}


def _normalize_keyword_sector(sector_str: Optional[str]) -> Optional[str]:
    if not sector_str:
        return None
    s = sector_str.lower()
    if "tech" in s or "it" == s:
        return "tech"
    if "health" in s:
        return "healthcare"
    if "finance" in s or "bank" in s:
        return "finance"
    return None


def _heuristic_intent(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ["top", "best", "gainers", "top stocks", "top movers"]):
        return "top_stocks"
    # research-ish keywords
    if any(k in q for k in ["trend", "outlook", "analysis", "where to invest", "opportunities", "why invest", "should i invest"]):
        return "research"
    return "unknown"
