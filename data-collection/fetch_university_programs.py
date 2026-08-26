"""Fetch per-university program data from CHSI API."""
import json, sys, time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Referer': 'https://yz.chsi.com.cn/zsml/',
    'X-Requested-With': 'XMLHttpRequest',
}

def submit_query(params):
    data = urlencode(params).encode()
    req = Request('https://yz.chsi.com.cn/zsml/rs/zys.do', data=data, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

def search_university(university_name):
    """Search for a specific university's CS programs."""
    params = {
        'dwmc': university_name,
        'ssdm': '',
        'yjxkdm': '',
        'xxfs': '',
        'mldm': '',
        'zymc': ''
    }
    result = submit_query(params)
    msg = result.get('msg', {})
    if not msg:
        print(f'  No msg for {university_name}', file=sys.stderr)
        return []
    items = msg.get('list', [])
    total = msg.get('totalCount', 0)
    total_pages = msg.get('totalPage', 0)
    print(f'  {university_name}: {total} programs, {total_pages} pages, got {len(items)} from page 1', file=sys.stderr)
    return items, total_pages, msg.get('size', 10), result.get('taskId', '')

# Test with a few well-known universities
universities = [
    '清华大学', '北京大学', '浙江大学', '上海交通大学',
    '南京大学', '中国科学技术大学', '哈尔滨工业大学',
    '西安交通大学', '华中科技大学', '电子科技大学',
    '北京航空航天大学', '北京理工大学', '东南大学',
    '武汉大学', '同济大学', '中山大学',
    '大连理工大学', '天津大学', '华南理工大学',
    '重庆大学', '山东大学', '厦门大学',
]

all_programs = []
for uni in universities:
    print(f'Searching {uni}...', file=sys.stderr)
    try:
        items, total_pages, size, task_id = search_university(uni)
        all_items = list(items)
        
        # Get remaining pages
        for page in range(2, total_pages + 1):
            time.sleep(1.5)
            start = (page - 1) * size
            data = urlencode({'taskId': task_id, 'start': str(start)}).encode()
            req = Request('https://yz.chsi.com.cn/zsml/ajaxRs.do', data=data, headers=HEADERS)
            try:
                with urlopen(req, timeout=30) as resp:
                    raw = resp.read()
                    if len(raw) > 5:
                        try:
                            result = json.loads(raw.decode('utf-8'))
                        except:
                            result = json.loads(raw.decode('gbk'))
                        if 'msg' in result:
                            all_items.extend(result['msg'].get('list', []))
                            print(f'  Page {page}/{total_pages}: +{len(result["msg"]["list"])}', file=sys.stderr)
            except Exception as e:
                print(f'  Page {page} failed: {e}', file=sys.stderr)
                break
        
        for item in all_items:
            item['dwmc'] = uni
        all_programs.extend(all_items)
        print(f'  Total for {uni}: {len(all_items)}', file=sys.stderr)
    except Exception as e:
        print(f'  ERROR for {uni}: {e}', file=sys.stderr)
    time.sleep(2)

print(f'\nGrand total: {len(all_programs)} programs', file=sys.stderr)

# Save
with open('data-collection/runs/chsi_university_programs.json', 'w', encoding='utf-8') as f:
    json.dump(all_programs, f, ensure_ascii=False, indent=2)

print('Saved to data-collection/runs/chsi_university_programs.json', file=sys.stderr)
