"""Debug CHSI API - search by university + major code."""
import json, sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Referer': 'https://yz.chsi.com.cn/zsml/',
    'X-Requested-With': 'XMLHttpRequest',
}

def search(dwmc, yjxkdm, zymc=''):
    params = {
        'dwmc': dwmc,
        'ssdm': '',
        'yjxkdm': yjxkdm,
        'xxfs': '',
        'mldm': '08',
        'zymc': zymc
    }
    data = urlencode(params).encode()
    req = Request('https://yz.chsi.com.cn/zsml/rs/zys.do', data=data, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
        return json.loads(raw.decode('utf-8'))

# Try different combinations
tests = [
    ('清华大学', '0812', '计算机'),
    ('清华大学', '0854', ''),
    ('北京大学', '0812', ''),
    ('浙江大学', '0812', ''),
    ('浙江大学', '0854', ''),
]

for dwmc, yjxkdm, zymc in tests:
    result = search(dwmc, yjxkdm, zymc)
    msg = result.get('msg', '')
    flag = result.get('flag', False)
    if isinstance(msg, dict):
        items = msg.get('list', [])
        total = msg.get('totalCount', 0)
        print(f'{dwmc} {yjxkdm} {zymc}: flag={flag}, total={total}, items={len(items)}')
        if items:
            for item in items[:2]:
                print(f'  {item.get("zydm")} {item.get("zymc")} ({item.get("xwlxmc")})')
    else:
        print(f'{dwmc} {yjxkdm} {zymc}: flag={flag}, msg={msg}')
