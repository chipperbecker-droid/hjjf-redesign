"""Builds every page of the redesigned site from content/*.json.

Usage: python3 tools/build.py
Output is written to the repository root so GitHub Pages can serve it as-is.
"""
import html
import json
import os
import re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
C = lambda n: json.load(open(os.path.join(ROOT, 'content', n + '.json'), encoding='utf-8'))

ATTORNEYS = C('attorneys')
PRACTICES = C('practices')
TESTIMONIALS = C('testimonials')
RESOURCES = C('resources')
META = C('meta')
PRIVACY = C('privacy')
DE_PATH = open(os.path.join(ROOT, 'tools', 'delaware-outline.txt')).read().strip()

FIRM = 'Hudson, Jones, Jaywork & Fisher'
SITE_URL = 'https://chipperbecker-droid.github.io/hjjf-redesign/'
FACEBOOK = 'https://www.facebook.com/pages/Hudson-Jones-Jaywork-Fisher/480679735327761'
EMAIL = 'info@delawarelaw.com'

OFFICES = {
    'dover': {
        'name': 'Dover', 'long': 'Dover Office', 'slug': 'dover-office',
        'county': 'Kent County', 'region': 'Kent County and Central Delaware',
        'street': '225 South State Street', 'city': 'Dover, DE 19901',
        'phone': '(302) 734-7401', 'tel': '+13027347401', 'fax': '(302) 734-5532',
        'map': 'https://www.google.com/maps/search/?api=1&query=Hudson%2C%20Jones%2C%20Jaywork%20%26%20Fisher%20225%20South%20State%20Street%20Dover%20DE%2019901',
        'photo': 'assets/img/dover-office', 'photo_w': 1275, 'photo_h': 1020,
        'xy': (117.2, 366.3),
    },
    'rehoboth': {
        'name': 'Rehoboth Beach', 'long': 'Rehoboth Beach Office', 'slug': 'rehoboth-office',
        'county': 'Sussex County', 'region': 'Sussex County and Coastal Delaware',
        'street': '309 Rehoboth Avenue', 'city': 'Rehoboth Beach, DE 19971',
        'phone': '(302) 227-9441', 'tel': '+13022279441', 'fax': '(302) 227-8847',
        'map': 'https://www.google.com/maps/search/?api=1&query=Hudson%2C%20Jones%2C%20Jaywork%20%26%20Fisher%20309%20Rehoboth%20Avenue%20Rehoboth%20Beach%20DE%2019971',
        'photo': 'assets/img/rehoboth-office', 'photo_w': 1200, 'photo_h': 1600,
        'xy': (297.2, 594.7),
    },
}

E = html.escape


def office_keys(a):
    lab = a['office_label']
    keys = []
    if 'Dover' in lab:
        keys.append('dover')
    if 'Rehoboth' in lab:
        keys.append('rehoboth')
    return keys


for a in ATTORNEYS:
    a['offices'] = office_keys(a)
    a['practice_slugs'] = [t['href'].rstrip('/').split('/')[-1] for t in a['tags']]
    # surname for sorting is already the directory order (alphabetical by surname)

PRACTICE_BY_SLUG = {p['slug']: p for p in PRACTICES}
ATTORNEY_BY_SLUG = {a['slug']: a for a in ATTORNEYS}

# Short labels used in tight places (matrix, finder)
SHORT = {
    'real-estate': 'Real Estate',
    'landlord-tenant-law': 'Landlord/Tenant',
    'trusts-wills-estates': 'Trusts, Wills & Estates',
    'alcoholic-beverage-licensing': 'Alcoholic Beverage Licensing',
    'business-law': 'Business Law',
    'civil-litigation': 'Civil Litigation',
    'condominium-homeowners-association-law': 'Condominium & HOA Law',
    'corporations-llcs': 'Corporations & LLCs',
    'domestic-law': 'Domestic Law',
    'municipal-law': 'Municipal Law',
    'personal-injury': 'Personal Injury',
    'registered-agent-service-of-process': 'Registered Agent',
    'zoning-subdivision': 'Zoning & Subdivision',
}

# Extra attorney links for practice areas whose related tag lives under a sibling page.
# Built only from the attorneys' own directory tags and published focus summaries.
TAG_ALIASES = {
    'corporations-llcs': ['business-law'],
    'zoning-subdivision': ['municipal-law'],
}

AUDIENCES = [
    ('ind', 'Individuals & families'),
    ('biz', 'Businesses'),
    ('prop', 'Property owners'),
    ('assoc', 'Associations'),
    ('pub', 'Public bodies'),
]
MATRIX = {
    'real-estate': ['ind', 'biz', 'prop'],
    'landlord-tenant-law': ['ind', 'biz', 'prop'],
    'trusts-wills-estates': ['ind'],
    'alcoholic-beverage-licensing': ['biz'],
    'business-law': ['biz'],
    'civil-litigation': ['ind', 'biz', 'prop', 'assoc'],
    'condominium-homeowners-association-law': ['prop', 'assoc'],
    'corporations-llcs': ['biz'],
    'domestic-law': ['ind'],
    'municipal-law': ['pub'],
    'personal-injury': ['ind'],
    'registered-agent-service-of-process': ['biz'],
    'zoning-subdivision': ['biz', 'prop', 'pub'],
}

FINDER = [
    {'role': 'a homeowner or buyer', 'needs': [
        ('buying or selling a home', 'real-estate'),
        ('refinancing a mortgage', 'real-estate'),
        ('a boundary, easement or title problem', 'real-estate'),
        ('a question about my HOA or condominium', 'condominium-homeowners-association-law'),
    ]},
    {'role': 'planning for my family', 'needs': [
        ('a will, trust or power of attorney', 'trusts-wills-estates'),
        ('settling a loved one’s estate', 'trusts-wills-estates'),
        ('divorce, custody or support', 'domestic-law'),
    ]},
    {'role': 'someone who was injured', 'needs': [
        ('a car accident claim', 'personal-injury'),
        ('an injury on unsafe property', 'personal-injury'),
    ]},
    {'role': 'a landlord or tenant', 'needs': [
        ('a lease or rent dispute', 'landlord-tenant-law'),
        ('a possession action', 'landlord-tenant-law'),
        ('a security deposit question', 'landlord-tenant-law'),
    ]},
    {'role': 'a business owner', 'needs': [
        ('forming an LLC or corporation', 'corporations-llcs'),
        ('contracts or selling a business', 'business-law'),
        ('a dispute that may go to court', 'civil-litigation'),
        ('a Delaware registered agent', 'registered-agent-service-of-process'),
    ]},
    {'role': 'a restaurant or hospitality owner', 'needs': [
        ('a new or transferred liquor license', 'alcoholic-beverage-licensing'),
        ('a hearing before the OABCC', 'alcoholic-beverage-licensing'),
    ]},
    {'role': 'on an association board', 'needs': [
        ('assessments and collections', 'condominium-homeowners-association-law'),
        ('governing documents or DUCIOA', 'condominium-homeowners-association-law'),
    ]},
    {'role': 'with a town or public body', 'needs': [
        ('ordinances, meetings and governance', 'municipal-law'),
        ('zoning, subdivision or land use', 'zoning-subdivision'),
    ]},
    {'role': 'a developer or landowner', 'needs': [
        ('a rezoning, variance or subdivision', 'zoning-subdivision'),
        ('buying or leasing commercial property', 'real-estate'),
    ]},
]


def attorneys_for(slug):
    wanted = [slug] + TAG_ALIASES.get(slug, [])
    direct = [a for a in ATTORNEYS if slug in a['practice_slugs']]
    if direct:
        return direct
    return [a for a in ATTORNEYS if any(s in a['practice_slugs'] for s in wanted)]


# ---------------------------------------------------------------- helpers

def rel(depth):
    return './' if depth == 0 else '../' * depth


def fix(s, depth):
    return s.replace('@/', rel(depth))


