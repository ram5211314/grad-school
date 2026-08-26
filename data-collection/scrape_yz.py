"""
研招网专业目录爬取脚本
目标：获取2020-2025年计算机相关专业的招生目录数据
数据源：https://yz.chsi.com.cn/zsml/queryAction.do
"""
import requests
import csv
import time
import random
import json
import sys
from datetime import datetime
from pathlib import Path

# 配置
BASE_URL = "https://yz.chsi.com.cn/zsml/queryAction.do"
DETAIL_URL = "https://yz.chsi.com.cn/zsml/querySchAction.do"
PROVINCES = {
    "11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古",
    "21": "辽宁", "22": "吉林", "23": "黑龙江", "31": "上海", "32": "江苏",
    "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东",
    "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西",
    "46": "海南", "50": "重庆", "51": "四川", "52": "贵州", "53": "云南",
    "54": "西藏", "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆"
}
MAJOR_CODES = ["0812", "0835", "0839", "0854"]
MAJOR_TYPES = {"zyxw": "学术学位", "zyzw": "专业学位"}
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
SUMMARY_FILE = RUN_DIR / "summary.json"

def get_random_header():
    return {"User-Agent": random.choice(HEADERS_LIST)}

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
    """解析列表页，提取学校列表"""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html, "lxml")
    
    schools = []
    # 查找表格中的学校链接
    table = soup.find("table", class_="ch-table")
    if not table:
        return schools, 0
    
    rows = table.find_all("tr")[1:]  # 跳过表头
    for row in rows:
        cols = row.find_all("td")
        if len(cols) >= 2:
            link = cols[1].find("a")
            if link:
                school_name = link.get_text(strip=True)
                school_url = link.get("href", "")
                schools.append({"name": school_name, "url": school_url})
    
    # 获取总页数
    page_info = soup.find("span", class_="page-info")
    total_pages = 1
    if page_info:
        text = page_info.get_text()
        if "/" in text:
            parts = text.split("/")
            total_pages = int(parts[1].strip()) if parts[1].strip().isdigit() else 1
    
    return schools, total_pages

def parse_detail_page(html, province, year, major_type_name):
    """解析详情页，提取专业信息"""
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
            # 学校名称（可能跨行）
            school_col = cols[0]
            if school_col.get_text(strip=True):
                current_school = school_col.get_text(strip=True)
            
            # 院系所
            dept_col = cols[1]
            if dept_col.get_text(strip=True):
                current_dept = dept_col.get_text(strip=True)
            
            # 专业
            major_text = cols[2].get_text(strip=True)
            # 研究方向
            direction = cols[3].get_text(strip=True)
            # 拟招人数
            plan_count_text = cols[4].get_text(strip=True)
            plan_count = None
            if plan_count_text and plan_count_text.isdigit():
                plan_count = int(plan_count_text)
            
            # 考试科目
            exam_subjects = cols[5].get_text(strip=True) if len(cols) > 5 else ""
            
            # 解析专业代码和名称
            major_code = ""
            major_name = major_text
            if "(" in major_text and ")" in major_text:
                code_part = major_text.split("(")[1].split(")")[0]
                name_part = major_text.split("(")[0]
                major_code = code_part
                major_name = name_part
            elif "（" in major_text and "）" in major_text:
                code_part = major_text.split("（")[1].split("）")[0]
                name_part = major_text.split("（")[0]
                major_code = code_part
                major_name = name_part
            
            # 判断是否为计算机相关专业
            is_cs_related = any(code in major_code for code in ["0812", "0835", "0839", "0854"])
            if not is_cs_related:
                continue
            
            # 确定学位类型
            degree_type = "学术学位" if "学硕" in major_type_name or "学术" in major_type_name else "专业学位"
            
            records.append({
                "universityName": current_school,
                "province": PROVINCES.get(province, province),
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

def scrape_year(year, session):
    """爬取某一年的数据"""
    all_records = []
    
    for province_code, province_name in PROVINCES.items():
        print(f"\n[{year}] 爬取 {province_name} ({province_code})...")
        
        for major_type_code, major_type_name in MAJOR_TYPES.items():
            for major_code in MAJOR_CODES:
                params = {
                    "ssdm": province_code,
                    "dwmc": "",
                    "mldm": major_type_code,
                    "yjxkdm": major_code,
                    "xxfs": "1",
                    "pageno": "1"
                }
                
                # 获取第一页，确定总页数
                html = fetch_page(params, session)
                if not html:
                    continue
                
                schools, total_pages = parse_list_page(html)
                
                # 解析第一页的详情
                records = parse_detail_page(html, province_code, year, major_type_name)
                all_records.extend(records)
                
                # 获取后续页面
                for page in range(2, min(total_pages + 1, 6)):  # 最多5页
                    params["pageno"] = str(page)
                    html = fetch_page(params, session)
                    if html:
                        records = parse_detail_page(html, province_code, year, major_type_name)
                        all_records.extend(records)
                    time.sleep(random.uniform(1, 2))
                
                # 请求间隔
                time.sleep(random.uniform(1, 3))
        
        print(f"  {province_name}: 累计 {len(all_records)} 条")
    
    return all_records

def main():
    print("=" * 60)
    print("研招网专业目录爬取脚本")
    print("=" * 60)
    print(f"目标年份: 2020-2025")
    print(f"目标专业: 0812计算机, 0835软件工程, 0839网安, 0854电子信息")
    print(f"输出目录: {RUN_DIR}")
    print()
    
    session = requests.Session()
    all_records = []
    
    # 爬取2020-2025年数据
    for year in range(2020, 2026):
        print(f"\n{'='*40}")
        print(f"开始爬取 {year} 年数据...")
        print(f"{'='*40}")
        records = scrape_year(year, session)
        all_records.extend(records)
        print(f"\n{year} 年完成，累计 {len(all_records)} 条")
    
    # 写入CSV
    header = [
        "universityName", "province", "majorCode", "majorName", "degreeType",
        "studyMode", "examSubjects", "reexaminationLine", "actualEnrollment",
        "registrationCount", "admissionYear", "universityLevel", "plannedEnrollment",
        "nationalLine", "sourceName", "sourceUrl", "sourceYear", "remarks"
    ]
    
    with open(OUTPUT_FILE, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(all_records)
    
    # 生成摘要
    summary = {
        "totalRecords": len(all_records),
        "years": list(set(r["admissionYear"] for r in all_records)),
        "provinces": list(set(r["province"] for r in all_records)),
        "universities": len(set(r["universityName"] for r in all_records)),
        "outputFile": str(OUTPUT_FILE),
        "generatedAt": datetime.now().isoformat()
    }
    
    with open(SUMMARY_FILE, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*60}")
    print(f"爬取完成!")
    print(f"总记录数: {len(all_records)}")
    print(f"高校数量: {summary['universities']}")
    print(f"省份数量: {len(summary['provinces'])}")
    print(f"年份范围: {min(summary['years'])}-{max(summary['years'])}")
    print(f"输出文件: {OUTPUT_FILE}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
