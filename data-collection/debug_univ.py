"""Fetch university list for a specific program from CHSI API."""
import json, sys, time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Referer': 'https://yz.chsi.com.cn/zsml/zydetail.do',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'X-Requested-With': 'XMLHttpRequest',
}

def fetch_universities(sign):
    data = urlencode({'sign': sign}).encode()
    req = Request('https://yz.chsi.com.cn/zsml/ajaxRs.do', data=data, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
        print(f'Response length: {len(raw)}', file=sys.stderr)
        try:
            return json.loads(raw.decode('utf-8'))
        except:
            return json.loads(raw.decode('gbk'))

# Try with the first program's sign
sign = 'dcfb855900b3c8433e3773a4b0c455f2'  # 081200 计算机科学与技术
result = fetch_universities(sign)
print(json.dumps(result, ensure_ascii=False, indent=2))
