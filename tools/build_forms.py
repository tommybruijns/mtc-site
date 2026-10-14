#!/usr/bin/env python3
"""Generates aanmelden-koper.html and object-aanbieden.html (same header/footer/design as the other pages).
Run: python3 tools/build_forms.py   (stdlib only; the pages are committed, this is the single source of the markup)."""
import html
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
E = html.escape


def t(nl, en, tag="span"):
    return f'<{tag} lang-nl>{nl}</{tag}><{tag} lang-en lang="en">{en}</{tag}>'


def label(nl, en, name, req=True, hint=None):
    star = '<span class="req" aria-hidden="true">*</span>' if req else f'<span class="opt">{t("optioneel", "optional")}</span>'
    h = f'<small class="hint">{t(*hint)}</small>' if hint else ""
    return f'<label for="{name}">{t(nl, en)} {star}</label>{h}'


def text(nl, en, name, req=True, typ="text", ac=None, maxlen=120, hint=None, mode=None, ph=None):
    a = f' autocomplete="{ac}"' if ac else ""
    m = f' inputmode="{mode}"' if mode else ""
    r = " required" if req else ""
    p = f' placeholder="{ph}"' if ph else ""
    return (f'<div class="field" data-field="{name}">{label(nl, en, name, req, hint)}'
            f'<input id="{name}" name="{name}" type="{typ}" maxlength="{maxlen}"{a}{m}{r}{p}>'
            f'<p class="err" role="alert" hidden></p></div>')


def chips(nl, en, name, kind, opts, req=True, hint=None, cls=""):
    """opts: list of (value, nl, en). kind = checkbox | radio."""
    items = "".join(
        f'<label class="chip"><input type="{kind}" name="{name}" value="{E(v)}"><span>{t(n, e) if n != e else n}</span></label>'
        for v, n, e in opts)
    star = '<span class="req" aria-hidden="true">*</span>' if req else f'<span class="opt">{t("optioneel", "optional")}</span>'
    h = f'<small class="hint">{t(*hint)}</small>' if hint else ""
    return (f'<fieldset class="field group" data-field="{name}" data-kind="{kind}"{" data-required" if req else ""}>'
            f'<legend>{t(nl, en)} {star}</legend>{h}<div class="chips {cls}">{items}</div>'
            f'<p class="err" role="alert" hidden></p></fieldset>')


def area(nl, en, name, req=False, maxlen=2000, hint=None):
    return (f'<div class="field" data-field="{name}">{label(nl, en, name, req, hint)}'
            f'<textarea id="{name}" name="{name}" rows="5" maxlength="{maxlen}"></textarea>'
            f'<p class="err" role="alert" hidden></p></div>')


def consent(name, nl, en):
    return (f'<div class="field consent" data-field="{name}"><label class="check"><input type="checkbox" name="{name}" value="ja" required>'
            f'<span>{t(nl, en)} <span class="req" aria-hidden="true">*</span></span></label>'
            f'<p class="err" role="alert" hidden></p></div>')


PRIVACY_NL = 'Ik ga akkoord met de <a href="privacy.html" target="_blank" rel="noopener">privacyverklaring</a>.'
PRIVACY_EN = 'I agree to the <a href="privacy.html" target="_blank" rel="noopener">privacy statement</a>.'

