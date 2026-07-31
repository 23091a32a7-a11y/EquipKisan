import sqlite3
import pandas as pd

df = pd.read_csv("Farm_Equipment_Sharing_Platform_Dataset.csv")

# Rename columns
df.columns = [
    "equipment_no",
    "equipment_name",
    "owner_name",
    "availability",
    "district",
    "phone",
    "rent"
]

conn = sqlite3.connect("database.db")

df.to_sql(
    "equipment",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("Data Loaded Successfully")