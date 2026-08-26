"""Check if university filter actually works on CHSI API."""
import json, sys
from urllib.request import Request, urlopen
from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Referer': 'https://yz.chsi.com.cn/zsml/',
    'X-Requested-With': 'XMLHttpRequest',
}

def search(dwmc, yjxkdm):
    params = {
        'dwmc': dwmc,
        'ssdm': '',
        'yjxkdm': yjxkdm,
        'xxfs': '',
        'mldm': '08',
        'zymc': ''
    }
    data = urlencode(params).encode()
    req = Request('https://yz.chsi.com.cn/zsml/rs/zys.do', data=data, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

# Compare with and without university name
for dwmc in ['', '清华大学', '北京大学', '浙江大学']:
    result = search(dwmc, '0812')
    msg = result.get('msg', {})
    if isinstance(msg, dict):
        total = msg.get('totalCount', 0)
        items = msg.get('list', [])
        signs = [item.get('sign', '')[:8] for item in items[:3]]
        print(f'dwmc="{dwmc}" yjxkdm=0812: total={total}, signs={signs}')
    else:
        print(f'dwmc="{dwmc}": msg={msg}')