BUYER = "".join([
    '<div class="fgrid">', text("Bedrijfsnaam", "Company name", "company", ac="organization"),
    text("KvK-nummer", "Chamber of Commerce (KvK) number", "web_kvk", False, maxlen=12, mode="numeric"), '</div>',
    '<div class="fgrid">', text("Contactpersoon", "Contact name", "fullname", ac="name"),
    text("Functie", "Role", "jobtitle", ac="organization-title"), '</div>',
    '<div class="fgrid">', text("Zakelijk e-mailadres", "Business email", "email", typ="email", ac="email", maxlen=120),
    text("Telefoon", "Phone", "phone", False, typ="tel", ac="tel", maxlen=25), '</div>',
    chips("Wat zoekt u?", "What are you looking for?", "web_types", "checkbox", [
        ("kantoren", "Kantoren", "Offices"), ("transformatie", "Transformatie", "Transformation"),
        ("ontwikkeling", "Ontwikkeling", "Development"),
        ("verhuurd beleggingsvastgoed", "Verhuurd beleggingsvastgoed", "Let investment property"),
        ("woonblokken", "Woonblokken", "Residential blocks")]),
    chips("Regio", "Region", "web_regions", "checkbox", [
        ("Heel Randstad", "Heel Randstad", "Entire Randstad"),
        ("Noord-Holland", "Noord-Holland", "Noord-Holland"), ("Zuid-Holland", "Zuid-Holland", "Zuid-Holland"),
        ("Provincie Utrecht", "Provincie Utrecht", "Province of Utrecht"), ("Flevoland", "Flevoland", "Flevoland"),
        ("Amsterdam", "Amsterdam", "Amsterdam"), ("Rotterdam", "Rotterdam", "Rotterdam"), ("Den Haag", "Den Haag", "Den Haag"),
        ("Utrecht (stad)", "Utrecht (stad)", "Utrecht (city)"), ("Haarlem", "Haarlem", "Haarlem"), ("Almere", "Almere", "Almere"),
        ("Amersfoort", "Amersfoort", "Amersfoort"), ("Leiden", "Leiden", "Leiden"), ("Dordrecht", "Dordrecht", "Dordrecht"),
        ("Zoetermeer", "Zoetermeer", "Zoetermeer")], hint=("Meerdere keuzes mogelijk.", "Multiple choices possible.")),
    '<div class="fgrid">',
    text("Ticket van (€)", "Ticket from (€)", "web_ticket_min", mode="numeric", maxlen=14, ph="500.000"),
    text("Ticket tot (€)", "Ticket up to (€)", "web_ticket_max", mode="numeric", maxlen=14, ph="5.000.000"), '</div>',
    chips("Financiering", "Financing", "web_financing", "radio", [
        ("eigen vermogen", "Eigen vermogen", "Equity"),
        ("zonder financieringsvoorbehoud", "Zonder financieringsvoorbehoud", "No financing condition"),
        ("met financiering", "Met financiering", "With financing")]),
    area("Toelichting", "Notes", "web_message", hint=("Bijvoorbeeld rendement, huurders, tijdlijn.", "For example yield, tenants, timeline.")),
    consent("web_consent_privacy", PRIVACY_NL, PRIVACY_EN),
    consent("web_consent_fee", "Ik begrijp dat MTC per object een vergoeding afspreekt voordat adressen worden gedeeld.",
            "I understand that MTC agrees a fee per property before addresses are shared."),
])

SELLER = "".join([
    chips("Uw rol", "Your role", "web_seller_role", "radio", [
        ("eigenaar", "Eigenaar", "Owner"), ("makelaar", "Makelaar", "Broker"), ("curator", "Curator", "Curator"),
        ("vereffenaar", "Vereffenaar", "Liquidator"), ("anders", "Anders", "Other")]),
    '<div class="fgrid">', text("Bedrijf", "Company", "company", ac="organization"),
    text("Contactpersoon", "Contact name", "fullname", ac="name"), '</div>',
    '<div class="fgrid">', text("Zakelijk e-mailadres", "Business email", "email", typ="email", ac="email", maxlen=120),
    text("Telefoon", "Phone", "phone", False, typ="tel", ac="tel", maxlen=25), '</div>',
    chips("Type object", "Property type", "web_object_type", "radio", [
        ("kantoor", "Kantoor", "Office"), ("transformatie", "Transformatie", "Transformation"),
        ("ontwikkellocatie", "Ontwikkellocatie", "Development site"),
        ("verhuurd beleggingsobject", "Verhuurd beleggingsobject", "Let investment property"),
        ("woonblok", "Woonblok", "Residential block"), ("anders", "Anders", "Other")]),
    '<div class="fgrid">', text("Plaats", "City", "web_city", ac="address-level2", maxlen=60),
    text("Adres", "Address", "web_address", False, ac="street-address", maxlen=120,
         hint=("Alleen als u dat al wilt delen; wij delen het nooit zonder uw akkoord.", "Only if you want to share it now; we never share it without your consent.")), '</div>',
    '<div class="fgrid">',
    text("Indicatieve prijs (€)", "Indicative price (€)", "web_price", mode="numeric", maxlen=14, ph="2.500.000"),
    text("Oppervlakte (m²)", "Floor area (m²)", "web_m2", mode="numeric", maxlen=9, ph="1.800"), '</div>',
    chips("Verhuurd of leeg", "Let or vacant", "web_occupancy", "radio", [
        ("verhuurd", "Verhuurd", "Let"), ("leeg", "Leeg", "Vacant"), ("deels verhuurd", "Deels verhuurd", "Partly let")]),
    '<div class="field" data-field="web_deadline">' + label("Uiterste verkoopdatum", "Sale deadline", "web_deadline", False,
                                                           ("Laat leeg als er geen deadline is.", "Leave empty if there is no deadline.")) +
    '<input id="web_deadline" name="web_deadline" type="date"><p class="err" role="alert" hidden></p></div>',
    area("Toelichting", "Notes", "web_message", hint=("Huurders, huurinkomsten, bijzonderheden. Geen bijlagen: die vragen wij later.", "Tenants, rent, specifics. No attachments: we ask for those later.")),
    consent("web_consent_privacy", PRIVACY_NL, PRIVACY_EN),
])

