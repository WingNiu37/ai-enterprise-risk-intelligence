# Data dictionary

## `events`

| Field | Type | Meaning |
|---|---|---|
| `event_id` | TEXT | Stable SHA-256 identifier derived from date, source, and headline |
| `event_date` | DATE | Publication date in ISO `YYYY-MM-DD` format |
| `headline` | TEXT | Event title |
| `source` | TEXT | Publishing organization |
| `description` | TEXT | Short source-provided description |
| `url` | TEXT | Link to the source item |
| `source_type` | TEXT | `rss`, `alpha_vantage`, or `sample` |
| `collected_at` | TIMESTAMP | UTC collection time |

## `risk_analysis`

| Field | Type | Meaning |
|---|---|---|
| `event_id` | TEXT | Foreign key to `events` |
| `risk_category` | TEXT | Exactly one of the five approved risk classes |
| `severity` | INTEGER | Consequence magnitude from 1 to 5 |
| `breadth` | INTEGER | Scope across organizations, sectors, or markets from 1 to 5 |
| `urgency` | INTEGER | Speed of required analyst attention from 1 to 5 |
| `confidence` | INTEGER | Model confidence from 1 to 5; not included in the risk score |
| `risk_score` | INTEGER | `20 × (0.5 × severity + 0.3 × breadth + 0.2 × urgency)` |
| `ai_summary` | TEXT | Concise explanation of the transmission channel |
| `analyst_focus` | TEXT | Indicator or development an analyst should monitor |
| `analysis_method` | TEXT | Model or fallback method that generated the record |
| `analyzed_at` | TIMESTAMP | UTC analysis time |

## `sectors` and `event_sectors`

`sectors` is the controlled sector lookup table. `event_sectors` is a
many-to-many junction table because one event can affect several sectors.
