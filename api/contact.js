// Vercel serverless function: emails website form submissions to Ryan's inbox via Resend.
// Environment variables (set in Vercel → Project → Settings → Environment Variables):
//   RESEND_API_KEY  required  API key from resend.com
//   CONTACT_TO      optional  where submissions go (default ryan@javelinre.com)
//   CONTACT_FROM    optional  verified sender (default "Javelin Residential Website <website@javelinre.com>")

const MAX_FIELD = 5000;
const LABELS = {
  form: "Form", name: "Name", organization: "Organization", email: "Email", phone: "Phone",
  interest: "Interest", portfolio: "Portfolio size", event: "Event", date: "Event date",
  location: "Location", audience: "Audience", budget: "Honorarium / travel", times: "Preferred times",
  message: "Message", page: "Submitted from"
};

function escapeHtml(s) {
  return String(s).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

module.exports = async function handler(req, res) {
  if (req.method !== "POST") {
    res.setHeader("Allow", "POST");
    return res.status(405).json({ ok: false, error: "Use POST." });
  }

  let data = req.body;
  if (typeof data === "string") { try { data = JSON.parse(data); } catch { data = {}; } }
  data = data || {};

  // Spam checks: hidden honeypot field must be empty; form must take longer than 3 seconds to fill.
  if (data.company_website) return res.status(200).json({ ok: true });
  if (data.started && Date.now() - Number(data.started) < 3000) return res.status(200).json({ ok: true });

  const clean = {};
  for (const key of Object.keys(LABELS)) {
    if (data[key] != null && data[key] !== "") clean[key] = String(data[key]).slice(0, MAX_FIELD).trim();
  }
  if (!clean.name || !clean.email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(clean.email)) {
    return res.status(400).json({ ok: false, error: "Please include your name and a valid email address." });
  }

  const apiKey = process.env.RESEND_API_KEY;
  if (!apiKey) return res.status(500).json({ ok: false, error: "Email isn't configured yet. Please email info@javelinre.com." });

  const to = process.env.CONTACT_TO || "ryan@javelinre.com";
  const from = process.env.CONTACT_FROM || "Javelin Residential Website <website@javelinre.com>";
  const formName = clean.form || "Website inquiry";
  const subject = `${formName}: ${clean.name}${clean.organization ? " (" + clean.organization + ")" : ""}${clean.interest ? " - " + clean.interest : ""}`;

  const rows = Object.keys(LABELS).filter(k => clean[k]).map(k =>
    `<tr><td style="padding:6px 12px 6px 0;color:#566275;vertical-align:top;white-space:nowrap">${LABELS[k]}</td>` +
    `<td style="padding:6px 0;color:#16233A">${escapeHtml(clean[k]).replace(/\n/g, "<br>")}</td></tr>`).join("");
  const html = `<div style="font-family:Arial,sans-serif;font-size:15px">
    <h2 style="color:#0C418A;font-family:Georgia,serif;letter-spacing:.06em;text-transform:uppercase;font-weight:normal">${escapeHtml(formName)}</h2>
    <table style="border-collapse:collapse">${rows}</table>
    <p style="color:#566275;font-size:13px;margin-top:24px">Reply to this email to respond to ${escapeHtml(clean.name)} directly.</p></div>`;
  const text = Object.keys(LABELS).filter(k => clean[k]).map(k => `${LABELS[k]}: ${clean[k]}`).join("\n");

  try {
    const r = await fetch("https://api.resend.com/emails", {
      method: "POST",
      headers: { Authorization: `Bearer ${apiKey}`, "Content-Type": "application/json" },
      body: JSON.stringify({ from, to: [to], reply_to: clean.email, subject, html, text })
    });
    if (!r.ok) {
      console.error("Resend error", r.status, await r.text());
      return res.status(502).json({ ok: false, error: "We couldn't send your message. Please email info@javelinre.com." });
    }
    return res.status(200).json({ ok: true });
  } catch (err) {
    console.error("Send failed", err);
    return res.status(502).json({ ok: false, error: "We couldn't send your message. Please email info@javelinre.com." });
  }
};