PAGES = {
    "aanmelden-koper.html": dict(
        kind="buyer", title="Aanmelden als koper | MTC Real Estate", nav="beleggers",
        desc="Meld u aan als professionele koper en ontvang off-market commercieel vastgoed in de Randstad dat past bij uw zoekprofiel.",
        h1=("Aanmelden als koper", "Register as a buyer"),
        lead=("Professionele beleggers en ontwikkelaars ontvangen off-market aanbod dat past bij hun zoekprofiel. Wij beoordelen elke aanmelding zelf voordat u iets van ons hoort.",
              "Professional investors and developers receive off-market supply that fits their buy box. We review every registration ourselves before you hear from us."),
        body=BUYER, subject="Aanmelden%20als%20koper%20-%20MTC%20Real%20Estate", btn=("Aanmelden", "Register"),
        thanks=("Bedankt voor uw aanmelding", "Thank you for registering"),
        thanks_p=("Wij hebben uw gegevens ontvangen en beoordelen ze persoonlijk. U hoort van ons zodra er passend aanbod is. Er wordt niets automatisch naar u verstuurd.",
                  "We have received your details and review them personally. You will hear from us when suitable supply comes up. Nothing is sent to you automatically.")),
    "object-aanbieden.html": dict(
        kind="seller", title="Object aanbieden | MTC Real Estate", nav="verkopers",
        desc="Biedt uw commercieel vastgoed discreet en off-market aan bij een beperkte kring van beproefde kopers.",
        h1=("Object aanbieden", "Submit a property"),
        lead=("Een korte aanmelding is genoeg. Wij nemen persoonlijk contact met u op en bevestigen beschikbaarheid altijd eerst met u. Uw object blijft buiten de openbare markt.",
              "A short submission is enough. We contact you personally and always confirm availability with you first. Your property stays off the public market."),
        body=SELLER, subject="Object%20aanbieden%20-%20MTC%20Real%20Estate", btn=("Object aanbieden", "Submit property"),
        thanks=("Bedankt voor uw aanbod", "Thank you for your submission"),
        thanks_p=("Wij hebben uw gegevens ontvangen en nemen persoonlijk contact met u op. Adresgegevens delen wij nooit zonder uw akkoord.",
                  "We have received your details and will contact you personally. We never share address details without your consent.")),
}

