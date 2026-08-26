"""Download CPEER dataset."""
import json, urllib.request, ssl, os

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Get repository tree
url = 'https://api.github.com/repos/Younai2021/CPEER-Dataset/git/trees/main?recursive=1'
req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0', 'Accept': 'application/vnd.github.v3+json'})
resp = urllib.request.urlopen(req, timeout=30, context=ctx)
data = json.loads(resp.read().decode('utf-8'))

print("Files in repo:")
for item in data.get('tree', []):
    if item['path'].endswith(('.db', '.csv', '.xlsx', '.xls')):
        size = item.get('size', '?')
        print(f"  {item['path']} ({size} bytes)")

# Find the database or data file
for item in data.get('tree', []):
    if item['path'].endswith('.db'):
        dl_url = f"https://raw.githubusercontent.com/Younai2021/CPEER-Dataset/main/{item['path']}"
        print(f"\nDownloading {item['path']}...")
        req2 = urllib.request.Request(dl_url, headers={'User-Agent': 'Mozilla/5.0'})
        resp2 = urllib.request.urlopen(req2, timeout=60, context=ctx)
        db_data = resp2.read()
        out_path = f"data-collection/runs/{os.path.basename(item['path'])}"
        with open(out_path, 'wb') as f:
            f.write(db_data)
        print(f"Saved {len(db_data)} bytes to {out_path}")
        break