def picture(base, depth, alt, w, h, cls='', lazy=True, sizes=None):
    r = rel(depth)
    webp = os.path.exists(os.path.join(ROOT, base + '.webp'))
    src = f'<source type="image/webp" srcset="{r}{base}.webp" />' if webp else ''
    load = 'loading="lazy" ' if lazy else 'fetchpriority="high" '
    c = f' class="{cls}"' if cls else ''
    return (f'<picture{c}>{src}<img {load}decoding="async" src="{r}{base}.jpg" '
            f'alt="{E(alt)}" width="{w}" height="{h}" /></picture>')


def portrait(a, depth, cls='', lazy=True, alt=None):
    return picture(f'assets/attorneys/{a["slug"]}', depth, a['name'] if alt is None else alt,
                   250, 304, cls, lazy)


def office_links(a, depth):
    r = rel(depth)
    return ' &amp; '.join(f'<a href="{r}{OFFICES[k]["slug"]}/">{OFFICES[k]["name"]}</a>'
                          for k in a['offices'])


NAV = [
    ('about', 'About'),
    ('attorneys', 'Attorneys'),
    ('practice-areas', 'Practice Areas'),
    ('links-and-resources', 'FAQ & Resources'),
    ('careers', 'Careers'),
]

FB_ICON = ('<svg aria-hidden="true" viewBox="0 0 24 24" width="16" height="16"><path fill="currentColor" '
           'd="M13.5 21v-7.5h2.5l.4-3h-2.9V8.6c0-.9.3-1.5 1.5-1.5h1.5V4.4c-.3 0-1.2-.1-2.2-.1-2.2 0-3.7 '
           '1.3-3.7 3.8v2.4H8.1v3h2.5V21h2.9z"/></svg>')


def head(title, desc, depth, path, extra=''):
    r = rel(depth)
    canon = SITE_URL + path
    return f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{E(title)}</title>
<meta name="description" content="{E(desc)}" />
<link rel="canonical" href="{canon}" />
<meta property="og:type" content="website" />
<meta property="og:title" content="{E(title)}" />
<meta property="og:description" content="{E(desc)}" />
<meta property="og:url" content="{canon}" />
<meta property="og:image" content="{SITE_URL}assets/social-share.png" />
<meta name="twitter:card" content="summary_large_image" />
<meta name="theme-color" content="#14382f" />
<link rel="icon" href="{r}assets/favicon.ico" sizes="any" />
<link rel="icon" type="image/png" href="{r}assets/favicon.png" />
<link rel="apple-touch-icon" href="{r}assets/apple-touch-icon.png" />
<link rel="preconnect" href="https://fonts.googleapis.com" />
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Libre+Caslon+Display&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&family=Public+Sans:wght@400;500;600;700&display=swap" />
<link rel="stylesheet" href="{r}assets/css/site.css" />
{extra}
</head>'''


def header(depth, active):
    r = rel(depth)
    links = ''.join(
        f'<li><a href="{r}{slug}/"{" aria-current=\"page\"" if slug == active else ""}>{label}</a></li>'
        for slug, label in NAV)
    d, rb = OFFICES['dover'], OFFICES['rehoboth']
    return f'''
<a class="skip" href="#main">Skip to content</a>
<div class="topline">
  <div class="wrap topline-inner">
    <span class="topline-est">Serving Delaware since 1956</span>
    <span class="topline-phones">
      <a href="tel:{d['tel']}"><span class="sc">Dover</span> {d['phone']}</a>
      <a href="tel:{rb['tel']}"><span class="sc">Rehoboth Beach</span> {rb['phone']}</a>
    </span>
  </div>
</div>
<header class="site-header">
  <div class="wrap header-inner">
    <a class="brand" href="{r}" aria-label="{FIRM}, home">
      <img src="{r}assets/logo-balanced.png" alt="{FIRM}, LLC" width="1561" height="162" />
    </a>
    <nav class="primary" aria-label="Primary">
      <ul>{links}<li class="nav-contact"><a href="{r}contact-us/"{" aria-current=\"page\"" if active == 'contact-us' else ""}>Contact</a></li></ul>
    </nav>
    <button class="menu-toggle" type="button" aria-expanded="false" aria-controls="menu-panel">
      <span class="menu-toggle-label">Menu</span><span class="menu-toggle-bars" aria-hidden="true"></span>
    </button>
  </div>
  <div class="menu-panel" id="menu-panel" hidden>
    <div class="wrap">
      <ol class="menu-list">
        <li><a href="{r}">Home</a></li>
        {''.join(f'<li><a href="{r}{s}/">{l}</a></li>' for s, l in NAV)}
        <li><a href="{r}contact-us/">Contact</a></li>
      </ol>
      <div class="menu-phones">
        <a href="tel:{d['tel']}"><span class="label">Dover</span>{d['phone']}</a>
        <a href="tel:{rb['tel']}"><span class="label">Rehoboth Beach</span>{rb['phone']}</a>
      </div>
    </div>
  </div>
</header>'''


def footer(depth):
    r = rel(depth)
    cols = ''
    for k in ('dover', 'rehoboth'):
        o = OFFICES[k]
        cols += f'''
      <div class="foot-office">
        <h2 class="label"><a href="{r}{o['slug']}/">{o['long']}</a></h2>
        <address>{o['street']}<br />{o['city']}</address>
        <p><a class="foot-phone" href="tel:{o['tel']}">{o['phone']}</a><br /><span class="muted">Fax {o['fax']}</span></p>
        <p><a class="arrow-link" href="{o['map']}" target="_blank" rel="noopener">Directions</a></p>
      </div>'''
    pa = ''.join(f'<li><a href="{r}practice-areas/{p["slug"]}/">{E(p["name"])}</a></li>' for p in PRACTICES)
    return f'''
<footer class="site-footer">
  <div class="wrap">
    <div class="foot-top">
      <div class="foot-brand">
        <img src="{r}assets/logo-balanced.png" alt="{FIRM}, LLC" width="1561" height="162" loading="lazy" />
        <p>Professional service on a personal basis, from Dover and Rehoboth Beach since December 31, 1956.</p>
        <a class="social" href="{FACEBOOK}" target="_blank" rel="noopener">{FB_ICON}<span>Facebook</span></a>
      </div>
      {cols}
    </div>
    <div class="foot-index">
      <h2 class="label">Practice areas</h2>
      <ul>{pa}</ul>
    </div>
    <div class="foot-legal">
      <p>Attorney Advertising. This website is for general information only and does not create an attorney-client relationship.</p>
      <p><a href="{r}privacy-policy/">Privacy Policy</a> <span aria-hidden="true">·</span> <a href="{r}contact-us/">Contact</a> <span aria-hidden="true">·</span> © {FIRM}, LLC</p>
    </div>
  </div>
</footer>
<script src="{r}assets/js/site.js" defer></script>
</body>
</html>
'''


def page(path, depth, title, desc, active, body, body_class='', extra_head=''):
    out = head(title, desc, depth, path, extra_head)
    out += f'\n<body class="{body_class}">' + header(depth, active)
    out += f'\n<main id="main">{body}\n</main>' + footer(depth)
    dest = os.path.join(ROOT, path, 'index.html') if path else os.path.join(ROOT, 'index.html')
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, 'w', encoding='utf-8') as fh:
        fh.write(out)


def call_band(depth, heading='Tell us what you need help with.', kicker='Speak with a Delaware attorney'):
    d, rb = OFFICES['dover'], OFFICES['rehoboth']
    r = rel(depth)
    return f'''
<section class="callband" aria-labelledby="callband-h">
  <div class="wrap">
    <p class="kicker">{kicker}</p>
    <h2 id="callband-h" class="callband-h">{heading}</h2>
    <div class="callband-lines">
      <a href="tel:{d['tel']}" class="bigline"><span class="label">Dover</span><span class="num">{d['phone']}</span></a>
      <a href="tel:{rb['tel']}" class="bigline"><span class="label">Rehoboth Beach</span><span class="num">{rb['phone']}</span></a>
    </div>
    <p class="callband-note">Please do not send confidential information until an attorney-client relationship has been established. <a href="{r}contact-us/">All contact details</a></p>
  </div>
