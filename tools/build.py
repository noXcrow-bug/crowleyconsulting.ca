"""Builds the Noah Crowley Asbestos and Designated Substances Consulting website.
Run:  python3 tools/build.py   (from the repo root). Writes the .html files, sitemap.xml and robots.txt.
All copy is drawn from the NCC business plan; every price comes from the public list in price book PB-2026.11. Edit SITE below for contact details, then rebuild."""
import json, os, hashlib, html as H
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SITE = {
    "domain": "https://crowleyconsulting.ca",
    "legal": "Noah Crowley Consulting",
    "online": "Noah Crowley Asbestos and Designated Substances Consulting",
    "tagline": "Asbestos & Designated Substances Compliance",
    "phone": "519-890-9654",
    "email": "info@crowleyconsulting.ca",
    "city": "Windsor",    # base city for search listings
    "founding": True,     # show the 10% founding-client offer (first 5 clients per program, 12 months)
}
REGIONS = "Windsor-Essex, Chatham-Kent, Sarnia-Lambton and London"
YEAR = date.today().year
e = H.escape
ASSET_V = hashlib.sha1(b"".join(open(os.path.join(ROOT, "assets", f), "rb").read() for f in ("site.css", "site.js", "config.js"))).hexdigest()[:8]

# ---------------------------------------------------------------- tiers (price book PB-2026.11)
# The website may quote only the public "from" prices in the price book. Anything more specific is quoted per building.
PRICE_BOOK = "PB-2026.11"
TIERS = {
 "bp_ess": dict(program="Building programs", name="Compliance Essentials", price=69, fits="Owners who need the yearly record kept current", page="building-owners.html",
   inc=["Yearly asbestos record update and visual condition inspection", "Hosted online register and an on-site inspector binder", "Occupier and contractor notice templates", "Annual compliance letter for insurers, lenders and tenants", "10% off reports, site visits and project work; extra lab layers at cost", "Phone advice if suspect material turns up"]),
 "bp_pr": dict(program="Building programs", name="Project Ready", price=149, fits="Buildings where contractors are working several times a year", page="building-owners.html",
   inc=["Yearly asbestos record update and visual condition inspection", "Notices prepared and issued to occupiers and contractors for you", "6 written “can we drill here?” desk reviews a year, answered within 1 business day", "1 maintenance staff awareness session a year", "15% off reports, site visits and project work; extra lab layers at cost", "Fieldwork booked within 5 business days; site visit the next business day if something turns up"]),
 "bp_fp": dict(program="Building programs", name="Facility Partner", price=529, fits="Three or more buildings, or a board or JHSC asking questions", page="building-owners.html",
   inc=["Record update and condition inspection twice a year", "Notices prepared, issued and tracked", "Unlimited written desk reviews, answered within 1 business day", "2 staff awareness sessions a year and a yearly board or JHSC presentation", "20% off reports, site visits and project work; extra lab layers at cost", "Fieldwork within 2 business days, a same-day visit if something turns up, and a yearly abatement budget"]),
 "pw_start": dict(program="Cleared-to-Start Pass", name="Starter", price=199, fits="Renovators and trades with 1–3 jobs a month in older buildings", page="contractors.html",
   inc=["A compliance desk to call before you bid or cut, business hours", "1 pre-bid review of the owner's designated substance report a month", "Site visit within 5 business days when a job needs testing", "10% off pre-work checks; extra lab layers at cost", "Written interim instructions on site when a job can't wait", "25% off work-classification letters, a due-diligence file per job, toolbox talk templates"]),
 "pw_pro": dict(program="Cleared-to-Start Pass", name="Pro", price=499, fits="General contractors and fit-out firms with 4 or more jobs a month", page="contractors.html",
   inc=["The compliance desk, business hours", "3 pre-bid reviews a month", "Site visit within 3 business days", "15% off pre-work checks; extra lab layers at cost", "Reports branded for your client", "1 live worker awareness session a year"]),
 "pw_rr": dict(program="Cleared-to-Start Pass", name="Restoration Priority", price=699, fits="Fire, flood and mould restoration firms, for the rebuild phase of a claim", page="contractors.html",
   inc=["Next-business-day site visits, Monday to Friday", "The compliance desk, business hours", "3 pre-bid reviews a month", "15% off pre-work checks; extra lab layers at cost", "Written interim instructions on every call, adjuster-ready reports", "Reports branded for your client and 1 worker awareness session a year"]),
}

# The public report menu: the lowest price of each product, always said as "from".
REPORTS = [
 ("Limited sampling visit", 650, "One to three suspect materials before a small repair: one floor, one pipe run, one wall", "A letter with lab results and the work classification for the planned job", "About 7 business days"),
 ("DSS update or re-assessment", 900, "An existing report that is out of date, or another firm's report that fell short", "A walk-through, gap sampling and a current, tender-ready report", "5 business days; 8–10 with sampling"),
 ("Project-specific DSS", 1700, "Renovation, repair or a tender for one work area", "All 11 designated substances in the work area, ready to attach to the tender", "8–10 business days"),
 ("Asbestos building survey", 2300, "No asbestos record on site, or the start of a building program", "The whole-building inventory that becomes your O. Reg. 278/05 record", "10–15 business days"),
 ("Full-building DSS and hazardous materials survey", 3050, "Acquisition, capital planning, several projects in one building", "All 11 substances plus PCBs, mould and refrigerants across the building", "10–20 business days"),
 ("Pre-demolition DSS", 4000, "A vacant building coming down, or a demolition permit", "A destructive survey of every space so materials can come out before demolition", "15–25 business days"),
]

def money(n): return "${:,.0f}".format(n)
def plabel(k, small=" a month"):
    p = TIERS[k]["price"]
    return (f'from {money(p)}' if k.startswith('bp_') else money(p)) + f'<small>{small}</small>' if p else '<small>Price on request</small>'

# ---------------------------------------------------------------- page chrome
NAV = [("building-owners.html", "Building owners"), ("landlords.html", "Landlords"), ("contractors.html", "Contractors"),
       ("services.html", "Reports & prices"), ("contact.html", "Contact")]
CITIES = [("asbestos-testing-windsor.html", "Windsor"), ("asbestos-testing-leamington.html", "Leamington"), ("asbestos-testing-chatham.html", "Chatham"),
          ("asbestos-testing-sarnia.html", "Sarnia"), ("asbestos-testing-london.html", "London")]
TRIGGERS = [("asbestos-testing-before-renovation.html", "Asbestos testing before renovation"),
            ("designated-substance-survey-demolition-permit.html", "Designated substance survey for a demolition permit"),
            ("silica-exposure-assessment.html", "Silica on renovation and demolition projects"),
            ("isocyanate-air-monitoring.html", "Isocyanate air monitoring")]
