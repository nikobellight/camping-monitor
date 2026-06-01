import requests
import json
import sys

def p(msg):
    print(msg, flush=True)
    sys.stdout.flush()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://www.reservecalifornia.com',
    'Referer': 'https://www.reservecalifornia.com/',
}

PARKS = [
    {'name': 'Leo Carrillo State Beach', 'place_id': 665},
    {'name': 'Carpinteria State Beach',  'place_id': 6},
    {'name': 'El Capitan State Beach',   'place_id': 8},
    {'name': 'Doheny State Beach',       'place_id': 639},
    {'name': 'San Clemente State Beach', 'place_id': 708},
]

URL = 'https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/search/place'

p("Starting ReserveCalifornia site type discovery...")

for park in PARKS:
    p(f"\n{'='*50}")
    p(f"Park: {park['name']} (PlaceId: {park['place_id']})")

    payload = {
        "PlaceId": park['place_id'],
        "StartDate": "2026-08-01",
        "Nights": 1,
        "CountNearby": False,
        "NearbyLimit": 0,
        "CustomerID": "0",
        "UnitCategoryId": 0,
        "UnitTypeId": 0,
        "IsADA": False,
        "InSeasonOnly": True,
        "ShowNearby": False
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=15)
        data = json.loads(response.text)
        selected = data.get('SelectedPlace', {})
        facilities = selected.get('Facilities', [])

        p(f"Facilities count: {len(facilities)}")
        # Print full raw structure of first facility to understand it
        if facilities:
            p(f"First facility raw: {json.dumps(facilities[0], indent=2)[:2000]}")

    except Exception as e:
        p(f"ERROR: {e}")
        import traceback
        p(traceback.format_exc())

p("\nDone!")