</section>'''


def page_head(kicker, title, deck='', crumbs=None, depth=1, extra=''):
    r = rel(depth)
    cr = ''
    if crumbs:
        items = ''.join(f'<li><a href="{r}{h}">{E(l)}</a></li>' for l, h in crumbs)
        cr = f'<nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{r}">Home</a></li>{items}</ol></nav>'
    dk = f'<p class="deck">{deck}</p>' if deck else ''
    return f'''
<header class="page-head">
  <div class="wrap">
    {cr}
    <p class="kicker">{kicker}</p>
    <h1 class="page-title">{title}</h1>
    {dk}
    {extra}
  </div>
</header>'''


def delaware_map(depth, cls='de-map', show_labels=True):
    pins = ''
    for k, o in OFFICES.items():
        x, y = o['xy']
        anchor = 'end' if k == 'rehoboth' else 'start'
        lx = x - 14 if k == 'rehoboth' else x + 14
        ly = y - 14 if k == 'rehoboth' else y + 5
        pins += (f'<g class="pin pin-{k}"><circle cx="{x}" cy="{y}" r="16" class="pin-halo"/>'
                 f'<circle cx="{x}" cy="{y}" r="6" class="pin-dot"/>'
                 + (f'<text x="{lx}" y="{ly}" text-anchor="{anchor}" class="pin-label">{o["name"]}</text>' if show_labels else '')
                 + '</g>')
    towns = [('Wilmington', 108.2, 59.0), ('Georgetown', 173.5, 609.3)]
    tl = ''.join(f'<circle cx="{x}" cy="{y}" r="2.5" class="town"/><text x="{x + 8 if n == "Wilmington" else x - 8}" y="{y + 4}" text-anchor="{"start" if n == "Wilmington" else "end"}" class="town-label">{n}</text>' for n, x, y in towns)
    return f'''<svg class="{cls}" viewBox="0 0 320 744" role="img" aria-label="Map of Delaware showing the Dover and Rehoboth Beach offices">
  <defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="6" class="hatch"/></pattern></defs>
  <path d="{DE_PATH}" class="de-fill"/>
  <path d="{DE_PATH}" class="de-line"/>
  <line x1="10" y1="410" x2="300" y2="410" class="county-hint"/>
  <text x="52" y="300" class="county-label">Kent</text>
  <text x="40" y="520" class="county-label">Sussex</text>
  <text x="306" y="300" class="water-label" text-anchor="end">Delaware Bay</text>
  {tl}{pins}
</svg>'''


# ---------------------------------------------------------------- pages

def build_home():
    depth = 0
    r = rel(depth)
    d, rb = OFFICES['dover'], OFFICES['rehoboth']

    # Two doors
    doors = ''
    for k in ('dover', 'rehoboth'):
        o = OFFICES[k]
        doors += f'''
      <figure class="door door-{k} reveal">
        <a href="{r}{o['slug']}/" class="door-img">{picture(o['photo'], depth, '', o['photo_w'], o['photo_h'], lazy=(k == 'rehoboth'))}</a>
        <figcaption>
          <span class="label">{o['county']}</span>
          <a class="door-name" href="{r}{o['slug']}/">{o['street']}, {o['name']}</a>
          <a class="door-phone" href="tel:{o['tel']}">{o['phone']}</a>
        </figcaption>
      </figure>'''

    # Table of contents
    toc = ''
    for i, p in enumerate(PRACTICES, 1):
        toc += f'''
        <li>
          <a href="{r}practice-areas/{p['slug']}/" data-summary="{E(p['summary'])}" data-num="{i:02d}">
            <span class="toc-num">{i:02d}</span><span class="toc-name">{E(p['name'])}</span><span class="toc-dots" aria-hidden="true"></span><span class="toc-arrow" aria-hidden="true">→</span>
          </a>
          <p class="toc-mobile-summary">{E(p['summary'])}</p>
        </li>'''

    # Roll call
    roll = ''
    for a in ATTORNEYS:
        roll += (f'<li><a href="{r}{a["slug"]}/" data-portrait="{r}assets/attorneys/{a["slug"]}.jpg" '
                 f'data-meta="{E(a["title"])} · {E(a["office_label"])}">{E(a["name"])}</a></li>')
    strip = ''.join(f'<li><a href="{r}{a["slug"]}/">{portrait(a, depth, alt="")}<span>{E(a["name"])}</span></a></li>' for a in ATTORNEYS)

    # Finder
    finder_data = json.dumps([{'role': f['role'], 'needs': [{'label': n, 'slug': s} for n, s in f['needs']]} for f in FINDER])
    practice_data = {}
    for p in PRACTICES:
        practice_data[p['slug']] = {
            'name': p['name'], 'summary': p['summary'], 'url': f'{r}practice-areas/{p["slug"]}/',
            'attorneys': [{'name': a['name'], 'url': f'{r}{a["slug"]}/', 'office': a['office_label']} for a in attorneys_for(p['slug'])],
        }
    role_opts = ''.join(f'<option value="{i}">{E(f["role"])}</option>' for i, f in enumerate(FINDER))
    need_opts = ''.join(f'<option value="{s}">{E(n)}</option>' for n, s in FINDER[0]['needs'])
    first = PRACTICE_BY_SLUG[FINDER[0]['needs'][0][1]]
    first_att = ', '.join(f'<a href="{r}{a["slug"]}/">{E(a["name"])}</a>' for a in attorneys_for(first['slug']))

    # Testimonials
    quotes = ''.join(
        f'<figure class="letter{" is-active" if i == 0 else ""}" data-index="{i}"{"" if i == 0 else " hidden"}>'
        f'<blockquote><p>{E(t["quote"])}</p></blockquote><figcaption>{E(t["name"])}</figcaption></figure>'
        for i, t in enumerate(TESTIMONIALS))

    m = META['index.html']
    body = f'''
<section class="masthead">
  <div class="wrap">
    <p class="dateline"><span>Dover</span><span class="dot" aria-hidden="true">·</span><span>Rehoboth Beach</span><span class="dot" aria-hidden="true">·</span><span>Est. December 31, 1956</span></p>
    <h1 class="masthead-h">Delaware attorneys for families, businesses, property owners, <em>and</em> governmental entities.</h1>
    <div class="masthead-foot">
      <p class="masthead-deck">Practical legal guidance across real estate, landlord-tenant matters, business law, litigation, estates, family matters, personal injury, municipal law, and more.</p>
      <div class="masthead-actions">
        <a class="btn btn-solid" href="{r}contact-us/">Contact the firm</a>
        <a class="btn btn-line" href="#finder">What brings you here?</a>
      </div>
    </div>
  </div>
</section>

<section class="doors" aria-label="Our two offices">
  <div class="wrap doors-inner">{doors}
  </div>
</section>

<section class="ledger" aria-label="The firm at a glance">
  <div class="wrap">
    <dl class="ledger-row">
      <div><dt>Founded</dt><dd>1956</dd></div>
      <div><dt>Offices</dt><dd>Two</dd></div>
      <div><dt>Attorneys</dt><dd>{len(ATTORNEYS)}</dd></div>
      <div><dt>Practice areas</dt><dd>{len(PRACTICES)}</dd></div>
    </dl>
  </div>
</section>

<section class="intro">
  <div class="wrap intro-grid">
    <p class="section-no">No. 01</p>
    <h2 class="intro-h reveal">Professional service on a personal basis.</h2>
    <div class="intro-body reveal">
      <p class="lede">{FIRM} has served Delaware clients since 1956, helping them protect what matters: family, property, business interests, personal rights, and community decisions.</p>
      <p>With offices in Dover and Rehoboth Beach, the firm serves individuals, families, businesses, associations, and governmental entities across Delaware.</p>
      <a class="arrow-link" href="{r}about/">The firm’s story</a>
    </div>
  </div>
