# Hudson, Jones, Jaywork & Fisher: redesigned website

A second, independent version of delawarelaw.com. The faithful copy of the current site lives in
[chipperbecker-droid/HJJF](https://github.com/chipperbecker-droid/HJJF) and is untouched.

- **Live preview:** https://chipperbecker-droid.github.io/hjjf-redesign/
- **Design plan and rationale:** [PLAN.md](PLAN.md) (including notes for a later move to WordPress)

## What stays the same
Attorney biographies (verbatim) and the firm logo. Everything else is new.

## Structure
- `content/*.json`: the site's words and data (attorneys, practice areas, testimonials, resources).
- `tools/build.py`: generates every page from the content. Run `python3 tools/build.py`.
- `tools/extract.py`: re-imports content from the original HJJF site if it changes.
- `assets/css/site.css`, `assets/js/site.js`: the single stylesheet and script.
- Generated pages are committed at the repository root, so GitHub Pages serves them directly.

## Images
Only the firm's own photographs (offices, attorney portraits), a public-domain Rehoboth Beach
boardwalk photo, and a map of Delaware drawn from public-domain U.S. Census outlines. No image
requires a credit.

_Last published: 2026-11-20._
