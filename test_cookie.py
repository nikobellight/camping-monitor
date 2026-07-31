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

    # Collect all unique site types and loops
    site_types = {}
    for site_id, site in campsites.items():
        st = site.get('campsite_type', 'UNKNOWN')
        site_types[st] = site_types.get(st, 0) + 1

    p("  → Types de sites uniques (site_type: nombre de sites):")
    for st, count in sorted(site_types.items(), key=lambda x: -x[1]):
        p(f"     {st}: {count}")

    # Count availability across the WHOLE month per site_type (any date available)
    p("  → Disponibilité sur tout le mois d'août, par type de site:")
    type_avail_any = {}
    for site_id, site in campsites.items():
        st = site.get('campsite_type', 'UNKNOWN')
        avail = site.get('availabilities', {})
        has_any = any(status == 'Available' for status in avail.values())
        if has_any:
            type_avail_any[st] = type_avail_any.get(st, 0) + 1
    if type_avail_any:
        for st, count in type_avail_any.items():
            p(f"     {st}: {count} site(s) avec au moins 1 nuit dispo en août")
    else:
        p("     Aucune disponibilité trouvée en août pour aucun type")
else:
    p(f"  → Erreur: {r.text[:500]}")

p("Done!")
