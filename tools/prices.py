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
assert P.get("schema") == 1 and P.get("stamp", {}).get("pb"), "tools/prices.json is not a valid NCC price list"

def money(x):
    x = float(x); return f"${x:,.0f}" if x == int(x) else f"${x:,.2f}"
def pct(d): return f"{round(d * 100)}%"
def rng(v, sep="–"): return f"{v[0]}{sep}{v[1]}"
WORD = {1: "One", 2: "Two", 3: "Three", 4: "Four", 5: "Five", 6: "Six"}

PG, PS = P["programs"], P["passes"]
def first_monthly(prog): return next(v for v in prog["m"].values() if v is not None)
def jobs(fits): return re.match(r"(\d+(?:–\d+)?(?: or more)?) jobs a month", fits).group(1)
T = P["turnaround"]

V = {
 "pb": P["stamp"]["pb"], "hst": pct(P["hst"]), "labDays": str(P["labDays"]),
 "sample.comp": money(P["sample"]["comp"]), "sample.demo": money(P["sample"]["demo"]), "layer": money(P["layer"]),
 "minVisit": money(P["minVisit"]), "freeKm": str(P["travel"]["freeKm"]), "freeMi": str(P["travel"]["freeMi"]),
 "paymentDays": str(P["paymentDays"]), "quoteValidDays": str(P["quoteValidDays"]), "creditDays": str(P["firstReportCreditDays"]),
 "termMonths": str(P["subscription"]["termMonths"]), "prepaidMonths": str(P["prepaidMonths"]),
 "deskReply": str(P["deskReplyDays"]), "snapshotDays": str(P["registerSnapshotDays"]), "classLetterOff": pct(P["classLetterOff"]),
 "classA.m2": f"{P['classes']['A']['m2']:,}", "classA.ft2": f"{P['classes']['A']['ft2']:,}",
 "portfolio.Word": WORD[P["portfolio"][0][0]],
 "d.min": pct(min(p["d"] for p in PG.values())), "d.max": pct(max(p["d"] for p in PG.values())),
 "ta.limited": str(T["limited"]), "ta.updateNo": str(T["updateNoSampling"]), "ta.updateS": rng(T["updateSampling"]),
 "ta.project": rng(T["project"]), "ta.project.to": rng(T["project"], " to "), "ta.survey": rng(T["survey"]),
 "ta.full": f"{T['fullAB'][0]}–{T['fullCD'][1]}", "ta.predemo": rng(T["predemo"]), "ta.predemo.to": rng(T["predemo"], " to "),
}
for k, v in P["publicFrom"].items(): V[f"from.{k}"] = money(v)
for k, p in PG.items():
    V[f"m.{k}"] = money(first_monthly(p)); V[f"d.{k}"] = pct(p["d"])
    V[f"sched.{k}"] = str(p["schedDays"]); V[f"train.{k}"] = str(p["training"]); V[f"deskN.{k}"] = str(p["deskReviews"])
    V[f"inspCell.{k}"] = {1: "Once a year", 2: "Twice a year"}[p["inspections"]]
    V[f"trainCell.{k}"] = "Not included" if p["training"] == 0 else f"{p['training']} session{'s' if p['training'] > 1 else ''} a year"
    V[f"deskCell.{k}"] = "Not included" if p["deskReviews"] == 0 else "Unlimited" if p["deskReviews"] == -1 else f"{p['deskReviews']} a year"
for k, p in PS.items():
    V[f"m.{k}"] = money(p["m"]); V[f"d.{k}"] = pct(p["d"]); V[f"prebid.{k}"] = str(p["prebid"]); V[f"aware.{k}"] = str(p["awareness"])
    V[f"jobs.{k}"] = jobs(p["fits"]) if "jobs a month" in p["fits"] else ""
    V[f"jobs.{k}.to"] = V[f"jobs.{k}"].replace("–", " to ")
    V[f"visit.{k}"] = "" if p["visitDays"] is None else str(p["visitDays"])
    V[f"visitCell.{k}"] = "Next business day, Monday to Friday" if p["visitDays"] is None else f"Within {p['visitDays']} business days"
# numbers the code needs as numbers (schema.org prices, the Obligation Check)
NUM = {"from": P["publicFrom"], "m": {**{k: first_monthly(p) for k, p in PG.items()}, **{k: p["m"] for k, p in PS.items()}}}

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
 ("Chrysotile 45%", "example register lab result"), ("chrysotile 4%", "example register lab result"), ("Chrysotile 2%", "example register lab result"),
 ("chrysotile 3%", "example register lab result"), ("Lead 0.9%", "example register lab result"), ("Lead 1.8%", "example register lab result"),
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
