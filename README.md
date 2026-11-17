# javelinre.com

Website for Javelin Residential. Static site deployed on Vercel.

- Pages: HTML files at the root, `services/`, `insights/`
- Contact form: `api/contact.js` (Vercel function, sends email via Resend; needs `RESEND_API_KEY`)
- `vercel.json`: clean URLs and caching
