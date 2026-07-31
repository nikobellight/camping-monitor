import requests
import json
import sys
import time

def p(msg):
    print(msg, flush=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://www.reservecalifornia.com',
    'Referer': 'https://www.reservecalifornia.com/',
}

URL = 'https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/search/place'

# Search broader range - print ALL valid park names found
candidates = list(range(550, 750))

p("Searching for Malibu Creek State Park PlaceId...")
p("Printing all valid parks found in range 550-750:")

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
            if name:
                p(f"  PlaceId {place_id} → {name}")
                if 'malibu' in name.lower() or 'creek' in name.lower():
                    p(f"*** FOUND MALIBU CREEK! PlaceId: {place_id} ***")
    except Exception as e:
        pass
    time.sleep(0.2)

p("Done!")
