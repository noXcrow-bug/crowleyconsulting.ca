/* Noah Crowley Consulting — menu, forms, booking links and the Obligation Check */
(function () {
  var CFG = window.NCC_CONFIG || {};

  var REDUCE = window.matchMedia("(prefers-reduced-motion: reduce)");
  var EASE_OUT = "cubic-bezier(0.23, 1, 0.32, 1)";

  // Register rows: tap a row (or its button) to open the result, what to do and the condition history
  document.querySelectorAll("[data-register]").forEach(function (reg) {
    reg.addEventListener("click", function (ev) {
      var row = ev.target.closest("tr.r"); if (!row || ev.target.closest("a")) return;
      var b = row.querySelector(".r-btn"), det = document.getElementById(b.getAttribute("aria-controls"));
      var open = b.getAttribute("aria-expanded") !== "true";
      b.setAttribute("aria-expanded", String(open)); row.classList.toggle("open", open); det.hidden = !open;
      var inner = det.querySelector(".rd-in");
      if (open && inner.animate && !REDUCE.matches) inner.animate([{ opacity: 0, transform: "translateY(-4px)" }, { opacity: 1, transform: "none" }], { duration: 220, easing: EASE_OUT });
    });
  });

  // Example register page: show all buildings or one, from the link's #name
  var sw = document.querySelector(".bld-switch");
  if (sw) {
    var blds = Array.prototype.slice.call(document.querySelectorAll(".bld"));
    var showBld = function () {
      var h = (location.hash || "").slice(1), one = blds.some(function (x) { return x.id === h; }) ? h : "all";
      blds.forEach(function (x) { x.hidden = one !== "all" && x.id !== one; });
      sw.querySelectorAll("a").forEach(function (a) { a.setAttribute("aria-current", String(a.dataset.go === one)); });
    };
    window.addEventListener("hashchange", showBld); showBld();
  }

  // Sections below the fold rise in once; anything already on screen at load is left alone
  if ("IntersectionObserver" in window && !REDUCE.matches) {
    var seen = new Map(), vh = window.innerHeight;
    var io = new IntersectionObserver(function (en) {
      en.forEach(function (x) {
        if (!x.isIntersecting) return;
        var el = x.target; io.unobserve(el);
        el.classList.add("rv-in"); requestAnimationFrame(function () { el.classList.remove("rv-wait"); });
        el.addEventListener("transitionend", function done() { el.classList.remove("rv-in"); el.style.removeProperty("--rd"); el.removeEventListener("transitionend", done); });
      });
    }, { rootMargin: "0px 0px -8% 0px" });
    document.querySelectorAll("main .section-head, main .door, main .step, main .program, main .fact, main .faq, main .bld, main .link-list > a, .cta-band .wrap > *").forEach(function (el) {
      if (el.getBoundingClientRect().top < vh) return;
      var n = seen.get(el.parentElement) || 0; seen.set(el.parentElement, n + 1);
      el.style.setProperty("--rd", Math.min(n, 4) * 70 + "ms"); el.classList.add("rv-wait"); io.observe(el);
    });
  }

  // Mobile menu: a panel under the header with a scrim; closes on scrim, Escape, link tap or resize
  var btn = document.querySelector(".menu-btn"), nav = document.getElementById("site-nav"), scrim = document.querySelector(".scrim");
  var mq = window.matchMedia("(max-width: 1060px)");
  function setMenu(open) {
    if (!btn || !nav) return;
    nav.classList.toggle("open", open);
    btn.setAttribute("aria-expanded", String(open));
    document.body.classList.toggle("menu-open", open);
    if (scrim) {
      if (open) { scrim.hidden = false; requestAnimationFrame(function () { scrim.classList.add("on"); }); }
      else { scrim.classList.remove("on"); setTimeout(function () { if (!nav.classList.contains("open")) scrim.hidden = true; }, 200); }
    }
    if (actionBar) syncBar();
  }
  if (btn && nav) {
    btn.addEventListener("click", function () { setMenu(!nav.classList.contains("open")); });
    nav.addEventListener("click", function (e) { if (e.target.closest("a")) setMenu(false); });
    if (scrim) scrim.addEventListener("click", function () { setMenu(false); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && nav.classList.contains("open")) { setMenu(false); btn.focus(); } });
    (mq.addEventListener ? mq.addEventListener("change", function () { if (!mq.matches) setMenu(false); }) : null);
  }

  // Phone action bar: appears once the first section's buttons have scrolled away, hides over the footer
  var actionBar = document.querySelector(".action-bar");
  var pastHero = false, atFoot = false;
  function syncBar() { actionBar.classList.toggle("on", pastHero && !atFoot && !(nav && nav.classList.contains("open"))); }
  if (actionBar && "IntersectionObserver" in window) {
    var hero = document.querySelector("main > section"), foot = document.querySelector(".site-foot");
    if (hero) new IntersectionObserver(function (en) { pastHero = !en[0].isIntersecting; syncBar(); }, { rootMargin: "-25% 0px 0px 0px" }).observe(hero);
    if (foot) new IntersectionObserver(function (en) { atFoot = en[0].isIntersecting; syncBar(); }).observe(foot);
  }

  // Booking links: use the booking page when configured
  function wireBooking(scope) {
    if (!CFG.BOOKING_URL) return;
    scope.querySelectorAll("[data-book]").forEach(function (a) {
      a.setAttribute("href", CFG.BOOKING_URL); a.setAttribute("target", "_blank"); a.setAttribute("rel", "noopener");
    });
  }
  wireBooking(document);

  // Tier cards (phones): the segmented control follows the swipe 1:1; tapping a tier scrolls to it
  document.querySelectorAll("[data-tiers]").forEach(function (box) {
    var track = box.querySelector(".tc-track"), thumb = box.querySelector(".seg-thumb"), tabs = [].slice.call(box.querySelectorAll('[role="tab"]'));
    var cards = track.children, n = cards.length, frame = 0, cur = 0;
    function update() {
      frame = 0;
      var max = track.scrollWidth - track.clientWidth;
      var p = max > 0 ? Math.min(1, Math.max(0, track.scrollLeft / max)) * (n - 1) : 0;
      thumb.style.transform = "translateX(" + (p * 100) + "%)";
      var i = Math.round(p);
      if (i !== cur) { cur = i; tabs.forEach(function (t, j) { t.setAttribute("aria-selected", String(j === i)); }); }
    }
    track.addEventListener("scroll", function () { if (!frame) frame = requestAnimationFrame(update); }, { passive: true });
    tabs.forEach(function (t, j) {
      t.addEventListener("click", function () {
        track.scrollTo({ left: cards[j].offsetLeft - track.firstElementChild.offsetLeft, behavior: REDUCE.matches ? "auto" : "smooth" });
      });
    });
    window.addEventListener("resize", update);
    update();
  });

  // FAQ: answers expand and collapse instead of snapping
  document.querySelectorAll(".faq details").forEach(function (d) {
    var sum = d.querySelector("summary"), body = d.querySelector(".faq-a"), anim = null;
    if (!sum || !body || !body.animate) return;
    sum.addEventListener("click", function (e) {
      if (REDUCE.matches) return;
      e.preventDefault();
      var opening = !d.open || d.dataset.closing === "1";
      var from = body.getBoundingClientRect().height;
      if (anim) anim.cancel();
      if (opening) { d.dataset.closing = ""; d.open = true; }
      var to = opening ? body.scrollHeight : 0;
      if (!opening) d.dataset.closing = "1";
      anim = body.animate([{ height: from + "px", opacity: opening ? (from ? 1 : 0) : 1 }, { height: to + "px", opacity: opening ? 1 : 0 }],
        { duration: opening ? 240 : 180, easing: EASE_OUT });
      anim.onfinish = function () { anim = null; if (!opening) { d.open = false; d.dataset.closing = ""; } };
    });
  });

  // Forms
  function msg(form, kind, text) {
    var m = form.querySelector(".form-msg");
    if (!m) { m = document.createElement("div"); m.setAttribute("role", "status"); form.appendChild(m); }
    m.className = "form-msg " + kind; m.textContent = text;
  }
  function wireForm(form) {
    form.addEventListener("submit", function (e) {
      e.preventDefault();
      if (!form.reportValidity()) return;
      if (form.querySelector(".hp input") && form.querySelector(".hp input").value) return; // spam trap
      if (!CFG.FORM_ENDPOINT) {
        msg(form, "err", "This form isn't connected yet. Please call or email us directly using the details on the contact page.");
        return;
      }
      var b = form.querySelector("[type=submit]"); if (b) { b.disabled = true; b.dataset.label = b.textContent; b.textContent = "Sending…"; }
      fetch(CFG.FORM_ENDPOINT, { method: "POST", body: new FormData(form), headers: { Accept: "application/json" } })
        .then(function (r) {
          if (!r.ok) throw new Error();
          form.reset();
          msg(form, "ok", form.dataset.success || "Sent. We'll reply within one business day.");
          if (window.gtag) window.gtag("event", "generate_lead", { form: form.dataset.name || "contact" });
        })
        .catch(function () { msg(form, "err", "That didn't send. Check your connection and try again, or call or email us."); })
        .finally(function () { if (b) { b.disabled = false; b.textContent = b.dataset.label; } });
    });
  }
  document.querySelectorAll("form[data-form]").forEach(wireForm);

  // ---------------- Obligation Check ----------------
  var root = document.getElementById("quiz");
  if (!root) return;

  var TIERS = window.NCC_TIERS || {};
  var Q = {
    who: { title: "Which describes you best?", options: [
      ["building", "I own or manage a commercial or institutional building", "Offices, plazas, churches, schools, clinics, municipal buildings"],
      ["rental", "I own or manage a rental or condo building", "Landlords with 5+ units, property managers, condominium corporations"],
      ["contractor", "I'm a contractor about to open walls or floors", "Renovators, trades, general contractors, fit-out firms"],
      ["restoration", "I run a fire, flood or mould restoration company", ""],
      ["project", "I have a project coming up and need to know if it needs a DSS", "Renovation, demolition, repair, tender or purchase"],
      ["employer", "My workers use, handle or store a designated substance", ""],
      ["abatement", "I'm an abatement contractor", ""],
      ["homeowner", "I'm a homeowner planning a renovation", ""] ] },
    b_age: { title: "Was the building built before 1990?", help: "Most buildings built after 1980 are largely free of asbestos; nearly everything older is a candidate.", options: [["yes", "Yes, before 1990"], ["no", "No, 1990 or later"], ["unsure", "I'm not sure"]] },
    b_count: { title: "How many buildings do you look after?", options: [["one", "One"], ["two", "Two"], ["many", "Three or more"]] },
    b_board: { title: "Is a board or a joint health and safety committee asking about asbestos?", options: [["yes", "Yes"], ["no", "No"]] },
    b_contractors: { title: "How often are contractors or maintenance staff working in the building?", options: [["often", "Several times a year or more"], ["rarely", "Rarely"]] },
    b_record: { title: "When was your asbestos record last updated?", help: "Owners must re-inspect and update it at least once every 12 months.", options: [["recent", "Within the last 12 months"], ["old", "More than 12 months ago"], ["none", "We don't have one, or I don't know"]] },
    c_jobs: { title: "How many jobs a month are in buildings built before 1990?", options: [["few", "1 to 3 a month"], ["many", "4 or more a month"]] },
    // Project path: does this project need a designated substance survey (OHSA s.30)?
    p_type: { title: "What type of building is it?", options: [["commercial", "Commercial", "Offices, retail, plazas, hotels"], ["institutional", "Institutional", "Schools, healthcare, government, churches"], ["industrial", "Industrial", "Plants, warehouses, shops"], ["multi", "Multi-unit residential", "Apartments, condominiums, townhouse complexes"], ["house", "Single-family home"]] },
    p_age: { title: "Was the building built before 1990?", help: "Age changes what we expect to find, not whether the owner needs a list.", options: [["yes", "Yes, before 1990"], ["no", "No, 1990 or later"], ["unsure", "I'm not sure"]] },
    p_work: { title: "What work is planned?", options: [["demo", "Demolition", "All or part of the building coming down"], ["major", "Major renovation", "Gutting or reconfiguring a floor or wing"], ["minor", "Minor renovation or repair"], ["mep", "Mechanical, electrical or plumbing upgrades"], ["finish", "Flooring or ceiling replacement"], ["due", "Change of ownership or due diligence"], ["know", "I just want to know what's in the building"]] },
    p_disturb: { title: "Will the work disturb any of these?", help: "Pick all that apply.", multi: true, options: [["drywall", "Drywall or plaster"], ["floor", "Floor tiles or mastic"], ["ceiling", "Ceiling tiles"], ["pipe", "Pipe or boiler insulation"], ["roof", "Roofing"], ["exterior", "Exterior cladding or caulking"], ["none", "None of these", "The work won't open, cut or remove building materials"], ["unsure", "I'm not sure"]] },
    p_report: { title: "Is there an existing asbestos or designated substance report?", options: [["recent", "Yes, current and it covers this work area"], ["old", "Yes, but it's old, incomplete or doesn't cover this area"], ["none", "No"], ["unsure", "I'm not sure"]] },
    p_role: { title: "What is your role on this project?", options: [["owner", "Owner"], ["manager", "Property or facility manager"], ["gc", "General contractor"], ["trade", "Trade contractor"], ["other", "Other"]] },
    p_time: { title: "When should the work start?", options: [["month", "Within 1 month"], ["quarter", "In 1 to 3 months"], ["later", "In 3 months or more"], ["planning", "Just planning"]] }
  };
  var FLOW = {
    building: ["b_age", "b_count", "b_board", "b_contractors", "b_record"],
    rental: ["b_age", "b_count", "b_board", "b_contractors", "b_record"],
    contractor: ["c_jobs"],
    project: ["p_type", "p_age", "p_work", "p_disturb", "p_report", "p_role", "p_time"],
    restoration: [], employer: [], abatement: [], homeowner: []
  };
  // Due diligence and "what's in the building" aren't renovation work, so skip the materials question
  function steps(who) {
    return (FLOW[who] || []).filter(function (k) { return !(k === "p_disturb" && (answers.p_work === "due" || answers.p_work === "know")); });
  }

  var answers = {}, path = ["who"], idx = 0, lastIdx = -1;

  // Step transitions: forward steps arrive from the right, Back from the left; progress fills as you go
  function enter(dir) {
    var step = root.firstElementChild, fresh = root.querySelector(".quiz-progress span.fresh");
    var still = !step || !step.animate || REDUCE.matches || dir === 0;
    if (fresh && (still || dir < 0)) fresh.className = "done";
    if (still) return;
    step.animate([{ opacity: 0, transform: "translateX(" + (dir * 14) + "px)" }, { opacity: 1, transform: "none" }], { duration: 240, easing: EASE_OUT });
    if (fresh && dir > 0) {
      var bar = document.createElement("i"); bar.className = "qp-fill"; fresh.appendChild(bar);
      bar.animate([{ transform: "scaleX(0)" }, { transform: "scaleX(1)" }], { duration: 360, delay: 60, easing: EASE_OUT, fill: "both" });
    }
  }

  function route(a) {
    switch (a.who) {
      case "building": case "rental":
        var entry = a.b_record === "none" ? "Baseline survey" : "DSS update";
        if (a.b_count === "many" || a.b_board === "yes") return { tier: "bp_fp", entry: "Discovery call" };
        if (a.b_contractors === "often" || a.b_count === "two") return { tier: "bp_pr", entry: entry };
        return { tier: "bp_ess", entry: entry };
      case "contractor":
        return a.c_jobs === "many" ? { tier: "pw_pro", entry: "First pre-work check" } : { tier: "pw_start", entry: "First pre-work check" };
      case "restoration": return { tier: "pw_rr", entry: "Discovery call" };
      default: return { special: a.who };
    }
  }
  var ENTRY_DESC = {
    "DSS update": "We review your existing report, walk the building and fill any sampling gaps, from $550 plus samples. Sign a program within 30 days and the update is repriced at your member rate.",
    "Baseline survey": "An asbestos building survey becomes your on-site record, from $1,800 plus samples. Sign a program before the work starts and it's priced at your member rate, or sign within 30 days of receiving it and the difference is credited on your first program invoice.",
    "First pre-work check": "One limited sampling visit or project report on your next job in an older building, at the list price (from $650), so you see a report before you commit.",
    "Discovery call": "A 30-minute call to scope your buildings or jobs, followed by a written proposal."
  };

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function total() { return answers.who ? path.length : 3; }
  function picked(key, v) { var a = answers[key]; return Array.isArray(a) ? a.indexOf(v) > -1 : a === v; }

  function renderQ() {
    var key = path[idx], q = Q[key];
    var dir = lastIdx < 0 ? 0 : (idx >= lastIdx ? 1 : -1);
    var bars = ""; for (var i = 0; i < total(); i++) bars += '<span class="' + (i < idx ? (i === idx - 1 && dir > 0 ? "fresh" : "done") : "") + '"></span>';
    root.innerHTML = '<div class="q-step"><div class="quiz-progress" aria-hidden="true">' + bars + '</div>' +
      '<p class="small" style="margin-bottom:8px">Question ' + (idx + 1) + ' of ' + total() + '</p>' +
      '<h2 class="q-title" id="q-title" tabindex="-1">' + esc(q.title) + '</h2>' +
      (q.help ? '<p class="q-help">' + esc(q.help) + '</p>' : "") +
      '<div class="options" role="group" aria-labelledby="q-title">' + q.options.map(function (o) {
        return '<button type="button" class="opt' + (q.multi ? ' multi' : '') + '" data-v="' + o[0] + '" aria-pressed="' + picked(key, o[0]) + '"><span>' + esc(o[1]) + (o[2] ? '<small>' + esc(o[2]) + '</small>' : "") + '</span></button>';
      }).join("") + '</div>' +
      '<div class="quiz-nav">' + (idx > 0 ? '<button type="button" class="linkish" data-back>Back</button>' : "<span></span>") +
      (q.multi ? '<button type="button" class="btn" data-next' + ((answers[key] || []).length ? '' : ' disabled') + '>Continue</button>' : '') + '</div></div>';
    enter(dir); lastIdx = idx;
    var t = document.getElementById("q-title"); if (t && idx > 0) t.focus({ preventScroll: true });
  }

  // ---- Project path: how much work the owner's designated substance list will take ----
  var PRICES = { limited: ["Limited sampling visit", 650], update: ["DSS update or re-assessment", 550], project: ["Project-specific DSS", 1500], survey: ["Asbestos building survey", 1800], full: ["Full-building DSS and hazardous materials survey", 2400], demo: ["Pre-demolition DSS", 3900] };
  // Routing lives in assets/ncc-rules.js (window.NCC_RULES.route), shared with NCC Office's intake so both give the same answer.
  function projectRoute(a) {
    var R = window.NCC_RULES;
    if (!R || !R.route) return { level: 2, report: null };
    var r = R.route({ use: a.p_type, era: { yes: "old", no: "new", unsure: "" }[a.p_age], work: { demo: "demo", major: "major", minor: "minor", mep: "minor", finish: "minor", due: "due", know: "know" }[a.p_work],
      disturb: a.p_disturb || [], report: { recent: "current", old: "old", none: "none", unsure: "unsure" }[a.p_report] });
    return { level: r.level, report: r.key === "predemo" ? "demo" : r.key };
  }
  var LEVEL = {
    1: ["A designated substance survey is needed before this project starts", "Nothing on file covers work that will open up this building. The list has to be made by sampling the materials the work will disturb."],
    2: ["Start with a targeted check or a review of what you have", "Some of what we'd need to know is missing or out of date. A targeted check of the work area, or a review of your existing report, settles it."],
    3: ["Your existing information may already cover this", "Confirm that your report is current and covers the work area, and that it goes to the contractor before the contract is signed."],
    "3n": ["This one should be simple", "A newer building and work that won't open up building materials usually means a short list. The owner still needs one before the work starts, and it has to reach the contractor before a contract is signed."],
    survey: ["A building survey answers that", "A purchase or a general question isn't a project, so section 30 doesn't apply yet. A survey tells you what's in the building and becomes the list when work is planned."]
  };
  var ROLE = {
    owner: "As the owner, the list is your duty. If a contractor later finds a substance you ought to have known about, you can be liable for their losses.",
    manager: "Do the project list and your yearly O. Reg. 278/05 re-inspection together, and keep your asbestos management program current.",
    gc: "Get the owner's list before you price the job. It's what protects you from stop-work orders and change-order disputes when something turns up behind a wall.",
    trade: "If you work in older buildings every month, the <a href=\"contractors.html\">Cleared-to-Start Pass</a> gives you a compliance desk to call before you bid or cut."
  };
  function projectHtml(a) {
    var r = projectRoute(a), L = LEVEL[r.level === 3 && a.p_report !== "recent" ? "3n" : r.level], out = [];
    out.push('<div class="rec"><span class="small">Your result</span><span class="t">' + esc(L[0]) + '</span><p>' + esc(L[1]) + '</p>');
    if (r.level !== "survey") out.push('<p class="small">Under OHSA section 30, before any project starts the owner must find out which designated substances are present and give the list to the contractor before a contract is signed. It applies whatever the building\u2019s age or the job\u2019s size; what changes is how much work it takes.</p>');
    if (r.report) { var P = PRICES[r.report]; out.push('<span class="p">' + esc(P[0]) + ': from $' + P[1].toLocaleString("en-CA") + ' <span class="small">CAD before HST, plus samples</span></span><p class="small"><a href="services.html">See the report menu and how samples are priced</a></p>'); }
    else if (r.level === "survey") out.push('<span class="p">Asbestos building survey from $1,800, or all designated substances from $2,400 <span class="small">CAD before HST, plus samples</span></span><p class="small"><a href="services.html">See the report menu</a></p>');
    else out.push('<p class="small">' + (a.p_report === "recent" ? 'Not sure it does? Book a call and have the report handy; we\u2019ll tell you whether it covers the job.' : 'Book a call and we\u2019ll tell you what the list needs to include for this job.') + '</p>');
    out.push('</div>');
    var flags = [];
    if (r.level !== "survey" && a.p_age !== "no") flags.push(["", "In a building built before 1990, assume asbestos-containing materials may be present until sampling shows otherwise."]);
    if (r.level !== "survey" && a.p_age === "no") flags.push(["", "Newer buildings still need a list. Silica is in almost all concrete and masonry, and lead, mercury and other substances turn up in buildings of every age."]);
    if (a.p_work === "demo" && a.p_report === "recent") flags.push(["", "For demolition, the report has to be a destructive pre-demolition survey that opened up walls, floors and ceilings. A regular building survey isn't enough."]);
    if (a.p_time === "month" && r.level !== 3) flags.push(["", "Timing is tight. A project report takes about 8 to 10 business days after the site visit, including the lab\u2019s 5 business days, and we don\u2019t offer rush analysis. Book the visit now."]);
    var role = ROLE[a.p_role];
    return { html: out.join("") + flags.map(function (f) { return '<p class="flag ' + f[0] + '">' + esc(f[1]) + '</p>'; }).join("") + (role && r.level !== "survey" ? '<p>' + role + '</p>' : ''),
      text: { 1: "Project: survey needed", 2: "Project: targeted check", 3: "Project: may be covered", survey: "Project: building survey" }[r.level] + (r.report ? " (" + PRICES[r.report][0] + ")" : "") };
  }
  var DISCLAIMER = '<p class="small disclaimer">This tool provides general guidance only and is not a substitute for a site-specific assessment by a qualified professional. Requirements depend on the specific building, materials and scope of work.</p>';

  function renderResult() {
    var r = route(answers), html = "", proj = r.special === "project" ? projectHtml(answers) : null;
    var flags = [];
    if (answers.b_age === "yes" || answers.b_age === "unsure") flags.push(["", "In a pre-1990 building, assume asbestos-containing materials may be present. Owners must identify them, keep a record on site and re-inspect at least every 12 months."]);
    if (answers.b_record === "old") flags.push(["", "Your asbestos record is overdue. Owners must update it at least once every 12 months, and a missing or stale record was the most common order in the Ministry's 2023–24 asbestos campaign."]);
    if (answers.b_record === "none") flags.push(["", "No record on file is the gap inspectors find most often. Before any renovation, repair or demolition you'll also need a list of every designated substance in the work area."]);
    if (answers.b_record === "recent") flags.push(["ok", "Good: your record is within the 12-month window. A program keeps it that way and answers “can we drill here?” from the register."]);

    if (proj) {
      html = proj.html +
        '<div class="btn-row"><a class="btn amber" href="contact.html#book" data-book>Book a free 30-minute call</a><a class="btn ghost" href="#quote">Request a quote</a></div>' +
        '<p class="small"><a href="guide-demolition-renovation-dss.html">Read the demolition and renovation DSS checklist</a></p>';
    } else if (r.special === "employer") {
      html = '<div class="rec"><span class="t">Exposure monitoring: not available yet</span><p>O. Reg. 490/09 asks for a written exposure assessment made with your JHSC, and air monitoring where workers may be exposed. Exposure monitoring is not available yet. Call 519-890-9654 to tell us what you need, and we will contact you when it launches.</p><p><a href="guide-designated-substance-self-check.html">Take the one-page self-check</a></p></div>';
    } else if (r.special === "abatement") {
      html = '<div class="rec"><span class="t">One-off services</span><p>We offer surveys, specifications, air monitoring and clearance to abatement contractors job by job. To keep clearance work independent, we don’t sell the Cleared-to-Start Pass to abatement firms, and we don’t clear work our Pass holders abate.</p></div>';
    } else if (r.special === "homeowner") {
      html = '<div class="rec"><span class="t">Limited sampling visit</span><span class="p">From $650</span><p>Homes need testing once per renovation, not a subscription. We sample the materials your work will disturb, priced per sample, and lab results take 5 business days.</p></div>';
    } else {
      var T = TIERS[r.tier];
      var perB = T.program === "Building programs" ? ", per building, priced by size" : "";
      html = '<div class="rec"><span class="small">Recommended for you</span><span class="t">' + esc(T.program) + ': ' + esc(T.name) + '</span><span class="p">' + (T.price ? (perB ? 'From $' : '$') + T.price.toLocaleString("en-CA") + ' a month' : 'Price on request') + ' <span class="small">CAD before HST' + perB + ', 12-month agreement</span></span><p class="small">' + esc(T.fits) + '</p>' +
        '<ul>' + T.inc.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + '</ul>' +
        '<p><a href="' + T.page + '">See the full ' + esc(T.program) + ' comparison</a></p></div>' +
        '<div><h3 style="margin-bottom:6px">Your next step: ' + esc(r.entry) + '</h3><p>' + esc(ENTRY_DESC[r.entry]) + '</p></div>';
    }
    var flagHtml = flags.map(function (f) { return '<p class="flag ' + f[0] + '">' + esc(f[1]) + '</p>'; }).join("");
    var summary = path.map(function (k) {
      var q = Q[k], v = answers[k]; if (!q || v == null) return "";
      var labels = q.options.filter(function (x) { return Array.isArray(v) ? v.indexOf(x[0]) > -1 : x[0] === v; }).map(function (x) { return x[1]; });
      return labels.length ? q.title + " " + labels.join(", ") : "";
    }).filter(Boolean).join(" | ");
    var recText = proj ? proj.text : r.special ? ({ abatement: "One-off services (abatement contractor)", homeowner: "Limited sampling visit (homeowner)", project: "One-off report", employer: "Exposure monitoring (not available yet; notify at launch)" }[r.special] || r.special) : TIERS[r.tier].program + " " + TIERS[r.tier].name + " → " + r.entry;

    root.innerHTML = '<div class="result" id="result" tabindex="-1">' +
      '<div class="print-only print-head"><img src="assets/ncc-logo-online-compact.svg" alt="Noah Crowley Consulting" width="606" height="128"><span>Obligation Check result · ' + new Date().toLocaleDateString("en-CA", { month: "short", day: "numeric", year: "numeric" }) + ' · crowleyconsulting.ca/obligation-check</span></div>' +
      '<h2 class="q-title" style="margin:0">Your Obligation Check result</h2>' + flagHtml + html + DISCLAIMER +
      '<div class="result-actions"><button type="button" class="btn ghost sm" data-save>Save as PDF</button><button type="button" class="btn ghost sm" data-share>Share this result</button></div>' +
      '<form class="form" id="quote" data-form data-name="obligation-check" data-success="Sent. We’ll be in touch within one business day to book your next step.">' +
      '<h3>' + (proj ? 'Request a quote' : 'Send me this result and book the next step') + '</h3>' +
      '<input type="hidden" name="_subject" value="Obligation Check: ' + esc(recText) + '">' +
      '<input type="hidden" name="recommendation" value="' + esc(recText) + '">' +
      '<input type="hidden" name="answers" value="' + esc(summary) + '">' +
      '<div class="row2"><label class="field">Your name<input name="name" required autocomplete="name"></label>' +
      '<label class="field">Company<input name="company" autocomplete="organization"></label></div>' +
      '<div class="row2"><label class="field">Email<input name="email" type="email" required autocomplete="email"></label>' +
      '<label class="field">Phone<input name="phone" type="tel" autocomplete="tel"></label></div>' +
      (proj ? '<label class="field">Project location (city or town)<input name="project_location" required autocomplete="address-level2"></label>' +
        '<label class="field">About the project<textarea name="project_description" placeholder="What work, which floors or areas, and when"></textarea></label>'
      : '<label class="field">Building or site address (optional)<input name="site_address" autocomplete="street-address"></label>') +
      '<label class="check"><input type="checkbox" name="consent_updates" value="yes"> Also send me occasional compliance reminders and updates by email. You can unsubscribe at any time.</label>' +
      '<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website_url" tabindex="-1" autocomplete="off"></label></div>' +
      '<div class="btn-row"><button class="btn" type="submit">' + (proj ? 'Send my request' : 'Send my result') + '</button>' + (proj ? '' : '<a class="btn ghost" href="contact.html#book" data-book>Book a call instead</a>') + '</div>' +
      '<p class="small">We use your details to reply about this request. See our <a href="privacy.html">privacy notice</a>.</p></form>' +
      '<button type="button" class="linkish" data-restart>Start over</button></div>';
    root.dataset.rec = recText;
    var shareBtn = root.querySelector("[data-share]"); if (shareBtn && !navigator.share) shareBtn.textContent = "Copy a link to share";
    wireForm(root.querySelector("form"));
    wireBooking(root);
    enter(lastIdx < 0 ? 0 : 1); lastIdx = -1;
    var res = document.getElementById("result"); res.focus({ preventScroll: true });
    var top = root.getBoundingClientRect().top;
    if (top < 0 || top > window.innerHeight * .6) root.scrollIntoView({ behavior: REDUCE.matches ? "auto" : "smooth", block: "start" });
    if (window.gtag) window.gtag("event", "quiz_complete", { result: recText });
  }

  root.addEventListener("click", function (e) {
    var o = e.target.closest(".opt");
    function next() {
      root.dataset.busy = "1";
      setTimeout(function () { delete root.dataset.busy; if (idx < path.length - 1) { idx++; renderQ(); } else renderResult(); }, REDUCE.matches ? 0 : 140);
    }
    if (o) {
      if (root.dataset.busy) return;
      var key = path[idx], v = o.dataset.v;
      if (Q[key].multi) {
        // Multi-select: "None" and "Not sure" stand alone; anything else clears them
        var cur = (answers[key] || []).slice(), solo = v === "none" || v === "unsure";
        if (cur.indexOf(v) > -1) cur.splice(cur.indexOf(v), 1);
        else cur = solo ? [v] : cur.filter(function (x) { return x !== "none" && x !== "unsure"; }).concat(v);
        answers[key] = cur;
        root.querySelectorAll(".opt").forEach(function (x) { x.setAttribute("aria-pressed", String(cur.indexOf(x.dataset.v) > -1)); });
        root.querySelector("[data-next]").disabled = !cur.length;
        return;
      }
      answers[key] = v;
      root.querySelectorAll(".opt").forEach(function (x) { x.setAttribute("aria-pressed", String(x === o)); });
      if (key === "who") Object.keys(answers).forEach(function (k) { if (k !== "who") delete answers[k]; });
      path = ["who"].concat(steps(answers.who));
      next();
      return;
    }
    if (e.target.closest("[data-next]")) { if (!root.dataset.busy) next(); return; }
    if (e.target.closest("[data-back]")) { idx = Math.max(0, idx - 1); renderQ(); return; }
    if (e.target.closest("[data-save]")) {
      document.documentElement.classList.add("print-result");
      window.addEventListener("afterprint", function off() { document.documentElement.classList.remove("print-result"); window.removeEventListener("afterprint", off); });
      window.print(); return;
    }
    var sh = e.target.closest("[data-share]");
    if (sh) {
      var url = location.origin + location.pathname + (answers.who ? "#" + answers.who : "");
      var text = "My Obligation Check result: " + (root.dataset.rec || "") + ". Take the check yourself:";
      if (navigator.share) { navigator.share({ title: "Obligation Check result", text: text, url: url }).catch(function () {}); return; }
      var done = function () { sh.textContent = "Link copied"; setTimeout(function () { sh.textContent = "Copy a link to share"; }, 1800); };
      if (navigator.clipboard) navigator.clipboard.writeText(text + " " + url).then(done, function () { window.prompt("Copy this link:", url); });
      else window.prompt("Copy this link:", url);
      return;
    }
    if (e.target.closest("[data-restart]")) { answers = {}; path = ["who"]; idx = 0; lastIdx = 1; renderQ(); }
  });

  // Preselect a segment from the link (obligation-check.html#building)
  var pre = (location.hash || "").slice(1);
  if (FLOW[pre]) { answers.who = pre; path = ["who"].concat(steps(pre)); idx = path.length > 1 ? 1 : 0; if (path.length === 1) { renderResult(); return; } }
  renderQ();
})();
