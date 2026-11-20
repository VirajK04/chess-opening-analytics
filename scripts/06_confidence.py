import sqlite3
import numpy as np
import pandas as pd

pd.set_option("display.width", 200)

con = sqlite3.connect("data/chess.db")
g = pd.read_sql_query(
    "SELECT rating_band, opening_family, winner, white_expected FROM games", con)
con.close()

# Per game: White's actual score minus the score the ratings predicted
g["diff"] = g["winner"].map({"white": 1.0, "draw": 0.5, "black": 0.0}) - g["white_expected"]

rows = []
scopes = [("All ratings", g)] + [(b, g[g["rating_band"] == b]) for b in sorted(g["rating_band"].unique())]
for scope, sub in scopes:
    baseline = sub["diff"].mean()   # White's normal edge in this scope
    for fam, d in sub.groupby("opening_family"):
        n = len(d)
        if n < 150:
            continue
        gap = d["diff"].mean() - baseline
        se = d["diff"].std(ddof=1) / np.sqrt(n)
        rows.append({"rating_band": scope, "opening_family": fam, "games": n,
                     "vs_baseline_pts": round(100 * gap, 2),
                     "ci_low": round(100 * (gap - 1.96 * se), 2),
                     "ci_high": round(100 * (gap + 1.96 * se), 2)})

res = pd.DataFrame(rows)
res["clear_signal"] = (res["ci_low"] > 0) | (res["ci_high"] < 0)
res.to_csv("outputs/09_family_confidence.csv", index=False)

print("Families tested (150+ games) and how many show a clear signal:")
print(res.groupby("rating_band")["clear_signal"].agg(["count", "sum"]).to_string())
print("\nClear signals only (interval excludes zero):")
print(res[res["clear_signal"]].sort_values(["rating_band", "vs_baseline_pts"]).to_string(index=False))
print("\nSpot check:")
print(res[res["opening_family"].isin(["English Opening", "Van't Kruijs Opening"])].to_string(index=False))
