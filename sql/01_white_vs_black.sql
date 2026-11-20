-- White vs Black win rate: overall and by rating band
SELECT 'All ratings' AS rating_band,
       COUNT(*) AS games,
       ROUND(100.0 * SUM(winner = 'white') / COUNT(*), 2) AS white_win_pct,
       ROUND(100.0 * SUM(winner = 'black') / COUNT(*), 2) AS black_win_pct,
       ROUND(100.0 * SUM(winner = 'draw')  / COUNT(*), 2) AS draw_pct
FROM games
UNION ALL
SELECT rating_band,
       COUNT(*),
       ROUND(100.0 * SUM(winner = 'white') / COUNT(*), 2),
       ROUND(100.0 * SUM(winner = 'black') / COUNT(*), 2),
       ROUND(100.0 * SUM(winner = 'draw')  / COUNT(*), 2)
FROM games
GROUP BY rating_band;
