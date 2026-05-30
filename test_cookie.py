import requests

cookies = {
    'aws-waf-token': '58342482-7fe9-458b-8dfa-ffa263cde177:FAoAj3Iut6MbAAAA:UqUzB1C3dlIjbesOFKYimMcXGYyM0gkscs8qZll9cwR2FVCDFk/zfNKZA6gV/gVOwCUBSJrtLsxIhKmpmzKKpUL/tH1aWO9jNsbzBPCK7IVh8ZzJC49qi5WLVSdyBhZ3VG/sWf3Qm1ciO5QNzQh3w0XckNqxlQm3U1cLHU4EEBCkp/lfTi011WePFkaqOUp8gx2vFkxc8YCmJW/Ptuc0RHBhmy+GNS8Py+8Gw3C6FKvtaHBIP5FiNcUEGiqZgIPp+xb0z1xaFP6KlsqIWdw=',
    'AWSALB': 'Ccq5UCMJcou8fws1TInKH5mnbfxJmo8XUt+iwfeoPliL/lXv5VnODQicjBnWS68T9JFRd5tGropzrokuOfb3EE82TGFDx0u/AAvv7tB/+i7Sznt5dXGrsouSIw/e',
    'AWSALBCORS': 'Ccq5UCMJcou8fws1TInKH5mnbfxJmo8XUt+iwfeoPliL/lXv5VnODQicjBnWS68T9JFRd5tGropzrokuOfb3EE82TGFDx0u/AAvv7tB/+i7Sznt5dXGrsouSIw/e'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://secure.sonomacountyparks.org/camp/'
}

response = requests.get(
    'https://secure.sonomacountyparks.org/camp/',
    cookies=cookies,
    headers=headers
)

print(f"Status code: {response.status_code}")
print(f"Response length: {len(response.text)}")
print(f"First 500 chars: {response.text[:500]}")
