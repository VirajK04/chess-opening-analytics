import sqlite3
import pandas as pd

df = pd.read_csv("data/games_clean.csv")

# Elo expected score for White: 0.5 when ratings are equal, ~0.91 when White is 400 points higher
df["white_expected"] = 1 / (1 + 10 ** ((df["black_rating"] - df["white_rating"]) / 400))

con = sqlite3.connect("data/chess.db")
df.to_sql("games", con, if_exists="replace", index=False)

print("Rows in games table:", con.execute("SELECT COUNT(*) FROM games").fetchone()[0])
con.close()
