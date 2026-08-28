"""
研招网专业目录爬取脚本（全学科版）
目标：获取2020-2025年所有学科门类的招生目录数据
数据源：https://yz.chsi.com.cn/zsml/queryAction.do
支持断点续爬：中断后重新运行会跳过已完成的任务
"""
import requests
import csv
import time
import random
import json
import sys
import argparse
from datetime import datetime
from pathlib import Path

# 配置
BASE_URL = "https://yz.chsi.com.cn/zsml/queryAction.do"
PROVINCES = {
    "11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古",
    "21": "辽宁", "22": "吉林", "23": "黑龙江", "31": "上海", "32": "江苏",
    "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东",
    "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西",
    "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南",
    "54": "西藏", "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆"
}
MAJOR_TYPES = {"zyxw": "学术学位", "zyzw": "专业学位"}
STUDY_MODES = {"1": "FULL_TIME", "2": "PART_TIME"}
# 默认爬取的学科门类（数据量最大的8个）
DEFAULT_CATEGORIES = ["02", "03", "04", "05", "07", "08", "10", "12"]
CATEGORY_NAMES = {
    "01": "哲学", "02": "经济学", "03": "法学", "04": "教育学", "05": "文学",
    "06": "历史学", "07": "理学", "08": "工学", "09": "农学", "10": "医学",
    "11": "军事学", "12": "管理学", "13": "艺术学", "14": "交叉学科"
}
HEADERS_LIST = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

# 输出目录
RUN_DIR = Path(__file__).parent / "runs" / datetime.now().strftime("%Y%m%d-%H%M%S")
RUN_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = RUN_DIR / "yz_directory.csv"
PROGRESS_FILE = RUN_DIR / "progress.json"
SUMMARY_FILE = RUN_DIR / "summary.json"

def get_random_header():
    return {"User-Agent": random.choice(HEADERS_LIST)}

def load_progress():
    """加载断点续爬进度"""
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"completed": [], "total_records": 0}

def save_progress(progress):
    """保存断点续爬进度"""
    with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
        json.dump(progress, f, ensure_ascii=False, indent=2)

def fetch_page(params, session, max_retries=3):
    """获取单页数据"""
    for attempt in range(max_retries):
        try:
            resp = session.post(BASE_URL, data=params, headers=get_random_header(), timeout=30)
            resp.encoding = "utf-8"
            if resp.status_code == 200:
                return resp.text
            print(f"  [WARN] HTTP {resp.status_code}, 重试 {attempt+1}/{max_retries}")
        except Exception as e:
            print(f"  [ERROR] 请求失败: {e}, 重试 {attempt+1}/{max_retries}")
        time.sleep(random.uniform(2, 4))
    return None

def parse_list_page(html):
    """解析列表页，提取总页数"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    page_info = soup.find("span", class_="page-info")
    total_pages = 1
    if page_info:
        text = page_info.get_text()
        if "/" in text:
            parts = text.split("/")
            total_pages = int(parts[1].strip()) if parts[1].strip().isdigit() else 1
    return total_pages

def parse_detail_page(html, province_code, year, degree_type):
    """解析详情页，提取所有专业的招生信息"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    records = []
    table = soup.find("table", class_="ch-table")
    if not table:
        return records

    rows = table.find_all("tr")[1:]
    current_school = ""
    current_dept = ""

    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 6:
            school_col = cols[0]
            if school_col.get_text(strip=True):
                current_school = school_col.get_text(strip=True)

            dept_col = cols[1]
            if dept_col.get_text(strip=True):
                current_dept = dept_col.get_text(strip=True)

            major_text = cols[2].get_text(strip=True)
            direction = cols[3].get_text(strip=True)
            plan_count_text = cols[4].get_text(strip=True)
            plan_count = None
            if plan_count_text and plan_count_text.isdigit():
                plan_count = int(plan_count_text)

            exam_subjects = cols[5].get_text(strip=True) if len(cols) > 5 else ""

            # 解析专业代码和名称
            major_code = ""
            major_name = major_text
            if "(" in major_text and ")" in major_text:
                code_part = major_text.split("(")[1].split(")")[0]
                name_part = major_text.split("(")[0]
                major_code = code_part
                major_name = name_part
            elif "\uff08" in major_text and "\uff09" in major_text:
                code_part = major_text.split("\uff08")[1].split("\uff09")[0]
                name_part = major_text.split("\uff08")[0]
                major_code = code_part
                major_name = name_part

            records.append({
                "universityName": current_school,
                "province": PROVINCES.get(province_code, province_code),
                "majorCode": major_code,
                "majorName": major_name,
                "degreeType": degree_type,
                "studyMode": "FULL_TIME",
                "examSubjects": exam_subjects,
                "reexaminationLine": "",
                "actualEnrollment": "",
                "registrationCount": "",
                "admissionYear": year,
                "universityLevel": "",
                "plannedEnrollment": plan_count if plan_count else "",
                "nationalLine": "",
                "sourceName": f"研招网专业目录({year}年)",
                "sourceUrl": "https://yz.chsi.com.cn/zsml/",
                "sourceYear": year,
                "remarks": f"院系: {current_dept}, 研究方向: {direction}"
            })

    return records

