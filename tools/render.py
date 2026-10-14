# Renders og-image.png, the profile PDF and preview screenshots (needs playwright + Chromium).
import pathlib
from playwright.sync_api import sync_playwright
R=pathlib.Path(__file__).resolve().parent.parent
with sync_playwright() as p:
    import glob,os;b=p.chromium.launch(executable_path=os.environ.get('CHROME') or glob.glob(os.path.expanduser('~/Library/Caches/ms-playwright/chromium_headless_shell-*/chrome-headless-shell-mac-arm64/chrome-headless-shell'))[-1])
    def page(w,h):
        c=b.new_context(viewport={'width':w,'height':h},reduced_motion='reduce'); return c.new_page()
    pg=page(1200,630); pg.goto((R/'tools/og.html').as_uri()); pg.screenshot(path=str(R/'og-image.png'))
    pg.screenshot(path=str(R/'preview/og.png'))
    pg=page(794,1123); pg.goto((R/'tools/profile.html').as_uri()); pg.pdf(path=str(R/'MTC-Real-Estate-profiel.pdf'),width='210mm',height='297mm',print_background=True)
    pg.screenshot(path=str(R/'preview/profile-pdf.png'))
    for name,w,h in (('desktop',1440,900),('phone',390,844)):
        pg=page(w,h); pg.goto((R/'index.html').as_uri()); pg.wait_for_timeout(300)
        pg.screenshot(path=str(R/f'preview/{name}.png'),full_page=True)
        if name=='phone':
            pg.click('#lang'); pg.wait_for_timeout(200); pg.screenshot(path=str(R/'preview/phone-en.png'),full_page=True)
    pg=page(1440,900); pg.goto((R/'privacy.html').as_uri()); pg.screenshot(path=str(R/'preview/privacy.png'),full_page=True)
    b.close()
