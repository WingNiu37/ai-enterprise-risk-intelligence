import sqlite3
from pathlib import Path


QUERIES = {
    "category_summary": """
        SELECT risk_category, COUNT(*) AS events, ROUND(AVG(risk_score), 1) AS average_score
        FROM risk_analysis GROUP BY risk_category ORDER BY events DESC
    """,
    "top_risks": """
        SELECT event_date, headline, risk_category, risk_score
        FROM dashboard_events ORDER BY risk_score DESC, event_date DESC LIMIT 10
    """,
    "sector_exposure": """
        SELECT s.sector_name, COUNT(DISTINCT es.event_id) AS affected_events
        FROM sectors s
        JOIN event_sectors es ON s.sector_id = es.sector_id
        GROUP BY s.sector_name ORDER BY affected_events DESC
    """,
}


if __name__ == "__main__":
    with sqlite3.connect(Path("database/risk_intelligence.db")) as connection:
        for name, query in QUERIES.items():
            print(f"\n{name}")
            columns = [item[0] for item in connection.execute(query).description]
            print(" | ".join(columns))
            for row in connection.execute(query):
                print(" | ".join(map(str, row)))
