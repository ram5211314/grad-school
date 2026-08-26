"""Full CHSI flow: get program list, then fetch per-program university details."""
import json, sys, time
from urllib.request import Request, urlopen
from urllib.parse import urlencode

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8',
    'Referer': 'https://yz.chsi.com.cn/zsml/',
    'X-Requested-With': 'XMLHttpRequest',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
}

def submit_query(params):
    data = urlencode(params).encode()
    req = Request('https://yz.chsi.com.cn/zsml/rs/zys.do', data=data, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode('utf-8'))

def fetch_detail_by_sign(sign):
    """Fetch the detail page for a specific program, then call ajaxRs.do to get university list."""
    # First load the detail page (this initializes the session/task)
    detail_url = f'https://yz.chsi.com.cn/zsml/zydetail.do?sign={sign}'
    req = Request(detail_url, headers={
        'User-Agent': HEADERS['User-Agent'],
        'Referer': 'https://yz.chsi.com.cn/zsml/',
    })
    with urlopen(req, timeout=30) as resp:
        resp.read()  # just load it
    
    time.sleep(1)
    
    # Now call ajaxRs.do with the sign to get university list
    data = urlencode({'sign': sign}).encode()
    req2 = Request('https://yz.chsi.com.cn/zsml/ajaxRs.do', data=data, headers=HEADERS)
    with urlopen(req2, timeout=30) as resp:
        raw = resp.read()
        if len(raw) <= 5:
            return None
        try:
            return json.loads(raw.decode('utf-8'))
        except:
            return json.loads(raw.decode('gbk'))

# First get program list for 0812
print("Step 1: Get 0812 program list...", file=sys.stderr)
result = submit_query({
    'dwmc': '', 'ssdm': '', 'yjxkdm': '0812', 'xxfs': '', 'mldm': '08', 'zymc': ''
})
msg = result.get('msg', {})
if not isinstance(msg, dict):
    print(f"Unexpected response: {result}", file=sys.stderr)
    sys.exit(1)

programs = msg.get('list', [])
total = msg.get('totalCount', 0)
print(f"Found {total} programs, got {len(programs)} from page 1", file=sys.stderr)

# Try to get university details for first few programs
all_data = []
for i, prog in enumerate(programs[:3]):
    sign = prog.get('sign', '')
    zydm = prog.get('zydm', '')
    zymc = prog.get('zymc', '')
    print(f"\nStep 2.{i+1}: Fetch universities for {zydm} {zymc} (sign={sign[:12]}...)", file=sys.stderr)
    
    try:
        detail = fetch_detail_by_sign(sign)
        if detail and 'msg' in detail:
            dmsg = detail['msg']
            if isinstance(dmsg, dict):
                unis = dmsg.get('list', [])
                print(f"  Got {len(unis)} universities", file=sys.stderr)
                for u in unis[:3]:
                    print(f"    {u.get('dwmc', '?')} - {u.get('ssmc', '?')}", file=sys.stderr)
                all_data.append({
                    'program': prog,
                    'universities': unis,
                    'total_universities': dmsg.get('totalCount', len(unis)),
                })
            else:
                print(f"  msg is not dict: {type(dmsg)}", file=sys.stderr)
        else:
            print(f"  No data returned", file=sys.stderr)
    except Exception as e:
        print(f"  Error: {e}", file=sys.stderr)
    
    time.sleep(2)

with open('data-collection/runs/chsi_detail_test.json', 'w', encoding='utf-8') as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)
print(f"\nSaved {len(all_data)} program details", file=sys.stderr)
