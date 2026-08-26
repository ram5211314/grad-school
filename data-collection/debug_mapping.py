"""Debug province/level mapping using actual column names."""
import sqlite3

db_path = 'data-collection/runs/CPEER.db'
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cursor = conn.cursor()

# Get column names
cursor.execute("PRAGMA table_info(Universities)")
uni_cols = [c[1] for c in cursor.fetchall()]
print("University columns:", uni_cols)

cursor.execute("PRAGMA table_info(Users)")
user_cols = [c[1] for c in cursor.fetchall()]
print("User columns:", user_cols)

# Get unique university names from Users
cursor.execute(f"SELECT DISTINCT {uni_cols[1]} FROM Users")
user_unis = [r[0] for r in cursor.fetchall()]

# Get university info
cursor.execute(f"SELECT {uni_cols[1]}, {uni_cols[2]}, {uni_cols[3]} FROM Universities")
uni_info = {}
for r in cursor.fetchall():
    uni_info[r[0]] = (r[1], r[2])

print(f"\nUser table universities ({len(user_unis)}):")
for u in sorted(user_unis):
    info = uni_info.get(u, ('???', '???'))
    matched = u in uni_info
    print(f"  {u} -> province={info[0]}, level={info[1]}, matched={matched}")

print(f"\nUniversities table names ({len(uni_info)}):")
for u in sorted(uni_info.keys()):
    print(f"  {u}")

conn.close()
