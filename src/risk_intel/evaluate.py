from __future__ import annotations

import json
import sqlite3
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

from risk_intel.config import RISK_CATEGORIES


def evaluate_predictions(database_path: Path, labels_path: Path, output_dir: Path) -> dict:
    labels = pd.read_csv(labels_path)
    with sqlite3.connect(database_path) as connection:
        predictions = pd.read_sql_query(
            "SELECT event_id, risk_category AS predicted_category FROM risk_analysis",
            connection,
        )
    comparison = labels.merge(predictions, on="event_id", how="inner")
    if comparison.empty:
        raise ValueError("No labelled event IDs matched database predictions")

    y_true = comparison["human_category"]
    y_pred = comparison["predicted_category"]
    report = classification_report(
        y_true, y_pred, labels=list(RISK_CATEGORIES), output_dict=True, zero_division=0
    )
    metrics = {
        "labelled_events": int(len(labels)),
        "matched_events": int(len(comparison)),
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "classification_report": report,
    }

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "evaluation_metrics.json").write_text(
        json.dumps(metrics, indent=2), encoding="utf-8"
    )
    comparison.to_csv(output_dir / "evaluation_comparison.csv", index=False)

    matrix = confusion_matrix(y_true, y_pred, labels=list(RISK_CATEGORIES))
    plt.figure(figsize=(9, 7))
    sns.heatmap(
        matrix, annot=True, fmt="d", cmap="Blues",
        xticklabels=RISK_CATEGORIES, yticklabels=RISK_CATEGORIES,
    )
    plt.xlabel("Predicted category")
    plt.ylabel("Human category")
    plt.title("Risk classification confusion matrix")
    plt.tight_layout()
    plt.savefig(output_dir / "confusion_matrix.png", dpi=160)
    plt.close()
    return metrics
