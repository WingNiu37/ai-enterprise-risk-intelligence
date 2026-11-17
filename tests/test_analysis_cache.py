import json

import pandas as pd

from risk_intel.analysis import analyze_events


def _events() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "event_id": "event-1",
                "event_date": "2026-01-01",
                "headline": "Bank reports loan defaults",
                "source": "Test source",
                "description": "Asset quality weakened after borrower defaults.",
            }
        ]
    )


def test_baseline_does_not_create_llm_cache(tmp_path):
    cache_path = tmp_path / "cache.jsonl"

    results = analyze_events(_events(), method="baseline", cache_path=cache_path)

    assert results[0]["event_id"] == "event-1"
    assert results[0]["analysis_method"] == "rule_based_baseline_v1"
    assert not cache_path.exists()


def test_llm_reuses_cached_result_without_api_key(tmp_path, monkeypatch):
    cache_path = tmp_path / "cache.jsonl"
    cached = {
        "event_id": "event-1",
        "risk_category": "Credit Risk",
        "analysis_method": "cached-test-model",
    }
    cache_path.write_text(json.dumps(cached) + "\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-used")

    results = analyze_events(_events(), method="llm", cache_path=cache_path)

    assert results == [cached]


def test_invalid_cache_is_reported(tmp_path, monkeypatch):
    cache_path = tmp_path / "cache.jsonl"
    cache_path.write_text("not-json\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key-not-used")

    try:
        analyze_events(_events(), method="llm", cache_path=cache_path)
    except ValueError as error:
        assert "line 1" in str(error)
    else:
        raise AssertionError("Invalid cache should raise ValueError")