HEAD = """<!doctype html>
<html lang="nl" data-lang="nl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; connect-src https://api.hsforms.com; form-action 'self'; base-uri 'self'">
<meta name="referrer" content="strict-origin-when-cross-origin">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#0b1d33">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="canonical" href="https://mtcrealestateinfo.com/{slug}">
<link rel="stylesheet" href="styles.css">
</head>
<body>
<a class="skip" href="#main">Naar inhoud</a>
<header class="top"><div class="wrap">
<a class="brand" href="index.html" aria-label="MTC Real Estate"><span class="mono" aria-hidden="true">MTC</span><span class="bname">Real Estate</span></a>
<nav aria-label="Hoofdmenu">
<a href="index.html#verkopers"><span lang-nl>Verkopers</span><span lang-en lang="en">Sellers</span></a>
<a href="index.html#beleggers"><span lang-nl>Beleggers</span><span lang-en lang="en">Investors</span></a>
<a href="index.html#werkwijze"><span lang-nl>Werkwijze</span><span lang-en lang="en">How it works</span></a>
<a href="index.html#vergoeding"><span lang-nl>Vergoeding</span><span lang-en lang="en">Fee</span></a>
<a href="index.html#contact">Contact</a>
</nav>
<button class="lang" id="lang" type="button" aria-label="Taal / Language">EN</button>
</div></header>
"""

MAIN = """<main id="main"><section class="formpage"><div class="wrap narrow">
<p class="eyebrow dark"><span lang-nl>Off-market · Randstad</span><span lang-en lang="en">Off-market · Randstad</span></p>
<h1>{h1}</h1>
<p class="lead-d">{lead}</p>
<div class="formcard">
<form id="signup" data-kind="{kind}" novalidate>
<p class="req-note"><span class="req" aria-hidden="true">*</span> {reqnote}</p>
{body}
<div class="hp" aria-hidden="true"><label>Website <input type="text" name="website_url" tabindex="-1" autocomplete="off"></label></div>
<p class="formerr" id="formerr" role="alert" hidden></p>
<div class="submitrow"><button class="btn primary" type="submit" id="send">{btn}</button>
<span class="alt-mail">{altmail}</span></div>
<p class="note small">{privnote}</p>
</form>
<div class="thanks" id="thanks" tabindex="-1" role="status" hidden>
<span class="tick-big" aria-hidden="true"></span>
<h2>{thanks}</h2>
<p>{thanks_p}</p>
<p><a class="btn small ghost-d" href="index.html">{back}</a></p>
</div>
</div>
</div></section></main>
<footer><div class="wrap">
<p><strong>MTC Real Estate</strong> · KvK 42007902 · Amsterdam · <span class="ph">[adres]</span> · <a href="mailto:mtc@mtcrealestateinfo.com">mtc@mtcrealestateinfo.com</a></p>
<p lang-nl>Wij verwerken uitsluitend zakelijke contactgegevens. Afmelden kan op elk moment: mail ons. <a href='privacy.html'>Privacyverklaring</a>.</p><p lang-en lang="en">We only process business contact data. Opt out at any time by emailing us. <a href='privacy.html'>Privacy statement</a>.</p>
<p>© 2026 MTC Real Estate</p>
</div></footer>
<script src="site.js"></script>
<script src="forms.js"></script>
</body></html>
"""

for slug, p in PAGES.items():
    mail = f'mailto:mtc@mtcrealestateinfo.com?subject={p["subject"]}'
    out = HEAD.format(title=p["title"], desc=p["desc"], slug=slug) + MAIN.format(
        h1=t(*p["h1"]), lead=t(*p["lead"], tag="span"), kind=p["kind"], body=p["body"], btn=t(*p["btn"]),
        thanks=t(*p["thanks"]), thanks_p=t(*p["thanks_p"], tag="span"),
        back=t("Terug naar home", "Back to home"),
        reqnote=t("verplicht veld", "required field"),
        altmail=t(f'Liever mailen? <a href="{mail}">mtc@mtcrealestateinfo.com</a>', f'Prefer email? <a href="{mail}">mtc@mtcrealestateinfo.com</a>'),
        privnote=t("Wij gebruiken uw gegevens alleen om contact met u op te nemen en u te koppelen aan passend vastgoed. Geen cookies, geen trackers. Zie de <a href=\"privacy.html\">privacyverklaring</a>.",
                   "We only use your details to contact you and match you with suitable property. No cookies, no trackers. See the <a href=\"privacy.html\">privacy statement</a>."))
    (ROOT / slug).write_text(out)
    print("wrote", slug, len(out))
