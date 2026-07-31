import requests
import json
import random
import sys

def p(msg):
    print(msg, flush=True)

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
]

headers = {
    'User-Agent': random.choice(USER_AGENTS),
    'Content-Type': 'application/json',
    'Origin': 'https://www.reservecalifornia.com',
    'Referer': 'https://www.reservecalifornia.com/',
}

URL = 'https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/search/place'

# Test all RC parks including Malibu Creek
PARKS = [
    ('Leo Carrillo', 665),
    ('Carpinteria', 6),
    ('Doheny', 639),
    ('Malibu Creek', 670),
]

for name, pid in PARKS:
    payload = {
        'PlaceId': pid,
        'StartDate': '2026-08-15',
        'Nights': 2,
        'CountNearby': False,
        'NearbyLimit': 0,
        'CustomerID': '0',
        'UnitCategoryId': 0,
        'UnitTypeId': 0,
        'IsADA': False,
        'InSeasonOnly': True,
        'ShowNearby': False,
    }
    r = requests.post(URL, headers=headers, json=payload, timeout=15)
    p(f"{name} (PlaceId {pid}): Status {r.status_code} | Length {len(r.text)}")
    if r.status_code == 200:
        data = json.loads(r.text)
        pname = data.get('SelectedPlace', {}).get('Name', 'unknown')
        p(f"  → Name: {pname}")

p("Done!")
