import pandas as pd

df = pd.read_csv("data/games.csv")

print("SHAPE (rows, columns):", df.shape)

print("\nCOLUMN TYPES:")
print(df.dtypes)

print("\nMISSING VALUES PER COLUMN:")
print(df.isna().sum())

print("\nFULLY IDENTICAL ROWS:", df.duplicated().sum())
print("DUPLICATE GAME IDs:", df["id"].duplicated().sum())

print("\nWINNER:")
print(df["winner"].value_counts())

print("\nVICTORY STATUS:")
print(df["victory_status"].value_counts())

print("\nNUMERIC SUMMARY:")
print(df[["turns", "white_rating", "black_rating", "opening_ply"]].describe())

print("\nUNIQUE OPENING NAMES:", df["opening_name"].nunique())
