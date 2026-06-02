import os
import json
import time
import random
import requests
from datetime import date, datetime, timedelta
import sys

def p(msg):
    print(msg, flush=True)
    sys.stdout.flush()

# ============================================================
# CONFIG
# ============================================================
SUPABASE_URL = os.environ.get('SUPABASE_URL')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')
RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
MODE = os.environ.get('CHECK_MODE', '15min')  # 15min, 10min, 5min, 8am

SITE_URL = 'https://campsitealert.com'
FROM_EMAIL = 'alerts@campsitealert.com'
ADMIN_EMAIL = 'nikobellight@gmail.com'

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
]

UNAVAILABLE_REASONS = [
    'Booked',
    'Not Reservable Online',
    'Not a Campsite',
    'First-Come, First-Served Site',
    'Site is Closed',
]

# ============================================================
# SUPABASE HELPERS
# ============================================================
def supabase_get(table, params={}):
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
        'Prefer': 'return=representation',
    }
    r = requests.get(f'{SUPABASE_URL}/rest/v1/{table}', headers=headers, params=params)
    p(f"Supabase GET status: {r.status_code}")
    if r.status_code != 200:
        p(f"Supabase GET error: {r.text[:200]}")
        return []
    return r.json()

def supabase_patch(table, match_params, data):
    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json',
    }
    r = requests.patch(f'{SUPABASE_URL}/rest/v1/{table}', headers=headers, params=match_params, json=data)
    return r.status_code

# ============================================================
# GET ACTIVE ALERTS FROM SUPABASE
# ============================================================
def get_active_alerts():
    today = date.today().isoformat()

    # Filter by arrival date proximity based on MODE
    result = supabase_get('alerts', {
        'active': 'eq.true',
        'expires_at': f'gte.{today}',
        'select': '*'
    })

    p(f"Supabase response type: {type(result)}")
    p(f"Supabase response: {str(result)[:200]}")

    # Handle error response
    if not isinstance(result, list):
        p(f"ERROR: Supabase returned unexpected response: {result}")
        return []

    if len(result) == 0:
        p("No active alerts in database.")
        return []

    if MODE == '8am':
        return [a for a in result if a.get('park_system') == 'reserve_california']

    filtered = []
    for alert in result:
        try:
            arrival = date.fromisoformat(alert['arrival_date'])
            days_until = (arrival - date.today()).days

            if MODE == '5min' and days_until <= 14:
                filtered.append(alert)
            elif MODE == '10min' and 14 < days_until <= 28:
                filtered.append(alert)
            elif MODE == '15min' and days_until > 28:
                filtered.append(alert)
        except Exception as e:
            p(f"Error processing alert {alert.get('id')}: {e}")

    return filtered

# ============================================================
# GROUP ALERTS BY UNIQUE PARK + DATE
# ============================================================
def group_alerts(alerts):
    groups = {}
    for alert in alerts:
        key = f"{alert['park_system']}|{alert['parent_idno']}|{alert['arrival_date']}|{alert['nights']}"
        if key not in groups:
            groups[key] = {
                'park_system': alert['park_system'],
                'park_name': alert['park_name'],
                'parent_idno': alert['parent_idno'],
                'arrival_date': alert['arrival_date'],
                'nights': alert['nights'],
                'customers': []
            }
        groups[key]['customers'].append(alert)
    return groups

# ============================================================
# API CALLS — COUNTY PARKS (Santa Barbara, Santa Clara, San Diego)
# ============================================================
COUNTY_URLS = {
    'santa_barbara': 'https://santabarbara.camava.com/reservation/getresults.asp',
    'santa_clara':   'https://gooutsideandplay.org/reservation/getresults.asp',
    'san_diego':     'parksres.sandiegocounty.gov/reservation/getresults.asp',
}
COUNTY_ORIGINS = {
    'santa_barbara': 'https://santabarbara.camava.com',
    'santa_clara':   'https://gooutsideandplay.org',
    'san_diego':     'https://parksres.sandiegocounty.gov',
}
COUNTY_REFERERS = {
    'santa_barbara': 'https://santabarbara.camava.com/reservation/camping/index.asp',
    'santa_clara':   'https://gooutsideandplay.org/reservation/camping/index.asp',
    'san_diego':     'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
}
COUNTY_BOOKING_URLS = {
    'santa_barbara': 'https://santabarbara.camava.com/reservation/camping/index.asp',
    'santa_clara':   'https://gooutsideandplay.org/reservation/camping/index.asp',
    'san_diego':     'https://parksres.sandiegocounty.gov/reservation/camping/index.asp',
}

