"""Builds the Noah Crowley Asbestos and Designated Substances Consulting website.
Run:  python3 tools/build.py   (from the repo root). Writes the .html files, sitemap.xml and robots.txt.
All copy is drawn from the NCC business plan. Edit SITE below for contact details, then rebuild."""
import json, os, html as H
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
    "founding": True,     # show the 15% founding-client offer
}
REGIONS = "Windsor-Essex, Chatham-Kent, Sarnia-Lambton and London"
YEAR = date.today().year
e = H.escape

# ---------------------------------------------------------------- tiers (from the plan)
TIERS = {
 "bc_ess": dict(program="Building Compliance Program", name="Essentials", price=199, fits="One building up to about 25,000 sq ft", page="building-owners.html",
   inc=["Annual reassessment and updated register of all 11 designated substances", "4 pre-work desk reviews a year, answered within 1 business day", "Occupier and contractor notice templates and an inspector-ready binder", "Fallen-material response within 48 hours", "10% off project work"]),
 "bc_man": dict(program="Building Compliance Program", name="Managed", price=549, fits="Up to 3 buildings or about 100,000 sq ft", page="building-owners.html",
   inc=["Annual reassessment plus a mid-year condition check", "2 pre-work desk reviews a month", "1 live staff awareness session a year", "Fallen-material response within 24 hours, call-out fee waived", "15% off project work"]),
 "bc_fp": dict(program="Building Compliance Program", name="Facility Partner", price=1950, fits="An industrial plant, campus or portfolio", page="building-owners.html",
   inc=["Annual reassessment plus quarterly walk-throughs", "Unlimited pre-work desk reviews", "2 live staff sessions a year", "Same-business-day response, call-out fee waived", "4 oversight or monitoring days a year for shutdowns", "20% off project work"]),
 "rp_s": dict(program="Rental Portfolio Program", name="Small", price=249, fits="Up to 3 buildings or 30 units", page="landlords.html",
   inc=["Annual reassessment, register and tenant notice letters", "2 suite turnover checks a year, written result within 1 week", "Next-business-day leak and flood response", "10% off project work"]),
 "rp_m": dict(program="Rental Portfolio Program", name="Mid", price=749, fits="Up to 150 units", page="landlords.html",
   inc=["Annual reassessment, register and tenant notice letters", "8 suite turnover checks a year", "1 live superintendent and maintenance staff session a year", "Priority leak and flood response, call-out fee waived", "Designated substance line items for your 5-year capital plan", "15% off project work"]),
 "rp_l": dict(program="Rental Portfolio Program", name="Large", price=1990, fits="150 to 500 units, or a condominium corporation", page="landlords.html",
   inc=["Annual reassessment, register and tenant notice letters", "24 suite turnover checks a year", "2 live staff sessions a year", "Priority leak and flood response, call-out fee waived", "Capital-plan input with quarterly walk-throughs", "20% off project work"]),
 "we_shop": dict(program="Workplace Exposure Program", name="Shop", price=299, fits="One workplace, one process with a designated substance", page="employers.html",
   inc=["Annual assessment review with your JHSC and control program update", "1 exposure monitoring day a year", "1 worker and supervisor training session a year", "Results posting, JHSC copies and 5-year monitoring records", "Inspector and JHSC support", "10% off project work"]),
 "we_plant": dict(program="Workplace Exposure Program", name="Plant", price=890, fits="One site, up to 3 substances or 50 exposed workers", page="employers.html",
   inc=["Annual assessment review plus a mid-year walk-through", "3 exposure monitoring days a year", "8 change-of-process reviews a year", "2 training sessions a year", "Medical surveillance coordination with your physician", "15% off project work"]),
 "we_site": dict(program="Workplace Exposure Program", name="Site Partner", price=2190, fits="Several processes or sites", page="employers.html",
   inc=["Annual assessment review plus quarterly reviews", "8 exposure monitoring days a year", "Unlimited change-of-process reviews", "4 training sessions a year", "Attendance at your JHSC quarterly", "20% off project work"]),
 "pw_start": dict(program="Pre-Work Clearance Pass", name="Starter", price=850, fits="Renovators and trades with 1–3 jobs a month in pre-1990 buildings", page="contractors.html",
   inc=["2 pre-work checks a month covering all 11 designated substances", "Site visit within 5 business days, report within 1 week", "Written interim instructions on site when the job can't wait", "A due-diligence file for every job", "Extra checks $475"]),
 "pw_pro": dict(program="Pre-Work Clearance Pass", name="Pro", price=2090, fits="General contractors and fit-out firms with 4 or more jobs a month", page="contractors.html",
   inc=["5 pre-work checks a month", "Site visit within 3 business days, report within 1 week", "Reports branded for your client", "1 live worker awareness session a year", "Extra checks $450"]),
 "pw_rr": dict(program="Pre-Work Clearance Pass", name="Restoration Rapid", price=2290, fits="Fire, flood and mould restoration firms", page="contractors.html",
   inc=["4 emergency checks a month", "Same or next-day visits, 7 days a week", "Adjuster-ready reports with photos and quantities within 1 week", "Written interim instructions on every call", "Extra checks $625"]),
}

def money(n): return "${:,.0f}".format(n)

# ---------------------------------------------------------------- page chrome
NAV = [("building-owners.html", "Building owners"), ("landlords.html", "Landlords"), ("employers.html", "Employers"),
       ("contractors.html", "Contractors"), ("services.html", "Services"), ("contact.html", "Contact")]
CITIES = [("asbestos-testing-windsor.html", "Windsor"), ("asbestos-testing-leamington.html", "Leamington"), ("asbestos-testing-chatham.html", "Chatham"),
          ("asbestos-testing-sarnia.html", "Sarnia"), ("asbestos-testing-london.html", "London")]
TRIGGERS = [("asbestos-testing-before-renovation.html", "Asbestos testing before renovation"),
            ("designated-substance-survey-demolition-permit.html", "Designated substance survey for a demolition permit"),
            ("silica-exposure-assessment.html", "Silica exposure assessment"),
            ("isocyanate-air-monitoring.html", "Isocyanate air monitoring")]
