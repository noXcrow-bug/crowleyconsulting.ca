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

# ---------------------------------------------------------------- products (from tools/prices.json)
# The website quotes the Guide's public prices only (products 1-5, 7, 8 and the add-ons). Product 6 and the Guide's
# "pricing assumptions" are never published (PB-2026.11g, decision 59).
PRICE_BOOK = P["stamp"]["pb"]
F = NUM["from"]
# (name, from price, when you need it, what you get, turnaround, page)
PRODUCTS = [
 ("Renovation-scope DSS", F["reno"], "Renovation, repair or a tender for one work area", "All 11 designated substances in the work area, ready to attach to the tender", "[[ta.reno]] business days", "designated-substance-survey.html"),
 ("Full-building DSS", F["full"], "Acquisition, capital planning, several projects in one building, or no survey on file", "All 11 designated substances across the whole building: the master reference for later projects", "[[ta.full]] business days", "designated-substance-survey.html"),
 ("Pre-demolition DSS", F["predemo"], "A vacant building coming down, or a demolition permit", "A destructive survey of every space so materials can come out before demolition", "[[ta.predemo]] business days", "designated-substance-survey.html"),
 ("Bulk Material Sampling", F["bulk"], "A few specific materials before drilling or cutting, or a find mid-job", "Sampling, lab analysis and a short letter: the result per material, photos, and the work classification if positive", "[[labDays]] business days; [[rushDays]] on a call-out", "contractors.html"),
 ("Annual Asbestos Reassessment Program", F["reassess"], "Keeping the O. Reg. 278/05 asbestos record current every year", "Year 1 builds the record; every year a walk-through, condition ratings, an updated record and notices", "Yearly", "building-owners.html"),
 ("Abatement Design & Oversight", F["abatement"], "Asbestos removal that needs a tender and someone on the owner's side", "Specification and tender package, site inspections, clearance and close-out", "Specification in [[abate.specDays]] business days", "services.html"),
 ("Clearance Air Testing", F["clearance"], "A Type 3 enclosure ready to come down", "Final visual inspection, air samples at the Table 3 count, rush lab analysis and a pass/fail certificate", "[[clr.days]] business days", "contractors.html"),
 ("Asbestos Instruction & Training", F["training"], "Workers in Type 1 and Type 2 operations, or building staff who need awareness training", "On-site training with attendance records and certificates", "Half day or full day", "services.html"),
 ("Peer Review", F["peer"], "A second opinion on another firm's survey or abatement specification", "A written memo listing each gap, its risk and the fix, plus a follow-up call", "[[peer.daysAB]] or [[peer.daysCD]] business days", "services.html"),
]
PKEY = ["reno", "full", "predemo", "bulk", "reassess", "abatement", "clearance", "training", "peer"]

def money(n): return "${:,.0f}".format(n)

# ---------------------------------------------------------------- page chrome
NAV = [("building-owners.html", "Building owners"), ("landlords.html", "Landlords"), ("contractors.html", "Contractors"),
       ("services.html", "Reports & prices"), ("contact.html", "Contact")]
CITIES = [("asbestos-testing-windsor.html", "Windsor"), ("asbestos-testing-leamington.html", "Leamington"), ("asbestos-testing-chatham.html", "Chatham"),
          ("asbestos-testing-sarnia.html", "Sarnia"), ("asbestos-testing-london.html", "London")]
