-- 1. Highest-priority events for analyst review
SELECT event_date, headline, risk_category, risk_score, affected_sectors
FROM dashboard_events
ORDER BY risk_score DESC, event_date DESC
LIMIT 10;

-- 2. Risk distribution by category
SELECT risk_category, COUNT(*) AS event_count, ROUND(AVG(risk_score), 1) AS average_score
FROM risk_analysis
GROUP BY risk_category
ORDER BY event_count DESC;

-- 3. Weekly risk trend
SELECT strftime('%Y-%W', e.event_date) AS year_week,
       COUNT(*) AS event_count,
       ROUND(AVG(r.risk_score), 1) AS average_score
FROM events e
JOIN risk_analysis r ON e.event_id = r.event_id
GROUP BY year_week
ORDER BY year_week;

-- 4. Sector exposure using the many-to-many junction table
SELECT s.sector_name,
       COUNT(DISTINCT es.event_id) AS affected_events,
       ROUND(AVG(r.risk_score), 1) AS average_score
FROM sectors s
JOIN event_sectors es ON s.sector_id = es.sector_id
JOIN risk_analysis r ON es.event_id = r.event_id
GROUP BY s.sector_name
ORDER BY affected_events DESC, average_score DESC;

-- 5. High-risk, lower-confidence cases requiring human review
SELECT e.event_date, e.headline, r.risk_category, r.risk_score, r.confidence
FROM events e
JOIN risk_analysis r ON e.event_id = r.event_id
WHERE r.risk_score >= 70 AND r.confidence <= 3
ORDER BY r.risk_score DESC;