GUIDES = [("guide-inspector-ready-binder.html", "Inspector-ready binder checklist", "For building owners"),
          ("guide-suite-turnover-checklist.html", "Suite turnover checklist", "For landlords and property managers"),
          ("guide-designated-substance-self-check.html", "Designated substance self-check", "For employers"),
          ("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "For contractors")]
PAGES = []

def contact_bits():
    out = []
    if SITE["phone"]: out.append(f'<a href="tel:{e(SITE["phone"].replace("-", ""))}">{e(SITE["phone"])}</a>')
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
<meta name="theme-color" content="#14233A">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="icon" href="favicon-32.png" sizes="32x32" type="image/png">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+Condensed:wght@600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
<link rel="stylesheet" href="assets/site.css">
{ld}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>"""

def header(active):
    links = "".join(f'<a href="{h}"{" aria-current=\"page\"" if h == active else ""}>{t}</a>' for h, t in NAV)
    return f"""<header class="site-head"><div class="wrap head-row">
<a class="brand" href="index.html" aria-label="{e(SITE['online'])}, home"><img src="assets/ncc-logo-online-compact.svg" alt="{e(SITE['online'])}" width="420" height="96"></a>
<button class="menu-btn" type="button" aria-expanded="false" aria-controls="site-nav">Menu</button>
<nav class="nav" id="site-nav" aria-label="Main">{links}<a class="btn amber" href="obligation-check.html">Take the Obligation Check</a></nav>
</div></header>
<main id="main">"""

def footer():
    cb = contact_bits()
    contact = ("<li>" + "</li><li>".join(cb) + "</li>") if cb else '<li><a href="contact.html">Send us a message</a></li>'
    return f"""</main>
<footer class="site-foot"><div class="wrap">
<div class="foot-grid">
<div class="foot-brand"><img src="assets/ncc-logo-online-compact-reverse.svg" alt="{e(SITE['online'])}" width="420" height="96">
<p>Independent asbestos and designated substances consulting for {REGIONS}. We never remove or abate anything and take no referral fees.</p></div>
<div><h4>Programs</h4><ul>
<li><a href="building-owners.html">Building Compliance</a></li><li><a href="landlords.html">Rental Portfolio</a></li>
<li><a href="employers.html">Workplace Exposure</a></li><li><a href="contractors.html">Pre-Work Clearance Pass</a></li>
<li><a href="services.html">One-off services</a></li><li><a href="obligation-check.html">Obligation Check</a></li></ul></div>
<div><h4>Where we work</h4><ul>{"".join(f'<li><a href="{h}">Asbestos testing in {t}</a></li>' for h, t in CITIES)}</ul></div>
<div><h4>Guides and contact</h4><ul>{"".join(f'<li><a href="{h}">{t}</a></li>' for h, t, _ in GUIDES)}{contact}<li><a href="about.html">How we work</a></li></ul></div>
</div>
<div class="foot-legal"><span>© {YEAR} {e(SITE['legal'])}, operating as {e(SITE['online'])}. Prices in CAD before HST.</span><a href="privacy.html">Privacy notice</a></div>
</div></footer>
<script src="assets/config.js"></script>
<script src="assets/site.js"></script>
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
    doc = head(title, desc, fname, schemas or None) + header(active) + body + footer().replace("<script src=\"assets/config.js\">", extra_js + "<script src=\"assets/config.js\">")
    open(os.path.join(ROOT, fname), "w").write(doc)

def cta(title="Find out what applies to you in two minutes.", text="Answer a few questions and the Obligation Check tells you which duties you carry, which program fits and what the first step costs.", href="obligation-check.html"):
    return f"""<section class="cta-band"><div class="wrap"><div><h2>{title}</h2><p>{text}</p></div>
<div class="btn-row"><a class="btn" href="{href}">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></section>"""

def crumbs(*items):
    parts = ['<a href="index.html">Home</a>'] + [f'<a href="{h}">{t}</a>' if h else e(t) for h, t in items]
    return '<nav class="crumbs" aria-label="Breadcrumb">' + " / ".join(parts) + "</nav>"

def faq(items):
    html = '<section class="section white"><div class="wrap"><div class="section-head"><h2>Questions people ask</h2></div><div class="faq">' + "".join(
        f'<details><summary>{q}</summary><p>{a}</p></details>' for q, a in items) + "</div></div></section>"
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
    th = "".join(f'<th scope="col"><span class="tname">{TIERS[k]["name"]}</span><span class="tprice">{money(TIERS[k]["price"])} <small>a month</small></span></th>' for k in keys)
    body = ""
    for label, vals in rows:
        tds = ""
        for v in vals:
            cls = ' class="yes"' if v == "Yes" else (' class="no"' if v.startswith("Not included") or v == "No" else "")
            tds += f"<td{cls}>{v}</td>"
        body += f'<tr><th scope="row">{label}</th>{tds}</tr>'
    return f'<div class="table-wrap"><table class="data tiers wide"><thead><tr><th scope="col"><span class="small">Monthly, CAD before HST</span></th>{th}</tr></thead><tbody>{body}</tbody></table></div>'

def value_table(rows, total, program, saving=""):
    body = "".join(f'<tr><th scope="row">{a}</th><td class="num">{money(b)}</td></tr>' for a, b in rows)
    return f"""<div class="table-wrap"><table class="data"><thead><tr><th scope="col">Bought one at a time</th><th class="num" scope="col">List price</th></tr></thead>
<tbody>{body}</tbody><tfoot><tr><th scope="row">The same year à la carte</th><td class="num">{money(total)}</td></tr>
<tr><th scope="row">The same year in the program</th><td class="num">{money(program)}</td></tr></tfoot></table></div>{f'<p class="small" style="margin-top:10px">{saving}</p>' if saving else ''}"""

COMMON_RULES = ul([
    "12-month agreement that renews automatically, with a live online register for every building or workplace that you can show an inspector or a contractor on a phone.",
    "Lab analysis is included in every price. Results come back within 1 week of the site visit, and if work can't wait we leave written interim instructions on site the same day.",
    "Included checks and reviews roll over within the contract year. Extra work is billed at your member rate.",
    "No baseline assessment yet? We do it first, or spread its cost over your first 12 months.",
    "We never remove or abate anything and take no referral fees, so no result is shaped by someone with a stake in the job."])
FOUNDING = ('<p class="flag ok" style="max-width:760px">Founding clients: the first five clients in each program get 15% off their monthly fee in exchange for a short case study.</p>'
            if SITE["founding"] else "")

def start_steps(entry, entry_text):
    return f"""<div class="steps">
<div class="step"><h3>{entry}</h3><p>{entry_text}</p></div>
<div class="step"><h3>Baseline and register</h3><p>We assess the building or workplace once, room by room, and set up the live register you'll keep using.</p></div>
<div class="step"><h3>Monthly coverage</h3><p>Reassessments, checks and reviews happen on schedule, with guaranteed response when something goes wrong.</p></div></div>"""

def segment_hero(crumb, h1, lede, seg):
    return f"""<section class="hero"><div class="wrap">{crumbs((None, crumb))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html#{seg}">Check what applies to you</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>"""

# ---------------------------------------------------------------- home
REGISTER = """<figure class="register" aria-label="Example of a live designated substance register">
<div class="reg-head"><b>Designated substance register</b><span>Example</span></div>
<div class="reg-meta"><span><strong>Last reassessed</strong> Sep 14, 2026</span><span><strong>Next due</strong> Sep 2027</span><span><strong>Pre-work reviews left</strong> 3</span></div>
<table class="reg-table"><thead><tr><th>Location</th><th>Material</th><th>Status</th></tr></thead><tbody>
<tr><td class="loc">Boiler room</td><td class="mat">Pipe elbow insulation</td><td><span class="status act">Act now</span></td></tr>
<tr><td class="loc">Corridor, 2nd floor</td><td class="mat">9-inch floor tile and mastic</td><td><span class="status monitor">Monitor</span></td></tr>
<tr><td class="loc">Stairwell B</td><td class="mat">Textured ceiling finish</td><td><span class="status monitor">Monitor</span></td></tr>
<tr><td class="loc">Suite 204</td><td class="mat">Drywall joint compound</td><td><span class="status good">Good</span></td></tr>
<tr><td class="loc">Front entrance</td><td class="mat">Window glazing (lead)</td><td><span class="status good">Good</span></td></tr>
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
<h1>Asbestos and designated substance compliance, kept current every month.</h1>
<p class="lede">Independent surveys, registers and air monitoring for building owners, landlords, employers and contractors. One predictable fee instead of a scramble before every inspection or renovation.</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="#doors">Find your program</a></div>
<p class="area">Serving {REGIONS}.</p>
</div>
{REGISTER}
</div></section>

<section class="section tight" id="doors"><div class="wrap">
<div class="section-head"><h2>Start with what you're responsible for</h2></div>
<div class="doors">
<a class="door" href="building-owners.html"><h3>I own or manage a building</h3><p>Keep your asbestos record current, answer contractors before they drill, and stay ready for an inspector.</p><span class="go">Building Compliance, from $199 a month</span></a>
<a class="door" href="landlords.html"><h3>I rent out units</h3><p>Check suites before turnover crews lift tile or sand ceilings, and keep tenant notices up to date.</p><span class="go">Rental Portfolio, from $249 a month</span></a>
<a class="door" href="employers.html"><h3>My workers handle a designated substance</h3><p>Exposure assessments, control programs and air monitoring under O. Reg. 490/09.</p><span class="go">Workplace Exposure, from $299 a month</span></a>
<a class="door" href="contractors.html"><h3>I'm about to open walls or floors</h3><p>Pre-work checks booked before you mobilize, so a find never idles your crew for a week.</p><span class="go">Clearance Pass, from $850 a month</span></a>
</div></div></section>

<section class="section white"><div class="wrap">
<div class="section-head"><h2>How it works</h2><p class="lede">The first step is free and takes two minutes.</p></div>
<div class="steps">
<div class="step"><h3>Take the Obligation Check</h3><p>A two-minute quiz that tells you which legal duties apply to your building, workplace or job, and which program fits.</p></div>
<div class="step"><h3>Start with one paid visit</h3><p>A gap audit, a first suite check or a first pre-work check. If you subscribe, the fee is credited to your program.</p></div>
<div class="step"><h3>Stay covered</h3><p>Reassessments, reviews and response times are booked in advance, at a monthly price you can budget for.</p></div>
</div></div></section>

<section class="section navy"><div class="wrap split">
<div class="section-head" style="margin:0"><h2>Inspectors are checking for exactly these gaps</h2>
<p class="lede">The Ministry of Labour's recent campaigns focused on small and mid-sized owners and employers. The most common orders were for not following the asbestos management program and not keeping an asbestos record on site.</p>
<div class="btn-row" style="margin-top:8px"><a class="btn amber" href="guide-inspector-ready-binder.html">Get the inspector-ready checklist</a></div></div>
<div class="facts">
<div class="fact"><b>31</b><span>orders and requirements from visits to 78 workplaces in the 2023–24 asbestos-in-buildings campaign.</span></div>
<div class="fact"><b>77%</b><span>of the workplaces visited in that campaign had fewer than 50 workers.</span></div>
<div class="fact"><b>144</b><span>orders and requirements at 131 workplaces in the 2024–25 campaign on worker exposure to chemical agents.</span></div>
<div class="fact"><b>$2M</b><span>maximum fine for a corporation under Ontario's Occupational Health and Safety Act.</span></div>
</div></div></section>

<section class="section" id="programs"><div class="wrap">
<div class="section-head"><h2>Four programs, priced by the month</h2><p class="lede">Each program costs about what the same year of compliance costs bought one job at a time, spread monthly, with guaranteed response and no gaps for an inspector to find.</p></div>
<div class="programs">
<a class="program" href="building-owners.html"><h3>Building Compliance Program</h3><span class="price">from $199/mo</span><p>Annual reassessment, a live register of every designated substance, pre-work desk reviews and priority response for commercial, industrial and institutional buildings.</p></a>
<a class="program" href="landlords.html"><h3>Rental Portfolio Program</h3><span class="price">from $249/mo</span><p>The same compliance core plus suite turnover checks, so units can be renovated between tenants without surprises.</p></a>
<a class="program" href="employers.html"><h3>Workplace Exposure Program</h3><span class="price">from $299/mo</span><p>Annual assessment review with your JHSC, control program upkeep, exposure monitoring days and training.</p></a>
<a class="program" href="contractors.html"><h3>Pre-Work Clearance Pass</h3><span class="price">from $850/mo</span><p>A monthly bank of pre-work checks with reserved booking, billed to your client or kept as due diligence.</p></a>
</div>
<p class="small" style="margin-top:18px">Need a single survey, an abatement specification or a Type 3 clearance? <a href="services.html">See one-off services and list prices.</a></p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>Independent, on purpose</h2>
<p>We never remove or abate anything, we take no referral fees, and we don't sell the Clearance Pass to abatement contractors. When we tell you a material is fine to leave in place, nobody on our side gains from the opposite answer.</p>
<p>You deal with one named consultant who knows your buildings, backed by a qualified occupational hygienist for workplace monitoring.</p>
<p><a href="about.html">How we work</a></p></div>
<div class="prose"><h2>All 11 designated substances</h2>
<p>Asbestos, lead, mercury and silica turn up in buildings. Isocyanates, benzene, vinyl chloride, acrylonitrile, arsenic, ethylene oxide and coke oven emissions mainly drive workplace duties. A pre-project list has to cover all of them, so every register we build does.</p>
<p><a href="services.html">See every service</a></p></div>
</div></section>
""" + cta()
HOME_FAQ, HOME_FAQ_SCHEMA = faq([
 ("What are Ontario's designated substances?", "There are 11: acrylonitrile, arsenic, asbestos, benzene, coke oven emissions, ethylene oxide, isocyanates, lead, mercury, silica and vinyl chloride. Asbestos, lead, mercury and silica are the ones usually found in buildings."),
 ("How often does a building owner have to update the asbestos record?", "At least once every 12 months, and whenever new information comes to light, under O. Reg. 278/05. The record has to be kept on the premises."),
 ("Who is responsible for the designated substance list before a renovation?", "The project owner. Under section 30 of the Occupational Health and Safety Act, the owner lists every designated substance in the work area before the project begins and includes the list in the tender."),
 ("How much do your programs cost?", "Building Compliance starts at $199 a month, Rental Portfolio at $249, Workplace Exposure at $299 and the Pre-Work Clearance Pass at $850, all in CAD before HST. One-off surveys start at $550 for a single suite."),
 ("Do you remove asbestos?", "No. We are independent consultants: we survey, write specifications, oversee abatement and test the air, but we never remove or abate anything and take no referral fees.")])
home = home.replace('<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', HOME_FAQ.replace('class="section white"', 'class="section"') + '<section class="section white"><div class="wrap split">\n<div class="prose"><h2>Independent, on purpose</h2>', 1)
page("index.html", "Asbestos & Designated Substance Consulting in Windsor, ON | Noah Crowley", f"Independent asbestos and designated substance surveys, registers and air monitoring in {REGIONS}. Monthly compliance programs from $199.", home, schema=[home_schema, HOME_FAQ_SCHEMA])

# ---------------------------------------------------------------- building owners
b = segment_hero("Building owners", "Building Compliance Program",
    "For owners and facility managers of commercial, industrial and institutional buildings, churches, private schools and small municipalities. Your 12-month asbestos update, your paper trail and your “can we drill here?” answers, handled for one monthly fee.", "building") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What the law asks of building owners</h3>{ul([
 "Keep an asbestos record on the premises: where each material is, its condition, and whether it is friable (O. Reg. 278/05).",
 "Re-inspect listed materials and update the record at least once every 12 months, and whenever you learn something new.",
 "Give occupiers written notice of asbestos in the areas they occupy, and tell contractors before work that may disturb it.",
 "Train workers who work on or near listed materials.",
 "Before any renovation, repair or demolition, list every designated substance in the work area and include it in the tender (OHSA s.30)."])}</div>
<div class="prose"><h2>What's at stake</h2>
<p>An owner who leaves a substance off the project list is liable to the constructor and every contractor for their losses when it turns up mid-job. The maximum OHSA fine is $2 million for a corporation and $1.5 million for a director or officer.</p>
<p>In Ontario's 2023–24 inspection campaign, the most common orders were for not following the asbestos management program and not keeping the record on site. Most of the workplaces visited had fewer than 50 workers.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Compare the tiers</h2>{FOUNDING}</div>
{tier_table(["bc_ess", "bc_man", "bc_fp"], [
 ("Fits", ["1 building up to about 25,000 sq ft", "Up to 3 buildings or about 100,000 sq ft", "Industrial plant, campus or portfolio"]),
 ("Annual reassessment and updated register", ["Yes", "Yes", "Yes, plus quarterly walk-throughs"]),
 ("Mid-year condition check", ["No", "Yes", "Quarterly"]),
 ("Pre-work desk reviews, answered within 1 business day", ["4 a year", "2 a month", "Unlimited"]),
 ("Occupier and contractor notice templates, inspector-ready binder", ["Yes", "Yes", "Yes"]),
 ("Staff awareness training", ["Not included; $675 member rate", "1 live session a year", "2 live sessions a year"]),
 ("Fallen-material response", ["Within 48 hours", "Within 24 hours, call-out fee waived", "Same business day, call-out fee waived"]),
 ("Oversight or monitoring days included", ["None", "None", "4 a year, for shutdowns"]),
 ("Discount on project work", ["10%", "15%", "20%"])])}
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>What Essentials replaces</h2><p>Bought one job at a time, a year of the same coverage costs about the same as the program. What changes is that it's budgeted, booked in advance and never missed.</p>
{value_table([("Annual reassessment, building up to 25,000 sq ft", 1190), ("4 pre-work desk reviews", 600), ("Occupier notices and inspector binder", 300), ("Support for a Ministry visit or order", 300)], 2390, 2388)}</div>
<div class="prose"><h2>How it starts</h2>{start_steps("Compliance gap audit", "A short paid review of your building against what an inspector checks. The fee is credited if you join.")}
<h3>Included in every program</h3>{COMMON_RULES}</div>
</div></section>
""" + cta("Is your asbestos record within 12 months?", "The Obligation Check takes two minutes and tells you which tier fits your buildings.", "obligation-check.html#building")
page("building-owners.html", "Building Compliance Program | Asbestos records and registers | Noah Crowley", "Annual asbestos reassessment, a live register of all 11 designated substances and pre-work desk reviews for building owners in southwestern Ontario. From $199 a month.", b, "building-owners.html", schema=service_schema("Building Compliance Program", "Monthly asbestos and designated substance compliance program in southwestern Ontario", 199))

# ---------------------------------------------------------------- landlords
r = segment_hero("Landlords", "Rental Portfolio Program",
    "For landlords, property managers and condominium corporations with pre-1990 buildings. A suite turns over, the crew lifts 9-inch floor tile or sands a stippled ceiling, and you now have exposed workers, a contaminated unit and an unhappy tenant. This program checks first.", "rental") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What the law asks of rental owners</h3>{ul([
 "Keep an asbestos record, update it at least every 12 months, and give tenants written notice of asbestos in the areas they occupy.",
 "Tell superintendents, maintenance staff and contractors what's there before work that may disturb it.",
 "List every designated substance in the work area before a renovation or repair project begins.",
 "Older suites also hide lead paint and mercury thermostats; the same check picks them up."])}</div>
<div class="prose"><h2>Why now</h2>
<p>Windsor's vacancy rate rose to 3.7% in 2025 and the rental stock grew 3.6%. Landlords are refreshing suites to compete, which means more flooring, drywall and ceiling work in older buildings.</p>
<p>A suite turnover check is a site visit and a written answer within 1 week on what the planned work will disturb, so the crew starts on known ground.</p>
<p><a href="guide-suite-turnover-checklist.html">Get the suite turnover checklist</a></p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Compare the tiers</h2>{FOUNDING}</div>
{tier_table(["rp_s", "rp_m", "rp_l"], [
 ("Fits", ["Up to 3 buildings or 30 units", "Up to 150 units", "150 to 500 units"]),
 ("Annual reassessment, register, tenant notice letters", ["Yes", "Yes", "Yes"]),
 ("Suite turnover checks, written result within 1 week", ["2 a year", "8 a year", "24 a year"]),
 ("Superintendent and maintenance staff training", ["Not included; $675 member rate", "1 live session a year", "2 live sessions a year"]),
 ("Leak and flood response", ["Next business day", "Priority, call-out fee waived", "Priority, call-out fee waived"]),
 ("Capital-plan input: designated substance line items for 5 years", ["No", "Yes", "Yes, with quarterly walk-throughs"]),
 ("Discount on project work", ["10%", "15%", "20%"])])}
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>What Mid replaces</h2>
{value_table([("Annual reassessment, up to 150 units", 1780), ("8 suite turnover checks at $660", 5280), ("1 live training session", 750), ("Tenant notice letters", 300), ("Capital-plan input", 300), ("2 leak or flood call-outs at $555", 1110)], 9520, 8988, "Mid saves 6% on the same year. Large saves 11% on a $26,860 à la carte year.")}</div>
<div class="prose"><h2>How it starts</h2>{start_steps("First suite check", "One check on your next unit turnover, so you see the process start to finish. The fee is credited if you join.")}
<h3>Included in every program</h3>{COMMON_RULES}</div>
</div></section>
""" + cta("Got a suite turning over soon?", "Book the first suite check, or take the Obligation Check to see which tier fits your portfolio.", "obligation-check.html#rental")
page("landlords.html", "Rental Portfolio Program | Suite turnover asbestos checks | Noah Crowley", "Suite turnover checks, asbestos records and tenant notices for landlords, property managers and condo corporations in Windsor-Essex and southwestern Ontario. From $249 a month.", r, "landlords.html", schema=service_schema("Rental Portfolio Program", "Monthly asbestos and designated substance compliance program in southwestern Ontario", 249))

# ---------------------------------------------------------------- employers
w = segment_hero("Employers", "Workplace Exposure Program",
    "For employers whose workers use, handle or store a designated substance: collision and auto body shops, countertop fabricators, foundries, concrete products, metal recyclers, plastics and resin plants, labs and hospital sterilization.", "employer") + f"""
<section class="section white"><div class="wrap split">
<div class="duty"><h3>What O. Reg. 490/09 asks of employers</h3>{ul([
 "A written exposure assessment, made with your joint health and safety committee, with a copy to each member. Redo it after any change that could significantly affect exposure.",
 "Where workers' health may be affected, a written control program: engineering controls, work and hygiene practices, monitoring, records and training.",
 "Keep exposure under the occupational exposure limit.",
 "Air monitoring by or under a qualified industrial hygienist, with results posted for 14 days, shared with the JHSC and kept for 5 years.",
 "Medical surveillance for asbestos, benzene, coke oven emissions, isocyanates, lead, mercury and silica.",
 "Protect other employers' workers at your site."])}<p class="small">The regulation doesn't apply on construction projects, where Regulation 833 and the building duties govern.</p></div>
<div class="prose"><h2>Who does the monitoring</h2>
<p>Exposure monitoring is done by or under our qualified occupational hygienist. Medical surveillance is done by your physician; we coordinate schedules and exposure records.</p>
<h2>What inspectors found</h2>
<p>The Ministry's 2024–25 campaign on chemical exposure visited 131 workplaces and issued 144 orders and requirements. Inspectors required air monitoring where exposure data was missing and found respiratory protection programs the most common gap.</p>
<p><a href="guide-designated-substance-self-check.html">Take the one-page self-check</a></p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Compare the tiers</h2>{FOUNDING}</div>
{tier_table(["we_shop", "we_plant", "we_site"], [
 ("Fits", ["One workplace, one process (a paint booth, a cutting line)", "One site, up to 3 substances or 50 exposed workers", "Several processes or sites"]),
 ("Annual assessment review with the JHSC and control program update", ["Yes", "Yes, plus a mid-year walk-through", "Yes, plus quarterly reviews"]),
 ("Exposure monitoring days", ["1 a year", "3 a year", "8 a year"]),
 ("Change-of-process reviews", ["As needed, at member rate", "8 a year", "Unlimited"]),
 ("Worker and supervisor training", ["1 session a year", "2 sessions a year", "4 sessions a year"]),
 ("Results posting, JHSC copies, 5-year monitoring records", ["Yes", "Yes", "Yes"]),
 ("Medical surveillance coordination with your physician", ["Records only", "Yes", "Yes"]),
 ("Inspector and JHSC support", ["Yes", "Yes", "Yes, attends JHSC quarterly"]),
 ("Discount on project work", ["10%", "15%", "20%"])])}
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>What Shop replaces</h2>
{value_table([("Assessment review and control program update", 900), ("1 exposure monitoring day", 1400), ("1 training session", 750), ("Records and inspector support", 600)], 3650, 3588, "Plant and Site Partner save 4% and 6% on their à la carte years of $11,100 and $28,000.")}
<p class="small">New clients start with a baseline assessment and written control program, bought once or spread over the first year.</p></div>
<div class="prose"><h2>How it starts</h2>{start_steps("Exposure gap audit", "A short paid review of your assessment, control program and monitoring records. The fee is credited if you join.")}
<h3>Included in every program</h3>{COMMON_RULES}</div>
</div></section>
""" + cta("Do you have a written exposure assessment?", "The Obligation Check tells you in two minutes whether O. Reg. 490/09 applies and which tier fits.", "obligation-check.html#employer")
page("employers.html", "Workplace Exposure Program | O. Reg. 490/09 assessments and air monitoring | Noah Crowley", "Designated substance exposure assessments, control programs and air monitoring under O. Reg. 490/09 for employers in southwestern Ontario. From $299 a month.", w, "employers.html", schema=service_schema("Workplace Exposure Program", "Monthly asbestos and designated substance compliance program in southwestern Ontario", 299))

# ---------------------------------------------------------------- contractors
c = segment_hero("Contractors", "Pre-Work Clearance Pass",
    "Buy pre-work checks wholesale, with reserved booking. Every job in an older building starts with a designated substance list you can bill to the client and keep as your due diligence.", "contractor") + f"""
<section class="section white"><div class="wrap split">
<div class="prose"><h2>The problem it solves</h2>
<p>On small jobs the owner rarely has a list. The law puts that duty on the owner, but you're the one standing in the room when a suspect material turns up.</p>
<p>When unlisted material is found, work has to stop except to identify it, and the Ministry, the owner, the contractor and the JHSC must be notified right away. With lab results taking a week, a find on day one idles your crew for a week or pushes the job into asbestos procedures by presumption.</p>
<p>The owner who failed to list is liable for your losses, but few renovators sue the client who's paying them.</p></div>
<div class="duty"><h3>What you get</h3>{ul([
 "A monthly bank of pre-work checks: a site visit to the work area (one suite or up to 2,000 sq ft) covering all 11 designated substances.",
 "Reserved booking: book when the client accepts your quote and results arrive before you mobilize.",
 "Written interim instructions on site if the client can't wait, so work can proceed lawfully.",
 "A due-diligence file per job: report, photos and instructions.",
 "A standard quote line, a one-page client explainer and a member badge for your website and trucks.",
 "Unused checks roll over within the 12-month term."])}
<p class="small">“Clearance” here means cleared to start work. Type 3 clearance air testing is a separate service retained by the building owner.</p></div>
</div></section>

<section class="section"><div class="wrap">
<div class="section-head"><h2>Compare the passes</h2>{FOUNDING}</div>
{tier_table(["pw_start", "pw_pro", "pw_rr"], [
 ("Fits", ["Renovators and trades, 1–3 jobs a month in pre-1990 buildings", "General contractors, fit-out and multi-trade firms, 4 or more jobs a month", "Fire, flood and mould restoration firms"]),
 ("Checks included", ["2 a month", "5 a month", "4 emergency checks a month"]),
 ("Cost per included check", ["$425", "$418", "$573"]),
 ("Site visit", ["Within 5 business days", "Within 3 business days", "Same or next day, 7 days a week"]),
 ("Report", ["Within 1 week of the visit", "Within 1 week of the visit", "Within 1 week, adjuster-ready with photos and quantities"]),
 ("Interim instructions on site", ["When needed", "When needed", "Every call"]),
 ("Reports branded for your client", ["No", "Yes", "Yes"]),
 ("Worker awareness", ["Toolbox talk templates", "1 live session a year", "1 live session a year"]),
 ("Extra checks", ["$475", "$450", "$625"])])}
<p class="small" style="margin-top:12px">The independent list price of a check is $550; an emergency check is $700. Members pay less because their visits are grouped into route days.</p>
</div></section>

<section class="section white"><div class="wrap split">
<div class="prose"><h2>The business case for Starter</h2>
<div class="table-wrap"><table class="data wide"><thead><tr><th scope="col">Two jobs a month</th><th scope="col">Without the Pass</th><th scope="col">With Starter</th></tr></thead><tbody>
<tr><th scope="row">Cost per check</th><td>$550, booked job by job</td><td>$425</td></tr>
<tr><th scope="row">Booking</th><td>Next available slot</td><td>Visit within 5 business days, reserved</td></tr>
<tr><th scope="row">How it's paid</th><td>Rarely quoted, so absorbed or skipped</td><td>Billed to the client as a $550 line item</td></tr>
<tr><th scope="row">Monthly result</th><td>$1,100 absorbed if tested, or the risk carried if skipped</td><td>$1,100 billed against $850 paid: $250 a month ahead</td></tr>
<tr><th scope="row">Suspect material</th><td>Found mid-job: stop work, notify, wait a week</td><td>Found before mobilizing and priced into the quote</td></tr>
</tbody></table></div>
<p class="small">Prefer not to bill the line? Absorb it and market “checked before we cut” to clients and insurers instead.</p></div>
<div class="prose"><h2>How it starts</h2>{start_steps("First pre-work check", "One check on your next job in an older building. The fee is credited if you take the Pass.")}
<h3>Independence</h3><p>Each report is addressed to the building owner, because it's the owner's list. We do no removal, pay no referral fees, and don't sell the Pass to abatement contractors.</p>
<p><a href="guide-demolition-renovation-dss.html">Read the demolition and renovation DSS guide</a></p></div>
</div></section>
""" + cta("Never stop a job for a week again.", "Book your first pre-work check, or take the Obligation Check to see which pass fits your volume.", "obligation-check.html#contractor")
page("contractors.html", "Pre-Work Clearance Pass | Pre-renovation asbestos checks for contractors | Noah Crowley", "Monthly pre-work designated substance checks with reserved booking for contractors, renovators and restoration firms in southwestern Ontario. From $850 a month.", c, "contractors.html", schema=service_schema("Pre-Work Clearance Pass", "Monthly asbestos and designated substance compliance program in southwestern Ontario", 850))

# ---------------------------------------------------------------- services
def svc_table(rows):
    body = "".join(f'<tr><th scope="row">{a}</th><td>{t}</td><td>{d}</td><td class="num">{p}</td></tr>' for a, t, d, p in rows)
    return f'<div class="table-wrap"><table class="data wide"><thead><tr><th scope="col">Service</th><th scope="col">Typical trigger</th><th scope="col">What you get</th><th scope="col" class="num">List price</th></tr></thead><tbody>{body}</tbody></table></div>'
s = f"""<section class="hero"><div class="wrap">{crumbs((None, "Services"))}
<div class="hero-copy" style="max-width:860px"><h1>One-off services and list prices</h1>
<p class="lede">Every price includes the lab analysis the service needs, so testing never appears as a separate line on a quote. Results come back within 1 week. Program members pay 10% to 20% less.</p></div></div></section>
<section class="section white"><div class="wrap">
<div class="section-head"><h2>Buildings and projects</h2></div>
{svc_table([
 ("Baseline designated substance assessment", "No record exists, building purchase, first subscription", "Room-by-room register of all 11 substances plus PCBs, mould and ozone-depleting refrigerants, condition ratings, priority actions, floor-plan markup", "$1,900–$6,500 by size"),
 ("Annual reassessment", "The 12-month update duty", "Condition re-check of every listed material, updated register, change log, action list", "$1,190 up to 25,000 sq ft; $1,780 for a rental up to 150 units"),
 ("Project designated substance survey (DSS)", "Renovation, repair, demolition, tender, demolition permit", "Report on all 11 substances in the work area, ready to attach to tenders", "$550 one suite or up to 2,000 sq ft; $1,300–$4,800 commercial"),
 ("Pre-work desk review", "Staff or a contractor is about to drill, cut or lift", "Written answer from your register within 1 business day", "$150"),
 ("Suite turnover check", "A rental unit is about to be renovated", "Site visit and a written result within 1 week", "$660"),
 ("Management program", "You have a register but no written program", "Roles, work authorization, notices, training and response", "$1,500–$4,000"),
 ("Abatement and remediation specifications", "Asbestos, lead or mercury devices must be removed, repaired or enclosed", "Scope of work, procedure type, quantities, bid review", "$1,500–$5,000"),
 ("Abatement oversight and air monitoring", "Type 2 or Type 3 asbestos work, lead removal", "Daily inspections, background and perimeter air testing, daily reports", "$1,100 a day"),
 ("Type 3 clearance", "Before a Type 3 enclosure comes down", "Visual inspection, aggressive clearance air testing, clearance letter", "$625–$900 a visit"),
 ("Fallen or damaged material call-out", "Water leak, ceiling collapse, damaged pipe lagging", "Site visit, written isolation instructions on the spot, confirmed result within 1 week", "$555"),
 ("Awareness training", "Workers on or near listed materials", "Live session for up to 15 staff, attendance records for the inspector", "$750; $675 member rate")])}
</div></section>
<section class="section"><div class="wrap">
<div class="section-head"><h2>Workplaces (O. Reg. 490/09)</h2></div>
{svc_table([
 ("Designated substance assessment", "Substance used, handled or stored; new process; Ministry order", "Written assessment prepared with your JHSC, stating whether exposure is likely and whether health may be affected", "$2,500–$7,500"),
 ("Control program", "Assessment shows health may be affected", "Controls, work and hygiene practices, monitoring plan, records, training and medical surveillance links", "$2,000–$5,000"),
 ("Exposure monitoring day", "Program schedule, complaint, process change", "A full day of personal and area air monitoring, results report, posting notice, JHSC copy", "$1,400 a day"),
 ("Respiratory protection program", "Respirators in use", "Written program, selection guidance, training records", "$1,200–$2,500")])}
<p class="small" style="margin-top:12px">Prices in CAD before HST. Ranges depend on building size or the number of processes; we confirm a fixed price before any work starts.</p>
</div></section>
<section class="section white"><div class="wrap"><div class="section-head"><h2>Common jobs</h2></div>
<div class="link-list">{"".join(f'<a href="{h}"><strong>{t}</strong><span>What it involves, what it costs and how fast you get results</span></a>' for h, t in TRIGGERS)}</div></div></section>""" + cta("Not sure which service you need?", "The Obligation Check points you to the right one, or send us the job details and we'll quote it.")
page("services.html", "Asbestos and designated substance services and prices | Noah Crowley", "List prices for designated substance surveys, asbestos reassessments, abatement specifications and oversight, Type 3 clearance and exposure monitoring in southwestern Ontario.", s, "services.html")

# ---------------------------------------------------------------- quiz
q = f"""<section class="hero"><div class="wrap">{crumbs((None, "Obligation Check"))}
<div class="split" style="align-items:start">
<div class="hero-copy"><h1>The Obligation Check</h1><p class="lede">Answer up to five questions. You'll see which legal duties apply to you, which program fits, and what the first step is. Nothing is sent until you choose to send it.</p>
<p class="small">Covers O. Reg. 278/05 (asbestos in buildings), OHSA section 30 (designated substances on projects) and O. Reg. 490/09 (designated substances at work).</p></div>
<div class="quiz" id="quiz" aria-live="polite"><noscript>The Obligation Check needs JavaScript. You can <a href="contact.html">send us a message</a> instead.</noscript></div>
</div></div></section>"""
page("obligation-check.html", "Obligation Check | Which asbestos and designated substance duties apply to you? | Noah Crowley",
     "A two-minute quiz for building owners, landlords, employers and contractors in Ontario: find out which asbestos and designated substance duties apply and which program fits.", q, None,
     extra_js=f"<script>window.NCC_TIERS={json.dumps({k: {kk: v[kk] for kk in ['program', 'name', 'price', 'fits', 'page', 'inc']} for k, v in TIERS.items()})};</script>\n")

# ---------------------------------------------------------------- local pages
def local_page(fname, city, region, intro, local_points, towns, extra_faq=()):
    items = [(f"How much does asbestos testing cost in {city}?", f"A project designated substance survey is $550 for one suite or up to 2,000 sq ft, and $1,300 to $4,800 for commercial work areas. Lab analysis is included, so there's no separate testing charge."),
             ("How long do results take?", "Lab results come back within 1 week of the site visit. If work can't wait, we leave written interim instructions on site the same day."),
             (f"Which buildings in {city} are likely to contain asbestos?", "Most buildings built after 1980 are largely free of asbestos; nearly anything older is a candidate. Floor tile and mastic, drywall compound, textured ceilings, pipe insulation and vermiculite are the usual suspects."),
             ("Are you independent of abatement contractors?", "Yes. We never remove or abate anything and take no referral fees, so our survey results aren't shaped by anyone who profits from removal.")] + list(extra_faq)
    FAQ_HTML, FAQ_SCHEMA = faq(items)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, f"Asbestos testing in {city}"))}
