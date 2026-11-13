"""Builds the Noah Crowley Asbestos and Designated Substances Consulting website.
Run:  python3 tools/build.py   (from the repo root). Writes the .html files, sitemap.xml and robots.txt.
All copy is drawn from the NCC business plan. Every price, rate, turnaround and inclusion count comes from tools/prices.json
(the NCC price list, generated from the Price Guide): copy writes [[tokens]] and tools/prices.py fills them. Never type a
price here; the build stops if you do. Edit SITE below for contact details, then rebuild."""
import json, os, re, sys, hashlib, html as H
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from prices import P, NUM, fill, deep_fill, lint_sources, check_output
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
    "founder": "Noah Crowley",
    # Profiles that confirm this is one business across the web. Add the Google Business Profile, Bing Places
    # and LinkedIn links here once they exist, then rebuild.
    "sameAs": ["https://x.com/CrowleyConsult"],
}
GUIDES_REVIEWED = "2026-11-09"   # change when the guides are actually re-checked, then rebuild
REGIONS = "Windsor-Essex, Chatham-Kent, Sarnia-Lambton and London"
YEAR = date.today().year
e = H.escape
ASSET_V = hashlib.sha1(b"".join(open(os.path.join(ROOT, "assets", f), "rb").read() for f in ("site.css", "site.js", "config.js", "ncc-rules.js"))).hexdigest()[:8]

# ---------------------------------------------------------------- tiers (from tools/prices.json)
# The website may quote only the public "from" prices in the price book. Anything more specific is quoted per building.
PRICE_BOOK = P["stamp"]["pb"]
TIERS = {
 "bp_ess": dict(program="Building programs", name=P["programs"]["ce"]["name"], price=NUM["m"]["ce"], fits="Owners who need the yearly record kept current", page="building-owners.html",
   inc=["Yearly asbestos record update and visual condition inspection", "Client register snapshot after each change, and an on-site inspector binder", "Occupier and contractor notice templates", "Annual compliance letter for insurers, lenders and tenants", "[[d.ce]] off reports, site visits and project work", "Phone advice if suspect material turns up"]),
 "bp_pr": dict(program="Building programs", name=P["programs"]["pr"]["name"], price=NUM["m"]["pr"], fits="Buildings where contractors are working several times a year", page="building-owners.html",
   inc=["Yearly asbestos record update and visual condition inspection", "Notices prepared and issued to occupiers and contractors for you", "[[deskN.pr]] written “can we drill here?” desk reviews a year, answered within [[deskReply]] business day", "[[train.pr]] maintenance staff awareness session[[pl:train.pr]] a year", "[[d.pr]] off reports, site visits and project work", "Fieldwork booked within [[sched.pr]] business days; site visit the next business day if something turns up"]),
 "bp_fp": dict(program="Building programs", name=P["programs"]["fp"]["name"], price=NUM["m"]["fp"], fits="Three or more buildings, or a board or JHSC asking questions", page="building-owners.html",
   inc=["Record update and condition inspection twice a year", "Notices prepared, issued and tracked", "Unlimited written desk reviews, answered within [[deskReply]] business day", "[[train.fp]] staff awareness session[[pl:train.fp]] a year and a yearly board or JHSC presentation", "[[d.fp]] off reports, site visits and project work", "Fieldwork within [[sched.fp]] business days, a same-day visit if something turns up, and a yearly abatement budget"]),
 "pw_start": dict(program="Cleared-to-Start Pass", name=P["passes"]["starter"]["short"], price=NUM["m"]["starter"], fits="Renovators and trades with [[jobs.starter]] jobs a month in older buildings", page="contractors.html",
   inc=["A compliance desk to call before you bid or cut, business hours", "[[prebid.starter]] pre-bid review[[pl:prebid.starter]] of the owner's designated substance report a month", "Site visit within [[visit.starter]] business days when a job needs testing", "[[d.starter]] off pre-work checks", "Written interim instructions on site when a job can't wait", "[[classLetterOff]] off work-classification letters, a due-diligence file per job, toolbox talk templates"]),
 "pw_pro": dict(program="Cleared-to-Start Pass", name=P["passes"]["pro"]["short"], price=NUM["m"]["pro"], fits="General contractors and fit-out firms with [[jobs.pro]] jobs a month", page="contractors.html",
   inc=["The compliance desk, business hours", "[[prebid.pro]] pre-bid review[[pl:prebid.pro]] a month", "Site visit within [[visit.pro]] business days", "[[d.pro]] off pre-work checks", "Reports branded for your client", "[[aware.pro]] live worker awareness session[[pl:aware.pro]] a year"]),
 "pw_rr": dict(program="Cleared-to-Start Pass", name=P["passes"]["rp"]["short"], price=NUM["m"]["rp"], fits="Fire, flood and mould restoration firms, for the rebuild phase of a claim", page="contractors.html",
   inc=["Next-business-day site visits, Monday to Friday", "The compliance desk, business hours", "[[prebid.rp]] pre-bid review[[pl:prebid.rp]] a month", "[[d.rp]] off pre-work checks", "Written interim instructions on every call, adjuster-ready reports", "Reports branded for your client and [[aware.rp]] worker awareness session[[pl:aware.rp]] a year"]),
}

# The public report menu: the lowest price of each product, always said as "from".
REPORTS = [
 ("Limited sampling visit", NUM["from"]["limited"], "One to three suspect materials before a small repair: one floor, one pipe run, one wall", "A letter with lab results and the work classification for the planned job", "About [[ta.limited]] business days"),
 ("DSS update or re-assessment", NUM["from"]["update"], "An existing report that is out of date, or another firm's report that fell short", "A walk-through, gap sampling and a current, tender-ready report", "[[ta.updateNo]] business days; [[ta.updateS]] with sampling"),
 ("Project-specific DSS", NUM["from"]["project"], "Renovation, repair or a tender for one work area", "All 11 designated substances in the work area, ready to attach to the tender", "[[ta.project]] business days"),
 ("Asbestos building survey", NUM["from"]["survey"], "No survey on file for the building, or the start of a building program", "The whole-building inventory that becomes your O. Reg. 278/05 record", "[[ta.survey]] business days"),
 ("Full-building DSS and hazardous materials survey", NUM["from"]["full"], "Acquisition, capital planning, several projects in one building", "All 11 substances plus PCBs, mould and refrigerants across the building", "[[ta.full]] business days"),
 ("Pre-demolition DSS", NUM["from"]["predemo"], "A vacant building coming down, or a demolition permit", "A destructive survey of every space so materials can come out before demolition", "[[ta.predemo]] business days"),
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
            ("designated-substance-survey-demolition-permit.html", "Designated substance survey for a demolition permit")]
