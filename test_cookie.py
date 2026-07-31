import requests
import json
import sys
import random

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

p("Testing PlaceId 670 (Malibu Creek) with same headers as monitor.py...")

payload = {
    'PlaceId': 670,
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
p(f"Status: {r.status_code}")
p(f"Response length: {len(r.text)}")
p(f"Response: {r.text[:3000]}")
