import urllib.request, json

all_items = []
page = 0
while True:
    url = f'http://localhost:8080/api/v1/programs?page={page}&pageSize=100'
    req = urllib.request.Request(url)
    resp = urllib.request.urlopen(req, timeout=30)
    data = json.loads(resp.read().decode('utf-8'))
    items = data['items']
    all_items.extend(items)
    total = data['total']
    total_pages = data['totalPages']
    if page + 1 >= total_pages:
        break
    page += 1

with open('data-collection/runs/verify_result.txt', 'w', encoding='utf-8') as f:
    f.write(f'Total programs: {total}\n')
    f.write(f'Fetched: {len(all_items)}\n\n')
    
    years = {}
    provinces = {}
    levels = {}
    for item in all_items:
        y = item.get('admissionYear', 0)
        p = item.get('province', '未知')
        l = item.get('universityLevel', '未知')
        years[y] = years.get(y, 0) + 1
        provinces[p] = provinces.get(p, 0) + 1
        levels[l] = levels.get(l, 0) + 1
    
    f.write('By year:\n')
    for y in sorted(years.keys()):
        f.write(f'  {y}: {years[y]}\n')
    
    f.write('\nBy province:\n')
    for p, c in sorted(provinces.items(), key=lambda x: -x[1])[:15]:
        f.write(f'  {p}: {c}\n')
    
    f.write('\nBy level:\n')
    for l, c in sorted(levels.items(), key=lambda x: -x[1]):
        f.write(f'  {l}: {c}\n')
    
    f.write('\nSample records (first 30):\n')
    for item in all_items[:30]:
        f.write(f"  {item['universityName']} | {item['majorName']} | {item['province']} | {item['admissionYear']} | enrolled={item['actualEnrollment']} | registered={item['registrationCount']}\n")

print(f'Done. {len(all_items)} records verified.')
