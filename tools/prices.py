"""The website's prices, rates and turnarounds: ONE file, tools/prices.json.

tools/prices.json is the NCC price list (the same file NCC Office uses as pricebook.js), generated from the NCC Service
Menu & Price Guide (NCC-011) and checked number by number against it before it is copied here. Never edit it by hand:
change the Guide, then ask Claude to "run the price change routine" (project note claude/price-sync.md).

Copy in tools/build.py and assets/site.js never types a price, rate, turnaround or inclusion count. It writes a token,
[[name]], and fill() puts the value in at build time. Two guards run on every build and stop it on any problem:
  lint_sources()  no NCC number typed into build.py or site.js (outside the documented NOT_PRICES list)
  check_output()  every NCC number on the built site is one the price list holds, and no token is left unfilled
Added 2026-11-12 (Noah: "top-down trickle")."""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = json.load(open(os.path.join(ROOT, "tools", "prices.json")))
assert P.get("schema") == 2 and P.get("stamp", {}).get("pb"), "tools/prices.json is not a schema-2 NCC price list (PB-2026.11g or later)"

def money(x):
    x = float(x); return f"${x:,.0f}" if x == int(x) else f"${x:,.2f}"
def pct(d): return f"{round(d * 100)}%"
def rng(v, sep="–"): return f"{v[0]}{sep}{v[1]}" if v[0] != v[1] else str(v[0])
def fee(v): return money(v["from"]) if isinstance(v, dict) else money(v)

S, D, RA, CL, PR = P["sample"], P["dss"], P["reassess"], P["clearance"], P["peer"]
V = {
 "pb": P["stamp"]["pb"], "hst": pct(P["hst"]), "labDays": str(P["labDays"]), "rushDays": rng(P["rush"]["days"]), "rushDays.to": rng(P["rush"]["days"], " to "),
 "visitDays": str(P["siteVisitDays"]),
 "sample": money(S["bulk"]), "layer": money(S["layer"]), "sample.demo": money(S["demo"]), "layer.demo": money(S["demoLayer"]), "sample.verm": money(S["verm"]),
 "rush.sample": money(S["rushBulk"]), "rush.layer": money(S["rushLayer"]), "rush.demo": money(S["rushDemo"]), "rush.verm": money(S["rushVerm"]),
 "minVisit": money(P["minVisit"]), "freeKm": str(P["travel"]["freeKm"]), "freeMi": str(P["travel"]["freeMi"]), "perKm": money(P["travel"]["perKm"]),
 "afterHours": pct(P["afterHours"]), "overnight": money(P["overnight"]), "binder": money(P["binder"]), "hazAddon": money(P["hazAddon"]),
 "paymentDays": str(P["paymentDays"]), "quoteValidDays": str(P["quoteValidDays"]), "cancelDays": str(RA["cancelNoticeDays"]),
 "classA.m2": f"{P['classes']['A']['m2']:,}", "classA.ft2": f"{P['classes']['A']['ft2']:,}",
 "classB.m2": f"{P['classes']['B']['m2']:,}", "classB.ft2": f"{P['classes']['B']['ft2']:,}", "classC.m2": f"{P['classes']['C']['m2']:,}", "classC.ft2": f"{P['classes']['C']['ft2']:,}",
 "bulk.visit": money(P["bulkSampling"]["visit"]), "bulk.callout": money(P["bulkSampling"]["callout"]),
 "abate.spec": money(P["abatement"]["spec"]), "abate.specDays": str(P["abatement"]["specDays"][0]), "abate.visit": money(P["abatement"]["visit"]), "abate.package": money(P["abatement"]["package"]),
 "clr.small": money(CL["small"]), "clr.mid": money(CL["mid"]), "clr.large": money(CL["large"]), "clr.days": rng(CL["days"]),
 "clr.lead": money(CL["leadWipe"]), "clr.disturb": money(CL["disturbance"]),
 "train.t12": money(P["training"]["type12"]), "train.t12max": str(P["training"]["type12Max"]), "train.aware": money(P["training"]["awareness"]), "train.awaremax": str(P["training"]["awarenessMax"]),
 "peer.daysAB": str(PR["deskDays"]["A"][0]), "peer.daysCD": str(PR["deskDays"]["C"][0]),
}
for k in ("reno", "full", "predemo"):
    V[f"ta.{k}"] = rng(D[k]["days"]); V[f"ta.{k}.to"] = rng(D[k]["days"], " to ")
    for c in "ABCD": V[f"{k}.{c}"] = fee(D[k]["fee"][c])
for c in "ABCD":
    V[f"ra.setup.{c}"] = fee(RA["setup"][c]); V[f"ra.annual.{c}"] = fee(RA["annual"][c])
    V[f"peer.desk.{c}"] = fee(PR["desk"][c]); V[f"peer.visit.{c}"] = fee(PR["visit"][c])
for k, v in P["publicFrom"].items(): V[f"from.{k}"] = money(v)
# numbers the code needs as numbers (schema.org prices, the Obligation Check)
NUM = {"from": P["publicFrom"]}