</section>

<section class="finder" id="finder" aria-labelledby="finder-h">
  <div class="wrap">
    <p class="section-no light">No. 02</p>
    <h2 id="finder-h" class="finder-kicker">What brings you here?</h2>
    <form class="finder-sentence" onsubmit="return false">
      <span>I am</span>
      <label class="sr-only" for="finder-role">Who you are</label>
      <span class="select-wrap"><select id="finder-role">{role_opts}</select></span>
      <span>and I need help with</span>
      <label class="sr-only" for="finder-need">What you need</label>
      <span class="select-wrap"><select id="finder-need">{need_opts}</select></span><span>.</span>
    </form>
    <div class="finder-answer" aria-live="polite">
      <div class="finder-answer-main">
        <p class="label">Start with</p>
        <a class="finder-practice" href="{r}practice-areas/{first['slug']}/">{E(first['name'])}</a>
        <p class="finder-summary">{E(first['summary'])}</p>
      </div>
      <div class="finder-answer-side">
        <p class="label">Attorneys who handle this</p>
        <p class="finder-attorneys">{first_att or 'Call either office and we will connect you with the right attorney.'}</p>
        <p class="label">Call</p>
        <p class="finder-call"><a href="tel:{d['tel']}">Dover {d['phone']}</a><br /><a href="tel:{rb['tel']}">Rehoboth Beach {rb['phone']}</a></p>
      </div>
    </div>
  </div>
  <script type="application/json" id="finder-data">{finder_data}</script>
  <script type="application/json" id="practice-data">{json.dumps(practice_data)}</script>
</section>

<section class="contents" aria-labelledby="contents-h">
  <div class="wrap contents-grid">
    <div class="contents-head">
      <p class="section-no">No. 03</p>
      <h2 id="contents-h" class="h2">Contents</h2>
      <p class="muted">Thirteen areas of practice, from a first home closing to a town’s zoning code.</p>
      <div class="toc-preview" aria-hidden="true"><span class="toc-preview-num">01</span><p class="toc-preview-text">{E(PRACTICES[0]['summary'])}</p></div>
    </div>
    <ol class="toc">{toc}
    </ol>
  </div>
</section>

<section class="timeline-sec" aria-labelledby="time-h">
  <div class="wrap">
    <p class="section-no">No. 04</p>
    <h2 id="time-h" class="h2">Seven decades on South State Street.</h2>
    {timeline()}
    <a class="arrow-link" href="{r}about/">Read the full history</a>
  </div>
</section>

<section class="rollcall" aria-labelledby="roll-h">
  <div class="wrap">
    <div class="rollcall-head">
      <p class="section-no">No. 05</p>
      <h2 id="roll-h" class="h2">The attorneys</h2>
      <a class="arrow-link" href="{r}attorneys/">Directory</a>
    </div>
    <ul class="roll">{roll}</ul>
    <ul class="roll-strip">{strip}</ul>
  </div>
  <div class="roll-float" aria-hidden="true"><img alt="" width="250" height="304" /><span></span></div>
</section>

<section class="letters" aria-labelledby="letters-h">
  <div class="wrap letters-grid">
    <div class="letters-head">
      <p class="section-no">No. 06</p>
      <h2 id="letters-h" class="h2">Letters from clients</h2>
      <div class="letters-controls">
        <button type="button" class="letters-prev" aria-label="Previous letter">←</button>
        <span class="letters-count"><span class="cur">01</span> / {len(TESTIMONIALS):02d}</span>
        <button type="button" class="letters-next" aria-label="Next letter">→</button>
      </div>
    </div>
    <div class="letters-stage">{quotes}</div>
  </div>
  <div class="wrap"><p class="fine">Client feedback reflects individual experiences. It does not guarantee or predict a similar outcome in any legal matter.</p></div>
</section>

<section class="where" aria-labelledby="where-h">
  <div class="wrap where-grid">
    <div class="where-map">{delaware_map(depth)}</div>
    <div class="where-text">
      <p class="section-no">No. 07</p>
      <h2 id="where-h" class="h2">Two offices, one state.</h2>
      <div class="where-office">
        <p class="label">Kent County</p>
        <h3><a href="{r}dover-office/">Dover</a></h3>
        <p>The Dover office remains at 225 South State Street, close to Delaware courts, government offices, and civic institutions.</p>
        <p class="where-meta"><a href="tel:{d['tel']}">{d['phone']}</a> · <a href="{d['map']}" target="_blank" rel="noopener">Directions</a></p>
      </div>
      <div class="where-office">
        <p class="label">Sussex County</p>
        <h3><a href="{r}rehoboth-office/">Rehoboth Beach</a></h3>
        <p>The Rehoboth Beach office serves clients throughout Sussex County from 309 Rehoboth Avenue in Delaware’s coastal real estate and business corridor.</p>
        <p class="where-meta"><a href="tel:{rb['tel']}">{rb['phone']}</a> · <a href="{rb['map']}" target="_blank" rel="noopener">Directions</a></p>
      </div>
    </div>
  </div>
</section>
{call_band(depth)}'''
    page('', depth, f'Delaware Law Firm | {FIRM}', m['description'], '', body, 'home')


def timeline(full=False):
    items = [
        ('1956', 'December 31', 'The firm is founded when David P. Buckson, later Attorney General and Lt. Governor of Delaware and a Family Court Judge, and George R. Wright, later Deputy Attorney General and Delaware Superior Court Judge, share offices at 225 South State Street in Dover.'),
        ('c. 1960', '', 'William S. Hudson joins them.'),
        ('1977', '', 'The firm becomes Hudson, Jones and Jaywork.'),
        ('Today', '', f'{FIRM}, LLC is one of Southern Delaware’s oldest and largest law firms, with offices in Dover and Rehoboth Beach.'),
    ]
    lis = ''.join(f'<li class="reveal"><p class="tl-year">{y}</p>{f"<p class=tl-sub>{s}</p>" if s else ""}<p class="tl-text">{t}</p></li>' for y, s, t in items)
    return f'<ol class="timeline{" timeline-full" if full else ""}">{lis}</ol>'


def build_about():
    depth = 1
    r = rel(depth)
    m = META['about/index.html']
    letters = ''.join(f'<figure class="col-letter"><blockquote><p>{E(t["quote"])}</p></blockquote><figcaption>{E(t["name"])}</figcaption></figure>' for t in TESTIMONIALS)
    body = page_head('About the firm', 'One of Southern Delaware’s oldest and largest law firms.',
                     f'{FIRM} was founded on December 31, 1956.', depth=depth) + f'''
<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside">
      <p class="section-no">No. 01</p>
      <p class="label">History</p>
    </aside>
    <div class="prose prose-lg">
      <p class="dropcap">{FIRM}, LLC is one of Southern Delaware’s oldest and largest law firms. The firm was founded on December 31, 1956, when David P. Buckson, later Attorney General and Lt. Governor of Delaware and a Family Court Judge, and George R. Wright, later Deputy Attorney General and Delaware Superior Court Judge, shared offices at 225 South State Street in Dover. William S. Hudson joined them around 1960, and the firm later became Hudson, Jones and Jaywork in 1977.</p>
      <p>{FIRM} is a full-service Delaware law firm serving individuals, families, businesses, property owners, associations, and public-sector clients from offices in Dover and Rehoboth Beach.</p>
      <p>The firm provides legal counsel and representation across automobile accidents and other personal injury matters, civil litigation, business law, residential and commercial real estate transactions, municipal and zoning law, domestic relations, creditor relations, wills and estates, and administrative law.</p>
    </div>
  </div>
</section>

<section class="timeline-sec timeline-sec-alt" aria-label="Timeline">
  <div class="wrap">{timeline(True)}</div>
</section>

