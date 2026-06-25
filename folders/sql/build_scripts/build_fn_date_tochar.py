"""In the fn-date Function reference: (1) regenerate the reference table from the reverted
REF['fn-date'] (drops the 3 inline month/weekday-name rows), and (2) add a collapsible
accordion listing the TO_CHAR(ts, fmt) format patterns and their values for one example
timestamp (mirrors the EXTRACT-fields accordion). Every value computed live in PostgreSQL.
Idempotent + balance-checked.
Run:  python3 build_fn_date_tochar.py
"""
import re, os, sys, html as _html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
import build_fn_container as bf
PATH = bf.PATH
E = lambda s: _html.escape(str(s), quote=False)
ACC_ID = 'fn-date-tochar-formats'
TS = "TIMESTAMP '2024-12-23 09:08:07'"
TABLE_HEAD = '<table style="border-collapse:collapse; font-size:1.15rem; margin:0 0 6px; width:100%;">'

PATTERNS = [
    ("YYYY", "4-digit year"),
    ("YY", "2-digit year"),
    ("MM", "month number 01-12 (zero-padded)"),
    ("Mon", "short month name"),
    ("Month", "full month name; PADS to width 9 with trailing spaces"),
    ("FMMonth", "full month name, no padding (FM trims)"),
    ("DD", "day of month, zero-padded"),
    ("FMDD", "day of month, no padding"),
    ("Dy", "short weekday name"),
    ("Day", "full weekday name; PADS with spaces"),
    ("FMDay", "full weekday name, no padding"),
    ("D", "weekday number 1-7 (1 = Sunday)"),
    ("ID", "ISO weekday 1-7 (1 = Monday)"),
    ("DDD", "day of the year"),
    ("HH24", "hour 00-23"),
    ("HH12", "hour 01-12"),
    ("MI", "minute"),
    ("SS", "second"),
    ("AM", "AM / PM marker"),
    ("WW", "week of the year"),
    ("Q", "quarter"),
    ("YYYY-MM-DD HH24:MI", "combined: date and time to the minute"),
    ("FMMonth DD, YYYY", "combined: a long date"),
    ("FMDy HH12:MI AM", "combined: short weekday and 12-hour clock"),
]


def compute():
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        def val(p):
            out = srv.psql("\\pset tuples_only on\n\\pset format unaligned\nSELECT TO_CHAR(%s,'%s');" % (TS, p.replace("'", "''")))
            line = out.strip('\n').split('\n')[-1]      # keep internal/trailing spaces
            return re.sub(r' +$', lambda m: '·' * len(m.group()), line)  # show trailing pad as middots
        return [(p, m, val(p)) for p, m in PATTERNS]
    finally:
        srv.cleanup()


def table(rows):
    head = ('<table style="border-collapse:collapse; font-size:1.1rem; margin:0;">'
            '<thead><tr style="border-bottom:2px solid #cbd5e1;">'
            '<th style="text-align:left; padding:6px 18px 6px 0;">Pattern (the fmt)</th>'
            '<th style="text-align:left; padding:6px 18px 6px 0;">What it prints</th>'
            '<th style="text-align:left; padding:6px 0;">Result</th></tr></thead><tbody>')
    body = ''
    for i, (p, m, v) in enumerate(rows):
        z = ' background:#f7f9fb;' if i % 2 else ''
        body += ('<tr style="border-bottom:1px solid #eef2f7;%s">'
                 '<td style="padding:6px 18px 6px 0;"><code>%s</code></td>'
                 '<td style="padding:6px 18px 6px 0; color:#475569;">%s</td>'
                 '<td style="padding:6px 0;"><code>%s</code></td></tr>' % (z, E(p), E(m), E(v)))
    return head + body + '</tbody></table>'


def accordion(rows):
    note = ('<p style="margin:0 0 8px; color:#475569;">Stitch patterns together with your own separators '
            '(<code>-</code>, <code>:</code>, spaces). Any plain letters you want kept literally go in '
            'double quotes, e.g. <code>TO_CHAR(ts, \'"Yr" YYYY\')</code>. The <code>FM</code> prefix removes the '
            'space / zero padding.</p>')
    return ('<div id="%s" class="problem-card collapsed" style="margin: 8px 0 4px; border-left:4px solid #1565c0;">'
            '<div class="problem-card-header"><h3 class="problem-card-title" style="margin:0; font-size:1.15rem;">'
            '&#128270; TO_CHAR format patterns &mdash; the <code>fmt</code> in <code>TO_CHAR(ts, fmt)</code> '
            '<span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to expand)</span></h3>'
            '<span class="problem-toggle">&#9660;</span></div>'
            '<div class="problem-card-excerpt"><p style="margin:0;">Common date / time format codes, shown for '
            '<code>%s</code>. A trailing <code>&middot;</code> marks space padding. All run in real PostgreSQL.</p></div>'
            '<div class="problem-card-content">%s%s</div></div>' % (ACC_ID, E(TS), note, table(rows)))


def main():
    text = open(PATH).read()
    before = eb.balance_report(text)

    # (1) regenerate the reference table from the (reverted) REF
    s = text.find('id="fn-date-ref"')
    s = text.rfind('<div', 0, s)
    depth = 0; e = None
    for m in re.finditer(r'<(/?)div\b', text[s:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            e = text.find('>', s + m.start()) + 1
            break
    tstart = text.find(TABLE_HEAD, s, e)
    tend = text.find('</tbody></table>', tstart, e) + len('</tbody></table>')
    text = text[:tstart] + bf.ref_table(bf.REF['fn-date']) + text[tend:]

    # (2) add the TO_CHAR accordion after the EXTRACT-fields accordion (idempotent)
    if 'id="%s"' % ACC_ID not in text:
        rows = compute()
        print('Computed', len(rows), 'TO_CHAR patterns')
        a = text.find('id="fn-date-extract-fields"')
        a = text.rfind('<div', 0, a)
        depth = 0; ae = None
        for m in re.finditer(r'<(/?)div\b', text[a:]):
            depth += 1 if m.group(1) == '' else -1
            if depth == 0:
                ae = text.find('>', a + m.start()) + 1
                break
        text = text[:ae] + accordion(rows) + text[ae:]
    else:
        print('TO_CHAR accordion already present; only regenerated the table.')

    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE: reverted fn-date table to %d rows + TO_CHAR accordion' % len(bf.REF['fn-date']))


if __name__ == '__main__':
    main()
