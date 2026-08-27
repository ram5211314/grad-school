"""
数据清洗脚本
1. 按4位专业代码归并专业名称
2. 过滤非CS专业（仅保留0812/0835/0839/0854）
3. 统一高校名（去除括号差异）
4. 过滤非主流专业名
"""
import csv
import re
import sys
from pathlib import Path

INPUT_FILE = Path(__file__).parent / "runs" / "full_import.csv"
OUTPUT_FILE = Path(__file__).parent / "runs" / "cleaned_import.csv"
RESOURCES_FILE = Path(__file__).parent.parent / "services" / "business-service" / "src" / "main" / "resources" / "data" / "cpeer_programs_import.csv"

# 专业代码 -> 标准名称
MAJOR_STANDARD = {
    "0812": "计算机科学与技术",
    "0835": "软件工程",
    "0839": "网络空间安全",
    "0854": "电子信息",
}

# 合法的专业名称关键词（包含这些词的专业保留）
CS_KEYWORDS = [
    "计算机", "软件", "网络空间安全", "信息安全", "电子信息",
    "大数据", "人工智能", "计算机技术", "软件工程",
    "计算机科学与技术", "网络与信息安全",
]

# 非CS专业黑名单
NON_CS_BLACKLIST = [
    "音乐", "艺术", "化学", "物理", "生物", "数学", "力学",
    "材料", "能源", "环境", "地理", "天文", "医学", "教育",
    "管理", "经济", "金融", "法学", "文学", "历史", "哲学",
    "电子科学与技术", "信息与通信工程", "通信工程", "信号",
    "控制科学与工程", "控制工程", "仪器", "光学工程",
    "电气工程", "机械", "交通", "土木", "建筑",
    "检测技术", "模式识别", "智能科学", "自动化",
    "集成电路", "光电", "微电子", "物联网",
    "电子商务", "物流", "工业工程", "工程管理",
    "数字媒体", "数字表演", "摄影测量", "遥感",
    "地图", "地理信息", "资源与环境", "智慧",
]

# 高校→省份映射（修复CPEER数据中缺失省份的高校）
UNI_PROVINCE_FIX = {
    "中国矿业大学(北京)": "北京",
    "中国地质大学(北京)": "北京",
    "中国地质大学(武汉)": "湖北",
    "中国科学院大学": "北京",
    "宁波大学": "浙江",
    "成都理工大学": "四川",
}

def normalize_uni(name):
    """标准化高校名"""
    name = name.strip()
    name = name.replace("（", "(").replace("）", ")")
    mapping = {
        "中国矿业大学（北京）": "中国矿业大学(北京)",
        "中国矿业大学(北京)": "中国矿业大学(北京)",
        "中国地质大学（北京）": "中国地质大学(北京)",
        "中国地质大学(北京)": "中国地质大学(北京)",
        "中国地质大学（武汉）": "中国地质大学(武汉)",
        "中国地质大学(武汉)": "中国地质大学(武汉)",
    }
    return mapping.get(name, name)

def normalize_major_name(name, code):
    """标准化专业名称"""
    name = name.strip()
    # 去除前缀代码如 "081203-计算机科学与技术" -> "计算机科学与技术"
    if re.match(r"^\d{6}-", name):
        name = name.split("-", 1)[1]
    # 去除括号内容
    for sep in ["（", "("]:
        if sep in name:
            name = name.split(sep)[0].strip()
    # 按代码归并
    if code in MAJOR_STANDARD:
        return MAJOR_STANDARD[code]
    return name

def is_cs_related(name):
    """判断是否为CS相关"""
    # 先检查黑名单
    for kw in NON_CS_BLACKLIST:
        if kw in name:
            return False
    # 再检查白名单
    for kw in CS_KEYWORDS:
        if kw in name:
            return True
    return False

def get_major_code(code):
    """标准化专业代码为4位"""
    if not code:
        return ""
    code = str(code).strip()
    # 提取前4位
    m = re.match(r"(\d{4})", code)
    if m:
        return m.group(1)
    return code

def main():
    print("=" * 60)
    print("数据清洗脚本")
    print("=" * 60)

    # 读取数据
    records = []
    with open(INPUT_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(row)

    print(f"原始记录数: {len(records)}")

    # 清洗
    cleaned = []
    skipped = {"non_cs": 0, "bad_major": 0, "no_code": 0}

    for r in records:
        code = get_major_code(r.get("majorCode", ""))
        major = r.get("majorName", "").strip()

        # 过滤非CS专业
        if code not in MAJOR_STANDARD:
            skipped["no_code"] += 1
            continue

        if not is_cs_related(major):
            skipped["non_cs"] += 1
            continue

        # 标准化
        r["universityName"] = normalize_uni(r.get("universityName", ""))
        r["majorCode"] = code
        r["majorName"] = MAJOR_STANDARD[code]

        # 修复省份
        uni = r["universityName"]
        if uni in UNI_PROVINCE_FIX:
            r["province"] = UNI_PROVINCE_FIX[uni]
        elif r.get("province", "") == "未知":
            r["province"] = "北京"  # 未知省份默认北京（多数CS强校在北京）

        cleaned.append(r)

    print(f"清洗后记录数: {len(cleaned)}")
    print(f"过滤: 非CS={skipped['non_cs']}, 无代码={skipped['no_code']}")

    # 统计
    majors = {}
    unis = set()
    for r in cleaned:
        mc = r["majorCode"]
        u = r["universityName"]
        if mc not in majors:
            majors[mc] = 0
        majors[mc] += 1
        unis.add(u)

    print(f"\n专业分布:")
    for mc, cnt in sorted(majors.items()):
        print(f"  {mc} {MAJOR_STANDARD.get(mc, '?')}: {cnt}条")
    print(f"\n高校数: {len(unis)}")

    # 输出
    header = [
        "universityName", "province", "majorCode", "majorName", "degreeType",
        "studyMode", "examSubjects", "reexaminationLine", "actualEnrollment",
        "registrationCount", "admissionYear", "universityLevel", "plannedEnrollment",
        "nationalLine", "sourceName", "sourceUrl", "sourceYear", "remarks"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(cleaned)

    # 同时复制到resources
    with open(RESOURCES_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(cleaned)

    print(f"\n输出: {OUTPUT_FILE}")
    print(f"复制到: {RESOURCES_FILE}")
    print("=" * 60)

if __name__ == "__main__":
    main()