def check_county_park(park_system, parent_idno, arrival_date, nights):
    url = COUNTY_URLS[park_system]
    arrive = datetime.strptime(arrival_date, '%Y-%m-%d')
    depart = arrive + timedelta(days=nights)

    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Origin': COUNTY_ORIGINS[park_system],
        'Referer': COUNTY_REFERERS[park_system],
    }
    data = {
        'parent_idno': parent_idno,
        'selected_idno': parent_idno,
        'arrive_date': arrive.strftime('%m/%d/%Y'),
        'depart_date': depart.strftime('%m/%d/%Y'),
        'cust_type_idno': '0',
        'isBuilder': '1',
        'typeUrl': 'camping',
        'showsites': 'Y',
    }

    try:
        r = requests.post(f'https://{url}' if not url.startswith('http') else url,
                         headers=headers, data=data, timeout=15)
        result = json.loads(r.text)
        sites = result.get('jsonPadicons', [])
        # Return available sites
        return [s for s in sites if s.get('reason_code', 'Booked') not in UNAVAILABLE_REASONS]
    except Exception as e:
        p(f"County park API error ({park_system}/{parent_idno}): {e}")
        return []

# ============================================================
# API CALLS — RESERVE CALIFORNIA
# ============================================================
RC_URL = 'https://california-rdr.prod.cali.rd12.recreation-management.tylerapp.com/rdr/search/place'
RC_BOOKING_URL = 'https://www.reservecalifornia.com/park/{place_id}'

def check_rc_park(place_id, arrival_date, nights):
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Content-Type': 'application/json',
        'Origin': 'https://www.reservecalifornia.com',
        'Referer': 'https://www.reservecalifornia.com/',
    }
    payload = {
        'PlaceId': int(place_id),
        'StartDate': arrival_date,
        'Nights': nights,
        'CountNearby': False,
        'NearbyLimit': 0,
        'CustomerID': '0',
        'UnitCategoryId': 0,
        'UnitTypeId': 0,
        'IsADA': False,
        'InSeasonOnly': True,
        'ShowNearby': False,
    }

    try:
        r = requests.post(RC_URL, headers=headers, json=payload, timeout=15)
        data = json.loads(r.text)
        selected = data.get('SelectedPlace', {})
        facilities = selected.get('Facilities', {})

        available_units = []
        for fac_id, facility in facilities.items():
            unit_types = facility.get('UnitTypes', {})
            for ut_id, ut in unit_types.items():
                if ut.get('Available'):
                    available_units.append({
                        'type_name': ut.get('Name', ''),
                        'unit_type_id': str(ut.get('UnitTypeId', '')),
                        'facility_name': facility.get('Name', ''),
                    })
        return available_units
    except Exception as e:
        p(f"RC API error ({place_id}): {e}")
        return []

# ============================================================
# MATCH AVAILABLE SITES TO CUSTOMER PREFERENCES
# ============================================================
def match_county(available_sites, customer_site_types):
    matched = []
    for site in available_sites:
        site_type = site.get('type_name', '')
        if any(st in site_type or site_type in st for st in customer_site_types):
            matched.append(site)
    return matched

def match_rc(available_units, customer_site_types):
    # customer_site_types for RC are comma-separated UnitTypeIds like '4303,4427,4328'
    matched = []
    allowed_ids = set()
    for st in customer_site_types:
        for tid in st.split(','):
            allowed_ids.add(tid.strip())

    for unit in available_units:
        if unit['unit_type_id'] in allowed_ids:
            matched.append(unit)
    return matched

