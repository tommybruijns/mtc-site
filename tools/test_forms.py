#!/usr/bin/env python3
"""Headless browser test of both sign-up forms against a local static server. No network: the HubSpot call is intercepted.
Run: python3 tools/test_forms.py [--shots]   (needs playwright + Chromium; --shots refreshes preview/form-*.png)"""
import glob, json, os, pathlib, subprocess, sys, time
from playwright.sync_api import sync_playwright

R = pathlib.Path(__file__).resolve().parent.parent
PORT = 8765
SHOTS = "--shots" in sys.argv
GUID = "11111111-2222-3333-4444-555555555555"
fails = []


def check(name, ok, extra=""):
    print(("PASS " if ok else "FAIL ") + name + (f" {extra}" if extra and not ok else ""))
    if not ok:
        fails.append(name)


srv = subprocess.Popen([sys.executable, "-m", "http.server", str(PORT), "--bind", "127.0.0.1", "--directory", str(R)],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.8)
exe = os.environ.get("CHROME") or glob.glob(os.path.expanduser(
    "~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell"))[-1]
try:
    with sync_playwright() as p:
        b = p.chromium.launch(executable_path=exe)

        def new(w, h):
            c = b.new_context(viewport={"width": w, "height": h}, reduced_motion="reduce")
            pg = c.new_page()
            sent, cookies_set, errors, other = [], [], [], []
            pg.on("pageerror", lambda e: errors.append(str(e)))
            pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

            def hs(route):
                sent.append(json.loads(route.request.post_data))
                route.fulfill(status=200, content_type="application/json", body='{"inlineMessage":"ok"}')
            pg.route("https://api.hsforms.com/**", hs)
            pg.on("request", lambda r: other.append(r.url) if not r.url.startswith(("http://127.0.0.1", "data:")) and "hsforms" not in r.url else None)
            return c, pg, sent, errors, other

        def shot(pg, name):
            if SHOTS:
                pg.screenshot(path=str(R / "preview" / name), full_page=True)

        def fill_common(pg, buyer):
            pg.fill("#fullname", "Anna de Vries")
            pg.fill("#email", "thomas+test@pintl.ai")
            pg.fill("#company", "Test Vastgoed BV")
            pg.check('[name=web_consent_privacy]', force=True)

        # ---------------------------------------------------------------- buyer
        c, pg, sent, errors, other = new(1280, 900)
        pg.goto(f"http://127.0.0.1:{PORT}/aanmelden-koper.html")
        pg.evaluate(f"window.__mtcForms.CFG.forms.buyer='{GUID}'")
        shot(pg, "form-buyer-desktop.png")
        pg.click("#send")
        n_err = pg.locator(".err:not([hidden])").count()
        check("buyer: empty submit shows errors, sends nothing", n_err >= 7 and not sent, n_err)
        check("buyer: summary error shown", pg.locator("#formerr").is_visible())
        shot(pg, "form-buyer-errors.png")
        fill_common(pg, True)
        pg.fill("#jobtitle", "Acquisitiemanager")
        pg.fill("#email", "anna@gmail.com")
        pg.check('[name=web_types][value="kantoren"]', force=True)
        pg.check('[name=web_regions][value="Utrecht (stad)"]', force=True)
        pg.check('[name=web_regions][value="Amsterdam"]', force=True)
        pg.fill("#web_ticket_min", "5.000.000"); pg.fill("#web_ticket_max", "2.000.000")
        pg.check('[name=web_financing][value="zonder financieringsvoorbehoud"]', force=True)
        pg.click("#send")
        txt = pg.locator('[data-field=email] .err').inner_text()
        check("buyer: freemail refused", "zakelijke" in txt, txt)
        check("buyer: ticket range refused", "maximum" in pg.locator('[data-field=web_ticket_max] .err').inner_text())
        check("buyer: fee consent required", pg.locator('[data-field=web_consent_fee] .err').is_visible())
        pg.click("#lang")
        check("buyer: error text follows EN toggle", "business email" in pg.locator('[data-field=email] .err').inner_text())
        pg.click("#lang")
        pg.fill("#email", "thomas+test@pintl.ai"); pg.fill("#web_ticket_max", "8.000.000")
        pg.check('[name=web_consent_fee]', force=True)
        pg.fill("#web_message", "Kantoren 2-5M Utrecht")
        pg.fill("#phone", "+31 6 12345678"); pg.fill("#web_kvk", "42007902")
        pg.wait_for_timeout(4200)
        shot(pg, "form-buyer-filled.png")
        pg.click("#send")
        pg.wait_for_selector("#thanks:not([hidden])")
        check("buyer: thank-you shown, form hidden", pg.locator("#signup").is_hidden() and pg.locator("#thanks").is_visible())
        check("buyer: exactly one HubSpot post", len(sent) == 1, len(sent))
        f = {x["name"]: x["value"] for x in sent[0]["fields"]} if sent else {}
        check("buyer: payload mapped", f.get("email") == "thomas+test@pintl.ai" and f.get("firstname") == "Anna" and f.get("lastname") == "de Vries"
              and f.get("web_types") == "kantoren" and f.get("web_regions") == "Amsterdam;Utrecht (stad)" and f.get("web_ticket_min") == "5000000"
              and f.get("web_ticket_max") == "8000000" and f.get("web_financing") == "zonder financieringsvoorbehoud"
              and f.get("web_form") == "buyer" and f.get("web_consent_privacy") == "ja" and f.get("web_consent_fee") == "ja", f)
        check("buyer: no hutk / cookie in context", "hutk" not in json.dumps(sent[0]) if sent else False)
        check("buyer: no cookies set", c.cookies() == [], c.cookies())
        check("buyer: no third-party requests", not other, other)
        check("buyer: no console errors", not errors, errors)
        shot(pg, "form-buyer-thanks.png")
        c.close()

        # honeypot + timing
        c, pg, sent, errors, other = new(1280, 900)
        pg.goto(f"http://127.0.0.1:{PORT}/aanmelden-koper.html")
        pg.evaluate(f"window.__mtcForms.CFG.forms.buyer='{GUID}'")
        fill_common(pg, True); pg.fill("#jobtitle", "X")
        pg.check('[name=web_types][value="kantoren"]', force=True); pg.check('[name=web_regions][value="Amsterdam"]', force=True)
        pg.fill("#web_ticket_min", "1"); pg.fill("#web_ticket_max", "2")
        pg.check('[name=web_financing][value="eigen vermogen"]', force=True); pg.check('[name=web_consent_fee]', force=True)
        pg.click("#send")
        pg.wait_for_selector("#thanks:not([hidden])")
        check("anti-spam: too-fast submit looks fine to a bot but sends nothing", not sent)
        pg.goto(f"http://127.0.0.1:{PORT}/aanmelden-koper.html")
        pg.evaluate(f"window.__mtcForms.CFG.forms.buyer='{GUID}'")
        fill_common(pg, True); pg.fill("#jobtitle", "X")
        pg.check('[name=web_types][value="kantoren"]', force=True); pg.check('[name=web_regions][value="Amsterdam"]', force=True)
        pg.fill("#web_ticket_min", "1"); pg.fill("#web_ticket_max", "2")
        pg.check('[name=web_financing][value="eigen vermogen"]', force=True); pg.check('[name=web_consent_fee]', force=True)
        pg.evaluate("document.querySelector('[name=website_url]').value='http://spam.example'")
        pg.wait_for_timeout(4200); pg.click("#send")
        pg.wait_for_selector("#thanks:not([hidden])")
        check("anti-spam: honeypot filled sends nothing", not sent)
        # unconfigured GUID
        pg.goto(f"http://127.0.0.1:{PORT}/aanmelden-koper.html")
        fill_common(pg, True); pg.fill("#jobtitle", "X")
        pg.check('[name=web_types][value="kantoren"]', force=True); pg.check('[name=web_regions][value="Amsterdam"]', force=True)
        pg.fill("#web_ticket_min", "1"); pg.fill("#web_ticket_max", "2")
        pg.check('[name=web_financing][value="eigen vermogen"]', force=True); pg.check('[name=web_consent_fee]', force=True)
        pg.wait_for_timeout(4200); pg.click("#send")
        check("unconfigured form says so and sends nothing", pg.locator("#formerr").is_visible() and "niet actief" in pg.locator("#formerr").inner_text() and not sent)
        c.close()

        # server error keeps the data
        c, pg, sent, errors, other = new(1280, 900)
        pg.unroute("https://api.hsforms.com/**")
        pg.route("https://api.hsforms.com/**", lambda r: r.fulfill(status=500, body="x"))
        pg.goto(f"http://127.0.0.1:{PORT}/aanmelden-koper.html")
        pg.evaluate(f"window.__mtcForms.CFG.forms.buyer='{GUID}'")
        fill_common(pg, True); pg.fill("#jobtitle", "X")
        pg.check('[name=web_types][value="kantoren"]', force=True); pg.check('[name=web_regions][value="Amsterdam"]', force=True)
        pg.fill("#web_ticket_min", "1"); pg.fill("#web_ticket_max", "2")
        pg.check('[name=web_financing][value="eigen vermogen"]', force=True); pg.check('[name=web_consent_fee]', force=True)
        pg.wait_for_timeout(4200); pg.click("#send")
        pg.wait_for_selector("#formerr:not([hidden])")
        check("server error: message shown, data kept, button usable", pg.input_value("#company") == "Test Vastgoed BV" and pg.locator("#send").is_enabled())
        c.close()

        # ---------------------------------------------------------------- seller
        c, pg, sent, errors, other = new(1280, 900)
        pg.goto(f"http://127.0.0.1:{PORT}/object-aanbieden.html")
        pg.evaluate(f"window.__mtcForms.CFG.forms.seller='{GUID}'")
        shot(pg, "form-seller-desktop.png")
        pg.click("#send")
        check("seller: empty submit shows errors", pg.locator(".err:not([hidden])").count() >= 9 and not sent)
        pg.check('[name=web_seller_role][value="makelaar"]', force=True)
        pg.fill("#company", "Makelaar BV"); pg.fill("#fullname", "Jan Jansen"); pg.fill("#email", "jan@makelaar.nl")
        pg.check('[name=web_object_type][value="kantoor"]', force=True)
        pg.fill("#web_city", "Utrecht"); pg.fill("#web_price", "2.500.000"); pg.fill("#web_m2", "1.800")
        pg.check('[name=web_occupancy][value="verhuurd"]', force=True)
        pg.fill("#web_deadline", "2020-01-01")
        pg.check('[name=web_consent_privacy]', force=True)
        pg.click("#send")
        check("seller: past deadline refused", pg.locator('[data-field=web_deadline] .err').is_visible())
        pg.fill("#web_deadline", "2099-12-31"); pg.fill("#web_address", "Stationsstraat 1")
        pg.wait_for_timeout(4200)
        shot(pg, "form-seller-filled.png")
        pg.click("#send")
        pg.wait_for_selector("#thanks:not([hidden])")
        f = {x["name"]: x["value"] for x in sent[0]["fields"]} if sent else {}
        check("seller: payload mapped", f.get("web_seller_role") == "makelaar" and f.get("web_object_type") == "kantoor" and f.get("web_city") == "Utrecht"
              and f.get("web_price") == "2500000" and f.get("web_m2") == "1800" and f.get("web_occupancy") == "verhuurd"
              and f.get("web_deadline") == "2099-12-31" and f.get("web_form") == "seller" and f.get("web_address") == "Stationsstraat 1", f)
        check("seller: no console errors / third parties", not errors and not other, (errors, other))
        shot(pg, "form-seller-thanks.png")
        c.close()

        # ---------------------------------------------------------------- phone widths + overflow, both languages
        for page_ in ("aanmelden-koper.html", "object-aanbieden.html"):
            c, pg, *_ = new(390, 844)
            pg.goto(f"http://127.0.0.1:{PORT}/{page_}")
            for lang in ("nl", "en"):
                over = pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                vis = pg.evaluate("[...document.querySelectorAll('[lang-en]')].filter(e=>e.offsetParent&&getComputedStyle(e).display!='none').length")
                vis_nl = pg.evaluate("[...document.querySelectorAll('[lang-nl]')].filter(e=>e.offsetParent&&getComputedStyle(e).display!='none').length")
                check(f"{page_} phone {lang}: no horizontal scroll", over <= 0, over)
                check(f"{page_} phone {lang}: only one language visible", (vis == 0) if lang == "nl" else (vis_nl == 0), (vis, vis_nl))
                tag = "buyer" if "koper" in page_ else "seller"
                shot(pg, f"form-{tag}-phone{'' if lang == 'nl' else '-en'}.png")
                pg.click("#lang")
            c.close()
        # existing pages still fine
        c, pg, sent, errors, other = new(1280, 900)
        pg.goto(f"http://127.0.0.1:{PORT}/index.html")
        hrefs = pg.evaluate("[...document.querySelectorAll('a.btn.primary,a.btn.ghost,a.btn.ghost-d')].map(a=>a.getAttribute('href'))")
        check("index: sign-up buttons link to the forms", all(h in ("object-aanbieden.html", "aanmelden-koper.html") or h in ("thomas-bruijns.vcf", "MTC-Real-Estate-profiel.pdf") for h in hrefs), hrefs)
        check("index: no console errors", not errors, errors)
        c.close()
        b.close()
finally:
    srv.terminate(); srv.wait()
print("FAILED: " + ", ".join(fails) if fails else "ALL PASS")
sys.exit(1 if fails else 0)
