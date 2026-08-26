"""Scrape real admission data from multiple accessible university graduate school websites."""
import json, sys, time, re, hashlib
from urllib.request import Request, urlopen
from urllib.parse import urljoin, urlparse

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def fetch(url, referer=None):
    headers = {'User-Agent': USER_AGENT, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'}
    if referer:
        headers['Referer'] = referer
    req = Request(url, headers=headers)
    try:
        with urlopen(req, timeout=30) as resp:
            return resp.read(), resp.url, resp.headers.get_content_type()
    except Exception as e:
        return None, url, str(e)

def try_universities():
    """Try accessing several known accessible graduate school websites."""
    targets = [
        # ZJU
        ("浙江大学", "浙江", "http://grs.zju.edu.cn/yjszs/", [
            "http://grs.zju.edu.cn/yjszs/redir.php?catalog=1",
        ]),
        # SJTU
        ("上海交通大学", "上海", "https://yzb.sjtu.edu.cn/", [
            "https://yzb.sjtu.edu.cn/web/gs_list.html",
        ]),
        # USTC
        ("中国科学技术大学", "安徽", "https://yz.ustc.edu.cn/", [
            "https://yz.ustc.edu.cn/lnzs",
        ]),
        # HIT
        ("哈尔滨工业大学", "黑龙江", "https://yzb.hit.edu.cn/", [
            "https://yzb.hit.edu.cn/zsml/ssfxzy.php",
        ]),
        # NUDT
        ("国防科技大学", "湖南", "https://yjszs.nudt.edu.cn/", [
            "https://yjszs.nudt.edu.cn/",
        ]),
        # XJTU
        ("西安交通大学", "陕西", "https://yz.xjtu.edu.cn/", [
            "https://yz.xjtu.edu.cn/zsml/ss ml.asp",
        ]),
        # NWPU
        ("西北工业大学", "陕西", "https://yzb.nwpu.edu.cn/", [
            "https://yzb.nwpu.edu.cn/",
        ]),
        # SCU
        ("四川大学", "四川", "https://yz.scu.edu.cn/", [
            "https://yz.scu.edu.cn/zsml/queryAction.do",
        ]),
        # ZJU CS
        ("中南大学", "湖南", "https://gra.csu.edu.cn/", [
            "https://gra.csu.edu.cn/",
        ]),
    ]
    
    results = []
    for name, province, base_url, pages in targets:
        for page_url in pages:
            print(f'Trying {name}: {page_url}', file=sys.stderr)
            body, final_url, ctype = fetch(page_url)
            if body is None:
                print(f'  FAILED: {ctype}', file=sys.stderr)
                continue
            content = body.decode('utf-8', errors='replace')
            # Save snapshot
            slug = hashlib.sha256(page_url.encode()).hexdigest()[:12]
            snapshot_path = f'data-collection/runs/univ_{slug}.html'
            with open(snapshot_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            has_data = len(content) > 5000
            # Check for enrollment-related keywords
            keywords = ['招生', '复试', '录取', '计划', '分数线', '报名']
            found_kw = [kw for kw in keywords if kw in content]
            
            results.append({
                'name': name,
                'province': province,
                'url': page_url,
                'final_url': final_url,
                'status': 'SNAPSHOT' if has_data else 'MINIMAL',
                'size': len(content),
                'keywords_found': found_kw,
                'snapshot': snapshot_path,
            })
            print(f'  OK: {len(content)} bytes, keywords: {found_kw}', file=sys.stderr)
            time.sleep(2)
            break  # Only try first URL per university
    
    return results

if __name__ == '__main__':
    results = try_universities()
    print(json.dumps(results, ensure_ascii=False, indent=2))
    with open('data-collection/runs/university_scan.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
