-- Opening FAMILY win rates, overall and by rating band, minimum 50 games
SELECT 'All ratings' AS rating_band,
       opening_family,
       COUNT(*) AS games,
       ROUND(100.0 * SUM(winner = 'white') / COUNT(*), 2) AS white_win_pct,
       ROUND(100.0 * SUM(winner = 'black') / COUNT(*), 2) AS black_win_pct,
       ROUND(100.0 * SUM(winner = 'draw')  / COUNT(*), 2) AS draw_pct,
       ROUND(AVG(white_rating - black_rating), 1) AS avg_white_rating_edge
FROM games
GROUP BY opening_family
HAVING COUNT(*) >= 50
UNION ALL
SELECT rating_band,
       opening_family,
       COUNT(*),
       ROUND(100.0 * SUM(winner = 'white') / COUNT(*), 2),
       ROUND(100.0 * SUM(winner = 'black') / COUNT(*), 2),
       ROUND(100.0 * SUM(winner = 'draw')  / COUNT(*), 2),
       ROUND(AVG(white_rating - black_rating), 1)
FROM games
GROUP BY rating_band, opening_family
HAVING COUNT(*) >= 50
ORDER BY rating_band, games DESC;