GUIDES = [("guide-inspector-ready-binder.html", "Inspector-ready binder checklist", "For building owners"),
          ("guide-suite-turnover-checklist.html", "Suite turnover checklist", "For landlords and property managers"),
          ("guide-designated-substance-self-check.html", "Designated substance self-check", "For employers"),
          ("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "For contractors")]
PAGES = []

def contact_bits():
    out = []
    if SITE["phone"]: out.append(f'<a href="{tel()}">{e(SITE["phone"])}</a>')
    if SITE["email"]: out.append(f'<a href="mailto:{e(SITE["email"])}">{e(SITE["email"])}</a>')
    return out

def head(title, desc, fname, schema=None):
    url = SITE["domain"] + "/" + ("" if fname == "index.html" else fname)
    ld = "".join(f'<script type="application/ld+json">{json.dumps(x)}</script>' for x in (schema if isinstance(schema, list) else [schema])) if schema else ""
    return f"""<!doctype html>
<html lang="en-CA">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="website">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{SITE['domain']}/assets/og-image.png">
<meta name="theme-color" content="#FFFFFF">
<meta name="color-scheme" content="light">
<meta name="format-detection" content="telephone=no">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preload" href="assets/fonts/ibm-plex-sans-condensed-latin-600-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="assets/fonts/ibm-plex-sans-latin-400-normal.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="assets/site.css?v={ASSET_V}">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""

ICON = {
 "phone": '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 3.5h2.6l1.5 4.2-2 1.3a11 11 0 0 0 6.3 6.3l1.3-2 4.2 1.5v2.6a2 2 0 0 1-2.2 2A16.5 16.5 0 0 1 4.6 5.7a2 2 0 0 1 2-2.2Z"/></svg>',
 "cal": '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><rect x="3.5" y="5" width="17" height="15.5" rx="2.5"/><path d="M3.5 10h17M8 3v4M16 3v4"/></svg>',
 "check": '<svg class="i" viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.2 4.2L19 7"/></svg>',
 "chev": '<svg class="i chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5.5l6.5 6.5L9 18.5"/></svg>',
}
def tel(): return "tel:+1" + SITE["phone"].replace("-", "")

def header(active):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    call = f'<a class="icon-btn call-btn" href="{tel()}" aria-label="Call {e(SITE["phone"])}">{ICON["phone"]}</a>' if SITE["phone"] else ""
    return f"""<header class="site-head"><div class="wrap head-row">
<a class="brand" href="index.html" aria-label="{e(SITE['online'])}, home"><img src="assets/ncc-logo-online-compact.svg" alt="{e(SITE['online'])}" width="606" height="128"></a>
<div class="head-actions">{call}<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav"><span class="burger" aria-hidden="true"><i></i><i></i></span><span class="menu-label">Menu</span></button></div>
<nav class="nav" id="site-nav" aria-label="Main">{links}<a class="btn amber" href="obligation-check.html">Take the Obligation Check</a></nav>
</div></header>
<div class="scrim" hidden></div>
<main id="main">"""

def action_bar(fname):
    if fname in ("contact.html", "404.html") or not SITE["phone"]: return ""
    second = ('<a class="btn" href="contact.html#book" data-book>' + ICON["cal"] + 'Book a call</a>') if fname == "obligation-check.html" else '<a class="btn amber" href="obligation-check.html">Take the Obligation Check</a>'
    return f'<div class="action-bar" aria-label="Quick actions"><a class="btn ghost" href="{tel()}">{ICON["phone"]}Call</a>{second}</div>'

def footer(fname=""):
    cb = contact_bits()
    contact = ("<li>" + "</li><li>".join(cb) + "</li>") if cb else '<li><a href="contact.html">Send us a message</a></li>'
    return f"""</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div class="foot-brand"><img src="assets/ncc-logo-online-compact-reverse.svg" alt="{e(SITE['online'])}" width="420" height="96">
<p>Independent asbestos and designated substances consulting for {REGIONS}. We never remove or abate anything and take no referral fees.</p></div>
<div><h4>Programs</h4><ul>
<li><a href="building-owners.html">Building programs</a></li><li><a href="landlords.html">Landlords and condos</a></li>
<li><a href="contractors.html">Cleared-to-Start Pass</a></li><li><a href="services.html">Reports and prices</a></li>
<li><a href="employers.html">Designated substances at work</a></li><li><a href="obligation-check.html">Obligation Check</a></li></ul></div>
<div><h4>Where we work</h4><ul>{"".join(f'<li><a href="{h}">Asbestos testing in {t}</a></li>' for h, t in CITIES)}</ul></div>
<div><h4>Guides and contact</h4><ul>{"".join(f'<li><a href="{h}">{t}</a></li>' for h, t, _ in GUIDES)}{contact}<li><a href="about.html">How we work</a></li></ul></div>
</div>
<div class="foot-legal"><span>© {YEAR} {e(SITE['legal'])}, operating as {e(SITE['online'])}. Prices in CAD before HST (13%). Lab results in 5 business days.</span><a href="privacy.html">Privacy notice</a></div>
</div></footer>
{action_bar(fname)}
<script src="assets/config.js?v={ASSET_V}"></script>
<script src="assets/site.js?v={ASSET_V}"></script>
</body></html>"""

BIZ_ID = SITE["domain"] + "/#business"
def page(fname, title, desc, body, active=None, schema=None, extra_js=""):
    import re
    PAGES.append(fname)
    schemas = schema if isinstance(schema, list) else ([schema] if schema else [])
    if fname not in ("index.html", "404.html"):
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        name = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else title
        schemas.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": H.unescape(name), "item": SITE["domain"] + "/" + fname}]})
    doc = head(title, desc, fname, schemas or None) + header(active) + body + footer(fname).replace("<script src=\"assets/config.js", extra_js + "<script src=\"assets/config.js", 1)
    open(os.path.join(ROOT, fname), "w").write(doc)

def cta(title="Find out what applies to you in two minutes.", text="Answer a few questions and the Obligation Check tells you which duties you carry, which program fits and what the first step costs.", href="obligation-check.html"):
    return f"""<section class="cta-band"><div class="wrap"><div><h2>{title}</h2><p>{text}</p></div>
<div class="btn-row"><a class="btn" href="{href}">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></section>"""

def crumbs(*items):
    parts = ['<a href="index.html">Home</a>'] + [f'<a href="{h}">{t}</a>' if h else e(t) for h, t in items]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"

def faq(items):
    html = '<section class="section white"><div class="wrap"><div class="section-head"><h2>Questions people ask</h2></div><div class="faq">' + "".join(
        f'<details><summary>{q}</summary><div class="faq-a"><p>{a}</p></div></details>' for q, a in items) + "</div></div></section>"
    import re
    sch = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in items]}
    return html, sch

def service_schema(name, desc, low):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc, "provider": {"@id": BIZ_ID},
        "areaServed": ["Windsor, ON", "Essex County, ON", "Chatham-Kent, ON", "Sarnia-Lambton, ON", "London, ON"],
        "offers": {"@type": "Offer", "priceCurrency": "CAD", "price": str(low), "description": f"From ${low} a month before HST"}}

def ul(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

def tier_table(keys, rows):
    th = "".join(f'<th scope="col"><span class="tname">{TIERS[k]["name"]}</span><span class="tprice">{plabel(k)}</span></th>' for k in keys)
    body = ""
    def cls(v): return "yes" if v == "Yes" else ("no" if v.startswith("Not included") or v in ("No", "None") else "")
    for label, vals in rows:
        tds = "".join(f'<td class="{cls(v)}">{v}</td>' if cls(v) else f"<td>{v}</td>" for v in vals)
        body += f'<tr><th scope="row">{label}</th>{tds}</tr>'
    table = f'<div class="table-wrap tier-table"><table class="data tiers wide"><thead><tr><th scope="col"><span class="small">Monthly, CAD before HST</span></th>{th}</tr></thead><tbody>{body}</tbody></table></div>'
    # Phone version: one card per tier in a snap-scrolling row, with a segmented control above it
    gid = keys[0].split("_")[0]
    seg = "".join(f'<button type="button" role="tab" aria-selected="{"true" if i == 0 else "false"}" aria-controls="tc-{k}" data-i="{i}">{TIERS[k]["name"]}</button>' for i, k in enumerate(keys))
    cards = ""
    for i, k in enumerate(keys):
        T = TIERS[k]
        dl = "".join(f'<div class="{cls(vals[i])}"><dt>{label}</dt><dd>{vals[i]}</dd></div>' for label, vals in rows if label != "Fits")
        fits = next((vals[i] for label, vals in rows if label == "Fits"), T["fits"])
        cards += f'<article class="tier-card" id="tc-{k}" role="tabpanel" aria-label="{T["name"]}"><header><h3>{T["name"]}</h3><p class="tc-price">{plabel(k)}</p><p class="tc-fits">{fits}</p></header><dl>{dl}</dl></article>'
    mobile = f'<div class="tier-cards" data-tiers><div class="seg" role="tablist" aria-label="Choose a tier"><span class="seg-thumb" aria-hidden="true"></span>{seg}</div><div class="tc-track">{cards}</div><p class="small tc-note">Monthly, CAD before HST. Swipe to compare.</p></div>'
    return table + mobile

def value_table(rows, total, program, saving=""):
    body = "".join(f'<tr><th scope="row">{a}</th><td class="num">{money(b)}</td></tr>' for a, b in rows)
    return f"""<div class="table-wrap"><table class="data"><thead><tr><th scope="col">Bought one at a time</th><th class="num" scope="col">List price</th></tr></thead>
<tbody>{body}</tbody><tfoot><tr><th scope="row">The same year à la carte</th><td class="num">{money(total)}</td></tr>
<tr><th scope="row">The same year in the program</th><td class="num">{money(program)}</td></tr></tfoot></table></div>{f'<p class="small" style="margin-top:10px">{saving}</p>' if saving else ''}"""

def start_steps(entry, entry_text):
    return f"""<div class="steps">
<div class="step"><h3>{entry}</h3><p>{entry_text}</p></div>
<div class="step"><h3>Record and register</h3><p>Your report becomes the on-site record and a live online register you can show an inspector or a contractor on a phone.</p></div>
<div class="step"><h3>Monthly coverage</h3><p>The yearly update, notices and reviews happen on schedule, and every report after that costs you the member rate.</p></div></div>"""

def segment_hero(crumb, h1, lede, seg):
    return f"""<section class="hero"><div class="wrap">{crumbs((None, crumb))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html#{seg}">Check what applies to you</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>"""

# ---------------------------------------------------------------- home
REGISTER = """<figure class="register" aria-label="Example of a live designated substance register">
<div class="reg-head"><b>Designated substance register</b><span>Example</span></div>
<div class="reg-meta"><span><strong>Last reassessed</strong> Sep 14, 2026</span><span><strong>Next due</strong> Sep 2027</span><span><strong>Pre-work reviews left</strong> 3</span></div>
<table class="reg-table"><thead><tr><th>Location</th><th>Material</th><th>Status</th></tr></thead><tbody>
<tr><td class="loc" data-mat="Pipe elbow insulation">Boiler room</td><td class="mat">Pipe elbow insulation</td><td><span class="status act">Act now</span></td></tr>
<tr><td class="loc" data-mat="9-inch floor tile and mastic">Corridor, 2nd floor</td><td class="mat">9-inch floor tile and mastic</td><td><span class="status monitor">Monitor</span></td></tr>
<tr><td class="loc" data-mat="Textured ceiling finish">Stairwell B</td><td class="mat">Textured ceiling finish</td><td><span class="status monitor">Monitor</span></td></tr>
<tr><td class="loc" data-mat="Drywall joint compound">Suite 204</td><td class="mat">Drywall joint compound</td><td><span class="status good">Good</span></td></tr>
<tr><td class="loc" data-mat="Window glazing (lead)">Front entrance</td><td class="mat">Window glazing (lead)</td><td><span class="status good">Good</span></td></tr>
</tbody></table>
<figcaption class="reg-foot">Every program includes a register like this, with photos, results and condition history.</figcaption></figure>"""

home_schema = {"@context": "https://schema.org", "@type": "ProfessionalService", "@id": BIZ_ID, "name": SITE["online"], "alternateName": SITE["legal"], "legalName": SITE["legal"],
    "knowsAbout": ["Asbestos testing", "Designated substance survey", "O. Reg. 278/05 asbestos management", "O. Reg. 490/09 exposure assessment", "Type 3 asbestos clearance", "Silica exposure monitoring", "Isocyanate air monitoring", "Lead paint testing"],
    "url": SITE["domain"] + "/", "logo": SITE["domain"] + "/assets/ncc-logo-primary.svg", "image": SITE["domain"] + "/assets/og-image.png",
    "description": "Independent asbestos and designated substances surveys, registers, abatement oversight and exposure monitoring in southwestern Ontario.",
    "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in ["Windsor-Essex", "Chatham-Kent", "Sarnia-Lambton", "London, Ontario"]],
    "address": {"@type": "PostalAddress", "addressLocality": SITE["city"], "addressRegion": "ON", "addressCountry": "CA"},
    "priceRange": "$$"}
if SITE["phone"]: home_schema["telephone"] = SITE["phone"]
if SITE["email"]: home_schema["email"] = SITE["email"]

home = f"""
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1>Asbestos and designated substance compliance, kept current all year.</h1>
<p class="lede">Independent surveys and designated substance reports when a project needs one, and a building program that keeps your asbestos record current in between. For owners, facility managers, landlords and contractors.</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="#doors">Find what fits</a></div>
<p class="area">Serving {REGIONS}.</p>
</div>
{REGISTER}
</div></section>

<section class="section tight" id="doors"><div class="wrap">
<div class="section-head"><h2>Start with what you're responsible for</h2></div>
<div class="doors">
<a class="door" href="building-owners.html"><h3>I own or manage a building</h3><p>Keep your asbestos record current, answer contractors before they drill, and stay ready for an inspector.</p><span class="go">Building programs, from $69 a month{ICON["chev"]}</span></a>
<a class="door" href="landlords.html"><h3>I rent out units or run a condo</h3><p>The same record and notices for rental and condo buildings, plus a quick check before a suite is renovated.</p><span class="go">Building programs, from $69 a month{ICON["chev"]}</span></a>
<a class="door" href="contractors.html"><h3>I'm about to open walls or floors</h3><p>A compliance desk to call before you bid or cut, and a site visit booked when a job needs testing.</p><span class="go">Cleared-to-Start Pass, from $199 a month{ICON["chev"]}</span></a>
<a class="door" href="services.html"><h3>I need a report for a project</h3><p>Designated substance surveys and reports for renovation, tenders, purchases and demolition permits.</p><span class="go">Reports from $650{ICON["chev"]}</span></a>
</div></div></section>

<section class="section white"><div class="wrap">
<div class="section-head"><h2>How it works</h2><p class="lede">The first step is free and takes two minutes.</p></div>
<div class="steps">
<div class="step"><h3>Take the Obligation Check</h3><p>A two-minute quiz that tells you which legal duties apply to your building or job, and what to do first.</p></div>
<div class="step"><h3>Bring your record up to date</h3><p>Usually a DSS update of the report you already have, or a baseline survey if there isn't one. Join a program within 30 days and the report is repriced at the member rate.</p></div>
<div class="step"><h3>Stay current</h3><p>The yearly update, notices and contractor answers are handled for a monthly fee. When a project needs a report, members pay less for it.</p></div>
</div></div></section>

<section class="section navy"><div class="wrap split">
<div class="section-head" style="margin:0"><h2>Inspectors are checking for exactly these gaps</h2>
<p class="lede">The Ministry of Labour's recent asbestos campaign focused on small and mid-sized owners and employers. The most common orders were for not following the asbestos management program and not keeping an asbestos record on site.</p>
<div class="btn-row" style="margin-top:8px"><a class="btn amber" href="guide-inspector-ready-binder.html">Get the inspector-ready checklist</a></div></div>
<div class="facts">
<div class="fact"><b>31</b><span>orders and requirements from visits to 78 workplaces in the 2023–24 asbestos-in-buildings campaign.</span></div>
<div class="fact"><b>77%</b><span>of the workplaces visited in that campaign had fewer than 50 workers.</span></div>
<div class="fact"><b>12</b><span>months: the longest an owner can go between asbestos re-inspections under O. Reg. 278/05.</span></div>
<div class="fact"><b>$2M</b><span>maximum fine for a corporation under Ontario's Occupational Health and Safety Act.</span></div>
</div></div></section>

<section class="section" id="programs"><div class="wrap">
<div class="section-head"><h2>Reports when a project needs one. A program for the rest of the year.</h2><p class="lede">A designated substance report is tied to a project, not the calendar, so no program includes one. The programs keep your record current, handle notices and contractor questions, and make every report cheaper when you do need one.</p></div>
<div class="programs">
<a class="program" href="building-owners.html"><h3>Building programs</h3><span class="price">from $69/mo</span><p>Compliance Essentials, Project Ready and Facility Partner, priced per building by size. For commercial, institutional and multi-unit residential buildings.</p></a>
<a class="program" href="contractors.html"><h3>Cleared-to-Start Pass</h3><span class="price">from $199/mo</span><p>The contractor compliance desk: pre-bid reviews of the owner's report, faster site visits and member rates on every pre-work check.</p></a>
<a class="program" href="services.html"><h3>Reports and surveys</h3><span class="price">from $650</span><p>Six report products from a limited sampling visit to a pre-demolition survey, priced by building size, lab analysis included.</p></a>
</div>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>Independent, on purpose</h2>
<p>We never remove or abate anything, we take no referral fees, and we don't sell the Cleared-to-Start Pass to abatement contractors. When we tell you a material is fine to leave in place, nobody on our side gains from the opposite answer.</p>
<p>You deal with one named consultant who knows your buildings.</p>
<p><a href="about.html">How we work</a></p></div>
<div class="prose"><h2>All 11 designated substances</h2>
<p>Asbestos, lead, mercury and silica turn up in buildings. Isocyanates, benzene, vinyl chloride, acrylonitrile, arsenic, ethylene oxide and coke oven emissions are mostly found in industrial processes. A pre-project list has to consider all of them, so every report we write does.</p>
<p><a href="services.html">See reports and prices</a></p></div>
</div></section>
""" + cta()
HOME_FAQ, HOME_FAQ_SCHEMA = faq([
 ("What are Ontario's designated substances?", "There are 11: acrylonitrile, arsenic, asbestos, benzene, coke oven emissions, ethylene oxide, isocyanates, lead, mercury, silica and vinyl chloride. Asbestos, lead, mercury and silica are the ones usually found in buildings."),
 ("How often does a building owner have to update the asbestos record?", "At least once every 12 months, and whenever new information comes to light, under O. Reg. 278/05. The record has to be kept on the premises."),
 ("Who is responsible for the designated substance list before a renovation?", "The project owner. Under section 30 of the Occupational Health and Safety Act, the owner lists every designated substance in the work area before the project begins and includes the list in the tender."),
 ("How much does it cost?", "Reports start at $650 for a limited sampling visit and $1,700 for a project-specific designated substance report, priced by building size. Building programs start at $69 a month per building and the Cleared-to-Start Pass at $199 a month. All prices are CAD before HST."),
 ("Does a program include my designated substance report?", "No, on purpose. A report is triggered by a project, not the calendar, so you'd be paying for it in years you don't need it. The program keeps your record current and gives you a member rate on every report."),
 ("How long do lab results take?", "5 business days from when the lab receives the samples. We don't offer rush analysis. If work can't wait, we leave written interim instructions on site."),
 ("Do you remove asbestos?", "No. We are independent consultants: we survey, write specifications, oversee abatement and test the air, but we never remove or abate anything and take no referral fees.")])
home = home.replace('<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', HOME_FAQ.replace('class="section white"', 'class="section"') + '<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', 1)
page("index.html", "Asbestos & Designated Substance Consulting in Windsor, ON | Noah Crowley", f"Independent asbestos and designated substance surveys and reports in {REGIONS}. Reports from $650, building programs from $69 a month.", home, schema=[home_schema, HOME_FAQ_SCHEMA])

# ---------------------------------------------------------------- building programs table
BP_ROWS = [
 ("Fits", ["Owners who need the yearly record kept current", "Contractors working in the building several times a year", "3 or more buildings, or a board or JHSC asking questions"]),
 ("Yearly record update and condition inspection", ["Once a year", "Once a year", "Twice a year"]),
 ("Hosted register and inspector binder", ["Yes", "Yes", "Yes, with a portfolio view"]),
 ("Occupier and contractor notices", ["Templates supplied", "Prepared and issued for you", "Prepared, issued and tracked"]),
 ("“Can we drill here?” desk reviews, within 1 business day", ["Not included", "6 a year", "Unlimited"]),
 ("Maintenance staff awareness training", ["Not included", "1 session a year", "2 sessions a year"]),
 ("Member rate on reports, site visits and project work", ["10% off", "15% off", "20% off"]),
 ("Extra lab layers", ["At the lab's cost", "At the lab's cost", "At the lab's cost"]),
 ("Fieldwork scheduling", ["Standard", "Within 5 business days", "Within 2 business days"]),
 ("If suspect material turns up", ["Phone advice", "Site visit next business day", "Site visit same business day"]),
 ("Board or JHSC presentation, abatement budget", ["No", "No", "Once a year"])]

def program_rules(member=True):
    return ul([
    "12-month agreement, billed monthly, or 12 months for the price of 10 paid up front. Prices are per building and depend on its size; we confirm yours in writing.",
    "No program includes a designated substance report or survey. Reports are bought when a project needs one, at your member rate. Lab costs are never marked up for members.",
    "Every program starts from a current asbestos record: a baseline survey, or a DSS update of a recent report. Sign within 30 days of receiving a DSS update and it's repriced at your member rate. Commit to the 12 months before a baseline survey and the survey is 15% off.",
    "Lab results take 5 business days from when the lab receives the samples. No rush analysis. If work can't wait, we leave written interim instructions on site.",
    "We never remove or abate anything and take no referral fees, so no result is shaped by someone with a stake in the job."])
FOUNDING = ('<p class="flag ok" style="max-width:760px">Founding clients: the first five clients in each program get 10% off the monthly fee for their first 12 months, in exchange for a short case study.</p>'
            if SITE["founding"] else "")

# ---------------------------------------------------------------- building owners
b = segment_hero("Building owners", "Building programs",
    "For owners and facility managers of commercial, institutional and multi-unit residential buildings: offices, plazas, schools, churches, clinics and small municipalities. Your 12-month asbestos update, your paper trail and your “can we drill here?” answers, handled for one monthly fee per building.", "building") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What the law asks of building owners</h3>{ul([
 "Keep an asbestos record on the premises: where each material is, its condition, and whether it is friable (O. Reg. 278/05).",
 "Re-inspect listed materials and update the record at least once every 12 months, and whenever you learn something new.",
 "Give occupiers written notice of asbestos in the areas they occupy, and tell contractors before work that may disturb it.",
 "Train maintenance workers who work on or near listed materials.",
 "Before any renovation, repair or demolition, list every designated substance in the work area and include it in the tender (OHSA s.30)."])}</div>
<div class="prose"><h2>What's at stake</h2>
<p>An owner who leaves a substance off the project list is liable to the constructor and every contractor for their losses when it turns up mid-job. The maximum OHSA fine is $2 million for a corporation and $1.5 million for a director or officer.</p>
<p>In Ontario's 2023–24 inspection campaign, the most common orders were for not following the asbestos management program and not keeping the record on site. Most of the workplaces visited had fewer than 50 workers.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Compare the programs</h2>{FOUNDING}</div>
{tier_table(["bp_ess", "bp_pr", "bp_fp"], BP_ROWS)}
<p class="small" style="margin-top:12px">Monthly, CAD before HST, per building. The price depends on the building's size; the figures above are the lowest. Facility Partner isn't offered for buildings under 5,000 sq ft. Three or more buildings get a portfolio discount.</p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>What the program is, and isn't</h2>
<p>A designated substance report is triggered by a project: a renovation, a tender, a sale, a demolition. It isn't something you need every year, so we don't bundle it into a monthly fee you'd pay in years without a project.</p>
<p>What you need every year is the record kept current, notices out, staff trained and a straight answer when a contractor asks what's in the ceiling. That's the program. When a project comes, the report costs you 10% to 20% less.</p>
<p><a href="services.html">See the report menu</a></p></div>
<div class="prose"><h2>How it starts</h2>{start_steps("DSS update", "We review your existing report, walk the building and fill any sampling gaps, from $900 depending on size. No report yet? A baseline asbestos survey starts at $2,300.")}
<h3>Included in every program</h3>{program_rules()}</div>
</div></section>
""" + cta("Is your asbestos record within 12 months?", "The Obligation Check takes two minutes and tells you which program fits your buildings.", "obligation-check.html#building")
page("building-owners.html", "Building programs | Asbestos records and registers | Noah Crowley", "Yearly asbestos record updates, notices, staff training and “can we drill here?” answers for building owners in southwestern Ontario. From $69 a month per building.", b, "building-owners.html", schema=service_schema("Building programs", "Monthly asbestos and designated substance compliance program in southwestern Ontario", 69))

# ---------------------------------------------------------------- landlords
r = segment_hero("Landlords", "Building programs for landlords and condos",
    "For landlords with five or more units, property managers and condominium corporations. A suite turns over, the crew lifts 9-inch floor tile or sands a stippled ceiling, and you now have exposed workers, a contaminated unit and an unhappy tenant. Check first, and keep the record that tells you where to look.", "rental") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What the law asks of rental owners</h3>{ul([
 "Keep an asbestos record, update it at least every 12 months, and give tenants written notice of asbestos in the areas they occupy.",
 "Tell superintendents, maintenance staff and contractors what's there before work that may disturb it.",
 "List every designated substance in the work area before a renovation or repair project begins.",
 "Older suites also hide lead paint and mercury thermostats; the same check picks them up."])}</div>
<div class="prose"><h2>Before a suite is renovated</h2>
<p>A limited sampling visit checks the one to three materials your crew will disturb, from $650 with lab analysis included. You get a written result about 7 business days after the visit, so book it before the tenant leaves.</p>
<p>Program members pay 10% to 20% less for every suite check and get extra lab layers at cost.</p>
<p><a href="guide-suite-turnover-checklist.html">Get the suite turnover checklist</a></p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>The same programs as every building</h2>{FOUNDING}</div>
{tier_table(["bp_ess", "bp_pr", "bp_fp"], BP_ROWS)}
<p class="small" style="margin-top:12px">Monthly, CAD before HST, per building, priced by the building's size. Condo boards usually choose Facility Partner for the yearly board presentation and abatement budget for reserve fund planning.</p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>How it starts</h2>{start_steps("DSS update", "We bring your existing report up to date, from $900 depending on size. No report yet? A baseline survey of the building starts at $2,300.")}</div>
<div class="prose"><h3>Included in every program</h3>{program_rules()}</div>
</div></section>
""" + cta("Got a suite turning over soon?", "Book a limited sampling visit, or take the Obligation Check to see which program fits your buildings.", "obligation-check.html#rental")
page("landlords.html", "Asbestos programs for landlords and condos | Noah Crowley", "Asbestos records, tenant notices and suite checks for landlords, property managers and condo corporations in Windsor-Essex and southwestern Ontario. Programs from $69 a month per building.", r, "landlords.html", schema=service_schema("Building programs for landlords", "Monthly asbestos and designated substance compliance program in southwestern Ontario", 69))

# ---------------------------------------------------------------- employers
w = f"""<section class="hero"><div class="wrap">{crumbs((None, "Employers"))}
<div class="hero-copy" style="max-width:860px"><h1>Designated substances at work</h1>
<p class="lede">For employers whose workers use, handle or store a designated substance under O. Reg. 490/09. We're not taking on ongoing workplace programs right now. Exposure monitoring is available as a one-off service, quoted per job.</p>
<div class="btn-row"><a class="btn amber" href="contact.html">Ask for a quote</a><a class="btn ghost" href="guide-designated-substance-self-check.html">Take the self-check</a></div></div></div></section>
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What O. Reg. 490/09 asks of employers</h3>{ul([
 "A written exposure assessment, made with your joint health and safety committee. Redo it after any change that could significantly affect exposure.",
 "Where workers' health may be affected, a written control program: engineering controls, work and hygiene practices, monitoring, records and training.",
 "Keep exposure under the occupational exposure limit, with air monitoring results posted, shared with the JHSC and kept for 5 years.",
 "Medical surveillance for asbestos, benzene, coke oven emissions, isocyanates, lead, mercury and silica."])}<p class="small">The regulation doesn't apply on construction projects, where Regulation 833 and the building duties govern.</p></div>
<div class="prose"><h2>What we can do</h2>
<p>A day of personal air monitoring on your process during a normal shift, with a short written report you can give your JHSC or a customer who asks. We quote each job in writing before it's booked.</p>
<p>If your building is older than 1990, it also carries the asbestos duties every owner has. See <a href="building-owners.html">building programs</a>.</p></div>
</div></section>""" + cta("Not sure which duties apply?", "The one-page self-check tells you whether O. Reg. 490/09 applies, or send us the details and we'll quote the job.", "guide-designated-substance-self-check.html")
page("employers.html", "Designated substances at work | O. Reg. 490/09 | Noah Crowley", "What O. Reg. 490/09 asks of Ontario employers, and one-off exposure monitoring quoted per job in southwestern Ontario.", w, "employers.html")

# ---------------------------------------------------------------- contractors
c = segment_hero("Contractors", "Cleared-to-Start Pass",
    "The contractor compliance desk. One number to call before you bid or cut: we review the owner's designated substance report for gaps, and when a job needs testing we're on site faster and you pay the member rate.", "contractor") + f"""
<section class="section white"><div class="wrap split">
<div class="prose"><h2>The problem it solves</h2>
<p>On small jobs the owner rarely has a current list. The law puts that duty on the owner, but you're the one standing in the room when a suspect material turns up.</p>
<p>When unlisted material is found, work has to stop except to identify it, and the Ministry, the owner, the contractor and the JHSC must be notified right away. Lab results take 5 business days, so a find on day one idles your crew or pushes the job into asbestos procedures by presumption.</p>
<p>Checking before you price the job moves that find to the quote, where the owner pays for it.</p></div>
<div class="duty"><h3>What you get</h3>{ul([
 "A compliance desk to call or email during business hours.",
 "Pre-bid reviews: send us the owner's designated substance report before you price the job, and we tell you whether it covers your work.",
 "When it doesn't, a pre-work check at your member rate: a limited sampling visit or a project report for the work area. Put the independent list price on your quote and the owner pays it.",
 "Written interim instructions on site if the client can't wait for results: leave the suspect materials alone, or proceed treating them as asbestos. You choose, and the owner gets a copy.",
 "Extra lab layers at the lab's cost, 25% off work-classification letters, and a due-diligence file for every job."])}
<p class="small">“Cleared to start” means the work area was checked before work began. It is not Type 3 clearance air testing, which the building owner retains separately, and we never do clearance on work a Pass holder abates.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Compare the passes</h2>{FOUNDING}</div>
{tier_table(["pw_start", "pw_pro", "pw_rr"], [
 ("Fits", ["Renovators and trades, 1–3 jobs a month in older buildings", "General contractors and fit-out firms, 4 or more jobs a month", "Restoration firms, for the rebuild phase of a claim"]),
 ("Compliance desk", ["Yes", "Yes", "Yes"]),
 ("Pre-bid reviews of the owner's report", ["1 a month", "3 a month", "3 a month"]),
 ("Member rate on pre-work checks", ["10% off", "15% off", "15% off"]),
 ("Site visit when a job needs testing", ["Within 5 business days", "Within 3 business days", "Next business day, Monday to Friday"]),
 ("Interim instructions on site", ["When needed", "When needed", "Every call"]),
 ("Reports branded for your client", ["No", "Yes", "Yes"]),
 ("Worker awareness", ["Toolbox talk templates", "1 live session a year", "1 live session a year"])])}
<p class="small" style="margin-top:12px">Monthly, CAD before HST, 12-month agreement. Pre-work checks are never included in the monthly fee: each one is priced per job at your member rate, from $650 at list. Lab results take 5 business days on every pass; we don't offer rush analysis.</p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>The business case</h2>
<div class="table-wrap stack"><table class="data"><thead><tr><th scope="col">A job in an older building</th><th scope="col">Without the Pass</th><th scope="col">With the Pass</th></tr></thead><tbody>
<tr><th scope="row">Before you bid</th><td data-label="Without the Pass">Guess, or price around it</td><td data-label="With the Pass">The owner's report reviewed for gaps</td></tr>
<tr><th scope="row">If testing is needed</th><td data-label="Without the Pass">Next available slot, full price</td><td data-label="With the Pass">Reserved visit, member rate</td></tr>
<tr><th scope="row">How it's paid</th><td data-label="Without the Pass">Rarely quoted, so absorbed or skipped</td><td data-label="With the Pass">A line on your quote at the list price</td></tr>
<tr><th scope="row">Suspect material</th><td data-label="Without the Pass">Found mid-job: stop work, notify, wait</td><td data-label="With the Pass">Found before mobilizing and priced into the quote</td></tr>
</tbody></table></div>
<p class="small">Prefer not to bill the line? Absorb it and market “checked before we cut” to clients and insurers instead.</p></div>
<div class="prose"><h2>How it starts</h2>{start_steps("First pre-work check", "One check on your next job in an older building at the list price, from $650, so you see a report before you commit.")}
<h3>Independence</h3><p>Each report is addressed to the building owner, because it's the owner's list. We do no removal, pay no referral fees, don't sell the Pass to abatement contractors, and never do clearance on work a Pass holder abates.</p>
<p><a href="guide-demolition-renovation-dss.html">Read the demolition and renovation DSS guide</a></p></div>
</div></section>
""" + cta("Know what's in the walls before your crew arrives.", "Book your first pre-work check, or take the Obligation Check to see which pass fits your volume.", "obligation-check.html#contractor")
page("contractors.html", "Cleared-to-Start Pass | The contractor compliance desk | Noah Crowley", "A compliance desk for contractors, renovators and restoration firms in southwestern Ontario: pre-bid reviews, faster site visits and member rates on pre-work checks. From $199 a month.", c, "contractors.html", schema=service_schema("Cleared-to-Start Pass", "Monthly compliance desk for contractors in southwestern Ontario", 199))

# ---------------------------------------------------------------- services
s = f"""<section class="hero"><div class="wrap">{crumbs((None, "Reports and prices"))}
<div class="hero-copy" style="max-width:860px"><h1>Reports and prices</h1>
<p class="lede">Every report covers Ontario's 11 designated substances and includes the lab analysis it needs, up to an allowance of sample layers set in your quote. Prices depend on the building's size; these are the starting prices. Program members pay 10% to 20% less.</p></div></div></section>
<section class="section white"><div class="wrap">
<div class="section-head"><h2>Report menu</h2></div>
<div class="table-wrap stack"><table class="data wide"><thead><tr><th scope="col">Report</th><th scope="col">When you need it</th><th scope="col">What you get</th><th scope="col">Turnaround</th><th scope="col" class="num">From</th></tr></thead><tbody>
{"".join(f'<tr><th scope="row">{n}</th><td data-label="When you need it">{w_}</td><td data-label="What you get">{g}</td><td data-label="Turnaround">{t}</td><td class="num" data-label="From">{money(p)}</td></tr>' for n, p, w_, g, t in REPORTS)}
</tbody></table></div>
<p class="small" style="margin-top:12px">CAD before HST (13%). Turnarounds are business days from the end of fieldwork and include the lab's 5 business days. We confirm a fixed price in writing before any work starts.</p>
</div></section>
<section class="section"><div class="wrap split">
<div class="prose"><h2>Samples and layers</h2>
<p>A sample is what we take from a material. The lab analyzes every layer in it: a floor tile and its glue are two layers, a plaster wall with a skim coat can be three. Your quote includes an allowance of layers sized to the building. If a building needs more, extra layers are billed per layer, and we tell you on site before we take them.</p>
<h2>Terms</h2>
{ul(["Deposit at booking: 50% on projects of $5,000 or more before HST, 30% under $5,000. The balance is due 30 days after the invoice.", "Minimum charge for a site visit: $450 before HST.", "Travel is free within 60 km of Windsor.", "Quotes are valid for 30 days."])}</div>
<div class="prose"><h2>After the report</h2>
<p>If materials have to come out, we write the abatement specification contractors bid on, review the bids, inspect the work and test the air, including Type 3 clearance. These are quoted per project. We never do the removal ourselves.</p>
<h2>Lab turnaround</h2>
<p>Lab results take 5 business days from when the lab receives the samples. We don't offer rush analysis. If work can't wait, we leave written interim instructions on site so it can continue lawfully.</p></div>
</div></section>
<section class="section white"><div class="wrap"><div class="section-head"><h2>Common jobs</h2></div>
<div class="link-list">{"".join(f'<a href="{h}"><strong>{t}</strong><span>What it involves, what it costs and how long it takes</span></a>' for h, t in TRIGGERS)}</div></div></section>""" + cta("Not sure which report you need?", "The Obligation Check points you to the right one, or send us the job details and we'll quote it.")
page("services.html", "Asbestos and designated substance reports and prices | Noah Crowley", "Designated substance reports and asbestos surveys in southwestern Ontario, priced by building size: from $650 for a limited sampling visit and $1,700 for a project-specific DSS.", s, "services.html")

# ---------------------------------------------------------------- quiz
q = f"""<section class="hero"><div class="wrap">{crumbs((None, "Obligation Check"))}
<div class="split" style="align-items:start">
<div class="hero-copy"><h1>The Obligation Check</h1><p class="lede">Answer up to five questions. You'll see which legal duties apply to you, what fits, and what the first step is. Nothing is sent until you choose to send it.</p>
<p class="small">Covers O. Reg. 278/05 (asbestos in buildings) and OHSA section 30 (designated substances on projects).</p></div>
<div class="quiz" id="quiz" aria-live="polite"><noscript>The Obligation Check needs JavaScript. You can <a href="contact.html">send us a message</a> instead.</noscript></div>
</div></div></section>"""
page("obligation-check.html", "Obligation Check | Which asbestos and designated substance duties apply to you? | Noah Crowley",
     "A two-minute quiz for building owners, landlords and contractors in Ontario: find out which asbestos and designated substance duties apply and what to do first.", q, None,
     extra_js=f"<script>window.NCC_TIERS={json.dumps({k: {kk: v[kk] for kk in ['program', 'name', 'price', 'fits', 'page', 'inc']} for k, v in TIERS.items()})};</script>\n")

# ---------------------------------------------------------------- local pages
def local_page(fname, city, region, intro, local_points, towns, extra_faq=()):
    items = [(f"How much does asbestos testing cost in {city}?", "A limited sampling visit for one to three materials starts at $650, and a project-specific designated substance report starts at $1,700. Prices depend on the building's size, and lab analysis is included up to the layer allowance in your quote."),
             ("How long do results take?", "Lab results take 5 business days from when the lab receives the samples. If work can't wait, we leave written interim instructions on site."),
             (f"Which buildings in {city} are likely to contain asbestos?", "Most buildings built after 1980 are largely free of asbestos; nearly anything older is a candidate. Floor tile and mastic, drywall compound, textured ceilings, pipe insulation and vermiculite are the usual suspects."),
             ("Are you independent of abatement contractors?", "Yes. We never remove or abate anything and take no referral fees, so our survey results aren't shaped by anyone who profits from removal.")] + list(extra_faq)
    FAQ_HTML, FAQ_SCHEMA = faq(items)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, f"Asbestos testing in {city}"))}