<section class="pullquote-sec">
  <div class="wrap">
    <blockquote class="pullquote reveal"><p>The practice of law is a service business built on quality work, careful judgment, responsive service, trust, and durable client relationships.</p></blockquote>
  </div>
</section>

<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside">
      <p class="section-no">No. 02</p>
      <p class="label">Billing</p>
    </aside>
    <div>
      <p class="prose-lg">The firm offers a variety of billing arrangements depending on the nature of the matter and client preferences.</p>
      <ul class="terms">
        <li>Hourly rates</li>
        <li>Flat fees</li>
        <li>Contingent fees</li>
        <li>Agreed-result hourly rates</li>
      </ul>
    </div>
  </div>
</section>

<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside">
      <p class="section-no">No. 03</p>
      <p class="label">Film</p>
    </aside>
    <div>
      <div class="video" data-video="8QmgQwmcflw" data-start="14">
        <button type="button" class="video-btn"><span class="video-play" aria-hidden="true">▶</span><span>Play the firm video</span><span class="muted">Loads from YouTube</span></button>
      </div>
      <p class="fine"><a href="https://www.youtube.com/watch?v=8QmgQwmcflw&amp;t=14s" target="_blank" rel="noopener">Watch on YouTube</a></p>
    </div>
  </div>
</section>

<section class="col-letters-sec" aria-labelledby="cl-h">
  <div class="wrap">
    <p class="section-no">No. 04</p>
    <h2 id="cl-h" class="h2">In our clients’ words</h2>
    <div class="col-letters">{letters}</div>
    <p class="fine">Client feedback reflects individual experiences. It does not guarantee or predict a similar outcome in any legal matter.</p>
  </div>
</section>
{call_band(depth)}'''
    page('about', depth, f'About Our Delaware Law Firm | {FIRM}', m['description'], 'about', body)


def build_attorneys():
    depth = 1
    r = rel(depth)
    m = META['attorneys/index.html']
    rows = ''
    for a in ATTORNEYS:
        tags = ' '.join(a['practice_slugs'])
        rows += f'''
        <li class="row" data-office="{' '.join(a['offices'])}" data-practices="{tags}">
          <a href="{r}{a['slug']}/" data-portrait="{r}assets/attorneys/{a['slug']}.jpg">
            <span class="row-thumb">{portrait(a, depth, alt='')}</span>
            <span class="row-name">{E(a['name'])}</span>
            <span class="row-title">{E(a['title'])}</span>
            <span class="row-office">{E(a['office_label'])}</span>
            <span class="row-focus">{E(a['summary'])}</span>
          </a>
        </li>'''
    used = []
    for a in ATTORNEYS:
        for t in a['practice_slugs']:
            if t not in used:
                used.append(t)
    popts = ''.join(f'<option value="{s}">{E(PRACTICE_BY_SLUG[s]["name"])}</option>' for s in sorted(used, key=lambda s: PRACTICE_BY_SLUG[s]['name']))
    body = page_head('Attorney directory', 'Delaware attorneys',
                     'The firm serves clients statewide at our Dover and Rehoboth Beach offices with experience across transactions, litigation, real estate, estates, business, and public-sector matters.',
                     depth=depth) + f'''
<section class="directory">
  <div class="wrap">
    <div class="filters" role="group" aria-label="Filter attorneys">
      <div class="filter-office" role="radiogroup" aria-label="Office">
        <button type="button" role="radio" aria-checked="true" data-office="">All offices</button>
        <button type="button" role="radio" aria-checked="false" data-office="dover">Dover</button>
        <button type="button" role="radio" aria-checked="false" data-office="rehoboth">Rehoboth Beach</button>
      </div>
      <label class="filter-practice"><span class="label">Practice</span>
        <span class="select-wrap select-plain"><select id="practice-filter"><option value="">Any practice area</option>{popts}</select></span>
      </label>
      <p class="filter-count" aria-live="polite"><span>{len(ATTORNEYS)}</span> attorneys</p>
    </div>
    <div class="directory-grid">
      <div class="directory-frame" aria-hidden="true">
        <img src="{r}assets/attorneys/{ATTORNEYS[0]['slug']}.jpg" alt="" width="250" height="304" />
      </div>
      <div class="directory-table">
        <div class="row row-head" aria-hidden="true"><span class="row-name">Name</span><span class="row-title">Title</span><span class="row-office">Office</span><span class="row-focus">Focus</span></div>
        <ul class="rows">{rows}
        </ul>
        <p class="no-match" hidden>No attorney matches those filters. Call either office and we will help you find the right person.</p>
      </div>
    </div>
  </div>
</section>
{call_band(depth, 'Not sure who to call?', 'We will connect you')}'''
    page('attorneys', depth, f'Delaware Attorneys | {FIRM}', m['description'], 'attorneys', body)


def build_bios():
    depth = 1
    r = rel(depth)
    n = len(ATTORNEYS)
    for i, a in enumerate(ATTORNEYS):
        prev_a, next_a = ATTORNEYS[i - 1], ATTORNEYS[(i + 1) % n]
        phones = ''.join(f'<li><a href="tel:{OFFICES[k]["tel"]}"><span class="label">{OFFICES[k]["name"]}</span>{OFFICES[k]["phone"]}</a></li>' for k in a['offices'])
        tags = ''.join(f'<li><a href="{fix(t["href"], depth)}">{E(t["label"])}</a></li>' for t in a['tags'])
        email = f'<div><dt>Email</dt><dd><a href="mailto:{E(a["email"])}">{E(a["email"])}</a></dd></div>' if a.get('email') else ''
        bio = fix(a['bio_html'], depth)
        body = f'''
<article class="profile">
  <div class="wrap">
    <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{r}">Home</a></li><li><a href="{r}attorneys/">Attorneys</a></li></ol></nav>
  </div>
  <div class="wrap profile-grid">
    <aside class="profile-aside">
      <div class="profile-sticky">
        {portrait(a, depth, 'profile-portrait', lazy=False)}
        <dl class="facts">
          <div><dt>Title</dt><dd>{E(a['title'])}</dd></div>
          <div><dt>Office</dt><dd>{office_links(a, depth)}</dd></div>
          {email}
        </dl>
        <p class="label">Call</p>
        <ul class="profile-phones">{phones}</ul>
        <p class="label">Related practice</p>
        <ul class="profile-tags">{tags}</ul>
      </div>
    </aside>
    <div class="profile-main">
      <header class="profile-head">
        <p class="kicker">{E(a['eyebrow'])}</p>
        <h1 class="profile-name">{E(a['name'])}</h1>
        <p class="deck">{E(a['deck'])}</p>
      </header>
      <div class="prose bio">
        {bio}
      </div>
    </div>
  </div>
  <nav class="pager" aria-label="More attorneys">
    <div class="wrap pager-inner">
      <a class="pager-prev" href="{r}{prev_a['slug']}/"><span class="label">Previous</span><span class="pager-name">{E(prev_a['name'])}</span></a>
      <a class="pager-all" href="{r}attorneys/">All attorneys</a>
      <a class="pager-next" href="{r}{next_a['slug']}/"><span class="label">Next</span><span class="pager-name">{E(next_a['name'])}</span></a>
    </div>
  </nav>
