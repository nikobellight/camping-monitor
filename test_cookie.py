import requests
import json
import time
import random

headers_base = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Accept': 'application/json, text/javascript, */*; q=0.01',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'X-Requested-With': 'XMLHttpRequest'
}

PARKS = [
    # Santa Barbara Camava
    {'system': 'Santa Barbara', 'url': 'https://santabarbara.camava.com/reservation/getresults.asp',
     'origin': 'https://santabarbara.camava.com', 'referer': 'https://santabarbara.camava.com/reservation/camping/index.asp',
     'name': 'Cachuma Lake', 'parent_idno': '1'},
    {'system': 'Santa Barbara', 'url': 'https://santabarbara.camava.com/reservation/getresults.asp',
     'origin': 'https://santabarbara.camava.com', 'referer': 'https://santabarbara.camava.com/reservation/camping/index.asp',
     'name': 'Jalama Beach', 'parent_idno': '2'},

    # Santa Clara
    {'system': 'Santa Clara', 'url': 'https://gooutsideandplay.org/reservation/getresults.asp',
     'origin': 'https://gooutsideandplay.org', 'referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
     'name': 'Coyote Lake', 'parent_idno': '3'},
    {'system': 'Santa Clara', 'url': 'https://gooutsideandplay.org/reservation/getresults.asp',
     'origin': 'https://gooutsideandplay.org', 'referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
     'name': 'Joseph Grant Park', 'parent_idno': '6'},
    {'system': 'Santa Clara', 'url': 'https://gooutsideandplay.org/reservation/getresults.asp',
     'origin': 'https://gooutsideandplay.org', 'referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
     'name': 'Mt Madonna Park', 'parent_idno': '8'},
    {'system': 'Santa Clara', 'url': 'https://gooutsideandplay.org/reservation/getresults.asp',
     'origin': 'https://gooutsideandplay.org', 'referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
     'name': 'Sanborn', 'parent_idno': '9'},
    {'system': 'Santa Clara', 'url': 'https://gooutsideandplay.org/reservation/getresults.asp',
     'origin': 'https://gooutsideandplay.org', 'referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
     'name': 'Uvas Canyon Park', 'parent_idno': '12'},

    # San Diego
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Agua Caliente', 'parent_idno': '1'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Dos Picos', 'parent_idno': '2'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Guajome', 'parent_idno': '3'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Lake Morena', 'parent_idno': '5'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Potrero', 'parent_idno': '6'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Sweetwater', 'parent_idno': '7'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Tijuana River Valley', 'parent_idno': '9494211'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'Vallecito', 'parent_idno': '8'},
    {'system': 'San Diego', 'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
     'origin': 'https://parksres.sandiegocounty.gov', 'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
     'name': 'William Heise', 'parent_idno': '9'},
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
        if response.status_code == 200:
            result = json.loads(response.text)
            sites = result.get('jsonPadicons', [])
            # Filter only camping-related site types (exclude picnic, admin etc)
            camping_types = sorted(set([
                s.get('type_name', '')
                for s in sites
                if s.get('type_name') and
                any(k in s.get('type_name', '').lower() for k in ['camp', 'rv', 'hookup', 'tent', 'hike', 'yurt', 'cabin', 'non-hookup', 'caravan'])
            ]))
            print(f"\n{'='*50}")
            print(f"[{park['system']}] {park['name']} (ID: {park['parent_idno']})")
            print(f"Camping site types:")
            for t in camping_types:
                print(f"  - {t}")
        else:
            print(f"\n[{park['system']}] {park['name']}: status {response.status_code}")
    except Exception as e:
        print(f"\n[{park['system']}] {park['name']}: error {e}")

    time.sleep(random.uniform(1, 2))

print("\n✅ Done!")
