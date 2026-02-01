import camelot
import pandas as pd

tables = camelot.read_pdf(
    "data\\mietspiegel_tables\\2024.pdf", pages="all", flavor="stream"
)

print("Tables found:", tables.n)

# combining into one DataFrame
df_list = [table.df for table in tables]
df = pd.concat(df_list, ignore_index=True)

df.to_csv("2024converted.csv", index=False, encoding="utf-8")