TOKEN = re.compile(r"\[\[(pl:)?([\w.]+)\]\]")
def fill(s):
    """Replace every [[name]] with its value; [[pl:name]] gives "s" unless the value is 1. Unknown names stop the build."""
    def sub(m):
        if m.group(2) not in V: raise SystemExit(f"Unknown price token [[{m.group(2)}]]: add it to tools/prices.py or fix the copy.")
        v = V[m.group(2)]; return ("" if v == "1" else "s") if m.group(1) else v
    return TOKEN.sub(sub, s)

def deep_fill(o):
    """fill() inside lists and dicts (schema.org data, the Obligation Check data) before they are written as JSON."""
    if isinstance(o, str): return fill(o)
    if isinstance(o, list): return [deep_fill(x) for x in o]
    if isinstance(o, dict): return {k: deep_fill(v) for k, v in o.items()}
    return o

# ---------------------------------------------------------------- guards
# What counts as an NCC number in copy: money, percentages, business days, "N a month/year", "N sessions a year".
CLAIM = re.compile(r"\$\d{1,3}(?:,\d{3})*(?:\.\d\d)?(?:–\d{1,3}(?:,\d{3})*)?|\b\d+(?:\.\d+)?%|\b\d+(?:–\d+| to \d+)? business days?|\b\d+(?:–\d+)? (?:jobs )?a (?:month|year)\b|\b\d+ (?:live )?sessions? a year|\b\d+-month\b|\b\d+ months\b|\b\d+(?:–\d+)? with (?:gap )?sampling")
# Numbers that are NOT NCC prices or promises, each with its reason. A match is allowed only inside one of these phrases.
NOT_PRICES = [
 ("$2M", "OHSA maximum corporate fine (statute)"), ("$2 million", "OHSA maximum corporate fine (statute)"),
 ("$1.5 million", "OHSA maximum fine for a director (statute)"), ("77%", "Ministry 2023–24 campaign statistic"),
 ("$2,000 for a house", "City of London demolition deposit (municipal form)"), ("$10 per square metre", "City of London deposit (municipal form)"),
 ("up to $10,000", "City of London deposit cap (municipal form)"),
 ("45% Chrysotile", "example register lab result"), ("4% Chrysotile", "example register lab result"), ("2% Chrysotile", "example register lab result"),
 ("3% Chrysotile", "example register lab result"), ("0.9% lead", "example register lab result"), ("1.8% lead", "example register lab result"),
 ("within 10 business days", "CASL unsubscribe handling (privacy notice), not a service promise"),
 ("toLocaleString", "code"),
 ("every 12 months", "O. Reg. 278/05 re-inspection interval (regulation)"), ("the last 12 months", "O. Reg. 278/05 re-inspection interval (quiz choice)"),
 ("than 12 months", "O. Reg. 278/05 re-inspection interval (quiz choice)"), ("the 12-month window", "O. Reg. 278/05 re-inspection interval"), ("record within 12 months", "O. Reg. 278/05 re-inspection interval"),
 ("Your 12-month asbestos update", "O. Reg. 278/05 re-inspection interval"),
 ("In 1 to 3 months", "Obligation Check project-timing choice"), ("In 3 months or more", "Obligation Check project-timing choice"), ("More than 3 months", "Obligation Check project-timing choice"), ("0px 0px -8% 0px", "CSS scroll margin in site.js"), ("-25% 0px 0px 0px", "CSS scroll margin in site.js"),
]
def _allowed(text, start, end):
    for phrase, _ in NOT_PRICES:
        for m in re.finditer(re.escape(phrase), text):
            if m.start() <= start and end <= m.end(): return True
    return False
def lint_sources(paths):
    """No NCC number may be typed in these source files: copy must use [[tokens]]."""
    bad = []
    for p in paths:
        src = open(os.path.join(ROOT, p)).read()
        for m in CLAIM.finditer(src):
            if _allowed(src, m.start(), m.end()): continue
            line = src.count("\n", 0, m.start()) + 1
            bad.append(f"{p}:{line}: typed '{m.group(0)}' (use a [[token]] from tools/prices.py)")
    return bad
def allowed_values():
    vals = set()
    def add(s): vals.add(s)
    for k, v in V.items():
        add(v)
    for v in list(vals): add(v.replace(",", ""))
    return vals
def check_output(files):
    """Every NCC number on the built site must be a value the price list gives, and no [[token]] may be left."""
    vals, bad = allowed_values(), []
    for f in files:
        text = open(os.path.join(ROOT, f)).read()
        if "[[" in text and TOKEN.search(text): bad.append(f"{f}: unfilled token {TOKEN.search(text).group(0)}")
        plain = re.sub(r"<[^>]+>", " ", re.sub(r"<(script|style)[^>]*>(?!\s*window\.NCC_)[\s\S]*?</\1>", " ", text))
        for m in CLAIM.finditer(plain):
            if _allowed(plain, m.start(), m.end()): continue
            c = m.group(0)
            core = re.sub(r"-month$| months$", "", c); core = re.sub(r" (?:business days?|(?:jobs )?a (?:month|year)|(?:live )?sessions? a year|with (?:gap )?sampling)$", "", core)
            if core in vals or core.replace("$", "") in vals: continue
            bad.append(f"{f}: '{c}' is not a value in tools/prices.json")
    return bad
