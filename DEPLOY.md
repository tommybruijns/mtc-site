# Deploy (nothing is live yet)

Static site: `index.html`, `privacy.html`, `aanmelden-koper.html`, `object-aanbieden.html`, `styles.css`, `site.js`, `forms.js`. No build step. Before going live, fill the `[adres]` and `[24]` (retention months) placeholders in index.html and privacy.html and in the PDF.

## Before going live: switch the sign-up forms on (once)
The forms post straight from the visitor's browser to the HubSpot Forms API (portal 149514484): no cookies, no embed script, no server of ours, no firewall or port change. Until the two form IDs are filled in, the forms show "not active yet, please email us".
1. HubSpot: add the scope `forms` to the private-app key used on the droplet (Settings > Integrations > Private Apps > Scopes > Marketing > Forms). One scope covers both creating the forms and reading the submissions.
2. On the droplet: `cd /opt/mtc-hubspot && PYTHONPATH=/opt/mtc-hubspot python3 forms_setup.py check` (must say OK), then `... forms_setup.py forms`. It creates the two forms (the contact properties `web_*` already exist), prints the two form IDs and writes `/opt/mtc-flow/forms.json`.
3. Paste the two IDs into `forms.js` (`CFG.forms.buyer` / `CFG.forms.seller`), commit.
4. Fill `[adres]` and `[24]` (retention months) in index.html, privacy.html, the new pages' footers and the PDF; check the privacy statement (HubSpot EU region, Slack notice).
5. Check in HubSpot that the account really is the EU data-centre account (the privacy statement says EU).
From then on the flow (`flow.py website`, every 2 hours with the replies run) files each submission as company + contact + note in HubSpot, posts a #mtc-todo item, and turns an offered object into a lead (source "website"). It never emails the submitter: you reply yourself. A new buyer stays unvetted (no mail from the buyer wave) until you vet it.

## Going live (after your approval)
GitHub Pages plus DNS, nothing else:
- 4 `A` records on the apex `@`: 185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153
- 1 `CNAME` for `www` -> `tommybruijns.github.io`
- Leave every `MX`, SPF, DKIM and DMARC record untouched (Google Workspace mail).
Steps: see Option A below (repo, Pages, `CNAME` file, Enforce HTTPS).

## Test plan after go-live (about 10 minutes, you run it)
1. Open https://mtcrealestateinfo.com/aanmelden-koper.html. Submit one test buyer with `thomas+test-koper@pintl.ai` (company "TEST Koper BV", any type/region/ticket, tick both boxes). Expect the thank-you screen.
2. Open /object-aanbieden.html. Submit one test object with `thomas+test-object@pintl.ai` (city Utrecht, tick the privacy box). Expect the thank-you screen.
3. HubSpot: both contacts exist (search "thomas+test"), the buyer company has role buyer_prospect, source "website", buyer_vetted empty, plus a note with the answers; the seller company has role seller.
4. Slack #mtc-todo: within 2 hours (or run `cd /opt/mtc-flow && python3 flow.py website` on the droplet for an immediate run) two items appear: "New buyer sign-up: TEST Koper BV ..." and "New object offered: ...". Mark them Done.
5. Check no email went out to either test address.
6. Delete: the two test contacts, the two test companies and their notes in HubSpot; the test lead in `/opt/mtc-sourcing-trial/out/website_leads.json` (remove its entry; `leads_all.jsonl` is append-only, so also tell me and I remove that line).
7. Phone check: both forms on your phone, once in Dutch, once in English (EN button).

## Local tests (no network, any time)
`python3 tools/build_forms.py` regenerates the two form pages; `python3 tools/test_forms.py [--shots]` runs the headless-browser tests (validation, anti-spam, payload, no cookies, no third-party requests, phone layout) and refreshes `preview/form-*.png`. Droplet side: `cd ~/code/tommybruijns/ceo && /usr/bin/python3 -m pytest -q tests/test_mtc_website.py`.

## Option A: GitHub Pages (account tommybruijns)
1. New public repo `mtc-site` under tommybruijns, push this folder (main branch).
2. Repo Settings > Pages > Deploy from branch `main`, folder `/ (root)`.
3. Add a file named `CNAME` containing `mtcrealestateinfo.com`, then set Custom domain in Pages and tick Enforce HTTPS once the certificate is issued.
4. DNS at the domain provider (apex site):
   - `A` @ 185.199.108.153
   - `A` @ 185.199.109.153
   - `A` @ 185.199.110.153
   - `A` @ 185.199.111.153
   - `CNAME` www -> tommybruijns.github.io
   (Optional IPv6 `AAAA` @ 2606:50c0:8000::153, 8001::153, 8002::153, 8003::153.)

## Option B: Cloudflare Pages
1. Free Cloudflare account > Workers & Pages > Create > Pages > Direct Upload (drag this folder) or connect the GitHub repo. No build command, output dir `/`.
2. Add custom domain mtcrealestateinfo.com. Easiest: move DNS hosting to Cloudflare (change nameservers at the registrar). Then, BEFORE switching, recreate the existing Google Workspace MX/SPF/DKIM/DMARC records in Cloudflare DNS exactly as they are now.
3. If keeping DNS at the current provider instead: `CNAME` www -> `<project>.pages.dev` and redirect apex to www (apex CNAME needs CNAME flattening, which many providers lack, so Option A is simpler for that case).

## Email safety (Google Workspace)
Do NOT touch, delete or edit any `MX` record, nor the SPF/DKIM/DMARC `TXT` records (e.g. `google._domainkey`, `_dmarc`). Only add the web records above (A/CNAME for @ and www). Check there is no existing A/CNAME on @ or www that must be replaced; replace only those. DNS changes can take up to a few hours.
