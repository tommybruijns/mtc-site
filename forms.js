/* MTC sign-up forms. Plain JS, no cookies, no trackers. Posts once to the HubSpot Forms submission API
   (no embed script, no hutk cookie). Until the two form GUIDs below are filled in, the forms show the e-mail fallback. */
(function () {
  "use strict";
  var CFG = {
    portal: "149514484",
    forms: { buyer: "REPLACE_WITH_BUYER_FORM_GUID", seller: "REPLACE_WITH_SELLER_FORM_GUID" },
    endpoint: "https://api.hsforms.com/submissions/v3/integration/submit/",
    minSeconds: 4,          // a human needs longer than this to fill the form
    timeoutMs: 15000
  };
  var FREEMAIL = ["gmail.com", "googlemail.com", "hotmail.com", "hotmail.nl", "outlook.com", "outlook.nl", "live.nl", "live.com",
    "yahoo.com", "yahoo.nl", "icloud.com", "me.com", "ziggo.nl", "kpnmail.nl", "planet.nl", "home.nl", "hetnet.nl", "xs4all.nl",
    "casema.nl", "upcmail.nl", "telfort.nl", "msn.com", "proton.me", "protonmail.com"];
  var M = {
    nl: { req: "Dit veld is verplicht.", pick: "Kies minimaal één optie.", email: "Vul een geldig e-mailadres in.",
      free: "Gebruik uw zakelijke e-mailadres (geen Gmail, Hotmail e.d.).", phone: "Vul een geldig telefoonnummer in.",
      num: "Vul een bedrag of aantal in, alleen cijfers.", range: "Het maximum moet gelijk zijn aan of hoger dan het minimum.",
      consent: "Dit akkoord is nodig om door te gaan.", kvk: "Een KvK-nummer heeft 8 cijfers.", date: "Kies een datum vanaf vandaag.",
      fail: "Verzenden is niet gelukt. Uw gegevens staan nog in het formulier. Probeer het zo nog eens, of mail ons.",
      off: "Dit formulier is nog niet actief. Mail ons gerust.", fix: "Controleer de gemarkeerde velden.", sending: "Bezig met verzenden..." },
    en: { req: "This field is required.", pick: "Choose at least one option.", email: "Enter a valid email address.",
      free: "Please use your business email address (no Gmail, Hotmail etc.).", phone: "Enter a valid phone number.",
      num: "Enter an amount or number, digits only.", range: "The maximum must be equal to or higher than the minimum.",
      consent: "This consent is needed to continue.", kvk: "A KvK number has 8 digits.", date: "Pick a date from today.",
      fail: "Sending failed. Your details are still in the form. Try again shortly, or email us.",
      off: "This form is not active yet. Please email us.", fix: "Please check the marked fields.", sending: "Sending..." }
  };
  var form = document.getElementById("signup");
  if (!form) { return; }
  var kind = form.getAttribute("data-kind");
  var shown = Date.now();
  var root = document.documentElement;
  function lang() { return root.getAttribute("data-lang") === "en" ? "en" : "nl"; }
  function msg(k) { return M[lang()][k]; }
  function q(sel, ctx) { return (ctx || form).querySelector(sel); }
  function qa(sel, ctx) { return Array.prototype.slice.call((ctx || form).querySelectorAll(sel)); }

  function num(s) {                    // Dutch notation: 2.500.000 or 2.500.000,50 or "EUR 2,5"
    var c = String(s || "").replace(/[^\d.,]/g, "");
    if (!c) { return null; }
    c = c.replace(/\./g, "").replace(",", ".");
    var n = Number(c);
    return isFinite(n) && n >= 0 ? n : null;
  }
  function val(name) { var e = q('[name="' + name + '"]'); return e ? e.value.trim() : ""; }
  function checked(name) { return qa('[name="' + name + '"]:checked').map(function (e) { return e.value; }); }

  function setErr(wrap, text) {
    if (!wrap) { return; }
    var p = q(".err", wrap);
    wrap.classList.toggle("bad", !!text);
    var inp = q("input,textarea", wrap);
    if (inp && inp.type !== "radio" && inp.type !== "checkbox") { inp.setAttribute("aria-invalid", text ? "true" : "false"); }
    if (p) { p.textContent = text || ""; p.hidden = !text; }
    if (!text && !qa(".bad").length) { var fe = document.getElementById("formerr"); if (fe) { fe.hidden = true; } }
  }
  function wrapOf(name) { return q('[data-field="' + name + '"]'); }

  function validate() {
    var bad = [], d = {};
    function fail(name, k) { setErr(wrapOf(name), msg(k)); bad.push(name); }
    qa("[data-field]").forEach(function (w) { setErr(w, ""); });
    qa(".field:not(.group):not(.consent) input[required], .field:not(.group) textarea[required]").forEach(function (e) {
      if (!e.value.trim()) { fail(e.name, "req"); }
    });
    qa("fieldset.group[data-required]").forEach(function (f) {
      var n = f.getAttribute("data-field");
      if (!checked(n).length) { fail(n, "pick"); }
    });
    qa(".consent input[required]").forEach(function (e) { if (!e.checked) { fail(e.name, "consent"); } });
    var em = val("email").toLowerCase();
    if (em && bad.indexOf("email") < 0) {
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(em)) { fail("email", "email"); }
      else if (FREEMAIL.indexOf(em.split("@")[1]) >= 0) { fail("email", "free"); }
    }
    var ph = val("phone");
    if (ph && !/^[+()\d][\d\s()+\-.]{5,24}$/.test(ph)) { fail("phone", "phone"); }
    var kvk = val("web_kvk");
    if (kvk && !/^\d{8}$/.test(kvk.replace(/\s/g, ""))) { fail("web_kvk", "kvk"); }
    ["web_ticket_min", "web_ticket_max", "web_price", "web_m2"].forEach(function (n) {
      if (q('[name="' + n + '"]') && val(n) && bad.indexOf(n) < 0 && num(val(n)) === null) { fail(n, "num"); }
    });
    if (kind === "buyer" && bad.indexOf("web_ticket_min") < 0 && bad.indexOf("web_ticket_max") < 0 &&
        num(val("web_ticket_min")) > num(val("web_ticket_max"))) { fail("web_ticket_max", "range"); }
    var dl = val("web_deadline");
    if (dl && dl < new Date().toISOString().slice(0, 10)) { fail("web_deadline", "date"); }
    return bad;
  }

  function fields() {
    var f = [];
    function add(name, value) { if (value !== "" && value !== null && value !== undefined) { f.push({ objectTypeId: "0-1", name: name, value: String(value) }); } }
    var full = val("fullname").replace(/\s+/g, " ");
    var i = full.indexOf(" ");
    add("firstname", i < 0 ? full : full.slice(0, i));
    add("lastname", i < 0 ? "-" : full.slice(i + 1));
    ["email", "phone", "company", "jobtitle", "web_kvk", "web_financing", "web_message", "web_city", "web_address",
      "web_seller_role", "web_object_type", "web_occupancy", "web_deadline"].forEach(function (n) {
      if (q('[name="' + n + '"]')) {
        var el = qa('[name="' + n + '"]')[0];
        add(n, el.type === "radio" ? (checked(n)[0] || "") : (n === "email" ? val(n).toLowerCase() : n === "web_kvk" ? val(n).replace(/\s/g, "") : val(n)));
      }
    });
    ["web_ticket_min", "web_ticket_max", "web_price", "web_m2"].forEach(function (n) {
      if (q('[name="' + n + '"]')) { add(n, num(val(n))); }
    });
    ["web_types", "web_regions"].forEach(function (n) { if (q('[name="' + n + '"]')) { add(n, checked(n).join(";")); } });
    add("web_form", kind);
    add("web_lang", lang());
    add("web_consent_privacy", checked("web_consent_privacy").length ? "ja" : "");
    if (kind === "buyer") { add("web_consent_fee", checked("web_consent_fee").length ? "ja" : ""); }
    return f;
  }

  function guid() { var g = CFG.forms[kind]; return /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(g || "") ? g : null; }
  function formErr(text) { var e = document.getElementById("formerr"); e.textContent = text || ""; e.hidden = !text; }
  function done() {
    form.hidden = true;
    var t = document.getElementById("thanks");
    t.hidden = false;
    t.focus();
    try { window.scrollTo({ top: Math.max(0, t.getBoundingClientRect().top + window.pageYOffset - 100), behavior: "smooth" }); } catch (e) { /* ignore */ }
  }

  qa("input,textarea").forEach(function (e) {      // clear a field's error as soon as it is edited
    e.addEventListener("input", function () { var w = e.closest("[data-field]"); if (w && w.classList.contains("bad")) { setErr(w, ""); } });
    e.addEventListener("change", function () { var w = e.closest("[data-field]"); if (w && w.classList.contains("bad")) { setErr(w, ""); } });
  });

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    formErr("");
    var bad = validate();
    if (bad.length) {
      formErr(msg("fix"));
      var first = wrapOf(bad[0]);
      var focus = first && q("input,textarea", first);
      if (focus) { focus.focus(); }
      return;
    }
    var hp = val("website_url");
    if (hp || (Date.now() - shown) / 1000 < CFG.minSeconds) { done(); return; }     // bot: pretend success, send nothing
    var g = guid();
    if (!g) { formErr(msg("off")); return; }
    var btn = document.getElementById("send");
    var label = btn.innerHTML;
    btn.disabled = true;
    btn.textContent = msg("sending");
    var ctl = "AbortController" in window ? new AbortController() : null;
    var timer = setTimeout(function () { if (ctl) { ctl.abort(); } }, CFG.timeoutMs);
    var body = JSON.stringify({ fields: fields(), context: { pageUri: location.href.split("#")[0], pageName: document.title } });
    fetch(CFG.endpoint + CFG.portal + "/" + g, {
      method: "POST", headers: { "Content-Type": "application/json" }, body: body,
      credentials: "omit", cache: "no-store", signal: ctl ? ctl.signal : undefined
    }).then(function (r) {
      clearTimeout(timer);
      if (r.ok) { done(); return; }
      throw new Error("http " + r.status);
    }).catch(function () {
      clearTimeout(timer);
      btn.disabled = false;
      btn.innerHTML = label;
      formErr(msg("fail"));
    });
  });

  document.addEventListener("mtc-lang", function () {          // re-render visible messages in the new language
    if (!form.hidden && qa(".bad").length) { validate(); formErr(msg("fix")); }
  });
  window.__mtcForms = { num: num, CFG: CFG };
})();
