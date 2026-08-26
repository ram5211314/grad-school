"""Aggregate CPEER exam records into Program-level records and generate import CSV."""
import sqlite3, csv, json, sys
from collections import defaultdict

db_path = 'data-collection/runs/CPEER.db'
conn = sqlite3.connect(db_path)
conn.text_factory = lambda b: b.decode('utf-8', errors='replace')
cursor = conn.cursor()

# Load university info
cursor.execute("SELECT * FROM Universities")
uni_rows = cursor.fetchall()
cursor.execute("PRAGMA table_info(Universities)")
uni_cols = [c[1] for c in cursor.fetchall()]

uni_info = {}
for row in uni_rows:
    u = dict(zip(uni_cols, row))
    uni_info[u.get('\u9662\u6821', '')] = u

# Load exam records
cursor.execute("SELECT * FROM Users")
rows = cursor.fetchall()
cursor.execute("PRAGMA table_info(Users)")
user_cols = [c[1] for c in cursor.fetchall()]

# Map major names to codes
MAJOR_CODE_MAP = {
    '\u8ba1\u7b97\u673a\u79d1\u5b66\u4e0e\u6280\u672f': '081200',
    '\u8ba1\u7b97\u673a\u7cfb\u7edf\u7ed3\u6784': '081201',
    '\u8ba1\u7b97\u673a\u8f6f\u4ef6\u4e0e\u7406\u8bba': '081202',
    '\u8ba1\u7b97\u673a\u5e94\u7528\u6280\u672f': '081203',
    '\u8f6f\u4ef6\u5de5\u7a0b': '083500',
    '\u7f51\u7edc\u7a7a\u95f4\u5b89\u5168': '083900',
    '\u7535\u5b50\u4fe1\u606f': '085400',
    '\u4eba\u5de5\u667a\u80fd': '081104',
    '\u6570\u636e\u79d1\u5b66\u4e0e\u5de5\u7a0b': '0812J1',
    '\u8f6f\u4ef6\u5de5\u7a0b': '083500',
    '\u8ba1\u7b97\u673a\u6280\u672f': '085400',
    '\u7f51\u7edc\u7a7a\u95f4\u5b89\u5168': '083900',
    '\u4fe1\u606f\u4e0e\u901a\u4fe1\u5de5\u7a0b': '081000',
    '\u63a7\u5236\u79d1\u5b66\u4e0e\u5de5\u7a0b': '081100',
    '\u8f6f\u4ef6\u5de5\u7a0b\uff08\u4e13\u7801\uff09': '085400',
}

# Deduplicate: aggregate by university + major + year
programs = defaultdict(lambda: {
    'scores': [], 'admitted': 0, 'total': 0,
    'dept': '', 'uni': '', 'major': '', 'year': 0
})

for row in rows:
    r = dict(zip(user_cols, row))
    uni = r.get('\u9662\u6821', '')
    year = r.get('\u5e74\u4efd', 0)
    dept = r.get('\u9662\u7cfb', '')
    major = r.get('\u4e13\u4e1a', '')
    score = r.get('\u521d\u8bd5\u6210\u7ee9', None)
    admitted = r.get('\u662f\u5426\u5f55\u53d6', '')
    
    # Normalize major name (remove research direction suffixes)
    base_major = major.split('\uff08')[0].split('(')[0].strip()
    if base_major.startswith('08'):
        # Already has code prefix
        parts = base_major.split('-', 1)
        if len(parts) > 1:
            base_major = parts[1].strip()
    
    key = (uni, base_major, year)
    prog = programs[key]
    prog['uni'] = uni
    prog['major'] = base_major
    prog['year'] = year
    prog['dept'] = dept
    prog['total'] += 1
    if admitted == '\u662f':
        prog['admitted'] += 1
    if score is not None and score > 0:
        prog['scores'].append(score)