</article>
{call_band(depth)}'''
        page(a['slug'], depth, a['meta']['title'], a['meta']['description'], 'attorneys', body, 'page-profile')


def build_practice_index():
    depth = 1
    r = rel(depth)
    m = META['practice-areas/index.html']
    items = ''
    prev_letter = ''
    for i, p in enumerate(sorted(PRACTICES, key=lambda p: p['name']), 1):
        if i > 1:
            prev_letter = sorted(PRACTICES, key=lambda p: p['name'])[i - 2]['name'][0]
        items += f'''
      <li class="az-item reveal">
        <a href="{r}practice-areas/{p['slug']}/">
          <span class="az-letter" aria-hidden="true">{p['name'][0] if p['name'][0] != prev_letter else ''}</span>
          <span class="az-name">{E(p['name'])}</span>
          <span class="az-summary">{E(p['summary'])}</span>
        </a>
      </li>'''
    head_cells = ''.join(f'<th scope="col"><span>{E(l)}</span></th>' for _, l in AUDIENCES)
    mrows = ''
    for p in sorted(PRACTICES, key=lambda p: p['name']):
        cells = ''.join(
            f'<td>{"<span class=mark aria-label=Yes>●</span>" if k in MATRIX[p["slug"]] else "<span class=nomark aria-label=No></span>"}</td>'
            for k, _ in AUDIENCES)
        mrows += f'<tr><th scope="row"><a href="{r}practice-areas/{p["slug"]}/">{E(SHORT[p["slug"]])}</a></th>{cells}</tr>'
    body = page_head('Practice areas', 'Legal services for Delaware clients.',
                     "Browse the firm's services for individuals, families, businesses, property owners, associations, creditors, and governmental entities.",
                     depth=depth) + f'''
<section class="az">
  <div class="wrap">
    <ol class="az-list">{items}
    </ol>
  </div>
</section>
<section class="matrix-sec" aria-labelledby="matrix-h">
  <div class="wrap">
    <p class="section-no">Index</p>
    <h2 id="matrix-h" class="h2">Who we serve</h2>
    <p class="muted matrix-intro">Find your column, then follow the marks.</p>
    <div class="matrix-scroll" tabindex="0">
      <table class="matrix">
        <thead><tr><th scope="col" class="matrix-corner">Practice area</th>{head_cells}</tr></thead>
        <tbody>{mrows}</tbody>
      </table>
    </div>
  </div>
</section>
{call_band(depth)}'''
    page('practice-areas', depth, f'Delaware Legal Practice Areas | {FIRM}', m['description'], 'practice-areas', body)


def build_practices():
    depth = 2
    r = rel(depth)
    n = len(PRACTICES)
    for i, p in enumerate(PRACTICES):
        nxt = PRACTICES[(i + 1) % n]
        atts = attorneys_for(p['slug'])
        toc = ['<li><a href="#overview">Overview</a></li>']
        sections = f'<section id="overview" class="pa-section"><div class="prose prose-first">{fix(p["body_html"], depth)}</div></section>'
        if p['helps']:
            toc.append(f'<li><a href="#how">{E(p["help_title"] or "How we help")}</a></li>')
            helps = ''.join(f'<li><span class="help-num">{j:02d}</span><span class="help-text">{fix(h, depth)}</span></li>' for j, h in enumerate(p['helps'], 1))
            sections += f'<section id="how" class="pa-section"><h2 class="h3">{E(p["help_title"] or "How we help")}</h2><ol class="helps">{helps}</ol></section>'
        if p['faqs']:
            toc.append('<li><a href="#questions">Questions</a></li>')
            qa = ''.join(f'<details class="qa"><summary><span class="qa-q" aria-hidden="true">Q.</span><span>{E(f["q"])}</span></summary><div class="qa-a prose">{fix(f["a"], depth)}</div></details>' for f in p['faqs'])
            sections += f'<section id="questions" class="pa-section"><h2 class="h3">{E(p["faq_title"])}</h2><div class="qas">{qa}</div></section>'
        toc.append('<li><a href="#attorneys">Attorneys</a></li>')
        if atts:
            alist = ''.join(f'<li><a href="{r}{a["slug"]}/">{portrait(a, depth, alt="")}<span class="pa-att-name">{E(a["name"])}</span><span class="pa-att-meta">{E(a["title"])} · {E(a["office_label"])}</span></a></li>' for a in atts)
            att_html = f'<ul class="pa-atts">{alist}</ul>'
        else:
            att_html = f'<p class="prose-lg">Call either office and the firm will connect you with the appropriate attorney for your matter.</p>'
        d, rb = OFFICES['dover'], OFFICES['rehoboth']
        sections += f'''<section id="attorneys" class="pa-section"><h2 class="h3">Attorneys</h2>{att_html}
          <p class="pa-call">Dover <a href="tel:{d['tel']}">{d['phone']}</a> <span aria-hidden="true">·</span> Rehoboth Beach <a href="tel:{rb['tel']}">{rb['phone']}</a></p></section>'''
        body = page_head(f'Practice area · No. {i + 1:02d}', E(p['name']), E(p['deck']),
                         crumbs=[('Practice areas', 'practice-areas/')], depth=depth) + f'''
<div class="wrap pa-grid">
  <aside class="pa-aside">
    <nav class="pa-toc" aria-label="On this page">
      <p class="label">On this page</p>
      <ol>{''.join(toc)}</ol>
    </nav>
  </aside>
  <div class="pa-main">{sections}</div>
</div>
<nav class="next-band" aria-label="Next practice area">
  <a class="wrap next-inner" href="{r}practice-areas/{nxt['slug']}/">
    <span class="label">Next · No. {(i + 1) % n + 1:02d}</span>
    <span class="next-name">{E(nxt['name'])}</span>
    <span class="next-arrow" aria-hidden="true">→</span>
  </a>
</nav>
{call_band(depth)}'''
        page(f'practice-areas/{p["slug"]}', depth, p['meta']['title'], p['meta']['description'], 'practice-areas', body, 'page-practice')


OFFICE_COPY = {
    'dover': {
        'title': 'Dover, Delaware Law Office',
        'deck': 'The Dover office remains at 225 South State Street, close to Delaware courts, government offices, and civic institutions.',
        'intro': f'{FIRM}’s Dover law office serves clients with matters in Dover, Kent County, and throughout Delaware. Call (302) 734-7401 to discuss your needs and the appropriate attorney.',
        'building': 'The Dover office occupies the buildings between historic Wesley Church and North Street.',
        'services_intro': 'The Dover attorneys’ published practices include landlord-tenant matters, estate planning and administration, real estate, civil litigation, and municipal and zoning work.',
        'services': ['Estate Planning & Administration', 'Landlord/Tenant Law', 'Business Law', 'Municipal Law', 'Zoning & Land Use', 'Real Estate', 'Civil Litigation', 'Appellate Advocacy', 'Consumer Bankruptcy', 'Insurance Regulation'],
        'visit': 'When contacting the office, a brief description of the issue can help start the discussion. If available, have relevant documents, the names of the parties involved, and any notices, court papers, or response dates ready. Ask the office how to provide documents and confirm the meeting location and time.',
        'faqs': [
            ('Where is the Dover office?', 'The office is at 225 South State Street, Dover, DE 19901, between historic Wesley Church and North Street.'),
            ('How do I contact the Dover office?', 'Call (302) 734-7401 or use the contact page to discuss your needs, the appropriate attorney, and meeting arrangements.'),
            ('Where can I learn about the Dover attorneys?', 'Each attorney listed on this page links to a full biography, including published practice areas and backgrounds. The firm can discuss which attorney is appropriate for your matter.'),
            ('What should I have ready for an initial discussion?', 'A short explanation of the matter, relevant documents, party names, and any notices or hearing or response dates can help. Contact the office to ask how to provide the records and confirm meeting arrangements.'),
        ],
    },
    'rehoboth': {
        'title': 'Rehoboth Beach Law Office',
        'deck': 'The Rehoboth Beach office serves clients throughout Sussex County from 309 Rehoboth Avenue, a central location in Delaware’s coastal real estate and business corridor.',
        'intro': f'{FIRM}’s Rehoboth Beach law office serves Sussex County clients and Delaware’s coastal communities. Call (302) 227-9441 to discuss your needs and the appropriate attorney.',
        'building': 'The office provides a meeting location for clients from Rehoboth Beach, Lewes, Dewey Beach, Bethany Beach, Georgetown, Millville, Ocean View, and surrounding Sussex County communities.',
        'services_intro': 'The Rehoboth Beach attorneys’ published practices include real estate, HOA and condominium association counsel, business law, estate planning and administration, and alcoholic beverage licensing.',
        'services': None,
        'visit': 'A short description of the matter, relevant records, party names, and any notices or response dates can help with an initial discussion. Ask how to provide documents and confirm the location and time.',
        'faqs': [
            ('Where is the Rehoboth Beach office?', 'The office is at 309 Rehoboth Avenue, Rehoboth Beach, DE 19971.'),
            ('How do I contact the Rehoboth Beach office?', 'Call (302) 227-9441 or use the contact page to discuss your needs, the appropriate attorney, and meeting arrangements.'),
            ('Which communities does the office serve?', 'Rehoboth Beach, Lewes, Dewey Beach, Bethany Beach, Georgetown, Millville, Ocean View, and surrounding Sussex County communities.'),
            ('What should I have ready for an initial discussion?', 'A short explanation of the matter, relevant documents, party names, and any notices or response dates can help. Contact the office to ask how to provide the records and confirm meeting arrangements.'),
        ],
    },
}


def build_offices():
    depth = 1
    r = rel(depth)
    for k, o in OFFICES.items():
        cp = OFFICE_COPY[k]
        other = OFFICES['rehoboth' if k == 'dover' else 'dover']
        atts = [a for a in ATTORNEYS if k in a['offices']]
        alist = ''.join(f'<li><a href="{r}{a["slug"]}/">{portrait(a, depth, alt="")}<span class="pa-att-name">{E(a["name"])}</span><span class="pa-att-meta">{E(a["title"])}</span></a></li>' for a in atts)
        if cp['services']:
            svc = ''.join(f'<li>{E(s)}</li>' for s in cp['services'])
        else:
            slugs = []
            for a in atts:
                for s in a['practice_slugs']:
                    if s not in slugs:
                        slugs.append(s)
            svc = ''.join(f'<li><a href="{r}practice-areas/{s}/">{E(PRACTICE_BY_SLUG[s]["name"])}</a></li>' for s in slugs)
        names = [a['name'] for a in atts]
        names_txt = ', '.join(names[:-1]) + ', and ' + names[-1] if len(names) > 2 else ' and '.join(names)
        faqs = ''.join(f'<details class="qa"><summary><span class="qa-q" aria-hidden="true">Q.</span><span>{E(q)}</span></summary><div class="qa-a prose"><p>{E(a_)}</p></div></details>' for q, a_ in cp['faqs'])
        m = META[f'{o["slug"]}/index.html']
        body = f'''
