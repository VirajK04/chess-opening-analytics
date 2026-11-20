-- White's actual score vs the score its rating edge predicts, by opening family (min 50 games)
-- white_over_expected > 0 means White did better than the ratings predicted
WITH g AS (
  SELECT *, CASE winner WHEN 'white' THEN 1.0 WHEN 'draw' THEN 0.5 ELSE 0.0 END AS white_score
  FROM games
)
SELECT 'All ratings' AS rating_band, opening_family,
       COUNT(*) AS games,
       ROUND(100.0 * AVG(white_score), 2) AS white_score_pct,
       ROUND(100.0 * AVG(white_expected), 2) AS expected_pct,
       ROUND(100.0 * (AVG(white_score) - AVG(white_expected)), 2) AS white_over_expected
FROM g GROUP BY opening_family HAVING COUNT(*) >= 50
UNION ALL
SELECT rating_band, opening_family,
       COUNT(*),
       ROUND(100.0 * AVG(white_score), 2),
       ROUND(100.0 * AVG(white_expected), 2),
       ROUND(100.0 * (AVG(white_score) - AVG(white_expected)), 2)
FROM g GROUP BY rating_band, opening_family HAVING COUNT(*) >= 50
ORDER BY rating_band, games DESC;
