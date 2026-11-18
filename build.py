"""Build javelinre.com in two modes:
   dist/      preview build (relative .html links) for the review artifact
   dist-prod/ production build for Vercel (clean URLs, absolute paths, sitemap, robots)"""
import json, os, shutil, html, datetime
from content import *

TODAY = datetime.date.today().isoformat()
E = html.escape

def cal(campaign, content):
    return f"{CAL}?utm_source=javelinre.com&utm_medium=website&utm_campaign={campaign}&utm_content={content}"

class Ctx:
    def __init__(s, mode, path):
        s.mode, s.path = mode, path              # path like "services/staffing" or "" for home
        s.depth = path.count("/")
    def L(s, p):                                  # link to a page path ("" = home, may include #hash)
        p, _, h = p.partition("#"); h = "#" + h if h else ""
        if s.mode == "prod": return ("/" + p if p else "/") + h
        return "../" * s.depth + (p or "index") + ".html" + h
    def A(s, f):                                  # static file
        return "/" + f if s.mode == "prod" else "../" * s.depth + f

ORG_ID = SITE + "/#org"
def org_schema():
    return {"@context":"https://schema.org","@type":"ProfessionalService","@id":ORG_ID,"name":"Javelin Residential","slogan":"Where Vision Takes Flight and Precision Hits the Mark.",
      "url":SITE+"/","logo":SITE+"/assets/javelin-residential-stacked.png","image":SITE+"/assets/og-image.png",
      "email":EMAIL,"address":{"@type":"PostalAddress","streetAddress":ADDRESS["street"],"addressLocality":ADDRESS["city"],"addressRegion":ADDRESS["region"],"postalCode":ADDRESS["zip"],"addressCountry":"US"},
      "areaServed":[{"@type":"Place","name":a} for a in AREA],
      "founder":{"@type":"Person","@id":SITE+"/leadership#ryan","name":"Ryan Moorehead"},
      "sameAs":[LINKEDIN, TOUGHLEAF],
      "description":"Property management, asset management and compliance, construction and construction management, procurement, staffing and organizational management for affordable and multifamily housing owners.",
      "hasOfferCatalog":{"@type":"OfferCatalog","name":"Services","itemListElement":[{"@type":"Offer","itemOffered":{"@type":"Service","name":v["name"],"url":f"{SITE}/services/{k}"}} for k,v in SERVICES.items()]}}