<header class="office-hero">
  <div class="wrap office-hero-grid">
    <div class="office-hero-text">
      <nav class="crumbs" aria-label="Breadcrumb"><ol><li><a href="{r}">Home</a></li><li><a href="{r}contact-us/">Offices</a></li></ol></nav>
      <p class="kicker">{o['county']}</p>
      <h1 class="page-title">{cp['title']}</h1>
      <p class="deck">{cp['deck']}</p>
      <div class="plaque">
        <p class="plaque-name">{FIRM}</p>
        <address>{o['street']}<br />{o['city']}</address>
        <p class="plaque-lines"><a href="tel:{o['tel']}">{o['phone']}</a><span>Fax {o['fax']}</span></p>
        <a class="btn btn-line" href="{o['map']}" target="_blank" rel="noopener">Get directions</a>
      </div>
    </div>
    <figure class="office-photo">{picture(o['photo'], depth, f"The {o['name']} office of {FIRM}", o['photo_w'], o['photo_h'], lazy=False)}</figure>
  </div>
</header>

<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside"><p class="section-no">No. 01</p><p class="label">The office</p></aside>
    <div class="prose prose-lg">
      <p class="dropcap">{cp['intro']}</p>
      <p>{cp['building']}</p>
    </div>
  </div>
</section>

<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside"><p class="section-no">No. 02</p><p class="label">Attorneys here</p></aside>
    <div>
      <p class="prose-lg">{E(names_txt)} {'work' if len(names) > 1 else 'works'} from the {o['name']} office. Contact the firm to discuss whether it can assist and which attorney is appropriate for your particular matter.</p>
      <ul class="pa-atts">{alist}</ul>
    </div>
  </div>
</section>

<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside"><p class="section-no">No. 03</p><p class="label">Legal services</p></aside>
    <div>
      <p class="prose-lg">{cp['services_intro']}</p>
      <ul class="svc-list">{svc}</ul>
    </div>
  </div>
</section>

<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside"><p class="section-no">No. 04</p><p class="label">Before you visit</p></aside>
    <div>
      <p class="prose-lg">{cp['visit']}</p>
      <div class="qas">{faqs}</div>
      <p class="muted">Also see the <a href="{r}{other['slug']}/">{other['long']}</a> or the <a href="{r}contact-us/">contact page</a>.</p>
    </div>
  </div>
</section>
{call_band(depth)}'''
        page(o['slug'], depth, f'{cp["title"].replace("Rehoboth Beach Law Office", "Rehoboth Beach, Delaware Law Office")} | {FIRM}', m['description'], '', body, 'page-office')


def build_contact():
    depth = 1
    r = rel(depth)
    m = META['contact-us/index.html']
    cols = ''
    for k, o in OFFICES.items():
        cols += f'''
      <section class="contact-col" aria-labelledby="c-{k}">
        <p class="label">{OFFICES[k]['region']}</p>
        <h2 id="c-{k}" class="h2"><a href="{r}{o['slug']}/">{o['long']}</a></h2>
        <a class="contact-phone" href="tel:{o['tel']}">{o['phone']}</a>
        <dl class="facts">
          <div><dt>Address</dt><dd>{o['street']}<br />{o['city']}</dd></div>
          <div><dt>Fax</dt><dd>{o['fax']}</dd></div>
        </dl>
        <p class="contact-links"><a class="arrow-link" href="{o['map']}" target="_blank" rel="noopener">Get directions</a> <a class="arrow-link" href="{r}{o['slug']}/">Office page</a></p>
      </section>'''
    body = page_head('Start here', 'Contact us',
                     'Please call the Delaware office nearest you. The firm serves clients from Dover and Rehoboth Beach, including matters in Kent County, Sussex County, and throughout Delaware.',
                     depth=depth) + f'''
<section class="contact">
  <div class="wrap contact-grid">{cols}
  </div>
  <div class="wrap">
    <p class="notice"><span class="label">Please note</span> Please do not provide confidential information until an attorney-client relationship has been established.</p>
  </div>
</section>
<section class="where where-plain" aria-label="Map">
  <div class="wrap where-grid">
    <div class="where-map">{delaware_map(depth)}</div>
    <div class="where-text">
      <p class="section-no">Getting here</p>
      <h2 class="h2">Central Delaware and the coast.</h2>
      <p class="prose-lg">The Dover office sits in the state capital, close to the courts and government offices. The Rehoboth Beach office is on Rehoboth Avenue, serving Lewes, Dewey Beach, Bethany Beach, Georgetown and the rest of Sussex County.</p>
    </div>
  </div>
</section>'''
    page('contact-us', depth, f'Contact Delaware Lawyers | {FIRM}', m['description'], 'contact-us', body)


def build_careers():
    depth = 1
    r = rel(depth)
    m = META['careers/index.html']
    jobs = [
        ('Rehoboth Beach', 'Associate Attorney, Real Estate', 'Our Rehoboth Beach office is looking for an associate with two to five years of real estate experience. The work includes residential and commercial settlements, title review, and appearances before Sussex County and town planning and zoning boards.',
         ['J.D. and admission to the Delaware Bar (or sitting for the next exam)', '2–5 years of real estate or transactional experience', 'Strong drafting skills and attention to detail'], 'Associate%20Attorney%20-%20Rehoboth%20Beach', 'Apply for the Rehoboth Beach position'),
        ('Dover', 'Associate Attorney, Litigation', "Our Dover office is looking for an associate with at least three years of litigation experience. The work includes civil cases in Delaware's trial courts and advising the towns and public bodies we represent in Kent County.",
         ['J.D. and admission to the Delaware Bar', '3+ years of litigation experience', 'Strong writing and courtroom skills'], 'Associate%20Attorney%20-%20Dover', 'Apply for the Dover position'),
    ]
    notices = ''
    for i, (office, title, desc, reqs, subj, cta) in enumerate(jobs, 1):
        rq = ''.join(f'<li>{E(x)}</li>' for x in reqs)
        notices += f'''
      <article class="notice-item reveal">
        <p class="notice-no">Notice No. {i}</p>
        <p class="label">{office} office · Full-time · In office</p>
        <h3 class="notice-title">{title}</h3>
        <p>{E(desc)}</p>
        <h4 class="label">Requirements</h4>
        <ul class="ticks">{rq}</ul>
        <a class="btn btn-solid" href="mailto:{EMAIL}?subject={subj}">{cta}</a>
      </article>'''
    body = page_head('Opportunities', 'Careers', 'We are hiring attorneys for our Dover and Rehoboth Beach offices.', depth=depth) + f'''
