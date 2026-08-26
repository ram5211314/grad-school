"""Fetch program detail and find API endpoints."""
import sys, re
from urllib.request import Request, urlopen

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://yz.chsi.com.cn/zsml/',
}

def fetch_detail(sign):
    url = f'https://yz.chsi.com.cn/zsml/zydetail.do?sign={sign}'
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=30) as resp:
        raw = resp.read()
        text = raw.decode('utf-8', errors='replace')
        # Find API endpoints in JavaScript
        api_patterns = re.findall(r'["\'](/zsml/[^"\']+)["\']', text)
        ajax_patterns = re.findall(r'ajax[^)]*\(["\']([^"\']+)["\']', text)
        fetch_patterns = re.findall(r'fetch\(["\']([^"\']+)["\']', text)
        
        print('API patterns:')
        for p in set(api_patterns):
            print(f'  {p}')
        print('\nAjax patterns:')
        for p in set(ajax_patterns):
            print(f'  {p}')
        print('\nFetch patterns:')
        for p in set(fetch_patterns):
            print(f'  {p}')
        
        # Also look for script src
        scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', text)
        print('\nScript sources:')
        for s in scripts:
            print(f'  {s}')

sign = 'dcfb855900b3c8433e3773a4b0c455f2'
fetch_detail(sign)
