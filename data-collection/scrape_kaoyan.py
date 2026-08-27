"""
kaoyan.cn API scraper - 补充考研数据（分数线+研究方向+多年数据）
API三层:
  1. /pc/school/schoolList → 院校列表
  2. /pc/school/planListV2 → 专业列表
  3. /pc/school/planDetailV2 → 分数线+研究方向详情
"""
import requests
import csv
import time
import random
import sys
import os
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Referer": "https://www.kaoyan.cn/",
    "Content-Type": "application/x-www-form-urlencoded"
}

CS_CODES_4 = {"0812", "0835", "0839", "0854"}
CS_CODES_6_PREFIX = {"0812", "0835", "0839", "0854"}

PROVINCES = {
    "11": "北京", "12": "天津", "13": "河北", "14": "山西", "15": "内蒙古",
    "21": "辽宁", "22": "吉林", "23": "黑龙江",
    "31": "上海", "32": "江苏", "33": "浙江", "34": "安徽", "35": "福建", "36": "江西", "37": "山东",
    "41": "河南", "42": "湖北", "43": "湖南", "44": "广东", "45": "广西", "46": "海南",
    "50": "重庆", "51": "四川", "52": "贵州", "53": "云南", "54": "西藏",
    "61": "陕西", "62": "甘肃", "63": "青海", "64": "宁夏", "65": "新疆"
}

BASE_URL = "https://api.kaoyan.cn/pc/school"
SESSION = requests.Session()
SESSION.headers.update(HEADERS)


def api_post(endpoint, params, retries=3):
    for attempt in range(retries):
        try:
            resp = SESSION.post(f"{BASE_URL}/{endpoint}", data=params, timeout=15)
            if resp.status_code == 200:
                return resp.json()
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 * (attempt + 1))
    return None


def get_schools(province_id):
    schools = []
    page = 1
    while True:
        data = api_post("schoolList", {"page": page, "limit": 50, "province_id": province_id, "type": "", "feature": "", "school_name": ""})
        if not data or "data" not in data or "data" not in data["data"]:
            break
        items = data["data"]["data"]
        if not items:
            break
        schools.extend(items)
        if len(schools) >= data["data"].get("total", 0):
            break
        page += 1
        time.sleep(random.uniform(0.5, 1.5))
    return schools


def get_majors(school_id):
    data = api_post("planListV2", {"school_id": school_id, "limit": 200})
    if not data or "data" not in data or "data" not in data["data"]:
        return []
    return data["data"]["data"]


def get_detail(plan_id):
    data = api_post("planDetailV2", {"plan_id": plan_id, "is_apply": 2})
    if not data or "data" not in data:
        return None
    return data["data"]


def is_cs_related(code):
    if not code:
        return False
    code4 = code[:4]
    return code4 in CS_CODES_4


def extract_records(school_name, province, major_info, detail):
    records = []
    if not detail:
        return records

    special_name = detail.get("special_name", "")
    special_code = detail.get("special_code", "")
    depart_name = detail.get("depart_name", "")
    degree_type = detail.get("degree_type_name", "")
    recruit_type = detail.get("recruit_type_name", "")
    min_score = detail.get("min_score")
    research_area_data = detail.get("research_area_data", {})

    for year_str, directions in research_area_data.items():
        try:
            year = int(year_str)
        except:
            continue
        if year < 2020 or year > 2026:
            continue
        for d in directions:
            research_area = d.get("research_area", "").strip()
            exam_subject = d.get("exam_subject", "").strip().replace("\n", " ")
            recruit_number = d.get("recruit_number")
            note = d.get("note", "").strip()

            study_mode = "FULL_TIME"
            if "非全日制" in str(recruit_type) or "非全" in str(note):
                study_mode = "PART_TIME"

            records.append({
                "universityName": school_name,
                "province": province,
                "majorCode": special_code,
                "majorName": special_name,
                "degreeType": degree_type,
                "studyMode": study_mode,
                "examSubjects": exam_subject,
                "department": depart_name,
                "researchDirection": research_area,
                "reexaminationLine": min_score if min_score else "",
                "plannedEnrollment": recruit_number if recruit_number else "",
                "remarks": note[:200] if note else "",
                "admissionYear": year,
                "sourceName": "kaoyan.cn",
                "sourceUrl": f"https://www.kaoyan.cn/school/{detail.get('school_id', '')}/major/{detail.get('spe_id', '')}",
                "sourceYear": year
            })
    return records


def main():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_file = os.path.join(out_dir, "runs", "kaoyan_cs_data.csv")
    os.makedirs(os.path.dirname(out_file), exist_ok=True)

    with open(out_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "universityName", "province", "majorCode", "majorName",
            "degreeType", "studyMode", "examSubjects", "department",
            "researchDirection", "reexaminationLine", "plannedEnrollment",
            "remarks", "admissionYear", "sourceName", "sourceUrl", "sourceYear"
        ])
        writer.writeheader()

        total_records = 0
        total_schools = 0
        total_majors = 0
        cs_majors_found = 0

        provinces_to_scan = list(PROVINCES.keys())
        random.shuffle(provinces_to_scan)

        for prov_code in provinces_to_scan:
            prov_name = PROVINCES[prov_code]
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Province: {prov_name} ({prov_code})")

            schools = get_schools(prov_code)
            print(f"  Found {len(schools)} schools")

            for school in schools:
                school_name = school.get("school_name", "")
                school_id = school.get("school_id", "")
                if not school_id:
                    continue

                total_schools += 1
                majors = get_majors(school_id)
                time.sleep(random.uniform(0.3, 0.8))

                cs_major_list = [m for m in majors if is_cs_related(m.get("special_code", ""))]
                if not cs_major_list:
                    continue

                cs_majors_found += len(cs_major_list)
                for major in cs_major_list:
                    plan_id = major.get("plan_id", "")
                    if not plan_id:
                        continue

                    detail = get_detail(plan_id)
                    time.sleep(random.uniform(0.3, 0.8))

                    if detail:
                        total_majors += 1
                        records = extract_records(school_name, prov_name, major, detail)
                        for r in records:
                            writer.writerow(r)
                            total_records += 1

                if total_schools % 50 == 0:
                    f.flush()
                    print(f"  Progress: {total_schools} schools, {total_records} records")

            print(f"  [{prov_name}] Done. Total so far: {total_records} records")

    print(f"\n{'='*60}")
    print(f"FINISHED")
    print(f"Total schools scanned: {total_schools}")
    print(f"Total CS majors found: {cs_majors_found}")
    print(f"Total records exported: {total_records}")
    print(f"Output: {out_file}")


if __name__ == "__main__":
    main()