<section class="careers">
  <div class="wrap careers-grid">
    <div>
      <p class="section-no">Open positions (2)</p>
      <p class="prose-lg">Both positions are full-time and based in the office, with competitive salary and benefits.</p>
      <div class="notices">{notices}</div>
    </div>
    <aside class="careers-aside">
      <figure class="careers-photo">{picture('assets/img/rehoboth-boardwalk', depth, '', 1690, 1110)}</figure>
      <h2 class="h3">How to apply</h2>
      <p>Email your resume, cover letter, and a writing sample to:</p>
      <p><a class="mail" href="mailto:{EMAIL}?subject=Attorney%20Application">{EMAIL}</a></p>
      <h2 class="h3">Not seeing the right position?</h2>
      <p>We accept applications from attorneys at any time. Send your materials to <a href="mailto:{EMAIL}">{EMAIL}</a> and we will keep them on file.</p>
      <h2 class="h3">Questions?</h2>
      <p>Dover <a href="tel:+13027347401">(302) 734-7401</a><br />Rehoboth Beach <a href="tel:+13022279441">(302) 227-9441</a></p>
      <p class="fine">{FIRM} is an equal opportunity employer.</p>
    </aside>
  </div>
</section>'''
    page('careers', depth, f'Delaware Law Firm Careers | {FIRM}', m['description'], 'careers', body)


def build_resources():
    depth = 1
    r = rel(depth)
    m = META['links-and-resources/index.html']
    faqs = ''.join(f'<details class="qa qa-article"><summary><span class="qa-q" aria-hidden="true">{i:02d}</span><span>{E(f["q"])}</span></summary><div class="qa-a prose">{fix(f["a"], depth)}</div></details>' for i, f in enumerate(RESOURCES['faq'], 1))
    groups = ''
    for g in RESOURCES['groups']:
        if g['title'] == 'Call Now':
            continue
        links = ''.join(f'<li><a href="{E(l["href"])}" target="_blank" rel="noopener">{E(l["label"])}<span class="ext" aria-hidden="true">↗</span></a></li>' for l in g['links'])
        groups += f'''
      <section class="res-group">
        <h3 class="label">{E(g['title'])}</h3>
        {f'<p class="muted">{E(g["description"])}</p>' if g['description'] else ''}
        <ul>{links}</ul>
      </section>'''
    body = page_head('Client information', 'FAQ &amp; resources',
                     'Frequently asked questions and official Delaware legal, court, and county resources for clients who need public information.', depth=depth) + f'''
<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside"><p class="section-no">Part I</p><p class="label">Questions</p></aside>
    <div>
      <p class="prose-lg">Answers to common client questions.</p>
      <div class="qas">{faqs}</div>
    </div>
  </div>
</section>
<section class="article-sec res-sec">
  <div class="wrap article-grid">
    <aside class="article-aside"><p class="section-no">Part II</p><p class="label">Official links</p></aside>
    <div>
      <p class="prose-lg">Official Delaware state, court, county, and municipal resources. These links are provided for convenience only. They do not replace legal advice about a specific matter, deadline, filing, or dispute.</p>
      <label class="res-search"><span class="label">Search the links</span><input type="search" id="res-filter" placeholder="Try “deeds”, “Sussex” or “zoning”" autocomplete="off" /></label>
      <div class="res-groups">{groups}</div>
      <p class="no-match" hidden>No links match. Try a shorter word.</p>
    </div>
  </div>
</section>
{call_band(depth)}'''
    page('links-and-resources', depth, f'Delaware Legal FAQ & Resources | {FIRM}', m['description'], 'links-and-resources', body)


def build_privacy():
    depth = 1
    m = META['privacy-policy/index.html']
    paras = ''
    for t in PRIVACY:
        if t.isupper():
            paras += f'<h2 class="h3">{E(t.capitalize())}</h2>'
        else:
            paras += f'<p>{E(t)}</p>'
    body = page_head('Privacy notice', 'Privacy policy', f'Privacy policy for client information handled by {FIRM}, LLC.', depth=depth) + f'''
<section class="article-sec">
  <div class="wrap article-grid">
    <aside class="article-aside"><p class="label">Policy</p></aside>
    <div class="prose">{paras}</div>
  </div>
</section>'''
    page('privacy-policy', depth, f'Privacy Policy | {FIRM}', m['description'], '', body)


def build_misc():
    # 404
    depth = 0
    r = '/hjjf-redesign/'
    body = f'''
<section class="page-head notfound">
  <div class="wrap">
    <p class="kicker">Error 404</p>
    <h1 class="page-title">This page is not in the almanac.</h1>
    <p class="deck">The page may have moved. Try the <a href="{r}">home page</a>, the <a href="{r}attorneys/">attorney directory</a> or the <a href="{r}practice-areas/">practice areas</a>, or call Dover (302) 734-7401 or Rehoboth Beach (302) 227-9441.</p>
  </div>
</section>'''
    out = head(f'Page not found | {FIRM}', 'Page not found.', 0, '404.html', f'<base href="{r}" />')
    out += '\n<body>' + header(0, '') + f'\n<main id="main">{body}\n</main>' + footer(0)
    open(os.path.join(ROOT, '404.html'), 'w', encoding='utf-8').write(out)
    # /faq/ redirect
    os.makedirs(os.path.join(ROOT, 'faq'), exist_ok=True)
    open(os.path.join(ROOT, 'faq', 'index.html'), 'w', encoding='utf-8').write(
        '<!doctype html><html lang="en"><head><meta charset="utf-8" /><title>FAQ &amp; Resources</title>'
        '<link rel="canonical" href="' + SITE_URL + 'links-and-resources/" />'
        '<meta http-equiv="refresh" content="0; url=../links-and-resources/" /></head>'
        '<body><p>The FAQ is now part of <a href="../links-and-resources/">FAQ &amp; Resources</a>.</p></body></html>\n')
    # sitemap + robots
    paths = ['', 'about/', 'attorneys/', 'practice-areas/', 'contact-us/', 'careers/', 'dover-office/',
             'rehoboth-office/', 'links-and-resources/', 'privacy-policy/']
    paths += [a['slug'] + '/' for a in ATTORNEYS] + [f'practice-areas/{p["slug"]}/' for p in PRACTICES]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += ''.join(f'  <url><loc>{SITE_URL}{p}</loc></url>\n' for p in paths) + '</urlset>\n'
    open(os.path.join(ROOT, 'sitemap.xml'), 'w').write(sm)
    open(os.path.join(ROOT, 'robots.txt'), 'w').write(f'User-agent: *\nAllow: /\nSitemap: {SITE_URL}sitemap.xml\n')
    open(os.path.join(ROOT, '.nojekyll'), 'w').write('')


if __name__ == '__main__':
    build_home()
    build_about()
    build_attorneys()
    build_bios()
    build_practice_index()
    build_practices()
    build_offices()
    build_contact()
    build_careers()
    build_resources()
    build_privacy()
    build_misc()
    print('built')
