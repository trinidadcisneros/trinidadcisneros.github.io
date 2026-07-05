"""Sync the DATE / TIME function reference table into BOTH places that show it:
  1) the Functions hub  -> #fn-date-ref  (Functions: Parse, Clean & Convert > Date / time functions)
  2) the Date Operations recipe -> #mo-date-ref (new card)

SINGLE SOURCE OF TRUTH: REF['fn-date'] in build_fn_container.py (+ ref_table renderer).
This script renders that once and writes it between AUTO markers in both cards, so a future
edit to REF['fn-date'] propagates to both by just re-running this. Idempotent + balance-checked.

Run:  python3 sync_date_ref.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from build_fn_container import REF, ref_table, PATH   # single source + renderer
import eabuild as eb

START = '<!--DATE-FN-REF:START (auto-generated from REF[\'fn-date\'] by sync_date_ref.py — do not hand-edit)-->'
END = '<!--DATE-FN-REF:END-->'
TABLE = ref_table(REF['fn-date'])
BLOCK = START + TABLE + END
N = len(REF['fn-date'])


def _match_div(text, start):
    """Return index just past the </div> that closes the <div ...> at `start`."""
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
    open_end = co + len('<div class="problem-card-content">')
    close_start = ce - len('</div>')
    return open_end, close_start


def main():
    text = open(PATH).read()
    before = eb.balance_report(text)

    if START in text:
        # Re-run: refresh every marker region from the single source.
        text = re.sub(re.escape(START) + r'.*?' + re.escape(END), lambda _m: BLOCK, text, flags=re.S)
        print('Re-synced %d marker region(s) from REF[\'fn-date\'] (%d functions).'
              % (text.count(START), N))
    else:
        # First run: (1) wrap ONLY the leading reference TABLE inside #fn-date-ref
        #                (its helper trees — EXTRACT / TO_CHAR / duration — sit AFTER the
        #                 table in the same content div and must be left untouched);
        #            (2) insert a new #mo-date-ref card (table only) into Date Operations.
        i = text.find('<div id="fn-date-ref"')
        if i < 0:
            raise SystemExit('#fn-date-ref not found')
        ts = text.find('<table', i)
        te = text.find('</table>', ts) + len('</table>')
        if ts < 0 or te < len('</table>'):
            raise SystemExit('reference table inside #fn-date-ref not found')
        text = text[:ts] + BLOCK + text[te:]

        card = (
            '\n<div id="mo-date-ref" class="problem-card collapsed qtype-group">\n'
            '                <div class="problem-card-header"><h3 class="problem-card-title" style="margin:0;">Date / time function reference <span class="count-badge">%d functions</span></h3><span class="problem-toggle">&#9660;</span></div>\n'
            '                <div class="problem-card-excerpt"><p style="margin:0;">The same reference shown in the Functions hub &mdash; every example is run in real PostgreSQL. <a href="#functions" onclick="jumpToRecipe(\'fn-date\'); return false;">Open the Functions hub &rarr;</a></p></div>\n'
            '                <div class="problem-card-content">%s</div>\n'
            '              </div>\n' % (N, BLOCK)
        )
        do = text.find('<div id="do-decide"')
        if do < 0:
            raise SystemExit('do-decide (Date Operations tree) not found')
        de = _match_div(text, do)   # insert right after the decision-tree card, before the leaves
        text = text[:de] + card + text[de:]
        print('First run: wrapped #fn-date-ref table in markers and inserted #mo-date-ref.')

    # Keep both count-badges in sync with the single source (they sit outside the markers).
    for cid in ('fn-date-ref', 'mo-date-ref'):
        ci = text.find('<div id="%s"' % cid)
        if ci < 0:
            continue
        bs = text.find('<span class="count-badge">', ci)
        be = text.find('</span>', bs)
        text = text[:bs + len('<span class="count-badge">')] + ('%d functions' % N) + text[be:]

    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if (after['div_open'] != after['div_close']
            or after['details_open'] != after['details_close']
            or after['final_depth'] != 0 or after['min_depth'] < 0):
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE date reference to #fn-date-ref and #mo-date-ref in %s' % PATH)


if __name__ == '__main__':
    main()
