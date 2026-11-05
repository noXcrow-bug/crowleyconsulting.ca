/* Noah Crowley Consulting — menu, forms, booking links and the Obligation Check */
(function () {
  var CFG = window.NCC_CONFIG || {};

  var REDUCE = window.matchMedia("(prefers-reduced-motion: reduce)");
  var EASE_OUT = "cubic-bezier(0.23, 1, 0.32, 1)";

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
      ["project", "I just need a report for one project", "Renovation, tender, purchase or demolition permit"],
      ["employer", "My workers use, handle or store a designated substance", ""],
      ["abatement", "I'm an abatement contractor", ""],
      ["homeowner", "I'm a homeowner planning a renovation", ""] ] },
    b_age: { title: "Was the building built before 1990?", help: "Most buildings built after 1980 are largely free of asbestos; nearly everything older is a candidate.", options: [["yes", "Yes, before 1990"], ["no", "No, 1990 or later"], ["unsure", "I'm not sure"]] },
    b_count: { title: "How many buildings do you look after?", options: [["one", "One"], ["two", "Two"], ["many", "Three or more"]] },
    b_board: { title: "Is a board or a joint health and safety committee asking about asbestos?", options: [["yes", "Yes"], ["no", "No"]] },
    b_contractors: { title: "How often are contractors or maintenance staff working in the building?", options: [["often", "Several times a year or more"], ["rarely", "Rarely"]] },
    b_record: { title: "When was your asbestos record last updated?", help: "Owners must re-inspect and update it at least once every 12 months.", options: [["recent", "Within the last 12 months"], ["old", "More than 12 months ago"], ["none", "We don't have one, or I don't know"]] },
    c_jobs: { title: "How many jobs a month are in buildings built before 1990?", options: [["few", "1 to 3 a month"], ["many", "4 or more a month"]] }
  };
  var FLOW = {
    building: ["b_age", "b_count", "b_board", "b_contractors", "b_record"],
    rental: ["b_age", "b_count", "b_board", "b_contractors", "b_record"],
    contractor: ["c_jobs"],
    restoration: [], project: [], employer: [], abatement: [], homeowner: []
  };

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
    "Baseline survey": "An asbestos building survey becomes your on-site record, from $1,800 plus samples. Commit to a 12-month program before the work starts and the survey is 15% off.",
    "First pre-work check": "One limited sampling visit or project report on your next job in an older building, at the list price (from $650), so you see a report before you commit.",
    "Discovery call": "A 30-minute call to scope your buildings or jobs, followed by a written proposal."
  };

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }
  function total() { return 1 + (FLOW[answers.who] ? FLOW[answers.who].length : 3); }

  function renderQ() {
    var key = path[idx], q = Q[key];
    var dir = lastIdx < 0 ? 0 : (idx >= lastIdx ? 1 : -1);
    var bars = ""; for (var i = 0; i < total(); i++) bars += '<span class="' + (i < idx ? (i === idx - 1 && dir > 0 ? "fresh" : "done") : "") + '"></span>';
    root.innerHTML = '<div class="q-step"><div class="quiz-progress" aria-hidden="true">' + bars + '</div>' +
      '<p class="small" style="margin-bottom:8px">Question ' + (idx + 1) + ' of ' + total() + '</p>' +
      '<h2 class="q-title" id="q-title" tabindex="-1">' + esc(q.title) + '</h2>' +
      (q.help ? '<p class="q-help">' + esc(q.help) + '</p>' : "") +
      '<div class="options" role="group" aria-labelledby="q-title">' + q.options.map(function (o) {
        return '<button type="button" class="opt" data-v="' + o[0] + '" aria-pressed="' + (answers[key] === o[0]) + '"><span>' + esc(o[1]) + (o[2] ? '<small>' + esc(o[2]) + '</small>' : "") + '</span></button>';
      }).join("") + '</div>' +
      '<div class="quiz-nav">' + (idx > 0 ? '<button type="button" class="linkish" data-back>Back</button>' : "<span></span>") + '</div></div>';
    enter(dir); lastIdx = idx;
    var t = document.getElementById("q-title"); if (t && idx > 0) t.focus({ preventScroll: true });
  }

  function renderResult() {
    var r = route(answers), html = "";
    var flags = [];
    if (answers.b_age === "yes" || answers.b_age === "unsure") flags.push(["", "In a pre-1990 building, assume asbestos-containing materials may be present. Owners must identify them, keep a record on site and re-inspect at least every 12 months."]);
    if (answers.b_record === "old") flags.push(["", "Your asbestos record is overdue. Owners must update it at least once every 12 months, and a missing or stale record was the most common order in the Ministry's 2023–24 asbestos campaign."]);
    if (answers.b_record === "none") flags.push(["", "No record on file is the gap inspectors find most often. Before any renovation, repair or demolition you'll also need a list of every designated substance in the work area."]);
    if (answers.b_record === "recent") flags.push(["ok", "Good: your record is within the 12-month window. A program keeps it that way and answers “can we drill here?” from the register."]);

    if (r.special === "project") {
      html = '<div class="rec"><span class="t">A report for your project</span><span class="p">From $650</span><p>A limited sampling visit for one to three materials starts at $650; a project-specific designated substance report for a whole work area starts at $1,500. Each report is priced as a report fee plus the samples taken, with lab analysis of the first layer of each sample included. Lab results take 5 business days.</p><p><a href="services.html">See the report menu</a></p></div>';
    } else if (r.special === "employer") {
      html = '<div class="rec"><span class="t">Exposure monitoring, quoted per job</span><p>O. Reg. 490/09 asks for a written exposure assessment made with your JHSC, and air monitoring where workers may be exposed. We offer exposure monitoring as a one-off service and quote each job in writing.</p><p><a href="guide-designated-substance-self-check.html">Take the one-page self-check</a></p></div>';
    } else if (r.special === "abatement") {
      html = '<div class="rec"><span class="t">One-off services</span><p>We offer surveys, specifications, air monitoring and clearance to abatement contractors job by job. To keep clearance work independent, we don’t sell the Cleared-to-Start Pass to abatement firms, and we don’t clear work our Pass holders abate.</p></div>';
    } else if (r.special === "homeowner") {
      html = '<div class="rec"><span class="t">Limited sampling visit</span><span class="p">From $650</span><p>Homes need testing once per renovation, not a subscription. We sample the materials your work will disturb, lab analysis included, and lab results take 5 business days.</p></div>';
    } else {
      var T = TIERS[r.tier];
      var perB = T.program === "Building programs" ? ", per building, priced by size" : "";
      html = '<div class="rec"><span class="small">Recommended for you</span><span class="t">' + esc(T.program) + ': ' + esc(T.name) + '</span><span class="p">' + (T.price ? (perB ? 'From $' : '$') + T.price.toLocaleString("en-CA") + ' a month' : 'Price on request') + ' <span class="small">CAD before HST' + perB + ', 12-month agreement</span></span><p class="small">' + esc(T.fits) + '</p>' +
        '<ul>' + T.inc.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + '</ul>' +
        '<p><a href="' + T.page + '">See the full ' + esc(T.program) + ' comparison</a></p></div>' +
        '<div><h3 style="margin-bottom:6px">Your next step: ' + esc(r.entry) + '</h3><p>' + esc(ENTRY_DESC[r.entry]) + '</p></div>';
    }
    var flagHtml = flags.map(function (f) { return '<p class="flag ' + f[0] + '">' + esc(f[1]) + '</p>'; }).join("");
    var summary = Object.keys(answers).map(function (k) {
      var q = Q[k], o = q && q.options.filter(function (x) { return x[0] === answers[k]; })[0];
      return q && o ? q.title + " " + o[1] : "";
    }).filter(Boolean).join(" | ");
    var recText = r.special ? ({ abatement: "One-off services (abatement contractor)", homeowner: "Limited sampling visit (homeowner)", project: "One-off report", employer: "Exposure monitoring quote" }[r.special] || r.special) : TIERS[r.tier].program + " " + TIERS[r.tier].name + " → " + r.entry;

    root.innerHTML = '<div class="result" id="result" tabindex="-1">' +
      '<h2 class="q-title" style="margin:0">Your Obligation Check result</h2>' + flagHtml + html +
      '<form class="form" data-form data-name="obligation-check" data-success="Sent. We’ll be in touch within one business day to book your next step.">' +
      '<h3>Send me this result and book the next step</h3>' +
      '<input type="hidden" name="_subject" value="Obligation Check: ' + esc(recText) + '">' +
      '<input type="hidden" name="recommendation" value="' + esc(recText) + '">' +
      '<input type="hidden" name="answers" value="' + esc(summary) + '">' +
      '<div class="row2"><label class="field">Your name<input name="name" required autocomplete="name"></label>' +
      '<label class="field">Company<input name="company" autocomplete="organization"></label></div>' +
      '<div class="row2"><label class="field">Email<input name="email" type="email" required autocomplete="email"></label>' +
      '<label class="field">Phone<input name="phone" type="tel" autocomplete="tel"></label></div>' +
      '<label class="field">Building or site address (optional)<input name="site_address" autocomplete="street-address"></label>' +
      '<label class="check"><input type="checkbox" name="consent_updates" value="yes"> Also send me occasional compliance reminders and updates by email. You can unsubscribe at any time.</label>' +
      '<div class="hp" aria-hidden="true"><label>Leave this empty<input name="website_url" tabindex="-1" autocomplete="off"></label></div>' +
      '<div class="btn-row"><button class="btn" type="submit">Send my result</button><a class="btn ghost" href="contact.html#book" data-book>Book a call instead</a></div>' +
      '<p class="small">We use your details to reply about this request. See our <a href="privacy.html">privacy notice</a>.</p></form>' +
      '<button type="button" class="linkish" data-restart>Start over</button></div>';
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
    if (o) {
      if (root.dataset.busy) return;
      var key = path[idx]; answers[key] = o.dataset.v;
      root.querySelectorAll(".opt").forEach(function (x) { x.setAttribute("aria-pressed", String(x === o)); });
      if (key === "who") { Object.keys(answers).forEach(function (k) { if (k !== "who") delete answers[k]; }); path = ["who"].concat(FLOW[answers.who]); }
      root.dataset.busy = "1";
      setTimeout(function () { delete root.dataset.busy; if (idx < path.length - 1) { idx++; renderQ(); } else renderResult(); }, REDUCE.matches ? 0 : 140);
      return;
    }
    if (e.target.closest("[data-back]")) { idx = Math.max(0, idx - 1); renderQ(); return; }
    if (e.target.closest("[data-restart]")) { answers = {}; path = ["who"]; idx = 0; lastIdx = 1; renderQ(); }
  });

  // Preselect a segment from the link (obligation-check.html#building)
  var pre = (location.hash || "").slice(1);
  if (FLOW[pre]) { answers.who = pre; path = ["who"].concat(FLOW[pre]); idx = path.length > 1 ? 1 : 0; if (path.length === 1) { renderResult(); return; } }
  renderQ();
})();
