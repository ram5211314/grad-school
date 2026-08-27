"""
数据清洗脚本 - 合并 freecho + kaoyan.cn 数据
输出: cleaned_engineering_import.csv (平台18列格式)
"""
import csv
import re
import os
import sys
from collections import defaultdict

INPUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "runs")
FREECHO_FILE = os.path.join(INPUT_DIR, "freecho", "majors.csv")
KAOYAN_FILE = os.path.join(INPUT_DIR, "kaoyan_cs_data.csv")
OUTPUT_FILE = os.path.join(INPUT_DIR, "cleaned_engineering_import.csv")

PLATFORM_COLUMNS = [
    "universityName", "province", "majorCode", "majorName", "degreeType",
    "studyMode", "examSubjects", "reexaminationLine", "actualEnrollment",
    "registrationCount", "admissionYear", "universityLevel", "plannedEnrollment",
    "nationalLine", "sourceName", "sourceUrl", "sourceYear", "remarks"
]

UNI_LEVEL_MAP = {}
UNI_PROVINCE_FIX = {
    "中国矿业大学(北京)": "北京",
    "中国矿业大学": "江苏",
    "中国地质大学(北京)": "北京",
    "中国地质大学(武汉)": "湖北",
    "中国石油大学(北京)": "北京",
    "中国石油大学(华东)": "山东",
    "中国科学院大学": "北京",
    "中国政法大学": "北京",
    "华北电力大学": "北京",
    "华北电力大学(保定)": "河北",
    "东北电力大学": "吉林",
    "华东理工大学": "上海",
    "华东政法大学": "上海",
    "南京信息工程大学": "江苏",
    "成都理工大学": "四川",
    "宁波大学": "浙江",
}

MAJOR_NAME_MAP = {
    "计算机科学与技术": "计算机科学与技术",
    "计算机系统结构": "计算机系统结构",
    "计算机软件与理论": "计算机软件与理论",
    "计算机应用技术": "计算机应用技术",
    "软件工程": "软件工程",
    "网络空间安全": "网络空间安全",
    "计算机技术": "计算机技术",
    "人工智能": "人工智能",
    "大数据技术与工程": "大数据技术与工程",
    "网络与信息安全": "网络与信息安全",
    "软件工程(专硕)": "软件工程",
    "电子信息": "电子信息",
}


def normalize_university(name):
    name = name.strip()
    name = re.sub(r"[（(].*?[）)]", "", name) if name in UNI_PROVINCE_FIX else name
    return name


def normalize_major_name(name):
    name = name.strip()
    for key, val in MAJOR_NAME_MAP.items():
        if key in name:
            return val
    return name


def get_major_code(code):
    if not code:
        return ""
    code = code.strip()
    if len(code) >= 4:
        return code[:4]
    return code


def get_uni_level(name):
    return UNI_LEVEL_MAP.get(name, "普通")


