# Interview guide

## 90-second explanation

I built an enterprise risk and market intelligence platform to solve a common
analyst problem: important information is spread across financial, regulatory,
and technology sources, and manually reviewing every event is slow and
inconsistent.

My Python pipeline collects structured events from official RSS feeds and the
NIST vulnerability API. I used Pandas to standardize dates and text, handle
missing descriptions, remove duplicates, and create stable event IDs. I then
loaded the cleaned data into a normalized SQLite database with separate event,
risk-analysis, sector, and junction tables.

The AI layer returns a primary risk category, affected sectors, a concise risk
explanation, and three scoring components. I compute the final score using a
transparent weighted formula based on severity, breadth, and urgency, while
keeping model confidence separate. I also created 25 human-labelled events and
compare predictions using accuracy, class-level metrics, and a confusion matrix.

Finally, SQL joins and aggregations produce the dataset for a Power BI dashboard
showing top risks, category trends, sector exposure, and severity distribution.
The key design choice was keeping every stage explainable and reproducible
rather than presenting the model as a black box.

## Draft resume bullets — use only after final LLM and PBIX runs

- Built a Python, SQLite, and LLM pipeline that cleaned and organized financial,
  regulatory, and technology events into five enterprise-risk categories with
  structured sector and analyst-attention outputs.
- Designed an explainable 20–100 risk score, evaluated classification against
  25 manually labelled events, and created a Power BI dashboard highlighting
  priority events, sector exposure, and risk trends.

Replace the evaluation wording with the final measured result. Do not report
the 32% rule-based baseline as LLM performance.

## Fifteen interview questions

1. What business decision does the platform support?
2. Why did you choose these five risk categories?
3. How do you decide the primary category when an event spans several risks?
4. Why did you weight severity more heavily than breadth and urgency?
5. Why is confidence excluded from the risk score?
6. How do you handle missing descriptions and invalid dates?
7. How does your duplicate-detection logic work?
8. Why did you choose SQLite instead of storing everything in CSV files?
9. Why is `event_sectors` a junction table?
10. Which SQL queries directly support the dashboard?
11. How did you make LLM output reproducible and machine-readable?
12. How did you evaluate the classifier without fabricating accuracy?
13. What did the confusion matrix reveal about category ambiguity?
14. What are the most important limitations of your dataset and score?
15. What would you add before using the platform in a real bank?

## Short answer triggers

- **Input:** raw JSON or RSS events.
- **Processing:** clean, standardize, classify, score, store, join, and aggregate.
- **Output:** database records, evaluation metrics, dashboard dataset, and analyst insights.
- **Main limitation:** the score prioritizes attention; it is not expected loss.
- **Production extension:** human-review queue, model monitoring, access controls,
  source licensing review, and a larger time-based validation set.
