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
        # Print full raw response to understand structure
        p(f"Full response: {json.dumps(data, indent=2)[:3000]}")

    except Exception as e:
        p(f"ERROR: {e}")
        import traceback
        p(traceback.format_exc())

p("\nDone!")
