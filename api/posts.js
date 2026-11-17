// Javelin Insights publishing API (used by the "Javelin Insights Writer" custom GPT).
//   GET  /api/posts  -> categories, recent posts, and the next category in the weekly rotation
//   POST /api/posts  -> publishes a post: commits content/insights/YYYY-MM-DD-slug.md to GitHub;
//                       Vercel rebuilds and the post is live in about a minute.
// Environment variables (Vercel -> Settings -> Environment Variables):
//   PUBLISH_TOKEN  required  shared secret; the GPT sends it as "Authorization: Bearer <token>"
//   GITHUB_TOKEN   required  fine-grained GitHub token with Contents: Read and write on the repo
//   GITHUB_REPO    optional  default "ryanmoorehead-ah48/javelinre-website"
//   GITHUB_BRANCH  optional  default "main"
//   SITE_URL       optional  default "https://www.javelinre.com"

const crypto = require("crypto");

const CATEGORIES = [
  { id: "leadership", name: "Leadership" },
  { id: "technology", name: "Technology" },
  { id: "affordable-housing", name: "Affordable Housing" },
  { id: "quick-tips", name: "Best Practices & Quick Tips" },
  { id: "mena", name: "Emerging Markets: MENA" },
];
const ORDER = CATEGORIES.map(c => c.id);
const DIR = "content/insights";

function authorized(req) {
  const expected = process.env.PUBLISH_TOKEN || "";
  const got = (req.headers.authorization || "").replace(/^Bearer\s+/i, "");
  if (!expected || !got) return false;
  const a = Buffer.from(expected), b = Buffer.from(got);
  return a.length === b.length && crypto.timingSafeEqual(a, b);
}

function gh(path, opts = {}) {
  const repo = process.env.GITHUB_REPO || "ryanmoorehead-ah48/javelinre-website";
  return fetch(`https://api.github.com/repos/${repo}/${path}`, {
    ...opts,
    headers: {
      Authorization: `Bearer ${process.env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "javelinre-publisher",
      "X-GitHub-Api-Version": "2022-11-28",
      ...(opts.headers || {}),
    },
  });
}

function todayNY() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "America/New_York", year: "numeric", month: "2-digit", day: "2-digit" }).format(new Date());
}

function slugify(s) {
  return String(s).toLowerCase().normalize("NFKD").replace(/[̀-ͯ]/g, "")
    .replace(/&/g, " and ").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 70).replace(/-+$/, "");
}

function q(s) { return '"' + String(s).replace(/\r?\n/g, " ").replace(/"/g, '\\"').trim() + '"'; }

async function listPosts() {
  const branch = process.env.GITHUB_BRANCH || "main";
  const r = await gh(`contents/${DIR}?ref=${branch}`);
  if (!r.ok) throw new Error(`GitHub list failed (${r.status})`);
  const files = (await r.json()).filter(f => f.name.endsWith(".md")).sort((a, b) => b.name.localeCompare(a.name)).slice(0, 12);
  const posts = await Promise.all(files.map(async f => {
    const fr = await gh(`contents/${DIR}/${f.name}?ref=${branch}`, { headers: { Accept: "application/vnd.github.raw+json" } });
    const text = fr.ok ? await fr.text() : "";
    const get = k => { const m = text.match(new RegExp(`^${k}:\\s*"?(.*?)"?\\s*$`, "m")); return m ? m[1] : ""; };
    return { file: f.name, date: get("date") || f.name.slice(0, 10), category: get("category"), title: get("title"), slug: get("slug") || f.name.slice(11, -3) };
  }));
  posts.sort((a, b) => (b.date + ORDER.indexOf(b.category)).localeCompare(a.date + ORDER.indexOf(a.category)) || ORDER.indexOf(b.category) - ORDER.indexOf(a.category));
  return posts;
}

function nextCategory(posts) {
  const last = posts.find(p => ORDER.includes(p.category));
  if (!last) return ORDER[0];
  return ORDER[(ORDER.indexOf(last.category) + 1) % ORDER.length];
}

module.exports = async function handler(req, res) {
  if (!authorized(req)) return res.status(401).json({ ok: false, error: "Unauthorized." });
  if (!process.env.GITHUB_TOKEN) return res.status(500).json({ ok: false, error: "GITHUB_TOKEN is not configured." });
  const site = (process.env.SITE_URL || "https://www.javelinre.com").replace(/\/$/, "");

  try {
    if (req.method === "GET") {
      const posts = await listPosts();
      const next = nextCategory(posts);
      return res.status(200).json({
        ok: true,
        categories: CATEGORIES,
        next_category: next,
        next_category_name: CATEGORIES.find(c => c.id === next).name,
        recent_posts: posts.map(p => ({ ...p, url: `${site}/insights/${p.slug}` })),
      });
    }

    if (req.method === "POST") {
      let d = req.body;
      if (typeof d === "string") { try { d = JSON.parse(d); } catch { d = {}; } }
      d = d || {};
      const errors = [];
      if (!d.title || String(d.title).length < 10) errors.push("title (10+ characters)");
      if (!ORDER.includes(d.category)) errors.push(`category (one of ${ORDER.join(", ")})`);
      if (!d.description || String(d.description).length < 50) errors.push("description (50-160 characters)");
      if (!d.body || String(d.body).length < 400) errors.push("body (Markdown, 400+ characters)");
      if (errors.length) return res.status(400).json({ ok: false, error: "Missing or invalid: " + errors.join("; ") });

      const date = todayNY();
      const slug = slugify(d.slug || d.title);
      if (!slug) return res.status(400).json({ ok: false, error: "Could not make a URL from the title." });
      const path = `${DIR}/${date}-${slug}.md`;
      const branch = process.env.GITHUB_BRANCH || "main";

      const exists = await gh(`contents/${path}?ref=${branch}`);
      if (exists.ok) return res.status(409).json({ ok: false, error: `A post with this title already exists today (${path}). Change the title or slug.` });

      const seo = d.seo_title && String(d.seo_title).length <= 60 ? d.seo_title : "";
      const md = ["---", `title: ${q(d.title)}`, `category: ${d.category}`, `description: ${q(String(d.description).slice(0, 160))}`,
        ...(seo ? [`seo_title: ${q(seo)}`] : []), `date: ${date}`, `slug: ${slug}`, "---", "", String(d.body).trim(), ""].join("\n");

      const put = await gh(`contents/${path}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: `Insights: ${String(d.title).slice(0, 72)}`,
          content: Buffer.from(md, "utf8").toString("base64"),
          branch,
          committer: { name: "Javelin Insights Writer", email: "info@javelinre.com" },
        }),
      });
      if (!put.ok) {
        console.error("GitHub commit failed", put.status, await put.text());
        return res.status(502).json({ ok: false, error: `GitHub commit failed (${put.status}). Check GITHUB_TOKEN permissions.` });
      }
      const commit = await put.json();
      return res.status(201).json({
        ok: true,
        status: "published",
        url: `${site}/insights/${slug}`,
        path,
        commit: commit.commit && commit.commit.html_url,
        note: "The site rebuilds automatically; the post is usually live within 1-2 minutes.",
      });
    }

    res.setHeader("Allow", "GET, POST");
    return res.status(405).json({ ok: false, error: "Use GET or POST." });
  } catch (err) {
    console.error(err);
    return res.status(500).json({ ok: false, error: err.message || "Unexpected error." });
  }
};
