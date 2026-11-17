# javelinre.com

Website for Javelin Residential. Vercel runs `python3 build.py` on every push and serves the generated `public/` folder.

- **Pages and copy:** `build.py` (layout and pages), `content.py` (services, address, links), `styles.css`, `main.js`
- **Blog posts:** one Markdown file per post in `content/insights/` (front matter: title, category, description, seo_title, date, slug). Posts dated in the future are skipped until a later build.
- **Contact form:** `api/contact.js` emails submissions via Resend (`RESEND_API_KEY`, optional `CONTACT_TO`)
- **Publishing API:** `api/posts.js` lets the Javelin Insights Writer GPT read status and publish posts (`PUBLISH_TOKEN`, `GITHUB_TOKEN`)

Build locally: `python3 build.py` (add `--preview` for a relative-link copy in `dist/`).