<div class="hero-copy" style="max-width:860px"><h1>Asbestos testing and designated substance surveys in {city}</h1>
<p class="lede">{intro}</p>
<div class="btn-row"><a class="btn amber" href="obligation-check.html">Take the Obligation Check</a><a class="btn ghost" href="contact.html#book" data-book>Book a call</a></div></div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>What we do in {region}</h2>{ul([
 '<a href="services.html">Project designated substance surveys</a> before renovation, repair or demolition, from $550 for one suite',
 '<a href="building-owners.html">Annual asbestos reassessments and live registers</a> for commercial, industrial and institutional buildings',
 '<a href="landlords.html">Suite turnover checks</a> for landlords and property managers',
 '<a href="services.html">Abatement specifications, oversight, air monitoring and Type 3 clearance</a>',
 '<a href="employers.html">Exposure assessments and air monitoring</a> under O. Reg. 490/09',
 '<a href="contractors.html">Pre-work checks for contractors</a> with reserved booking'])}</div>
<div class="prose"><h2>Why it matters here</h2>{"".join(f"<p>{p}</p>" for p in local_points)}
<p class="small">We also cover {towns}.</p></div>
</div></section>
<section class="section"><div class="wrap"><div class="section-head"><h2>Common reasons people call</h2></div>
<div class="link-list">{"".join(f'<a href="{h}"><strong>{t}</strong><span>What it involves, what it costs and how fast you get results</span></a>' for h, t in TRIGGERS)}</div></div></section>
""" + FAQ_HTML + cta()
    page(fname, f"Asbestos Testing {city}, ON | Designated Substance Surveys | Noah Crowley",
         f"Independent asbestos testing, designated substance surveys, registers and air monitoring in {city} and {region}. Lab analysis included, results within 1 week.", body,
         schema=[FAQ_SCHEMA, {"@context": "https://schema.org", "@type": "Service", "name": f"Asbestos testing and designated substance surveys in {city}", "serviceType": "Asbestos testing", "provider": {"@id": BIZ_ID}, "areaServed": {"@type": "City", "name": f"{city}, Ontario"}}])

local_page("asbestos-testing-windsor.html", "Windsor", "Windsor-Essex",
    "Independent asbestos and designated substance work for Windsor building owners, landlords, employers and contractors, with lab analysis included and results within 1 week.",
    ["More than one in three Windsor dwellings was built before 1960, and most of the city's industrial and institutional floor space dates from the same era. Nearly everything built before 1980 is a candidate for asbestos-containing materials.",
     "The City of Windsor's demolition permit checklist asks for a designated substance list, so every demolition starts with a survey. We write them ready to attach to the permit and the tender."],
    "LaSalle, Tecumseh, Amherstburg and Lakeshore",
    [("Do I need a designated substance survey for a demolition permit in Windsor?", "Yes. The City of Windsor's demolition permit checklist asks for a list of designated substances. We write the survey ready to attach to the permit application and the demolition tender.")])
local_page("asbestos-testing-leamington.html", "Leamington", "Essex County",
    "Asbestos testing, designated substance surveys and suite turnover checks for Leamington and the rest of Essex County, booked into regular route days.",
    ["Older commercial buildings, rental stock and industrial sites across Essex County carry the same duties as the city: an asbestos record updated every 12 months, and a designated substance list before any renovation or demolition.",
     "Visits in the county are grouped into route days, which keeps response times predictable and travel off your invoice."],
    "Kingsville, Essex, Lakeshore and the rest of Essex County")
local_page("asbestos-testing-chatham.html", "Chatham", "Chatham-Kent",
    "Designated substance surveys, asbestos reassessments and air monitoring for owners, landlords and contractors across Chatham-Kent.",
    ["Older buildings changing hands or changing use, from former schools to commercial blocks, need a designated substance list before contractors are hired. We write it ready to attach to the tender.",
     "Landlords and property managers can add suite turnover checks so units are renovated between tenants without surprises."],
    "Wallaceburg, Tilbury, Blenheim and Ridgetown")
local_page("asbestos-testing-sarnia.html", "Sarnia", "Sarnia-Lambton",
    "Asbestos surveys, abatement oversight and designated substance exposure monitoring for Sarnia-Lambton's buildings, plants and contractors.",
    ["Sarnia's petrochemical sites add turnaround and shutdown work, which is when asbestos in older facilities gets disturbed. Facility Partner clients get oversight and monitoring days reserved for those windows.",
     "Plastics and resin plants in the area carry O. Reg. 490/09 duties for benzene, vinyl chloride and acrylonitrile. Our Workplace Exposure Program covers the assessment, control program and air monitoring."],
    "Point Edward, Petrolia and the rest of Lambton County")
local_page("asbestos-testing-london.html", "London", "London and Middlesex",
    "Independent designated substance surveys, asbestos registers and exposure monitoring for London-area owners, landlords, employers and contractors.",
    ["Large national firms are strong on big portfolios and public tenders, but their minimum fees make small jobs unattractive. We work for owners who want one named consultant and a predictable monthly price.",
     "Contractors working in older London buildings can book pre-work checks into reserved slots, so results arrive before the crew mobilizes."],
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
  "Before walls or floors open in an older building, a designated substance survey lists what the work will disturb. From $550, lab analysis included, results within 1 week.",
  "Before walls, floors or ceilings open in an older building, Ontario law requires a list of every designated substance in the work area. We survey it, test it and hand you a report ready for the contractor.",
  [("What the law requires", "<p>The project owner must list all designated substances before a renovation, repair or demolition project begins and include the list in the tender (OHSA section 30). An owner who leaves one off is liable to the contractors when it turns up mid-job.</p><p>Most buildings built after 1980 are largely free of asbestos; nearly everything older is a candidate.</p>"),
   ("What we test for", ul(["Floor tile and mastic, drywall joint compound, plaster and stipple ceilings", "Pipe and boiler insulation, cement board and vermiculite", "Lead in paint, solder, pipes and glazing", "Mercury in thermostats, switches and lamps", "Silica released when concrete, masonry or tile is cut", "All 11 designated substances, as the project list requires"])),
   ("Price and timing", "<p>$550 for one suite or up to 2,000 sq ft, and $1,300 to $4,800 for commercial work areas. Lab analysis is included and results come back within 1 week.</p><p>If the job can't wait, we leave written interim instructions on site: which materials to treat as asbestos-containing and which procedures apply until results are in.</p>"),
   ("If you renovate often", "<p>Contractors can buy checks wholesale with the <a href=\"contractors.html\">Pre-Work Clearance Pass</a> from $425 a check, and landlords can add <a href=\"landlords.html\">suite turnover checks</a> to their program.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "What a survey covers and what to do if you find suspect material mid-job"),
      ("guide-suite-turnover-checklist.html", "Suite turnover checklist", "The materials to stop and test in older rental suites")))

trigger_page("designated-substance-survey-demolition-permit.html", "Designated substance survey for a demolition permit",
  "Designated substance survey for a demolition permit in Windsor | Noah Crowley",
  "The City of Windsor's demolition permit checklist asks for a designated substance list. We write the survey ready to attach to the permit application and the tender.",
  "The City of Windsor's demolition permit checklist asks for a list of designated substances. We survey the building and write a report you can attach to the permit application and the demolition tender.",
  [("What the survey covers", "<p>All 11 designated substances in the building, with locations, quantities and condition, plus other hazardous materials that affect demolition such as PCBs, mould and ozone-depleting refrigerants.</p>"),
   ("What usually follows", ul(["<strong>Abatement specification:</strong> scope of work, procedure type, quantities and bid review, $1,500–$5,000", "<strong>Abatement oversight and air monitoring:</strong> daily inspections and reports during Type 2 or Type 3 work, $1,100 a day", "<strong>Type 3 clearance:</strong> visual inspection and aggressive air testing before the enclosure comes down, $625–$900 a visit"])),
   ("Price and timing", "<p>Commercial work areas are $1,300 to $4,800 depending on size; a single house or suite is $550. Lab analysis is included and results come back within 1 week.</p>"),
   ("Independent from the abatement", "<p>We never remove or abate anything and take no referral fees, so the survey, the specification and the clearance are all written by someone with no stake in how much removal there is.</p>")],
  rel(("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide", "Built around the City of Windsor's demolition permit checklist"),
      ("services.html", "One-off services and list prices", "Every survey, specification and monitoring service")))

trigger_page("silica-exposure-assessment.html", "Silica exposure assessment",
  "Silica exposure assessment and air monitoring in southwestern Ontario | Noah Crowley",
  "Written silica exposure assessments, control programs and air monitoring under O. Reg. 490/09 for countertop fabricators, foundries and concrete products plants.",
  "Countertop fabricators, foundries, concrete products and glass plants carry O. Reg. 490/09 duties for silica. We write the assessment with your JHSC, set up the control program and run the air monitoring.",
  [("Why silica is in focus", "<p>Engineered stone can be up to 95% silica, and Ontario's Ministry of Labour issued a safety alert on silica exposure during countertop manufacturing and installing in 2023, updated in May 2025.</p>"),
   ("What you need on file", ul(["A written exposure assessment made with your joint health and safety committee", "A control program where health may be affected: wet cutting and ventilation, work and hygiene practices, training", "Air monitoring by or under a qualified hygienist, results posted for 14 days and kept 5 years", "Medical surveillance arranged with your physician", "A respiratory protection program if respirators are in use"])),
   ("Price", "<p>Assessments run $2,500 to $7,500 depending on processes. A control program is $2,000 to $5,000 and an exposure monitoring day is $1,400. The <a href=\"employers.html\">Workplace Exposure Program</a> keeps it all current from $299 a month.</p>"),
   ("Who does the monitoring", "<p>Monitoring is done by or under our qualified occupational hygienist. Medical surveillance is done by your physician; we coordinate the records.</p>")],
  rel(("guide-designated-substance-self-check.html", "Designated substance self-check", "A one-page test of whether O. Reg. 490/09 applies to you"),
      ("employers.html", "Workplace Exposure Program", "Assessment, control program and monitoring on one monthly fee")))

trigger_page("isocyanate-air-monitoring.html", "Isocyanate air monitoring",
  "Isocyanate air monitoring for collision shops and paint lines | Noah Crowley",
  "Isocyanate exposure assessments and air monitoring under O. Reg. 490/09 for collision and auto body shops, paint lines and spray foam installers in southwestern Ontario.",
  "Collision and auto body paint booths, auto-sector paint lines, spray foam installers and polyurethane manufacturers work with isocyanates, one of Ontario's designated substances. We assess the exposure and monitor the air.",
  [("What the regulation asks", ul(["A written exposure assessment made with your JHSC, redone after any change that could significantly affect exposure", "A control program where health may be affected", "Air monitoring by or under a qualified hygienist, results posted for 14 days, copied to the JHSC and kept 5 years", "Medical surveillance, which applies to isocyanates"])),
   ("What a monitoring day includes", "<p>A full day of personal and area air monitoring during normal spraying, a results report, a posting notice and a copy for your JHSC. $1,400 a day, lab analysis included.</p>"),
   ("For a one-booth shop", "<p>The <a href=\"employers.html\">Workplace Exposure Program Shop tier</a> covers the annual assessment review, one monitoring day, a training session and your records for $299 a month, about what the same year costs bought one service at a time.</p>"),
   ("Respirators", "<p>Respiratory protection programs were the most common gap in the Ministry's 2024–25 chemical exposure campaign. We write the program, selection guidance and training records for $1,200 to $2,500.</p>")],
  rel(("guide-designated-substance-self-check.html", "Designated substance self-check", "A one-page test of whether O. Reg. 490/09 applies to you"),
      ("employers.html", "Workplace Exposure Program", "Assessment, control program and monitoring on one monthly fee")))

# ---------------------------------------------------------------- guides (lead magnets)
def guide_page(fname, h1, title, desc, lede, items, after, cta_href):
    lis = "".join(f"<li><div><b>{a}</b><span>{b}</span></div></li>" for a, b in items)
    body = f"""<section class="hero"><div class="wrap">{crumbs((None, h1))}
