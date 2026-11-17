from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import pandas as pd


REQUIRED_COLUMNS = [
    "event_date",
    "headline",
    "source",
    "description",
    "url",
    "source_type",
    "collected_at",
]


def _normalized_headline(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def _event_id(row: pd.Series) -> str:
    identity = "|".join(
        [str(row["event_date"]), row["source"].lower(), _normalized_headline(row["headline"])]
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()[:16]


def clean_events(records: list[dict]) -> pd.DataFrame:
    """Clean, validate, standardize, and deduplicate raw event records."""
    frame = pd.DataFrame(records)
    for column in REQUIRED_COLUMNS:
        if column not in frame:
            frame[column] = ""
    frame = frame[REQUIRED_COLUMNS].copy()

    text_columns = ["headline", "source", "description", "url", "source_type"]
    for column in text_columns:
        frame[column] = frame[column].fillna("").astype(str).str.replace(r"\s+", " ", regex=True).str.strip()

    frame = frame[frame["headline"].ne("") & frame["source"].ne("")].copy()
    frame["description"] = frame["description"].mask(frame["description"].eq(""), frame["headline"])
    frame["event_date"] = pd.to_datetime(
        frame["event_date"], errors="coerce", utc=True, format="mixed"
    ).dt.date
    frame["collected_at"] = pd.to_datetime(frame["collected_at"], errors="coerce", utc=True)
    frame = frame.dropna(subset=["event_date"])

    frame["headline_key"] = frame["headline"].map(_normalized_headline)
    frame = frame.sort_values(["event_date", "collected_at"], ascending=[False, False])
    frame = frame.drop_duplicates(subset=["headline_key"], keep="first")
    frame["event_id"] = frame.apply(_event_id, axis=1)
    frame = frame.drop(columns="headline_key")
    return frame[["event_id", *REQUIRED_COLUMNS]].reset_index(drop=True)


def clean_json_file(raw_path: Path, output_path: Path) -> pd.DataFrame:
    payload = json.loads(raw_path.read_text(encoding="utf-8"))
    records = payload["events"] if isinstance(payload, dict) else payload
    frame = clean_events(records)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame


def data_quality_report(frame: pd.DataFrame) -> dict:
    return {
        "rows": int(len(frame)),
        "duplicate_event_ids": int(frame["event_id"].duplicated().sum()),
        "missing_headlines": int(frame["headline"].isna().sum() + frame["headline"].eq("").sum()),
        "missing_dates": int(frame["event_date"].isna().sum()),
        "sources": int(frame["source"].nunique()),
        "date_min": str(frame["event_date"].min()) if len(frame) else None,
        "date_max": str(frame["event_date"].max()) if len(frame) else None,
    }