<div class="hero-copy" style="max-width:860px"><h1>Asbestos testing and designated substance surveys in {city}</h1>
<p class="lede">{intro}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>What we do in {region}</h2>{ul([
 '<a href="services.html">Designated substance surveys and reports</a> before renovation, repair or demolition, from $650',
 '<a href="building-owners.html">Building programs</a> that keep your asbestos record current, from $69 a month per building',
 '<a href="landlords.html">Suite checks and records</a> for landlords, property managers and condo corporations',
 '<a href="services.html">Abatement specifications, oversight, air monitoring and Type 3 clearance</a>',
 '<a href="contractors.html">A compliance desk for contractors</a>, from $199 a month'])}</div>
<div class="prose"><h2>Why it matters here</h2>{"".join(f"<p>{p}</p>" for p in local_points)}
<p class="small">We also cover {towns}.</p></div>
</div></section>
<section class="section"><div class="wrap"><div class="section-head"><h2>Common reasons people call</h2></div>
<div class="link-list">{"".join(f'<a href="{h}"><strong>{t}</strong><span>What it involves, what it costs and how long it takes</span></a>' for h, t in TRIGGERS)}</div></div></section>
""" + FAQ_HTML + cta()
    page(fname, f"Asbestos Testing {city}, ON | Designated Substance Surveys | Noah Crowley",
         f"Independent asbestos testing and designated substance surveys in {city} and {region}. Lab analysis included, lab results in 5 business days. Reports from $650.", body,
         schema=[FAQ_SCHEMA, {"@context": "https://schema.org", "@type": "Service", "name": f"Asbestos testing and designated substance surveys in {city}", "serviceType": "Asbestos testing", "provider": {"@id": BIZ_ID}, "areaServed": {"@type": "City", "name": f"{city}, Ontario"}}])

local_page("asbestos-testing-windsor.html", "Windsor", "Windsor-Essex",
    "Independent asbestos and designated substance work for Windsor building owners, landlords and contractors, with lab analysis included and lab results in 5 business days.",
    ["More than one in three Windsor dwellings was built before 1960, and most of the city's industrial and institutional floor space dates from the same era. Nearly everything built before 1980 is a candidate for asbestos-containing materials.",
     "The City of Windsor's demolition permit checklist asks for a designated substance list, so every demolition starts with a survey. We write them ready to attach to the permit and the tender."],
    "LaSalle, Tecumseh, Amherstburg and Lakeshore",
    [("Do I need a designated substance survey for a demolition permit in Windsor?", "Yes. The City of Windsor's demolition permit checklist asks for a list of designated substances. We write the survey ready to attach to the permit application and the demolition tender.")])
local_page("asbestos-testing-leamington.html", "Leamington", "Essex County",
    "Asbestos testing, designated substance surveys and suite checks for Leamington and the rest of Essex County, booked into regular route days.",
    ["Older commercial buildings, rental stock and industrial sites across Essex County carry the same duties as the city: an asbestos record updated every 12 months, and a designated substance list before any renovation or demolition.",
     "Visits in the county are grouped into route days, which keeps scheduling predictable."],
    "Kingsville, Essex, Lakeshore and the rest of Essex County")
local_page("asbestos-testing-chatham.html", "Chatham", "Chatham-Kent",
    "Designated substance surveys, asbestos record updates and air monitoring for owners, landlords and contractors across Chatham-Kent.",
    ["Older buildings changing hands or changing use, from former schools to commercial blocks, need a designated substance list before contractors are hired. We write it ready to attach to the tender.",
     "Landlords and property managers can book a limited sampling visit before a suite is renovated, so units turn over without surprises."],
    "Wallaceburg, Tilbury, Blenheim and Ridgetown")
local_page("asbestos-testing-sarnia.html", "Sarnia", "Sarnia-Lambton",
    "Asbestos surveys, abatement oversight and designated substance reports for Sarnia-Lambton's buildings, plants and contractors.",
    ["Sarnia's industrial sites add turnaround and shutdown work, which is when asbestos in older facilities gets disturbed. A current record and a project-specific report before the shutdown keep the work on schedule.",
     "Facility Partner clients get fieldwork scheduled within 2 business days and a yearly abatement budget for capital planning."],
    "Point Edward, Petrolia and the rest of Lambton County")
local_page("asbestos-testing-london.html", "London", "London and Middlesex",
    "Independent designated substance surveys and asbestos records for London-area owners, landlords and contractors.",
    ["Large national firms are strong on big portfolios and public tenders, but their minimum fees make small jobs unattractive. We work for owners who want one named consultant and a predictable price.",
     "Contractors working in older London buildings can have the owner's report reviewed before they bid, and book a pre-work check when it falls short."],
    "Strathroy, St. Thomas and the rest of Middlesex County")

# ---------------------------------------------------------------- trigger pages
def trigger_page(fname, h1, title, desc, lede, sections, related):
    secs = "".join(f'<div class="prose"><h2>{h}</h2>{b}</div>' for h, b in sections)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, h1))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>
<section class="section white"><div class="wrap split">{secs}</div></section>
<section class="section"><div class="wrap"><div class="section-head"><h2>Related</h2></div><div class="link-list">{related}</div></div></section>""" + cta()
    page(fname, title, desc, body)

