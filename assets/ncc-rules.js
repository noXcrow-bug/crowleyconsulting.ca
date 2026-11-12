/* NCC shared rules (2026-11-12): which product fits a caller, and what to warn about.
   ONE copy of the "Do I need a DSS?" logic, used by NCC Office's intake (index.html) and, next, by the website's
   Obligation Check (crowleyconsulting.ca). No prices here and no page code: prices come from pricebook.js when a page passes it in.
   Ground rules (Noah):
   - OHSA s.30 applies before EVERY project, whatever the building's age. Age never decides WHETHER a DSS is needed;
     it decides how big the job is (1990+ = fewer suspect materials = smaller sample estimate = lower quote).
   - The trigger decides the scope (whole building vs the work area), not the age.
   - Never say "not required", and never confirm "no asbestos" without lab results.
   - Cleared-to-Start Pass is never offered to abatement contractors.
   - Lab: 5 business days from the lab's receipt; 8-10 business days start to finish; no rush service.
   window.NCC_RULES = { version, TRIGGERS, ROLES, USES, REPORTS, AREAS, SCALES, SEGMENT, era, cls, bizDaysUntil, route, fromIntake, recommend, flags, summary } */
(function (root) {
  "use strict";
  const version = "R-2026.11c";

  const TRIGGERS = [
    ["reno", "Renovation or repairs"], ["demo", "Demolition"], ["claim", "Insurance claim / restoration (fire, flood, mould)"],
    ["tender", "Tender or project documents"], ["sale", "Selling, buying or refinancing"], ["concern", "Damaged material or exposure worry"],
    ["know", "Wants to know what's in the building"], ["other", "Something else"]];
  const ROLES = [
    ["owner", "Building owner"], ["pm", "Property or facility manager"], ["restoration", "Restoration contractor"], ["gc", "General contractor / renovator"],
    ["trade", "Trade (electrician, plumber, HVAC...)"], ["abatement", "Abatement contractor"], ["homeowner", "Homeowner"], ["other", "Other"]];
  const USES = [["house", "House (single-family)"], ["multi", "Multi-unit residential"], ["commercial", "Office / retail / commercial"], ["industrial", "Industrial"], ["institutional", "School / hospital / institutional"], ["other", "Other"]];
  const REPORTS = [["none", "No report"], ["current", "Yes, current and covers this work"], ["old", "Yes, but old or out of date"], ["partial", "Yes, but it doesn't cover this work"], ["unsure", "Not sure"]];
  const AREAS = [["kitchen", "Kitchen"], ["bath", "Bathroom"], ["basement", "Basement"], ["flooring", "Flooring"], ["walls", "Walls / ceilings"], ["roof", "Roof"], ["mech", "Boiler / pipes / ducts"], ["exterior", "Windows / exterior"], ["whole", "Whole building"], ["demo", "Demolition"]];
  /* Customer type in NCC Office for each caller role */
  const SEGMENT = { owner: "building", pm: "building", restoration: "contractor", gc: "contractor", trade: "contractor", abatement: "abatement", homeowner: "homeowner" };
  const CONTRACTOR = new Set(["restoration", "gc", "trade", "abatement"]);

  /* Building age bucket from a year or a choice: "old" (before 1990), "new" (1990 or later), "" (not sure) */
  function era(built) {
    const s = String(built == null ? "" : built).trim().toLowerCase();
    if (s === "pre1990" || s === "old") return "old";
    if (s === "1990+" || s === "post1990" || s === "new") return "new";
    const y = parseInt(s, 10);
    if (/^\d{4}$/.test(s) && y > 1800) return y < 1990 ? "old" : "new";
    return "";
  }
  /* Building class from floor area in m², using the price list's class boundaries when given */
  function cls(m2, pb) {
    const a = Number(m2); if (!isFinite(a) || a <= 0) return "";
    const C = (pb && pb.classes) || { A: { m2: 465 }, B: { m2: 2323 }, C: { m2: 9290 } };
    return a <= C.A.m2 ? "A" : a <= C.B.m2 ? "B" : a <= C.C.m2 ? "C" : "D";
  }
  /* Business days from today to a YYYY-MM-DD date (weekends skipped; holidays ignored). null when no date. */
  function bizDaysUntil(date, today) {
    if (!/^\d{4}-\d{2}-\d{2}/.test(String(date || ""))) return null;
    const t = today ? new Date(String(today).slice(0, 10) + "T12:00:00") : new Date(new Date().toDateString() + " 12:00");
    const d = new Date(String(date).slice(0, 10) + "T12:00:00");
    if (d <= t) return 0;
    let n = 0; const x = new Date(t);
    while (x < d) { x.setDate(x.getDate() + 1); const w = x.getDay(); if (w !== 0 && w !== 6) n++; }
    return n;
  }

  const isHouse = (a) => a.role === "homeowner" || a.use === "house";
  const isDemo = (a) => a.trigger === "demo" || (a.areas || []).includes("demo");
  const MATERIAL_AREAS = new Set(["kitchen", "bath", "basement", "flooring", "walls", "roof", "mech", "exterior"]);
  const SCALES = [["minor", "Small job: a repair or a few materials"], ["major", "Major renovation: gutting or reconfiguring"]];

  /* THE routing both surfaces share (moved here from the website's Obligation Check, R-2026.11b; same results for all 672 website answer sets).
     p = { use ("house" = single-family), era: "old" | "new" | "" (not sure), work: "demo" | "major" | "minor" | "due" | "know",
           disturb: materials the work disturbs (any keys), plus "none" (won't open materials) and/or "unsure", report: "none" | "current" | "old" | "unsure" }
     Returns { level, key }: level 1 = survey needed, 2 = targeted check or review, 3 = may already be covered / should be simple,
     "survey" = not a project yet (purchase or general question). key = limited | update | project | survey | full | predemo, or null (no product yet). */
  function route(p) {
    const d = p.disturb || [], work = p.work, real = d.filter((x) => x !== "none" && x !== "unsure");
    if (work === "due" || work === "know") return { level: "survey", key: work === "due" ? "full" : "survey" };
    const unsure = p.era === "" || p.report === "unsure" || d.includes("unsure");
    const opens = work === "demo" || work === "major" || real.length > 0;
    const old = p.era !== "new", house = p.use === "house";
    let level, key;
    if (work === "demo" && p.report !== "current") level = 1;
    else if (old && opens && (p.report === "none" || p.report === "unsure")) level = 1;
    else if (!unsure && work !== "demo" && (p.report === "current" || (p.era === "new" && d.includes("none")))) level = 3;
    else level = 2;
    if (work === "demo") key = "predemo";
    else if (level === 3) key = null;
    else if (p.report === "old") key = "update";
    else if (house || (level === 2 && work === "minor" && real.length <= 3)) key = "limited";
    else key = "project";
    return { level, key };
  }
  /* Intake answers -> route() input */
  function fromIntake(a) {
    const areas = (a.areas || []).filter((x) => MATERIAL_AREAS.has(x));
    const work = isDemo(a) ? "demo" : a.trigger === "sale" ? "due" : a.trigger === "know" ? "know"
      : (a.areas || []).includes("whole") ? "major" : a.scale === "minor" ? "minor" : a.scale === "major" ? "major"
      : ["claim", "tender"].includes(a.trigger) ? "major" : a.trigger === "concern" ? "minor" : "major";
    const report = a.report === "current" ? "current" : a.report === "old" || a.report === "partial" ? "old" : a.report === "none" ? "none" : "unsure";
    return { use: isHouse(a) ? "house" : a.use, era: era(a.built), work, disturb: areas.length ? areas : (a.areas || []).length ? ["whole"] : ["unsure"], report };
  }

  /* The likely fit for the intake. a = { trigger, role, use, built, areaM2, report, areas[], scale, start, today, member: {kind: "pass"|"program", name} for active clients }.
     Returns { key, name, cls, level, why, say, also, from }; key is a price-list report key or "review" / "simple" (no product yet). */
  function recommend(a, pb) {
    a = a || {};
    const names = (pb && pb.names) || { limited: "Limited sampling visit", update: "DSS update or re-assessment", project: "Project-specific DSS", survey: "Asbestos building survey", full: "Full-building DSS + hazmat", predemo: "Pre-demolition DSS" };
    const p = fromIntake(a), r = route(p), c = isHouse(a) ? "A" : cls(a.areaM2, pb), e = p.era;
    let key = r.key, why, say;
    /* Class D (R-2026.11c, Noah): the price book has no limited visit over Class C, so a big building gets a Project-specific DSS. Website unaffected (it doesn't ask size). */
    const classD = key === "limited" && !isHouse(a) && c === "D";
    if (classD) key = "project";
    if (key === "predemo") { why = "Demolition needs a destructive pre-demolition survey, even if there's a recent report."; say = "For demolition we do a destructive survey: we open up walls, floors and ceilings so nothing is missed."; }
    else if (key === null && a.report === "current") { key = "review"; why = "They say they have a current report that covers this work. Read it before selling anything."; say = "Send me a copy of your report. If it covers this work, you may not need much from us."; }
    else if (key === null) { key = "simple"; why = "Newer building and work that won't open up materials: likely a short list. The owner still needs one before work starts."; say = "This one should be simple, but the owner still needs the list before the contract is signed."; }
    else if (key === "limited") { why = isHouse(a) ? "A house renovation: test or presume each material the work touches. Homeowner pays; no program." : "A small job touching a few materials: a scoped sampling visit covers it."; say = isHouse(a) ? "For a house, we only test the materials your renovation will disturb." : "For a small job, we only sample the few materials the work touches."; }
    else if (key === "update") { why = a.report === "partial" ? "Their report doesn't cover this work: update it to take in the work area." : "There's a report, but it's old or out of date. Updating it costs less than starting over."; say = "We can update your existing report instead of starting from scratch."; }
    else if (key === "full" || key === "survey") { why = key === "full" ? "A sale or refinance: a full DSS covers every designated substance for the buyer or lender." : "They want to know what's in the building. An asbestos building survey answers it; a full DSS adds the other designated substances."; say = "A survey tells you what's in the building and becomes your list when work is planned."; }
    else { why = a.trigger === "tender" ? "Tender documents need the designated substance list for the work (OHSA s.30)." : r.level === 1 ? "Nothing on file covers work that opens up this building: the work area needs sampling (OHSA s.30)." : "The work area needs a designated substance list before work starts (OHSA s.30)."; say = "We survey just the areas your project touches, and you get the report the contractor needs."; }
    if (classD) why = "Small job, but a Class D building: the price book has no limited visit at this size, so a Project-specific DSS.";
    if (e === "new" && !["review", "simple"].includes(key)) why += " Built 1990 or later: still needs it, but expect fewer suspect materials, so a smaller sample estimate.";
    const also = [], m = a.member || null;
    /* Existing clients first (R-2026.11c, Noah): Pass members -> check the Pass; program clients -> member rate. */
    if (m && m.kind === "pass") also.push(`Pass member (${m.name || "Cleared-to-Start Pass"}): check what their Pass includes before quoting a separate report.`);
    if (m && m.kind === "program") also.push(`Program client (${m.name || "building program"}): quote it at their member rate.`);
    if (key === "limited" && !isHouse(a)) also.push("Open question (Noah, Nov 12): confirm a limited visit report can serve as the owner's s.30 list for a commercial job before you sell it.");
    if (!m && CONTRACTOR.has(a.role) && a.role !== "abatement" && key !== "predemo") also.push("If they do this kind of work often: the Cleared-to-Start Pass. Ask how many jobs a month.");
    if (!m && (a.role === "owner" || a.role === "pm") && !isHouse(a)) also.push("Later, once the report is delivered: a building program (mention it then, not on this call).");
    if (key === "review") also.push(`If the report is older or doesn't match the building: ${names.update}.`);
    if (key === "simple") also.push(`If they're unsure what the work touches: ${names.limited}.`);
    const from = pb && pb.publicFrom && pb.publicFrom[key] != null ? pb.publicFrom[key] : null;
    const NM = { review: "Review their existing report", simple: "Likely a short list (confirm the scope)" };
    return { key, name: NM[key] || names[key], cls: c, level: r.level, scope: ["survey", "full", "predemo"].includes(key) ? "whole" : "project", era: e, why, say, also, from };
  }

  /* Warnings to raise on the call. Each { lvl: "act"|"warn"|"info", t, say } */
  function flags(a, pb) {
    a = a || {};
    const out = [], e = era(a.built), lab = (pb && pb.labDays) || 5, bd = a.startWithin === "month" ? 15 : bizDaysUntil(a.start, a.today);
    if (bd !== null && bd < 10) out.push({ lvl: "act", t: `Work starts in ${bd} business day${bd === 1 ? "" : "s"}. Results take 8-10 business days from the site visit (lab: ${lab} from receipt). No rush service.`, say: "Tell them now, before anything else: we can't have results before the start date." });
    else if (bd !== null && bd < 22) out.push({ lvl: "warn", t: "Work starts within a month. Book the site visit soon: results take 8-10 business days, no rush service.", say: "To be ready on time we should get in this week or next." });
    if (a.role === "abatement") out.push({ lvl: "warn", t: "Abatement contractor: the Cleared-to-Start Pass is not offered to abatement contractors.", say: "We can survey for the building owner; the report goes to the owner." });
    if (isDemo(a) && (a.report === "current" || a.report === "old" || a.report === "partial")) out.push({ lvl: "warn", t: "Demolition with an existing report: it still needs a destructive pre-demolition survey.", say: "" });
    if (isDemo(a)) out.push({ lvl: "info", t: "Demolition samples use the demolition sample rate on the quote.", say: "" });
    if (a.trigger === "concern") out.push({ lvl: "act", t: "Damaged material or exposure worry: tell them not to disturb it and keep people away until it's sampled.", say: "Don't touch or clean it up yourselves. Keep people out of that area until we've sampled it." });
    if (e === "new") out.push({ lvl: "info", t: "Built 1990 or later: it STILL needs a DSS (OHSA s.30 has no age limit; asbestos products were legal until 2018; silica, lead and mercury still apply). Expect fewer suspect materials, so a lower quote.", say: "Newer buildings still need the survey, but there's usually less to sample, so it costs less." });
    else if (e === "old") out.push({ lvl: "info", t: "Built before 1990: expect asbestos-containing materials; presume until tested.", say: "" });
    else if (a.built !== undefined) out.push({ lvl: "info", t: "Building age unknown: ask them to find the year, or treat it as before 1990.", say: "" });
    if (a.payer && a.payer !== "caller") out.push({ lvl: "warn", t: "Someone else signs and pays. Get their name and email, and quote to them.", say: "Who should the quote go to?" });
    if (CONTRACTOR.has(a.role) && a.role !== "abatement") out.push({ lvl: "info", t: "The report is addressed to the building owner, with the contractor as requester. Get the owner's name.", say: "" });
    if (a.report === "unsure") out.push({ lvl: "info", t: "They're not sure about an existing report: ask the owner or property manager to check before you quote.", say: "" });
    out.push({ lvl: "info", t: "Never say a material is clean or 'no asbestos' without lab results.", say: "" });
    return out;
  }

  /* One-paragraph summary for the customer's history */
  function summary(a, rec, labelOf) {
    const L = (list, k) => ((list.find((x) => x[0] === k) || [])[1]) || "";
    const parts = [];
    parts.push(`Intake: ${L(TRIGGERS, a.trigger) || "reason not given"}${a.start ? `, work starts ${a.start}` : ""}.`);
    if (a.role) parts.push(`Caller: ${L(ROLES, a.role)}.`);
    if (a.address || a.built || a.areaM2) parts.push(`Building: ${[a.address, a.use ? L(USES, a.use) : "", a.built ? `built ${a.built}` : "", a.areaM2 ? `${Math.round(a.areaM2)} m²` : ""].filter(Boolean).join(", ")}.`);
    if (a.report) parts.push(`Existing report: ${L(REPORTS, a.report)}${a.reportBy || a.reportYear ? ` (${[a.reportBy, a.reportYear].filter(Boolean).join(", ")})` : ""}.`);
    if ((a.areas || []).length || a.scale) parts.push(`Work: ${[L(SCALES, a.scale), ...(a.areas || []).map((k) => L(AREAS, k))].filter(Boolean).join(", ")}.`);
    if (rec) parts.push(`Likely fit: ${rec.name}${rec.cls ? ` (Class ${rec.cls})` : ""}.`);
    return parts.join(" ");
  }

  root.NCC_RULES = { version, TRIGGERS, ROLES, USES, REPORTS, AREAS, SCALES, SEGMENT, era, cls, bizDaysUntil, route, fromIntake, recommend, flags, summary };
})(typeof window !== "undefined" ? window : globalThis);
