# Deploy (nothing is live yet)

Static site: `index.html`, `privacy.html`, `styles.css`. No build step. Before going live, fill the `[adres]` and `[24]` (retention months) placeholders in index.html and privacy.html and in the PDF.

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
