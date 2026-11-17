from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from risk_intel.config import ROOT, SECTORS


def connect(database_path: Path) -> sqlite3.Connection:
    connection = sqlite3.connect(database_path)
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(database_path: Path) -> None:
    database_path.parent.mkdir(parents=True, exist_ok=True)
    schema = (ROOT / "sql" / "schema.sql").read_text(encoding="utf-8")
    with connect(database_path) as connection:
        connection.executescript(schema)
        connection.executemany(
            "INSERT OR IGNORE INTO sectors (sector_name) VALUES (?)",
            [(sector,) for sector in SECTORS],
        )


def load_events(database_path: Path, events: pd.DataFrame) -> int:
    columns = [
        "event_id", "event_date", "headline", "source", "description",
        "url", "source_type", "collected_at",
    ]
    prepared = events[columns].copy().astype(str)
    with connect(database_path) as connection:
        prepared.to_sql("events", connection, if_exists="append", index=False, method="multi")
    return len(prepared)


def replace_analysis(database_path: Path, analyses: list[dict]) -> None:
    analysis_sql = """
        INSERT OR REPLACE INTO risk_analysis (
            event_id, risk_category, severity, breadth, urgency, confidence,
            risk_score, ai_summary, analyst_focus, analysis_method, analyzed_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    with connect(database_path) as connection:
        for item in analyses:
            connection.execute(
                analysis_sql,
                tuple(item[key] for key in [
                    "event_id", "risk_category", "severity", "breadth", "urgency",
                    "confidence", "risk_score", "ai_summary", "analyst_focus",
                    "analysis_method", "analyzed_at",
                ]),
            )
            connection.execute("DELETE FROM event_sectors WHERE event_id = ?", (item["event_id"],))
            connection.executemany(
                """
                INSERT OR IGNORE INTO event_sectors (event_id, sector_id)
                SELECT ?, sector_id FROM sectors WHERE sector_name = ?
                """,
                [(item["event_id"], sector) for sector in item["affected_sectors"]],
            )


def export_dashboard_view(database_path: Path, output_path: Path) -> pd.DataFrame:
    with connect(database_path) as connection:
        frame = pd.read_sql_query(
            "SELECT * FROM dashboard_events ORDER BY risk_score DESC, event_date DESC",
            connection,
        )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    frame.to_csv(output_path, index=False)
    return frame
