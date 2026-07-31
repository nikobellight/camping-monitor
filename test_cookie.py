import requests
import json

def p(msg):
    print(msg, flush=True)

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

FACILITY_ID = 232250  # Serrano Campground, San Bernardino National Forest

# Recreation.gov returns a full month of availability per call
URL = f'https://www.recreation.gov/api/camps/availability/campground/{FACILITY_ID}/month'
params = {'start_date': '2026-08-01T00:00:00.000Z'}

r = requests.get(URL, headers=headers, params=params, timeout=15)
p(f"Serrano (Facility {FACILITY_ID}): Status {r.status_code} | Length {len(r.text)}")

if r.status_code == 200:
    data = r.json()
    campsites = data.get('campsites', {})
    p(f"  → Nombre de sites trouvés: {len(campsites)}")

    # Show first site's structure as a sample
    if campsites:
        first_id = next(iter(campsites))
        first = campsites[first_id]
        p(f"  → Exemple site ID {first_id}:")
        p(f"     site_type: {first.get('campsite_type')}")
        p(f"     loop: {first.get('loop')}")
        avail = first.get('availabilities', {})
        # Print a few sample dates
        sample_dates = list(avail.items())[:5]
        for date, status in sample_dates:
            p(f"     {date}: {status}")

    # Count how many sites are Available on Aug 15 as a test
    test_date = '2026-08-15T00:00:00Z'
    available_count = 0
    for site_id, site in campsites.items():
        status = site.get('availabilities', {}).get(test_date)
        if status == 'Available':
            available_count += 1
    p(f"  → Sites disponibles le {test_date}: {available_count}")
else:
    p(f"  → Erreur: {r.text[:500]}")

p("Done!")
