from pathlib import Path

from risk_intel.evaluate import evaluate_predictions


if __name__ == "__main__":
    metrics = evaluate_predictions(
        Path("database/risk_intelligence.db"),
        Path("data/labels/manual_labels.csv"),
        Path("reports"),
    )
    print(f"Matched events: {metrics['matched_events']}")
    print(f"Accuracy: {metrics['accuracy']:.1%}")
