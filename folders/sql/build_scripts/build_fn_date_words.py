"""Regenerate the fn-date Function reference table in the playbook from the (now updated)
REF['fn-date'] in build_fn_container.py — adds the TO_CHAR month/weekday NAME rows
(FMMonth -> December, FMDay -> Monday, Mon -> Dec). Replaces only the reference table inside
fn-date-ref; the EXTRACT-fields accordion below it is untouched. Balance-checked.
Run:  python3 build_fn_date_words.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
import build_fn_container as bf
PATH = bf.PATH

TABLE_HEAD = '<table style="border-collapse:collapse; font-size:1.15rem; margin:0 0 6px; width:100%;">'


def main():
    text = open(PATH).read()
    if "TO_CHAR(DATE '2024-12-23','FMMonth')" in text:
        print('month/weekday name rows already present; nothing to do.'); return
    before = eb.balance_report(text)
    # bound the fn-date-ref card
    s = text.find('id="fn-date-ref"')
    if s < 0:
        raise SystemExit('fn-date-ref not found')
    s = text.rfind('<div', 0, s)
    depth = 0; e = None
    for m in re.finditer(r'<(/?)div\b', text[s:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            e = text.find('>', s + m.start()) + 1
            break
    # the reference table = first 1.15rem table in the card, up to its </tbody></table>
    tstart = text.find(TABLE_HEAD, s, e)
    if tstart < 0:
        raise SystemExit('reference table not found in fn-date-ref')
    tend = text.find('</tbody></table>', tstart, e) + len('</tbody></table>')
    new_table = bf.ref_table(bf.REF['fn-date'])
    text = text[:tstart] + new_table + text[tend:]
    after = eb.balance_report(text)
    print('rows now:', len(bf.REF['fn-date']))
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE updated fn-date reference table')


if __name__ == '__main__':
    main()
