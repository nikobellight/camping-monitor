import requests

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://gooutsideandplay.org',
    'Referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
    'X-Requested-With': 'XMLHttpRequest'
}

data = {
    'parent_idno': '3',
    'selected_idno': '3',
    'arrive_date': '07/04/2026',
    'depart_date': '07/06/2026',
    'cust_type_idno': '0',
    'isBuilder': '1',
    'typeUrl': 'camping',
    'showsites': 'Y'
}

response = requests.post(
    'https://gooutsideandplay.org/reservation/getresults.asp',
    headers=headers,
    data=data
)

print(f"Status code: {response.status_code}")
print(f"Response length: {len(response.text)}")
print(f"First 1000 chars: {response.text[:1000]}")