def crumbs_schema(items):
    return {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":i+1,"name":n,"item":SITE+("/"+p if p else "/")} for i,(n,p) in enumerate(items)]}

def faq_schema(faqs):
    return {"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
        {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]}

def head(c, title, desc, schemas, og_type="website"):
    canon = SITE + ("/" + c.path if c.path else "/")
    lds = "\n".join(f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>' for s in [org_schema()] + schemas)
    nav = lambda p, label: f'<li><a href="{c.L(p)}"{" aria-current=\"page\"" if c.path.split("/")[0]==p else ""}>{label}</a></li>'
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}">
<link rel="canonical" href="{canon}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="{og_type}">
<meta property="og:site_name" content="Javelin Residential">
<meta property="og:title" content="{E(title)}">
<meta property="og:description" content="{E(desc)}">
<meta property="og:url" content="{canon}">
<meta property="og:image" content="{SITE}/assets/og-image.png">
<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="US-NY"><meta name="geo.placename" content="New Rochelle">
<link rel="icon" type="image/png" sizes="32x32" href="{c.A('assets/javelin-icon-32.png')}">
<link rel="apple-touch-icon" href="{c.A('assets/javelin-icon-180.png')}">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=EB+Garamond:ital,wght@0,400;0,500;1,400&family=Public+Sans:wght@400;500;600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{c.A('styles.css')}">
<!-- Google Analytics 4 / Google Ads: paste the gtag.js snippet here with the site's G- and AW- IDs.
     main.js already pushes calendly_click, calendly_booked, email_click and form_submit events to dataLayer. -->
{lds}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<header class="site-header">
  <div class="wrap bar">
    <ul class="nav-l">{nav("services","Services")}{nav("capabilities","Capabilities")}{nav("leadership","Leadership")}{nav("speaking","Speaking")}</ul>
    <button class="menu-btn" aria-label="Menu" aria-expanded="false" aria-controls="mnav"><span></span><span></span><span></span></button>
    <a class="brand" href="{c.L('')}" aria-label="Javelin Residential home"><img src="{c.A('assets/javelin-residential-horizontal.png')}" alt="Javelin Residential" width="320" height="80"></a>
    <ul class="nav-r">{nav("coaching","Coaching")}{nav("insights","Insights")}<li><a href="{c.L('book#contact')}">Contact</a></li><li><a class="btn btn-solid" href="{c.L('book')}">Book a call</a></li></ul>
  </div>
  <ul class="mobile-nav" id="mnav">{nav("services","Services")}{nav("capabilities","Capabilities")}{nav("leadership","Leadership")}{nav("speaking","Speaking")}{nav("coaching","Coaching")}{nav("insights","Insights")}<li><a href="{c.L('book#contact')}">Contact</a></li><li><a class="btn btn-solid" href="{c.L('book')}">Book a call</a></li></ul>
</header>
<main id="main">
"""

def foot(c):
    return f"""</main>
<footer class="site-footer">
  <div class="wrap">
    <img class="logo" src="{c.A('assets/javelin-residential-stacked.png')}" alt="Javelin Residential" width="170" height="115">
    <p class="foot-tag">Innovative Real Estate Solutions<br><em>The Right Aim. The Perfect Trajectory. Exceptional Results.</em></p>
    <ul class="foot-nav">
      <li><a href="{c.L('services')}">Services</a></li><li><a href="{c.L('capabilities')}">Capabilities</a></li><li><a href="{c.L('leadership')}">Leadership</a></li>
      <li><a href="{c.L('speaking')}">Speaking</a></li><li><a href="{c.L('coaching')}">Coaching</a></li><li><a href="{c.L('insights')}">Insights</a></li><li><a href="{c.L('book')}">Book a call</a></li><li><a href="{LINKEDIN}" rel="me">LinkedIn</a></li><li><a href="{TOUGHLEAF}">Project portfolio</a></li>
    </ul>
    <address>{ADDRESS['street']}, {ADDRESS['city']}, {ADDRESS['region']} {ADDRESS['zip']}<br><a href="mailto:{EMAIL}">{EMAIL}</a></address>
    <div class="legal">&copy; <span id="yr">2026</span> Javelin Residential. Serving owners in New York City, Westchester and New Jersey. &middot; <a href="{c.L('privacy')}">Privacy policy</a></div>
  </div>
</footer>
<script src="{c.A('main.js')}"></script>
</body>
</html>
"""

def crumbs_html(c, items):
    parts = [f'<a href="{c.L(p)}">{E(n)}</a>' for n,p in items[:-1]] + [E(items[-1][0])]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"

def band(c, campaign, title="Start with a 15-minute call", text="Tell us about the property, the contract or the problem. If it's a fit, we'll scope it on the call."):
    return f"""<section class="band">
  <div class="wrap">
    <img class="mark" src="{c.A('assets/javelin-mark-white.png')}" alt="">
    <h2>{E(title)}</h2>
    <hr class="divider" style="background:#fff">
    <p class="narrow">{E(text)}</p>
    <div class="cta-row" style="margin-top:28px">
      <a class="btn btn-solid" href="{cal(campaign,'band')}" data-cta="band-calendly">Book a 15-minute call</a>
      <a class="btn btn-line" href="{c.L('capabilities#rfp')}">Send an RFP or scope</a>
    </div>
  </div>
</section>"""

def svc_link(c, k):
    s = SERVICES[k]
    return f'<a class="svc-link" href="{c.L("services/"+k)}"><h4>{E(s["name"])}</h4><p>{E(s["short"])}</p><span class="go">Learn more</span></a>'

def clients_block(c, tint=False):
    cells = "".join(f'<li>{E(n)}</li>' for n in CLIENTS)
    return f"""<section class="section{' tint' if tint else ''}" id="clients"><div class="wrap">
  <div class="head"><h2>Selected clients</h2><hr class="divider"><p class="lede">Owners, developers, investors and operators who have worked with Ryan and the Javelin team.</p></div>
  <ul class="clients">{cells}</ul>
</div></section>"""

EXPERTISE = [
  ("Residential expertise", [
    ("Affordable & multifamily operations", "Grew a NYC portfolio to 14,000+ affordable and market-rate units with 400+ employees",
     "Career highlight", "At GRC Management, Ryan grew the portfolio from 5,000 to more than 14,000 units in six years, rebuilding staffing, systems, compliance and reporting to carry a 400-person team."),
    ("LIHTC & HUD compliance", "Recertifications, file audits, MOR preparation and agency approvals",
     "What we do", "For a nonprofit affordable housing owner in Newark, NJ, Javelin runs LIHTC compliance and annual recertifications alongside asset management, staffing and written policies and procedures."),
    ("Large-scale restructuring", "Led the organizational restructuring of a complex urban community with 700+ employees",
     "From Ryan's background", "Ryan led the restructuring of a complex urban community: 700+ employees, 12,000+ apartments in two condominium structures with separate boards, a sponsor-led team, 500,000 SF of commercial and three parking garages."),
    ("Capital programs", "$100M+ in capital projects across redevelopment, renovation and modernization",
     "Career highlight", "Across his career, Ryan has led more than $100 million in capital work: redevelopment, apartment renovations and building-system modernization, including one renovation program delivered $3 million under budget."),
    ("Owners, agencies & nonprofits", "Housing authorities, community developers, investors and managing agents",
     "What we do", "For a Harlem affordable housing developer, Javelin prepared the managing-agent approval submission to the housing agency, from organizational documents to operating plans."),
  ]),
  ("Transferable skills", [
    ("Turnarounds & scaling", "Restructuring organizations and nearly tripling an operation's size without losing control",
     "From Ryan's background", "Ryan partnered with a 49-year-old management company to restructure and modernize it, then nearly tripled its size while keeping service, compliance and reporting on track."),
    ("Construction & procurement", "Scoping, bidding, contracting and delivering capital work in any built environment",
     "Outside real estate", "Ryan took Affogato House, a specialty coffee and gelato caf\u00e9 in New Rochelle, from raw space through design, contractor bids, construction, equipment and opening."),
    ("Organizational design & staffing", "Structure, policies, hiring and performance systems for teams of any size",
     "Career highlight", "Ryan rightsized a management company's staff from 160 to 100, built a clear reporting structure, job descriptions, training and an operations procedures manual, and made key hires that reset the culture."),
    ("Regulated programs & contracts", "Running operations that answer to auditors, lenders, agencies and boards",
     "From Ryan's background", "Ryan's portfolios have answered to HUD, state housing agencies, lenders, auditors and condominium boards, often all at once, with reporting built to satisfy each of them."),
    ("Technology & finance", "AI company founder; asset management and lending experience; P&L and capital stewardship",
     "From Ryan's background", "Ryan co-founded Arlo, an AI leasing and compliance platform for affordable housing. At First Sterling Financial he negotiated loans that cut non-performing assets."),
  ]),
]
def flip_tiles():
    out = ""
    for col, tiles in EXPERTISE:
        out += f'<h3 class="flip-head">{E(col)}</h3>'
        for t, front, label, back in tiles:
            out += (f'<button type="button" class="flip" aria-pressed="false" aria-label="{E(t)}: show example">'
                    f'<span class="flip-inner"><span class="face front"><strong>{E(t)}</strong><span class="txt">{E(front)}</span><span class="cue">See an example</span></span>'
                    f'<span class="face back" aria-hidden="true"><span class="label">{E(label)}</span><span class="txt">{E(back)}</span><span class="cue">Flip back</span></span></span></button>')
    return f'<div class="flipgrid">{out}</div>'

SAMPLES = [
  ("Management audit", "An operating review of a residential management company: options analysis with costs, then recommendations organized by function.",
   [("management-audit-options","Options and findings"),("management-audit-recommendations","Recommendations")]),
  ("Asset management report", "A quarterly owner report for a mixed residential and commercial portfolio: year-over-year financials, trend data and portfolio charts.",
   [("asset-report-financial-overview","Financial overview"),("asset-report-charts","Portfolio charts")]),
  ("Property management report", "A one-page monthly dashboard covering occupancy, leasing, A/R, staffing, work orders, violations and capital projects.",
   [("property-report-dashboard","Monthly dashboard")]),
]
def samples(c, heading="h2"):
    cards = ""
    for t, d, pages in SAMPLES:
        figs = "".join(f'<a class="sample-page" href="{c.A("assets/samples/"+f+".jpg")}" target="_blank" rel="noopener"><img src="{c.A("assets/samples/"+f+".jpg")}" alt="{E(t)}: {E(cap)} (sample, client details removed)" width="1275" height="1650" loading="lazy"><span>{E(cap)}</span></a>' for f, cap in pages)
        cards += f'<article class="sample"><div class="sample-pages n{len(pages)}">{figs}</div><h3>{E(t)}</h3><p>{E(d)}</p></article>'
    return f'''<section class="section" id="reporting">
  <div class="wrap">
    <div class="head"><{heading}>Reporting samples</{heading}><hr class="divider">
      <p class="lede">Owners and boards get reporting they can act on. These are excerpts from past work, with client names, properties and identifying details removed.</p></div>
    <div class="samples">{cards}</div>
  </div>
</section>'''

def pillars(c):
    out = []
    for name, sub, keys in PILLARS:
        out.append(f'<div class="pillar"><h3>{name}</h3><p>{E(sub)}</p>' + "".join(svc_link(c,k) for k in keys) + '</div>')
    return '<div class="pillars">' + "".join(out) + '</div>'

def contact_form(campaign):
    opts = "".join(f"<option>{E(v['name'])}</option>" for v in SERVICES.values())
    return f"""<form data-mail="Website inquiry ({campaign})">
  <div class="row"><label>Name<input name="name" autocomplete="name" required></label><label>Organization<input name="organization" autocomplete="organization"></label></div>
  <div class="row"><label>Email<input name="email" type="email" autocomplete="email" required></label><label>Phone<input name="phone" type="tel" autocomplete="tel"></label></div>
  <div class="row"><label>Service<select name="interest"><option value="">Choose one</option>{opts}<option>RFP / RFQ</option><option>Career coaching</option><option>Other</option></select></label>
  <label>Portfolio size<input name="portfolio" placeholder="e.g. 3 buildings, 420 units"></label></div>
  <label>What do you need?<textarea name="message" placeholder="Location, timeline, and any RFP or bid deadline"></textarea></label>
  <button class="btn btn-solid" type="submit">Send inquiry</button>
  <p class="form-note" role="status"></p>
</form>"""

# ---------------------------------------------------------------- pages
def p_home(c):
    posts = posts_html(c, 3)
    return head(c, "Javelin Residential | Innovative Real Estate Solutions",
      "Innovative real estate solutions: operations, compliance, construction, procurement and staffing for housing owners, plus turnaround and operating expertise for other industries.",
      []) + f"""
<section class="hero">
  <div class="wrap">
    <img class="mark" src="{c.A('assets/javelin-mark-navy.png')}" alt="" width="900" height="434">
    <p class="brandline">Javelin Residential</p>
    <p class="tagline">Innovative Real Estate Solutions</p>
    <h1>Where Vision Takes Flight<br> and Precision Hits the Mark.</h1>
    <p class="catch">The Right Aim. The Perfect Trajectory. Exceptional Results.</p>
    <hr class="divider">
    <div class="lede hero-copy">
      <p>Javelin Residential is a full-service real estate advisory and operations platform specializing in residential development, construction advisory, owner's representation, asset and property management, staffing, financial analysis, operations reporting and strategic consulting</p>
      <p>With deep expertise in affordable and multifamily housing, we partner with owners, investors, and organizations to optimize operations, maximize asset value, navigate complex challenges, and deliver measurable results</p>
      <p>From organizational restructuring and asset repositioning to market analysis, regulatory compliance, and operational transformation, Javelin combines strategic insight with hands-on execution to deliver targeted solutions</p>
      <p>Serving clients coast-to-coast and internationally, we bring precision to complex challenges and deliver results that go the distance</p>
    </div>    <div class="cta-row">
      <a class="btn btn-solid" href="{cal('home','hero')}" data-cta="hero-calendly">Book a 15-minute call</a>
      <a class="btn btn-line" href="{c.L('capabilities')}">View capability statement</a>
    </div>
    <div class="stats">
      <div><strong>14,000+ units</strong><span>affordable and market-rate portfolio grown and managed</span></div>
      <div><strong>$100M+ capital projects</strong><span>redevelopment, renovation and building-system modernization</span></div>
      <div><strong>20+ years</strong><span>in development, asset management and operations</span></div>
    </div>
  </div>
</section>

<section class="section" id="services">
  <div class="wrap">
    <div class="head"><h2>One team for everything a building needs</h2><hr class="divider">
      <p class="lede">Most owners coordinate a manager, a contractor, a staffing agency, a purchasing desk and a compliance consultant. Javelin runs those functions together, under one operating plan and one point of accountability.</p></div>
    {pillars(c)}
  </div>
</section>
<section class="section tint" id="expertise">
  <div class="wrap">
    <div class="head"><h2>Residential depth. Cross-industry reach.</h2><hr class="divider">
      <p class="lede">Two decades running some of New York's largest residential portfolios built skills that work in any organization with people, buildings, budgets and rules to answer to.</p></div>
    {flip_tiles()}
    <div class="head" style="margin:72px auto 28px"><h3>Industries we bring them to</h3></div>
    <ul class="clients industries">
      <li>Hospitality & food service</li><li>Commercial & mixed-use</li><li>Technology & startups</li>
      <li>Financial services</li><li>Public sector & nonprofits</li><li>Emerging markets: MENA</li>
    </ul>
  </div>
</section>

{samples(c)}

<section class="section">
  <div class="wrap">
    <div class="head"><h2>How an engagement runs</h2><hr class="divider">
      <p class="lede">We start with what's actually happening at the property and finish with a team and system that keep working after we step back.</p></div>
    <ol class="steps">
      <li><h3>Assess</h3><p>Site walkthroughs, file reviews, staffing and vendor audits to find what is costing you money.</p></li>
      <li><h3>Plan</h3><p>A prioritized operating plan with budget, milestones and a named owner for every item.</p></li>
      <li><h3>Execute</h3><p>We do the work: fill the roles, bid the vendors, run the construction, fix the files.</p></li>
      <li><h3>Sustain</h3><p>Policies, reporting and training that hold the gains, with ongoing oversight if you want it.</p></li>
    </ol>
  </div>
</section>

<section class="section">
  <div class="wrap leader">
    <div class="portrait"><img src="{c.A('assets/ryan-moorehead.jpg')}" alt="Ryan Moorehead, Founder of Javelin Residential" width="960" height="1200" loading="lazy"></div>
    <div>
      <h2>Leadership</h2>
      <p class="role">Ryan Moorehead, Founder &amp; Principal</p>
      <p>Ryan has spent more than twenty years running and repositioning residential real estate. As President of GRC Management from 2019 to 2025, he restructured a 49-year-old New York City management company and grew its portfolio from 5,000 to more than 14,000 affordable and market-rate units. Before that, he led the organizational restructuring of a 12,000+ apartment urban community with 700+ employees. Since 2013 he has been a real estate career coach at Columbia University.</p>
      <ul class="creds"><li>GlobeSt.com Top 50 Under 40 (2016)</li><li>MBA, Columbia Business School</li><li>B.S. Real Estate, NYU, magna cum laude</li><li>Member, REEC, NYREC and ULI</li></ul>
      <div class="cta-row" style="justify-content:flex-start"><a class="btn btn-line" href="{c.L('leadership')}">Read Ryan's bio</a><a class="btn btn-line" href="{c.L('speaking')}">Invite Ryan to speak</a></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="head"><h2>Insights, every week</h2><hr class="divider"><p class="lede">Practical notes on running affordable and multifamily housing.</p></div>
    {posts}
  </div>
</section>
{band(c,'home')}
""" + foot(c)

def p_services(c):
    items = [("Home",""),("Services","services")]
    return head(c, "Property, Asset & Construction Services | Javelin",
      "Property management, LIHTC and HUD compliance, construction management, procurement, staffing and organizational management for housing owners.",
      [crumbs_schema(items)]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Services</h1><hr class="divider">
  <p class="lede">Nine services in three groups, delivered by one team for affordable and multifamily housing owners. Use one, or let us run them together under a single operating plan.</p>
  <div class="cta-row"><a class="btn btn-solid" href="{cal('services','head')}" data-cta="services-calendly">Book a 15-minute call</a></div>
</div></section>
<section class="section"><div class="wrap">{pillars(c)}</div></section>
{band(c,'services')}
""" + foot(c)

def p_service(c, k):
    s = SERVICES[k]
    items = [("Home",""),("Services","services"),(s["name"],"services/"+k)]
    svc = {"@context":"https://schema.org","@type":"Service","name":s["name"],"serviceType":s["name"],"description":s["desc"],
           "provider":{"@id":ORG_ID},"areaServed":[{"@type":"Place","name":a} for a in AREA],"url":f"{SITE}/services/{k}"}
    ticks = lambda xs: '<ul class="ticks">' + "".join(f"<li>{E(x)}</li>" for x in xs) + "</ul>"
    faqs = "".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in s["faqs"])
    rel = "".join(f'<a class="btn btn-line" href="{c.L("services/"+r)}">{E(SERVICES[r]["name"])}</a>' for r in s["related"])
    return head(c, s["title"], s["desc"], [crumbs_schema(items), svc, faq_schema(s["faqs"])]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>{E(s['h1'])}</h1><hr class="divider">
  <p class="lede">{E(s['lede'])}</p>
  <div class="cta-row"><a class="btn btn-solid" href="{cal('svc-'+k,'head')}" data-cta="svc-calendly">Book a 15-minute call</a><a class="btn btn-line" href="{c.L('capabilities#rfp')}">Send an RFP or scope</a></div>
</div></section>
<section class="section"><div class="wrap narrow">{"".join(f"<p>{E(p)}</p>" for p in s['intro'])}</div></section>
<section class="section tint"><div class="wrap scope">
  <div><h2>What's included</h2>{ticks(s['scope'])}</div>
  <div><h2>What you get</h2>{ticks(s['outcomes'])}</div>
</div></section>
<section class="section"><div class="wrap narrow">
  <div class="head"><h2>Who it's for</h2><hr class="divider"><p>{E(s['who'])}</p></div>
  <div class="head"><h2>Questions</h2><hr class="divider"></div>
  <div class="faq">{faqs}</div>
  <div class="head" style="margin:56px auto 20px"><h3>Related services</h3></div>
  <div class="related">{rel}</div>
</div></section>
{band(c,'svc-'+k)}
""" + foot(c)

def p_capabilities(c):
    items = [("Home",""),("Capabilities","capabilities")]
    comp = "".join(f"<li>{E(v['name'])}</li>" for v in SERVICES.values())
    naics = "".join(f"<tr><td>{n}</td><td>{E(t)}</td></tr>" for n,t in NAICS)
    return head(c, "Capability Statement, NAICS & RFPs | Javelin Residential",
      "Capability statement for housing authorities, agencies and owners: core competencies, NAICS codes, past performance and how to send an RFP.",
      [crumbs_schema(items)]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Capability statement</h1><hr class="divider">
  <p class="lede">For housing authorities, government agencies, nonprofit owners and private owners issuing RFPs, RFQs and contracts for property operations, compliance, construction and staffing.</p>
  <div class="cta-row no-print"><a class="btn btn-solid" href="#rfp">Send an RFP or scope</a><a class="btn btn-line" href="{TOUGHLEAF}">View project portfolio</a><a class="btn btn-line" href="{cal('capabilities','head')}" data-cta="cap-calendly">Book a 15-minute call</a></div>
</div></section>
<section class="section"><div class="wrap">
  <div class="cap">
    <div><h2>Core competencies</h2><ul class="ticks">{comp}</ul></div>
    <div><h2>Differentiators</h2><ul class="ticks">
      <li>One accountable team across operations, construction, procurement and staffing</li>
      <li>Leadership that grew a NYC portfolio to 14,000+ units and restructured a 700+ employee urban community</li><li>$100M+ in capital projects: redevelopment, apartment renovations and building-system modernization</li>
      <li>Deep LIHTC, HUD and agency compliance experience</li>
      <li>Flat-fee retainers and fixed-scope projects, no hourly billing</li>
      <li>Technology fluency from co-founding an affordable housing leasing and compliance platform</li></ul></div>
    <div><h2>Past performance</h2><ul class="ticks">
      <li><b>GRC Management, New York City</b> (President, April 2019&ndash;October 2025): restructured and modernized a 49-year-old full-service management company; grew the portfolio from 5,000 to 14,000+ affordable and market-rate units with 400+ employees</li>
      <li><b>Large urban residential community, Bronx</b> (Executive leadership, 2012&ndash;2017): organizational restructuring of 700+ employees; 12,000+ apartments in two condominium structures with separate governing boards, a sponsor-led team, 500,000 sq. ft. of commercial and three parking garages; renovation program delivered $3M under budget, ownership profits up 60%; sponsor-led refinance</li>
      <li><b>Nonprofit affordable housing owner, Newark, NJ</b> (Javelin, 2026&ndash;present): asset management, staffing, policies and procedures, LIHTC compliance and recertifications</li>
      <li><b>Harlem affordable housing developer</b> (Javelin, 2026): managing-agent agency approval submission</li>
      <li><b>Workforce housing firms</b> (consultant): property and asset management reporting packages and standard operating procedures</li>
      <li><b>First Sterling Financial, now Regents Bank</b> (VP, Asset Management &amp; Business Development, 2010&ndash;2012): built third-party management from the asset management platform; negotiated loans to reduce non-performing assets</li></ul></div>
    <div><h2>Company data</h2><table>
      <tr><td>Name</td><td>Javelin Residential</td></tr>
      <tr><td>Principal</td><td>Ryan Moorehead, Founder</td></tr>
      <tr><td>Address</td><td>{ADDRESS['street']}, {ADDRESS['city']}, {ADDRESS['region']} {ADDRESS['zip']}</td></tr>
      <tr><td>Email</td><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr>
      <tr><td>Web</td><td>www.javelinre.com</td></tr>
      <tr><td>Portfolio</td><td><a href="{TOUGHLEAF}">Projects on Tough Leaf</a></td></tr>
      <tr><td>UEI / CAGE</td><td class="pending">To be added</td></tr>
      <tr><td>Certifications</td><td>MBE certification in progress</td></tr>
      <tr><td>Memberships</td><td>REEC, NYREC, ULI</td></tr>
      <tr><td>Insurance</td><td class="pending">To be added</td></tr></table></div>
  </div>
  <div class="head" style="margin:72px auto 28px"><h2>NAICS codes</h2><hr class="divider"></div>
  <div class="cap" style="grid-template-columns:1fr"><div style="border-right:0"><table>{naics}</table></div></div>
</div></section>
{samples(c)}
<section class="section tint" id="rfp"><div class="wrap narrow">
  <div class="head"><h2>Send an RFP, RFQ or scope</h2><hr class="divider">
    <p class="lede">Include the solicitation number and due date if there is one. We confirm receipt within one business day and tell you whether we'll bid.</p></div>
  {contact_form('rfp')}
  <p class="cta-note">Or email solicitations to <a href="mailto:{EMAIL}?subject=RFP" data-cta="rfp-email">{EMAIL}</a></p>
</div></section>
""" + foot(c)

def p_leadership(c):
    items = [("Home",""),("Leadership","leadership")]
    person = {"@context":"https://schema.org","@type":"Person","@id":SITE+"/leadership#ryan","name":"Ryan Moorehead","jobTitle":"Founder & Principal",
              "worksFor":{"@id":ORG_ID},"image":SITE+"/assets/ryan-moorehead.jpg","sameAs":[LINKEDIN],
              "alumniOf":[{"@type":"CollegeOrUniversity","name":"Columbia Business School"},{"@type":"CollegeOrUniversity","name":"New York University"}],
              "award":"GlobeSt.com Top 50 Under 40 (2016)","memberOf":[{"@type":"Organization","name":"REEC"},{"@type":"Organization","name":"NYREC"},{"@type":"Organization","name":"Urban Land Institute"}],"knowsAbout":["Affordable housing","Asset management","LIHTC compliance","Property management","Construction management"]}
    return head(c, "Ryan Moorehead, Founder | Javelin Residential",
      "Ryan Moorehead: 20+ years in residential real estate; grew GRC Management to 14,000+ units; $100M+ in capital projects; Columbia career coach since 2013.",
      [crumbs_schema(items), person], "profile") + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Ryan Moorehead</h1><hr class="divider">
  <p class="lede">Founder &amp; Principal, Javelin Residential. Real estate operator, company builder and, since 2013, a real estate career coach at Columbia Business School.</p>
</div></section>
<section class="section"><div class="wrap bio">
  <div class="portrait"><img src="{c.A('assets/ryan-moorehead.jpg')}" alt="Ryan Moorehead" width="960" height="1200"></div>
  <div class="facts">
    <div><strong>Experience</strong>20+ years in real estate</div>
    <div><strong>Education</strong>Columbia MBA &middot; NYU B.S.</div>
    <div><strong>Portfolio</strong>14,000+ units grown at GRC</div>
  </div>
  <div class="prose">
    <p>Ryan Moorehead has spent more than twenty years in residential real estate, across development, asset management, property management and technology. He founded Javelin Residential to give owners what he wanted as an operator: one accountable partner across management, construction, procurement and people.</p>
    <p>His path into real estate was not a straight line. Ryan grew up in Oakland, California, and started college at UC Berkeley, where he played football. He left to study music theory and sound design in Arizona, then began his career at Sony Music, working his way from intern to signing an artist from his hometown while taking classes at NYU at night. It was at NYU that he found real estate. He moved to The Richman Group, where he developed a lasting interest in affordable housing, and interned at AvalonBay while in graduate school. He graduated from NYU with a B.S. in Real Estate, magna cum laude, and holds an MBA from Columbia Business School.</p>
    <h2>Asset management and turnarounds</h2>
    <p>From 2010 to 2012, as Vice President of Asset Management and Business Development at First Sterling Financial (now Regents Bank), Ryan grew the firm by turning its asset management platform into a third-party management business, while managing risk across an asset-based portfolio with a focus on cost control. He was instrumental in loan negotiations that reduced the number of non-performing assets in the portfolio. He also consulted for workforce housing firms, building their property and asset management reporting packages and standard operating procedures.</p>
    <h2>Large-scale urban restructuring</h2>
    <p>From 2012 to 2017, Ryan held a senior executive role with a privately owned New York real estate firm with a $2 billion multifamily portfolio. There he led the organizational restructuring of a large, complex urban community: more than 700 employees, over 12,000 apartments in two condominium structures with separate governing boards, a sponsor-led team, 500,000 square feet of commercial space and three parking garages. He created a modernization program whose apartment renovations finished $3 million under budget while lifting revenue more than 12 percent and ROI by 20.6 percent. His value-add strategies, operational efficiencies and organizational changes grew ownership's profits by 60 percent, and he led a complex sponsor-led refinancing while managing teams across multiple states.</p>
    <p>Across his career, Ryan has led more than $100 million in capital projects spanning redevelopment, apartment renovations and building-system modernization.</p>
    <p class="pull">The most valuable fixes in a building are usually organizational: who owns the hand-off, who signs the contract, who checks the file.</p>
    <h2>GRC Management</h2>
    <p>From April 2019 to October 2025, Ryan served as President of GRC Management, a 49-year-old full-service residential property management company in New York City, which he partnered with to restructure and modernize. He grew its portfolio from 5,000 to more than 14,000 units of affordable and market-rate housing, with more than 400 employees across the portfolio. That work, rebuilding staffing, systems, compliance and reporting at scale, is the foundation of Javelin's practice today. He stepped away from GRC in October 2025 to focus on Javelin and Arlo.</p>
    <h2>Building companies</h2>
    <p>Alongside Javelin, Ryan is co-founder of Arlo, an AI-powered leasing and compliance platform for affordable housing. He also owns Affogato House, a specialty coffee and gelato caf&eacute; in New Rochelle, New York, which he took from raw space through design, construction and opening. Outside of real estate, he is a published poet with two collections in print.</p>
    <h2>Recognition, coaching and community</h2>
    <p>GlobeSt.com named Ryan to its Top 50 Under 40 at the 2016 Real Estate Forum. Since 2013 he has been a real estate career coach for Columbia University, working with MBA students and alumni moving into or within real estate, and he now offers one-on-one coaching through Javelin. He is a member of REEC, NYREC and ULI, and has spoken at REEC, DCRE, AAREPNY and CRETech on affordable housing operations, real estate technology and careers.</p>
  </div>
  <div class="cta-row" style="margin-top:36px"><a class="btn btn-solid" href="{cal('leadership','bio')}" data-cta="bio-calendly">Book a call with Ryan</a><a class="btn btn-line" href="{c.L('speaking')}">Invite Ryan to speak</a><a class="btn btn-line" href="{TOUGHLEAF}">Project portfolio</a><a class="btn btn-line" href="{LINKEDIN}" rel="me">LinkedIn</a></div>
</div></section>
""" + foot(c)

def p_coaching(c):
    items = [("Home",""),("Coaching","coaching")]
    faqs = [("Who is coaching for?","MBA students and alumni, career changers moving into real estate, and professionals stepping into asset management, development or operations leadership."),
            ("How do sessions work?","Start with a 15-minute intro call. From there, sessions are one-on-one by video, single sessions or a short series around a goal such as a job search."),
            ("Do you coach outside Columbia?","Yes. Coaching through Javelin is open to anyone building a career in real estate.")]
    svc = {"@context":"https://schema.org","@type":"Service","name":"Real estate career coaching","provider":{"@id":ORG_ID},"description":"One-on-one real estate career coaching with Ryan Moorehead, a Columbia Business School real estate career coach since 2013."}
    return head(c, "Real Estate Career Coaching | Ryan Moorehead",
      "One-on-one real estate career coaching with Ryan Moorehead, a Columbia Business School coach since 2013: career paths, interviews and leadership.",
      [crumbs_schema(items), svc, faq_schema(faqs)]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Real estate career coaching</h1><hr class="divider">
  <p class="lede">One-on-one coaching with Ryan Moorehead, who has coached real estate MBA students at Columbia Business School since 2013 and has spent two decades hiring and leading teams in residential real estate.</p>
  <div class="cta-row"><a class="btn btn-solid" href="{cal('coaching','head')}" data-cta="coaching-calendly">Book a 15-minute intro call</a></div>
</div></section>
<section class="section"><div class="wrap">
  <div class="head"><h2>What we work on</h2><hr class="divider"></div>
  <div class="pillars">
    <div class="pillar"><h3>Choosing a path</h3><p>Development, acquisitions, asset management, operations or proptech: what each job is really like and which fits you.</p></div>
    <div class="pillar"><h3>Getting the job</h3><p>Positioning, networking, resumes, interviews and case or modeling preparation for real estate roles.</p></div>
    <div class="pillar"><h3>Leading the team</h3><p>Stepping into a first management or leadership role and building credibility with owners and staff.</p></div>
  </div>
</div></section>
<section class="section tint"><div class="wrap">
  <div class="head"><h2>How it works</h2><hr class="divider"></div>
  <ol class="steps" style="grid-template-columns:repeat(3,1fr)">
    <li><h3>Intro call</h3><p>A 15-minute call to understand where you are and what you want.</p></li>
    <li><h3>Plan</h3><p>A short written plan: target roles, gaps to close and the next three moves.</p></li>
    <li><h3>Sessions</h3><p>One-on-one video sessions, single or as a short series around a goal.</p></li>
  </ol>
</div></section>
<section class="section"><div class="wrap narrow">
  <div class="head"><h2>Questions</h2><hr class="divider"></div>
  <div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in faqs)}</div>
</div></section>
{band(c,'coaching','Book a coaching intro call','Fifteen minutes to talk through where you are, where you want to go and whether coaching is the right next step.')}
""" + foot(c)

def p_speaking(c):
    items = [("Home",""),("Speaking","speaking")]
    topics = [
      ("Affordable housing operations at scale","How a NYC management company grew from 5,000 to 14,000+ units: staffing, systems, compliance and the decisions that held it together."),
      ("AI and technology in affordable housing","What AI can and can't do for leasing, income certification and compliance, from the co-founder of an affordable housing leasing platform."),
      ("Value-add in occupied buildings","Lessons from $100M+ in capital work, including a renovation program delivered $3M under budget with residents in place."),
      ("Turning around a property organization","Consolidating fragmented management, writing the playbook, and building teams that own the hand-offs."),
      ("Building a career in real estate","From Sony Music to restructuring a 700-person urban community, and more than a decade coaching MBA students at Columbia."),
      ("Procurement and the cost of operations","Where operating budgets leak, and how owners recover it through vendors, staffing and capital planning."),
    ]
    faqs = [("What formats does Ryan do?","Keynotes, panels, moderated discussions, fireside chats, workshops, podcasts and university guest lectures, in person or virtual."),
            ("How far ahead should we ask?","Four to six weeks is ideal. Shorter timelines are possible; book a call and we'll check the date."),
            ("Do you provide a bio and headshot?","Yes. A short bio and headshot are on this page, and a longer bio is on the Leadership page.")]
    svc = {"@context":"https://schema.org","@type":"Service","name":"Speaking engagements: Ryan Moorehead","provider":{"@id":SITE+"/leadership#ryan"},
           "description":"Conference keynotes, panels and moderated discussions on affordable housing operations, real estate technology, value-add renovation and real estate careers.","areaServed":"United States"}
    tlist = "".join(f'<div class="svc-link" style="cursor:default"><h4>{E(t)}</h4><p>{E(d)}</p></div>' for t,d in topics)
    half = (len(topics)+1)//2
    tl = "".join(f'<div class="svc-link"><h4>{E(t)}</h4><p>{E(d)}</p></div>' for t,d in topics[:half])
    tr = "".join(f'<div class="svc-link"><h4>{E(t)}</h4><p>{E(d)}</p></div>' for t,d in topics[half:])
    short_bio = ("Ryan Moorehead is the Founder of Javelin Residential and co-founder of Arlo, an AI-powered leasing and compliance platform for affordable housing. "
                 "As President of GRC Management from 2019 to 2025, he grew a New York City portfolio from 5,000 to more than 14,000 affordable and market-rate units. "
                 "Previously, he led the organizational restructuring of a 12,000+ apartment urban community with 700+ employees. Across his career he has led more than $100M in capital projects. "
                 "A GlobeSt.com Top 50 Under 40 honoree, he has been a real estate career coach for Columbia University since 2013 and holds an MBA from Columbia Business School and a B.S. in Real Estate from NYU.")
    return head(c, "Book Ryan Moorehead to Speak | Javelin Residential",
      "Invite Ryan Moorehead to speak at your conference, panel or podcast on affordable housing operations, AI and PropTech, and real estate careers.",
      [crumbs_schema(items), svc, faq_schema(faqs)]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Speaking engagements</h1><hr class="divider">
  <p class="lede">Looking for Ryan to speak at a conference, sit on a panel or join a podcast? He brings two decades of operating experience, from restructuring a 700+ employee urban community to growing a NYC portfolio past 14,000 units, and the perspective of a proptech founder.</p>
  <div class="cta-row"><a class="btn btn-solid" href="#request">Request Ryan for an event</a><a class="btn btn-line" href="{cal('speaking','head')}" data-cta="speaking-calendly">Book a 15-minute call</a></div>
</div></section>
<section class="section"><div class="wrap">
  <div class="head"><h2>Topics</h2><hr class="divider"><p class="lede">Each talk can be tailored to the audience: owners and investors, operators, public agencies, technologists or students.</p></div>
  <div class="duo"><div>{tl}</div><div>{tr}</div></div>
</div></section>
<section class="section"><div class="wrap">
  <div class="head"><h2>Where Ryan has spoken</h2><hr class="divider"></div>
  <ul class="clients venues"><li>REEC</li><li>DCRE</li><li>AAREPNY</li><li>CRETech</li></ul>
</div></section>
<section class="section tint"><div class="wrap">
  <div class="head"><h2>Formats</h2><hr class="divider"></div>
  <div class="pillars">
    <div class="pillar"><h3>Keynote</h3><p>A 20 to 45 minute talk built around one of the topics above, with time for questions.</p></div>
    <div class="pillar"><h3>Panel &amp; moderation</h3><p>Panelist or moderator on operations, affordable housing policy in practice, and real estate technology.</p></div>
    <div class="pillar"><h3>Workshop &amp; lecture</h3><p>Fireside chats, podcasts, operator workshops and university guest lectures, in person or virtual.</p></div>
  </div>
</div></section>
<section class="section"><div class="wrap leader">
  <div class="portrait"><img src="{c.A('assets/ryan-moorehead.jpg')}" alt="Ryan Moorehead headshot" width="960" height="1200" loading="lazy"></div>
  <div>
    <h2>Speaker bio</h2>
    <p class="role">For programs and introductions</p>
    <p>{E(short_bio)}</p>
    <ul class="creds"><li>Has spoken at REEC, DCRE, AAREPNY and CRETech</li><li>GlobeSt.com Top 50 Under 40 (2016)</li><li>Columbia University career coach since 2013</li><li>Member, REEC, NYREC and ULI</li></ul>
    <div class="cta-row" style="justify-content:flex-start"><a class="btn btn-line" href="{c.A('assets/ryan-moorehead.jpg')}">Download headshot</a><a class="btn btn-line" href="{c.L('leadership')}">Full bio</a></div>
  </div>
</div></section>
<section class="section tint" id="request"><div class="wrap narrow">
  <div class="head"><h2>Request Ryan for an event</h2><hr class="divider"><p class="lede">Send the details and we'll confirm availability within two business days.</p></div>
  <form data-mail="Speaking request">
    <div class="row"><label>Your name<input name="name" autocomplete="name" required></label><label>Organization<input name="organization" autocomplete="organization" required></label></div>
    <div class="row"><label>Email<input name="email" type="email" autocomplete="email" required></label><label>Phone<input name="phone" type="tel" autocomplete="tel"></label></div>
    <div class="row"><label>Event name<input name="event" required></label><label>Event date<input name="date" type="date"></label></div>
    <div class="row"><label>Location or virtual<input name="location" placeholder="City, venue, or virtual"></label>
      <label>Format<select name="interest"><option value="">Choose one</option><option>Keynote</option><option>Panel</option><option>Moderator</option><option>Fireside chat</option><option>Workshop</option><option>Podcast</option><option>University lecture</option></select></label></div>
    <div class="row"><label>Audience and size<input name="audience" placeholder="e.g. 300 owners and operators"></label><label>Honorarium / travel<input name="budget" placeholder="Budget or covered expenses"></label></div>
    <label>Topic and details<textarea name="message" placeholder="Session topic, other speakers, and your deadline to confirm"></textarea></label>
    <button class="btn btn-solid" type="submit">Send speaking request</button>
    <p class="form-note" role="status"></p>
  </form>
  <p class="cta-note">Or email <a href="mailto:{EMAIL}?subject=Speaking%20request" data-cta="speaking-email">{EMAIL}</a></p>
</div></section>
<section class="section"><div class="wrap narrow">
  <div class="head"><h2>Questions</h2><hr class="divider"></div>
  <div class="faq">{"".join(f"<details><summary>{E(q)}</summary><p>{E(a)}</p></details>" for q,a in faqs)}</div>
</div></section>
{band(c,'speaking','Planning a program?','A 15-minute call is the fastest way to check the date, the audience and the right topic.')}
""" + foot(c)

import re, glob
CATEGORIES = [
  ("leadership", "Leadership"),
  ("technology", "Technology"),
  ("affordable-housing", "Affordable Housing"),
  ("quick-tips", "Best Practices & Quick Tips"),
  ("mena", "Emerging Markets: MENA"),
]
CATORDER = [k for k,_ in CATEGORIES]

def md_inline(t):
    t = E(t, quote=False)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?![*\w])", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+|/[^)\s]*)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t

def md_to_blocks(text):
    blocks, para, items = [], [], []
    def flush():
        if para: blocks.append(("p", md_inline(" ".join(para)))); para.clear()
        if items: blocks.append(("ul", items[:])); items.clear()
    for line in text.splitlines():
        s = line.strip()
        if not s: flush(); continue
        if s.startswith("## ") or s.startswith("### "): flush(); blocks.append(("h2", s.lstrip("#").strip())); continue
        if s.startswith("> "): flush(); blocks.append(("pull", s[2:].strip())); continue
        if s.startswith("- ") or s.startswith("* "):
            if para: flush()
            items.append(md_inline(s[2:].strip())); continue
        if items: flush()
        para.append(s)
    flush()
    return blocks

def load_posts(include_future=False):
    posts = []
    for f in sorted(glob.glob("content/insights/*.md")):
        raw = open(f, encoding="utf-8").read()
        m = re.match(r"---\n(.*?)\n---\n(.*)", raw, re.S)
        if not m: continue
        meta = {}
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1); v = v.strip()
                if len(v) >= 2 and v[0] == v[-1] == '"': v = v[1:-1].replace('\\"', '"')
                meta[k.strip()] = v
        if meta.get("category") not in CATORDER: continue
        if not include_future and meta.get("date", TODAY) > TODAY: continue
        slug = meta.get("slug") or re.sub(r"^\d{4}-\d{2}-\d{2}-", "", f.split("/")[-1][:-3])
        posts.append(dict(slug=slug, title=meta["title"], cat=meta["category"], desc=meta.get("description",""),
                          seo=meta.get("seo_title") or (meta["title"][:52] + " | Javelin"), date=meta.get("date", TODAY),
                          body=md_to_blocks(m.group(2))))
    posts.sort(key=lambda p: (p["date"], CATORDER.index(p["cat"])), reverse=True)
    return posts

POSTS = load_posts()
CATNAME = {k:n for k,n in CATEGORIES}

def posts_html(c, n=None):
    out=[]
    for p in POSTS[:n] if n else POSTS:
        out.append(f'<a class="post" href="{c.L("insights/"+p["slug"])}"><span class="tag">{E(CATNAME[p["cat"]])}</span><h3>{E(p["title"])}</h3><p>{E(p["desc"])}</p><span class="more">Read the post</span></a>')
    return '<div class="posts">' + "".join(out) + "</div>"

def p_insights(c):
    items = [("Home",""),("Insights","insights")]
    blog = {"@context":"https://schema.org","@type":"Blog","name":"Javelin Insights","url":SITE+"/insights","publisher":{"@id":ORG_ID},
            "blogPost":[{"@type":"BlogPosting","headline":p["title"],"url":f"{SITE}/insights/{p['slug']}"} for p in POSTS]}
    return head(c, "Javelin Insights | Housing, Leadership & PropTech",
      "Weekly posts from Ryan Moorehead on leadership, technology, affordable housing, best practices and MENA real estate opportunities.",
      [crumbs_schema(items), blog]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Insights</h1><hr class="divider">
  <p class="lede">Practical writing from Ryan Moorehead on leadership, technology, affordable housing and emerging markets. New posts every week.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="head"><h2>Latest posts</h2><hr class="divider"></div>
  {posts_html(c)}
</div></section>
{band(c,'insights','Have a question we should write about?','Book a short call or send us the problem. The best questions become next week\'s post.')}
""" + foot(c)

def render_body(c, body):
    out=[]
    for kind, text in body:
        if kind=="p": out.append(f"<p>{text}</p>")
        elif kind=="h2": out.append(f"<h2>{E(text)}</h2>")
        elif kind=="pull": out.append(f'<p class="pull">{E(text)}</p>')
        elif kind=="ul": out.append('<ul class="ticks">' + "".join(f"<li>{i}</li>" for i in text) + "</ul>")
    return "\n  ".join(out)

def p_post(c, p):
    items = [("Home",""),("Insights","insights"),(p["title"],"insights/"+p["slug"])]
    art = {"@context":"https://schema.org","@type":"BlogPosting","headline":p["title"],"description":p["desc"],"datePublished":p["date"],
           "articleSection":CATNAME[p["cat"]],"author":{"@id":SITE+"/leadership#ryan","@type":"Person","name":"Ryan Moorehead"},"publisher":{"@id":ORG_ID},
           "mainEntityOfPage":f"{SITE}/insights/{p['slug']}","image":SITE+"/assets/og-image.png"}
    t = p["title"] if len(p["title"])<=52 else p["title"][:p["title"].rfind(" ",0,52)].rstrip(",:")
    others = [q for q in POSTS if q is not p][:3]
    more = "".join(f'<a class="post" href="{c.L("insights/"+q["slug"])}"><span class="tag">{E(CATNAME[q["cat"]])}</span><h3>{E(q["title"])}</h3><span class="more">Read the post</span></a>' for q in others)
    return head(c, p["seo"], p["desc"], [crumbs_schema(items), art], "article") + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>{E(p['title'])}</h1><hr class="divider">
  <p class="article meta">By Ryan Moorehead &middot; {E(CATNAME[p['cat']])} &middot; {datetime.date.fromisoformat(p['date']).strftime('%B %-d, %Y')}</p>
</div></section>
<section class="section"><div class="wrap article prose">
  {render_body(c, p['body'])}
</div></section>
<section class="section tint"><div class="wrap"><div class="head"><h2>More insights</h2><hr class="divider"></div><div class="posts">{more}</div></div></section>
{band(c,'post-'+p['slug'],'Talk it through with Ryan','A 15-minute call is the fastest way to see whether Javelin can help.')}
""" + foot(c)

def p_privacy(c):
    items = [("Home",""),("Privacy policy","privacy")]
    secs = [
     ("Who we are", f"Javelin Residential (\"Javelin,\" \"we,\" \"us\") operates www.javelinre.com. Our office is at {ADDRESS['street']}, {ADDRESS['city']}, {ADDRESS['region']} {ADDRESS['zip']}. Questions about this policy can be sent to <a href=\"mailto:{EMAIL}\">{EMAIL}</a>."),
     ("Information you give us", "When you use a form on this site (a general inquiry, an RFP or scope, a speaking request or a newsletter sign-up) we collect what you enter, such as your name, organization, email address, phone number and message. We use it only to respond to you, evaluate the request and keep a record of our correspondence."),
     ("Scheduling", "Meetings are booked through Calendly. When you schedule a call, Calendly collects your name, email address and any answers you provide, and shares them with us so we can hold the meeting. Calendly's own privacy policy applies to the information it processes."),
     ("Analytics and advertising", "We may use Google Analytics and Google Ads to understand how visitors find and use the site and to measure whether our advertising leads to inquiries or booked calls. These services use cookies and similar technologies to collect information such as pages visited, approximate location, device and browser type, and the website that referred you. They do not give us your name or contact details. You can opt out of Google Analytics with Google's browser add-on and control ad personalization in your Google account settings."),
     ("Cookies", "Cookies are small files stored by your browser. Beyond analytics and advertising cookies, this site does not set cookies for its own purposes. You can block or delete cookies in your browser settings; the site will still work."),
     ("How we share information", "We do not sell your personal information. We share it only with service providers that help us run the site and respond to you, such as our hosting provider (Vercel), email delivery service, Calendly and Google, and only as needed for those purposes, or when the law requires it."),
     ("How long we keep it", "We keep inquiry and correspondence records for as long as needed to respond, carry out any resulting engagement and meet legal and accounting obligations, then delete them."),
     ("Your choices and rights", f"You can ask us what personal information we hold about you, ask us to correct or delete it, or unsubscribe from any email at any time by writing to <a href=\"mailto:{EMAIL}\">{EMAIL}</a>. Depending on where you live, you may have additional rights under local law."),
     ("Security", "We use reasonable safeguards to protect the information you send us. No method of transmission over the internet is completely secure, so please do not send sensitive personal or financial information through our forms."),
     ("Children", "This site is intended for business audiences and is not directed to children under 13. We do not knowingly collect information from children."),
     ("Changes", "We may update this policy from time to time. The date below shows when it last changed."),
    ]
    body = "".join(f"<h2>{E(h)}</h2><p>{t}</p>" for h,t in secs)
    return head(c, "Privacy Policy | Javelin Residential", "How Javelin Residential collects, uses and protects information submitted through javelinre.com, Calendly scheduling and site analytics.",
      [crumbs_schema(items)]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Privacy policy</h1><hr class="divider">
  <p class="lede">Last updated {datetime.date.today().strftime('%B %-d, %Y')}</p>
</div></section>
<section class="section"><div class="wrap article prose policy">{body}</div></section>
""" + foot(c)

def p_book(c):
    items = [("Home",""),("Book a call","book")]
    return head(c, "Book a Call | Consulting or Coaching | Javelin Residential",
      "Book a 15-minute call with Javelin Residential about a property, portfolio, contract or RFP, or a real estate career coaching session with Ryan Moorehead.",
      [crumbs_schema(items)]) + f"""
<section class="page-head"><div class="wrap">{crumbs_html(c,items)}
  <h1>Book a call</h1><hr class="divider">
  <p class="lede">Every engagement starts with a 15-minute call. Pick a time below and tell us whether it's about a property, a contract or your career.</p>
</div></section>
<section class="section"><div class="wrap">
  <div class="sessions">
    <div class="session"><h2>Consulting</h2><p class="meta">15-minute intro call</p>
      <ul><li>Property and portfolio operations</li><li>LIHTC and HUD compliance, audits and MORs</li><li>Capital projects and construction management</li><li>Procurement, staffing and organization</li><li>RFPs, RFQs and contract scopes</li></ul>
      <a class="btn btn-solid" href="{cal('book','consulting')}" data-cta="book-consulting">Book a consulting call</a></div>
    <div class="session"><h2>Coaching</h2><p class="meta">15-minute intro call</p>
      <ul><li>Choosing a real estate career path</li><li>Interviews and case preparation</li><li>Career changes into real estate</li><li>First leadership roles</li><li>With a Columbia coach since 2013</li></ul>
      <a class="btn btn-solid" href="{cal('book','coaching')}" data-cta="book-coaching">Book a coaching call</a></div>
  </div>
</div></section>
<section class="section tint" id="calendar"><div class="wrap">
  <div class="head"><h2>Pick a time</h2><hr class="divider"></div>
  <div class="calendly-inline-widget" data-url="{cal('book','inline')}&amp;hide_gdpr_banner=1&amp;primary_color=0c418a" style="min-width:300px;height:700px"></div>
  <div class="cta-row"><a class="btn btn-line" href="{cal('book','fallback')}">Open the calendar in a new page</a></div>
</div></section>
<section class="section" id="contact"><div class="wrap narrow">
  <div class="head"><h2>Have a problem? Let's discuss it.</h2><hr class="divider"><p class="lede">Send a few details and we'll reply within one business day.</p></div>
  {contact_form('book')}
  <p class="cta-note">{ADDRESS['street']}, {ADDRESS['city']}, {ADDRESS['region']} {ADDRESS['zip']} &middot; <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</div></section>
<script src="https://assets.calendly.com/assets/external/widget.js" async></script>
""" + foot(c)

def p_404(c):
    return head(c, "Page not found | Javelin Residential", "The page you were looking for isn't here.", []).replace('content="index, follow"','content="noindex"') + f"""
<section class="page-head"><div class="wrap"><h1>Page not found</h1><hr class="divider">
<p class="lede">That page has moved or no longer exists. Try our services, or book a call.</p>
<div class="cta-row"><a class="btn btn-solid" href="{c.L('services')}">View services</a><a class="btn btn-line" href="{c.L('book')}">Book a call</a></div></div></section>
""" + foot(c)

PAGES = [("",p_home),("services",p_services),("capabilities",p_capabilities),("leadership",p_leadership),("coaching",p_coaching),("speaking",p_speaking),
         ("insights",p_insights),("privacy",p_privacy),("book",p_book)] + \
        [("services/"+k,(lambda k: lambda c: p_service(c,k))(k)) for k in SERVICES] + \
        [("insights/"+p["slug"],(lambda p: lambda c: p_post(c,p))(p)) for p in POSTS]

NBH = "\u2011"  # non-breaking hyphen: hyphenated words never split across lines
def keep_hyphens(html_text):
    def fix(m): return m.group(1) + re.sub(r"(?<=\w)-(?=\w)", NBH, m.group(2)) + m.group(3)
    html_text = re.sub(r"(<h[1-4][^>]*>)(.*?)(</h[1-4]>)", fix, html_text, flags=re.S)
    html_text = re.sub(r'(<a class="btn[^"]*"[^>]*>)(.*?)(</a>)', fix, html_text, flags=re.S)
    html_text = re.sub(r'(<(?:strong|summary|span class="tag"|li)[^>]*>)([^<]*?)(</(?:strong|summary|span|li)>)', fix, html_text)
    return html_text

def build(mode, out):
    shutil.rmtree(out, ignore_errors=True); os.makedirs(out)
    shutil.copytree("assets", out+"/assets"); shutil.copy("styles.css", out); shutil.copy("main.js", out)
    for path, fn in PAGES:
        c = Ctx(mode, path); fname = (path or "index") + ".html"
        os.makedirs(os.path.dirname(os.path.join(out, fname)) or out, exist_ok=True)
        open(os.path.join(out, fname), "w").write(keep_hyphens(fn(c)))
    if mode == "prod":
        open(out+"/404.html","w").write(p_404(Ctx("prod","404")))
        open(out+"/robots.txt","w").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
        urls = "".join(f"  <url><loc>{SITE}{'/'+p if p else '/'}</loc><lastmod>{TODAY}</lastmod><priority>{'1.0' if not p else '0.8' if p.startswith('services') or p in ('capabilities','book','speaking') else '0.6'}</priority></url>\n" for p,_ in PAGES)
        open(out+"/sitemap.xml","w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')

if __name__ == "__main__":
    import sys
    if "--preview" in sys.argv: build("preview","dist")
    build("prod","public")
    print(len(PAGES),"pages")
