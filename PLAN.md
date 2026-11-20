# Hudson, Jones, Jaywork & Fisher: redesign plan

This repository is a second, independent version of delawarelaw.com. The faithful copy of the
current site stays untouched in `chipperbecker-droid/HJJF`. Everything here is new except two
things the firm asked to keep exactly as they are:

- **Attorney biographies**: the bio text on every attorney page is copied verbatim from the
  current site by `tools/extract.py` (only link paths are rewritten). Nothing in it is edited, not
  even the known stray comma in Daniel Patrick Myers II's bio.
- **The logo**: `assets/logo-balanced.png`, unchanged, used at its original proportions.

## 1. The idea: a Delaware almanac, not a template

Most law firm sites, including the current one, are built from the same parts: a dark photo hero,
three-across cards, a testimonial carousel, more cards. The redesign treats the site like a
well-made printed reference book about the firm: an almanac with a table of contents, a ledger of
attorneys, a timeline, letters from clients, and a map. Information is organised by rules,
numbers, columns and type rather than boxes.

Inspiration taken from real firm sites and 2026 design write-ups (PaperStreet's 2026 trends,
Blacksmith's survey of New York firms, Lawyerist's Best Law Firm Websites 2026):

| Seen at | What we borrow |
| --- | --- |
| Cravath, Davis Polk, Wachtell | Typography does the work; restraint signals confidence. |
| Zimmerman Reed, Johnston Clem | Thin rules and dividers to structure pages instead of boxes. |
| Zemsky Family Law, Leake & Andersson | Editorial grids, asymmetry, generous margins. |
| FFP Law, Chubb firm | Real photography of the firm's own places instead of stock. |
| Cairns Law, ALH Law | Plain-language guidance and accordions that make dry topics easy to scan. |
| Sidweber Law | A single guiding device (here, the "What brings you here?" sentence) that routes visitors. |

What we deliberately avoid: card grids, icon rows, gradient blobs, glassmorphism, stock photos of
handshakes and gavels, purple/blue tech palettes, and the "Inter + rounded corners" AI look.

## 2. Visual system

- **Colour** comes from the logo and the two buildings: bottle green `#14382F` (logo ring),
  brass `#B08442` (logo scales), warm paper `#F5F0E6`, ink `#1C1B18`, and a brick red `#8C3A2B`
  (the Dover building) used only for small marks such as the map pins and the active link.
- **Type**: Libre Caslon Display for large headings, Libre Caslon Text for reading (Caslon is the
  face of the Declaration of Independence printing and suits a firm founded in the First State),
  and Public Sans (designed by the U.S. government) for small labels, navigation and data.
- **Structure**: a 12-column grid with wide margins, hairline rules, numbered sections
  (No. 01, No. 02 ...), old-style figures and small caps for labels.
- **Imagery**: only the firm's own photos (the Dover and Rehoboth Beach offices, attorney portraits)
  plus the public-domain Rehoboth boardwalk photo already approved for the careers page. A drawn map
  of Delaware (traced from public-domain U.S. Census outlines) marks the two offices. No photo credits
  appear anywhere because nothing needs one. The Wikimedia landmark photos in the old site were left
  out because their licences could not be confirmed as public domain or CC0.
- **Motion**: short fades as sections enter, hover previews of portraits. All motion is turned off
  for visitors who ask for reduced motion.

## 3. Page by page

### Home
1. **Masthead hero**: the firm's promise set large in Caslon, with a dateline ("Dover · Rehoboth
   Beach · Est. December 31, 1956") instead of a stock photo.
2. **Two doors**: the Dover brick building and the Rehoboth Beach cottage side by side, each captioned
   with its address and phone number. The firm's real places are the strongest image it has.
3. **Ledger strip**: "Since 1956 · 2 offices · 11 attorneys · 13 practice areas" in one ruled row
   ("Since 1956" replaces "70 years", which would go stale).
4. **What brings you here?**: an interactive sentence, "I am a [homeowner] and I need help with
   [buying or selling a home]", that answers with the right practice area, the attorneys who handle
   it and which office to call.
