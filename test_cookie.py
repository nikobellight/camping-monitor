import requests, json, random

USER_AGENTS = ['Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36']

FACILITY_ID = 10124502  # Azalea Campground, Sequoia & Kings Canyon NP
URL = f'https://www.recreation.gov/api/camps/availability/campground/{FACILITY_ID}/month'
r = requests.get(URL, headers={'User-Agent': random.choice(USER_AGENTS)}, params={'start_date': '2026-08-01T00:00:00.000Z'}, timeout=15)
print(f"Status: {r.status_code} | Length: {len(r.text)}")
if r.status_code == 200:
    data = r.json()
    campsites = data.get('campsites', {})
    print(f"Sites: {len(campsites)}")
    types = {}
    for s in campsites.values():
        t = s.get('campsite_type', 'UNKNOWN')
        types[t] = types.get(t, 0) + 1
    for t, c in types.items():
        print(f"  {t}: {c}")
