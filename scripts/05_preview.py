import sqlite3
import pandas as pd

pd.set_option("display.width", 200)

print("HOW GAMES END BY BAND (all rows)")
print(pd.read_csv("outputs/03_how_games_end_by_band.csv").to_string(index=False))

con = sqlite3.connect("data/chess.db")
g = pd.read_sql_query("SELECT rating_band, winner, white_expected FROM games", con)
con.close()
g["score"] = g["winner"].map({"white": 1.0, "draw": 0.5, "black": 0.0})
g["diff"] = g["score"] - g["white_expected"]
print("\nBASELINE: White over expected, ALL games (points):", round(100 * g["diff"].mean(), 2))
print(round(100 * g.groupby("rating_band")["diff"].mean(), 2).to_string())

f = pd.read_csv("outputs/07_family_adjusted.csv")
f = f[f["games"] >= 150]
for band in f["rating_band"].unique():
    d = f[f["rating_band"] == band].sort_values("white_over_expected", ascending=False)
    print("\n" + "=" * 70)
    print(band, "- families with 150+ games:", len(d))
    if len(d) <= 8:
        print(d.to_string(index=False))
    else:
        print(d.head(4).to_string(index=False))
        print("   ...")
        print(d.tail(4).to_string(index=False))
