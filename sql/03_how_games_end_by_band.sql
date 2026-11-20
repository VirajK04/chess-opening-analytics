-- How games end within each rating band (percentages add to 100 per band)
WITH g AS (
  SELECT *,
         CASE WHEN winner = 'draw'            THEN 'Draw'
              WHEN victory_status = 'mate'      THEN 'Checkmate'
              WHEN victory_status = 'resign'    THEN 'Resignation'
              WHEN victory_status = 'outoftime' THEN 'Out of time'
         END AS ending
  FROM games
)
SELECT rating_band,
       ending,
       COUNT(*) AS games,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY rating_band), 2) AS pct_within_band
FROM g
GROUP BY rating_band, ending
ORDER BY rating_band, games DESC;
