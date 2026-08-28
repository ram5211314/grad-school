"""
数据清洗脚本 - 合并 freecho + kaoyan.cn 数据
智能合并：同（学校+专业+年份）取两个数据源的最优字段
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

UNI_PROVINCE_FIX = {
    "中国矿业大学(北京)": "北京",
    "中国矿业大学": "江苏",
    "中国地质大学(北京)": "北京",
    "中国地质大学(武汉)": "湖北",
    "中国石油大学(北京)": "北京",
    "中国石油大学(华东)": "山东",
    "中国科学院大学": "北京",
    "华北电力大学": "北京",
    "华北电力大学(保定)": "河北",
    "东北电力大学": "吉林",
    "华东理工大学": "上海",
    "华东政法大学": "上海",
    "南京信息工程大学": "江苏",
    "成都理工大学": "四川",
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
}


def normalize_university(name):
    return name.strip()


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

            exam_parts = []
            for i in range(1, 5):
                val = (row.get(f"考试科目{i}", "") or "").strip()
                if val:
                    exam_parts.append(val)
            exam_str = " | ".join(exam_parts) if exam_parts else ""

            records.append({
                "universityName": uni,
                "province": prov,
                "majorCode": row.get("专业代码", "") or row.get("majorCode", ""),
                "majorName": normalize_major_name(row.get("专业名称", "") or row.get("majorName", "")),
                "degreeType": row.get("学位类型", "") or row.get("degreeType", ""),
                "studyMode": (row.get("学习模式", "") or row.get("studyMode", "FULL_TIME")),
                "examSubjects": exam_str,
                "reexaminationLine": "",
                "actualEnrollment": "",
                "registrationCount": "",
                "admissionYear": "2025",
                "universityLevel": "",
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
                "universityLevel": "",
                "plannedEnrollment": row.get("plannedEnrollment", ""),
                "nationalLine": "",
                "sourceName": "kaoyan.cn",
                "sourceUrl": row.get("sourceUrl", ""),
                "sourceYear": str(row.get("sourceYear", "2025")),
                "remarks": f"研究方向: {row.get('researchDirection', '')} | 院系: {row.get('department', '')}"
            })

    print(f"Kaoyan records loaded: {len(records)}")
    return records


def merge_records(freecho_records, kaoyan_records):
    """智能合并：同（学校+专业代码+年份）的记录合并为一条，取各源最优字段"""
    groups = defaultdict(list)

    for r in freecho_records:
        key = (r["universityName"], r["majorCode"][:4], r["admissionYear"])
        groups[key].append(("freecho", r))

    for r in kaoyan_records:
        key = (r["universityName"], r["majorCode"][:4], r["admissionYear"])
        groups[key].append(("kaoyan", r))

    merged = []
    for key, sources in groups.items():
        if len(sources) == 1:
            source_name, record = sources[0]
            record["sourceName"] = source_name
            merged.append(record)
        else:
            # 多源合并：以freecho为基础，用kaoyan补充
            freecho_rec = None
            kaoyan_rec = None
            for src, rec in sources:
                if src == "freecho":
                    freecho_rec = rec
                else:
                    kaoyan_rec = rec

            base = freecho_rec or kaoyan_rec
            supplement = kaoyan_rec if base == freecho_rec else freecho_rec

            # 用kaoyan的复试线（freecho没有）
            if supplement and not base.get("reexaminationLine") and supplement.get("reexaminationLine"):
                base["reexaminationLine"] = supplement["reexaminationLine"]

            # 用kaoyan的考试科目（如果freecho为空）
            if supplement and not base.get("examSubjects") and supplement.get("examSubjects"):
                base["examSubjects"] = supplement["examSubjects"]

            # 合并remarks
            base_remarks = base.get("remarks", "")
            supp_remarks = supplement.get("remarks", "") if supplement else ""
            if supp_remarks and supp_remarks not in base_remarks:
                base["remarks"] = f"{base_remarks} | {supp_remarks}".strip(" |")

            # 标记多源
            base["sourceName"] = "freecho+kaoyan"

            merged.append(base)

    return merged


def main():
    print("=" * 60)
    print("Data Cleaning Pipeline (freecho + kaoyan merge)")
    print("=" * 60)

    freecho = read_freecho()
    kaoyan = read_kaoyan()

    print(f"\nMerging records...")
    merged = merge_records(freecho, kaoyan)
    print(f"After merge: {len(merged)}")

    merged.sort(key=lambda x: (x["universityName"], x["majorCode"], x["admissionYear"]))

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=PLATFORM_COLUMNS)
        writer.writeheader()
        for r in merged:
            writer.writerow({k: r.get(k, "") for k in PLATFORM_COLUMNS})

    print(f"\nOutput: {OUTPUT_FILE}")
    f_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
    print(f"File size: {f_size:.2f} MB")

    # 统计
    uni_set = set()
    year_stats = defaultdict(int)
    cat_stats = defaultdict(int)
    source_stats = defaultdict(int)
    for r in merged:
        uni_set.add(r["universityName"])
        year_stats[r["admissionYear"]] += 1
        cat_stats[r["majorCode"][:2]] += 1
        source_stats[r["sourceName"]] += 1

    print(f"\nStats:")
    print(f"  Total records: {len(merged)}")
    print(f"  Unique universities: {len(uni_set)}")
    print(f"  By source:")
    for k, v in sorted(source_stats.items(), key=lambda x: -x[1]):
        print(f"    {k}: {v}")
    print(f"  By year:")
    for k, v in sorted(year_stats.items()):
        print(f"    {k}: {v}")
    print(f"  Top categories:")
    for k, v in sorted(cat_stats.items(), key=lambda x: -x[1])[:10]:
        print(f"    {k}: {v}")


if __name__ == "__main__":
    main()