TRIGGERS = [("designated-substance-survey.html", "Designated substance surveys"),
            ("commercial-asbestos-survey.html", "Commercial and industrial asbestos surveys"),
            ("designated-substance-list-tender.html", "The designated substance list for a tender"),
            ("asbestos-testing-before-renovation.html", "Asbestos testing before renovation"),
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
<link rel="icon" href="favicon-16.png" sizes="16x16" type="image/png">
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
<a class="brand" href="index.html" aria-label="{e(SITE['online'])}, home"><img src="assets/ncc-lockup.svg" alt="{e(SITE['online'])}" width="655" height="184"></a>
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
<div class="foot-brand"><img src="assets/ncc-lockup-dark.svg" alt="{e(SITE['online'])}" width="655" height="184">
<p>Independent asbestos and designated substances consulting for {REGIONS}. We never remove or abate anything and take no referral fees.</p></div>
<div><h4>Services</h4><ul>
<li><a href="building-owners.html">Annual Asbestos Reassessment</a></li><li><a href="landlords.html">Landlords and condos</a></li>
<li><a href="contractors.html">Testing and clearance for contractors</a></li><li><a href="designated-substance-survey.html">Designated substance surveys</a></li>
<li><a href="commercial-asbestos-survey.html">Commercial buildings</a></li><li><a href="services.html">Reports and prices</a></li>
<li><a href="obligation-check.html">Obligation Check</a></li></ul></div>
<div><h4>Where we work</h4><ul>{"".join(f'<li><a href="{h}">Asbestos testing in {t}</a></li>' for h, t in CITIES)}</ul></div>
<div><h4>Guides and contact</h4><ul>{"".join(f'<li><a href="{h}">{t}</a></li>' for h, t, _ in GUIDES)}<li><a href="asbestos-in-commercial-buildings.html">Where asbestos hides</a></li><li><a href="designated-substances-ontario.html">The 11 designated substances</a></li>{contact}<li><a href="about.html">How we work</a></li></ul></div>
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

def cta(title="Find out what applies to you in two minutes.", text="Answer a few questions and the Obligation Check tells you which duties you carry, what fits and what the first step costs.", href="obligation-check.html"):
    return f"""<section class="cta-band"><div class="wrap"><div><h2>{title}</h2><p>{text}</p></div>
<div class="btn-row"><a class="btn" href="{href}">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></section>"""

def crumbs(*items):
    parts = ['<a href="index.html">Home</a>'] + [f'<a href="{h}">{t}</a>' if h else e(t) for h, t in items]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"

def byline():
    """Who wrote the page and when it last changed (the page's own sitemap date). Search engines and commercial buyers
    both look for a named, accountable author; the date moves only when the page's content changes."""
    return f'<p class="byline">Written by {e(SITE["founder"])}, asbestos and designated substances consultant. Last updated {LASTMOD_TOKEN}.</p>'

def faq(items):
    html = '<section class="section white"><div class="wrap"><div class="section-head"><h2>Questions people ask</h2></div><div class="faq">' + "".join(
        f'<details><summary><h3>{q}</h3></summary><div class="faq-a"><p>{a}</p></div></details>' for q, a in items) + "</div></div></section>"
    import re
    sch = {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", a)}} for q, a in items]}
    return html, sch

def service_schema(name, desc, low):
    return {"@context": "https://schema.org", "@type": "Service", "name": name, "description": desc, "provider": {"@id": BIZ_ID},
        "areaServed": ["Windsor, ON", "Essex County, ON", "Chatham-Kent, ON", "Sarnia-Lambton, ON", "London, ON"],
        "offers": {"@type": "Offer", "priceCurrency": "CAD", "price": str(low), "description": f"From ${low:,} before HST"}}

def ul(items): return "<ul>" + "".join(f"<li>{x}</li>" for x in items) + "</ul>"

def reassess_table():
    rows = "".join(f'<tr><th scope="row">Class {c}</th><td data-label="Floor area">{a}</td><td class="num" data-label="Year 1 setup">{"From " if c == "D" else ""}[[ra.setup.{c}]]</td><td class="num" data-label="Each year after">{"From " if c == "D" else ""}[[ra.annual.{c}]]</td></tr>'
        for c, a in (("A", "Under [[classA.m2]] m² [[[classA.ft2]] sq ft]"), ("B", "[[classA.m2]]–[[classB.m2]] m² [[[classA.ft2]]–[[classB.ft2]] sq ft]"), ("C", "[[classB.m2]]–[[classC.m2]] m² [[[classB.ft2]]–[[classC.ft2]] sq ft]"), ("D", "Over [[classC.m2]] m² [[[classC.ft2]] sq ft]")))
    return f"""<div class="table-wrap stack"><table class="data"><thead><tr><th scope="col">Building</th><th scope="col">Floor area</th><th scope="col" class="num">Year 1 setup</th><th scope="col" class="num">Each year after</th></tr></thead><tbody>{rows}</tbody></table></div>
<p class="small" style="margin-top:12px">CAD before HST, per building. The Year 1 setup covers the whole first year, with no other fee that year. From the second year, the annual fee is billed once a year in advance.</p>"""

REASSESS_INC = ["Year 1: we build your asbestos record from your existing survey", "Every year: a walk-through of every recorded material, a condition rating and an updated record", "Written notices to occupants and to contractors working in the building", "Your register snapshot, refreshed after each change, with a PDF for the on-site binder"]
def reassess_terms():
    return ul(["The Year 1 setup covers the whole first year. From the second year the fee is paid a full year in advance.",
     "It renews each year unless you cancel at least [[cancelDays]] days before the renewal date. There's no refund for part of a year, and it ends when the building is fully abated.",
     "The setup builds the record from an existing survey. If there isn't a usable one, a full-building designated substance survey comes first, from [[from.full]] plus samples.",
     "Designated substance surveys for projects are never included: a project triggers them, not the calendar. They're quoted when you need one.",
     "We never remove or abate anything and take no referral fees, so no result is shaped by someone with a stake in the job."])
def start_steps():
    return """<div class="steps">
<div class="step"><h3>Year 1 setup</h3><p>We turn your existing survey into your on-site asbestos record and register. The setup fee covers the whole first year.</p></div>
<div class="step"><h3>Record and register</h3><p>Your record becomes a register snapshot, refreshed after each change, that you can show an inspector or a contractor on a phone. <a href="register-example.html">See an example</a></p></div>
<div class="step"><h3>Every year after</h3><p>A walk-through of every recorded material, condition ratings, an updated record and the notices, billed once a year in advance.</p></div></div>"""

def segment_hero(crumb, h1, lede, seg):
    return f"""<section class="hero"><div class="wrap">{crumbs((None, crumb))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html#{seg}">Check what applies to you</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>"""

# ---------------------------------------------------------------- home
# ---------------------------------------------------------------- the register (homepage card and the example page)
# Example data only: invented buildings, shown to explain what a program client sees. Dates are ISO; quantities metric with imperial in brackets.
ST_LABEL = {"act": "Act now", "monitor": "Monitor", "good": "Good"}
MARK = '<img class="reg-mark" src="assets/ncc-logo-dark.svg" alt="" width="30" height="30">'
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
REG_MEANS = {"act": "Repair, remove or isolate before the area is used or disturbed.", "monitor": "Leave in place; check its condition at every visit.", "good": "Leave in place; manage under the asbestos management program.", "lead": "Leave in place; no sanding, grinding, torch cutting or heat gun without lead precautions."}
def _ex_row(x):
    smp = x.get("samples") or []
    rid = smp[0] if smp else ("Visual ID" if x.get("basis") == "visual-acm" else "Not sampled")
    typ = x.get("friable") or ("Paint" if "lead" in (x.get("result") or "").lower() else "")
    note = (x.get("reason") or "").strip() or (REG_MEANS["lead"] if x.get("sub") == "Lead (paint)" and x["status"] == "good" else "")
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
<div class="reg-meta"><span><strong>Last reassessed</strong> <span class="mono">{fdate(b["last"])}</span></span><span><strong>Next due</strong> <span class="mono">{fdate(b["next"])}</span></span></div>
<table class="reg-table"><thead><tr><th>Location</th><th>Material</th><th>Status</th></tr></thead><tbody>{reg_rows(b["rows"], pre)}</tbody></table>
{f'<figcaption class="reg-foot">{foot}</figcaption>' if foot else ""}</figure>"""
REGISTER = register(EX_BUILDINGS[0], "hr", foot='Tap a row to see the result and its history. <a href="register-example.html">See a full example register</a>')

home_schema = {"@context": "https://schema.org", "@type": "ProfessionalService", "@id": BIZ_ID, "name": SITE["legal"], "alternateName": SITE["online"], "legalName": SITE["legal"],
    "knowsAbout": ["Asbestos testing", "Designated substance survey", "O. Reg. 278/05 asbestos management", "Type 3 asbestos clearance", "Lead paint testing"],
    "url": SITE["domain"] + "/", "logo": SITE["domain"] + "/assets/ncc-lockup.svg", "image": SITE["domain"] + "/assets/og-image.png",
    "description": "Independent designated substance surveys, asbestos testing, annual asbestos reassessments, abatement design and oversight, and Type 3 clearance air testing in southwestern Ontario.",
    "areaServed": [{"@type": "AdministrativeArea", "name": n} for n in ["Windsor-Essex", "Chatham-Kent", "Sarnia-Lambton", "London, Ontario"]],
    "address": {"@type": "PostalAddress", "addressLocality": SITE["city"], "addressRegion": "ON", "addressCountry": "CA"},
    "priceRange": "$$"}
home_schema["founder"] = {"@type": "Person", "@id": SITE["domain"] + "/#founder", "name": SITE["founder"], "jobTitle": "Asbestos and designated substances consultant", "worksFor": {"@id": BIZ_ID}}
if SITE["sameAs"]: home_schema["sameAs"] = SITE["sameAs"]
site_schema = {"@context": "https://schema.org", "@type": "WebSite", "@id": SITE["domain"] + "/#website", "url": SITE["domain"] + "/",
    "name": SITE["legal"], "alternateName": [SITE["online"], "NCC"], "publisher": {"@id": BIZ_ID}, "inLanguage": "en-CA"}
if SITE["phone"]: home_schema["telephone"] = SITE["phone"]
if SITE["email"]: home_schema["email"] = SITE["email"]

home = f"""
<section class="hero"><div class="wrap hero-grid">
<div class="hero-copy">
<h1>Asbestos and designated substance compliance, kept current all year.</h1>
<p class="lede">Independent designated substance surveys when a project needs one, testing when a job turns something up, and a yearly reassessment that keeps your asbestos record current. For owners and facility managers of commercial, industrial and institutional buildings, landlords and contractors.</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="#doors">Find what fits</a></div>
{DSS_CHECK}
<p class="area">Serving {REGIONS}.</p>
</div>
{REGISTER}
</div></section>

<section class="section tight" id="doors"><div class="wrap">
<div class="section-head"><h2>Start with what you're responsible for</h2></div>
<div class="doors">
<a class="door" href="building-owners.html"><h3>I own or manage a building</h3><p>Keep your asbestos record current every year, with notices sent and a register you can show an inspector.</p><span class="go">Annual Asbestos Reassessment{ICON["chev"]}</span></a>
<a class="door" href="landlords.html"><h3>I rent out units or run a condo</h3><p>The same yearly record and notices for rental and condo buildings, plus a quick test before a suite is renovated.</p><span class="go">Records and suite testing{ICON["chev"]}</span></a>
<a class="door" href="contractors.html"><h3>I'm about to open walls or floors</h3><p>Test the materials before you cut, a call-out when work uncovers something, and clearance air testing.</p><span class="go">Bulk Material Sampling, from [[bulk.visit]]{ICON["chev"]}</span></a>
<a class="door" href="designated-substance-survey.html"><h3>I need a report for a project</h3><p>Designated substance surveys for renovation, tenders, purchases and demolition permits.</p><span class="go">Designated substance surveys{ICON["chev"]}</span></a>
</div></div></section>

<section class="section white"><div class="wrap">
<div class="section-head"><h2>How it works</h2><p class="lede">The first step is free and takes two minutes.</p></div>
<div class="steps">
<div class="step"><h3>Take the Obligation Check</h3><p>A two-minute quiz that tells you which legal duties apply to your building or job, and what to do first.</p></div>
<div class="step"><h3>Get the right report</h3><p>A designated substance survey for the project, or a full-building survey if there isn't one on file. Priced by building size, plus the samples taken.</p></div>
<div class="step"><h3>Stay current</h3><p>The Annual Asbestos Reassessment updates your record every year, sends the notices and keeps your register current.</p></div>
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
<div class="section-head"><h2>A report when a project needs one. A yearly reassessment in between.</h2><p class="lede">A designated substance survey is tied to a project, not the calendar, so the Annual Reassessment never includes one. It keeps your record current between projects.</p></div>
<div class="programs">
<a class="program" href="designated-substance-survey.html"><h3>Designated substance surveys</h3><p>Renovation-scope, full-building and pre-demolition surveys, priced by building size, plus samples as needed.</p></a>
<a class="program" href="building-owners.html"><h3>Annual Asbestos Reassessment</h3><p>Your O. Reg. 278/05 record built in year one, then re-inspected and updated every year, with notices and a register.</p></a>
<a class="program" href="contractors.html"><h3>Testing and clearance</h3><p>Bulk Material Sampling before you cut, same- or next-day call-outs when work uncovers something, and Type 3 clearance air testing.</p></a>
</div>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>Independent, on purpose</h2>
<p>We never remove or abate anything and take no referral fees. When we tell you a material is fine to leave in place, nobody on our side gains from the opposite answer. When we test the air for an abatement contractor, our fee doesn't depend on the result.</p>
<p>You deal with one named consultant who knows your buildings.</p>
<p><a href="about.html">How we work</a></p></div>
<div class="prose"><h2>All 11 designated substances</h2>
<p>Asbestos, lead, mercury and silica turn up in buildings. Isocyanates, benzene, vinyl chloride, acrylonitrile, arsenic, ethylene oxide and coke oven emissions are mostly found in industrial processes. A pre-project list has to consider all of them, so every survey we write does.</p>
<p><a href="designated-substances-ontario.html">Where each one turns up</a> · <a href="services.html">See reports and prices</a></p></div>
</div></section>
""" + cta()
HOME_FAQ, HOME_FAQ_SCHEMA = faq([
 ("What are Ontario's designated substances?", "There are 11: acrylonitrile, arsenic, asbestos, benzene, coke oven emissions, ethylene oxide, isocyanates, lead, mercury, silica and vinyl chloride. Asbestos, lead, mercury and silica are the ones usually found in buildings."),
 ("How often does a building owner have to update the asbestos record?", "At least once every 12 months, and whenever new information comes to light, under O. Reg. 278/05. The record has to be kept on the premises."),
 ("Who is responsible for the designated substance list before a renovation?", "The project owner. Under section 30 of the Occupational Health and Safety Act, the owner lists every designated substance in the work area before the project begins and includes the list in the tender."),
 ("How much does it cost?", "Designated substance surveys start at [[from.reno]] for one work area and [[from.full]] for a whole building, plus samples at [[sample]] each. Testing a few materials starts at [[bulk.visit]] for the visit, plus samples. The Annual Asbestos Reassessment starts at [[from.reassess]] for the first year. All prices are CAD before HST."),
 ("Does the Annual Reassessment include my designated substance survey?", "No, on purpose. A survey is triggered by a project, not the calendar, so you'd be paying for it in years you don't need it. The reassessment keeps your record current; if you don't have a usable survey yet, a full-building survey comes first."),
 ("How long do lab results take?", "[[labDays]] business days from when the lab receives the samples. Rush analysis takes [[rushDays]] business days, at double the sample price. If work can't wait, we leave written interim instructions on site."),
 ("Do you remove asbestos?", "No. We are independent consultants: we survey, test, write specifications, oversee abatement and test the air, but we never remove or abate anything and take no referral fees.")])
home = home.replace('<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', HOME_FAQ.replace('class="section white"', 'class="section"') + '<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', 1)
page("index.html", "Asbestos & Designated Substance Consulting, Windsor ON", "Independent designated substance surveys, asbestos testing and annual asbestos reassessments in Windsor and southwestern Ontario. Surveys from [[from.reno]].", home, schema=[home_schema, site_schema, HOME_FAQ_SCHEMA])

# ---------------------------------------------------------------- building owners
b = segment_hero("Building owners", "Annual Asbestos Reassessment",
    "For owners and facility managers of commercial, institutional and multi-unit residential buildings: offices, plazas, schools, churches, clinics and small municipalities. Your 12-month asbestos update, your notices and your register, for one yearly fee per building.", "building") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What the law asks of building owners</h3>{ul([
 "Keep an asbestos record on the premises: where each material is, its condition, and whether it is friable (O. Reg. 278/05).",
 "Re-inspect listed materials and update the record at least once every 12 months, and whenever you learn something new.",
 "Give occupiers written notice of asbestos in the areas they occupy, and tell contractors before work that may disturb it.",
 "Train maintenance workers who work on or near listed materials.",
 "Before any renovation, repair or demolition, list every designated substance in the work area and include it in the tender (OHSA s.30)."])}<p class="small"><a href="asbestos-management-program.html">More on asbestos management programs</a> · <a href="designated-substance-list-tender.html">The list for a tender</a></p></div>
<div class="prose"><h2>What's at stake</h2>
<p>An owner who leaves a substance off the project list is liable to the constructor and every contractor for their losses when it turns up mid-job. The maximum OHSA fine is $2 million for a corporation and $1.5 million for a director or officer.</p>
<p>In Ontario's 2023–24 inspection campaign, the most common orders were for not following the asbestos management program and not keeping the record on site. Most of the workplaces visited had fewer than 50 workers.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Prices by building size</h2></div>
{reassess_table()}
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>What's included</h2>{ul(REASSESS_INC)}
<h3>What it isn't</h3>
<p>A designated substance survey is triggered by a project: a renovation, a tender, a sale, a demolition. It isn't something you need every year, so it isn't in the yearly fee. When a project comes, we quote the survey for it. Staff awareness training is also booked separately, from [[train.aware]] a session.</p>
<p><a href="services.html">See the report menu</a></p></div>
<div class="prose"><h2>How it works</h2>{start_steps()}
<h3>Terms</h3>{reassess_terms()}</div>
</div></section>
""" + cta("Is your asbestos record within 12 months?", "The Obligation Check takes two minutes and tells you what your buildings need first.", "obligation-check.html#building")
page("building-owners.html", "Annual Asbestos Reassessment | Ontario Asbestos Records", "Yearly asbestos record updates, notices and a register for building owners in southwestern Ontario. From [[from.reassess]] per building for the first year.", b, "building-owners.html", schema=service_schema("Annual Asbestos Reassessment Program", "Yearly O. Reg. 278/05 asbestos record reassessment in southwestern Ontario", F["reassess"]))

# ---------------------------------------------------------------- landlords
r = segment_hero("Landlords", "Asbestos records and suite testing for landlords and condos",
    "For landlords with five or more units, property managers and condominium corporations. A suite turns over, the crew lifts 23 cm [9-inch] floor tile or sands a stippled ceiling, and you now have exposed workers, a contaminated unit and an unhappy tenant. Test first, and keep the record that tells you where to look.", "rental") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What the law asks of rental owners</h3>{ul([
 "Keep an asbestos record, update it at least every 12 months, and give tenants written notice of asbestos in the areas they occupy.",
 "Tell superintendents, maintenance staff and contractors what's there before work that may disturb it.",
 "List every designated substance in the work area before a renovation or repair project begins.",
 "Older suites also hide lead paint and mercury thermostats; the same check picks them up."])}</div>
<div class="prose"><h2>Before a suite is renovated</h2>
<p>Bulk Material Sampling tests the few materials your crew will disturb: a [[bulk.visit]] visit plus [[sample]] a sample, with the lab's analysis of the first layer included. Results take [[labDays]] business days, so book it before the tenant leaves.</p>
<p>Already uncovered something? An unexpected-find call-out comes the same or next business day, with rush lab results in [[rushDays]] business days.</p>
<p><a href="guide-suite-turnover-checklist.html">Get the suite turnover checklist</a></p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>The Annual Asbestos Reassessment</h2><p class="lede">The same yearly record, notices and register as every building, priced by the building's size.</p></div>
{reassess_table()}
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>How it works</h2>{start_steps()}</div>
<div class="prose"><h3>What's included</h3>{ul(REASSESS_INC)}<h3>Terms</h3>{reassess_terms()}</div>
</div></section>
""" + cta("Got a suite turning over soon?", "Book Bulk Material Sampling, or take the Obligation Check to see what your buildings need.", "obligation-check.html#rental")
page("landlords.html", "Asbestos Records & Suite Testing for Landlords and Condos", "Asbestos records, tenant notices and suite testing for landlords, property managers and condos in Windsor-Essex and SW Ontario. From [[bulk.visit]] plus samples.", r, "landlords.html", schema=service_schema("Annual Asbestos Reassessment for landlords", "Yearly asbestos record reassessment for rental and condo buildings in southwestern Ontario", F["reassess"]))

# ---------------------------------------------------------------- employers
w = f"""<section class="hero"><div class="wrap">{crumbs((None, "Employers"))}
<div class="hero-copy" style="max-width:860px"><h1>Designated substances at work</h1>
<p class="lede">For employers whose workers use, handle or store a designated substance under O. Reg. 490/09. Workplace exposure monitoring is not available yet. Call 519-890-9654 and tell us what you need, and we'll contact you when it launches.</p>
<div class="btn-row"><a class="btn amber" href="contact.html">Leave your details</a><a class="btn ghost" href="guide-designated-substance-self-check.html">Take the self-check</a></div></div></div></section>
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What O. Reg. 490/09 asks of employers</h3>{ul([
 "A written exposure assessment, made with your joint health and safety committee. Redo it after any change that could significantly affect exposure.",
 "Where workers' health may be affected, a written control program: engineering controls, work and hygiene practices, monitoring, records and training.",
 "Keep exposure under the occupational exposure limit, with air monitoring results posted, shared with the JHSC and kept for 5 years.",
 "Medical surveillance for asbestos, benzene, coke oven emissions, isocyanates, lead, mercury and silica."])}<p class="small">The regulation doesn't apply on construction projects, where Regulation 833 and the building duties govern.</p></div>
<div class="prose"><h2>What we can do</h2>
<p>Workplace exposure monitoring is not available yet. Call 519-890-9654 and tell us what you need, and we'll contact you when it launches.</p>
<p>If your building is older than 1990, it also carries the asbestos duties every owner has. See the <a href="building-owners.html">Annual Asbestos Reassessment</a>.</p></div>
</div></section>""" + cta("Not sure which duties apply?", "The one-page self-check tells you whether O. Reg. 490/09 applies, or leave your details and we'll contact you when exposure monitoring launches.", "guide-designated-substance-self-check.html")
page("employers.html", "Designated Substances at Work | O. Reg. 490/09", "What O. Reg. 490/09 asks of Ontario employers in southwestern Ontario. Workplace exposure monitoring is not available yet.", w, "employers.html")

# ---------------------------------------------------------------- contractors
def price_rows(rows):
    return "".join(f'<tr><th scope="row">{a}</th><td class="num" data-label="Price">{b}</td><td data-label="Results">{c}</td></tr>' for a, b, c in rows)
c = segment_hero("Contractors", "Testing and clearance for contractors",
    "Test the materials before your crew cuts, get someone on site the same or next business day when work uncovers something, and book clearance air testing when a Type 3 enclosure is ready to come down.", "contractor") + f"""
<section class="section white"><div class="wrap split">
<div class="prose"><h2>The problem it solves</h2>
<p>On small jobs the owner rarely has a current list. The law puts that duty on the owner, but you're the one standing in the room when a suspect material turns up.</p>
<p>When unlisted material is found, work has to stop except to identify it, and the Ministry, the owner, the contractor and the JHSC must be notified right away. Standard lab results take [[labDays]] business days, so a find on day one idles your crew or pushes the job into asbestos procedures by presumption.</p>
<p>Testing before you price the job moves that find to the quote, where the owner pays for it.</p></div>
<div class="duty"><h3>What we do for contractors</h3>{ul([
 "Bulk Material Sampling: we test the few materials your work will disturb, with chain of custody and accredited lab analysis.",
 "A short letter report for each job: the result per material, photos, and the work classification if a result is positive.",
 "An unexpected-find call-out the same or next business day when work uncovers suspect material, with rush lab results in [[rushDays]] business days.",
 "Written interim instructions on site if the job can't wait for results: leave the suspect materials alone, or proceed treating them as asbestos.",
 "Clearance air testing for Type 3 enclosures, sold directly to abatement contractors.",
 "Type 1 and Type 2 instruction and training for your crew, at your site."])}
<p class="small">Each report is addressed to the building owner, because it's the owner's list. You're named as requester and get a copy.</p>
<p class="small">Know what to look for: <a href="asbestos-in-commercial-buildings.html">where asbestos hides in commercial buildings</a> · <a href="lead-paint-survey.html">lead paint</a></p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Prices</h2></div>
<div class="table-wrap stack"><table class="data"><thead><tr><th scope="col">Bulk Material Sampling</th><th scope="col" class="num">Price</th><th scope="col">Results</th></tr></thead><tbody>
{price_rows([("Scheduled visit", "[[bulk.visit]]", "[[labDays]] business days"), ("Each sample, first layer included", "[[sample]]", ""), ("Each extra layer in a sample", "[[layer]]", ""),
  ("Unexpected-find call-out, same or next business day", "[[bulk.callout]]", "[[rushDays]] business days"), ("Each call-out sample, rush lab, first layer included", "[[rush.sample]]", ""), ("Each extra layer on a call-out sample", "[[rush.layer]]", "")])}
</tbody></table></div>
<div class="table-wrap stack" style="margin-top:18px"><table class="data"><thead><tr><th scope="col">Clearance Air Testing</th><th scope="col" class="num">Price</th><th scope="col">Results</th></tr></thead><tbody>
{price_rows([("Enclosure 10 m² [108 sq ft] or less, 2 air samples", "[[clr.small]]", "[[clr.days]] business days"), ("Enclosure over 10 m² and under 500 m² [5,382 sq ft], 3 air samples", "[[clr.mid]]", "[[clr.days]] business days"),
  ("Enclosure 500 m² [5,382 sq ft] or more, 5 air samples", "[[clr.large]]", "[[clr.days]] business days"), ("Re-test after a failed clearance", "Same price", "[[clr.days]] business days")])}
</tbody></table></div>
<p class="small" style="margin-top:12px">CAD before HST. Samples are billed on top of the visit fee. Rush sample prices are double the standard sample price. Minimum charge for any site visit: [[minVisit]].</p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>The business case</h2>
<div class="table-wrap stack"><table class="data"><thead><tr><th scope="col">A job in an older building</th><th scope="col">Without testing first</th><th scope="col">With testing first</th></tr></thead><tbody>
<tr><th scope="row">Before you bid</th><td data-label="Without testing first">Guess, or price around it</td><td data-label="With testing first">The materials you'll disturb are tested</td></tr>
<tr><th scope="row">How it's paid</th><td data-label="Without testing first">Rarely quoted, so absorbed or skipped</td><td data-label="With testing first">A line on your quote, paid by the owner</td></tr>
<tr><th scope="row">Suspect material</th><td data-label="Without testing first">Found mid-job: stop work, notify, wait</td><td data-label="With testing first">Found before mobilizing and priced into the quote</td></tr>
</tbody></table></div>
<p class="small">Prefer not to bill the line? Absorb it and market “tested before we cut” to clients and insurers instead.</p></div>
<div class="prose"><h2>Clearance for abatement contractors</h2>
<p>Type 3 work needs a clearance air test before the enclosure comes down: a final visual inspection, then air samples at the Table 3 count for the enclosure size, analysed on rush. We sell it directly to abatement contractors.</p>
<p>Our fee doesn't depend on the result, and the result is reported as found. We never remove or abate anything and take no referral fees.</p>
<p><a href="guide-demolition-renovation-dss.html">Read the demolition and renovation DSS guide</a></p></div>
</div></section>
""" + cta("Know what's in the walls before your crew arrives.", "Book Bulk Material Sampling for your next job, or take the Obligation Check to see what fits.", "obligation-check.html#contractor")
page("contractors.html", "Asbestos Testing & Clearance for Contractors | Windsor, ON", "Bulk Material Sampling before you cut, same- or next-day call-outs and Type 3 clearance air testing for contractors in southwestern Ontario. From [[bulk.visit]].", c, "contractors.html", schema=service_schema("Bulk Material Sampling", "Asbestos testing of specific materials for contractors in southwestern Ontario", F["bulk"]))

# ---------------------------------------------------------------- services
SVC_FAQ_HTML, SVC_FAQ_SCHEMA = faq([
 ("How much does a designated substance survey cost?", "Surveys start at [[from.reno]] for one work area, [[from.full]] for a whole building and [[from.predemo]] for a pre-demolition survey, by building size. Samples are added on top: [[sample]] each ([[sample.demo]] on a demolition survey), including lab analysis of the first layer, and [[layer]] for each extra layer. All prices are CAD before HST."),
 ("Why is it priced per sample?", "The lab analyzes every layer in a sample, and buildings differ: a floor tile and its glue are two layers, a plastered wall can be three. Pricing per sample means you pay for what your building actually needs, and we ask before going over the top of the estimate on your quote."),
 ("How long does a survey take?", "A renovation-scope survey takes [[ta.reno]] business days, a full-building survey [[ta.full]] and a pre-demolition survey [[ta.predemo]], from the end of fieldwork. Lab results take [[labDays]] business days from when the lab receives the samples; rush takes [[rushDays]] business days at double the sample price."),
 ("Is there a minimum charge or travel fee?", "The minimum charge for a site visit is [[minVisit]] before HST. Travel is free within [[freeKm]] km [[[freeMi]] mi] of Riverside Dr. and Ouellette Ave. (downtown Windsor); beyond that it's [[perKm]] a km for each km past [[freeKm]], counted both ways, by road."),
 ("Do you do the asbestos removal?", "No. We write the abatement specification, review bids, inspect the work and test the air, including Type 3 clearance, but we never remove anything and take no referral fees."),
])
SVC_SCHEMA = {"@context": "https://schema.org", "@type": "Service", "name": "Asbestos and designated substance services", "serviceType": "Designated substance survey",
  "provider": {"@id": BIZ_ID}, "areaServed": ["Windsor, ON", "Essex County, ON", "Chatham-Kent, ON", "Sarnia-Lambton, ON", "London, ON"],
  "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Service menu", "itemListElement": [
    {"@type": "Offer", "itemOffered": {"@type": "Service", "name": n, "description": g},
     "priceSpecification": {"@type": "PriceSpecification", "minPrice": p, "priceCurrency": "CAD", "valueAddedTaxIncluded": False}} for n, p, w_, g, t, pg in PRODUCTS]}}
def cls_row(label, key):
    return f'<tr><th scope="row">{label}</th>' + "".join(f'<td class="num" data-label="Class {c}">{"From " if c == "D" else ""}[[{key}.{c}]]</td>' for c in "ABCD") + f'<td data-label="Turnaround">[[ta.{key}]] business days</td></tr>'
s = f"""<section class="hero"><div class="wrap">{crumbs((None, "Reports and prices"))}
<div class="hero-copy" style="max-width:860px"><h1>Reports and prices</h1>
<p class="lede">Every survey covers Ontario's 11 designated substances and is priced as a report fee by building size, plus the samples taken. Samples are [[sample]] each ([[sample.demo]] on a demolition survey), and extra layers are [[layer]] each. Rush sample prices are double the standard sample price. These are starting prices: larger or more complex jobs are quoted above them.</p>{DSS_CHECK}</div></div></section>
<section class="section white"><div class="wrap">
<div class="section-head"><h2>Service menu</h2></div>
<div class="table-wrap stack"><table class="data wide"><thead><tr><th scope="col">Service</th><th scope="col">When you need it</th><th scope="col">What you get</th><th scope="col">Turnaround</th><th scope="col" class="num">From</th></tr></thead><tbody>
{"".join(f'<tr><th scope="row"><a href="{pg}">{n}</a></th><td data-label="When you need it">{w_}</td><td data-label="What you get">{g}</td><td data-label="Turnaround">{t}</td><td class="num" data-label="From">{money(p)}</td></tr>' for n, p, w_, g, t, pg in PRODUCTS)}
</tbody></table></div>
<p class="small" style="margin-top:12px">CAD before HST ([[hst]]). Survey turnarounds are business days from the end of fieldwork and include the lab's [[labDays]] business days. We confirm the report fee and the estimated number of samples in writing before any work starts, and we ask before going over the top of that estimate.</p>
</div></section>
<section class="section"><div class="wrap">
<div class="section-head"><h2>Survey report fees by building size</h2><p class="lede">Class A is under [[classA.m2]] m² [[[classA.ft2]] sq ft], Class B up to [[classB.m2]] m² [[[classB.ft2]] sq ft], Class C up to [[classC.m2]] m² [[[classC.ft2]] sq ft], and Class D anything larger. Samples are extra.</p></div>
<div class="table-wrap stack"><table class="data wide"><thead><tr><th scope="col">Survey</th><th scope="col" class="num">Class A</th><th scope="col" class="num">Class B</th><th scope="col" class="num">Class C</th><th scope="col" class="num">Class D</th><th scope="col">Turnaround</th></tr></thead><tbody>
{cls_row("Renovation-scope DSS (one work area)", "reno")}{cls_row("Full-building DSS", "full")}{cls_row("Pre-demolition DSS (destructive, building vacant)", "predemo")}
</tbody></table></div>
</div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>Samples and layers</h2>
<p>A sample is what we take from a material. The lab analyzes every layer in it: a floor tile and its glue are two layers, a plaster wall with a skim coat can be three. Each sample is [[sample]] ([[sample.demo]] on a demolition survey) and includes lab analysis of its first layer. Extra layers are [[layer]] each, billed per layer analyzed. Vermiculite samples are [[sample.verm]] each.</p>
<p>Rush sample prices are double the standard sample price, extra layers included: a [[sample]] sample is [[rush.sample]] on rush, and a [[layer]] extra layer is [[rush.layer]]. Rush results take [[rushDays]] business days.</p>
<h2>Terms</h2>
{ul(["No deposit. For a survey or a sampling visit, the fee and samples are invoiced as soon as the samples are taken, so you can pay while the lab works; any extra layers the lab finds are invoiced once every result is in. The report is released once both are paid. Every invoice is due in [[paymentDays]] days. The Annual Reassessment is billed a year in advance.",
     "Minimum charge for any site visit: [[minVisit]] before HST.",
     "Travel is free within [[freeKm]] km [[[freeMi]] mi] of Riverside Dr. and Ouellette Ave. (downtown Windsor). Beyond that, [[perKm]] a km for each km past [[freeKm]], counted both ways, by road.",
     "After-hours or weekend fieldwork, only at your request: +[[afterHours]] on the fieldwork portion.",
     "A job that needs an overnight stay: [[overnight]] a night for hotel and meals.",
     "Quotes are valid for [[quoteValidDays]] days."])}</div>
<div class="prose"><h2>Add-ons</h2>
{ul(["Other hazardous building materials (PCBs, ozone-depleting substances, mould) added to a survey: [[hazAddon]], any samples at the sample prices above.",
     "Every report comes as a PDF, and each designated substance survey with one printed binder. A replacement binder is [[binder]]."])}
<h2>After the report</h2>
<p>If materials have to come out, Abatement Design & Oversight puts someone on your side: a specification and tender package from [[abate.spec]], site inspection visits at [[abate.visit]] each, or the full package with three site visits, clearance and a close-out report from [[abate.package]]. Clearance air testing starts at [[clr.small]]. We never do the removal ourselves.</p>
<h2>Training and second opinions</h2>
<p>On-site Type 1 and Type 2 instruction and training for up to [[train.t12max]] workers is [[train.t12]] a session; asbestos awareness for up to [[train.awaremax]] building staff is [[train.aware]]. A peer review of another firm's survey or specification starts at [[from.peer]].</p></div>
</div></section>
<section class="section white"><div class="wrap"><div class="section-head"><h2>Common jobs</h2></div>
<div class="link-list">{"".join(f'<a href="{h}"><strong>{t}</strong><span>What it involves, what it costs and how long it takes</span></a>' for h, t in TRIGGERS)}</div></div></section>""" + SVC_FAQ_HTML + cta("Not sure which report you need?", "The Obligation Check points you to the right one, or send us the job details and we'll quote it.")
page("services.html", "Designated Substance Survey & Asbestos Testing Prices | Ontario", "Designated substance surveys and asbestos testing in southwestern Ontario, priced by building size plus samples. Surveys from [[from.reno]], testing from [[bulk.visit]].", s, "services.html", schema=[SVC_SCHEMA, SVC_FAQ_SCHEMA])

# ---------------------------------------------------------------- example register (public demo of the client register snapshot)
write_example_register()
ex = f"""<section class="hero"><div class="wrap">{crumbs(("building-owners.html", "Annual Reassessment"), (None, "Example register"))}
<div class="hero-copy" style="max-width:62ch">
<h1>Your asbestos record, on any phone</h1>
<p class="lede">Every Annual Asbestos Reassessment client gets a register snapshot like this one. Show it to an inspector, send it to a contractor before they bid, and check a material before anyone drills. A fresh snapshot is shared after every reassessment, lab result or condition change. Below is the same register page a client receives, filled with an invented client's data.</p>
<p><a class="btn ghost" href="examples/register-brockmere.html" target="_blank" rel="noopener">Open it full screen</a></p></div>
</div></section>
<section class="section tight"><div class="wrap">
<div class="reg-frame"><iframe id="exReg" src="examples/register-brockmere.html" title="Example designated substance register (Brockmere Property Group, invented)" loading="lazy"></iframe></div>
</div></section>""" + cta("Want a register like this for your building?", "Take the Obligation Check to see what your building needs, or book a free 30-minute call.", "obligation-check.html")
page("register-example.html", "Example Asbestos Register | What Reassessment Clients See", "The designated substance register every Annual Asbestos Reassessment client gets: statuses, lab results, condition history and what to do, on any phone.", ex, "building-owners.html")

# ---------------------------------------------------------------- quiz
# What the Obligation Check (assets/site.js) shows: "from" prices, turnarounds and next-step wording, all from the price list.
QUIZ_PUBLIC = {
 "reports": {k: [n, p] for (n, p, *_), k in zip(PRODUCTS, PKEY)},
 "labDays": "[[labDays]]", "rushDays": "[[rushDays.to]]", "taRenoTo": "[[ta.reno.to]]",
 "offers": {
  "reassess": {"name": "Annual Asbestos Reassessment", "price": F["reassess"], "unit": "for the first year, per building, priced by size", "page": "building-owners.html",
     "inc": REASSESS_INC + ["From the second year, the annual fee is billed once a year in advance"]},
  "contractor": {"name": "Bulk Material Sampling", "price": F["bulk"], "unit": "for the visit, plus [[sample]] a sample", "page": "contractors.html",
     "inc": ["Testing of the materials your work will disturb, with chain of custody", "A short letter: the result per material, photos, and the work classification if positive", "Results in [[labDays]] business days", "Unexpected-find call-out the same or next business day: [[bulk.callout]] plus [[rush.sample]] a sample, results in [[rushDays]] business days"]},
  "restoration": {"name": "Unexpected-find call-out", "price": P["bulkSampling"]["callout"], "unit": "for the visit, plus [[rush.sample]] a sample at rush", "page": "contractors.html",
     "inc": ["Same or next business day", "Rush lab results in [[rushDays]] business days", "Air sampling after a disturbance from [[clr.disturb]]", "Clearance air testing from [[clr.small]] when a Type 3 enclosure comes down"]},
  "abatement": {"name": "Clearance Air Testing", "price": F["clearance"], "unit": "per event, by enclosure size", "page": "contractors.html",
     "inc": ["Final visual inspection", "Air samples at the Table 3 count for the enclosure size", "Rush lab analysis, results in [[clr.days]] business days", "Pass/fail certificate formatted for posting; our fee doesn't depend on the result"]},
  "homeowner": {"name": "Bulk Material Sampling", "price": F["bulk"], "unit": "for the visit, plus [[sample]] a sample", "page": "contractors.html",
     "inc": ["We test only the materials your renovation will disturb", "Results in [[labDays]] business days", "A short letter with the result per material"]}},
 "entry": {
  "Year 1 setup": "We build your asbestos record from your existing survey. The setup covers the whole first year, from [[from.reassess]] per building.",
  "Full-building DSS first": "There's no usable survey yet, so the record starts with a full-building designated substance survey, from [[from.full]] plus samples. The Annual Reassessment then keeps it current.",
  "Book a site visit": "Tell us the address and the materials, and we'll book the visit. Sites are usually visited within [[visitDays]] business days.",
  "Discovery call": "A 30-minute call to scope your buildings or jobs, followed by a written proposal."}}
q = f"""<section class="hero"><div class="wrap">{crumbs((None, "Obligation Check"))}
<div class="split" style="align-items:start">
<div class="hero-copy"><h1>The Obligation Check</h1><p class="lede">Answer a few questions. You'll see which legal duties apply to you, what fits, and what the first step is. Planning a renovation or demolition? Choose the project option to see whether it needs a designated substance survey. Nothing is sent until you choose to send it.</p>
<p class="small">Covers O. Reg. 278/05 (asbestos in buildings) and OHSA section 30 (designated substances on projects). General guidance only, not a site-specific assessment.</p></div>
<div class="quiz" id="quiz" aria-live="polite"><noscript>The Obligation Check needs JavaScript. You can <a href="contact.html">send us a message</a> instead.</noscript></div>
</div></div></section>"""
page("obligation-check.html", "Obligation Check | Which Asbestos Duties Apply to You?",
     "A two-minute quiz for building owners, landlords and contractors in Ontario: find out which asbestos and designated substance duties apply and what to do first.", q, None,
     extra_js=f"<script src=\"assets/ncc-rules.js?v={ASSET_V}\"></script>\n<script>window.NCC_PUBLIC={json.dumps(deep_fill(QUIZ_PUBLIC))};</script>\n")

# ---------------------------------------------------------------- local pages
# Each city page carries its own local facts: what that municipality's demolition paperwork actually asks,
# the local building stock, and city-specific questions. Keep them genuinely different: near-identical
# city pages read to Google as doorway pages. Facts were checked against the linked municipal forms (Nov 2026).
def local_page(fname, city, region, intro, permit_h2, permit, stock_h2, stock, towns, local_faq, sources):
    items = list(local_faq) + [
        (f"How much does asbestos testing cost in {city}?", "Testing a few materials starts at [[bulk.visit]] for the visit, and a designated substance survey for one work area starts at [[from.reno]]. Samples are added at [[sample]] each, with the lab's analysis of the first layer included, so the total depends on the building."),
        ("How long do results take?", "Lab results take [[labDays]] business days from when the lab receives the samples, or [[rushDays]] business days on rush. If work can't wait, we leave written interim instructions on site."),
        ("Are you independent of abatement contractors?", "Yes. We never remove or abate anything and take no referral fees, so our survey results aren't shaped by anyone who profits from removal.")]
    FAQ_HTML, FAQ_SCHEMA = faq(items)
    src = " · ".join(f'<a href="{u}" rel="noopener">{t}</a>' for t, u in sources)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, f"Asbestos testing in {city}"))}
<div class="hero-copy" style="max-width:860px"><h1>Asbestos testing and designated substance surveys in {city}</h1>
<p class="lede">{intro}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div>{byline()}</div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>{permit_h2}</h2>{"".join(f"<p>{x}</p>" for x in permit)}
<p class="small">Sources: {src}. Check the current form with the building department before you apply.</p></div>
<div class="prose"><h2>{stock_h2}</h2>{"".join(f"<p>{x}</p>" for x in stock)}
<p class="small">We also cover {towns}.</p></div>
</div></section>
<section class="section"><div class="wrap split">
<div class="prose"><h2>What we do in {region}</h2>{ul([
 '<a href="designated-substance-survey.html">Designated substance surveys</a> before renovation, repair, demolition or a tender',
 '<a href="commercial-asbestos-survey.html">Commercial, industrial and institutional surveys</a> for offices, plazas, plants, schools and churches, done while the building operates',
 '<a href="building-owners.html">The Annual Asbestos Reassessment</a> that keeps your <a href="asbestos-management-program.html">asbestos record and management program</a> current',
 '<a href="landlords.html">Suite testing and records</a> for landlords, property managers and condo corporations',
 '<a href="services.html">Abatement design and oversight</a>, and <a href="contractors.html">Type 3 clearance air testing</a>',
 '<a href="contractors.html">Testing for contractors</a>, from [[bulk.visit]] plus samples'])}</div>
<div class="prose"><h2>Common reasons people call</h2><div class="link-list" style="grid-template-columns:1fr">{"".join(f'<a href="{h}"><strong>{t}</strong></a>' for h, t in TRIGGERS)}</div></div>
</div></section>
""" + FAQ_HTML + cta()
    page(fname, f"Asbestos Testing & Designated Substance Surveys {city}, ON",
         f"Independent asbestos testing and designated substance surveys in {region if region.startswith(city + ' and ') else city + ' and ' + region}. Testing from [[bulk.visit]] plus samples, lab results in [[labDays]] business days.", body,
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
     "Landlords and property managers can book Bulk Material Sampling before a suite is renovated, so units turn over without surprises."],
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
     "On the building side, we test the materials those contractors will disturb before they cut, and come out the same or next business day when a job uncovers something.",
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
     "Contractors working in older London buildings can have the owner's report peer reviewed before they bid, and book Bulk Material Sampling when it falls short."],
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
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div>{byline()}</div></div></section>
<section class="section white"><div class="wrap split">{secs}</div></section>
<section class="section"><div class="wrap"><div class="section-head"><h2>Related</h2></div><div class="link-list">{related}</div></div></section>""" + cta()
    page(fname, title, desc, body)

def rel(*items): return "".join(f'<a href="{h}"><strong>{t}</strong><span>{s}</span></a>' for h, t, s in items)

trigger_page("asbestos-testing-before-renovation.html", "Asbestos testing before renovation",
  "Asbestos Testing Before Renovation | Windsor & SW Ontario",
  "Before walls or floors open in an older building, Ontario law requires a designated substance list. Testing from [[bulk.visit]] plus samples, results in [[labDays]] business days.",
  "Before walls, floors or ceilings open in an older building, Ontario law requires a list of every designated substance in the work area. We survey it, test it and hand you a report ready for the contractor.",
  [("What the law requires", "<p>The project owner must list all designated substances before a renovation, repair or demolition project begins and include the list in the tender (OHSA section 30). An owner who leaves one off is liable to the contractors when it turns up mid-job.</p><p>Any building built before 1990 is a candidate for asbestos-containing materials; newer buildings are much less likely to contain them.</p>"),
   ("What we test for", ul(["Floor tile and mastic, drywall joint compound, plaster and stipple ceilings", "Pipe and boiler insulation, cement board and vermiculite", "Lead in paint, solder, pipes and glazing", "Mercury in thermostats, switches and lamps", "Silica released when concrete, masonry or tile is cut", "All 11 designated substances, as the project list requires"])),
   ("Price and timing", "<p>Bulk Material Sampling for a few materials is a [[bulk.visit]] visit plus [[sample]] a sample. A renovation-scope designated substance survey for a whole work area starts at [[from.reno]] plus samples. The first layer of every sample is analyzed by the lab and included, so the total depends on the building. Lab results take [[labDays]] business days, or [[rushDays]] on rush at double the sample price.</p><p>If the job can't wait, we leave written interim instructions on site: which materials to treat as asbestos-containing and which procedures apply until results are in.</p>"),
   ("If you renovate often", "<p>Contractors can book <a href=\"contractors.html\">Bulk Material Sampling</a> before every job in an older building, and owners can keep their record current with the <a href=\"building-owners.html\">Annual Asbestos Reassessment</a>.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "What a survey covers and what to do if you find suspect material mid-job"),
      ("guide-suite-turnover-checklist.html", "Suite turnover checklist", "The materials to stop and test in older rental suites")))

trigger_page("designated-substance-survey-demolition-permit.html", "Designated substance survey for a demolition permit",
  "Designated Substance Survey for a Demolition Permit, Windsor",
  "Windsor's demolition permit checklist asks for a designated substance list. We write the pre-demolition survey for the permit and the tender. From [[from.predemo]].",
  "The City of Windsor's demolition permit checklist asks for a list of designated substances. We survey the building and write a report you can attach to the permit application and the demolition tender.",
  [("What the survey covers", "<p>A destructive survey of every space, because the building is coming down: walls opened, flooring lifted and roofs cored, so concealed materials are found before demolition. It covers all 11 designated substances plus PCBs, mould and ozone-depleting refrigerants. The building has to be vacant.</p>"),
   ("What usually follows", ul(["<strong>Abatement specification and tender package:</strong> scope of work, procedure type, quantities and bid comparison, from [[abate.spec]]", "<strong>Site inspections:</strong> pre-start, progress and glove bag checks during the work, [[abate.visit]] a visit", "<strong>Type 3 clearance:</strong> visual inspection and air testing before the enclosure comes down, from [[clr.small]]"]) + "<p class=\"small\">Larger projects are quoted above these prices.</p>"),
   ("Price and timing", "<p>A pre-demolition survey starts at [[from.predemo]], priced as a report fee plus the samples taken. Demolition surveys take more samples than a renovation report because concealed spaces are opened up. The report takes [[ta.predemo.to]] business days after fieldwork, including the lab's [[labDays]] business days. No deposit: the report fee and samples are invoiced as soon as the samples are taken, any extra layers once the results are in, and the report is released once both are paid.</p>"),
   ("Independent from the abatement", "<p>We never remove or abate anything and take no referral fees, so the survey, the specification and the clearance are all written by someone with no stake in how much removal there is.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "Built around the City of Windsor's demolition permit checklist"),
      ("services.html", "Reports and prices", "Every survey and service, with starting prices")))

trigger_page("silica-exposure-assessment.html", "Silica on renovation and demolition projects",
  "Silica on Renovation and Demolition Projects | Ontario",
  "Silica is one of Ontario's 11 designated substances. When a project will cut concrete, masonry or tile, it belongs on the designated substance list and in the contractor's control plan.",
  "Cutting, grinding or coring concrete, masonry and tile releases respirable crystalline silica, one of Ontario's 11 designated substances. If the work will disturb it, it belongs on the project's designated substance list.",
  [("Where it shows up", "<p>Concrete, mortar, brick, block, ceramic tile, drywall and plaster all contain silica. Every project-specific report we write records where silica-containing materials are and what the planned work will do to them.</p>"),
   ("What the contractor needs", ul(["The designated substance list, with silica-generating work identified", "Work classified by type, with controls such as wet cutting and local exhaust", "Training and respiratory protection where the work calls for it"])),
   ("Price", "<p>Silica is covered in every designated substance survey, from [[from.reno]]. Exposure monitoring is not available yet. Call <a href=\"tel:+15198909654\">519-890-9654</a> or <a href=\"contact.html\">contact us</a> to be notified when it launches.</p>"),
   ("For contractors", "<p>See <a href=\"contractors.html\">testing and clearance for contractors</a>.</p>")],
  rel(("services.html", "Reports and prices", "Every survey and service, with starting prices"),
      ("contractors.html", "Testing and clearance for contractors", "Bulk Material Sampling, call-outs and clearance air testing")))

trigger_page("isocyanate-air-monitoring.html", "Isocyanate air monitoring",
  "Isocyanate Air Monitoring | Southwestern Ontario",
  "What O. Reg. 490/09 asks of employers who spray or mix isocyanates. Exposure monitoring is not available yet.",
  "Collision and auto body paint booths, paint lines, spray foam installers and polyurethane manufacturers work with isocyanates, one of Ontario's designated substances.",
  [("What the regulation asks", ul(["A written exposure assessment made with your JHSC, redone after any change that could significantly affect exposure", "A control program where health may be affected", "Air monitoring, with results posted for 14 days, copied to the JHSC and kept 5 years", "Medical surveillance, which applies to isocyanates"])),
   ("What we offer", "<p>Exposure monitoring is not available yet. Call <a href=\"tel:+15198909654\">519-890-9654</a> or <a href=\"contact.html\">contact us</a> to be notified when it launches.</p>"),
   ("Your building", "<p>Older shops also carry the asbestos duties every building owner has. See the <a href=\"building-owners.html\">Annual Asbestos Reassessment</a>.</p>")],
  rel(("guide-designated-substance-self-check.html", "Designated substance self-check", "A one-page test of whether O. Reg. 490/09 applies to you"),
      ("employers.html", "Designated substances at work", "What employers need on file under O. Reg. 490/09")))

# ---------------------------------------------------------------- commercial search pages (2026-11-25, SEO pass)
# One page per thing commercial buyers search for: the survey itself, commercial buildings, the tender list, the
# management program, the 11 substances, lead and where asbestos hides. Each page answers the question in full, links
# to the product that fits, and carries its own FAQ. Prices are tokens only, like everywhere else.
def tbl(head, rows, wide=False):
    th = "".join(f'<th scope="col">{h}</th>' for h in head)
    body = "".join("<tr>" + f'<th scope="row">{r[0]}</th>' + "".join(f'<td data-label="{H.escape(re.sub("<[^>]+>", "", head[i + 1]))}">{c}</td>' for i, c in enumerate(r[1:])) + "</tr>" for r in rows)
    return f'<div class="table-wrap stack"><table class="data{" wide" if wide else ""}"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

def topic_page(fname, title, desc, h1, lede, sections, faq_items, related, schema=None, crumb=None, cta_args=()):
    """sections: (h2, html) pairs, one band each, alternating white and plain. A tuple ("wide", h2, html) gets the
    full width (tables)."""
    bands = []
    for i, sec in enumerate(sections):
        wide = sec[0] == "wide"; h2, inner = sec[1:] if wide else sec
        bands.append(f'<section class="section{" white" if i % 2 == 0 else ""}"><div class="wrap">' +
                     (f'<div class="section-head"><h2>{h2}</h2></div>{inner}' if wide else f'<div class="prose" style="max-width:820px"><h2>{h2}</h2>{inner}</div>') + "</div></section>")
    FAQ_HTML, FAQ_SCHEMA = faq(faq_items)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, crumb or h1))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row"><a class="btn amber" href="contact.html">Ask for a quote</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div>{byline()}</div></div></section>
{"".join(bands)}
<section class="section white"><div class="wrap"><div class="section-head"><h2>Related</h2></div><div class="link-list">{related}</div></div></section>""" + FAQ_HTML.replace('class="section white"', 'class="section"') + cta(*cta_args)
    page(fname, title, desc, body, schema=[FAQ_SCHEMA] + ([schema] if schema else []))

def prod_rows(keys, link=True):
    return [(f'<a href="{pg}">{n}</a>' if link else n, w_, t, money(p)) for (n, p, w_, g, t, pg), k in zip(PRODUCTS, PKEY) if k in keys]

INDEPENDENT = "<p>We never remove or abate anything and take no referral fees. Nobody on our side gains from finding more asbestos, or less.</p>"
REPORT_CONTENTS = ul([
 "<strong>At a glance and a summary of findings</strong> written so it can go straight into tender documents: friable, non-friable and presumed asbestos-containing materials, materials awaiting lab results, lead, and any other designated substance, each with its sample numbers and quantity",
 "<strong>Building and scope:</strong> the areas surveyed, the areas not accessed (materials there that could contain asbestos are treated as asbestos-containing until inspected), and the earlier reports and drawings we reviewed",
 "<strong>How the survey was done:</strong> homogeneous materials sampled to at least the minimum in Table 1 of O. Reg. 278/05, chain of custody and analysis by a CALA-accredited lab",
 "<strong>Plans:</strong> where each sample was taken and where the asbestos-containing materials are",
 "<strong>A register of every material:</strong> location, condition, quantity in metric with imperial beside it, and what to do with it",
 "<strong>All 11 designated substances</strong> addressed, with lead in paint reported against the EACO Lead Guideline classes",
 "<strong>Before work starts:</strong> how to handle what was found, and the owner's duties under Ontario law",
 "<strong>Lab certificates and a photo log,</strong> limitations and sign-off",
])

# ---- 1. the survey itself
DSS_KEYS = ("reno", "full", "predemo")
topic_page("designated-substance-survey.html",
  "Designated Substance Survey (DSS) | Windsor & SW Ontario",
  "Independent designated substance surveys for Ontario renovations, tenders, purchases and demolition permits. All 11 substances, from [[from.reno]] plus samples.",
  "Designated substance surveys in Windsor and southwestern Ontario",
  f"A designated substance survey (DSS) finds and lists the designated substances in a building or work area before a project starts, so the owner meets section 30 of the Occupational Health and Safety Act and every bidder prices the same job. We survey offices, plazas, plants, schools, churches, clinics and apartment buildings across {REGIONS}.",
  [("When you need one", ul([
      "<strong>Before a renovation, repair or demolition project</strong> is tendered or a contract is signed. The owner has to list every designated substance in the work area first.",
      '<strong>For a demolition permit.</strong> Windsor\'s demolition checklist asks for the list; see <a href="designated-substance-survey-demolition-permit.html">surveys for a demolition permit</a>.',
      "<strong>When you buy a building or plan capital work,</strong> so the cost of what's in it is known before you commit.",
      "<strong>When there's no survey on file,</strong> or the one you have doesn't cover the area the work will touch. A full-building survey also becomes the base for your <a href=\"asbestos-management-program.html\">asbestos record</a>."]) +
      "<p>Building age changes how big the job is, never whether a list is needed. A newer building usually has fewer suspect materials and a smaller report; it still needs one.</p>"),
   ("wide", "Which survey fits", tbl(["Survey", "When you need it", "Turnaround", "From"], prod_rows(DSS_KEYS, link=False), wide=True) +
      '<p class="small" style="margin-top:12px">CAD before HST, plus samples at [[sample]] each ([[sample.demo]] on a demolition survey), the lab\'s analysis of the first layer included. Turnarounds are from the end of fieldwork and include the lab\'s [[labDays]] business days.</p>'),
   ("What the report contains", "<p>One report, one data source, so the summary, the register and the plans never contradict each other.</p>" + REPORT_CONTENTS +
      '<p>Every report comes as a PDF with one printed binder. See <a href="register-example.html">an example register</a> built from the same kind of data.</p>'),
   ("wide", "Report fees by building size", f"""<div class="table-wrap stack"><table class="data wide"><thead><tr><th scope="col">Survey</th><th scope="col" class="num">Class A</th><th scope="col" class="num">Class B</th><th scope="col" class="num">Class C</th><th scope="col" class="num">Class D</th><th scope="col">Turnaround</th></tr></thead><tbody>
{cls_row("Renovation-scope DSS (one work area)", "reno")}{cls_row("Full-building DSS", "full")}{cls_row("Pre-demolition DSS (destructive, building vacant)", "predemo")}</tbody></table></div>
<p class="small" style="margin-top:12px">Class A is under [[classA.m2]] m² [[[classA.ft2]] sq ft], Class B up to [[classB.m2]] m² [[[classB.ft2]] sq ft], Class C up to [[classC.m2]] m² [[[classC.ft2]] sq ft], and Class D anything larger. Samples are extra. Your quote gives the report fee and an estimated number of samples in writing, and we ask before going over that estimate.</p>"""),
   ("How a survey runs", ul([
      "<strong>Quote:</strong> send the address, year built, floor area and the planned work. We confirm the report fee and the estimated samples in writing.",
      "<strong>Fieldwork:</strong> scheduled around your tenants or production. After-hours or weekend fieldwork at your request is +[[afterHours]] on the fieldwork portion.",
      "<strong>Lab:</strong> results in [[labDays]] business days from when the lab receives the samples, or [[rushDays]] on rush at double the sample price.",
      "<strong>Invoices:</strong> the report fee and samples as soon as the samples are taken, any extra layers once the results are in. The report is released once both are paid. No deposit."]) + INDEPENDENT)],
  [("What is a designated substance survey?", "A survey that identifies which of Ontario's 11 designated substances are in a building or work area, where they are and how much there is, so the owner can give the list to contractors before a project. Asbestos, lead, mercury and silica are the ones usually found in buildings."),
   ("Is a designated substance survey required in Ontario?", "Before a project, yes. Section 30 of the Occupational Health and Safety Act requires the project owner to find out which designated substances are present and give the list to the constructor and every bidder before a binding contract. There's no building-age or size cutoff."),
   ("What's the difference between a DSS and an asbestos survey?", "An asbestos survey looks only for asbestos. A designated substance survey covers all 11 designated substances, which is what section 30 asks the owner to list. Every survey we write is a designated substance survey."),
   ("How long is a designated substance survey good for?", "The law doesn't set an expiry date. What matters is whether the report covers the area and the work now planned, and whether it still matches the building. If the scope has grown or materials have changed since, the report needs to be extended or redone."),
   ("Who pays for the survey?", "The project owner, because the duty is the owner's. A contractor can arrange it on the owner's behalf, and the report is addressed to the owner."),
   ("Do you also remove the asbestos?", "No. We survey, test, write abatement specifications, oversee the work and test the air, but we never remove anything and take no referral fees.")],
  rel(("designated-substance-list-tender.html", "The designated substance list for a tender", "What section 30 asks of owners, and when to book"),
      ("commercial-asbestos-survey.html", "Commercial and industrial buildings", "Surveying offices, plazas, plants and institutions while they operate"),
      ("designated-substances-ontario.html", "Ontario's 11 designated substances", "Where each one turns up in buildings"),
      ("services.html", "Reports and prices", "Every survey and service, with starting prices")),
  schema=service_schema("Designated substance survey", "Designated substance surveys (all 11 Ontario designated substances) in Windsor and southwestern Ontario", F["reno"]),
  crumb="Designated substance surveys")

# ---- 2. commercial, industrial and institutional buildings
topic_page("commercial-asbestos-survey.html",
  "Commercial Asbestos Surveys | Windsor & SW Ontario",
  "Asbestos and designated substance surveys for offices, plazas, plants, schools and other commercial buildings in Windsor and SW Ontario. From [[from.reno]].",
  "Asbestos surveys for commercial, industrial and institutional buildings",
  "Offices, plazas, plants, warehouses, schools, churches, clinics and municipal buildings. We survey them while they operate, write the list your contractors need, and keep the owner's asbestos record current between projects.",
  [("Who calls us", ul([
      "<strong>Property managers and owners</strong> of offices, plazas and mixed-use buildings, before a tenant fit-out or a roof, mechanical or flooring project",
      "<strong>Plant and facility managers</strong> planning a shutdown, a line change or a demolition inside the plant",
      "<strong>School boards, churches, clinics and municipalities</strong> that tender their projects and need the list in the tender documents",
      "<strong>General and restoration contractors</strong> working for those owners, who need the owner's list before they cut",
      "<strong>Buyers and their lenders</strong> who want to know what a building holds before closing"])),
   ("wide", "Which service fits the job", tbl(["The situation", "What fits", "From"], [
      ("A tenant space or one area being renovated", '<a href="designated-substance-survey.html">Renovation-scope DSS</a> for that work area', "[[from.reno]]"),
      ("A whole building: purchase, capital plan, or no survey on file", '<a href="designated-substance-survey.html">Full-building DSS</a>', "[[from.full]]"),
      ("A building coming down", '<a href="designated-substance-survey-demolition-permit.html">Pre-demolition DSS</a>', "[[from.predemo]]"),
      ("A few materials before maintenance work", '<a href="contractors.html">Bulk Material Sampling</a>', "[[bulk.visit]] plus samples"),
      ("Keeping the O. Reg. 278/05 asbestos record current", '<a href="building-owners.html">Annual Asbestos Reassessment</a>', "[[from.reassess]]"),
      ("Asbestos has to come out", '<a href="services.html">Abatement Design &amp; Oversight</a>', "[[abate.spec]]"),
      ("A Type 3 enclosure ready to come down", '<a href="contractors.html">Clearance Air Testing</a>', "[[clr.small]]")], wide=True) +
      '<p class="small" style="margin-top:12px">CAD before HST. Larger or more complex jobs are quoted above these starting prices.</p>'),
   ("Surveying a building that's open", ul([
      "We work around tenants, shifts and production, and book mechanical rooms, roofs and ceiling spaces with your maintenance staff.",
      "Samples are small. Each spot is wetted, sealed and patched, and labelled where it was taken.",
      "After-hours or weekend fieldwork at your request is +[[afterHours]] on the fieldwork portion of the fee.",
      "Areas we can't get into are named in the report. Materials there that could contain asbestos are treated as asbestos-containing until they're inspected, so nobody assumes they match the rooms we did see."])),
   ("What we need to quote", ul([
      "The address, the year it was built and any additions",
      "Floor area in m² or sq ft, and the number of storeys",
      "The work planned and where, or the reason for the survey (purchase, tender, demolition)",
      "Any earlier asbestos or designated substance reports and drawings",
      "Access: hours, keys, escorts, shutdown windows, and the tender or start date"]) +
      '<p>Send it through the <a href="contact.html">contact form</a> and we reply within one business day. Not sure what applies? <a href="obligation-check.html">Take the Obligation Check</a>.</p>'),
   ("Where asbestos hides in commercial buildings", '<p>Sprayed fireproofing on structural steel, pipe and boiler insulation, lay-in ceiling tiles, floor tile and mastic, cement panels, roofing and caulking are the usual finds in buildings from before the 1990s. See <a href="asbestos-in-commercial-buildings.html">where asbestos hides in commercial and industrial buildings</a> for the full list.</p>' + INDEPENDENT)],
  [("Do commercial buildings need an asbestos survey in Ontario?", "Two rules apply. Before any renovation, repair or demolition project, section 30 of the Occupational Health and Safety Act requires the owner to list the designated substances in the work area. And where a building has asbestos-containing material, O. Reg. 278/05 requires the owner to keep a record of it, re-inspect it at least every 12 months and have an asbestos management program."),
   ("Can you survey while the building is open?", "Yes. We schedule around tenants and production, keep sampling small and sealed, and can work after hours or on weekends at your request."),
   ("Do my tenants have to be told?", "Where there is asbestos-containing material, the owner has to give written notice to occupiers about the asbestos in the areas they occupy, and tell contractors before work that could disturb it. Our reports and registers give you what to send."),
   ("Do you survey industrial plants?", "Yes: process areas, boiler houses, warehouses and offices. Tell us about current and past processes, because some designated substances, like isocyanates or benzene, come from what a plant did rather than what it's built of."),
   ("How much does a commercial asbestos survey cost?", "A renovation-scope survey starts at [[from.reno]] and a full-building survey at [[from.full]], by building size, plus samples at [[sample]] each. We confirm the fee and the estimated samples in writing before any work starts.")],
  rel(("designated-substance-survey.html", "Designated substance surveys", "What a survey covers, the report and prices by building size"),
      ("asbestos-management-program.html", "Asbestos management programs", "What O. Reg. 278/05 asks of building owners"),
      ("asbestos-in-commercial-buildings.html", "Where asbestos hides", "Materials to know about in commercial and industrial buildings"),
      ("designated-substance-list-tender.html", "The list for a tender", "Section 30 for owners who tender their projects")),
  schema=service_schema("Commercial asbestos survey", "Asbestos and designated substance surveys of commercial, industrial and institutional buildings in southwestern Ontario", F["reno"]),
  crumb="Commercial buildings")

# ---- 3. the section 30 list for a tender
topic_page("designated-substance-list-tender.html",
  "Designated Substance List for a Tender | OHSA Section 30",
  "What section 30 of Ontario's OHSA asks of project owners before a tender, who must receive the list, and when to book the survey. Surveys from [[from.reno]].",
  "The designated substance list for a tender (OHSA section 30)",
  "For municipalities, school boards, institutions, property managers and the contractors who bid their work. The owner has to know what's in the work area before the project is tendered, and every bidder has to see the same list.",
  [("What section 30 asks", ul([
      "Before a project begins, the owner determines whether any designated substances are present at the project site and prepares a list of them.",
      "If the project is tendered, the list goes into the tender documents. Either way, the constructor gets it before a binding contract is signed.",
      "The constructor makes sure every prospective contractor and subcontractor receives the list before they're bound by a contract.",
      "An owner who leaves a designated substance off the list is liable to the constructor and every contractor for their losses when it turns up."]) +
      "<p>There's no building-age or project-size threshold. A small repair in a newer building still needs a list; it's just a shorter one.</p>"),
   ("When to book the survey", "<p>Before the drawings go out. A renovation-scope survey takes [[ta.reno.to]] business days after fieldwork and a full-building survey [[ta.full.to]], including the lab's [[labDays]] business days, so book it while the design is being finished. If the job can't wait for standard lab results, rush analysis takes [[rushDays]] business days at double the sample price.</p>"
      "<p>If the scope grows after the survey, the new areas need to be added before that work is tendered.</p>"),
   ("What bidders need from the report", ul([
      "Locations they can find: room names and plans showing where each material is",
      "Quantities in metric with imperial beside them, so removal can be priced",
      "Friable and non-friable materials kept separate, and presumed materials named as presumed",
      "Lead results by class, so the paint work can be priced with the right precautions",
      "Areas not accessed named, with materials there that could contain asbestos treated as asbestos-containing until inspected"]) +
      "<p>The report's summary of findings can go into the tender documents as the list. The whole report still has to be given to the constructor.</p>"),
   ("Already have a report?", '<p>A report written for different work, or by a firm you no longer use, may not cover what you\'re tendering now. A <a href="services.html">peer review</a> from [[from.peer]] tells you what\'s missing and what to fix before it goes out. When removal is needed, <a href="services.html">Abatement Design &amp; Oversight</a> writes the specification and tender package from [[abate.spec]].</p>' + INDEPENDENT)],
  [("Does the list have to cover all 11 designated substances?", "Yes. Section 30 is about designated substances, not just asbestos. In most buildings asbestos, lead, mercury and silica are the ones found; the others are considered and noted, usually because of a past industrial use."),
   ("Can we reuse an old designated substance report?", "Only if it covers the area and the work now planned and still matches the building. Have it reviewed if you're not sure; a gap found during the project costs far more than one found before the tender."),
   ("Who has to receive a copy?", "The constructor, before a binding contract, and through the constructor every prospective contractor and subcontractor before they're bound. If the project is tendered, the list is part of the tender documents."),
   ("What happens if something not on the list turns up?", "Work in that area stops except to identify the material, and the Ministry, the owner, the contractor and the joint health and safety committee are notified. The owner is liable for the contractors' losses from a designated substance left off the list."),
   ("How much does a survey for a tender cost?", "A renovation-scope survey for one work area starts at [[from.reno]], a full-building survey at [[from.full]], and a pre-demolition survey at [[from.predemo]], plus samples at [[sample]] each. All prices are CAD before HST.")],
  rel(("designated-substance-survey.html", "Designated substance surveys", "Which survey fits, the report and prices"),
      ("designated-substance-survey-demolition-permit.html", "Surveys for a demolition permit", "Built around Windsor's demolition checklist"),
      ("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "A printable checklist, including what to do mid-job")),
  schema=service_schema("Designated substance survey for a tender", "Designated substance lists for tendered projects under OHSA section 30 in southwestern Ontario", F["reno"]),
  crumb="The list for a tender", cta_args=("Tendering a project soon?", "Send us the drawings and the tender date and we'll quote the survey, or take the Obligation Check to see what applies.", "obligation-check.html#project"))

# ---- 4. asbestos management program (O. Reg. 278/05)
topic_page("asbestos-management-program.html",
  "Asbestos Management Program Ontario | O. Reg. 278/05",
  "What O. Reg. 278/05 asks of Ontario building owners: the asbestos record, yearly re-inspection, notices and a management program. Reassessment from [[from.reassess]].",
  "Asbestos management programs and records for Ontario buildings",
  "People search for an asbestos management plan; Ontario's regulation calls it a program. If your building has asbestos-containing material, it's the set of records and procedures that keeps everyone working in it safe, and it's the first thing a Ministry inspector asks to see.",
  [("What O. Reg. 278/05 asks of owners", ul([
      "Keep a record of the asbestos-containing material in the building: where it is, its condition, and whether it's friable. Keep it on the premises.",
      "Re-inspect the listed materials and update the record at least once every 12 months, and whenever you learn something new.",
      "Give written notice to occupiers about asbestos in the areas they occupy, and tell contractors and employers before work that could disturb it.",
      "Have an asbestos management program, and train the workers who work on or near the material.",
      "When asbestos-containing material falls or is damaged, deal with it: isolate it, then repair, seal, enclose or remove it."])),
   ("What a good program covers", ul([
      "Who is responsible for it, by name",
      "The record and a register anyone can check before work starts",
      "How work near listed materials is approved, and by whom",
      "What staff do when material is damaged or something suspect turns up",
      "Notices, training and inspection records, kept together in the on-site binder"]) +
      "<p>In the Ministry's 2023–24 asbestos-in-buildings campaign, the most common orders were for not following the asbestos management program and not keeping the record on site.</p>"),
   ("How we keep it current", '<p>The <a href="building-owners.html">Annual Asbestos Reassessment</a> builds your record in year one from your existing survey, then re-inspects every listed material each year, rates its condition, updates the record and sends the notices. You get a <a href="register-example.html">register snapshot</a> you can show an inspector or a contractor on a phone, and a PDF for the binder.</p>'
      "<p>It starts at [[from.reassess]] per building for the whole first year. If there isn't a usable survey yet, a full-building designated substance survey comes first, from [[from.full]] plus samples. Asbestos awareness training for building staff is [[train.aware]] a session.</p>"),
   ("wide", "Annual Reassessment prices by building size", reassess_table())],
  [("Is an asbestos management program required in Ontario?", "Where a building has asbestos-containing material, yes. O. Reg. 278/05 requires the owner to keep a record, re-inspect at least every 12 months, notify occupiers and contractors, train workers and have an asbestos management program."),
   ("How often does the asbestos record have to be updated?", "At least once every 12 months, and whenever new information comes to light, such as a lab result, damage or removal."),
   ("Does the Annual Reassessment include a designated substance survey?", "No, on purpose. A survey is triggered by a project, not the calendar. The reassessment keeps your record current between projects; a project still gets its own survey when it comes."),
   ("We don't have a survey. Where do we start?", "With a full-building designated substance survey, from [[from.full]] plus samples. It becomes the record the Annual Reassessment keeps current.")],
  rel(("building-owners.html", "Annual Asbestos Reassessment", "Prices, what's included and the terms"),
      ("guide-inspector-ready-binder.html", "Inspector-ready binder checklist", "What a Ministry inspector checks, as a printable list"),
      ("register-example.html", "Example register", "What a reassessment client sees on a phone"),
      ("commercial-asbestos-survey.html", "Commercial buildings", "Surveys for offices, plazas, plants and institutions")),
  schema=service_schema("Asbestos management program and annual reassessment", "O. Reg. 278/05 asbestos records, re-inspection and notices for Ontario building owners", F["reassess"]),
  crumb="Asbestos management programs", cta_args=("Is your asbestos record within 12 months?", "The Obligation Check takes two minutes and tells you what your buildings need first.", "obligation-check.html#building"))

# ---- 5. the 11 designated substances
topic_page("designated-substances-ontario.html",
  "Ontario's 11 Designated Substances in Buildings",
  "Ontario's 11 designated substances: which ones turn up in buildings, where to look, and how a designated substance survey deals with each one.",
  "Ontario's 11 designated substances, and where they turn up in buildings",
  "Ontario regulates 11 designated substances. Four of them are found in ordinary buildings; the rest come mostly from industrial processes. A designated substance survey has to consider all 11, so every survey we write does.",
  [("wide", "Where each one turns up", tbl(["Substance", "Where it turns up", "What the survey does"], [
      ("Asbestos", "Insulation, sprayed fireproofing, floor tile and mastic, plaster, joint compound, ceiling tile, cement products, roofing, caulking", 'Samples each suspect material for lab analysis, or presumes it asbestos-containing. See <a href="asbestos-in-commercial-buildings.html">where asbestos hides</a>.'),
      ("Lead", "Paint and coatings on older trim, doors, windows and structural steel; solder, flashing, old pipes", 'Samples painted surfaces the work will disturb and reports them by class. See <a href="lead-paint-survey.html">lead paint testing</a>.'),
      ("Mercury", "Fluorescent and high-intensity lamps, older thermostats and switches, manometers and gauges", "Records where devices are, so they're removed intact before the work"),
      ("Silica", "Concrete, brick, block, mortar, tile, plaster and drywall", "Notes where the planned work will cut, grind, drill or core them, so the contractor plans dust controls"),
      ("Isocyanates", "Spray foam insulation, polyurethane coatings, auto body and paint shops", "Records where they're used or will be applied"),
      ("Arsenic", "Older pressure-treated wood, some pesticide storage and industrial sites", "Notes treated wood and past uses that matter"),
      ("Benzene", "Fuel storage, refineries and chemical plants", "Records past and present process use"),
      ("Vinyl chloride, acrylonitrile", "Plastics and chemical manufacturing", "Records process use; rarely relevant outside those plants"),
      ("Ethylene oxide", "Sterilizers in hospitals, clinics and labs", "Records sterilizers and their removal"),
      ("Coke oven emissions", "Steel making", "Records process use; not found in ordinary buildings")], wide=True)),
   ("Often in the same report, though not designated", '<p>PCBs in older fluorescent light ballasts, transformers and some caulking, ozone-depleting refrigerants in old cooling equipment, and mould. They aren\'t designated substances, but demolition and renovation paperwork often asks about them. We add them to a survey for [[hazAddon]], with any samples at the usual sample prices.</p>'),
   ("Which rule applies", ul([
      "<strong>Before a project:</strong> section 30 of the Occupational Health and Safety Act. The owner lists the designated substances in the work area before tendering or contracting.",
      '<strong>Asbestos in buildings:</strong> O. Reg. 278/05, which sets the owner\'s record, re-inspection and notice duties and how asbestos work is classified. See <a href="asbestos-management-program.html">asbestos management programs</a>.',
      "<strong>Workplaces that use a designated substance:</strong> O. Reg. 490/09, which covers exposure assessments and control programs. It doesn't apply on construction projects."]) + INDEPENDENT)],
  [("What are Ontario's 11 designated substances?", "Acrylonitrile, arsenic, asbestos, benzene, coke oven emissions, ethylene oxide, isocyanates, lead, mercury, silica and vinyl chloride."),
   ("Which designated substances are found in buildings?", "Asbestos, lead, mercury and silica, in almost every older building. Isocyanates and arsenic show up in some. The others are tied to industrial processes."),
   ("Does a designated substance survey test for all 11?", "It considers all 11. Materials that can contain asbestos or lead are sampled for the lab; mercury devices are recorded where they're found; silica-containing materials are noted where the work will disturb them; and the process substances are covered through the building's current and past uses."),
   ("Are PCBs a designated substance?", "No, but they're often asked about on demolition and renovation projects. We can add PCBs, ozone-depleting refrigerants and mould to a survey for [[hazAddon]].")],
  rel(("designated-substance-survey.html", "Designated substance surveys", "Which survey fits, the report and prices"),
      ("lead-paint-survey.html", "Lead paint testing", "Before renovation and demolition"),
      ("asbestos-in-commercial-buildings.html", "Where asbestos hides", "Materials in commercial and industrial buildings")),
  crumb="The 11 designated substances")

# ---- 6. lead paint
topic_page("lead-paint-survey.html",
  "Lead Paint Testing Before Renovation | Windsor, ON",
  "Lead paint testing before renovation and demolition in Windsor and SW Ontario, reported against the EACO Lead Guideline classes. Part of every DSS.",
  "Lead paint testing before renovation and demolition",
  "Lead is one of Ontario's designated substances, and older paint and industrial coatings are where it's usually found. When the work will sand, grind, cut, torch or strip painted surfaces, the contractor needs to know which ones contain lead before pricing the job.",
  [("Where lead turns up", ul([
      "Paint on trim, doors, windows, radiators and walls in older buildings",
      "Primers and coatings on structural steel, tanks, railings and industrial equipment, which kept lead long after house paint stopped",
      "Solder, flashing, old water service pipes and some window glazing"])),
   ("How we test and report it", "<p>We take paint samples from the surfaces the planned work will disturb and send them to a CALA-accredited lab. Results are reported against the EACO Lead Guideline classes, which tell the contractor what precautions each kind of work needs. The report says which surfaces can be worked on normally and where there must be no sanding, grinding, torch cutting or heat gun without lead precautions.</p>"
      "<p>Lead is part of every designated substance survey we write, alongside asbestos, mercury, silica and the rest of the 11.</p>"),
   ("Price", '<p>Lead is covered in every <a href="designated-substance-survey.html">designated substance survey</a>, from [[from.reno]] for one work area plus samples. If you only need a few painted surfaces checked, <a href="contact.html">tell us what they are</a> and we\'ll quote it.</p>' + INDEPENDENT)],
  [("Is there an Ontario regulation for lead on construction projects?", "Lead is a designated substance, so it belongs on the section 30 list before a project. The Ministry of Labour's guideline on lead on construction projects, and the EACO Lead Guideline used across the industry, set out how lead work is classified and controlled."),
   ("Does paint have to be stripped before demolition?", "Not always. What matters is how the work disturbs it. Demolishing painted walls is treated differently from sanding or torch cutting painted steel. The report tells the contractor which work needs which precautions."),
   ("Can you test lead without a full survey?", "Yes. Tell us which surfaces and what work is planned, and we'll quote the visit and the samples.")],
  rel(("designated-substances-ontario.html", "Ontario's 11 designated substances", "Where each one turns up in buildings"),
      ("designated-substance-survey.html", "Designated substance surveys", "Which survey fits, the report and prices"),
      ("contractors.html", "Testing for contractors", "Bulk Material Sampling and call-outs")),
  crumb="Lead paint testing")

# ---- 7. where asbestos hides in commercial and industrial buildings
topic_page("asbestos-in-commercial-buildings.html",
  "Where Asbestos Hides in Commercial Buildings | Ontario",
  "Asbestos-containing materials in Ontario offices, plazas, plants, schools and churches: where they are, whether they're friable, and what disturbs them.",
  "Where asbestos hides in commercial and industrial buildings",
  "Canada banned most asbestos products on December 30, 2018, so any building material put in before then can contain it. In commercial and industrial buildings these are the materials that turn up most, and the work that disturbs them.",
  [("wide", "Materials to know about", tbl(["Material", "Where you find it", "Friable?", "What disturbs it"], [
      ("Sprayed fireproofing", "Structural steel beams, decks and columns, often above the ceiling", "Usually friable", "Ceiling work, cabling, HVAC and sprinkler work"),
      ("Sprayed or trowelled texture and acoustic finishes", "Ceilings in gyms, halls, corridors and stairwells", "Usually friable", "Drilling, scraping, fixtures, painting prep"),
      ("Pipe, boiler and tank insulation, and fitting cement", "Mechanical rooms, risers, crawlspaces, above ceilings", "Usually friable", "Mechanical work, leaks, damage, shutdowns"),
      ("Lay-in ceiling tiles", "Offices, schools, clinics and plazas", "Can be either", "Lifting tiles for cabling or HVAC, replacement"),
      ("Floor tile and mastic, sheet flooring", "Corridors, classrooms, offices, under newer flooring", "Tile and mastic usually not; felt backing can be", "Lifting, grinding, levelling, demolition"),
      ("Drywall joint compound and plaster", "Walls and ceilings", "Not while intact", "Cutting, sanding, opening walls, demolition"),
      ("Cement products: panels, pipe, ducts, lab benches and fume hoods", "Exterior cladding, soffits, labs, plants, underground services", "Usually not", "Drilling, cutting, breaking"),
      ("Roofing felts, mastics and flashing cement", "Flat roofs, parapets, roof penetrations", "Usually not", "Re-roofing, coring, new rooftop units"),
      ("Caulking, sealants and window putty", "Windows, expansion joints, cladding joints", "Usually not", "Window replacement, joint repair"),
      ("Gaskets, rope seals, fire doors and firestopping", "Boilers, ovens, flanges, fire doors, wall penetrations", "Can be either", "Equipment repair and removal, new penetrations"),
      ("Vermiculite", "Loose fill in block wall cores and attics", "Friable", "Drilling or opening block walls")], wide=True) +
      '<p class="small" style="margin-top:12px">"Friable" means it can be crumbled or powdered by hand pressure when dry. Friability is decided on site for each material, and it changes how the work is classified under O. Reg. 278/05.</p>'),
   ("What clears a material, and what doesn't", "<p>A material is only left off the sampling list when it can't contain asbestos because of what it's made of (bare metal, glass, solid wood, poured concrete, fibreglass batt), or when it's a documented product: we know what it is, where and when it went in, and that it was made without asbestos or installed on or after December 30, 2018. Looking new, or being in a newer building, never clears a material on its own.</p>"),
   ("Windsor's buildings", '<p>Windsor-Essex has a large stock of auto-era plants, warehouses, schools, churches and plazas built before the 1990s. Boiler houses and process areas tend to hold the friable materials; offices and schools hold the tile, ceiling and plaster finds. A <a href="commercial-asbestos-survey.html">commercial survey</a> finds them before your contractor does.</p>' + INDEPENDENT)],
  [("How do I know if a material contains asbestos?", "Only a lab result tells you, or you treat the material as asbestos-containing. Suspect materials are sampled and analyzed by a CALA-accredited lab; anything not sampled is presumed to contain asbestos."),
   ("Is asbestos in a commercial building illegal?", "No. Asbestos-containing material that's in good condition can stay in place. The owner has to record it, re-inspect it at least every 12 months, notify occupiers and contractors, and manage it under O. Reg. 278/05."),
   ("Our building was built in the 1990s. Can it still contain asbestos?", "It can. Asbestos products stayed on the Canadian market until the end of 2018, and older materials were reused or left in place during renovations. Age changes how much we expect to find, not whether to look."),
   ("What does testing cost?", "Testing a few materials starts at [[bulk.visit]] for the visit plus [[sample]] a sample. A survey of a work area starts at [[from.reno]] plus samples.")],
  rel(("commercial-asbestos-survey.html", "Commercial and industrial buildings", "Which service fits, and how we survey a building that's open"),
      ("designated-substance-survey.html", "Designated substance surveys", "The report and prices by building size"),
      ("asbestos-management-program.html", "Asbestos management programs", "What O. Reg. 278/05 asks of owners")),
  crumb="Where asbestos hides")

# ---------------------------------------------------------------- guides (lead magnets)
def guide_page(fname, h1, title, desc, lede, items, after, cta_href):
    lis = "".join(f"<li><div><b>{a}</b><span>{b}</span></div></li>" for a, b in items)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, h1))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row no-print"><button class="btn ghost" type="button" onclick="window.print()">Print this checklist</button><a class="btn amber" href="{cta_href}">Take the Obligation Check</a></div></div></div></section>
<section class="section white"><div class="wrap"><div class="prose" style="max-width:820px"><ul class="checklist">{lis}</ul>{after}
<p class="small">Last reviewed {fdate(GUIDES_REVIEWED)} by {e(SITE['founder'])}. This checklist is general guidance, not legal advice. Ontario regulations referenced: O. Reg. 278/05, OHSA section 30 and O. Reg. 490/09.</p></div></div></section>""" + cta("Want someone to keep it current for you?", "The Annual Asbestos Reassessment builds your record in year one and updates it every year, from [[from.reassess]] per building.", cta_href)
    art = {"@context": "https://schema.org", "@type": "Article", "headline": h1, "description": desc, "url": SITE["domain"] + "/" + fname,
        "datePublished": GUIDES_REVIEWED, "dateModified": GUIDES_REVIEWED, "inLanguage": "en-CA",
        "author": {"@type": "Person", "@id": SITE["domain"] + "/#founder", "name": SITE["founder"]}, "publisher": {"@id": BIZ_ID},
        "about": ["O. Reg. 278/05", "OHSA section 30", "O. Reg. 490/09"]}
    page(fname, title, desc, body, schema=art)

guide_page("guide-inspector-ready-binder.html", "Inspector-ready binder checklist",
  "Inspector-Ready Asbestos Binder Checklist | Ontario Owners",
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
  "Suite Turnover Asbestos Checklist for Ontario Landlords",
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
  "<p>Bulk Material Sampling before a turnover is a [[bulk.visit]] visit plus [[sample]] a sample, with results in [[labDays]] business days. See <a href=\"landlords.html\">records and suite testing for landlords</a>.</p>", "obligation-check.html#rental")

guide_page("guide-designated-substance-self-check.html", "Designated substance self-check",
  "Does O. Reg. 490/09 Apply to You? A Designated Substance Check",
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
  "Demolition & Renovation DSS Guide | Windsor-Essex",
  "What a designated substance survey covers before demolition or renovation in Windsor-Essex, and what to do when you find suspect material mid-job.",
  "Built around the City of Windsor's demolition permit checklist, which asks for a designated substance list. The second half covers what to do when suspect material turns up mid-job.",
  [("The owner lists every designated substance before the project begins", "OHSA section 30 puts this on the project owner, and the list goes into the tender."),
   ("The list covers all 11 substances in the work area", "Not just asbestos: lead, mercury, silica and the rest are part of the same list."),
   ("Demolition permits need it", "The City of Windsor's demolition permit checklist asks for the designated substance list with the application."),
   ("Abatement follows the survey", "A specification sets the procedure type, quantities and scope before abatement is bid."),
   ("Type 3 work needs clearance before the enclosure comes down", "Air testing below 0.01 fibres per cc, done by someone independent of the abatement contractor."),
   ("Mid-job find: stop work except to identify the material", "Don't keep cutting or demolishing in that area."),
   ("Mid-job find: notify right away", "The constructor or employer notifies the Ministry, the owner, the contractor and the JHSC."),
   ("Mid-job find: test or presume", "Wait for lab results, [[labDays]] business days ([[rushDays]] on rush), or treat the material as asbestos-containing and follow the matching procedures."),
   ("Mid-job find: get written interim instructions", "A consultant can tell you on site which materials to treat as asbestos-containing so lawful work can continue.")],
  "<p>Contractors who test before they cut avoid all of the second half. See <a href=\"contractors.html\">testing and clearance for contractors</a>.</p>", "obligation-check.html#contractor")

# ---------------------------------------------------------------- about
a = f"""<section class="hero"><div class="wrap">{crumbs((None, "How we work"))}
<div class="hero-copy" style="max-width:860px"><h1>How we work</h1><p class="lede">{e(SITE['online'])} is the online name of {e(SITE['legal'])}, an independent consultancy covering all 11 of Ontario's designated substances across {REGIONS}.</p></div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>Independence</h2><p>We never remove or abate anything and take no referral fees. When an abatement contractor hires us for a clearance air test, our fee doesn't depend on the result, and the result is reported as found. It's written into our terms.</p>
<h2>One named consultant</h2><p>You deal with the same person who walks your building, writes your report and answers your pre-work questions.</p></div>
<div class="prose"><h2>How pricing works</h2><p>Surveys are priced as a report fee by building size plus the samples taken. Your quote gives an estimated number of samples, you pay for the samples actually taken, and we ask on site before going over the estimate. Samples are [[sample]] each ([[sample.demo]] on a demolition survey), including lab analysis of the first layer; extra layers are [[layer]] each. Lab results take [[labDays]] business days; rush takes [[rushDays]] at double the sample price.</p>
<p>The Annual Asbestos Reassessment is a yearly fee per building, paid a year in advance. It keeps your record current; it never includes a designated substance survey.</p>
<h2>Where we work</h2><p>{", ".join(f'<a href="{h}">{t}</a>' for h, t in CITIES)}, and the towns around them.</p></div>
</div></section>""" + cta()
page("about.html", "How We Work | Independent Asbestos Consultant, Windsor ON", "An independent asbestos and designated substances consultancy in Windsor, serving southwestern Ontario. No removal, no referral fees, one named consultant.", a)

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
<option>A designated substance survey for a project</option><option>Testing a few materials before work (Bulk Material Sampling)</option>
<option>Suspect material found mid-job: a call-out</option><option>Annual asbestos reassessment for my building</option>
<option>A suite test before a rental unit is renovated</option><option>Abatement design and oversight</option><option>Clearance air testing</option>
<option>Asbestos instruction and training</option><option>Peer review of a report or specification</option><option>Workplace exposure monitoring (not available yet: notify me at launch)</option><option>Something else</option></select></label>
<label class="field">Site address (optional)<input name="site_address" autocomplete="street-address"></label>
<label class="field">Details<textarea name="message" placeholder="Building age, size, what work is planned and when"></textarea></label>
<label class="check"><input type="checkbox" name="consent_updates" value="yes"> Also send me occasional compliance reminders and updates by email. You can unsubscribe at any time.</label>
<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website_url" tabindex="-1" autocomplete="off"></label></div>
<button class="btn block" type="submit">Send message</button>
<p class="small">We use your details only to reply to this request. See our <a href="privacy.html">privacy notice</a>.</p>
</form></div></div></section>"""
page("contact.html", "Contact | Noah Crowley Consulting, Windsor ON", "Ask for a designated substance survey, asbestos testing, an annual reassessment or clearance air testing in Windsor-Essex and southwestern Ontario.", ct, "contact.html")

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

> {SITE['legal']} is an independent asbestos and designated substances consultancy based in {SITE['city']}, Ontario, serving {REGIONS}. It surveys buildings, tests materials, keeps O. Reg. 278/05 asbestos records through an annual reassessment, writes abatement specifications, oversees abatement, tests the air and does Type 3 clearance. It never removes asbestos and takes no referral fees.

- Clients: commercial and institutional building owners, landlords and condos, general, restoration and abatement contractors.
- Surveys cover all 11 Ontario designated substances and are priced as a report fee by building size plus samples taken. Prices are CAD before HST.
- Lab results take [[labDays]] business days from the lab's receipt. Rush takes [[rushDays]] business days at double the sample price.
- Contact: {SITE['phone']}, {SITE['email']}, {SITE['domain']}/contact.html

## Services (starting prices, CAD before HST)
""" + "".join(f"- {n}: from {money(p)}. {w_}. {t}.\n" for n, p, w_, g, t, pg in PRODUCTS) + f"""
## Key pages
- [Reports and prices]({SITE['domain']}/services.html)
- [Designated substance surveys]({SITE['domain']}/designated-substance-survey.html)
- [Commercial and industrial asbestos surveys]({SITE['domain']}/commercial-asbestos-survey.html)
- [The designated substance list for a tender (OHSA s.30)]({SITE['domain']}/designated-substance-list-tender.html)
- [Asbestos management programs (O. Reg. 278/05)]({SITE['domain']}/asbestos-management-program.html)
- [Ontario's 11 designated substances in buildings]({SITE['domain']}/designated-substances-ontario.html)
- [Lead paint testing]({SITE['domain']}/lead-paint-survey.html)
- [Where asbestos hides in commercial buildings]({SITE['domain']}/asbestos-in-commercial-buildings.html)
- [Annual Asbestos Reassessment]({SITE['domain']}/building-owners.html)
- [Testing and clearance for contractors]({SITE['domain']}/contractors.html)
- [Obligation Check: which duties apply to you]({SITE['domain']}/obligation-check.html)
- [How we work]({SITE['domain']}/about.html)
""" + "".join(f"- [Asbestos testing in {t}]({SITE['domain']}/{h})\n" for h, t in CITIES) + "".join(f"- [{t}]({SITE['domain']}/{h})\n" for h, t, _ in GUIDES)
open(os.path.join(ROOT, "llms.txt"), "w").write(fill(LLMS))
open(os.path.join(ROOT, "CNAME"), "w").write(SITE["domain"].replace("https://", "") + "\n")
open(os.path.join(ROOT, ".nojekyll"), "w").write("")
# ---------------------------------------------------------------- search snippet lengths (warning only)
# Titles over ~65 characters and descriptions over ~160 get cut off in search results. Indexed pages only.
for p_ in PAGES:
    if p_ in HIDDEN or p_ == "404.html": continue
    d_ = open(os.path.join(ROOT, p_)).read()
    t_ = H.unescape(re.search(r"<title>(.*?)</title>", d_).group(1)); m_ = H.unescape(re.search(r'name="description" content="(.*?)"', d_).group(1))
    if len(t_) > 65: print(f"SEO warning: {p_} title is {len(t_)} characters (keep it to 65): {t_}")
    if len(m_) > 160: print(f"SEO warning: {p_} description is {len(m_)} characters (keep it to 160)")
# ---------------------------------------------------------------- price guards (tools/prices.py): stop on any problem
problems = lint_sources(["tools/build.py", "assets/site.js", "assets/ncc-rules.js"]) + check_output(PAGES + ["llms.txt"])
if problems:
    print("PRICE CHECK FAILED: the site was built but must not be published.\n  " + "\n  ".join(problems))
    sys.exit(1)
print(len(PAGES), "pages built;", P["stamp"]["pb"], "from tools/prices.json (Guide rev", str(P["stamp"]["guideRev"]) + "); price guards passed")
