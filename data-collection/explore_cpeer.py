"""Explore CPEER database and extract CS-related data."""
import sqlite3, json, sys

db_path = 'data-collection/runs/CPEER.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print("Tables:", [t[0] for t in tables])

# For each table, show schema and sample data
for table_name in [t[0] for t in tables]:
    print(f"\n=== {table_name} ===")
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    print("Columns:", [(c[1], c[2]) for c in columns])
    
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    print(f"Row count: {count}")
    
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    rows = cursor.fetchall()
    col_names = [c[1] for c in columns]
    for row in rows:
        print(f"  {dict(zip(col_names, row))}")

conn.close()
