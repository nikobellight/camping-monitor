import requests
import json
import sys

def p(msg):
    print(msg, flush=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Content-Type': 'application/json',
    'Origin': 'https://www.reservecalifornia.com',
    'Referer': 'https://www.reservecalifornia.com/park/670',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'en-US,en;q=0.9',
}

URL = 'https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/search/place'

p("Testing PlaceId 670 (Malibu Creek State Park)...")

payload = {
    "PlaceId": 670,
    "StartDate": "2026-08-15",
    "Nights": 2,
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
    "InSeasonOnly": False,
    "ShowNearby": False
}

r = requests.post(URL, headers=headers, json=payload, timeout=15)
p(f"Status: {r.status_code}")
p(f"Response length: {len(r.text)}")
p(f"Response: {r.text[:3000]}")
