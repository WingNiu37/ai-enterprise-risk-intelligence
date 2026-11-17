from risk_intel.clean import clean_events, data_quality_report


def test_cleaning_deduplicates_and_fills_description():
    records = [
        {
            "event_date": "2026-01-02T10:30:00Z",
            "headline": " Bank reports outage ",
            "source": "Example",
            "description": "",
            "url": "https://example.com/a",
            "source_type": "sample",
            "collected_at": "2026-01-02T12:00:00Z",
        },
        {
            "event_date": "2026-01-02T09:30:00Z",
            "headline": "Bank reports outage",
            "source": "Example",
            "description": "Duplicate",
            "url": "https://example.com/b",
            "source_type": "sample",
            "collected_at": "2026-01-02T11:00:00Z",
        },
    ]
    cleaned = clean_events(records)
    assert len(cleaned) == 1
    assert cleaned.iloc[0]["description"] == "Bank reports outage"
    assert data_quality_report(cleaned)["duplicate_event_ids"] == 0