# Pages for services NCC can't sell yet (workplace exposure monitoring waits on a hygienist arrangement, Toolkit
# backlog b04 / b-exposure-services). They still build so old links keep working, but carry noindex, stay out of
# the sitemap, and nothing on the site links to them. To relaunch: add the two pages back to TRIGGERS, put the
# employers link back in the footer, and empty HIDDEN.
HIDDEN = {"employers.html", "silica-exposure-assessment.html", "isocyanate-air-monitoring.html"}
GUIDES = [("guide-inspector-ready-binder.html", "Inspector-ready binder checklist", "For building owners"),
          ("guide-suite-turnover-checklist.html", "Suite turnover checklist", "For landlords and property managers"),
          ("guide-designated-substance-self-check.html", "Designated substance self-check", "For employers"),
          ("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "For contractors")]
PAGES = []

# Each page's "last changed" date lives in tools/lastmod.json as {page: {hash, date}}. A page's date moves to
# today only when its content actually changes, so sitemap.xml <lastmod> stays truthful (search engines stop
# trusting lastmod if it moves on every rebuild). The asset ?v= stamps and the footer year are left out of the
# hash. Write LASTMOD_TOKEN in a page body to show that page's own last-changed date (the privacy notice does).
LASTMOD_FILE = os.path.join(ROOT, "tools", "lastmod.json")
LASTMOD = json.load(open(LASTMOD_FILE)) if os.path.exists(LASTMOD_FILE) else {}
TODAY = date.today().isoformat()
LASTMOD_TOKEN = "__LASTMOD__"
def fingerprint(doc):
    doc = re.sub(r"\?v=[0-9a-f]{8}", "", doc).replace(f"© {YEAR} ", "© ")
    return hashlib.sha1(doc.encode()).hexdigest()
def nice_date(iso): return date.fromisoformat(iso).strftime("%B %-d, %Y")

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
{'<meta name="robots" content="noindex, follow">' + chr(10) if fname in HIDDEN else ""}<link rel="canonical" href="{url}">
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
<a class="brand" href="index.html" aria-label="{e(SITE['online'])}, home"><img src="assets/ncc-logo-online-compact.svg" alt="{e(SITE['online'])}" width="551" height="128"></a>
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
<div class="foot-brand"><img src="assets/ncc-logo-online-compact-reverse.svg" alt="{e(SITE['online'])}" width="413" height="96">
<p>Independent asbestos and designated substances consulting for {REGIONS}. We never remove or abate anything and take no referral fees.</p></div>
<div><h4>Programs</h4><ul>
<li><a href="building-owners.html">Building programs</a></li><li><a href="landlords.html">Landlords and condos</a></li>
<li><a href="contractors.html">Cleared-to-Start Pass</a></li><li><a href="services.html">Reports and prices</a></li>
<li><a href="obligation-check.html">Obligation Check</a></li></ul></div>
<div><h4>Where we work</h4><ul>{"".join(f'<li><a href="{h}">Asbestos testing in {t}</a></li>' for h, t in CITIES)}</ul></div>
<div><h4>Guides and contact</h4><ul>{"".join(f'<li><a href="{h}">{t}</a></li>' for h, t, _ in GUIDES)}{contact}<li><a href="about.html">How we work</a></li></ul></div>
</div>
<div class="foot-legal"><span>© {YEAR} {e(SITE['legal'])}, operating as {e(SITE['online'])}. Prices in CAD before HST ([[hst]]). Lab results in [[labDays]] business days.</span><a href="privacy.html">Privacy notice</a></div>
</div></footer>
{action_bar(fname)}
<script src="assets/config.js?v={ASSET_V}"></script>
<script src="assets/site.js?v={ASSET_V}"></script>
</body></html>"""

BIZ_ID = SITE["domain"] + "/#business"
def page(fname, title, desc, body, active=None, schema=None, extra_js=""):
    import re
    PAGES.append(fname)
    schemas = deep_fill(schema if isinstance(schema, list) else ([schema] if schema else []))
    if fname not in ("index.html", "404.html"):
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        name = re.sub(r"<[^>]+>", "", m.group(1)).strip() if m else title
        schemas.append({"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": SITE["domain"] + "/"},
            {"@type": "ListItem", "position": 2, "name": H.unescape(name), "item": SITE["domain"] + "/" + fname}]})
    doc = fill(head(title, desc, fname, schemas or None) + header(active) + body + footer(fname).replace("<script src=\"assets/config.js", extra_js + "<script src=\"assets/config.js", 1))
    fp = fingerprint(doc)
    if LASTMOD.get(fname, {}).get("hash") != fp:
        LASTMOD[fname] = {"hash": fp, "date": TODAY}
    open(os.path.join(ROOT, fname), "w").write(doc.replace(LASTMOD_TOKEN, nice_date(LASTMOD[fname]["date"])))

DSS_CHECK = '<p class="dss-check"><a href="obligation-check.html#project">Not sure if your project needs a DSS? <strong>Check in 60 seconds</strong></a></p>'

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
        "offers": {"@type": "Offer", "priceCurrency": "CAD", "price": str(low), "description": f"From ${low:,} a month before HST"}}

def ul(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

def tier_table(keys, rows):
    th = "".join(f'<th scope="col"><span class="tname">{TIERS[k]["name"]}</span><span class="tprice">{plabel(k)}</span></th>' for k in keys)
    body = ""
    def cls(v): return "yes" if v == "Yes" else ("no" if v.startswith("Not included") or v in ("No", "None") else "")
    rows = [(fill(label), [fill(v) for v in vals]) for label, vals in rows]
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

def start_steps(entry, entry_text, contractor=False):
    if contractor:
        return f"""<div class="steps">
<div class="step"><h3>{entry}</h3><p>{entry_text}</p></div>
<div class="step"><h3>Your due-diligence file</h3><p>Each report goes to the building owner, because it's the owner's list, with a copy for you to keep with the job.</p></div>
<div class="step"><h3>Monthly coverage</h3><p>Pre-bid reviews, the compliance desk and faster site visits run every month, and every check after that costs you the member rate.</p></div></div>"""
    return f"""<div class="steps">
<div class="step"><h3>{entry}</h3><p>{entry_text}</p></div>
<div class="step"><h3>Record and register</h3><p>Your report becomes the on-site record and a register snapshot, refreshed after each change, that you can show an inspector or a contractor on a phone. <a href="register-example.html">See an example</a></p></div>
<div class="step"><h3>Monthly coverage</h3><p>The yearly update, notices and reviews happen on schedule, and every report after that costs you the member rate.</p></div></div>"""

def segment_hero(crumb, h1, lede, seg):
    return f"""<section class="hero"><div class="wrap">{crumbs((None, crumb))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html#{seg}">Check what applies to you</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>"""

# ---------------------------------------------------------------- home
# ---------------------------------------------------------------- the register (homepage card and the example page)
# Example data only: invented buildings, shown to explain what a program client sees. Dates are ISO; quantities metric with imperial in brackets.
ST_LABEL = {"act": "Act now", "monitor": "Monitor", "good": "Good"}
MARK = ('<svg class="reg-mark" viewBox="0 0 512 512" aria-hidden="true"><polygon pathLength="1" points="256,75.78 412.08,165.89 412.08,346.11 256,436.22 99.92,346.11 99.92,165.89"/>'
        '<line pathLength="1" x1="180.97" y1="264.68" x2="235.95" y2="183.18"/><line pathLength="1" class="am" x1="210.19" y1="323.91" x2="301.81" y2="188.09"/><line pathLength="1" x1="276.05" y1="328.82" x2="331.03" y2="247.32"/></svg>')
def fdate(iso):
    y, m, d = map(int, iso.split("-")); return date(y, m, d).strftime("%b %-d, %Y")
# Example register: generated from the same template and data as the real client register pages, so the website
# example can't drift from what clients receive (Noah, 2026-11-13). Source files:
#   tools/register-template.html  = claude/client-register-template.html (NCC project), copied verbatim
#   tools/register-example.json   = the Brockmere demo register data (built from claude/brockmere-example-records.json
#                                    through NCC Office's survey page; photos embedded and corner-marked)
# When either changes in the project, copy it here and rebuild. Never hand-edit rows on the website.
REG_TPL = open(os.path.join(ROOT, "tools", "register-template.html")).read()
REG_DATA = json.load(open(os.path.join(ROOT, "tools", "register-example.json")))
REG_MEANS = {"act": "Repair, remove or isolate before the area is used or disturbed.", "monitor": "Leave in place; check its condition at every visit.", "good": "Leave in place; manage under the asbestos management program."}
def _ex_row(x):
    smp = x.get("samples") or []
    rid = smp[0] if smp else ("Visual ID" if x.get("basis") == "visual-acm" else "Not sampled")
    typ = x.get("friable") or ("Paint" if "lead" in (x.get("result") or "").lower() else "")
    note = (x.get("reason") or "").strip()
    spots = [z for z in x.get("spots", []) if z.get("status") != "fixed"]
    do = " ".join(filter(None, [f'{z["where"]}: {z.get("note") or z.get("action", "")}' for z in spots] + [note or REG_MEANS[x["status"]]]))
    hist = sorted({(h["date"], (h.get("condition") + ": " if h.get("condition") else "") + (h.get("note") or "")) for h in x.get("history", []) if h.get("date")}, reverse=True)
    return {"loc": x["loc"], "mat": x["mat"], "st": x["status"], "res": x["result"], "type": typ, "id": rid, "qty": x.get("qty") or "", "do": do, "hist": hist}
EX_BUILDINGS = [{"slug": b["slug"], "name": b["name"], "built": b.get("yearBuilt", ""), "last": b.get("last", ""), "next": b.get("next", ""),
                 "reviews": f'{b.get("reviewsUsed", 0)} used · ' + ("unlimited" if b.get("reviewsIncl") == -1 else f'{b.get("reviewsIncl")} included'),
                 "rows": [_ex_row(x) for x in b["lines"] if x["status"] in ("act", "monitor", "good") and x.get("base") != "ds" and not (x.get("loc") or "").startswith("Building-wide")]}
                for b in REG_DATA["buildings"]]
def write_example_register():
    """examples/register-brockmere.html: the real client register page with the demo data, framed on register-example.html."""
    data = json.dumps(REG_DATA, ensure_ascii=False).replace("</", "<\\/")
    doc = REG_TPL.replace("/*DATA*/", data, 1)
    assert "<title>" in doc
    if "<!DOCTYPE" not in doc[:200].upper():  # the template is an artifact body; a standalone page needs these
        doc = '<!DOCTYPE html>\n<html lang="en-CA">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' + doc
    doc = doc.replace("<title>", '<meta name="robots" content="noindex"><link rel="canonical" href="' + SITE["domain"] + '/register-example.html">\n<title>', 1)
    os.makedirs(os.path.join(ROOT, "examples"), exist_ok=True)
    open(os.path.join(ROOT, "examples", "register-brockmere.html"), "w").write(doc)
def reg_rows(rows, pre):
    out = []
    for i, r in enumerate(rows):
        rid = f"{pre}-{i+1}"
        hist = "".join(f'<li><span class="mono">{fdate(d)}</span><span>{e(t)}</span></li>' for d, t in r["hist"])
        out.append(f'<tr class="r" style="--i:{i}"><td class="loc" data-mat="{e(r["mat"])}"><button class="r-btn" type="button" aria-expanded="false" aria-controls="{rid}">{e(r["loc"])}<svg class="i r-chev" viewBox="0 0 24 24" aria-hidden="true"><path d="M6 9.5l6 6 6-6"/></svg></button></td>'
                   f'<td class="mat">{e(r["mat"])}</td><td><span class="status {r["st"]}">{ST_LABEL[r["st"]]}</span></td></tr>'
                   f'<tr class="rd" id="{rid}" hidden><td colspan="3"><div class="rd-in">'
                   f'<dl class="rd-grid"><div><dt>Result</dt><dd class="mono">{e(r["res"])}</dd></div><div><dt>Type</dt><dd>{e(r["type"])}</dd></div><div><dt>Sample</dt><dd class="mono">{e(r["id"])}</dd></div><div><dt>Quantity</dt><dd>{e(r["qty"])}</dd></div></dl>'
                   f'<p class="rd-do"><b>What to do</b>{e(r["do"])}</p><div class="rd-hist"><b>Condition history</b><ol>{hist}</ol></div></div></td></tr>')
    return "".join(out)
def register(b, pre, title="Designated substance register", tag="Example", foot=""):
    return f"""<figure class="register" data-register aria-label="Example of a designated substance register snapshot">
<div class="reg-head">{MARK}<b>{e(title)}</b><span>{e(tag)}</span></div>
<div class="reg-meta"><span><strong>Last reassessed</strong> <span class="mono">{fdate(b["last"])}</span></span><span><strong>Next due</strong> <span class="mono">{fdate(b["next"])}</span></span><span><strong>Pre-work reviews</strong> {e(b["reviews"])}</span></div>
<table class="reg-table"><thead><tr><th>Location</th><th>Material</th><th>Status</th></tr></thead><tbody>{reg_rows(b["rows"], pre)}</tbody></table>
{f'<figcaption class="reg-foot">{foot}</figcaption>' if foot else ""}</figure>"""
REGISTER = register(EX_BUILDINGS[0], "hr", foot='Tap a row to see the result and its history. <a href="register-example.html">See a full example register</a>')

home_schema = {"@context": "https://schema.org", "@type": "ProfessionalService", "@id": BIZ_ID, "name": SITE["legal"], "alternateName": SITE["online"], "legalName": SITE["legal"],
    "knowsAbout": ["Asbestos testing", "Designated substance survey", "O. Reg. 278/05 asbestos management", "Type 3 asbestos clearance", "Lead paint testing"],
    "url": SITE["domain"] + "/", "logo": SITE["domain"] + "/assets/ncc-logo-primary.svg", "image": SITE["domain"] + "/assets/og-image.png",
    "description": "Independent asbestos and designated substances surveys, registers, abatement oversight with air monitoring, and Type 3 clearance in southwestern Ontario.",
    "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in ["Windsor-Essex", "Chatham-Kent", "Sarnia-Lambton", "London, Ontario"]],
    "address": {"@type": "PostalAddress", "addressLocality": SITE["city"], "addressRegion": "ON", "addressCountry": "CA"},
    "priceRange": "$$"}
home_schema["founder"] = {"@type": "Person", "@id": SITE["domain"] + "/#founder", "name": SITE["founder"], "jobTitle": "Asbestos and designated substances consultant", "worksFor": {"@id": BIZ_ID}}
if SITE["sameAs"]: home_schema["sameAs"] = SITE["sameAs"]
if SITE["phone"]: home_schema["telephone"] = SITE["phone"]
if SITE["email"]: home_schema["email"] = SITE["email"]

home = f"""
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1>Asbestos and designated substance compliance, kept current all year.</h1>
<p class="lede">Independent surveys and designated substance reports when a project needs one, and a building program that keeps your asbestos record current in between. For owners, facility managers, landlords and contractors.</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="#doors">Find what fits</a></div>
{DSS_CHECK}
<p class="area">Serving {REGIONS}.</p>
</div>
{REGISTER}
</div></section>

<section class="section tight" id="doors"><div class="wrap">
<div class="section-head"><h2>Start with what you're responsible for</h2></div>
<div class="doors">
<a class="door" href="building-owners.html"><h3>I own or manage a building</h3><p>Keep your asbestos record current, answer contractors before they drill, and stay ready for an inspector.</p><span class="go">Building programs, from [[m.ce]] a month{ICON["chev"]}</span></a>
<a class="door" href="landlords.html"><h3>I rent out units or run a condo</h3><p>The same record and notices for rental and condo buildings, plus a quick check before a suite is renovated.</p><span class="go">Building programs, from [[m.ce]] a month{ICON["chev"]}</span></a>
<a class="door" href="contractors.html"><h3>I'm about to open walls or floors</h3><p>A compliance desk to call before you bid or cut, and a site visit booked when a job needs testing.</p><span class="go">Cleared-to-Start Pass, from [[m.starter]] a month{ICON["chev"]}</span></a>
<a class="door" href="services.html"><h3>I need a report for a project</h3><p>Designated substance surveys and reports for renovation, tenders, purchases and demolition permits.</p><span class="go">Reports from [[from.limited]]{ICON["chev"]}</span></a>
</div></div></section>

<section class="section white"><div class="wrap">
<div class="section-head"><h2>How it works</h2><p class="lede">The first step is free and takes two minutes.</p></div>
<div class="steps">
<div class="step"><h3>Take the Obligation Check</h3><p>A two-minute quiz that tells you which legal duties apply to your building or job, and what to do first.</p></div>
<div class="step"><h3>Bring your record up to date</h3><p>Usually a DSS update of the report you already have, or a baseline survey if there isn't one. Join a program within [[creditDays]] days and the report is repriced at the member rate.</p></div>
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
<a class="program" href="building-owners.html"><h3>Building programs</h3><span class="price">from [[m.ce]]/mo</span><p>Compliance Essentials, Project Ready and Facility Partner, priced per building by size. For commercial, institutional and multi-unit residential buildings.</p></a>
<a class="program" href="contractors.html"><h3>Cleared-to-Start Pass</h3><span class="price">from [[m.starter]]/mo</span><p>The contractor compliance desk: pre-bid reviews of the owner's report, faster site visits and member rates on every pre-work check.</p></a>
<a class="program" href="services.html"><h3>Reports and surveys</h3><span class="price">from [[from.limited]]</span><p>Six report products from a limited sampling visit to a pre-demolition survey, priced by building size, plus samples as needed.</p></a>
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
 ("How much does it cost?", "Reports start at [[from.limited]] for a limited sampling visit and [[from.project]] for a project-specific designated substance report. Each report is a report fee plus the samples taken, so the total depends on the building. Building programs start at [[m.ce]] a month per building and the Cleared-to-Start Pass at [[m.starter]] a month. All prices are CAD before HST."),
 ("Does a program include my designated substance report?", "No, on purpose. A report is triggered by a project, not the calendar, so you'd be paying for it in years you don't need it. The program keeps your record current and gives you a member rate on every report."),
 ("How long do lab results take?", "[[labDays]] business days from when the lab receives the samples. We don't offer rush analysis. If work can't wait, we leave written interim instructions on site."),
 ("Do you remove asbestos?", "No. We are independent consultants: we survey, write specifications, oversee abatement and test the air, but we never remove or abate anything and take no referral fees.")])
home = home.replace('<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', HOME_FAQ.replace('class="section white"', 'class="section"') + '<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', 1)
page("index.html", "Asbestos & Designated Substance Consulting in Windsor, ON | Noah Crowley Consulting", f"Independent asbestos and designated substance surveys and reports in {REGIONS}. Reports from [[from.limited]], building programs from [[m.ce]] a month.", home, schema=[home_schema, HOME_FAQ_SCHEMA])

# ---------------------------------------------------------------- building programs table
BP_ROWS = [
 ("Fits", ["Owners who need the yearly record kept current", "Contractors working in the building several times a year", "3 or more buildings, or a board or JHSC asking questions"]),
 ("Yearly record update and condition inspection", ["[[inspCell.ce]]", "[[inspCell.pr]]", "[[inspCell.fp]]"]),
 ("Register snapshot and inspector binder", ["Yes", "Yes", "Yes, one per building"]),
 ("Occupier and contractor notices", ["Templates supplied", "Prepared and issued for you", "Prepared, issued and tracked"]),
 ("“Can we drill here?” desk reviews, within [[deskReply]] business day", ["[[deskCell.ce]]", "[[deskCell.pr]]", "[[deskCell.fp]]"]),
 ("Maintenance staff awareness training", ["[[trainCell.ce]]", "[[trainCell.pr]]", "[[trainCell.fp]]"]),
 ("Member rate on reports, site visits and project work", ["[[d.ce]] off", "[[d.pr]] off", "[[d.fp]] off"]),
 ("Fieldwork scheduling", ["Within [[sched.ce]] business days", "Within [[sched.pr]] business days", "Within [[sched.fp]] business days"]),
 ("If suspect material turns up", ["Phone advice", "Site visit next business day", "Site visit same business day"]),
 ("Board or JHSC presentation, abatement budget", ["No", "No", "Once a year"])]

def program_rules(member=True):
    return ul([
    "[[termMonths]]-month agreement, billed monthly, or [[termMonths]] months for the price of [[prepaidMonths]] paid up front. Prices are per building and depend on its size; we confirm yours in writing.",
    "No program includes a designated substance report or survey. Reports are bought when a project needs one, at your member rate. Lab costs are never marked up for members.",
    "Every program starts from a current asbestos record: a baseline survey, or a DSS update of a recent report. Your first report, whether a new asbestos survey or a DSS update of the report you have, is priced at your program's member rate if you sign before the work. Sign within [[creditDays]] days of receiving it and the difference is credited on your first program invoice.",
    "Lab results take [[labDays]] business days from when the lab receives the samples. No rush analysis. If work can't wait, we leave written interim instructions on site.",
    "We never remove or abate anything and take no referral fees, so no result is shaped by someone with a stake in the job."])
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
<div class="section-head"><h2>Compare the programs</h2></div>
{tier_table(["bp_ess", "bp_pr", "bp_fp"], BP_ROWS)}
<p class="small" style="margin-top:12px">Monthly, CAD before HST, per building. The price depends on the building's size; the figures above are the lowest. Facility Partner isn't offered for buildings under [[classA.m2]] m² [[[classA.ft2]] sq ft].</p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>What the program is, and isn't</h2>
<p>A designated substance report is triggered by a project: a renovation, a tender, a sale, a demolition. It isn't something you need every year, so we don't bundle it into a monthly fee you'd pay in years without a project.</p>
<p>What you need every year is the record kept current, notices out, staff trained and a straight answer when a contractor asks what's in the ceiling. That's the program. When a project comes, the report costs you [[d.min]] to [[d.max]] less.</p>
<p><a href="services.html">See the report menu</a></p></div>
<div class="prose"><h2>How it starts</h2>{start_steps("DSS update", "We review your existing report, walk the building and fill any sampling gaps, from [[from.update]] plus samples. No report yet? A baseline asbestos survey starts at [[from.survey]].")}
<h3>Included in every program</h3>{program_rules()}</div>
</div></section>
""" + cta("Is your asbestos record within 12 months?", "The Obligation Check takes two minutes and tells you which program fits your buildings.", "obligation-check.html#building")
page("building-owners.html", "Building programs | Asbestos records and registers | Noah Crowley Consulting", "Yearly asbestos record updates, notices, staff training and “can we drill here?” answers for building owners in southwestern Ontario. From [[m.ce]] a month per building.", b, "building-owners.html", schema=service_schema("Building programs", "Monthly asbestos and designated substance compliance program in southwestern Ontario", NUM["m"]["ce"]))

# ---------------------------------------------------------------- landlords
r = segment_hero("Landlords", "Building programs for landlords and condos",
    "For landlords with five or more units, property managers and condominium corporations. A suite turns over, the crew lifts 23 cm [9-inch] floor tile or sands a stippled ceiling, and you now have exposed workers, a contaminated unit and an unhappy tenant. Check first, and keep the record that tells you where to look.", "rental") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What the law asks of rental owners</h3>{ul([
 "Keep an asbestos record, update it at least every 12 months, and give tenants written notice of asbestos in the areas they occupy.",
 "Tell superintendents, maintenance staff and contractors what's there before work that may disturb it.",
 "List every designated substance in the work area before a renovation or repair project begins.",
 "Older suites also hide lead paint and mercury thermostats; the same check picks them up."])}</div>
<div class="prose"><h2>Before a suite is renovated</h2>
<p>A limited sampling visit checks the one to three materials your crew will disturb, from [[from.limited]] plus samples as needed. You get a written result about [[ta.limited]] business days after the visit, so book it before the tenant leaves.</p>
<p>Program members pay [[d.min]] to [[d.max]] less on the report fee and our time on each sample for every suite check.</p>
<p><a href="guide-suite-turnover-checklist.html">Get the suite turnover checklist</a></p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>The same programs as every building</h2></div>
{tier_table(["bp_ess", "bp_pr", "bp_fp"], BP_ROWS)}
<p class="small" style="margin-top:12px">Monthly, CAD before HST, per building, priced by the building's size. Condo boards usually choose Facility Partner for the yearly board presentation and abatement budget for reserve fund planning.</p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>How it starts</h2>{start_steps("DSS update", "We bring your existing report up to date, from [[from.update]] plus samples. No report yet? A baseline survey of the building starts at [[from.survey]].")}</div>
<div class="prose"><h3>Included in every program</h3>{program_rules()}</div>
</div></section>
""" + cta("Got a suite turning over soon?", "Book a limited sampling visit, or take the Obligation Check to see which program fits your buildings.", "obligation-check.html#rental")
page("landlords.html", "Asbestos programs for landlords and condos | Noah Crowley Consulting", "Asbestos records, tenant notices and suite checks for landlords, property managers and condo corporations in Windsor-Essex and southwestern Ontario. Programs from [[m.ce]] a month per building.", r, "landlords.html", schema=service_schema("Building programs for landlords", "Monthly asbestos and designated substance compliance program in southwestern Ontario", NUM["m"]["ce"]))

# ---------------------------------------------------------------- employers
w = f"""<section class="hero"><div class="wrap">{crumbs((None, "Employers"))}
<div class="hero-copy" style="max-width:860px"><h1>Designated substances at work</h1>
<p class="lede">For employers whose workers use, handle or store a designated substance under O. Reg. 490/09. We're not taking on ongoing workplace programs right now. Workplace exposure monitoring is not available yet. Call 519-890-9654 and tell us what you need, and we'll contact you when it launches.</p>
<div class="btn-row"><a class="btn amber" href="contact.html">Leave your details</a><a class="btn ghost" href="guide-designated-substance-self-check.html">Take the self-check</a></div></div></div></section>
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What O. Reg. 490/09 asks of employers</h3>{ul([
 "A written exposure assessment, made with your joint health and safety committee. Redo it after any change that could significantly affect exposure.",
 "Where workers' health may be affected, a written control program: engineering controls, work and hygiene practices, monitoring, records and training.",
 "Keep exposure under the occupational exposure limit, with air monitoring results posted, shared with the JHSC and kept for 5 years.",
 "Medical surveillance for asbestos, benzene, coke oven emissions, isocyanates, lead, mercury and silica."])}<p class="small">The regulation doesn't apply on construction projects, where Regulation 833 and the building duties govern.</p></div>
<div class="prose"><h2>What we can do</h2>
<p>Workplace exposure monitoring is not available yet. Call 519-890-9654 and tell us what you need, and we'll contact you when it launches.</p>
<p>If your building is older than 1990, it also carries the asbestos duties every owner has. See <a href="building-owners.html">building programs</a>.</p></div>
</div></section>""" + cta("Not sure which duties apply?", "The one-page self-check tells you whether O. Reg. 490/09 applies, or leave your details and we'll contact you when exposure monitoring launches.", "guide-designated-substance-self-check.html")
page("employers.html", "Designated substances at work | O. Reg. 490/09 | Noah Crowley Consulting", "What O. Reg. 490/09 asks of Ontario employers in southwestern Ontario. Workplace exposure monitoring is not available yet.", w, "employers.html")

# ---------------------------------------------------------------- contractors
c = segment_hero("Contractors", "Cleared-to-Start Pass",
    "The contractor compliance desk. One number to call before you bid or cut: we review the owner's designated substance report for gaps, and when a job needs testing we're on site faster and you pay the member rate.", "contractor") + f"""
<section class="section white"><div class="wrap split">
<div class="prose"><h2>The problem it solves</h2>
<p>On small jobs the owner rarely has a current list. The law puts that duty on the owner, but you're the one standing in the room when a suspect material turns up.</p>
<p>When unlisted material is found, work has to stop except to identify it, and the Ministry, the owner, the contractor and the JHSC must be notified right away. Lab results take [[labDays]] business days, so a find on day one idles your crew or pushes the job into asbestos procedures by presumption.</p>
<p>Checking before you price the job moves that find to the quote, where the owner pays for it.</p></div>
<div class="duty"><h3>What you get</h3>{ul([
 "A compliance desk to call or email during business hours.",
 "Pre-bid reviews: send us the owner's designated substance report before you price the job, and we tell you whether it covers your work.",
 "When it doesn't, a pre-work check at your member rate: a limited sampling visit or a project report for the work area. Put the independent list price on your quote and the owner pays it.",
 "Written interim instructions on site if the client can't wait for results: leave the suspect materials alone, or proceed treating them as asbestos. You choose, and the owner gets a copy.",
 "[[classLetterOff]] off work-classification letters, and a due-diligence file for every job."])}
<p class="small">“Cleared to start” means the work area was checked before work began. It is not Type 3 clearance air testing, which the building owner retains separately, and we never do clearance on work a Pass holder abates.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Compare the passes</h2></div>
{tier_table(["pw_start", "pw_pro", "pw_rr"], [
 ("Fits", ["Renovators and trades, [[jobs.starter]] jobs a month in older buildings", "General contractors and fit-out firms, [[jobs.pro]] jobs a month", "Restoration firms, for the rebuild phase of a claim"]),
 ("Compliance desk", ["Yes", "Yes", "Yes"]),
 ("Pre-bid reviews of the owner's report", ["[[prebid.starter]] a month", "[[prebid.pro]] a month", "[[prebid.rp]] a month"]),
 ("Member rate on pre-work checks", ["[[d.starter]] off", "[[d.pro]] off", "[[d.rp]] off"]),
 ("Site visit when a job needs testing", ["[[visitCell.starter]]", "[[visitCell.pro]]", "[[visitCell.rp]]"]),
 ("Interim instructions on site", ["When needed", "When needed", "Every call"]),
 ("Reports branded for your client", ["No", "Yes", "Yes"]),
 ("Worker awareness", ["Toolbox talk templates", "[[aware.pro]] live session[[pl:aware.pro]] a year", "[[aware.rp]] live session[[pl:aware.rp]] a year"])])}
<p class="small" style="margin-top:12px">Monthly, CAD before HST, [[termMonths]]-month agreement. Pre-work checks are never included in the monthly fee: each one is priced per job at your member rate, from [[from.limited]] at list. Lab results take [[labDays]] business days on every pass; we don't offer rush analysis.</p>
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
<div class="prose"><h2>How it starts</h2>{start_steps("First pre-work check", "One check on your next job in an older building at the list price, from [[from.limited]], so you see a report before you commit.", contractor=True)}
<h3>Independence</h3><p>Each report is addressed to the building owner, because it's the owner's list. We do no removal, pay no referral fees, don't sell the Pass to abatement contractors, and never do clearance on work a Pass holder abates.</p>
<p><a href="guide-demolition-renovation-dss.html">Read the demolition and renovation DSS guide</a></p></div>
</div></section>
""" + cta("Know what's in the walls before your crew arrives.", "Book your first pre-work check, or take the Obligation Check to see which pass fits your volume.", "obligation-check.html#contractor")
page("contractors.html", "Cleared-to-Start Pass | The contractor compliance desk | Noah Crowley Consulting", "A compliance desk for contractors, renovators and restoration firms in southwestern Ontario: pre-bid reviews, faster site visits and member rates on pre-work checks. From [[m.starter]] a month.", c, "contractors.html", schema=service_schema("Cleared-to-Start Pass", "Monthly compliance desk for contractors in southwestern Ontario", NUM["m"]["starter"]))

# ---------------------------------------------------------------- services
SVC_FAQ_HTML, SVC_FAQ_SCHEMA = faq([
 ("How much does a designated substance report cost?", "Reports start at [[from.limited]] for a limited sampling visit and [[from.project]] for a project-specific designated substance report. Each report is a report fee plus the samples taken: [[sample.comp]] a sample ([[sample.demo]] on a demolition survey), including lab analysis of the first layer, and [[layer]] for each extra layer. All prices are CAD before HST."),
 ("Why is it priced per sample?", "The lab analyzes every layer in a sample, and buildings differ: a floor tile and its glue are two layers, a plastered wall can be three. Pricing per sample means you pay for what your building actually needs, and we ask before going over the top of your quoted range."),
 ("How long does a report take?", "From about [[ta.updateNo]] business days for a DSS update without sampling to [[ta.predemo]] business days for a pre-demolition survey. Lab results take [[labDays]] business days from when the lab receives the samples, and we don't offer rush analysis."),
 ("Is there a minimum charge or travel fee?", "The minimum charge for a site visit is [[minVisit]] before HST. Travel is free within [[freeKm]] km [[[freeMi]] mi] of Riverside Dr. and Ouellette Ave. (downtown Windsor)."),
 ("Do you do the asbestos removal?", "No. We write the abatement specification, review bids, inspect the work and test the air, including Type 3 clearance, but we never remove anything and take no referral fees."),
])
SVC_SCHEMA = {"@context": "https://schema.org", "@type": "Service", "name": "Asbestos and designated substance reports", "serviceType": "Designated substance survey",
  "provider": {"@id": BIZ_ID}, "areaServed": ["Windsor, ON", "Essex County, ON", "Chatham-Kent, ON", "Sarnia-Lambton, ON", "London, ON"],
  "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Report menu", "itemListElement": [
    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": g},
     "priceSpecification": {"@type": "PriceSpecification", "minPrice": p, "priceCurrency": "CAD", "valueAddedTaxIncluded": False}} for n, p, w_, g, t in REPORTS]}}
s = f"""<section class="hero"><div class="wrap">{crumbs((None, "Reports and prices"))}
<div class="hero-copy" style="max-width:860px"><h1>Reports and prices</h1>
<p class="lede">Every report covers Ontario's 11 designated substances and is priced as a report fee plus the samples taken. Your quote sets the report fee and an estimated range of samples for your building, and you pay for the samples actually taken. Samples are [[sample.comp]] each ([[sample.demo]] on a demolition survey), and extra layers are [[layer]] each. These are the starting prices. Program members pay [[d.min]] to [[d.max]] less on the report fee and our time on each sample; lab costs and extra layers are not discounted.</p>{DSS_CHECK}</div></div></section>
<section class="section white"><div class="wrap">
<div class="section-head"><h2>Report menu</h2></div>
<div class="table-wrap stack"><table class="data wide"><thead><tr><th scope="col">Report</th><th scope="col">When you need it</th><th scope="col">What you get</th><th scope="col">Turnaround</th><th scope="col" class="num">From</th></tr></thead><tbody>
{"".join(f'<tr><th scope="row">{n}</th><td data-label="When you need it">{w_}</td><td data-label="What you get">{g}</td><td data-label="Turnaround">{t}</td><td class="num" data-label="From">{money(p)}</td></tr>' for n, p, w_, g, t in REPORTS)}
</tbody></table></div>
<p class="small" style="margin-top:12px">CAD before HST ([[hst]]). Turnarounds are business days from the end of fieldwork and include the lab's [[labDays]] business days. We confirm the report fee and the estimated sample range in writing before any work starts, and we ask before going over the top of that range.</p>
</div></section>
<section class="section"><div class="wrap split">
<div class="prose"><h2>Samples and layers</h2>
<p>A sample is what we take from a material. The lab analyzes every layer in it: a floor tile and its glue are two layers, a plaster wall with a skim coat can be three. Each sample is [[sample.comp]] ([[sample.demo]] on a demolition survey) and includes lab analysis of its first layer. Extra layers are [[layer]] each, billed per layer analyzed. Demolition surveys take more samples, because walls, floors and ceilings are opened up.</p>
<h2>Terms</h2>
{ul(["No deposit. We invoice the report fee and samples when fieldwork ends, and the extra layers when the lab's results arrive. Lab results and the report are released once both invoices are paid; invoices are due in [[paymentDays]] days.", "Minimum charge for a site visit: [[minVisit]] before HST.", "Travel is free within [[freeKm]] km [[[freeMi]] mi] of Riverside Dr. and Ouellette Ave. (downtown Windsor).", "Quotes are valid for [[quoteValidDays]] days."])}</div>
<div class="prose"><h2>After the report</h2>
<p>If materials have to come out, we write the abatement specification contractors bid on, review the bids, inspect the work and test the air, including Type 3 clearance. These are quoted per project. We never do the removal ourselves.</p>
<h2>Lab turnaround</h2>
<p>Lab results take [[labDays]] business days from when the lab receives the samples. We don't offer rush analysis. If work can't wait, we leave written interim instructions on site so it can continue lawfully.</p></div>
</div></section>
<section class="section white"><div class="wrap"><div class="section-head"><h2>Common jobs</h2></div>
<div class="link-list">{"".join(f'<a href="{h}"><strong>{t}</strong><span>What it involves, what it costs and how long it takes</span></a>' for h, t in TRIGGERS)}</div></div></section>""" + SVC_FAQ_HTML + cta("Not sure which report you need?", "The Obligation Check points you to the right one, or send us the job details and we'll quote it.")
page("services.html", "Asbestos and designated substance reports and prices | Noah Crowley Consulting", "Designated substance reports and asbestos surveys in southwestern Ontario, priced as a report fee plus samples: from [[from.limited]] for a limited sampling visit and [[from.project]] for a project-specific DSS.", s, "services.html", schema=[SVC_SCHEMA, SVC_FAQ_SCHEMA])

# ---------------------------------------------------------------- example register (public demo of the client register snapshot)
write_example_register()
ex = f"""<section class="hero"><div class="wrap">{crumbs(("building-owners.html", "Building programs"), (None, "Example register"))}
<div class="hero-copy" style="max-width:62ch">
<h1>Your asbestos record, on any phone</h1>
<p class="lede">Every building program client gets a register snapshot like this one. Show it to an inspector, send it to a contractor before they bid, and check a material before anyone drills. A fresh snapshot is shared within [[snapshotDays]] business days of every survey, reassessment, lab result or condition change. Below is the same register page a program client receives, filled with an invented client's data.</p>
<p><a class="btn ghost" href="examples/register-brockmere.html" target="_blank" rel="noopener">Open it full screen</a></p></div>
</div></section>
<section class="section tight"><div class="wrap">
<div class="reg-frame"><iframe id="exReg" src="examples/register-brockmere.html" title="Example designated substance register (Brockmere Property Group, invented)" loading="lazy"></iframe></div>
</div></section>""" + cta("Want a register like this for your building?", "Take the Obligation Check to see which program fits, or book a free 30-minute call.", "obligation-check.html")
page("register-example.html", "Example asbestos register | What program clients see | Noah Crowley Consulting", "An example of the designated substance register snapshot every building program client gets: statuses, lab results, condition history and what to do, on any phone.", ex, "building-owners.html")

# ---------------------------------------------------------------- quiz
# What the Obligation Check (assets/site.js) shows: report "from" prices, turnarounds and next-step wording, all from the price list.
QUIZ_PUBLIC = {
 "reports": {k: [n, p] for (n, p, *_), k in zip(REPORTS, ["limited", "update", "project", "survey", "full", "demo"])},
 "labDays": "[[labDays]]", "taProjectTo": "[[ta.project.to]]", "jobsStarter": "[[jobs.starter.to]]", "jobsPro": "[[jobs.pro.to]]", "termMonths": "[[termMonths]]",
 "entry": {
  "DSS update": "We review your existing report, walk the building and fill any sampling gaps, from [[from.update]] plus samples. Sign a program within [[creditDays]] days and the update is repriced at your member rate.",
  "Baseline survey": "An asbestos building survey becomes your on-site record, from [[from.survey]] plus samples. Sign a program before the work starts and it's priced at your member rate, or sign within [[creditDays]] days of receiving it and the difference is credited on your first program invoice.",
  "First pre-work check": "One limited sampling visit or project report on your next job in an older building, at the list price (from [[from.limited]]), so you see a report before you commit.",
  "Discovery call": "A 30-minute call to scope your buildings or jobs, followed by a written proposal."}}
q = f"""<section class="hero"><div class="wrap">{crumbs((None, "Obligation Check"))}
<div class="split" style="align-items:start">
<div class="hero-copy"><h1>The Obligation Check</h1><p class="lede">Answer a few questions. You'll see which legal duties apply to you, what fits, and what the first step is. Planning a renovation or demolition? Choose the project option to see whether it needs a designated substance survey. Nothing is sent until you choose to send it.</p>
<p class="small">Covers O. Reg. 278/05 (asbestos in buildings) and OHSA section 30 (designated substances on projects). General guidance only, not a site-specific assessment.</p></div>
<div class="quiz" id="quiz" aria-live="polite"><noscript>The Obligation Check needs JavaScript. You can <a href="contact.html">send us a message</a> instead.</noscript></div>
</div></div></section>"""
page("obligation-check.html", "Obligation Check | Which asbestos and designated substance duties apply to you? | Noah Crowley Consulting",
     "A two-minute quiz for building owners, landlords and contractors in Ontario: find out which asbestos and designated substance duties apply and what to do first.", q, None,
     extra_js=f"<script src=\"assets/ncc-rules.js?v={ASSET_V}\"></script>\n<script>window.NCC_TIERS={json.dumps(deep_fill({k: {kk: v[kk] for kk in ['program', 'name', 'price', 'fits', 'page', 'inc']} for k, v in TIERS.items()}))};"
              f"window.NCC_PUBLIC={json.dumps(deep_fill(QUIZ_PUBLIC))};</script>\n")

# ---------------------------------------------------------------- local pages
# Each city page carries its own local facts: what that municipality's demolition paperwork actually asks,
# the local building stock, and city-specific questions. Keep them genuinely different: near-identical
# city pages read to Google as doorway pages. Facts were checked against the linked municipal forms (Nov 2026).
def local_page(fname, city, region, intro, permit_h2, permit, stock_h2, stock, towns, local_faq, sources):
    items = list(local_faq) + [
        (f"How much does asbestos testing cost in {city}?", "A limited sampling visit for one to three materials starts at [[from.limited]], and a project-specific designated substance report starts at [[from.project]]. Each report is priced as a report fee plus the samples taken, with the first layer of every sample analyzed by the lab included, so the total depends on the building."),
        ("How long do results take?", "Lab results take [[labDays]] business days from when the lab receives the samples. If work can't wait, we leave written interim instructions on site."),
        ("Are you independent of abatement contractors?", "Yes. We never remove or abate anything and take no referral fees, so our survey results aren't shaped by anyone who profits from removal.")]
    FAQ_HTML, FAQ_SCHEMA = faq(items)
    src = " · ".join(f'<a href="{u}" rel="noopener">{t}</a>' for t, u in sources)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, f"Asbestos testing in {city}"))}
<div class="hero-copy" style="max-width:860px"><h1>Asbestos testing and designated substance surveys in {city}</h1>
<p class="lede">{intro}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>{permit_h2}</h2>{"".join(f"<p>{x}</p>" for x in permit)}
<p class="small">Sources: {src}. Check the current form with the building department before you apply.</p></div>
<div class="prose"><h2>{stock_h2}</h2>{"".join(f"<p>{x}</p>" for x in stock)}
<p class="small">We also cover {towns}.</p></div>
</div></section>
<section class="section"><div class="wrap split">
<div class="prose"><h2>What we do in {region}</h2>{ul([
 '<a href="services.html">Designated substance surveys and reports</a> before renovation, repair or demolition, from [[from.limited]]',
 '<a href="building-owners.html">Building programs</a> that keep your asbestos record current, from [[m.ce]] a month per building',
 '<a href="landlords.html">Suite checks and records</a> for landlords, property managers and condo corporations',
 '<a href="services.html">Abatement specifications, oversight, air monitoring and Type 3 clearance</a>',
 '<a href="contractors.html">A compliance desk for contractors</a>, from [[m.starter]] a month'])}</div>
<div class="prose"><h2>Common reasons people call</h2><div class="link-list" style="grid-template-columns:1fr">{"".join(f'<a href="{h}"><strong>{t}</strong></a>' for h, t in TRIGGERS)}</div></div>
</div></section>
""" + FAQ_HTML + cta()
    page(fname, f"Asbestos Testing {city}, ON | Designated Substance Surveys | Noah Crowley Consulting",
         f"Independent asbestos testing and designated substance surveys in {region if region.startswith(city + ' and ') else city + ' and ' + region}. Reports from [[from.limited]] plus samples, lab results in [[labDays]] business days.", body,
         schema=[FAQ_SCHEMA, {"@context": "https://schema.org", "@type": "Service", "name": f"Asbestos testing and designated substance surveys in {city}", "serviceType": "Asbestos testing", "provider": {"@id": BIZ_ID}, "areaServed": {"@type": "City", "name": f"{city}, Ontario"}}])

OHSA_DUTY = "Under Ontario's Occupational Health and Safety Act, the owner must find out which designated substances are present before a renovation or demolition is tendered, and give that list to every contractor who bids."

local_page("asbestos-testing-windsor.html", "Windsor", "Windsor-Essex",
    "Independent asbestos and designated substance work for Windsor building owners, landlords and contractors, from a consultant based in the city. Sample pricing is explained up front and lab results take [[labDays]] business days.",
    "What Windsor's demolition checklist asks",
    ["The City of Windsor's demolition permit checklist (Form A.8.1) asks seven environmental questions: past industrial use of the site, whether there is a list of designated substances for the site and building, fluid storage tanks, outstanding Ministry of the Environment or Ministry of Labour orders, PCBs, ozone-depleting substances, and WHMIS hazardous products.",
     "Answer yes to any of them and the checklist says an environmental consultant must complete an Environmental Building Audit, with a dust control plan, before you apply. In a building from before 1990, the designated substances question is almost always a yes.",
     "Our pre-demolition survey answers the designated substance, PCB and refrigerant questions in one report you can attach to both the permit application and the demolition tender."],
    "Windsor's buildings",
    ["About two in five Windsor homes were built before 1961, and roughly three in four before 1991, by the 2021 Census. The oldest stock sits in and around the core: Walkerville, Sandwich and the neighbourhoods near downtown.",
     "The city's auto-era plants, warehouses, schools and churches are where the checklist's industrial-use question matters. Pipe and boiler insulation, PCB light ballasts and old refrigeration equipment all need to be found and listed before anyone cuts.",
     "More than a third of Windsor households rent, so suite turnovers never stop. A suite check before a unit is renovated tells the contractor what's in the walls, ceilings and floors."],
    "LaSalle, Tecumseh, Amherstburg and Lakeshore",
    [("Do I need a designated substance survey for a demolition permit in Windsor?", "In almost every older building, yes. The City of Windsor's demolition checklist asks whether there is a list of designated substances for the site and building, and any yes on its environmental questions means an Environmental Building Audit before you apply. We write the survey ready to attach to the permit application and the tender."),
     ("What is the Environmental Building Audit on Windsor's checklist?", "It's the consultant's report the City asks for when any of the checklist's environmental questions is answered yes: industrial use, designated substances, tanks, outstanding orders, PCBs, ozone-depleting substances or hazardous products. It has to include a dust control plan and be finished before the demolition permit application goes in.")],
    [("City of Windsor demolition permit checklist (Form A.8.1)", "https://www.citywindsor.ca/Documents/residents/building/building-permits/Demolition%20Permit%20Application%20Checklist%20-%20Form%20A.8.1.pdf")])

local_page("asbestos-testing-leamington.html", "Leamington", "Essex County",
    "Asbestos testing, designated substance surveys and suite checks for Leamington, Kingsville and the rest of Essex County, booked into regular route days from our Windsor base.",
    "Renovating or demolishing in Leamington",
    ["The Municipality of Leamington takes building and demolition permit applications online through Cloudpermit. The permit doesn't replace the survey. " + OHSA_DUTY,
     "Heritage adds steps. A property designated under the Ontario Heritage Act needs a heritage permit from Leamington before it can be demolished, and a property listed on Leamington's Register of Heritage Properties needs at least 60 days' written notice to council. Book the survey early so it isn't the last thing holding up the job."],
    "Leamington's buildings",
    ["Greenhouse growth keeps changing Leamington's farmland, and expanding operations often take in older farmhouses, barns, packing sheds and boiler buildings. Anything built before 1990 needs a designated substance list before it's renovated or taken down.",
     "Uptown Leamington's older commercial blocks and the town's rental housing carry the same duties as Windsor's: an asbestos record kept up to date at least every 12 months where asbestos is present, and a list before any work starts.",
     "Visits in the county are grouped into route days, which keeps scheduling predictable."],
    "Kingsville, Essex, Harrow and the rest of Essex County",
    [("Does Leamington require a designated substance survey for a demolition permit?", "The duty comes from the Occupational Health and Safety Act rather than the permit: the owner must identify designated substances before demolition or renovation work is tendered. Ask Leamington Building Services what they want attached to your application. We write the report so it serves both."),
     ("Do you survey farm and greenhouse buildings?", "Yes. A farm building on a farm doesn't need a demolition permit under the Building Code, but hiring contractors to take one down is still construction work, so the owner's designated substance duty still applies. We survey farmhouses, barns, packing sheds and boiler buildings before they're renovated or removed.")],
    [("Leamington building permits", "https://www.leamington.ca/municipal-services/building-services/building-permits/"),
     ("Leamington heritage permit guide", "https://www.leamington.ca/en/discover/resources/Heritage-Permit-Application-Guide.pdf")])

local_page("asbestos-testing-chatham.html", "Chatham", "Chatham-Kent",
    "Designated substance surveys, asbestos record updates and suite checks for owners, landlords and contractors across Chatham-Kent.",
    "Demolishing in Chatham-Kent",
    ["Chatham-Kent's Building Development Services has demolition applicants complete a Utility Notification Form. Its conditions remind owners that the Ministry of Labour requires an environmental survey where a designated substance such as asbestos is believed to be present, and that a Notice of Project will be required.",
     "In practice that means a designated substance survey before the demolition contract is signed, so removal can be priced and scheduled with the rest of the job instead of stopping it halfway."],
    "Chatham-Kent's buildings",
    ["Chatham-Kent is one municipality spread across Chatham, Wallaceburg, Blenheim, Ridgetown, Tilbury and dozens of smaller communities, with older main-street commercial blocks, churches, halls and schools in nearly every one of them.",
     "Surplus buildings are being turned into housing. The former St. Agnes Catholic School on Croydon Street in Chatham came down in 2025 to make way for affordable housing. Every project like that starts with a pre-demolition survey.",
     "Landlords and property managers can book a limited sampling visit before a suite is renovated, so units turn over without surprises."],
    "Wallaceburg, Tilbury, Blenheim and Ridgetown",
    [("Who arranges the survey for a demolition in Chatham-Kent, the owner or the contractor?", "The owner. " + OHSA_DUTY + " A contractor can arrange the survey on the owner's behalf, but the duty stays with the owner."),
     ("Do you cover Wallaceburg, Tilbury and the rest of Chatham-Kent?", "Yes: Wallaceburg, Tilbury, Blenheim, Ridgetown and the communities between them, as well as Chatham itself.")],
    [("Chatham-Kent Utility Notification Form", "https://www.chatham-kent.ca/apply/permits/Documents/Utility%20Notification%20Form%202024.pdf")])

local_page("asbestos-testing-sarnia.html", "Sarnia", "Sarnia-Lambton",
    "Asbestos surveys, abatement oversight and designated substance reports for Sarnia-Lambton building owners and the contractors who work in their buildings.",
    "What Sarnia's demolition application asks",
    ["The City of Sarnia's demolition application checklist asks applicants to check for designated substances under the Occupational Health and Safety Act, and points owners to the Ministry of Labour's rules on what must happen before demolition, alteration or repair is tendered.",
     "It also flags past uses that can leave other hazards behind, naming dentist offices and veterinary clinics, and sets a separate heritage step: a property on the municipal heritage register needs 60 days' written notice to council before it's demolished.",
     "Our survey covers all 11 designated substances. We record the building's past uses in the report and flag anything outside those 11 for the right specialist."],
    "Sarnia's buildings and trades",
    ["Many Sarnia trades split the year between Chemical Valley turnarounds and building work. Imperial's 2023 Sarnia turnaround alone brought in a peak of about 1,200 contractors.",
     "On the building side, the Cleared-to-Start Pass gives those contractors a compliance desk: a review of the owner's report before they bid, and a site visit when a job needs testing.",
     "Downtown Sarnia, Point Edward and the older parts of Lambton County carry the same owner duties as anywhere in Ontario: an asbestos record for buildings that contain it, and a designated substance list before any project is tendered."],
    "Point Edward, Petrolia, Corunna and the rest of Lambton County",
    [("Does Sarnia need a designated substance report before demolition?", "Sarnia's demolition application checklist asks you to check for designated substances under the Occupational Health and Safety Act. " + OHSA_DUTY + " We write the report ready for both the application and the tender."),
     ("My building used to be a dental office or a vet clinic. Does that matter?", "Sarnia's demolition checklist names those past uses as signs that radioactive materials may have been used on site. That's outside the 11 designated substances, so tell us about past uses when you book. We note them in the report and tell you who handles the follow-up.")],
    [("City of Sarnia demolition application (Feb 2026)", "https://www.sarnia.ca/app/uploads/2026/04/Demolition-Application-Feb-2026.pdf"),
     ("Imperial 2023 turnaround (Sarnia News Today)", "https://sarnianewstoday.ca/sarnia/news/2023/09/06/planned-maintenance-shutdown-at-imperial")])

local_page("asbestos-testing-london.html", "London", "London and Middlesex",
    "Independent designated substance surveys and asbestos records for London-area owners, landlords and contractors who want one named consultant and a predictable price.",
    "What London's demolition form leaves out",
    ["The City of London's demolition clearances form covers heritage review, utility sign-offs and a security deposit: $2,000 for a house, or $10 per square metre of ground floor for other buildings, up to $10,000. It doesn't ask about designated substances.",
     "That doesn't remove the duty. " + OHSA_DUTY + " A contractor who bids without that list carries the risk when the walls come open.",
     "Heritage adds time. For a property on London's Register of Cultural Heritage Resources, the owner must give council at least 60 days' written notice before demolishing, and council can move to designate it instead. Have the survey done during that window so it's ready when the permit is."],
    "London's buildings",
    ["Many of London's older neighbourhoods, from Old East Village to Wortley Village, sit inside heritage conservation districts or on the register, so demolition and major renovation there run on a longer clock.",
     "Large national firms are strong on big portfolios and public tenders, but their minimum fees make small jobs unattractive. We work for owners who want one named consultant and a predictable price.",
     "Contractors working in older London buildings can have the owner's report reviewed before they bid, and book a pre-work check when it falls short."],
    "Strathroy, St. Thomas and the rest of Middlesex County",
    [("London's demolition form doesn't mention designated substances. Do I still need a survey?", "Yes. The duty comes from the Occupational Health and Safety Act, not the permit form. " + OHSA_DUTY),
     ("How long does demolishing a heritage-listed property in London take?", "At least 60 days from the owner's written notice to council, and longer if council decides to designate the property. London's heritage planner reviews it as part of the demolition clearances.")],
    [("City of London required clearances for demolition", "https://london.ca/sites/default/files/2024-11/Required%20clearances%20for%20demolition%20permit.pdf"),
     ("City of London demolition control policy", "https://london.ca/council-policies/demolition-control")])

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
  "Asbestos testing before renovation in Windsor and southwestern Ontario | Noah Crowley Consulting",
  "Before walls or floors open in an older building, a designated substance survey lists what the work will disturb. From [[from.limited]] plus samples, lab results in [[labDays]] business days. Independent asbestos and designated substances consulting.",
  "Before walls, floors or ceilings open in an older building, Ontario law requires a list of every designated substance in the work area. We survey it, test it and hand you a report ready for the contractor.",
  [("What the law requires", "<p>The project owner must list all designated substances before a renovation, repair or demolition project begins and include the list in the tender (OHSA section 30). An owner who leaves one off is liable to the contractors when it turns up mid-job.</p><p>Any building built before 1990 is a candidate for asbestos-containing materials; newer buildings are much less likely to contain them.</p>"),
   ("What we test for", ul(["Floor tile and mastic, drywall joint compound, plaster and stipple ceilings", "Pipe and boiler insulation, cement board and vermiculite", "Lead in paint, solder, pipes and glazing", "Mercury in thermostats, switches and lamps", "Silica released when concrete, masonry or tile is cut", "All 11 designated substances, as the project list requires"])),
   ("Price and timing", "<p>A limited sampling visit for one to three materials starts at [[from.limited]]. A project-specific report for a whole work area starts at [[from.project]]. Each report is priced as a report fee plus the samples taken, with the first layer of every sample analyzed by the lab included, so the total depends on the building. Lab results take [[labDays]] business days.</p><p>If the job can't wait, we leave written interim instructions on site: which materials to treat as asbestos-containing and which procedures apply until results are in.</p>"),
   ("If you renovate often", "<p>Contractors can get the owner's report reviewed before they bid and pay member rates on every check with the <a href=\"contractors.html\">Cleared-to-Start Pass</a>, and owners pay less for every report with a <a href=\"building-owners.html\">building program</a>.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "What a survey covers and what to do if you find suspect material mid-job"),
      ("guide-suite-turnover-checklist.html", "Suite turnover checklist", "The materials to stop and test in older rental suites")))

trigger_page("designated-substance-survey-demolition-permit.html", "Designated substance survey for a demolition permit",
  "Designated substance survey for a demolition permit in Windsor | Noah Crowley Consulting",
  "The City of Windsor's demolition permit checklist asks for a designated substance list. We write the pre-demolition survey ready to attach to the permit application and the tender. From [[from.predemo]].",
  "The City of Windsor's demolition permit checklist asks for a list of designated substances. We survey the building and write a report you can attach to the permit application and the demolition tender.",
  [("What the survey covers", "<p>A destructive survey of every space, because the building is coming down: walls opened, flooring lifted and roofs cored, so concealed materials are found before demolition. It covers all 11 designated substances plus PCBs, mould and ozone-depleting refrigerants. The building has to be vacant.</p>"),
   ("What usually follows", ul(["<strong>Abatement specification:</strong> scope of work, procedure type, quantities and bid review", "<strong>Abatement oversight and air monitoring:</strong> inspections and reports during Type 2 or Type 3 work", "<strong>Type 3 clearance:</strong> visual inspection and air testing before the enclosure comes down"]) + "<p class=\"small\">Each is quoted per project.</p>"),
   ("Price and timing", "<p>A pre-demolition survey starts at [[from.predemo]], priced as a report fee plus the samples taken. Demolition surveys take more samples than a renovation report because concealed spaces are opened up. The report takes [[ta.predemo.to]] business days after fieldwork, including the lab's [[labDays]] business days. No deposit: results are released once the fieldwork and lab invoices are paid.</p>"),
   ("Independent from the abatement", "<p>We never remove or abate anything and take no referral fees, so the survey, the specification and the clearance are all written by someone with no stake in how much removal there is.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "Built around the City of Windsor's demolition permit checklist"),
      ("services.html", "Reports and prices", "Every report, from a limited sampling visit to a pre-demolition survey")))

trigger_page("silica-exposure-assessment.html", "Silica on renovation and demolition projects",
  "Silica on renovation and demolition projects in Ontario | Noah Crowley Consulting",
  "Silica is one of Ontario's 11 designated substances. When a project will cut concrete, masonry or tile, it belongs on the designated substance list and in the contractor's control plan.",
  "Cutting, grinding or coring concrete, masonry and tile releases respirable crystalline silica, one of Ontario's 11 designated substances. If the work will disturb it, it belongs on the project's designated substance list.",
  [("Where it shows up", "<p>Concrete, mortar, brick, block, ceramic tile, drywall and plaster all contain silica. Every project-specific report we write records where silica-containing materials are and what the planned work will do to them.</p>"),
   ("What the contractor needs", ul(["The designated substance list, with silica-generating work identified", "Work classified by type, with controls such as wet cutting and local exhaust", "Training and respiratory protection where the work calls for it"]) + "<p>We write work-classification letters for silica and lead as a project service.</p>"),
   ("Price", "<p>Silica is covered in every project-specific report, from [[from.project]]. Exposure monitoring is not available yet. Call <a href=\"tel:+15198909654\">519-890-9654</a> or <a href=\"contact.html\">contact us</a> to be notified when it launches.</p>"),
   ("For contractors", "<p>Pass holders get [[classLetterOff]] off work-classification letters. See the <a href=\"contractors.html\">Cleared-to-Start Pass</a>.</p>")],
  rel(("services.html", "Reports and prices", "Every report, from a limited sampling visit to a pre-demolition survey"),
      ("contractors.html", "Cleared-to-Start Pass", "The compliance desk for contractors")))

trigger_page("isocyanate-air-monitoring.html", "Isocyanate air monitoring",
  "Isocyanate air monitoring in southwestern Ontario | Noah Crowley Consulting",
  "What O. Reg. 490/09 asks of employers who spray or mix isocyanates. Exposure monitoring is not available yet.",
  "Collision and auto body paint booths, paint lines, spray foam installers and polyurethane manufacturers work with isocyanates, one of Ontario's designated substances.",
  [("What the regulation asks", ul(["A written exposure assessment made with your JHSC, redone after any change that could significantly affect exposure", "A control program where health may be affected", "Air monitoring, with results posted for 14 days, copied to the JHSC and kept 5 years", "Medical surveillance, which applies to isocyanates"])),
   ("What we offer", "<p>Exposure monitoring is not available yet. Call <a href=\"tel:+15198909654\">519-890-9654</a> or <a href=\"contact.html\">contact us</a> to be notified when it launches.</p>"),
   ("Your building", "<p>Older shops also carry the asbestos duties every building owner has. See <a href=\"building-owners.html\">building programs</a>.</p>")],
  rel(("guide-designated-substance-self-check.html", "Designated substance self-check", "A one-page test of whether O. Reg. 490/09 applies to you"),
      ("employers.html", "Designated substances at work", "What employers need on file under O. Reg. 490/09")))

# ---------------------------------------------------------------- guides (lead magnets)
def guide_page(fname, h1, title, desc, lede, items, after, cta_href):
    lis = "".join(f"<li><div><b>{a}</b><span>{b}</span></div></li>" for a, b in items)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, h1))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row no-print"><button class="btn ghost" type="button" onclick="window.print()">Print this checklist</button><a class="btn amber" href="{cta_href}">Take the Obligation Check</a></div></div></div></section>
<section class="section white"><div class="wrap"><div class="prose" style="max-width:820px"><ul class="checklist">{lis}</ul>{after}
<p class="small">Last reviewed {fdate(GUIDES_REVIEWED)} by {e(SITE['founder'])}. This checklist is general guidance, not legal advice. Ontario regulations referenced: O. Reg. 278/05, OHSA section 30 and O. Reg. 490/09.</p></div></div></section>""" + cta("Want someone to check it for you?", "A DSS update brings your existing report current, from [[from.update]] plus samples. Join a program within [[creditDays]] days and it's repriced at your member rate.", cta_href)
    art = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "url": SITE["domain"] + "/" + fname,
        "datePublished": GUIDES_REVIEWED, "dateModified": GUIDES_REVIEWED, "inLanguage": "en-CA",
        "author": {"@type": "Person", "@id": SITE["domain"] + "/#founder", "name": SITE["founder"]}, "publisher": {"@id": BIZ_ID},
        "about": ["O. Reg. 278/05", "OHSA section 30", "O. Reg. 490/09"]}
    page(fname, title, desc, body, schema=art)

guide_page("guide-inspector-ready-binder.html", "Inspector-ready binder checklist",
  "Inspector-ready asbestos binder checklist for Ontario building owners | Noah Crowley Consulting",
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
  "Suite turnover asbestos checklist for Ontario landlords | Noah Crowley Consulting",
  "Which materials to stop and test before renovating a rental suite in an older building, as a printable checklist for landlords and property managers.",
  "Before a turnover crew starts in a pre-1990 suite, check whether the work will disturb any of these. If it will and you don't know what's in them, stop and test first.",
  [("23 cm [9-inch] floor tile and its mastic", "Common in older suites and hallways; lifting or grinding it disturbs both layers."),
   ("Drywall joint compound and plaster", "Sanding, cutting or demolishing walls releases it."),
   ("Stipple and textured ceilings", "Scraping or sanding a textured ceiling is a classic exposure."),
   ("Pipe lagging and boiler insulation", "Often in basements, risers and mechanical rooms."),
   ("Vermiculite insulation", "Loose, pebble-like fill in attics and wall cavities."),
   ("Lead paint", "Sanding or heat-stripping old painted trim, doors and windows."),
   ("Mercury thermostats", "Older dial thermostats contain mercury; remove them intact."),
   ("Tell the crew before they start", "Owners must tell workers and contractors what's there before work that may disturb it."),
   ("Keep the result with the suite record", "A written result per suite builds the record and answers the next turnover in minutes.")],
  "<p>A limited sampling visit before a turnover starts at [[from.limited]], with a written result about [[ta.limited]] business days after the visit. <a href=\"landlords.html\">Building program</a> members pay [[d.min]] to [[d.max]] less.</p>", "obligation-check.html#rental")

guide_page("guide-designated-substance-self-check.html", "Designated substance self-check",
  "Does O. Reg. 490/09 apply to you? A designated substance self-check | Noah Crowley Consulting",
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
  "<p>Exposure monitoring is not available yet. Call <a href=\"tel:+15198909654\">519-890-9654</a> or <a href=\"contact.html\">contact us</a> to be notified when it launches.</p>", "obligation-check.html")

guide_page("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide",
  "Demolition and renovation designated substance survey guide for Windsor-Essex | Noah Crowley Consulting",
  "What a designated substance survey covers before demolition or renovation in Windsor-Essex, and what to do when you find suspect material mid-job.",
  "Built around the City of Windsor's demolition permit checklist, which asks for a designated substance list. The second half covers what to do when suspect material turns up mid-job.",
  [("The owner lists every designated substance before the project begins", "OHSA section 30 puts this on the project owner, and the list goes into the tender."),
   ("The list covers all 11 substances in the work area", "Not just asbestos: lead, mercury, silica and the rest are part of the same list."),
   ("Demolition permits need it", "The City of Windsor's demolition permit checklist asks for the designated substance list with the application."),
   ("Abatement follows the survey", "A specification sets the procedure type, quantities and scope before abatement is bid."),
   ("Type 3 work needs clearance before the enclosure comes down", "Air testing below 0.01 fibres per cc, done by someone independent of the abatement contractor."),
   ("Mid-job find: stop work except to identify the material", "Don't keep cutting or demolishing in that area."),
   ("Mid-job find: notify right away", "The constructor or employer notifies the Ministry, the owner, the contractor and the JHSC."),
   ("Mid-job find: test or presume", "Wait for lab results, [[labDays]] business days, or treat the material as asbestos-containing and follow the matching procedures."),
   ("Mid-job find: get written interim instructions", "A consultant can tell you on site which materials to treat as asbestos-containing so lawful work can continue.")],
  "<p>Contractors who check before they cut avoid all of the second half. See the <a href=\"contractors.html\">Cleared-to-Start Pass</a>.</p>", "obligation-check.html#contractor")

# ---------------------------------------------------------------- about
a = f"""<section class="hero"><div class="wrap">{crumbs((None, "How we work"))}
<div class="hero-copy" style="max-width:860px"><h1>How we work</h1><p class="lede">{e(SITE['online'])} is the online name of {e(SITE['legal'])}, an independent consultancy covering all 11 of Ontario's designated substances across {REGIONS}.</p></div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>Independence</h2><p>We never remove or abate anything and take no referral fees. We don't sell the Cleared-to-Start Pass to abatement contractors, and we don't do clearance on work a Pass holder abates. It's written into every agreement.</p>
<h2>One named consultant</h2><p>You deal with the same person who walks your building, writes your report and answers your pre-work questions.</p></div>
<div class="prose"><h2>How pricing works</h2><p>Reports are priced as a report fee plus the samples taken. Your quote gives an estimated range of samples, you pay for the samples actually taken, and we ask on site before going over the top of the range. Samples are [[sample.comp]] each ([[sample.demo]] on a demolition survey), including lab analysis of the first layer; extra layers are [[layer]] each. Lab results take [[labDays]] business days; we don't offer rush analysis.</p>
<p>Programs run on [[termMonths]]-month agreements at a monthly fee per building. They keep your record current and give you a member rate on reports; they never include a report themselves.</p>
<h2>Where we work</h2><p>{", ".join(f'<a href="{h}">{t}</a>' for h, t in CITIES)}, and the towns around them.</p></div>
</div></section>""" + cta()
page("about.html", "How we work | Independent asbestos consulting | Noah Crowley Consulting", f"An independent asbestos and designated substances consultancy for {REGIONS}. No removal work, no referral fees, one named consultant.", a)

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
<div id="book" class="duty"><h3>Prefer to book a call?</h3><p>Pick a free 30-minute slot and we'll call you.</p><div class="btn-row"><a class="btn" href="contact.html#book" data-book>{ICON["cal"]}Book a call</a></div></div>
<p class="area">Serving {REGIONS}.</p></div>
<form class="form panel" data-form data-name="contact">
<input type="hidden" name="_subject" value="Website enquiry">
<div class="row2"><label class="field">Your name<input name="name" required autocomplete="name"></label><label class="field">Company<input name="company" autocomplete="organization"></label></div>
<div class="row2"><label class="field">Email<input name="email" type="email" required autocomplete="email" autocapitalize="none" spellcheck="false"></label><label class="field">Phone<input name="phone" type="tel" inputmode="tel" autocomplete="tel"></label></div>
<label class="field">What do you need?<select name="need">
<option>A designated substance survey or report for a project</option><option>Updating the asbestos record for my building</option>
<option>A building program for one or more buildings</option><option>A suite check before a rental unit is renovated</option>
<option>The Cleared-to-Start Pass for my contracting business</option><option>Abatement specification, oversight or Type 3 clearance</option><option>Workplace exposure monitoring (not available yet: notify me at launch)</option><option>Something else</option></select></label>
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
<p class="small">Last updated {LASTMOD_TOKEN}.</p>
</div></div></section>"""
page("privacy.html", "Privacy notice | Noah Crowley Consulting", "How Noah Crowley Consulting collects, uses and protects the information you send through this website.", pv)

# ---------------------------------------------------------------- 404
nf = """<section class="hero"><div class="wrap"><div class="prose"><h1>That page isn't here</h1>
<p class="lede">The link may be old or mistyped. Start from one of these instead.</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="index.html">Go to the home page</a></div></div></div></section>"""
page("404.html", "Page not found | Noah Crowley Consulting", "This page doesn't exist.", nf)

# ---------------------------------------------------------------- sitemap, robots
urls = "".join(f"<url><loc>{SITE['domain']}/{'' if p == 'index.html' else p}</loc><lastmod>{LASTMOD[p]['date']}</lastmod></url>" for p in PAGES if p != "404.html" and p not in HIDDEN)
json.dump({p: LASTMOD[p] for p in sorted(PAGES)}, open(LASTMOD_FILE, "w"), indent=1)
open(os.path.join(ROOT, "sitemap.xml"), "w").write(f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{urls}</urlset>')
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nSitemap: {SITE['domain']}/sitemap.xml\n")
LLMS = f"""# {SITE['online']}

> {SITE['legal']} is an independent asbestos and designated substances consultancy based in {SITE['city']}, Ontario, serving {REGIONS}. It surveys buildings, keeps O. Reg. 278/05 asbestos records, writes abatement specifications, oversees abatement, tests the air and does Type 3 clearance. It never removes asbestos and takes no referral fees.

- Clients: commercial and institutional building owners, landlords and condos, general and restoration contractors.
- Reports cover all 11 Ontario designated substances and are priced as a report fee plus samples taken. Prices are CAD before HST.
- Lab results take [[labDays]] business days from the lab's receipt. Rush analysis is not offered.
- Contact: {SITE['phone']}, {SITE['email']}, {SITE['domain']}/contact.html

## Reports (starting prices)
""" + "".join(f"- {n}: from {money(p)}. {w_}. {t}.\n" for n, p, w_, g, t in REPORTS) + """
## Programs (monthly, per building)
""" + "".join(f"- {v['program']}, {v['name']}: from {money(v['price'])} a month. {v['fits']}.\n" for v in TIERS.values()) + f"""
## Key pages
- [Reports and prices]({SITE['domain']}/services.html)
- [Building programs]({SITE['domain']}/building-owners.html)
- [Cleared-to-Start Pass for contractors]({SITE['domain']}/contractors.html)
- [Obligation Check: which duties apply to you]({SITE['domain']}/obligation-check.html)
- [How we work]({SITE['domain']}/about.html)
""" + "".join(f"- [Asbestos testing in {t}]({SITE['domain']}/{h})\n" for h, t in CITIES) + "".join(f"- [{t}]({SITE['domain']}/{h})\n" for h, t, _ in GUIDES)
open(os.path.join(ROOT, "llms.txt"), "w").write(fill(LLMS))
open(os.path.join(ROOT, "CNAME"), "w").write(SITE["domain"].replace("https://", "") + "\n")
open(os.path.join(ROOT, ".nojekyll"), "w").write("")
# ---------------------------------------------------------------- price guards (tools/prices.py): stop on any problem
problems = lint_sources(["tools/build.py", "assets/site.js", "assets/ncc-rules.js"]) + check_output(PAGES + ["llms.txt"])
if problems:
    print("PRICE CHECK FAILED: the site was built but must not be published.\n  " + "\n  ".join(problems))
    sys.exit(1)
print(len(PAGES), "pages built;", P["stamp"]["pb"], "from tools/prices.json (Guide rev", str(P["stamp"]["guideRev"]) + "); price guards passed")
