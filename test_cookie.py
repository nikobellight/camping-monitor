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

# Our 5 ReserveCalifornia parks
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
        "NearbyOnlyAvailable": False,
        "NearbyCountLimit": 10,
        "CustomerID": "0",
        "RefPlaceId": 0,
        "UnitCategoryId": 0,
        "UnitTypeId": 0,
        "UnitTypeName": "",
        "SleepingUnitId": 0,
        "MinVehicleLength": 0,
        "MaxVehicleLength": 0,
        "IsADA": False,
        "UnitSort": "orderby",
        "IsFiltered": False,
        "InSeasonOnly": True,
        "ShowNearby": False
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=15)
        p(f"Status: {response.status_code} | Length: {len(response.text)}")

        if response.status_code == 200:
            data = json.loads(response.text)

            # Get selected place info
            selected = data.get('SelectedPlace', {})
            p(f"Available: {selected.get('Available')} | Units: {selected.get('AvailableUnitCount')}")

            # Get all unit types from the response
            facilities = data.get('SelectedPlace', {}).get('Facilities', [])
            p(f"Facilities count: {len(facilities)}")

            unit_types = set()
            unit_type_ids = set()
            for facility in facilities:
                for unit in facility.get('Units', []):
                    unit_type = unit.get('UnitTypeName', '')
                    unit_type_id = unit.get('UnitTypeId', '')
                    if unit_type:
                        unit_types.add(unit_type)
                        unit_type_ids.add(f"{unit_type} (id:{unit_type_id})")

            p(f"Unit types found: {sorted(unit_type_ids)}")

            # Also check nearby places
            nearby = data.get('NearbyPlaces', [])
            p(f"Nearby places: {len(nearby)}")

            # Print raw first 500 chars to understand structure
            p(f"Raw response preview: {response.text[:800]}")

    except Exception as e:
        p(f"ERROR: {e}")

p("\nDone!")
