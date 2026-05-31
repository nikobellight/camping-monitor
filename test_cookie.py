import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'Origin': 'https://santabarbara.camava.com',
    'Referer': 'https://santabarbara.camava.com/reservation/camping/index.asp',
    'X-Requested-With': 'XMLHttpRequest'
}

data = {
    'parent_idno': '2',
    'selected_idno': '2',
    'arrive_date': '07/04/2026',
    'depart_date': '07/05/2026',
    'cust_type_idno': '0',
    'isBuilder': '1',
    'typeUrl': 'camping',
    'showsites': 'Y'
}

response = requests.post('https://santabarbara.camava.com/reservation/getresults.asp', headers=headers, data=data)
result = json.loads(response.text)

print("ALL REASON CODES AT JALAMA:")
for site in result['jsonPadicons']:
    print(f"  {site['short_label']} — reason_code: '{site['reason_code']}' — type: {site['type_name']}", flush=True)