def read_freecho():
    records = []
    if not os.path.exists(FREECHO_FILE):
        print(f"Freecho file not found: {FREECHO_FILE}")
        return records

    with open(FREECHO_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = get_major_code(row.get("专业代码", "") or row.get("majorCode", ""))
            if not code:
                continue

            uni = (row.get("学校名称", "") or row.get("universityName", "")).strip()
            prov = (row.get("省份", "") or row.get("province", "")).strip()
            if uni in UNI_PROVINCE_FIX:
                prov = UNI_PROVINCE_FIX[uni]

            records.append({
                "universityName": uni,
                "province": prov,
                "majorCode": row.get("专业代码", "") or row.get("majorCode", ""),
                "majorName": normalize_major_name(row.get("专业名称", "") or row.get("majorName", "")),
                "degreeType": row.get("学位类型", "") or row.get("degreeType", ""),
                "studyMode": (row.get("学习模式", "") or row.get("studyMode", "FULL_TIME")),
                "examSubjects": (row.get("考试科目1", "") or "") + " " + (row.get("考试科目2", "") or "") + " " + (row.get("考试科目3", "") or "") + " " + (row.get("考试科目4", "") or ""),
                "reexaminationLine": "",
                "actualEnrollment": "",
                "registrationCount": "",
                "admissionYear": "2025",
                "universityLevel": get_uni_level(uni),
                "plannedEnrollment": row.get("拟招生人数", "") or row.get("plannedEnrollment", ""),
                "nationalLine": "",
                "sourceName": "freecho/yzw",
                "sourceUrl": "https://github.com/freecho/yzw",
                "sourceYear": "2025",
                "remarks": f"研究方向: {row.get('研究方向', '') or row.get('researchDirection', '')} | 导师: {row.get('导师', '') or row.get('advisor', '')} | 院系: {row.get('院系', '') or row.get('department', '')}"
            })

    print(f"Freecho records loaded: {len(records)}")
    return records


def read_kaoyan():
    records = []
    if not os.path.exists(KAOYAN_FILE):
        print(f"Kaoyan file not found: {KAOYAN_FILE}")
        return records

    with open(KAOYAN_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            code = get_major_code(row.get("majorCode", ""))
            if not code:
                continue

            records.append({
                "universityName": row.get("universityName", "").strip(),
                "province": row.get("province", "").strip(),
                "majorCode": row.get("majorCode", ""),
                "majorName": normalize_major_name(row.get("majorName", "")),
                "degreeType": row.get("degreeType", ""),
                "studyMode": row.get("studyMode", "FULL_TIME"),
                "examSubjects": row.get("examSubjects", ""),
                "reexaminationLine": row.get("reexaminationLine", ""),
                "actualEnrollment": "",
                "registrationCount": "",
                "admissionYear": str(row.get("admissionYear", "2025")),
                "universityLevel": get_uni_level(row.get("universityName", "")),
                "plannedEnrollment": row.get("plannedEnrollment", ""),
                "nationalLine": "",
                "sourceName": "kaoyan.cn",
                "sourceUrl": row.get("sourceUrl", ""),
                "sourceYear": str(row.get("sourceYear", "2025")),
                "remarks": f"研究方向: {row.get('researchDirection', '')} | 院系: {row.get('department', '')}"
            })

    print(f"Kaoyan records loaded: {len(records)}")
    return records


def deduplicate(records):
    seen = set()
    unique = []
    for r in records:
        key = (
            r["universityName"],
            r["majorCode"],
            r["majorName"],
            r.get("remarks", "").split("|")[0].strip(),
            r["admissionYear"]
        )
        if key not in seen:
            seen.add(key)
            unique.append(r)
    return unique


def main():
    print("=" * 60)
    print("Data Cleaning Pipeline")
    print("=" * 60)

    freecho = read_freecho()
    kaoyan = read_kaoyan()

    all_records = freecho + kaoyan
    print(f"\nTotal before dedup: {len(all_records)}")

    unique = deduplicate(all_records)
    print(f"Total after dedup: {len(unique)}")

    unique.sort(key=lambda x: (x["universityName"], x["majorCode"], x["admissionYear"]))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=PLATFORM_COLUMNS)
        writer.writeheader()
        for r in unique:
            writer.writerow({k: r.get(k, "") for k in PLATFORM_COLUMNS})

    print(f"\nOutput: {OUTPUT_FILE}")
    f_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"File size: {f_size:.2f} MB")

    stats = defaultdict(int)
    for r in unique:
        stats["universities"] += 1
        code4 = r["majorCode"][:4] if r["majorCode"] else ""
        stats[f"major_{code4}"] += 1
        stats[f"year_{r['admissionYear']}"] += 1

    print(f"\nStats:")
    print(f"  Total records: {len(unique)}")
    print(f"  Unique universities: {len(set(r['universityName'] for r in unique))}")
    print(f"  By major code:")
    for k, v in sorted(stats.items()):
        if k.startswith("major_"):
            print(f"    {k.replace('major_', '')}: {v}")
    print(f"  By year:")
    for k, v in sorted(stats.items()):
        if k.startswith("year_"):
            print(f"    {k.replace('year_', '')}: {v}")


if __name__ == "__main__":
    main()
