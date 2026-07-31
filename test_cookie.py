import requests
import json
import sys

def p(msg):
    print(msg, flush=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://www.reservecalifornia.com',
    'Referer': 'https://www.reservecalifornia.com/',
}

URL = 'https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/search/place'

# Try a range of PlaceIds around likely numbers for Malibu Creek
# Known IDs: Leo Carrillo=665, Doheny=639, San Clemente=708
# Try IDs around these
candidates = list(range(650, 700)) + list(range(700, 750)) + [586, 587, 588, 589, 590]

p("Searching for Malibu Creek State Park PlaceId...")

for place_id in candidates:
    payload = {
        "PlaceId": place_id,
        "StartDate": "2026-08-01",
        "Nights": 1,
        "CountNearby": False,
        "NearbyLimit": 0,
        "CustomerID": "0",
        "UnitCategoryId": 0,
        "UnitTypeId": 0,
        "IsADA": False,
        "InSeasonOnly": True,
        "ShowNearby": False,
    }
    try:
        r = requests.post(URL, headers=headers, json=payload, timeout=10)
        if r.status_code == 200 and len(r.text) > 100:
            data = json.loads(r.text)
            name = data.get('SelectedPlace', {}).get('Name', '')
            if 'malibu' in name.lower() or 'creek' in name.lower():
                p(f"FOUND! PlaceId: {place_id} → Name: {name}")
                p(json.dumps(data.get('SelectedPlace', {}), indent=2)[:500])
                break
            elif name:
                p(f"  PlaceId {place_id} → {name}")
    except Exception as e:
        pass

p("Done!")
