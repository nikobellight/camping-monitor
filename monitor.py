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
    }
    r = requests.get(f'{SUPABASE_URL}/rest/v1/{table}', headers=headers, params=params)
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
    now = datetime.now()

    # Filter by arrival date proximity based on MODE
    alerts = supabase_get('alerts', {
        'active': 'eq.true',
        'expires_at': f'gte.{today}',
        'select': '*'
    })

    if MODE == '8am':
        # Only ReserveCalifornia parks
        return [a for a in alerts if a['park_system'] == 'reserve_california']

    filtered = []
    for alert in alerts:
        arrival = date.fromisoformat(alert['arrival_date'])
        days_until = (arrival - date.today()).days

        if MODE == '5min' and days_until <= 14:
            filtered.append(alert)
        elif MODE == '10min' and 14 < days_until <= 28:
            filtered.append(alert)
        elif MODE == '15min' and days_until > 28:
            filtered.append(alert)

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

# RC unit type ID to display label mapping
RC_TYPE_LABELS = {
    '4303': 'Standard Campsite',
    '4305': 'Standard Campsite',
    '4427': 'Standard Campsite',
    '4328': 'Tent Only Campsite',
    '4321': 'Hookup — Electric',
    '4322': 'Hookup — Electric + Water',
    '4324': 'Hookup — Full (E/W/S)',
    '4444': 'Hookup — Full (E/W/S)',
    '4320': 'Hike / Bike Campsite',
}

def match_rc(available_units, customer_site_types):
    # customer_site_types for RC are comma-separated UnitTypeIds like '4303,4427,4328'
    matched = []
    allowed_ids = set()
    for st in customer_site_types:
        for tid in st.split(','):
            allowed_ids.add(tid.strip())

    for unit in available_units:
        if unit['unit_type_id'] in allowed_ids:
            # Use our display label instead of API type name
            display_label = RC_TYPE_LABELS.get(unit['unit_type_id'], unit['type_name'])
            matched.append({**unit, 'type_name': display_label})
    return matched

# ============================================================
# SEND EMAIL VIA RESEND
# ============================================================
def send_alert_email(customer, park_name, park_system, available_sites, arrival_date, nights):
    if park_system == 'reserve_california':
        booking_url = RC_BOOKING_URL.format(place_id=customer['parent_idno'])
        booking_platform = 'ReserveCalifornia'
        site_desc = ', '.join(set([s['type_name'] for s in available_sites[:3]]))
    else:
        booking_url = COUNTY_BOOKING_URLS[park_system]
        platform_names = {
            'santa_barbara': 'Santa Barbara County Parks',
            'santa_clara': 'Santa Clara County Parks',
            'san_diego': 'San Diego County Parks',
        }
        booking_platform = platform_names.get(park_system, 'the park website')
        site_desc = ', '.join(set([s.get('type_name', '') for s in available_sites[:3]]))

    cancel_url = f"{SITE_URL}/cancel?token={customer['cancel_token']}"
    detected_at = datetime.now().strftime('%B %d, %Y — %I:%M %p')
    arrival_formatted = datetime.strptime(arrival_date, '%Y-%m-%d').strftime('%B %d, %Y')

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F2E8D5;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="background:#2C4A3E;border-radius:16px 16px 0 0;padding:28px 32px;">
      <div style="font-size:13px;color:#7CC8A0;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:4px;">CampSiteAlert</div>
      <div style="font-size:13px;color:rgba(242,232,213,0.5);">alerts@campsitealert.com</div>
    </div>
    <div style="background:#FFF3EE;padding:12px 32px;border-left:4px solid #D4622A;">
      <span style="font-size:13px;color:#2C4A3E;">Subject: <span style="color:#D4622A;font-weight:700;">🏕 Spot available!</span> — {park_name}, {arrival_formatted}</span>
    </div>
    <div style="background:#ffffff;padding:36px 32px;border-radius:0 0 16px 16px;box-shadow:0 4px 24px rgba(44,74,62,0.08);">
      <h1 style="font-size:26px;color:#2C4A3E;margin:0 0 8px 0;">A site just opened up! 🎉</h1>
      <p style="font-size:15px;color:#5C7A6E;margin:0 0 24px 0;">A <strong>{site_desc}</strong> just became available at <strong>{park_name}</strong> for your dates. Move fast — these spots go quickly!</p>
      <div style="background:#F9F6F0;border-radius:12px;padding:24px;margin-bottom:24px;">
        <table style="width:100%;border-collapse:collapse;">
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;width:140px;border-bottom:1px solid #EDE8DF;">Park</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;font-weight:600;border-bottom:1px solid #EDE8DF;">{park_name}</td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Date available</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">{arrival_formatted}</td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Nights</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">{nights}</td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Site type</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">{site_desc}</td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;">Detected at</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;">{detected_at}</td></tr>
        </table>
      </div>
      <a href="{booking_url}" target="_blank" style="display:block;background:#D4622A;color:white;text-align:center;padding:18px 32px;border-radius:100px;text-decoration:none;font-size:16px;font-weight:600;margin-bottom:8px;">→ Book now on {booking_platform}</a>
      <p style="font-size:11px;color:rgba(139,94,60,0.7);text-align:center;margin:0 0 24px 0;">Opens the park booking page — select your dates to complete your reservation.</p>
      <div style="background:#F9F6F0;border-radius:12px;padding:20px 24px;margin-bottom:20px;text-align:center;">
        <p style="margin:0 0 12px 0;font-size:14px;color:#5C7A6E;">Already booked your spot?</p>
        <a href="{cancel_url}" style="display:inline-block;background:#ffffff;border:2px solid #2C4A3E;color:#2C4A3E;padding:10px 24px;border-radius:100px;text-decoration:none;font-size:14px;font-weight:600;">✅ I booked it — stop my alerts</a>
      </div>
      <p style="font-size:13px;color:rgba(139,94,60,0.7);text-align:center;margin:0;">We'll keep monitoring in case you miss this one.</p>
    </div>
    <div style="text-align:center;padding:20px;font-size:12px;color:#8B5E3C;">CampSiteAlert · Not affiliated with California State Parks or any county park system</div>
  </div>
</body>
</html>"""

    try:
        r = requests.post('https://api.resend.com/emails',
            headers={
                'Authorization': f'Bearer {RESEND_API_KEY}',
                'Content-Type': 'application/json',
            },
            json={
                'from': f'CampSiteAlert <{FROM_EMAIL}>',
                'to': [customer['email']],
                'subject': f'🏕 Spot available! — {park_name}, {arrival_formatted}',
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
