"""Import CSV data into Spring Boot via multipart upload."""
import sys, json
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import io

CSV_PATH = 'data-collection/runs/cpeer_programs_import.csv'
API_URL = 'http://localhost:8080/api/v1/admin/imports/programs'

def upload_multipart(url, file_path, field_name='file'):
    boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    
    with open(file_path, 'rb') as f:
        file_data = f.read()
    
    body = bytearray()
    body.extend(f'--{boundary}\r\n'.encode())
    body.extend(f'Content-Disposition: form-data; name="{field_name}"; filename="cpeer_programs_import.csv"\r\n'.encode())
    body.extend(b'Content-Type: text/csv\r\n\r\n')
    body.extend(file_data)
    body.extend(f'\r\n--{boundary}--\r\n'.encode())
    
    headers = {
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body)),
    }
    
    req = Request(url, data=bytes(body), headers=headers, method='POST')
    with urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode('utf-8'))

print(f"Uploading {CSV_PATH} to {API_URL}...")
result = upload_multipart(API_URL, CSV_PATH)
print(json.dumps(result, ensure_ascii=False, indent=2))
