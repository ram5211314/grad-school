"""Scrape real admission data from USTC graduate school website."""
import json, sys, time, re
from urllib.request import Request, urlopen
from urllib.parse import urljoin

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
}

def fetch(url):
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        return resp.read().decode('utf-8', errors='replace'), resp.url

def extract_links(html, base_url):
    """Extract article links from page."""
    links = re.findall(r'href=["\']([^"\']+)["\']', html)
    results = []
    for link in links:
        full = urljoin(base_url, link)
        if '/column/' in full or '/article/' in full or '.do' in full:
            results.append(full)
    return list(set(results))

def extract_text(html):
    """Remove HTML tags and return plain text."""
    text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# 1. Fetch USTC main page and find links to admission data
print("Fetching USTC graduate school...", file=sys.stderr)
html, url = fetch('https://yz.ustc.edu.cn/')
links = extract_links(html, url)
print(f"Found {len(links)} links", file=sys.stderr)

# 2. Find pages about computer science admission
cs_keywords = ['计算机', '0812', '0854', '专业目录', '招生目录', '复试']
cs_links = []
for link in links[:30]:
    try:
        page_html, page_url = fetch(link)
        text = extract_text(page_html)
        matched = [kw for kw in cs_keywords if kw in text]
        if matched:
            cs_links.append({'url': link, 'text_preview': text[:200], 'keywords': matched})
            print(f"  Found relevant page: {link} (keywords: {matched})", file=sys.stderr)
        time.sleep(1)
    except Exception as e:
        pass

# 3. Try to find specific enrollment data
# Also try direct URLs for common pages
direct_urls = [
    'https://yz.ustc.edu.cn/lnzs',  # 历年招生
    'https://yz.ustc.edu.cn/zsml',  # 专业目录
]

for durl in direct_urls:
    try:
        page_html, page_url = fetch(durl)
        text = extract_text(page_html)
        print(f"\n{durl}: {len(text)} chars", file=sys.stderr)
        print(f"  Preview: {text[:300]}", file=sys.stderr)
    except Exception as e:
        print(f"  {durl}: {e}", file=sys.stderr)

print(json.dumps({'cs_links': cs_links}, ensure_ascii=False, indent=2))
