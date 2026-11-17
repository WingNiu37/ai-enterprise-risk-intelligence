"""Run the LLM only on the human-labelled sample before paying for a full run."""

from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from risk_intel.analysis import analyze_events
from risk_intel.clean import clean_json_file
from risk_intel.database import initialize_database, load_events, replace_analysis
from risk_intel.evaluate import evaluate_predictions


RAW_PATH = Path("data/raw/sample_events.json")
CLEANED_PATH = Path("data/processed/events_cleaned.csv")
LABELS_PATH = Path("data/labels/manual_labels.csv")
DATABASE_PATH = Path("database/risk_intelligence.db")
CACHE_PATH = Path("data/processed/llm_analysis_cache.jsonl")
REPORTS_PATH = Path("reports")


def main() -> None:
    load_dotenv()
    events = clean_json_file(RAW_PATH, CLEANED_PATH)
    labels = pd.read_csv(LABELS_PATH)
    labelled_events = events[events["event_id"].isin(labels["event_id"])].copy()

    if len(labelled_events) != len(labels):
        missing = set(labels["event_id"]) - set(labelled_events["event_id"])
        raise ValueError(f"Labelled events missing from sample data: {sorted(missing)}")

    if DATABASE_PATH.exists():
        DATABASE_PATH.unlink()
    initialize_database(DATABASE_PATH)
    load_events(DATABASE_PATH, events)
    analyses = analyze_events(
        labelled_events,
        method="llm",
        cache_path=CACHE_PATH,
    )
    replace_analysis(DATABASE_PATH, analyses)
    metrics = evaluate_predictions(DATABASE_PATH, LABELS_PATH, REPORTS_PATH)

    print(f"Evaluated labelled events: {metrics['matched_events']}")
    print(f"LLM classification accuracy: {metrics['accuracy']:.1%}")
    print(f"Reusable cache: {CACHE_PATH}")


if __name__ == "__main__":
    main()
