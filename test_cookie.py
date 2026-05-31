import requests
import json
import time
import random
import sys

def p(msg):
    print(msg, flush=True)
    sys.stdout.flush()

headers_base = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}

PARKS = [
    {'system': 'Santa Barbara', 'url': 'https://santabarbara.camava.com/reservation/getresults.asp',
     'origin': 'https://santabarbara.camava.com', 'referer': 'https://santabarbara.camava.com/reservation/camping/index.asp',
     'name': 'Cachuma Lake', 'parent_idno': '1'},
    {'system': 'Santa Clara', 'url': 'https://gooutsideandplay.org/reservation/getresults.asp',
     'origin': 'https://gooutsideandplay.org', 'referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
     'name': 'Coyote Lake', 'parent_idno': '3'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Agua Caliente', 'parent_idno': '1'},
]

for park in PARKS:
    h = headers_base.copy()
    h['Origin'] = park['origin']
    h['Referer'] = park['referer']

    data = {
        'parent_idno': park['parent_idno'],
        'selected_idno': park['parent_idno'],
        'arrive_date': '07/04/2026',
        'depart_date': '07/05/2026',
        'cust_type_idno': '0',
        'isBuilder': '1',
        'typeUrl': 'camping',
        'showsites': 'Y'
    }

    try:
        response = requests.post(park['url'], headers=h, data=data, timeout=15)
        result = json.loads(response.text)
        sites = result.get('jsonPadicons', [])

        # Get all unique reason codes
        all_codes = set([s.get('reason_code', '') for s in sites])
        p(f"\n[{park['system']}] {park['name']} — all unique reason_codes:")
        for code in sorted(all_codes):
            p(f"  '{code}'")

        # Show non-booked sites specifically
        non_booked = [s for s in sites if s.get('reason_code') not in ['Booked', 'Not Reservable Online', 'Closed']]
        p(f"  Non-booked sites ({len(non_booked)}):")
        for s in non_booked[:10]:
            p(f"    {s['short_label']} — '{s['reason_code']}' — {s['type_name']}")

    except Exception as e:
        p(f"[{park['system']}] {park['name']}: ERROR {e}")

    time.sleep(random.uniform(1, 2))

p("\nDone!")
