"""One-time extraction of content from the original HJJF static site.

Usage: python3 tools/extract.py /path/to/HJJF
Writes content/*.json. Bio HTML is copied verbatim (only link prefixes are
normalised to "@/" so pages at any depth can re-root them).
"""
import json, re, sys, os
from bs4 import BeautifulSoup

SRC = sys.argv[1]
OUT = os.path.join(os.path.dirname(__file__), '..', 'content')

def soup(p):
    return BeautifulSoup(open(os.path.join(SRC, p), encoding='utf-8'), 'html.parser')

def norm_links(el):
    for a in el.find_all(['a', 'img', 'source']):
        for attr in ('href', 'src', 'srcset'):
            v = a.get(attr)
            if v and not re.match(r'^(https?:|mailto:|tel:|#)', v):
                a[attr] = '@/' + re.sub(r'^(\.\./|\./)+', '', v)
    return el

def clean_html(el):
    # collapse prettier whitespace but keep the markup itself unchanged
    s = el.decode_contents() if hasattr(el, 'decode_contents') else str(el)
    return re.sub(r'\s+', ' ', s).strip()

def text(el):
    return ' '.join(el.get_text(' ', strip=True).split()) if el else ''

def meta(s):
    d = s.find('meta', attrs={'name': 'description'})
    return {'title': text(s.title), 'description': d['content'].strip() if d else ''}

# ---------- attorneys ----------
d = soup('attorneys/index.html')
attorneys = []
for art in d.select('article.directory-person'):
    href = art.find('h2').a['href']
    slug = href.strip('./').strip('/')
    person = {
        'slug': slug,
        'name': text(art.find('h2')),
        'office_label': text(art.select_one('.directory-office')),
        'title': text(art.select_one('.directory-title')),
        'summary': text(art.select_one('.practice-summary')),
        'tags': [{'label': text(a), 'href': '@/' + re.sub(r'^(\.\./)+', '', a['href'])}
                 for a in art.select('.directory-practices a')],
    }
    b = soup(f'{slug}/index.html')
    person['meta'] = meta(b)
    hero = b.select_one('section.hero')
    person['eyebrow'] = text(hero.select_one('.eyebrow'))
    person['deck'] = text(hero.select_one('.hero-copy > p:not(.eyebrow)'))
    artc = b.select_one('article.article-card')
    ph = artc.select_one('.profile-header')
    person['portrait'] = 'assets/attorneys/' + slug + '.jpg'
    ph.decompose()
    norm_links(artc)
    blocks = [str(c) for c in artc.children if getattr(c, 'name', None)]
    person['bio_html'] = re.sub(r'\s+', ' ', '\n'.join(blocks)).strip()
    side = b.select_one('aside.side-panel')
    em = side.select_one('.attorney-email p') if side else None
    person['email'] = text(em) if em else ''
    attorneys.append(person)

# ---------- practice areas ----------
p = soup('practice-areas/index.html')
practices = []
for a in p.select('main a[href*="practice-areas/"]'):
    h = a.find(['h2', 'h3', 'span'])
    if not h:
        continue
    slug = a['href'].rstrip('/').split('/')[-1]
    if any(x['slug'] == slug for x in practices):
        continue
    pg = soup(f'practice-areas/{slug}/index.html')
    hero = pg.select_one('section.hero')
    art = pg.select_one('article.article-card')
    norm_links(art)
    faqs = []
    fl = art.select_one('.faq-list')
    if fl:
        for det in fl.select('details'):
            faqs.append({'q': text(det.summary), 'a': clean_html(det.select_one('.faq-answer'))})
        prev = fl.find_previous_sibling('h2')
        faq_title = text(prev) if prev else 'Questions'
        if prev:
            prev.decompose()
        fl.decompose()
    else:
        faq_title = ''
    helps, help_title = [], ''
    for h2 in art.find_all('h2'):
        ul = h2.find_next_sibling()
        if ul is not None and ul.name == 'ul':
            help_title = text(h2)
            helps = [clean_html(li) for li in ul.find_all('li')]
            h2.decompose(); ul.decompose()
            break
    practices.append({
        'slug': slug,
        'name': text(h),
        'summary': text(a.find('p')),
        'meta': meta(pg),
        'deck': text(hero.select_one('.hero-copy > p:not(.eyebrow)')),
        'body_html': clean_html(art),
        'help_title': help_title,
        'helps': helps,
        'faq_title': faq_title,
        'faqs': faqs,
    })

# ---------- testimonials ----------
h = soup('index.html')
testimonials = []
for f in h.select('.testimonial-track figure'):
    q = text(f.blockquote).strip('“”" ')
    if any(t['quote'] == q for t in testimonials):
        continue
    who = text(f.figcaption) if f.figcaption else text(f).replace(text(f.blockquote), '').strip()
    testimonials.append({'quote': q, 'name': who})

# ---------- resources page ----------
r = soup('links-and-resources/index.html')
faq = []
for det in r.select('main details'):
    ans = det.find(class_=re.compile('faq-answer')) or det
    s = det.summary.extract()
    faq.append({'q': text(s), 'a': clean_html(ans)})
groups = []
for h2 in r.select('main h2'):
    sec = h2.find_parent(['section', 'div'])
    links = []
    nxt = h2.find_next_sibling()
    container = h2.find_parent('section')
    for a in container.find_all('a', href=re.compile('^https')):
        links.append({'label': text(a), 'href': a['href']})
    desc = h2.find_next_sibling('p')
    if links:
        groups.append({'title': text(h2), 'description': text(desc) if desc else '', 'links': links})

meta_pages = {}
for pth in ['index.html', 'about/index.html', 'attorneys/index.html', 'practice-areas/index.html',
            'contact-us/index.html', 'careers/index.html', 'dover-office/index.html',
            'rehoboth-office/index.html', 'links-and-resources/index.html', 'privacy-policy/index.html']:
    meta_pages[pth] = meta(soup(pth))

pp = soup('privacy-policy/index.html')
priv = pp.select_one('main section.section article') or pp.select_one('main section.section')
privacy_paras = [text(x) for x in priv.find_all('p') if 'Dover:' not in text(x) and 'Rehoboth:' not in text(x)]

for name, data in [('attorneys', attorneys), ('practices', practices), ('testimonials', testimonials),
                   ('resources', {'faq': faq, 'groups': groups}), ('meta', meta_pages),
                   ('privacy', privacy_paras)]:
    with open(os.path.join(OUT, name + '.json'), 'w', encoding='utf-8') as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
print(len(attorneys), 'attorneys', len(practices), 'practices', len(testimonials), 'testimonials',
      len(faq), 'faq', [g['title'] for g in groups])
