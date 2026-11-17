"""Create a static layout preview; the final deliverable remains a Power BI file."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns


DATA = Path("data/processed/dashboard_events.csv")
OUTPUT = Path("reports/dashboard_layout_preview.png")


def main() -> None:
    frame = pd.read_csv(DATA, parse_dates=["event_date"])
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")
    figure = plt.figure(figsize=(16, 10), constrained_layout=True)
    grid = figure.add_gridspec(3, 4)

    figure.suptitle(
        "Enterprise Risk Intelligence — Layout Preview (build final version in Power BI)",
        fontsize=18,
        fontweight="bold",
    )

    top = frame.nlargest(8, "risk_score").sort_values("risk_score")
    ax1 = figure.add_subplot(grid[:2, :2])
    ax1.barh(top["headline"].str.slice(0, 58), top["risk_score"], color="#315b7d")
    ax1.set_title("Top risk events")
    ax1.set_xlabel("Risk score (20–100)")
    ax1.set_ylabel("")

    category = frame.groupby("risk_category")["event_id"].nunique().sort_values()
    ax2 = figure.add_subplot(grid[0, 2:])
    ax2.barh(category.index, category.values, color="#5e8c6a")
    ax2.set_title("Risk category distribution")
    ax2.set_xlabel("Distinct events")
    ax2.set_ylabel("")

    weekly = frame.set_index("event_date").resample("W")["risk_score"].mean()
    ax3 = figure.add_subplot(grid[1, 2:])
    ax3.plot(weekly.index, weekly.values, marker="o", color="#a65f46")
    ax3.set_title("Average risk score over time")
    ax3.set_ylabel("Average score")
    ax3.tick_params(axis="x", rotation=25)

    sectors = (
        frame.assign(sector=frame["affected_sectors"].fillna("Cross-sector").str.split("; "))
        .explode("sector").groupby("sector")["event_id"].nunique().nlargest(8).sort_values()
    )
    ax4 = figure.add_subplot(grid[2, :2])
    ax4.barh(sectors.index, sectors.values, color="#8066a8")
    ax4.set_title("Sector exposure")
    ax4.set_xlabel("Distinct events")
    ax4.set_ylabel("")

    severity = frame["severity"].value_counts().sort_index()
    ax5 = figure.add_subplot(grid[2, 2:])
    ax5.bar(severity.index.astype(str), severity.values, color="#bd8b3f")
    ax5.set_title("Severity distribution")
    ax5.set_xlabel("Severity (1–5)")
    ax5.set_ylabel("Events")

    figure.savefig(OUTPUT, dpi=170, bbox_inches="tight")


if __name__ == "__main__":
    main()
