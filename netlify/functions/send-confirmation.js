exports.handler = async function(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const payload = JSON.parse(event.body);
    const { email, park_name, arrival_date, nights, plan, site_types, cancel_token, expires_at } = payload;

    console.log('Sending email to:', email);
    console.log('RESEND_API_KEY present:', !!process.env.RESEND_API_KEY);

    const planWeeks = { basic: 4, standard: 8, premium: 16 };
    const planParks = { basic: 1, standard: 2, premium: 3 };
    const weeks = planWeeks[plan] || 4;
    const parks = planParks[plan] || 1;
    const siteDesc = Array.isArray(site_types) ? site_types.join(' · ') : site_types;
    const cancelUrl = `https://campsitealert.com/cancel?token=${cancel_token}`;

    // Format arrival date nicely
    const arrivalFormatted = new Date(arrival_date + 'T12:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
    const expiresFormatted = new Date(expires_at + 'T12:00:00').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });

    // Determine check speed based on days until arrival
    const today = new Date();
    const arrival = new Date(arrival_date + 'T12:00:00');
    const daysUntil = Math.ceil((arrival - today) / (1000 * 60 * 60 * 24));
    let checkSpeed = 'Every 15 min';
    if (daysUntil < 14) checkSpeed = 'Every 5 min';
    else if (daysUntil < 28) checkSpeed = 'Every 10 min';

    const html = `<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0"></head>
<body style="margin:0;padding:0;background:#F2E8D5;font-family:Arial,sans-serif;">
  <div style="max-width:600px;margin:0 auto;padding:24px 16px;">

    <!-- Header -->
    <div style="background:#2C4A3E;border-radius:16px 16px 0 0;padding:28px 32px;">
      <div style="font-size:13px;color:#7CC8A0;font-weight:600;letter-spacing:1px;text-transform:uppercase;margin-bottom:8px;">CampSiteAlert</div>
      <div style="font-size:13px;color:#A8C5B5;">alerts@campsitealert.com</div>
    </div>

    <!-- Subject bar -->
    <div style="background:#E8F0EC;padding:12px 32px;border-left:4px solid #7CC8A0;">
      <span style="font-size:13px;color:#2C4A3E;font-weight:600;">Subject: ✅ Your alert is active — ${park_name}, ${arrivalFormatted}</span>
    </div>

    <!-- Main card -->
    <div style="background:#ffffff;padding:36px 32px;border-radius:0 0 16px 16px;box-shadow:0 4px 24px rgba(44,74,62,0.08);">
      
      <h1 style="font-size:26px;color:#2C4A3E;margin:0 0 8px 0;">You're all set! 🏕</h1>
      <p style="font-size:15px;color:#5C7A6E;margin:0 0 28px 0;">We're now monitoring <strong>${park_name}</strong> on your behalf. Here's a summary of your alert:</p>

      <!-- Summary box -->
      <div style="background:#F9F6F0;border-radius:12px;padding:24px;margin-bottom:24px;">
        <table style="width:100%;border-collapse:collapse;">
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;width:140px;border-bottom:1px solid #EDE8DF;">Park</td>
            <td style="padding:10px 0;color:#2C4A3E;font-size:14px;font-weight:600;border-bottom:1px solid #EDE8DF;">${park_name}</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Arrival date</td>
            <td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">${arrivalFormatted}</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Nights</td>
            <td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">${nights} night${nights > 1 ? 's' : ''}</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Site types</td>
            <td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">${siteDesc}</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Plan</td>
            <td style="padding:10px 0;color:#2C4A3E;font-size:14px;border-bottom:1px solid #EDE8DF;">${plan.charAt(0).toUpperCase() + plan.slice(1)} — ${parks} park${parks > 1 ? 's' : ''} · ${weeks} weeks (${Math.round(weeks / 4)} month${weeks > 4 ? 's' : ''})</td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;border-bottom:1px solid #EDE8DF;">Monitoring until</td>
            <td style="padding:10px 0;font-size:14px;border-bottom:1px solid #EDE8DF;"><span style="color:#D4622A;font-weight:600;">${expiresFormatted} (day before arrival)</span></td>
          </tr>
          <tr>
            <td style="padding:10px 0;color:#8B5E3C;font-size:13px;font-weight:600;">Current check speed</td>
            <td style="padding:10px 0;color:#2C4A3E;font-size:14px;">${checkSpeed} → escalates automatically</td>
          </tr>
        </table>
      </div>

      <!-- Cancel CTA -->
      <div style="background:#F9F6F0;border-radius:12px;padding:20px 24px;margin-bottom:24px;text-align:center;">
        <p style="margin:0 0 12px 0;font-size:14px;color:#5C7A6E;">Already found a spot another way?</p>
        <a href="${cancelUrl}" style="display:inline-block;background:#ffffff;border:2px solid #2C4A3E;color:#2C4A3E;padding:10px 24px;border-radius:100px;text-decoration:none;font-size:14px;font-weight:600;">✅ I booked it — stop my alerts</a>
      </div>

      <!-- Info bullets -->
      <div style="font-size:13px;color:#5C7A6E;line-height:1.8;">
        <div style="margin-bottom:6px;">⚡ Check speed escalates automatically as your arrival date approaches</div>
        <div style="margin-bottom:6px;">🔴 Alerts stop when you click "I booked it" or on your arrival date</div>
        <div>🔵 If plan expires before arrival with no spot found, we'll notify you with an option to renew</div>
      </div>

    </div>

    <!-- Footer -->
    <div style="text-align:center;padding:20px;font-size:12px;color:#8B5E3C;">
      CampSiteAlert · Not affiliated with California State Parks or any county park system
    </div>

  </div>
</body>
</html>`;

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
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
    console.log('Resend response status:', res.status);
    console.log('Resend response:', JSON.stringify(data));
    return { statusCode: res.status, body: JSON.stringify(data) };

  } catch(e) {
    console.log('Error:', e.message);
    return { statusCode: 500, body: JSON.stringify({ error: e.message }) };
  }
};
