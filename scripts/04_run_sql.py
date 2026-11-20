import glob
import os
import sqlite3
import pandas as pd

con = sqlite3.connect("data/chess.db")

for path in sorted(glob.glob("sql/*.sql")):
    name = os.path.splitext(os.path.basename(path))[0]
    with open(path) as f:
        query = f.read()
    df = pd.read_sql_query(query, con)
    df.to_csv(f"outputs/{name}.csv", index=False)

    print("=" * 80)
    print(name, "->", len(df), "rows, saved to outputs/" + name + ".csv")
    print(df.head(12).to_string(index=False))
    if "rating_band" in df.columns and "opening_family" in df.columns:
        print("\nQualifying rows (50+ games) per rating band:")
        print(df["rating_band"].value_counts().to_string())

con.close()
