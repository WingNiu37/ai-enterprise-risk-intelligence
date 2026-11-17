from __future__ import annotations

import hashlib
import json
import os
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html import unescape
from pathlib import Path

from risk_intel.config import RAW_DIR, RSS_SOURCES


USER_AGENT = "enterprise-risk-intelligence/0.1 student research project"


def _download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def _plain_text(value: str | None) -> str:
    if not value:
        return ""
    without_tags = re.sub(r"<[^>]+>", " ", unescape(value))
    return re.sub(r"\s+", " ", without_tags).strip()


def fetch_rss_feed(source: str, url: str) -> list[dict]:
    """Download one official RSS feed and normalize it to raw event records."""
    root = ET.fromstring(_download(url))
    collected_at = datetime.now(timezone.utc).isoformat()
    records: list[dict] = []

    # RSS uses <item>; Atom uses <entry>. The wildcard handles namespaces.
    items = root.findall(".//item") or root.findall(".//{*}entry")
    for item in items:
        def value(*names: str) -> str:
            for name in names:
                element = item.find(name)
                if element is None:
                    element = item.find(f"{{*}}{name}")
                if element is not None:
                    if name == "link" and element.get("href"):
                        return element.get("href", "")
                    return element.text or ""
            return ""

        headline = _plain_text(value("title"))
        if not headline:
            continue
        records.append(
            {
                "event_date": value("pubDate", "published", "updated"),
                "headline": headline,
                "source": source,
                "description": _plain_text(value("description", "summary", "content")),
                "url": value("link"),
                "source_type": "rss",
                "collected_at": collected_at,
            }
        )
    return records


def fetch_official_feeds() -> tuple[list[dict], dict[str, str]]:
    """Collect all configured feeds while preserving per-source errors."""
    events: list[dict] = []
    errors: dict[str, str] = {}
    for source, url in RSS_SOURCES.items():
        try:
            events.extend(fetch_rss_feed(source, url))
        except Exception as exc:  # one unavailable feed must not break the run
            errors[source] = f"{type(exc).__name__}: {exc}"
    return events, errors


def fetch_alpha_vantage(api_key: str, limit: int = 200) -> list[dict]:
    """Collect market news from the documented Alpha Vantage endpoint."""
    params = {
        "function": "NEWS_SENTIMENT",
        "topics": "financial_markets",
        "sort": "LATEST",
        "limit": str(limit),
        "apikey": api_key,
    }
    url = "https://www.alphavantage.co/query?" + urllib.parse.urlencode(params)
    payload = json.loads(_download(url))
    if "feed" not in payload:
        message = payload.get("Information") or payload.get("Note") or str(payload)
        raise RuntimeError(f"Alpha Vantage did not return a feed: {message}")

    collected_at = datetime.now(timezone.utc).isoformat()
    return [
        {
            "event_date": item.get("time_published", ""),
            "headline": item.get("title", ""),
            "source": item.get("source", "Alpha Vantage"),
            "description": item.get("summary", ""),
            "url": item.get("url", ""),
            "source_type": "alpha_vantage",
            "collected_at": collected_at,
        }
        for item in payload["feed"]
    ]


def fetch_nvd_cves(limit: int = 25, lookback_days: int = 60) -> list[dict]:
    """Collect recently published vulnerabilities from the public NVD API."""
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback_days)
    timestamp = "%Y-%m-%dT%H:%M:%S.000Z"
    params = {
        "pubStartDate": start.strftime(timestamp),
        "pubEndDate": end.strftime(timestamp),
        "resultsPerPage": str(limit),
    }
    url = "https://services.nvd.nist.gov/rest/json/cves/2.0?" + urllib.parse.urlencode(params)
    payload = json.loads(_download(url))
    collected_at = datetime.now(timezone.utc).isoformat()
    records: list[dict] = []
    for wrapper in payload.get("vulnerabilities", []):
        cve = wrapper.get("cve", {})
        descriptions = cve.get("descriptions", [])
        description = next(
            (item.get("value", "") for item in descriptions if item.get("lang") == "en"), ""
        )
        cve_id = cve.get("id", "Unknown CVE")
        records.append(
            {
                "event_date": cve.get("published", ""),
                "headline": f"{cve_id}: {description[:160]}",
                "source": "NIST National Vulnerability Database",
                "description": description,
                "url": f"https://nvd.nist.gov/vuln/detail/{cve_id}",
                "source_type": "nvd_api",
                "collected_at": collected_at,
            }
        )
    return records


def collect_raw_events(output_path: Path | None = None) -> Path:
    """Collect official feeds plus optional Alpha Vantage data and save JSON."""
    events, errors = fetch_official_feeds()
    try:
        events.extend(fetch_nvd_cves())
    except Exception as exc:
        errors["NIST NVD"] = f"{type(exc).__name__}: {exc}"
    api_key = os.getenv("ALPHAVANTAGE_API_KEY")
    if api_key:
        try:
            events.extend(fetch_alpha_vantage(api_key))
        except Exception as exc:
            errors["Alpha Vantage"] = f"{type(exc).__name__}: {exc}"

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    output_path = output_path or RAW_DIR / "events_latest.json"
    payload = {
        "metadata": {
            "collected_at": datetime.now(timezone.utc).isoformat(),
            "event_count": len(events),
            "source_errors": errors,
            "run_id": hashlib.sha256(str(events).encode()).hexdigest()[:12],
        },
        "events": events,
    }
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path