# Generate CSV
csv_rows = []
for (uni, major, year), prog in sorted(programs.items(), key=lambda x: (x[0][2], x[0][0])):
    scores = prog['scores']
    admitted_count = prog['admitted']
    total_count = prog['total']
    
    # Derive reexamination line (min score of admitted students as proxy)
    reex_line = None
    
    # Map major code
    major_code = MAJOR_CODE_MAP.get(major, '')
    if not major_code:
        # Try to find partial match
        for name, code in MAJOR_CODE_MAP.items():
            if name in major or major in name:
                major_code = code
                break
    if not major_code:
        major_code = '085400'  # default to electronic info
    
    # Get province
    uni_data = uni_info.get(uni, {})
    province = uni_data.get('\u6240\u5728\u7701', '\u672a\u77e5')
    
    # University level
    level = uni_data.get('\u9662\u6821\u5c42\u6b21', '')
    if level == 985:
        level = '985'
    elif level == 211:
        level = '211'
    else:
        level = str(level) if level else '\u666e\u901a'
    
    # Determine degree type from dept/major
    degree_type = '\u5b66\u4e66\u5b66\u4f4d' if '\u5b66\u672f' in prog['dept'] or '\u5b66\u7855' in major else '\u4e13\u4e1a\u5b66\u4f4d'
    
    # Exam subjects (not available in CPEER, mark as unknown)
    exam_subjects = '\u672a\u516c\u5f00'
    
    # Source
    source_name = 'CPEER\u6570\u636e\u96c6(\u8003\u7814\u771f\u5b9e\u5f55\u53d6)'
    source_url = 'https://github.com/Younai2021/CPEER-Dataset'
    
    csv_row = [
        uni,                    # universityName
        province,               # province
        major_code,             # majorCode
        major,                  # majorName
        degree_type,            # degreeType
        'FULL_TIME',            # studyMode
        exam_subjects,          # examSubjects
        '',                     # reexaminationLine (not available at program level)
        admitted_count,         # actualEnrollment
        total_count,            # registrationCount
        year,                   # admissionYear
        level,                  # universityLevel
        '',                     # plannedEnrollment
        '',                     # nationalLine
        source_name,            # sourceName
        source_url,             # sourceUrl
        year,                   # sourceYear
        f'\u6570\u636e\u6765\u6e90\u4e8eCPEER\u5f00\u653e\u6570\u636e\u96c6\uff0c\u5171{total_count}\u6761\u8003\u751f\u8bb0\u5f55\uff0c\u5176\u4e2d{admitted_count}\u4eba\u5f55\u53d6'  # remarks
    ]
    csv_rows.append(csv_row)

# Write CSV
out_path = 'data-collection/runs/cpeer_programs_import.csv'
header = [
    'universityName', 'province', 'majorCode', 'majorName', 'degreeType',
    'studyMode', 'examSubjects', 'reexaminationLine', 'actualEnrollment',
    'registrationCount', 'admissionYear', 'universityLevel', 'plannedEnrollment',
    'nationalLine', 'sourceName', 'sourceUrl', 'sourceYear', 'remarks'
]

with open(out_path, 'w', encoding='utf-8-sig', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(csv_rows)

print(f"Generated {len(csv_rows)} program records to {out_path}", file=sys.stderr)

# Summary stats
years = defaultdict(int)
provinces = defaultdict(int)
levels = defaultdict(int)
for row in csv_rows:
    years[row[10]] += 1
    provinces[row[1]] += 1
    levels[row[11]] += 1

print(f"\nBy year:", file=sys.stderr)
for y in sorted(years.keys()):
    print(f"  {y}: {years[y]}", file=sys.stderr)

print(f"\nBy province:", file=sys.stderr)
for p in sorted(provinces.keys(), key=lambda x: -provinces[x])[:10]:
    print(f"  {p}: {provinces[p]}", file=sys.stderr)

print(f"\nBy level:", file=sys.stderr)
for l in sorted(levels.keys(), key=lambda x: -levels[x]):
    print(f"  {l}: {levels[l]}", file=sys.stderr)

conn.close()