def rel(*items): return "".join(f'<a href="{h}"><strong>{t}</strong><span>{s}</span></a>' for h, t, s in items)

trigger_page("asbestos-testing-before-renovation.html", "Asbestos testing before renovation",
  "Asbestos testing before renovation in Windsor and southwestern Ontario | Noah Crowley",
  "Before walls or floors open in an older building, a designated substance survey lists what the work will disturb. From $650, lab analysis included, lab results in 5 business days.",
  "Before walls, floors or ceilings open in an older building, Ontario law requires a list of every designated substance in the work area. We survey it, test it and hand you a report ready for the contractor.",
  [("What the law requires", "<p>The project owner must list all designated substances before a renovation, repair or demolition project begins and include the list in the tender (OHSA section 30). An owner who leaves one off is liable to the contractors when it turns up mid-job.</p><p>Most buildings built after 1980 are largely free of asbestos; nearly everything older is a candidate.</p>"),
   ("What we test for", ul(["Floor tile and mastic, drywall joint compound, plaster and stipple ceilings", "Pipe and boiler insulation, cement board and vermiculite", "Lead in paint, solder, pipes and glazing", "Mercury in thermostats, switches and lamps", "Silica released when concrete, masonry or tile is cut", "All 11 designated substances, as the project list requires"])),
   ("Price and timing", "<p>A limited sampling visit for one to three materials starts at $650. A project-specific report for a whole work area starts at $1,700. Both depend on the building's size and include lab analysis up to the layer allowance in your quote. Lab results take 5 business days.</p><p>If the job can't wait, we leave written interim instructions on site: which materials to treat as asbestos-containing and which procedures apply until results are in.</p>"),
   ("If you renovate often", "<p>Contractors can get the owner's report reviewed before they bid and pay member rates on every check with the <a href=\"contractors.html\">Cleared-to-Start Pass</a>, and owners pay less for every report with a <a href=\"building-owners.html\">building program</a>.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "What a survey covers and what to do if you find suspect material mid-job"),
      ("guide-suite-turnover-checklist.html", "Suite turnover checklist", "The materials to stop and test in older rental suites")))

trigger_page("designated-substance-survey-demolition-permit.html", "Designated substance survey for a demolition permit",
  "Designated substance survey for a demolition permit in Windsor | Noah Crowley",
  "The City of Windsor's demolition permit checklist asks for a designated substance list. We write the pre-demolition survey ready to attach to the permit application and the tender. From $4,000.",
  "The City of Windsor's demolition permit checklist asks for a list of designated substances. We survey the building and write a report you can attach to the permit application and the demolition tender.",
  [("What the survey covers", "<p>A destructive survey of every space, because the building is coming down: walls opened, flooring lifted and roofs cored, so concealed materials are found before demolition. It covers all 11 designated substances plus PCBs, mould and ozone-depleting refrigerants. The building has to be vacant.</p>"),
   ("What usually follows", ul(["<strong>Abatement specification:</strong> scope of work, procedure type, quantities and bid review", "<strong>Abatement oversight and air monitoring:</strong> inspections and reports during Type 2 or Type 3 work", "<strong>Type 3 clearance:</strong> visual inspection and air testing before the enclosure comes down"]) + "<p class=\"small\">Each is quoted per project.</p>"),
   ("Price and timing", "<p>A pre-demolition survey starts at $4,000 and depends on the building's size. The report takes 15 to 25 business days after fieldwork, including the lab's 5 business days. Projects of $5,000 or more take a 50% deposit at booking.</p>"),
   ("Independent from the abatement", "<p>We never remove or abate anything and take no referral fees, so the survey, the specification and the clearance are all written by someone with no stake in how much removal there is.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "Built around the City of Windsor's demolition permit checklist"),
      ("services.html", "Reports and prices", "Every report, from a limited sampling visit to a pre-demolition survey")))

trigger_page("silica-exposure-assessment.html", "Silica on renovation and demolition projects",
  "Silica on renovation and demolition projects in Ontario | Noah Crowley",
  "Silica is one of Ontario's 11 designated substances. When a project will cut concrete, masonry or tile, it belongs on the designated substance list and in the contractor's control plan.",
  "Cutting, grinding or coring concrete, masonry and tile releases respirable crystalline silica, one of Ontario's 11 designated substances. If the work will disturb it, it belongs on the project's designated substance list.",
  [("Where it shows up", "<p>Concrete, mortar, brick, block, ceramic tile, drywall and plaster all contain silica. Every project-specific report we write records where silica-containing materials are and what the planned work will do to them.</p>"),
   ("What the contractor needs", ul(["The designated substance list, with silica-generating work identified", "Work classified by type, with controls such as wet cutting and local exhaust", "Training and respiratory protection where the work calls for it"]) + "<p>We write work-classification letters for silica and lead as a project service.</p>"),
   ("Price", "<p>Silica is covered in every project-specific report, from $1,700. Exposure monitoring for employers is quoted per job; see <a href=\"employers.html\">designated substances at work</a>.</p>"),
   ("For contractors", "<p>Pass holders get 25% off work-classification letters. See the <a href=\"contractors.html\">Cleared-to-Start Pass</a>.</p>")],
  rel(("services.html", "Reports and prices", "Every report, from a limited sampling visit to a pre-demolition survey"),
      ("contractors.html", "Cleared-to-Start Pass", "The compliance desk for contractors")))

trigger_page("isocyanate-air-monitoring.html", "Isocyanate air monitoring",
  "Isocyanate air monitoring in southwestern Ontario | Noah Crowley",
  "What O. Reg. 490/09 asks of employers who spray or mix isocyanates, and one-off air monitoring quoted per job.",
  "Collision and auto body paint booths, paint lines, spray foam installers and polyurethane manufacturers work with isocyanates, one of Ontario's designated substances.",
  [("What the regulation asks", ul(["A written exposure assessment made with your JHSC, redone after any change that could significantly affect exposure", "A control program where health may be affected", "Air monitoring, with results posted for 14 days, copied to the JHSC and kept 5 years", "Medical surveillance, which applies to isocyanates"])),
   ("What we offer", "<p>We're not taking on ongoing workplace programs right now. A day of air monitoring during normal spraying, with a short written report, is available as a one-off service, quoted in writing per job.</p>"),
   ("Your building", "<p>Older shops also carry the asbestos duties every building owner has. See <a href=\"building-owners.html\">building programs</a>.</p>")],
  rel(("guide-designated-substance-self-check.html", "Designated substance self-check", "A one-page test of whether O. Reg. 490/09 applies to you"),
      ("employers.html", "Designated substances at work", "What employers need on file, and how to get a quote")))

# ---------------------------------------------------------------- guides (lead magnets)
def guide_page(fname, h1, title, desc, lede, items, after, cta_href):
    lis = "".join(f"<li><div><b>{a}</b><span>{b}</span></div></li>" for a, b in items)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, h1))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row no-print"><button class="btn ghost" type="button" onclick="window.print()">Print this checklist</button><a class="btn amber" href="{cta_href}">Take the Obligation Check</a></div></div></div></section>
