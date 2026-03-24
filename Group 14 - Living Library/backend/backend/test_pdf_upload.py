import urllib.request
import os

with open("dummy.pdf", "wb") as f:
    f.write(b"dummy pdf content")

boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
file_path = 'dummy.pdf'

with open(file_path, 'rb') as f:
    file_data = f.read()

body = (
    f'--{boundary}\r\n'
    f'Content-Disposition: form-data; name="file"; filename="{os.path.basename(file_path)}"\r\n'
    f'Content-Type: application/pdf\r\n\r\n'
).encode() + file_data + f'\r\n--{boundary}--\r\n'.encode()

req = urllib.request.Request(
    'http://localhost:8000/api/ingest',
    data=body,
    headers={'Content-Type': f'multipart/form-data; boundary={boundary}'}
)

try:
    resp = urllib.request.urlopen(req, timeout=60)
    print('SUCCESS:', resp.read().decode())
except Exception as e:
    print('ERROR:', e)
    if hasattr(e, 'read'):
        print('DETAIL:', e.read().decode())
