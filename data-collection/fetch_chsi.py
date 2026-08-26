"""Fetch real program data from CHSI API - submit response contains data directly."""
import json, csv, sys, time, io
from urllib.request import Request, urlopen
from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Referer': 'https://yz.chsi.com.cn/zsml/',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
}

def submit_and_get(params):
    data = urlencode(params).encode()
    req = Request('https://yz.chsi.com.cn/zsml/rs/zys.do', data=data, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
        return json.loads(raw.decode('utf-8'))

def get_page(task_id, start):
    data = urlencode({'taskId': task_id, 'start': str(start)}).encode()
    req = Request('https://yz.chsi.com.cn/zsml/ajaxRs.do', data=data, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
        if len(raw) <= 5:
            return None
        try:
            return json.loads(raw.decode('utf-8'))
        except:
            return json.loads(raw.decode('gbk'))

def get_all_pages(task_id, first_msg):
    all_items = list(first_msg['list'])
    total_pages = first_msg['totalPage']
    size = first_msg.get('size', 10)
    print(f'  Page 1/{total_pages}: got {len(first_msg["list"])} items', file=sys.stderr)
    
    for page in range(2, total_pages + 1):
        time.sleep(2)
        start = (page - 1) * size
        result = get_page(task_id, start)
        if result and 'msg' in result:
            msg = result['msg']
            all_items.extend(msg['list'])
            print(f'  Page {page}/{total_pages}: got {len(msg["list"])} items', file=sys.stderr)
        else:
            # Try re-submitting the query
            print(f'  Page {page}: poll returned empty, re-submitting...', file=sys.stderr)
            break
    return all_items

def main():
    categories = [
        ('0812', '08', '计算机科学与技术'),
        ('0835', '08', '软件工程'),
        ('0839', '08', '网络空间安全'),
        ('0854', '08', '电子信息'),
    ]
    
    all_programs = []
    
    for yjxkdm, mldm, ml_name in categories:
        print(f'Querying category {yjxkdm} ({ml_name})...', file=sys.stderr)
        params = {
            'dwmc': '',
            'ssdm': '',
            'yjxkdm': yjxkdm,
            'xxfs': '',
            'mldm': mldm,
            'zymc': ''
        }
        result = submit_and_get(params)
        msg = result.get('msg', {})
        if not msg:
            print(f'  No msg in response, keys: {list(result.keys())}', file=sys.stderr)
            continue
        
        task_id = result.get('taskId', '')
        total = msg.get('totalCount', 0)
        total_pages = msg.get('totalPage', 0)
        print(f'  Found {total} programs across {total_pages} pages', file=sys.stderr)
        
        items = list(msg['list'])
        
        # Get remaining pages
        for page in range(2, total_pages + 1):
            time.sleep(2)
            start = (page - 1) * msg.get('size', 10)
            page_result = get_page(task_id, start)
            if page_result and 'msg' in page_result:
                page_msg = page_result['msg']
                items.extend(page_msg['list'])
                print(f'  Page {page}/{total_pages}: got {len(page_msg["list"])} items', file=sys.stderr)
            else:
                print(f'  Page {page}: empty response', file=sys.stderr)
                break
        
        for item in items:
            item['query_category'] = yjxkdm
            item['query_category_name'] = ml_name
        all_programs.extend(items)
        print(f'  Total {len(items)} programs in {yjxkdm}', file=sys.stderr)
        time.sleep(2)
    
    print(f'\nTotal programs found: {len(all_programs)}', file=sys.stderr)
    
    # Save raw JSON
    with open('data-collection/runs/chsi_programs_raw.json', 'w', encoding='utf-8') as f:
        json.dump(all_programs, f, ensure_ascii=False, indent=2)
    
    print('Saved to data-collection/runs/chsi_programs_raw.json', file=sys.stderr)

if __name__ == '__main__':
    main()
