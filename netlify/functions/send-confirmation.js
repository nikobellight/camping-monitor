exports.handler = async function(event) {
  if (event.httpMethod !== 'POST') {
    return { statusCode: 405, body: 'Method Not Allowed' };
  }

  try {
    const payload = JSON.parse(event.body);
    const { email, park_name, arrival_date, nights, plan, site_types, cancel_token, expires_at } = payload;

    console.log('Sending email to:', email);
    console.log('RESEND_API_KEY present:', !!process.env.RESEND_API_KEY);
    console.log('RESEND_API_KEY starts with:', process.env.RESEND_API_KEY?.substring(0, 10));

    const planWeeks = { basic: 4, standard: 8, premium: 16 };
    const weeks = planWeeks[plan] || 4;
    const siteDesc = Array.isArray(site_types) ? site_types.join(', ') : site_types;
    const cancelUrl = `https://campsitealert.com/cancel?token=${cancel_token}`;

    const html = `<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;">
      <div style="background:#2C4A3E;padding:24px;border-radius:12px 12px 0 0;">
        <h1 style="color:#F2E8D5;margin:0;font-size:22px;">🏕 Alert confirmed!</h1>
      </div>
      <div style="background:#F9F6F0;padding:32px;border-radius:0 0 12px 12px;">
        <p style="font-size:16px;color:#2C4A3E;">We're now watching <strong>${park_name}</strong> for you.</p>
        <table style="width:100%;border-collapse:collapse;margin:24px 0;">
          <tr><td style="padding:8px 0;color:#8B5E3C;font-weight:bold;">Park</td><td>${park_name}</td></tr>
          <tr><td style="padding:8px 0;color:#8B5E3C;font-weight:bold;">Arrival</td><td>${arrival_date}</td></tr>
          <tr><td style="padding:8px 0;color:#8B5E3C;font-weight:bold;">Nights</td><td>${nights}</td></tr>
          <tr><td style="padding:8px 0;color:#8B5E3C;font-weight:bold;">Site types</td><td>${siteDesc}</td></tr>
          <tr><td style="padding:8px 0;color:#8B5E3C;font-weight:bold;">Plan</td><td>${plan} (${weeks} weeks)</td></tr>
          <tr><td style="padding:8px 0;color:#8B5E3C;font-weight:bold;">Monitoring until</td><td>${expires_at}</td></tr>
        </table>
        <a href="${cancelUrl}" style="font-size:13px;color:#8B5E3C;">✅ Cancel my alert</a>
      </div>
    </div>`;

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        from: 'CampSiteAlert <alerts@campsitealert.com>',
        to: [email],
        subject: `🏕 Alert set — we're watching ${park_name} for you`,
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
