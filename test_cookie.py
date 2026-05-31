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

systems = [
    {
        'name': 'Santa Barbara (santabarbara.camava.com)',
        'url': 'https://santabarbara.camava.com/reservation/getresults.asp',
        'origin': 'https://santabarbara.camava.com',
        'referer': 'https://santabarbara.camava.com/reservation/camping/index.asp',
        'park_ids': list(range(1, 30)) + [50, 100, 150, 200]
    },
    {
        'name': 'Santa Clara (gooutsideandplay.org)',
        'url': 'https://gooutsideandplay.org/reservation/getresults.asp',
        'origin': 'https://gooutsideandplay.org',
        'referer': 'https://gooutsideandplay.org/reservation/camping/index.asp',
        'park_ids': list(range(1, 30)) + [50, 100, 150, 200]
    },
    {
        'name': 'San Diego (parksres.sandiegocounty.gov)',
        'url': 'https://parksres.sandiegocounty.gov/reservation/getresults.asp',
        'origin': 'https://parksres.sandiegocounty.gov',
        'referer': 'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
        'park_ids': list(range(1, 30)) + [50, 100, 150, 200, 9494211, 9494212, 9494213, 9494214, 9494215, 9494216, 9494217, 9494218, 9494219, 9494220]
    }
]

for system in systems:
    print(f"\n{'='*60}")
    print(f"SYSTEM: {system['name']}")
    print(f"{'='*60}")
    
    h = headers_base.copy()
    h['Origin'] = system['origin']
    h['Referer'] = system['referer']
    
    found_parks = []
    
    for park_id in system['park_ids']:
        data = {
            'parent_idno': str(park_id),
            'selected_idno': str(park_id),
            'arrive_date': '07/04/2026',
            'depart_date': '07/05/2026',
            'cust_type_idno': '0',
            'isBuilder': '1',
            'typeUrl': 'camping',
            'showsites': 'Y'
        }
        
        try:
            response = requests.post(system['url'], headers=h, data=data, timeout=10)
            
            if response.status_code == 200 and len(response.text) > 100:
                try:
                    result = json.loads(response.text)
                    if 'jsonPadicons' in result and len(result['jsonPadicons']) > 0:
                        sites = result['jsonPadicons']
                        site_types = list(set([s.get('type_name', 'unknown') for s in sites]))
                        available = [s for s in sites if s.get('reason_code') not in ['Booked', 'Not Reservable Online', 'Closed', 'Unavailable']]
                        found_parks.append(park_id)
                        print(f"\n✅ PARK ID {park_id}:")
                        print(f"   Total sites: {len(sites)}")
                        print(f"   Site types: {site_types}")
                        print(f"   Available now: {len(available)}")
                        if available:
                            print(f"   Available sites: {[s.get('short_label') for s in available[:5]]}")
                except json.JSONDecodeError:
                    pass
        except Exception as e:
            print(f"Park ID {park_id}: error {e}")
        
        time.sleep(random.uniform(0.5, 1.5))
    
    print(f"\n📊 Summary for {system['name']}:")
    print(f"   Valid park IDs found: {found_parks}")

print("\n✅ Discovery complete!")
