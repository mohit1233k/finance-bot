# services/intent.py
import re
from typing import Optional

# simple keyword based sector detection
SECTOR_KEYWORDS = {
    "tech": [
        r"\btech\b", r"\btechnology\b", r"\bsoftware\b", r"\bsemiconductor\b",
        r"\bit\b", r"\bcloud\b", r"\bsaas\b", r"\bchip\b", r"\bai\b", r"\bcybersecurity\b"
    ],
    "healthcare": [
        r"\bhealthcare\b", r"\bhealth care\b", r"\bpharma\b", r"\bbiotech\b",
        r"\bmedical\b", r"\bdrug\b", r"\bhospital\b", r"\bclinical\b", r"\bbiotech\b"
    ],
    "finance": [
        r"\bfinance\b", r"\bbank\b", r"\binsurance\b", r"\bstock market\b", r"\binvest\b",
        r"\bportfolio\b", r"\bdividend\b", r"\basset allocation\b"
    ],
}

def detect_sector_from_query(query: str) -> Optional[str]:
    """Return a best-match sector key or None if not confidently detected."""
    q = query.lower()
    scores = {k: 0 for k in SECTOR_KEYWORDS.keys()}
    for sector, patterns in SECTOR_KEYWORDS.items():
        for pat in patterns:
            if re.search(pat, q):
                scores[sector] += 1

    # choose highest score if it's > 0 and unique
    best = max(scores.items(), key=lambda x: x[1])
    if best[1] == 0:
        return None
    # if tie or low evidence (1 match) we can still return best but risk false positive;
    # here we return best if score >=1 (simple approach) — tune later if needed
    return best[0]
