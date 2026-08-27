"""
从CPEER录取记录推算复试线
逻辑：取录取考生的最低初试成绩作为复试线近似值
"""
import sqlite3
import csv
import json
import sys
from pathlib import Path
from collections import defaultdict

DB_PATH = Path(__file__).parent / "runs" / "CPEER.db"
OUTPUT_FILE = Path(__file__).parent / "runs" / "cpeer_derived_lines.csv"

# 专业名称 -> 专业代码映射
MAJOR_CODE_MAP = {
    "计算机科学与技术": "081200",
    "计算机系统结构": "081200",
    "计算机软件与理论": "081200",
    "计算机应用技术": "081200",
    "软件工程": "083500",
    "网络空间安全": "083900",
    "信息安全": "083900",
    "电子信息": "085400",
    "计算机技术": "085400",
    "大数据技术与工程": "085400",
    "人工智能": "085400",
    "控制工程": "085400",
    "仪器仪表工程": "085400",
    "光学工程": "085400",
    "集成电路工程": "085400",
    "软件工程(专业学位)": "085400",
}

def normalize_major(name):
    """标准化专业名称"""
    name = name.strip()
    # 去除括号内容
    for sep in ["（", "("]:
        if sep in name:
            name = name.split(sep)[0].strip()
    return name

def get_major_code(major_name):
    """获取专业代码"""
    major = normalize_major(major_name)
    # 精确匹配
    if major in MAJOR_CODE_MAP:
        return MAJOR_CODE_MAP[major][:4]
    # 模糊匹配
    for key, code in MAJOR_CODE_MAP.items():
        if key in major or major in key:
            return code[:4]
    # 默认
    return "0854"

def is_cs_related(major_name):
    """判断是否为计算机相关专业"""
    major = normalize_major(major_name)
    cs_keywords = ["计算机", "软件", "网络空间安全", "信息安全", "电子信息",
                   "大数据", "人工智能", "控制工程", "计算机技术"]
    return any(kw in major for kw in cs_keywords)

def main():
    print("=" * 60)
    print("从CPEER推算复试线")
    print("=" * 60)

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    # 查询所有录取记录
    query = """
    SELECT u."院校", u."专业", u."年份", u."初试成绩", u."是否录取",
           un."所在省", un."院校性质"
    FROM Users u
    LEFT JOIN Universities un ON u."院校" = un."院校"
    WHERE u."初试成绩" IS NOT NULL AND u."初试成绩" > 0
    """
    cursor.execute(query)
    rows = cursor.fetchall()
    print(f"读取 {len(rows)} 条记录")

    # 按(高校, 专业, 年份)分组
    groups = defaultdict(lambda: {
        "scores_all": [], "scores_admitted": [], "scores_rejected": [],
        "province": "", "level": ""
    })

    for row in rows:
        uni, major, year, score, admitted, province, level = row
        if not is_cs_related(major):
            continue

        key = (uni.strip(), normalize_major(major), year)
        groups[key]["scores_all"].append(score)
        groups[key]["province"] = province or ""
        groups[key]["level"] = str(level) if level else ""

        if admitted == "是":
            groups[key]["scores_admitted"].append(score)
        else:
            groups[key]["scores_rejected"].append(score)

    print(f"计算机相关分组: {len(groups)} 个")

    # 生成复试线数据
    records = []
    for (uni, major, year), data in groups.items():
        admitted = sorted(data["scores_admitted"])
        if not admitted:
            continue

        # 复试线 = 录取考生最低分（近似值）
        reex_line = int(min(admitted))
        # 录取最高分
        max_score = int(max(admitted))
        # 平均分
        avg_score = round(sum(admitted) / len(admitted), 1)
        # 录取人数
        enroll_count = len(admitted)
        # 报名人数（录取+未录取）
        reg_count = len(data["scores_all"])

        major_code = get_major_code(major)

        records.append({
            "universityName": uni,
            "province": data["province"],
            "majorCode": major_code,
            "majorName": major,
            "degreeType": "学术学位" if major_code in ["0812", "0835", "0839"] else "专业学位",
            "studyMode": "FULL_TIME",
            "examSubjects": "待补充",
            "reexaminationLine": reex_line,
            "actualEnrollment": enroll_count,
            "registrationCount": reg_count,
            "admissionYear": year,
            "universityLevel": data["level"],
            "plannedEnrollment": "",
            "nationalLine": "",
            "sourceName": "CPEER推算(录取最低分)",
            "sourceUrl": "https://github.com/Younai2021/CPEER-Dataset",
            "sourceYear": year,
            "remarks": f"推算复试线{reex_line}分,录取最高{max_score}分,平均{avg_score}分,录取{enroll_count}人"
        })

    # 按年份+高校排序
    records.sort(key=lambda r: (-r["admissionYear"], r["universityName"], r["majorCode"]))

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
        writer.writerows(records)

    print(f"\n输出 {len(records)} 条推算记录到 {OUTPUT_FILE}")

    # 统计
    unis = set(r["universityName"] for r in records)
    years = set(r["admissionYear"] for r in records)
    print(f"覆盖高校: {len(unis)} 所")
    print(f"覆盖年份: {sorted(years)}")

    # 复试线分布
    lines = [r["reexaminationLine"] for r in records]
    print(f"\n复试线分布:")
    print(f"  最低: {min(lines)}")
    print(f"  最高: {max(lines)}")
    print(f"  平均: {round(sum(lines)/len(lines), 1)}")
    print(f"  中位: {sorted(lines)[len(lines)//2]}")

    conn.close()

if __name__ == "__main__":
    main()