# ============================================================
# SEND EMAIL VIA RESEND
# ============================================================
def send_alert_email(customer, park_name, park_system, available_sites, arrival_date, nights):
    if park_system == 'reserve_california':
        booking_url = RC_BOOKING_URL.format(place_id=customer['parent_idno'])
        site_desc = ', '.join(set([s['type_name'] for s in available_sites[:3]]))
    else:
        booking_url = COUNTY_BOOKING_URLS[park_system]
        site_desc = ', '.join(set([s.get('type_name', '') for s in available_sites[:3]]))

    cancel_url = f"{SITE_URL}/cancel?token={customer['cancel_token']}"
    detected_at = datetime.now().strftime('%B %d, %Y — %I:%M%p')

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
      <div style="background: #2C4A3E; padding: 24px; border-radius: 12px 12px 0 0;">
        <h1 style="color: #F2E8D5; margin: 0; font-size: 24px;">🏕 Spot Available!</h1>
      </div>
      <div style="background: #F9F6F0; padding: 32px; border-radius: 0 0 12px 12px;">
        <p style="font-size: 16px; color: #2C4A3E;">A campsite just opened up at <strong>{park_name}</strong> for your dates!</p>
        <table style="width: 100%; border-collapse: collapse; margin: 24px 0;">
          <tr><td style="padding: 8px 0; color: #8B5E3C; font-weight: bold;">Park</td><td style="padding: 8px 0;">{park_name}</td></tr>
          <tr><td style="padding: 8px 0; color: #8B5E3C; font-weight: bold;">Arrival</td><td style="padding: 8px 0;">{arrival_date}</td></tr>
          <tr><td style="padding: 8px 0; color: #8B5E3C; font-weight: bold;">Nights</td><td style="padding: 8px 0;">{nights}</td></tr>
          <tr><td style="padding: 8px 0; color: #8B5E3C; font-weight: bold;">Site type</td><td style="padding: 8px 0;">{site_desc}</td></tr>
          <tr><td style="padding: 8px 0; color: #8B5E3C; font-weight: bold;">Detected at</td><td style="padding: 8px 0;">{detected_at}</td></tr>
        </table>
        <a href="{booking_url}" style="display: block; background: #D4622A; color: white; text-align: center; padding: 16px; border-radius: 8px; text-decoration: none; font-size: 16px; font-weight: bold; margin: 24px 0;">→ Book Now</a>
        <p style="font-size: 13px; color: #8B5E3C;">We'll keep monitoring in case you miss this one.</p>
        <a href="{cancel_url}" style="font-size: 13px; color: #8B5E3C;">✅ I booked it — stop my alerts</a>
      </div>
    </div>
    """

    try:
        r = requests.post('https://api.resend.com/emails', 
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'from': f'CampSiteAlert <{FROM_EMAIL}>',
                'to': [customer['email']],
                'subject': f'🏕 Spot available! — {park_name}, {arrival_date}',
                'html': html,
            }
        )
        return r.status_code in (200, 201)
    except Exception as e:
        p(f"Email error: {e}")
        return False

def send_admin_notification(message):
    try:
        requests.post('https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'from': f'CampSiteAlert <{FROM_EMAIL}>',
                'to': [ADMIN_EMAIL],
                'subject': f'⚠️ CampSiteAlert Admin: {message}',
                'html': f'<p>{message}</p>',
            }
        )
    except:
        pass

# ============================================================
# MAIN
# ============================================================
def main():
    p(f"Starting CampSiteAlert monitor — MODE: {MODE}")
    p(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Get active alerts filtered by mode
    alerts = get_active_alerts()
    p(f"Active alerts to check: {len(alerts)}")

    if not alerts:
        p("No alerts to check. Exiting.")
        return

    # Group by unique park + date combo
    groups = group_alerts(alerts)
    p(f"Unique park/date combinations: {len(groups)}")

    alerts_sent = 0

    for key, group in groups.items():
        park_system = group['park_system']
        parent_idno = group['parent_idno']
        park_name = group['park_name']
        arrival_date = group['arrival_date']
        nights = group['nights']
        customers = group['customers']

        p(f"\nChecking: {park_name} ({arrival_date}, {nights} nights) — {len(customers)} customer(s)")

        # Make ONE API call for this park/date combo
        if park_system == 'reserve_california':
            available = check_rc_park(parent_idno, arrival_date, nights)
        else:
            available = check_county_park(park_system, parent_idno, arrival_date, nights)

        p(f"  Available sites: {len(available)}")

        if not available:
            time.sleep(random.uniform(2, 4))
            continue

        # Check each customer's site type preferences
        for customer in customers:
            site_types = customer.get('site_types', [])

            if park_system == 'reserve_california':
                matched = match_rc(available, site_types)
            else:
                matched = match_county(available, site_types)

            if matched:
                p(f"  MATCH for {customer['email']}! Sending alert...")
                sent = send_alert_email(customer, park_name, park_system, matched, arrival_date, nights)
                if sent:
                    alerts_sent += 1
                    # Update alerted_at in Supabase
                    supabase_patch('alerts', {'id': f"eq.{customer['id']}"}, {
                        'alerted_at': datetime.now().isoformat()
                    })
                    p(f"  Alert sent to {customer['email']} ✅")
                else:
                    p(f"  Failed to send alert to {customer['email']} ❌")

        # Anti-detection delay between park checks
        time.sleep(random.uniform(2, 4))

    p(f"\n{'='*50}")
    p(f"Done! Alerts sent: {alerts_sent}")

    # Admin notification at 8am run
    if MODE == '8am':
        send_admin_notification(f"8am RC check complete. {len(alerts)} alerts checked, {alerts_sent} alerts sent.")

if __name__ == '__main__':
    main()

# ============================================================
# NOTE ON PROMO CODES
# ============================================================
# Promo code users are stored in Supabase with:
#   plan = 'premium'
#   free_user = true
#   promo_code = 'CAMPING2026' (or similar)
# They get full Premium treatment — 3 parks, 16 weeks, all site types
# They are NOT counted in the 15 free user counter
# Script handles them identically to paid premium users
