"""Re-sync every Function reference TABLE in sql_problem_patterns.html from the single
source REF (in build_fn_container.py) + the shared ref_table() renderer.

Why this exists: build_fn_container.main() only INSERTS the Functions container once
(it no-ops if id="functions" already present), so a later change to REF or to the table
shape (e.g. adding the "Goes in" column) never reaches the HTML. This script regenerates
the <table> inside each family's reference card in place, so REF stays the one source.

Covers the 6 family reference cards (#fn-<fam>-ref) AND the Date Operations copy
(#mo-date-ref). For the date cards the table sits inside the DATE-FN-REF markers written
by sync_date_ref.py; we replace ONLY the <table> span, so those markers are preserved.

Run:  python3 sync_fn_ref.py   (idempotent, balance-checked)
"""
import os, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_fn_container import REF, ref_table, PATH   # single source + renderer
import eabuild as eb

# card id -> the REF rows that fill it
CARDS = {
    'fn-string-ref':      REF['fn-string'],
    'fn-array-ref':       REF['fn-array'],
    'fn-date-ref':        REF['fn-date'],
    'fn-cast-ref':        REF['fn-cast'],
    'fn-numeric-ref':     REF['fn-numeric'],
    'fn-conditional-ref': REF['fn-conditional'],
    'mo-date-ref':        REF['fn-date'],   # Date Operations copy
}
# family container ids whose header badge must also match len(REF[fid])
FAMILY_IDS = ['fn-string', 'fn-array', 'fn-date', 'fn-cast', 'fn-numeric', 'fn-conditional']


def _match_div(text, start):
    """Index just past the </div> that closes the <div ...> at `start`."""
    depth = 0
    for m in re.finditer(r'<div\b|</div>', text[start:]):
        depth += 1 if m.group().startswith('<div') else -1
        if depth == 0:
            return start + m.end()
    raise SystemExit('unbalanced div from %d' % start)


def _content_region(text, card_id):
    """(open_end, close_start) of the <div class="problem-card-content"> inside card_id."""
    i = text.find('<div id="%s"' % card_id)
    if i < 0:
        raise SystemExit('card #%s not found' % card_id)
    co = text.find('<div class="problem-card-content">', i)
    ce = _match_div(text, co)
    return co + len('<div class="problem-card-content">'), ce - len('</div>')


def _replace_table(text, card_id, rows):
    """Swap the FIRST <table>...</table> inside card_id's content with a fresh render."""
    lo, hi = _content_region(text, card_id)
    ts = text.find('<table', lo)
    if ts < 0 or ts >= hi:
        raise SystemExit('no <table> inside #%s' % card_id)
    te = text.find('</table>', ts) + len('</table>')
    if te <= ts or te > hi:
        raise SystemExit('unbalanced <table> inside #%s' % card_id)
    return text[:ts] + ref_table(rows) + text[te:]


def _set_badge(text, card_id, n):
    """Set the first <span class="count-badge"> in card_id's header to '<n> functions'."""
    i = text.find('<div id="%s"' % card_id)
    if i < 0:
        return text
    bs = text.find('<span class="count-badge">', i)
    be = text.find('</span>', bs)
    return text[:bs + len('<span class="count-badge">')] + ('%d functions' % n) + text[be:]


def main():
    text = open(PATH).read()
    before = eb.balance_report(text)

    for cid, rows in CARDS.items():
        text = _replace_table(text, cid, rows)
        text = _set_badge(text, cid, len(rows))
    for fid in FAMILY_IDS:
        text = _set_badge(text, fid, len(REF[fid]))

    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if (after['div_open'] != after['div_close']
            or after['details_open'] != after['details_close']
            or after['final_depth'] != 0 or after['min_depth'] < 0):
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('Re-synced %d reference tables (+ badges) from REF into %s'
          % (len(CARDS), os.path.basename(PATH)))


if __name__ == '__main__':
    main()
