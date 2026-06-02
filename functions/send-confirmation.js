export async function onRequestPost(context) {
  try {
    const payload = await context.request.json();
    const { email, park_name, arrival_date, nights, plan, site_types, cancel_token, expires_at, all_parks } = payload;

    const planWeeks = { basic: 4, standard: 8, premium: 16 };
    const planParksCount = { basic: 1, standard: 2, premium: 3 };
    const weeks = planWeeks[plan] || 4;
    const parksCount = planParksCount[plan] || 1;
    const cancelUrl = `https://campsitealert.com/cancel?token=${cancel_token}`;

    const arrivalFormatted = new Date(arrival_date + 'T12:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    const expiresFormatted = new Date(expires_at + 'T12:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

    const today = new Date();
    const arrival = new Date(arrival_date + 'T12:00:00');
    const daysUntil = Math.ceil((arrival - today) / (1000 * 60 * 60 * 24));
    let checkSpeed = 'Every 15 min';
    if (daysUntil < 14) checkSpeed = 'Every 5 min';
    else if (daysUntil < 28) checkSpeed = 'Every 10 min';

    let parkRows = '';
    if (all_parks && all_parks.length > 1) {
      all_parks.forEach((p, i) => {
        const types = Array.isArray(p.site_types) ? p.site_types.join(' · ') : p.site_types;
        parkRows += `
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;width:140px;border-bottom:1px solid #EDE8DF;">Park ${i+1}</td>
            <td style="padding:10px 0;color:#2C4A3E;font-size:14px;font-weight:600;border-bottom:1px solid #EDE8DF;">${p.park_name}</td>
          </tr>
          <tr>
            <td style="padding:4px 0 10px 0;color:#8B5E3C;font-size:12px;border-bottom:1px solid #EDE8DF;"></td>
            <td style="padding:4px 0 10px 0;color:#5C7A6E;font-size:13px;border-bottom:1px solid #EDE8DF;">${types}</td>
          </tr>`;
      });
    } else {
      const siteDesc = Array.isArray(site_types) ? site_types.join(' · ') : site_types;
      parkRows = `
        <tr>
          <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;width:140px;border-bottom:1px solid #EDE8DF;">Park</td>
          <td style="padding:10px 0;color:#2C4A3E;font-size:14px;font-weight:600;border-bottom:1px solid #EDE8DF;">${park_name}</td>
        </tr>
        <tr>
          <td style="padding:4px 0 10px 0;color:#8B5E3C;font-size:12px;border-bottom:1px solid #EDE8DF;"></td>
          <td style="padding:4px 0 10px 0;color:#5C7A6E;font-size:13px;border-bottom:1px solid #EDE8DF;">${siteDesc}</td>
        </tr>`;
    }

    const firstName = all_parks ? all_parks[0].park_name : park_name;
    
    // Real count from Supabase
    let peopleCount = 0;
    try {
      const countRes = await fetch(
        `${context.env.SUPABASE_URL}/rest/v1/alerts?park_name=eq.${encodeURIComponent(firstName)}&arrival_date=eq.${arrival_date}&active=eq.true&select=id`,
        {
          headers: {
            'apikey': context.env.SUPABASE_SERVICE_KEY,
            'Authorization': `Bearer ${context.env.SUPABASE_SERVICE_KEY}`,
            'Prefer': 'count=exact',
          }
        }
      );
      const countHeader = countRes.headers.get('content-range');
      peopleCount = countHeader ? parseInt(countHeader.split('/')[1]) || 0 : 0;
    } catch(e) {
      peopleCount = 0;
    }

    const html = `<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F2E8D5;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">
    <div style="background:#2C4A3E;border-radius:16px 16px 0 0;padding:28px 32px;">
      <div style="font-size:13px;color:#7CC8A0;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">CampSiteAlert</div>
      <div style="font-size:13px;color:#A8C5B5;">alerts@campsitealert.com</div>
    </div>
    <div style="background:#FFF3EE;padding:12px 32px;border-left:4px solid #D4622A;">
      <span style="font-size:13px;color:#2C4A3E;font-weight:400;">Subject: <span style="color:#D4622A;font-weight:700;">✅ Your alert is active</span> — ${park_name}, ${arrivalFormatted}</span>
    </div>
    <div style="background:#ffffff;padding:36px 32px;border-radius:0 0 16px 16px;box-shadow:0 4px 24px rgba(44,74,62,0.08);">
      <h1 style="font-size:26px;color:#2C4A3E;margin:0 0 8px 0;">You're all set! 🏕</h1>
      <p style="font-size:15px;color:#5C7A6E;margin:0 0 28px 0;">We're now monitoring <strong>${park_name}</strong> on your behalf. Here's a summary of your alert:</p>
      <div style="background:#F9F6F0;border-radius:12px;padding:24px;margin-bottom:24px;">
        <table style="width:100%;border-collapse:collapse;">
          ${parkRows}
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Arrival date</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">${arrivalFormatted}</td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Nights</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">${nights} night${nights > 1 ? 's' : ''}</td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Plan</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">${plan.charAt(0).toUpperCase() + plan.slice(1)} — ${parksCount} park${parksCount > 1 ? 's' : ''} · ${weeks} weeks (${Math.round(weeks / 4)} month${weeks > 4 ? 's' : ''})</td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Monitoring until</td><td style="padding:10px 0;font-size:14px;border-bottom:1px solid #EDE8DF;"><span style="color:#2C7A4E;font-weight:600;">${expiresFormatted} (day before arrival)</span></td></tr>
          <tr><td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;">Current check speed</td><td style="padding:10px 0;color:#2C4A3E;font-size:14px;">${checkSpeed} → escalates automatically</td></tr>
        </table>
      </div>
      ${peopleCount > 0 ? `<div style="background:#FFF8F0;border-radius:12px;padding:16px 20px;margin-bottom:24px;font-size:14px;color:#5C7A6E;line-height:1.6;">👥 <strong style="color:#D4622A;">${peopleCount} people</strong> are currently monitoring <strong>${firstName}</strong> for similar dates — have your park account ready to book fast.</div>` : ''}
      <div style="background:#F9F6F0;border-radius:12px;padding:20px 24px;margin-bottom:24px;text-align:center;">
        <p style="margin:0 0 12px 0;font-size:14px;color:#5C7A6E;">Already found a spot another way?</p>
        <a href="${cancelUrl}" style="display:inline-block;background:#ffffff;border:2px solid #2C4A3E;color:#2C4A3E;padding:10px 24px;border-radius:100px;text-decoration:none;font-size:14px;font-weight:600;">✅ I booked it — stop my alerts</a>
      </div>
      <div style="font-size:13px;color:#5C7A6E;line-height:1.8;">
        <div style="margin-bottom:6px;">⚡ Check speed escalates automatically as your arrival date approaches</div>
        <div style="margin-bottom:6px;">🔴 Alerts stop when you click "I booked it" or on your arrival date</div>
        <div>🔵 If plan expires before arrival with no spot found, we'll notify you with an option to renew</div>
      </div>
    </div>
    <div style="text-align:center;padding:20px;font-size:12px;color:#8B5E3C;">
      CampSiteAlert · Not affiliated with California State Parks or any county park system
    </div>
  </div>
</body>
</html>`;

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${context.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'CampSiteAlert <alerts@campsitealert.com>',
        to: [email],
        subject: `✅ Your alert is active — ${park_name}, ${arrivalFormatted}`,
        html,
      }),
    });

    const data = await res.json();
    return new Response(JSON.stringify(data), {
      status: res.status,
      headers: { 'Content-Type': 'application/json' }
    });

  } catch(e) {
    return new Response(JSON.stringify({ error: e.message }), {
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}
