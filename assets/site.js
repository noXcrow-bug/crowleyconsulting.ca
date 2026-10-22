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
      ["building", "I own or manage a commercial, industrial or institutional building", "Offices, plants, churches, private schools, municipal buildings"],
      ["rental", "I rent out units or manage a residential building", "Landlords, property managers, condominium corporations"],
      ["employer", "My workers use, handle or store a designated substance", "Paint booths, cutting lines, foundries, labs, sterilization"],
      ["contractor", "I'm a contractor about to open walls or floors", "Renovators, trades, general contractors, fit-out firms"],
      ["restoration", "I run a fire, flood or mould restoration company", ""],
      ["abatement", "I'm an abatement contractor", ""],
      ["homeowner", "I'm a homeowner planning a renovation", ""] ] },
    b_age: { title: "Was the building built before 1990?", help: "Most buildings built after 1980 are largely free of asbestos; nearly everything older is a candidate.", options: [["yes", "Yes, before 1990"], ["no", "No, 1990 or later"], ["unsure", "I'm not sure"]] },
    b_size: { title: "How many buildings do you look after?", options: [["one", "One building", "Up to about 25,000 sq ft"], ["few", "Two or three buildings", "Or up to about 100,000 sq ft"], ["big", "An industrial plant, campus or portfolio", "Planned shutdowns, several large buildings"]] },
    b_staff: { title: "Do you have in-house maintenance staff?", options: [["yes", "Yes"], ["no", "No, we call contractors"]] },
    b_record: { title: "When was your asbestos record last updated?", help: "Owners must re-inspect and update it at least once every 12 months.", options: [["recent", "Within the last 12 months"], ["old", "More than 12 months ago"], ["none", "We don't have one, or I don't know"]] },
    r_units: { title: "How many rental units?", options: [["small", "Fewer than 30"], ["mid", "30 to 150"], ["large", "More than 150"], ["condo", "We're a condominium corporation"]] },
    r_super: { title: "Is there a superintendent or maintenance staff on site?", options: [["yes", "Yes"], ["no", "No"]] },
    e_scope: { title: "How much of your operation involves designated substances?", options: [["shop", "One process", "A paint booth, one cutting line, one sterilizer"], ["plant", "Up to 3 substances or 50 exposed workers", "One site"], ["site", "Several processes or several sites", ""]] },
    e_assess: { title: "Do you have a written exposure assessment done with your JHSC?", options: [["yes", "Yes, and it's current"], ["old", "Yes, but processes have changed since"], ["no", "No, or I'm not sure"]] },
    c_jobs: { title: "How many jobs a month are in buildings built before 1990?", options: [["few", "1 to 3 a month"], ["many", "4 or more a month"]] }
  };
  var FLOW = {
    building: ["b_age", "b_size", "b_staff", "b_record"],
    rental: ["r_units", "r_super", "b_record"],
    employer: ["e_scope", "e_assess"],
    contractor: ["c_jobs"],
    restoration: [], abatement: [], homeowner: []
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
      case "building":
        if (a.b_size === "big") return { tier: "bc_fp", entry: "Discovery call" };
        if (a.b_size === "few" || a.b_staff === "yes") return { tier: "bc_man", entry: "Compliance gap audit" };
        return { tier: "bc_ess", entry: "Compliance gap audit" };
      case "rental":
        if (a.r_units === "large" || a.r_units === "condo") return { tier: "rp_l", entry: "Discovery call" };
        if (a.r_units === "mid" || a.r_super === "yes") return { tier: "rp_m", entry: "First suite check" };
        return { tier: "rp_s", entry: "First suite check" };
      case "employer":
        if (a.e_scope === "site") return { tier: "we_site", entry: "Discovery call" };
        if (a.e_scope === "plant") return { tier: "we_plant", entry: "Exposure gap audit" };
        return { tier: "we_shop", entry: "Exposure gap audit" };
      case "contractor":
        return a.c_jobs === "many" ? { tier: "pw_pro", entry: "First pre-work check" } : { tier: "pw_start", entry: "First pre-work check" };
      case "restoration": return { tier: "pw_rr", entry: "Discovery call" };
      case "abatement": return { special: "abatement" };
      case "homeowner": return { special: "homeowner" };
    }
  }
  var ENTRY_DESC = {
    "Compliance gap audit": "A short paid review of your building against what a Ministry inspector checks. The fee is credited if you join the program.",
    "First suite check": "One suite turnover check on your next unit, so you see the process start to finish. The fee is credited if you join the program.",
    "Exposure gap audit": "A short paid review of your assessment, control program and monitoring records. The fee is credited if you join the program.",
    "First pre-work check": "One pre-work check on your next job in an older building. The fee is credited if you take the Pass.",
    "Discovery call": "A 30-minute call to scope your sites, shutdowns or project calendar, followed by a written proposal."
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
    if (answers.b_record === "recent") flags.push(["ok", "Good: your record is within the 12-month window. The program keeps it that way and answers “can we drill here?” from the register."]);
    if (answers.e_assess === "no") flags.push(["", "O. Reg. 490/09 requires a written exposure assessment made with your joint health and safety committee wherever workers are likely to be exposed."]);
    if (answers.e_assess === "old") flags.push(["", "A change that could significantly affect exposure means the assessment has to be redone."]);

    if (r.special === "abatement") {
      html = '<div class="rec"><span class="t">One-off services</span><p>We offer surveys, specifications, air monitoring and clearance to abatement contractors job by job. To keep clearance work independent, we don’t sell the Cleared-to-Start Pass to abatement firms, and we don’t clear work our Pass holders abate.</p></div>';
    } else if (r.special === "homeowner") {
      html = '<div class="rec"><span class="t">Project designated substance survey</span><span class="p">$550 for one suite or up to 2,000 sq ft</span><p>Homes need testing once per renovation, not a subscription. The survey covers all 11 designated substances in the work area, lab analysis included, with results within 1 week.</p></div>';
    } else {
      var T = TIERS[r.tier];
      html = '<div class="rec"><span class="small">Recommended for you</span><span class="t">' + esc(T.program) + ': ' + esc(T.name) + '</span><span class="p">$' + T.price.toLocaleString("en-CA") + ' a month <span class="small">CAD before HST, 12-month agreement</span></span><p class="small">' + esc(T.fits) + '</p>' +
        '<ul>' + T.inc.map(function (x) { return "<li>" + esc(x) + "</li>"; }).join("") + '</ul>' +
        '<p><a href="' + T.page + '">See the full ' + esc(T.program) + ' comparison</a></p></div>' +
        '<div><h3 style="margin-bottom:6px">Your next step: ' + esc(r.entry) + '</h3><p>' + esc(ENTRY_DESC[r.entry]) + '</p></div>';
    }
    var flagHtml = flags.map(function (f) { return '<p class="flag ' + f[0] + '">' + esc(f[1]) + '</p>'; }).join("");
    var summary = Object.keys(answers).map(function (k) {
      var q = Q[k], o = q && q.options.filter(function (x) { return x[0] === answers[k]; })[0];
      return q && o ? q.title + " " + o[1] : "";
    }).filter(Boolean).join(" | ");
    var recText = r.special ? (r.special === "abatement" ? "One-off services (abatement contractor)" : "Project DSS (homeowner)") : TIERS[r.tier].program + " " + TIERS[r.tier].name + " → " + r.entry;

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
