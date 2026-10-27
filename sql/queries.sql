-- Uptime за последние 24 часа
SELECT t.name,
       ROUND(100.0 * AVG(c.is_up::int), 2) AS uptime_pct
FROM checks c
JOIN targets t ON t.id = c.target_id
WHERE c.checked_at > now() - interval '24 hours'
GROUP BY t.name
ORDER BY t.name;

-- Среднее время ответа по минутам (для графика)
SELECT date_trunc('minute', c.checked_at) AS time,
       t.name AS metric,
       AVG(c.response_ms) AS value
FROM checks c
JOIN targets t ON t.id = c.target_id
WHERE c.checked_at > now() - interval '6 hours'
GROUP BY 1, 2
ORDER BY 1;

-- Последние сбои
SELECT c.checked_at, t.name, c.status_code, c.error
FROM checks c
JOIN targets t ON t.id = c.target_id
WHERE NOT c.is_up
ORDER BY c.checked_at DESC
LIMIT 20;