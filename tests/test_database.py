from pathlib import Path

import pandas as pd

from risk_intel.database import export_dashboard_view, initialize_database, load_events, replace_analysis


def test_database_join_and_export(tmp_path: Path):
    database = tmp_path / "test.db"
    initialize_database(database)
    events = pd.DataFrame([
        {
            "event_id": "event-1",
            "event_date": "2026-01-01",
            "headline": "Example event",
            "source": "Example",
            "description": "Example description",
            "url": "https://example.com",
            "source_type": "sample",
            "collected_at": "2026-01-01T00:00:00+00:00",
        }
    ])
    load_events(database, events)
    replace_analysis(database, [{
        "event_id": "event-1",
        "risk_category": "Technology Risk",
        "severity": 4,
        "breadth": 3,
        "urgency": 4,
        "confidence": 5,
        "risk_score": 74,
        "affected_sectors": ["Financials", "Information Technology"],
        "ai_summary": "Example summary",
        "analyst_focus": "Example focus",
        "analysis_method": "test",
        "analyzed_at": "2026-01-01T00:00:00+00:00",
    }])
    output = tmp_path / "dashboard.csv"
    exported = export_dashboard_view(database, output)
    assert len(exported) == 1
    assert exported.loc[0, "affected_sectors"] == "Financials; Information Technology"
    assert output.exists()
