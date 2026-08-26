"""Extract CS-related data from CPEER database and save as JSON."""
import sqlite3, json, sys
from collections import defaultdict

db_path = 'data-collection/runs/CPEER.db'
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cursor = conn.cursor()

cursor.execute("SELECT * FROM Users")
rows = cursor.fetchall()
cursor.execute("PRAGMA table_info(Users)")
columns = [c[1] for c in cursor.fetchall()]

cursor.execute("SELECT * FROM Universities")
uni_rows = cursor.fetchall()
cursor.execute("PRAGMA table_info(Universities)")
uni_columns = [c[1] for c in cursor.fetchall()]

universities = {}
for row in uni_rows:
    uni = dict(zip(uni_columns, row))
    universities[uni.get('\u9662\u6821', '')] = uni

cs_keywords = ['\u8ba1\u7b97\u673a', '\u8f6f\u4ef6', '\u7f51\u7edc', '\u4fe1\u606f', '\u4eba\u5de5\u667a\u80fd', '\u6570\u636e', '\u5927\u6570\u636e', '\u4fe1\u606f\u5b89\u5168', '\u7f51\u7edc\u5b89\u5168']
all_records = []
cs_records = []

for row in rows:
    record = dict(zip(columns, row))
    major = record.get('\u4e13\u4e1a', '') or ''
    dept = record.get('\u9662\u7cfb', '') or ''
    is_cs = any(kw in major for kw in cs_keywords) or any(kw in dept for kw in cs_keywords)
    record['is_cs'] = is_cs
    all_records.append(record)
    if is_cs:
        cs_records.append(record)

print(f"Total records: {len(all_records)}", file=sys.stderr)
print(f"CS-related records: {len(cs_records)}", file=sys.stderr)

summary = defaultdict(lambda: defaultdict(list))
for r in cs_records:
    uni = r.get('\u9662\u6821', '')
    major = r.get('\u4e13\u4e1a', '')
    summary[uni][major].append(r)

print(f"\nCS universities: {len(summary)}", file=sys.stderr)
for uni, majors in sorted(summary.items(), key=lambda x: -sum(len(v) for v in x[1].values())):
    total = sum(len(v) for v in majors.values())
    major_list = ', '.join(f"{m}({len(v)})" for m, v in majors.items())
    print(f"  {uni}: {total} records - {major_list}", file=sys.stderr)

output = {
    'total_records': len(all_records),
    'cs_records': len(cs_records),
    'universities_count': len(summary),
    'records': cs_records,
}

with open('data-collection/runs/cpeer_cs_data.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, ensure_ascii=False, indent=2)
print(f"\nSaved to data-collection/runs/cpeer_cs_data.json", file=sys.stderr)

conn.close()
