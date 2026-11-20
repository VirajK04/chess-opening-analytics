-- Average game length overall, by rating band, and by how the game ended
WITH g AS (
  SELECT *,
         CASE WHEN winner = 'draw'            THEN 'Draw'
              WHEN victory_status = 'mate'      THEN 'Checkmate'
              WHEN victory_status = 'resign'    THEN 'Resignation'
              WHEN victory_status = 'outoftime' THEN 'Out of time'
         END AS ending
  FROM games
)
SELECT 'All games' AS group_type, 'All' AS category,
       COUNT(*) AS games,
       ROUND(AVG(turns), 1) AS avg_plies,
       ROUND(AVG(turns) / 2.0, 1) AS avg_full_moves
FROM g
UNION ALL
SELECT 'Rating band', rating_band, COUNT(*), ROUND(AVG(turns), 1), ROUND(AVG(turns) / 2.0, 1)
FROM g GROUP BY rating_band
UNION ALL
SELECT 'Ending', ending, COUNT(*), ROUND(AVG(turns), 1), ROUND(AVG(turns) / 2.0, 1)
FROM g GROUP BY ending;