<section class="section white"><div class="wrap"><div class="prose" style="max-width:820px"><ul class="checklist">{lis}</ul>{after}
<p class="small">This checklist is general guidance, not legal advice. Ontario regulations referenced: O. Reg. 278/05, OHSA section 30 and O. Reg. 490/09.</p></div></div></section>""" + cta("Want someone to check it for you?", "A DSS update brings your existing report current, from $900. Join a program within 30 days and it's repriced at your member rate.", cta_href)
    page(fname, title, desc, body)

guide_page("guide-inspector-ready-binder.html", "Inspector-ready binder checklist",
  "Inspector-ready asbestos binder checklist for Ontario building owners | Noah Crowley",
  "The items a Ministry of Labour inspector checks in an asbestos-in-buildings visit, as a printable checklist for Ontario building owners.",
  "Built on what inspectors checked in the Ministry's 2023–24 asbestos-in-buildings campaign. The most common orders were for not following the asbestos management program and not keeping the record on site.",
  [("Asbestos record, kept on the premises", "Every listed material with its location, condition, and whether it is friable."),
   ("Inspection dates within the last 12 months", "Each material re-inspected at least once every 12 months, and the record updated after any new information."),
   ("A written asbestos management program", "Who is responsible, how work near listed materials is authorized, and how you respond to damage."),
   ("Occupier notices", "Written notice to tenants and occupiers of asbestos in the areas they occupy, with dates sent."),
   ("Contractor and employer notifications", "Records that contractors were told what's there before work that could disturb it."),
   ("Training records", "Attendance for workers who work on or near listed materials."),
   ("Fallen or damaged material procedure", "Stop work, isolate, have it examined, then clean up, repair, seal, enclose or remove."),
   ("Designated substance lists for current projects", "A list of all 11 substances in each renovation, repair or demolition work area, included in the tender."),
   ("Abatement and clearance records", "Procedure type used, contractor reports, and Type 3 clearance letters where applicable.")],
  "", "obligation-check.html#building")

guide_page("guide-suite-turnover-checklist.html", "Suite turnover checklist",
  "Suite turnover asbestos checklist for Ontario landlords | Noah Crowley",
  "Which materials to stop and test before renovating a rental suite in an older building, as a printable checklist for landlords and property managers.",
  "Before a turnover crew starts in a pre-1990 suite, check whether the work will disturb any of these. If it will and you don't know what's in them, stop and test first.",
  [("9-inch floor tile and its mastic", "Common in older suites and hallways; lifting or grinding it disturbs both layers."),
   ("Drywall joint compound and plaster", "Sanding, cutting or demolishing walls releases it."),
   ("Stipple and textured ceilings", "Scraping or sanding a textured ceiling is a classic exposure."),
   ("Pipe lagging and boiler insulation", "Often in basements, risers and mechanical rooms."),
   ("Vermiculite insulation", "Loose, pebble-like fill in attics and wall cavities."),
   ("Lead paint", "Sanding or heat-stripping old painted trim, doors and windows."),
   ("Mercury thermostats", "Older dial thermostats contain mercury; remove them intact."),
   ("Tell the crew before they start", "Owners must tell workers and contractors what's there before work that may disturb it."),
   ("Keep the result with the suite record", "A written result per suite builds the record and answers the next turnover in minutes.")],
  "<p>A limited sampling visit before a turnover starts at $650, with a written result about 7 business days after the visit. <a href=\"landlords.html\">Building program</a> members pay 10% to 20% less.</p>", "obligation-check.html#rental")

guide_page("guide-designated-substance-self-check.html", "Designated substance self-check",
  "Does O. Reg. 490/09 apply to you? A designated substance self-check | Noah Crowley",
  "A one-page self-check for Ontario employers: whether O. Reg. 490/09 applies, and what an inspector will ask for.",
  "Work down the list. If you answer yes to the first two items and no to any after them, you have a gap an inspector would find.",
  [("Is a designated substance present, used, handled or stored at your workplace?", "Asbestos, acrylonitrile, arsenic, benzene, coke oven emissions, ethylene oxide, isocyanates, lead, mercury, silica or vinyl chloride."),
   ("Is a worker likely to be exposed to it?", "If so, the regulation applies. It does not apply on construction projects; dental practices are excluded for mercury and pumping gas is excluded for benzene."),
   ("Do you have a written exposure assessment made with your JHSC?", "Each committee member gets a copy, and it is redone after any change that could significantly affect exposure."),
   ("If health may be affected, do you have a written control program?", "Engineering controls, work and hygiene practices, monitoring, records and training."),
   ("Is air monitoring done and recorded?", "Results posted for 14 days, given to the JHSC, and kept for 5 years."),
   ("Is medical surveillance in place where required?", "Required for asbestos, benzene, coke oven emissions, isocyanates, lead, mercury and silica."),
   ("If respirators are used, is there a respiratory protection program?", "The most common gap in the Ministry's 2024–25 chemical exposure campaign."),
   ("Are other employers' workers protected at your site?", "Contractors are told about the substance and follow joint procedures.")],
  "<p>Exposure monitoring is available as a one-off service, quoted per job. <a href=\"contact.html\">Ask for a quote</a>.</p>", "obligation-check.html")

guide_page("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide",
  "Demolition and renovation designated substance survey guide for Windsor-Essex | Noah Crowley",
  "What a designated substance survey covers before demolition or renovation in Windsor-Essex, and what to do when you find suspect material mid-job.",
  "Built around the City of Windsor's demolition permit checklist, which asks for a designated substance list. The second half covers what to do when suspect material turns up mid-job.",
  [("The owner lists every designated substance before the project begins", "OHSA section 30 puts this on the project owner, and the list goes into the tender."),
   ("The list covers all 11 substances in the work area", "Not just asbestos: lead, mercury, silica and the rest are part of the same list."),
   ("Demolition permits need it", "The City of Windsor's demolition permit checklist asks for the designated substance list with the application."),
   ("Abatement follows the survey", "A specification sets the procedure type, quantities and scope before abatement is bid."),
   ("Type 3 work needs clearance before the enclosure comes down", "Air testing below 0.01 fibres per cc, done by someone independent of the abatement contractor."),
   ("Mid-job find: stop work except to identify the material", "Don't keep cutting or demolishing in that area."),
   ("Mid-job find: notify right away", "The constructor or employer notifies the Ministry, the owner, the contractor and the JHSC."),
   ("Mid-job find: test or presume", "Wait for lab results, 5 business days, or treat the material as asbestos-containing and follow the matching procedures."),
   ("Mid-job find: get written interim instructions", "A consultant can tell you on site which materials to treat as asbestos-containing so lawful work can continue.")],
  "<p>Contractors who check before they cut avoid all of the second half. See the <a href=\"contractors.html\">Cleared-to-Start Pass</a>.</p>", "obligation-check.html#contractor")

# ---------------------------------------------------------------- about
a = f"""<section class="hero"><div class="wrap">{crumbs((None, "How we work"))}
<div class="hero-copy" style="max-width:860px"><h1>How we work</h1><p class="lede">{e(SITE['online'])} is the online name of {e(SITE['legal'])}, an independent consultancy covering all 11 of Ontario's designated substances across {REGIONS}.</p></div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>Independence</h2><p>We never remove or abate anything and take no referral fees. We don't sell the Cleared-to-Start Pass to abatement contractors, and we don't do clearance on work a Pass holder abates. It's written into every agreement.</p>
<h2>One named consultant</h2><p>You deal with the same person who walks your building, writes your report and answers your pre-work questions.</p></div>
<div class="prose"><h2>How pricing works</h2><p>Reports are priced by the building's size and include lab analysis up to an allowance of sample layers set in your quote. The lab analyzes every layer of a sample, so if a building needs more, we tell you on site before we take them. Lab results take 5 business days; we don't offer rush analysis.</p>
<p>Programs run on 12-month agreements at a monthly fee per building. They keep your record current and give you a member rate on reports; they never include a report themselves.</p>
<h2>Where we work</h2><p>{", ".join(f'<a href="{h}">{t}</a>' for h, t in CITIES)}, and the towns around them.</p></div>
</div></section>""" + cta()
page("about.html", "How we work | Independent asbestos consulting | Noah Crowley", f"An independent asbestos and designated substances consultancy for {REGIONS}. No removal work, no referral fees, one named consultant.", a)

# ---------------------------------------------------------------- contact
cb = contact_bits()
rows = []
if SITE["phone"]: rows.append(f'<a class="contact-row" href="{tel()}">{ICON["phone"]}<span><b>{e(SITE["phone"])}</b><small>Call us</small></span></a>')
if SITE["email"]: rows.append(f'<a class="contact-row" href="mailto:{e(SITE["email"])}"><svg class="i" viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5.5" width="18" height="13" rx="2.5"/><path d="M4 7.5l8 5.5 8-5.5"/></svg><span><b>{e(SITE["email"])}</b><small>We reply within one business day</small></span></a>')
contact_side = ('<div class="contact-list">' + "".join(rows) + "</div>") if rows else ""
ct = f"""<section class="hero"><div class="wrap">{crumbs((None, "Contact"))}
<div class="split">
<div class="hero-copy"><h1>Talk to us about a building, a workplace or a job</h1>
<p class="lede">Tell us what you're dealing with and we'll reply within one business day with a price or a time to visit.</p>
{contact_side}
<div id="book" class="duty"><h3>Prefer to book a call?</h3><p>Pick a 15-minute slot and we'll call you.</p><div class="btn-row"><a class="btn" href="contact.html#book" data-book>{ICON["cal"]}Book a call</a></div></div>
<p class="area">Serving {REGIONS}.</p></div>
<form class="form panel" data-form data-name="contact">
<input type="hidden" name="_subject" value="Website enquiry">
<div class="row2"><label class="field">Your name<input name="name" required autocomplete="name"></label><label class="field">Company<input name="company" autocomplete="organization"></label></div>
<div class="row2"><label class="field">Email<input name="email" type="email" required autocomplete="email" autocapitalize="none" spellcheck="false"></label><label class="field">Phone<input name="phone" type="tel" inputmode="tel" autocomplete="tel"></label></div>
<label class="field">What do you need?<select name="need">
<option>A designated substance survey or report for a project</option><option>Updating the asbestos record for my building</option>
<option>A building program for one or more buildings</option><option>A suite check before a rental unit is renovated</option>
<option>The Cleared-to-Start Pass for my contracting business</option><option>Abatement specification, oversight or Type 3 clearance</option><option>Exposure monitoring for my workplace</option><option>Something else</option></select></label>
<label class="field">Site address (optional)<input name="site_address" autocomplete="street-address"></label>
<label class="field">Details<textarea name="message" placeholder="Building age, size, what work is planned and when"></textarea></label>
<label class="check"><input type="checkbox" name="consent_updates" value="yes"> Also send me occasional compliance reminders and updates by email. You can unsubscribe at any time.</label>
<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website_url" tabindex="-1" autocomplete="off"></label></div>
<button class="btn block" type="submit">Send message</button>
<p class="small">We use your details only to reply to this request. See our <a href="privacy.html">privacy notice</a>.</p>
</form></div></div></section>"""
page("contact.html", "Contact | Noah Crowley Asbestos and Designated Substances Consulting", f"Ask for a designated substance survey, an asbestos record update, a building program or a contractor Pass quote in {REGIONS}.", ct, "contact.html")

# ---------------------------------------------------------------- privacy
pv = f"""<section class="hero"><div class="wrap">{crumbs((None, "Privacy notice"))}
<div class="prose"><h1>Privacy notice</h1>
<p>{e(SITE['legal'])}, operating as {e(SITE['online'])}, collects only the personal information you choose to send us through this website.</p>
<h2>What we collect and why</h2>
<p>When you send a form or the Obligation Check result, we receive your name, company, email, phone, site address and the answers or details you provide. We use them to reply, to quote and to deliver the service you ask for.</p>
<h2>Email</h2>
<p>We send commercial emails only with your consent or where Canada's Anti-Spam Legislation otherwise allows it. The reminders checkbox on our forms is optional and unticked by default. Every email we send includes a way to unsubscribe, and we act on unsubscribe requests within 10 business days.</p>
<h2>Who processes it</h2>
<p>Form submissions are delivered to us by our form provider, and calls are booked through our scheduling provider. Fonts are served from this website, not a third party. We don't sell or rent personal information, and this site does not use advertising trackers.</p>
<h2>Keeping and correcting it</h2>
<p>We keep enquiry records for as long as needed to serve you and meet our legal and insurance obligations. You can ask to see, correct or delete your information by contacting us{(" at " + e(SITE['email'])) if SITE['email'] else ' through the <a href="contact.html">contact page</a>'}.</p>
<p class="small">Last updated {date.today().strftime("%B %-d, %Y")}.</p>
</div></div></section>"""
page("privacy.html", "Privacy notice | Noah Crowley Consulting", "How Noah Crowley Consulting collects, uses and protects the information you send through this website.", pv)

# ---------------------------------------------------------------- 404
nf = """<section class="hero"><div class="wrap"><div class="prose"><h1>That page isn't here</h1>
<p class="lede">The link may be old or mistyped. Start from one of these instead.</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="index.html">Go to the home page</a></div></div></div></section>"""
page("404.html", "Page not found | Noah Crowley", "This page doesn't exist.", nf)

# ---------------------------------------------------------------- sitemap, robots
today = date.today().isoformat()
urls = "".join(f"<url><loc>{SITE['domain']}/{'' if p == 'index.html' else p}</loc><lastmod>{today}</lastmod></url>" for p in PAGES if p != "404.html")
open(os.path.join(ROOT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
open(os.path.join(ROOT, "CNAME"), "w").write(SITE["domain"].replace("https://", "") + "\n")
open(os.path.join(ROOT, ".nojekyll"), "w").write("")
print(len(PAGES), "pages built")
