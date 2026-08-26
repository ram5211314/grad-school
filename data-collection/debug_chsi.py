"""Debug CHSI API response."""
import json, time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Referer': 'https://yz.chsi.com.cn/zsml/',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
}

# Step 1: Submit query
data = urlencode({
    'dwmc': '',
    'ssdm': '',
    'yjxkdm': '0812',
    'xxfs': '',
    'mldm': '08',
    'zymc': ''
}).encode()

req = Request('https://yz.chsi.com.cn/zsml/rs/zys.do', data=data, headers=HEADERS)
with urlopen(req, timeout=30) as resp:
    raw1 = resp.read()
    print(f'Submit response length: {len(raw1)}')
    print(f'Submit response (first 500): {raw1[:500]}')
    result1 = json.loads(raw1.decode('utf-8'))
    task_id = result1['taskId']
    print(f'Task ID: {task_id}')

time.sleep(3)

# Step 2: Poll
data2 = urlencode({'taskId': task_id}).encode()
req2 = Request('https://yz.chsi.com.cn/zsml/ajaxRs.do', data=data2, headers=HEADERS)
with urlopen(req2, timeout=30) as resp:
    raw2 = resp.read()
    print(f'\nPoll response length: {len(raw2)}')
    print(f'Poll raw bytes (first 200): {raw2[:200]}')
    # Try different encodings
    for enc in ['utf-8', 'gbk', 'gb2312', 'gb18030', 'latin1']:
        try:
            decoded = raw2.decode(enc)
            print(f'\nDecode with {enc}: {decoded[:500]}')
            result2 = json.loads(decoded)
            print(f'Parsed JSON keys: {list(result2.keys())}')
            if 'msg' in result2:
                print(f'MSG keys: {list(result2["msg"].keys())}')
                print(f'Total count: {result2["msg"].get("totalCount")}')
            break
        except Exception as e:
            print(f'  {enc} failed: {e}')
