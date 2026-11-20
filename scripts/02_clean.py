import pandas as pd

df = pd.read_csv("data/games.csv")
rows_start = len(df)
print("Rows at start:", rows_start)

# Check for duplicates
print("Exact duplicate rows:", df.duplicated().sum())
print("Repeated game IDs:", df["id"].duplicated().sum())

repeats = df[df.duplicated("id", keep=False)].drop_duplicates()
differs = {col: int((repeats.groupby("id")[col].nunique() > 1).sum()) for col in df.columns}
print("\nColumns that differ between copies of the same ID (number of IDs affected):")
print({k: v for k, v in differs.items() if v > 0})

# Remove duplicates
df = df.drop_duplicates(subset="id", keep="first").copy()
print("\nRows after removing duplicate IDs:", len(df), "| removed:", rows_start - len(df))

# Tidy text columns
for col in ["winner", "victory_status", "opening_name", "opening_eco"]:
    df[col] = df[col].str.strip()
df["winner"] = df["winner"].str.lower()
df["victory_status"] = df["victory_status"].str.lower()

df["avg_rating"] = (df["white_rating"] + df["black_rating"]) / 2

bins = [0, 1200, 1600, 2000, float("inf")]
labels = ["Under 1200", "1200-1599", "1600-1999", "2000+"]
df["rating_band"] = pd.cut(df["avg_rating"], bins=bins, labels=labels, right=False).astype(str)

df["opening_family"] = (
    df["opening_name"]
    .str.split(":").str[0]
    .str.split("|").str[0]
    .str.replace(r"\s*#\d+$", "", regex=True)
    .str.strip()
)

keep = ["id", "rated", "turns", "victory_status", "winner", "increment_code",
        "white_id", "white_rating", "black_id", "black_rating",
        "avg_rating", "rating_band", "opening_eco", "opening_name",
        "opening_family", "opening_ply"]
df = df[keep]

print("\nWINNER (after cleaning):")
print(df["winner"].value_counts())
print("\nVICTORY STATUS vs WINNER:")
print(pd.crosstab(df["victory_status"], df["winner"]))
print("\nGAMES PER RATING BAND:")
print(df["rating_band"].value_counts())
print("\nDistinct full opening names:", df["opening_name"].nunique())
print("Distinct opening families:", df["opening_family"].nunique())
print("Top 5 families by games:")
print(df["opening_family"].value_counts().head(5))
print("\nGames with 5 turns or fewer:", (df["turns"] <= 5).sum())

# Save
df.to_csv("data/games_clean.csv", index=False)
print("\nSaved data/games_clean.csv with", len(df), "rows and", len(df.columns), "columns")
