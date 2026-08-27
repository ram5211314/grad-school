"""
数据合并清洗脚本（改进版）
支持模糊匹配高校名、三源合并、自动补充国家线
"""
import csv
import re
import sys
from pathlib import Path
from collections import defaultdict

RUNS_DIR = Path(__file__).parent / "runs"
DERIVED_FILE = RUNS_DIR / "cpeer_derived_lines.csv"
OUTPUT_FILE = RUNS_DIR / "full_import.csv"

def normalize_uni(name):
    """标准化高校名（去除括号差异）"""
    name = name.strip()
    # 统一括号
    name = name.replace("（", "(").replace("）", ")")
    return name

def uni_key(name):
    """生成高校匹配键"""
    n = normalize_uni(name)
    # 去除括号内容
    base = re.sub(r"\s*\(.*?\)", "", n)
    return base

def load_csv(filepath):
    """加载CSV文件"""
    records = []
    if not filepath.exists():
        print(f"  [WARN] 文件不存在: {filepath}")
        return records
    with open(filepath, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)
    print(f"  加载 {len(records)} 条: {filepath.name}")
    return records

def normalize_major_code(code):
    """标准化专业代码"""
    if not code:
        return code
    code = code.strip()
    if len(code) >= 4:
        return code[:4]
    return code

def make_key(record):
    """生成去重键（改进版：使用标准化高校名）"""
    uni = uni_key(record.get("universityName", ""))
    major = record.get("majorName", "").strip()
    year = record.get("admissionYear", "").strip()
    return f"{uni}|{major}|{year}"

def merge_records(cpeer, fsx, derived):
    """合并三条数据源"""
    merged = {}

    # 1. 先加载CPEER数据（基础数据）
    for r in cpeer:
        key = make_key(r)
        if key not in merged:
            merged[key] = {
                "universityName": r.get("universityName", ""),
                "province": r.get("province", ""),
                "majorCode": normalize_major_code(r.get("majorCode", "")),
                "majorName": r.get("majorName", ""),
                "degreeType": r.get("degreeType", ""),
                "studyMode": r.get("studyMode", "FULL_TIME"),
                "examSubjects": r.get("examSubjects", ""),
                "reexaminationLine": r.get("reexaminationLine", ""),
                "actualEnrollment": r.get("actualEnrollment", ""),
                "registrationCount": r.get("registrationCount", ""),
                "admissionYear": r.get("admissionYear", ""),
                "universityLevel": r.get("universityLevel", ""),
                "plannedEnrollment": r.get("plannedEnrollment", ""),
                "nationalLine": r.get("nationalLine", ""),
                "sourceName": r.get("sourceName", ""),
                "sourceUrl": r.get("sourceUrl", ""),
                "sourceYear": r.get("sourceYear", ""),
                "remarks": r.get("remarks", "")
            }

    # 2. 合并推算的复试线数据
    derived_count = 0
    for r in derived:
        key = make_key(r)
        if key in merged:
            existing = merged[key]
            # 补充复试线（仅当原记录为空时）
            if not existing.get("reexaminationLine") and r.get("reexaminationLine"):
                existing["reexaminationLine"] = r["reexaminationLine"]
                derived_count += 1
            # 补充备注
            if r.get("remarks") and not existing.get("remarks"):
                existing["remarks"] = r["remarks"]
        else:
            # 新记录
            merged[key] = {
                "universityName": r.get("universityName", ""),
                "province": r.get("province", ""),
                "majorCode": normalize_major_code(r.get("majorCode", "")),
                "majorName": r.get("majorName", ""),
                "degreeType": r.get("degreeType", ""),
                "studyMode": r.get("studyMode", "FULL_TIME"),
                "examSubjects": r.get("examSubjects", ""),
                "reexaminationLine": r.get("reexaminationLine", ""),
                "actualEnrollment": r.get("actualEnrollment", ""),
                "registrationCount": r.get("registrationCount", ""),
                "admissionYear": r.get("admissionYear", ""),
                "universityLevel": r.get("universityLevel", ""),
                "plannedEnrollment": r.get("plannedEnrollment", ""),
                "nationalLine": r.get("nationalLine", ""),
                "sourceName": r.get("sourceName", ""),
                "sourceUrl": r.get("sourceUrl", ""),
                "sourceYear": r.get("sourceYear", ""),
                "remarks": r.get("remarks", "")
            }
            derived_count += 1

    # 3. 合并手动复试线数据（优先级最高）
    fsx_count = 0
    for r in fsx:
        key = make_key(r)
        if key in merged:
            existing = merged[key]
            # 补充复试线
            if r.get("reexaminationLine") and not existing.get("reexaminationLine"):
                existing["reexaminationLine"] = r["reexaminationLine"]
                fsx_count += 1
            # 补充计划招生数
            if r.get("plannedEnrollment") and not existing.get("plannedEnrollment"):
                existing["plannedEnrollment"] = r["plannedEnrollment"]
            # 补充考试科目
            if r.get("examSubjects") and r["examSubjects"] != "待补充" and not existing.get("examSubjects"):
                existing["examSubjects"] = r["examSubjects"]
            # 补充国家线
            if r.get("nationalLine") and not existing.get("nationalLine"):
                existing["nationalLine"] = r["nationalLine"]
            # 补充院校层次
            if r.get("universityLevel") and not existing.get("universityLevel"):
                existing["universityLevel"] = r["universityLevel"]
        else:
            # 新记录
            merged[key] = {
                "universityName": r.get("universityName", ""),
                "province": r.get("province", ""),
                "majorCode": normalize_major_code(r.get("majorCode", "")),
                "majorName": r.get("majorName", ""),
                "degreeType": r.get("degreeType", ""),
                "studyMode": r.get("studyMode", "FULL_TIME"),
                "examSubjects": r.get("examSubjects", ""),
                "reexaminationLine": r.get("reexaminationLine", ""),
                "actualEnrollment": r.get("actualEnrollment", ""),
                "registrationCount": r.get("registrationCount", ""),
                "admissionYear": r.get("admissionYear", ""),
                "universityLevel": r.get("universityLevel", ""),
                "plannedEnrollment": r.get("plannedEnrollment", ""),
                "nationalLine": r.get("nationalLine", ""),
                "sourceName": r.get("sourceName", ""),
                "sourceUrl": r.get("sourceUrl", ""),
                "sourceYear": r.get("sourceYear", ""),
                "remarks": r.get("remarks", "")
            }
            fsx_count += 1

    print(f"\n合并统计:")
    print(f"  CPEER原始: {len(cpeer)} 条")
    print(f"  推算复试线匹配: {derived_count} 条")
    print(f"  手动复试线匹配: {fsx_count} 条")
    print(f"  合并后总计: {len(merged)} 条")

    return list(merged.values())