<div class="hero-copy" style="max-width:860px"><h1>{h1}</h1><p class="lede">{lede}</p>
<div class="btn-row no-print"><button class="btn ghost" type="button" onclick="window.print()">Print this checklist</button><a class="btn amber" href="{cta_href}">Take the Obligation Check</a></div></div></div></section>
<section class="section white"><div class="wrap"><div class="prose" style="max-width:820px"><ul class="checklist">{lis}</ul>{after}
<p class="small">This checklist is general guidance, not legal advice. Ontario regulations referenced: O. Reg. 278/05, OHSA section 30 and O. Reg. 490/09.</p></div></div></section>""" + cta("Want someone to check it for you?", "A paid gap audit walks your site against this list. The fee is credited if you join a program.", cta_href)
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
   ("Keep the result with the suite record", "A written result per suite builds the register and answers the next turnover in minutes.")],
  "<p>Our <a href=\"landlords.html\">Rental Portfolio Program</a> includes 2 to 24 suite turnover checks a year, with a written result within 1 week of each visit.</p>", "obligation-check.html#rental")

guide_page("guide-designated-substance-self-check.html", "Designated substance self-check",
  "Does O. Reg. 490/09 apply to you? A designated substance self-check | Noah Crowley",
  "A one-page self-check for Ontario employers: whether O. Reg. 490/09 applies, and what an inspector will ask for.",
  "Work down the list. If you answer yes to the first two items and no to any after them, you have a gap an inspector would find.",
  [("Is a designated substance present, used, handled or stored at your workplace?", "Asbestos, acrylonitrile, arsenic, benzene, coke oven emissions, ethylene oxide, isocyanates, lead, mercury, silica or vinyl chloride."),
   ("Is a worker likely to be exposed to it?", "If so, the regulation applies. It does not apply on construction projects; dental practices are excluded for mercury and pumping gas is excluded for benzene."),
   ("Do you have a written exposure assessment made with your JHSC?", "Each committee member gets a copy, and it is redone after any change that could significantly affect exposure."),
   ("If health may be affected, do you have a written control program?", "Engineering controls, work and hygiene practices, monitoring, records and training."),
   ("Is air monitoring done by or under a qualified industrial hygienist?", "Results posted for 14 days, given to the JHSC, and kept for 5 years."),
   ("Is medical surveillance in place where required?", "Required for asbestos, benzene, coke oven emissions, isocyanates, lead, mercury and silica."),
   ("If respirators are used, is there a respiratory protection program?", "The most common gap in the Ministry's 2024–25 chemical exposure campaign."),
   ("Are other employers' workers protected at your site?", "Contractors are told about the substance and follow joint procedures.")],
  "", "obligation-check.html#employer")

guide_page("guide-demolition-renovation-dss.html", "Demolition and renovation DSS guide",
  "Demolition and renovation designated substance survey guide for Windsor-Essex | Noah Crowley",
  "What a designated substance survey covers before demolition or renovation in Windsor-Essex, and what to do when you find suspect material mid-job.",
  "Built around the City of Windsor's demolition permit checklist, which asks for a designated substance list. The second half covers what to do when suspect material turns up mid-job.",
  [("The owner lists every designated substance before the project begins", "OHSA section 30 puts this on the project owner, and the list goes into the tender."),
   ("The list covers all 11 substances in the work area", "Not just asbestos: lead, mercury, silica and the rest are part of the same list."),
   ("Demolition permits need it", "The City of Windsor's demolition permit checklist asks for the designated substance list with the application."),
   ("Abatement follows the survey", "A specification sets the procedure type, quantities and scope before abatement is bid."),
   ("Type 3 work needs clearance before the enclosure comes down", "Aggressive air testing below 0.01 fibres per cc, done by someone independent of the abatement contractor."),
   ("Mid-job find: stop work except to identify the material", "Don't keep cutting or demolishing in that area."),
   ("Mid-job find: notify right away", "The constructor or employer notifies the Ministry, the owner, the contractor and the JHSC."),
   ("Mid-job find: test or presume", "Wait for results, about a week, or treat the material as asbestos-containing and follow the matching procedures."),
   ("Mid-job find: get written interim instructions", "A consultant can tell you on site which materials to treat as asbestos-containing so lawful work can continue.")],
  "<p>Contractors who check before they cut avoid all of the second half. See the <a href=\"contractors.html\">Pre-Work Clearance Pass</a>.</p>", "obligation-check.html#contractor")

# ---------------------------------------------------------------- about
a = f"""<section class="hero"><div class="wrap">{crumbs((None, "How we work"))}
<div class="hero-copy" style="max-width:860px"><h1>How we work</h1><p class="lede">{e(SITE['online'])} is the online name of {e(SITE['legal'])}, an independent consultancy covering all 11 of Ontario's designated substances across {REGIONS}.</p></div></div></section>
<section class="section white"><div class="wrap split">
<div class="prose"><h2>Independence</h2><p>We never remove or abate anything and take no referral fees. We don't sell the Pre-Work Clearance Pass to abatement contractors, and we don't do clearance on work a Pass holder abates. It's written into every agreement.</p>
<h2>One named consultant</h2><p>You deal with the same person who walks your building, writes your register and answers your pre-work questions. Workplace exposure monitoring is done by or under our qualified occupational hygienist.</p></div>
<div class="prose"><h2>How pricing works</h2><p>Every price includes the lab analysis the service needs, so testing never shows up as a surprise line. Results come back within 1 week, and when work can't wait we leave written interim instructions on site.</p>
<p>Programs run on 12-month agreements at a monthly fee, priced at about what the same year of compliance costs bought one job at a time.</p>
<h2>Where we work</h2><p>{", ".join(f'<a href="{h}">{t}</a>' for h, t in CITIES)}, and the towns around them.</p></div>
</div></section>""" + cta()
page("about.html", "How we work | Independent asbestos consulting | Noah Crowley", f"An independent asbestos and designated substances consultancy for {REGIONS}. No removal work, no referral fees, one named consultant.", a)

# ---------------------------------------------------------------- contact
cb = contact_bits()
contact_side = ("<p>" + "<br>".join(cb) + "</p>") if cb else ""
ct = f"""<section class="hero"><div class="wrap">{crumbs((None, "Contact"))}
<div class="split">
<div class="hero-copy"><h1>Talk to us about a building, a workplace or a job</h1>
<p class="lede">Tell us what you're dealing with and we'll reply within one business day with a price or a time to visit.</p>
{contact_side}
<div id="book" class="duty" style="margin-top:8px"><h3>Prefer to book a call?</h3><p>Pick a 15-minute slot and we'll call you.</p><div class="btn-row"><a class="btn" href="contact.html#book" data-book>Book a call</a></div></div>
<p class="area">Serving {REGIONS}.</p></div>
<form class="form" data-form data-name="contact" style="background:var(--paper);border:1px solid var(--line);border-radius:10px;padding:28px">
<input type="hidden" name="_subject" value="Website enquiry">
<div class="row2"><label class="field">Your name<input name="name" required autocomplete="name"></label><label class="field">Company<input name="company" autocomplete="organization"></label></div>
<div class="row2"><label class="field">Email<input name="email" type="email" required autocomplete="email"></label><label class="field">Phone<input name="phone" type="tel" autocomplete="tel"></label></div>
<label class="field">What do you need?<select name="need">
<option>A designated substance survey before renovation or demolition</option><option>An asbestos reassessment or register for my building</option>
<option>Suite turnover checks for rental units</option><option>A workplace exposure assessment or air monitoring</option>
<option>Pre-work checks for my contracting business</option><option>Abatement specification, oversight or Type 3 clearance</option><option>Something else</option></select></label>
<label class="field">Site address (optional)<input name="site_address" autocomplete="street-address"></label>
<label class="field">Details<textarea name="message" placeholder="Building age, size, what work is planned and when"></textarea></label>
<label class="check"><input type="checkbox" name="consent_updates" value="yes"> Also send me occasional compliance reminders and updates by email. You can unsubscribe at any time.</label>
<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website_url" tabindex="-1" autocomplete="off"></label></div>
<button class="btn" type="submit">Send message</button>
<p class="small">We use your details only to reply to this request. See our <a href="privacy.html">privacy notice</a>.</p>
</form></div></div></section>"""
page("contact.html", "Contact | Noah Crowley Asbestos and Designated Substances Consulting", f"Ask for a designated substance survey, asbestos reassessment, suite check or exposure monitoring quote in {REGIONS}.", ct, "contact.html")

# ---------------------------------------------------------------- privacy
pv = f"""<section class="hero"><div class="wrap">{crumbs((None, "Privacy notice"))}
<div class="prose"><h1>Privacy notice</h1>
<p>{e(SITE['legal'])}, operating as {e(SITE['online'])}, collects only the personal information you choose to send us through this website.</p>
<h2>What we collect and why</h2>
<p>When you send a form or the Obligation Check result, we receive your name, company, email, phone, site address and the answers or details you provide. We use them to reply, to quote and to deliver the service you ask for.</p>
<h2>Email</h2>
<p>We send commercial emails only with your consent or where Canada's Anti-Spam Legislation otherwise allows it. The reminders checkbox on our forms is optional and unticked by default. Every email we send includes a way to unsubscribe, and we act on unsubscribe requests within 10 business days.</p>
<h2>Who processes it</h2>
<p>Form submissions are delivered to us by our form provider, and calls are booked through our scheduling provider. Fonts are loaded from Google Fonts. We don't sell or rent personal information, and this site does not use advertising trackers.</p>
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