5. **Table of contents**: the practice areas as a numbered contents page with dotted leaders. Hovering
   a line shows its summary in a side column.
6. **Timeline**: 1956, c. 1960, 1977, today, drawn as a horizontal rule with dates.
7. **Attorneys as a roll call**: every name set in large type as one flowing line; hovering a name
   shows the portrait beside the cursor (on phones the portraits sit in a scrolling strip).
8. **Letters from clients**: one quotation at a time, set very large, with a "03 / 16" counter.
9. **Map and offices**: the Delaware map with both offices pinned, beside the two addresses.
10. **Closing call**: both phone numbers set as large tappable lines.

### Attorneys directory
A ledger (name, title, office, focus) instead of a portrait grid. Filters for office and practice
area. Hovering a row shows that attorney's portrait in a sticky frame; on phones each row carries a
small portrait.

### Attorney profile (11 pages)
Portrait and a fact column (title, office, phone, related practice areas) stay pinned on the left
while the verbatim biography reads in a comfortable column on the right with a drop cap. Previous and
next attorney links close the page.

### Practice areas index
An A to Z index with summaries, followed by a "Who we serve" matrix: practice areas down the side,
client types (individuals and families, businesses, property owners, associations, public bodies)
across the top, with marks where they meet.

### Practice area pages (13)
Long-form article layout: title and standfirst, a pinned "On this page" column, the firm's text, a
numbered "How we help" list, questions and answers, the attorneys who handle the area (drawn from the
directory tags) and a large "next practice area" link.

### About
Founding story, the timeline in full, the firm's service principle as a pull quote, billing
arrangements as a definition list, the firm video (loaded only when clicked), and all 16 client
letters in newspaper columns.

### Dover and Rehoboth Beach offices
A large photograph of the building, the address set like a brass plaque, who works there, what the
office handles, what to bring to a first meeting, and office questions.

### Contact
Two columns, one per office, with very large phone numbers, fax, directions and the confidentiality
notice. No form, matching the firm's current preference for phone contact.

### Careers
Openings set as classified notices with requirements and a plain `mailto:` link (not hidden behind
Cloudflare email protection).

### FAQ & Resources
The firm's articles as an accordion, then the official links as a searchable directory grouped by
topic.

### Privacy policy, 404 and /faq/
Plain long-form text; a branded 404; `/faq/` redirects to `/links-and-resources/`.

## 4. Fixes from the improvement notes that are built in
- One spelling of the firm name everywhere: "Hudson, Jones, Jaywork & Fisher".
- "Since 1956" instead of a year count.
- A real Facebook label and icon instead of a bare "f".
- Decorative images have empty alt text; no auto-generated hover titles.
- One header and one footer in the markup (no duplicated mobile copies).
- Dover office page names all five Dover attorneys and drops the drafting-note wording.
- Careers uses a plain mailto link to info@delawarelaw.com.
- One small cached stylesheet and one small script; WebP images where available.

## 5. Moving to WordPress later
The site is plain HTML, one stylesheet (`assets/css/site.css`) and one script (`assets/js/site.js`)
generated from structured content (`content/*.json`) by `tools/build.py`. That separation maps
directly onto WordPress:

- **Theme**: the stylesheet and script become a block or classic theme; the header and footer become
  template parts.
- **Custom post types**: `attorney` (name, title, office, summary, tags, portrait, bio) and
  `practice_area` (name, summary, standfirst, body, how we help, FAQs), imported from the JSON files.
- **Page templates**: home, directory, profile, practice index, practice area, office, contact.
- **URLs**: every page keeps the exact slug the live site uses today, so no redirects are needed.
- **The interactive pieces** (sentence finder, directory filters, quotation counter, portrait
  previews) are small, dependency-free JavaScript that works as-is inside a WordPress theme.

## 6. How to work on it
```
python3 tools/extract.py /path/to/HJJF   # only to re-import content from the old site
python3 tools/build.py                   # regenerates every page from content/ and templates
```
The generated HTML is committed so GitHub Pages can serve the repository root directly.
