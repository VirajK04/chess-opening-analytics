-- How games end, classified by OUTCOME first so every draw is a draw
WITH g AS (
  SELECT *,
         CASE WHEN winner = 'draw'            THEN 'Draw'
              WHEN victory_status = 'mate'      THEN 'Checkmate'
              WHEN victory_status = 'resign'    THEN 'Resignation'
              WHEN victory_status = 'outoftime' THEN 'Out of time'
         END AS ending
  FROM games
)
SELECT ending,
       COUNT(*) AS games,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM games), 2) AS pct_of_games
FROM g
GROUP BY ending
ORDER BY games DESC;