def validate_data(records):
    """数据验证"""
    stats = {
        "total": len(records),
        "with_reex_line": 0,
        "with_planned": 0,
        "with_exam_subjects": 0,
        "with_enrollment": 0,
        "with_national": 0,
        "universities": set(),
        "years": set(),
        "provinces": set()
    }

    for r in records:
        if r.get("reexaminationLine") and str(r["reexaminationLine"]).strip():
            stats["with_reex_line"] += 1
        if r.get("plannedEnrollment") and str(r["plannedEnrollment"]).strip():
            stats["with_planned"] += 1
        if r.get("examSubjects") and r["examSubjects"] not in ["", "未公开", "待补充"]:
            stats["with_exam_subjects"] += 1
        if r.get("actualEnrollment") and str(r["actualEnrollment"]).strip():
            stats["with_enrollment"] += 1
        if r.get("nationalLine") and str(r["nationalLine"]).strip():
            stats["with_national"] += 1
        stats["universities"].add(r.get("universityName", ""))
        stats["years"].add(r.get("admissionYear", ""))
        stats["provinces"].add(r.get("province", ""))

    print(f"\n数据验证:")
    print(f"  总记录数: {stats['total']}")
    print(f"  复试线完整: {stats['with_reex_line']}/{stats['total']} ({stats['with_reex_line']/stats['total']*100:.1f}%)")
    print(f"  计划招生完整: {stats['with_planned']}/{stats['total']} ({stats['with_planned']/stats['total']*100:.1f}%)")
    print(f"  考试科目完整: {stats['with_exam_subjects']}/{stats['total']} ({stats['with_exam_subjects']/stats['total']*100:.1f}%)")
    print(f"  录取人数完整: {stats['with_enrollment']}/{stats['total']} ({stats['with_enrollment']/stats['total']*100:.1f}%)")
    print(f"  国家线完整: {stats['with_national']}/{stats['total']} ({stats['with_national']/stats['total']*100:.1f}%)")
    print(f"  高校数量: {len(stats['universities'])}")
    print(f"  年份范围: {sorted(stats['years'])}")
    print(f"  省份数量: {len(stats['provinces'])}")

def main():
    print("=" * 60)
    print("数据合并清洗脚本（改进版）")
    print("=" * 60)

    # 查找数据文件
    cpeer_file = RUNS_DIR / "cpeer_programs_import.csv"
    derived_file = DERIVED_FILE

    # 查找最新的复试线文件
    fsx_files = sorted(RUNS_DIR.glob("*/reexamination_lines.csv"))
    fsx_file = fsx_files[-1] if fsx_files else None

    print(f"\n数据源:")
    print(f"  CPEER数据: {cpeer_file}")
    print(f"  推算复试线: {derived_file}")
    print(f"  手动复试线: {fsx_file}")

    # 加载数据
    cpeer = load_csv(cpeer_file)
    derived = load_csv(derived_file) if derived_file and derived_file.exists() else []
    fsx = load_csv(fsx_file) if fsx_file else []

    if not cpeer:
        print("\n[ERROR] 没有找到CPEER数据!")
        sys.exit(1)

    # 合并数据
    merged = merge_records(cpeer, fsx, derived)

    # 验证数据
    validate_data(merged)

    # 输出CSV
    header = [
        "universityName", "province", "majorCode", "majorName", "degreeType",
        "studyMode", "examSubjects", "reexaminationLine", "actualEnrollment",
        "registrationCount", "admissionYear", "universityLevel", "plannedEnrollment",
        "nationalLine", "sourceName", "sourceUrl", "sourceYear", "remarks"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(merged)

    print(f"\n输出文件: {OUTPUT_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
