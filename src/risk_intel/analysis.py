from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

import pandas as pd

from risk_intel.config import RISK_CATEGORIES, SECTORS
from risk_intel.scoring import calculate_risk_score


CATEGORY_KEYWORDS = {
    "Technology Risk": (
        "cyber", "ransomware", "data breach", "software", "technology", "digital",
        "cloud", "system outage", "artificial intelligence", "crypto", "blockchain",
    ),
    "Credit Risk": (
        "default", "delinquen", "credit loss", "loan loss", "insolv", "bankrupt",
        "downgrade", "debt restructuring", "capital requirement", "asset quality",
    ),
    "Market Risk": (
        "interest rate", "inflation", "monetary policy", "federal funds", "treasury",
        "market volatility", "liquidity", "exchange rate", "securities", "trading",
    ),
    "Operational Risk": (
        "fraud", "misconduct", "penalty", "settlement", "compliance", "control",
        "outage", "disruption", "enforcement", "accounting", "reporting failure",
    ),
    "Emerging Risk": (
        "climate", "geopolit", "pandemic", "supply chain", "new rule", "proposal",
        "emerging", "quantum", "reputation risk", "digital asset",
    ),
}

SECTOR_KEYWORDS = {
    "Financials": ("bank", "credit", "loan", "capital", "financial", "securit", "fund"),
    "Information Technology": ("cyber", "software", "technology", "digital", "data", "cloud", "ai "),
    "Real Estate": ("mortgage", "real estate", "housing", "property"),
    "Energy": ("oil", "gas", "energy", "pipeline"),
    "Health Care": ("health", "hospital", "pharma", "drug"),
    "Industrials": ("manufactur", "transport", "shipping", "aviation", "supply chain"),
    "Consumer Discretionary": ("retail", "consumer", "automotive"),
    "Government and Public Sector": ("federal reserve", "government", "regulator", "treasury", "agency"),
}


def _text(row: pd.Series) -> str:
    return f"{row['headline']} {row['description']}".lower()


def _keyword_count(text: str, words: tuple[str, ...]) -> int:
    return sum(1 for word in words if word in text)


def baseline_analysis(row: pd.Series) -> dict:
    """Transparent fallback and benchmark; it is never reported as LLM output."""
    text = _text(row)
    scores = {category: _keyword_count(text, words) for category, words in CATEGORY_KEYWORDS.items()}
    category = max(scores, key=scores.get)
    if scores[category] == 0:
        category = "Emerging Risk"

    sectors = [sector for sector, words in SECTOR_KEYWORDS.items() if _keyword_count(text, words)]
    if not sectors:
        sectors = ["Cross-sector"]
    sectors = sectors[:3]

    high_impact = ("default", "failure", "breach", "emergency", "systemic", "shutdown", "crisis")
    severity = min(5, 2 + _keyword_count(text, high_impact))
    breadth = 4 if "industry" in text or "financial system" in text else min(5, max(2, len(sectors) + 1))
    urgency = 4 if any(word in text for word in ("immediate", "today", "outage", "attack", "emergency")) else 3
    confidence = min(5, max(2, scores[category] + 2))

    transmission = {
        "Market Risk": "The event may change asset prices, rates, liquidity, or market volatility.",
        "Credit Risk": "The event may weaken repayment capacity, asset quality, or counterparty strength.",
        "Operational Risk": "The event may create losses through failed processes, controls, compliance, or business continuity.",
        "Technology Risk": "The event may disrupt systems, compromise data, or increase cybersecurity exposure.",
        "Emerging Risk": "The event introduces a developing exposure whose scale and transmission remain uncertain.",
    }[category]

    return {
        "event_id": row["event_id"],
        "risk_category": category,
        "severity": severity,
        "breadth": breadth,
        "urgency": urgency,
        "confidence": confidence,
        "risk_score": calculate_risk_score(severity, breadth, urgency),
        "affected_sectors": sectors,
        "ai_summary": transmission,
        "analyst_focus": "Monitor follow-up disclosures, affected exposures, and evidence that the impact is spreading.",
        "analysis_method": "rule_based_baseline_v1",
        "analyzed_at": datetime.now(timezone.utc).isoformat(),
    }


SYSTEM_PROMPT = """You are a financial risk analyst. Analyze one event using exactly one primary category.

Taxonomy:
- Market Risk: rates, FX, equities, commodities, volatility, or market liquidity.
- Credit Risk: default, repayment capacity, counterparty weakness, asset quality, or credit spreads.
- Operational Risk: people, process, vendor, legal/compliance, fraud, or business-continuity failure.
- Technology Risk: cyberattack, data, software, models, AI, or technology infrastructure.
- Emerging Risk: new or difficult-to-quantify geopolitical, climate, public-health, or regulatory exposure.

Severity measures consequence, breadth measures scope, urgency measures required response speed, and confidence measures confidence in this classification. Each is an integer from 1 to 5. Use only approved sectors. Do not invent facts beyond the supplied text. The summary must explain the risk transmission channel in no more than 40 words."""


OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "risk_category": {"type": "string", "enum": list(RISK_CATEGORIES)},
        "severity": {"type": "integer", "minimum": 1, "maximum": 5},
        "breadth": {"type": "integer", "minimum": 1, "maximum": 5},
        "urgency": {"type": "integer", "minimum": 1, "maximum": 5},
        "confidence": {"type": "integer", "minimum": 1, "maximum": 5},
        "affected_sectors": {
            "type": "array", "items": {"type": "string", "enum": list(SECTORS)},
            "minItems": 1, "maxItems": 3,
        },
        "ai_summary": {"type": "string"},
        "analyst_focus": {"type": "string"},
    },
    "required": [
        "risk_category", "severity", "breadth", "urgency", "confidence",
        "affected_sectors", "ai_summary", "analyst_focus",
    ],
    "additionalProperties": False,
}


def llm_analysis(row: pd.Series, model: str | None = None) -> dict:
    """Generate structured analysis using the OpenAI Responses API."""
    from openai import OpenAI

    model = model or os.getenv("OPENAI_MODEL", "gpt-5-mini")
    client = OpenAI()
    event_input = {
        "date": str(row["event_date"]),
        "headline": row["headline"],
        "source": row["source"],
        "description": row["description"],
    }
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(event_input, ensure_ascii=False)},
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "risk_analysis",
                "strict": True,
                "schema": OUTPUT_SCHEMA,
            }
        },
    )
    result = json.loads(response.output_text)
    result.update(
        {
            "event_id": row["event_id"],
            "risk_score": calculate_risk_score(
                result["severity"], result["breadth"], result["urgency"]
            ),
            "analysis_method": model,
            "analyzed_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return result


def analyze_events(events: pd.DataFrame, method: str = "auto", limit: int | None = None) -> list[dict]:
    """Analyze events with the LLM when configured, otherwise use the benchmark."""
    if method not in {"auto", "llm", "baseline"}:
        raise ValueError("method must be auto, llm, or baseline")
    use_llm = method == "llm" or (method == "auto" and bool(os.getenv("OPENAI_API_KEY")))
    if method == "llm" and not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("OPENAI_API_KEY is required for method='llm'")

    subset = events.head(limit) if limit else events
    analyzer = llm_analysis if use_llm else baseline_analysis
    return [analyzer(row) for _, row in subset.iterrows()]
