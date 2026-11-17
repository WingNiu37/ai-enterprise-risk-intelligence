from __future__ import annotations

import argparse
import json
from pathlib import Path

from dotenv import load_dotenv

from risk_intel.analysis import analyze_events
from risk_intel.clean import clean_json_file, data_quality_report
from risk_intel.config import DATABASE_DIR, PROCESSED_DIR
from risk_intel.database import (
    export_dashboard_view,
    initialize_database,
    load_events,
    replace_analysis,
)
from risk_intel.fetch import collect_raw_events


def run(
    method: str = "auto",
    limit: int | None = None,
    raw_path: Path | None = None,
) -> dict:
    load_dotenv()
    raw_path = raw_path or collect_raw_events()
    cleaned_path = PROCESSED_DIR / "events_cleaned.csv"
    events = clean_json_file(raw_path, cleaned_path)

    database_path = DATABASE_DIR / "risk_intelligence.db"
    if database_path.exists():
        database_path.unlink()
    initialize_database(database_path)
    load_events(database_path, events)

    cache_path = PROCESSED_DIR / "llm_analysis_cache.jsonl"
    analyses = analyze_events(
        events,
        method=method,
        limit=limit,
        cache_path=cache_path,
    )
    replace_analysis(database_path, analyses)
    dashboard_path = PROCESSED_DIR / "dashboard_events.csv"
    dashboard = export_dashboard_view(database_path, dashboard_path)

    report = {
        "raw_path": str(raw_path),
        "cleaned_path": str(cleaned_path),
        "database_path": str(database_path),
        "dashboard_path": str(dashboard_path),
        "data_quality": data_quality_report(events),
        "analyzed_events": len(analyses),
        "dashboard_rows": len(dashboard),
        "analysis_method": analyses[0]["analysis_method"] if analyses else None,
        "llm_cache_path": str(cache_path) if method in {"auto", "llm"} else None,
    }
    (PROCESSED_DIR / "pipeline_report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the enterprise risk intelligence pipeline")
    parser.add_argument("--method", choices=["auto", "llm", "baseline"], default="auto")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--raw-path", type=Path, default=None)
    args = parser.parse_args()
    print(json.dumps(run(args.method, args.limit, args.raw_path), indent=2))


if __name__ == "__main__":
    main()
