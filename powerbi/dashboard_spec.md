# Power BI dashboard build specification

## Data source

Import `data/processed/dashboard_events.csv`. This file is created by a SQL
query against the SQLite `dashboard_events` view; Power BI is therefore the
presentation layer, not a second data-cleaning pipeline.

## Page: Enterprise Risk Overview

### Slicers

- `event_date` — between/date-range slicer
- `risk_category` — dropdown
- `affected_sectors` — dropdown
- `source` — dropdown

### Visuals and business questions

1. **Top Risk Events — table**
   - Columns: date, headline, category, score, sectors, analyst focus
   - Sort: risk score descending
   - Question: What should an analyst review first?

2. **Risk Category Distribution — horizontal bar chart**
   - Axis: category
   - Value: distinct count of event ID
   - Question: Where is current risk concentrated?

3. **Risk Trend Over Time — line chart**
   - X: date by week
   - Y: average risk score
   - Legend: risk category
   - Question: Is risk intensity rising or falling?

4. **Sector Exposure — horizontal bar chart**
   - Axis: affected sectors
   - Value: distinct count of event ID
   - Question: Which sectors appear most exposed?

5. **Severity Distribution — column chart**
   - X: severity (1–5)
   - Y: distinct count of event ID
   - Question: Is the event set dominated by low- or high-severity items?

### Measures

```DAX
Event Count = DISTINCTCOUNT(dashboard_events[event_id])

Average Risk Score = AVERAGE(dashboard_events[risk_score])

High Risk Events =
CALCULATE(
    DISTINCTCOUNT(dashboard_events[event_id]),
    dashboard_events[risk_score] >= 70
)

High Risk Share = DIVIDE([High Risk Events], [Event Count])
```

## Design rules

- Use one page only.
- Use category colors consistently across charts.
- Do not use a pie chart: five categories are easier to compare in bars.
- Keep headlines in a table; do not truncate the main business evidence into cards.
- Add a subtitle stating the data window and analysis method.