def scrape_task(year, province_code, province_name, major_type_code, major_type_name, study_mode_code, study_mode_name, session):
    """爬取单个任务（年份+省份+学位类型+学习方式）"""
    params = {
        "ssdm": province_code,
        "dwmc": "",
        "mldm": major_type_code,
        "xxfs": study_mode_code,
        "pageno": "1"
    }

    html = fetch_page(params, session)
    if not html:
        return []

    total_pages = parse_list_page(html)
    records = parse_detail_page(html, province_code, year, major_type_name)
    # 设置学习方式
    for r in records:
        r["studyMode"] = study_mode_name

    for page in range(2, min(total_pages + 1, 10)):
        params["pageno"] = str(page)
        html = fetch_page(params, session)
        if html:
            page_records = parse_detail_page(html, province_code, year, major_type_name)
            for r in page_records:
                r["studyMode"] = study_mode_name
            records.extend(page_records)
        time.sleep(random.uniform(1, 2))

    return records

def main():
    parser = argparse.ArgumentParser(description="研招网专业目录爬取脚本（全学科版）")
    parser.add_argument("--categories", type=str, default=",".join(DEFAULT_CATEGORIES),
                        help=f"要爬取的学科门类代码，逗号分隔。默认: {','.join(DEFAULT_CATEGORIES)}")
    parser.add_argument("--year-start", type=int, default=2020, help="起始年份，默认2020")
    parser.add_argument("--year-end", type=int, default=2026, help="结束年份，默认2026")
    parser.add_argument("--resume", action="store_true", default=True, help="断点续爬（默认开启）")
    parser.add_argument("--fresh", action="store_true", help="不续爬，从头开始")
    args = parser.parse_args()

    categories = [c.strip() for c in args.categories.split(",") if c.strip()]
    year_start = args.year_start
    year_end = args.year_end

    print("=" * 60)
    print("研招网专业目录爬取脚本（全学科版）")
    print("=" * 60)
    print(f"目标年份: {year_start}-{year_end}")
    print(f"学科门类: {', '.join(f'{c} {CATEGORY_NAMES.get(c, c)}' for c in categories)}")
    print(f"省份数量: {len(PROVINCES)}")
    print(f"输出目录: {RUN_DIR}")
    print()

    # 加载进度
    progress = load_progress() if not args.fresh else {"completed": [], "total_records": 0}
    completed_set = set(progress["completed"])
    all_records_count = progress["total_records"]

    session = requests.Session()

    # 生成所有任务
    tasks = []
    for year in range(year_start, year_end + 1):
        for prov_code, prov_name in PROVINCES.items():
            for mt_code, mt_name in MAJOR_TYPES.items():
                for sm_code, sm_name in STUDY_MODES.items():
                    task_key = f"{year}|{prov_code}|{mt_code}|{sm_code}"
                    tasks.append((year, prov_code, prov_name, mt_code, mt_name, sm_code, sm_name, task_key))

    total_tasks = len(tasks)
    skip_tasks = len(completed_set)
    print(f"总任务数: {total_tasks}，已完成: {skip_tasks}，剩余: {total_tasks - skip_tasks}")
    print()

    # 创建输出文件并写入表头
    header = [
        "universityName", "province", "majorCode", "majorName", "degreeType",
        "studyMode", "examSubjects", "reexaminationLine", "actualEnrollment",
        "registrationCount", "admissionYear", "universityLevel", "plannedEnrollment",
        "nationalLine", "sourceName", "sourceUrl", "sourceYear", "remarks"
    ]

    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()

    # 执行任务
    for i, (year, prov_code, prov_name, mt_code, mt_name, sm_code, sm_name, task_key) in enumerate(tasks):
        if task_key in completed_set:
            continue

        print(f"[{i+1}/{total_tasks}] {year}年 {prov_name} {mt_name} {sm_name}...", end=" ", flush=True)

        records = scrape_task(year, prov_code, prov_name, mt_code, mt_name, sm_code, sm_name, session)
        all_records_count += len(records)

        # 追加写入CSV
        if records:
            with open(OUTPUT_FILE, "a", encoding="utf-8-sig", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=header)
                writer.writerows(records)

        # 更新进度
        completed_set.add(task_key)
        progress["completed"] = list(completed_set)
        progress["total_records"] = all_records_count
        save_progress(progress)

        print(f"{len(records)}条 (累计: {all_records_count})")

        # 请求间隔
        time.sleep(random.uniform(1, 3))

    # 生成摘要
    summary = {
        "totalRecords": all_records_count,
        "categories": categories,
        "yearRange": [year_start, year_end],
        "provinces": list(PROVINCES.values()),
        "outputFile": str(OUTPUT_FILE),
        "generatedAt": datetime.now().isoformat()
    }

    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"爬取完成!")
    print(f"总记录数: {all_records_count}")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
