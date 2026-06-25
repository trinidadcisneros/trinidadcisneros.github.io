"""Add a collapsible accordion to the fn-date Function reference (inside fn-date-ref) listing
the EXTRACT(x FROM d) field options and their values for one example timestamp. Every value is
verified in real PostgreSQL. Idempotent + balance-checked.
Run:  python3 build_fn_date_extract.py
"""
import re, os, sys, html as _html
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
E = lambda s: _html.escape(str(s), quote=False)
ACC_ID = 'fn-date-extract-fields'
TS = "TIMESTAMP '2024-03-15 14:30:45'"

# (field, meaning) — values are computed live in Postgres so they can't drift
FIELDS = [
    ("YEAR", "calendar year"),
    ("QUARTER", "quarter of the year, 1-4"),
    ("MONTH", "month, 1-12"),
    ("WEEK", "ISO week of the year, 1-53"),
    ("DAY", "day of the month, 1-31"),
    ("DOW", "day of week, 0 = Sunday .. 6 = Saturday"),
    ("ISODOW", "day of week, 1 = Monday .. 7 = Sunday"),
    ("DOY", "day of the year, 1-366"),
    ("HOUR", "hour, 0-23"),
    ("MINUTE", "minute, 0-59"),
    ("SECOND", "second (with fractional part)"),
    ("EPOCH", "seconds since 1970-01-01 (Unix time)"),
]


def compute():
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        def s(q):
            return srv.psql("\\pset tuples_only on\n\\pset format unaligned\n" + q).strip().splitlines()[-1]
        return [(f, m, s(f"SELECT EXTRACT({f} FROM {TS});")) for f, m in FIELDS]
    finally:
        srv.cleanup()


def table(rows):
    head = ('<table style="border-collapse:collapse; font-size:1.1rem; margin:0;">'
            '<thead><tr style="border-bottom:2px solid #cbd5e1;">'
            '<th style="text-align:left; padding:6px 18px 6px 0;">Field (the x)</th>'
            '<th style="text-align:left; padding:6px 18px 6px 0;">What it pulls</th>'
            '<th style="text-align:left; padding:6px 0;">Result</th></tr></thead><tbody>')
    body = ''
    for i, (f, m, v) in enumerate(rows):
        z = ' background:#f7f9fb;' if i % 2 else ''
        body += ('<tr style="border-bottom:1px solid #eef2f7;%s">'
                 '<td style="padding:6px 18px 6px 0;"><code>%s</code></td>'
                 '<td style="padding:6px 18px 6px 0; color:#475569;">%s</td>'
                 '<td style="padding:6px 0;"><code>%s</code></td></tr>' % (z, E(f), E(m), E(v)))
    return head + body + '</tbody></table>'


def accordion(rows):
    return ('<div id="%s" class="problem-card collapsed" style="margin: 12px 0 4px; border-left:4px solid #1565c0;">'
            '<div class="problem-card-header"><h3 class="problem-card-title" style="margin:0; font-size:1.15rem;">'
            '&#128270; EXTRACT field options &mdash; the <code>x</code> in <code>EXTRACT(x FROM d)</code> '
            '<span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to expand)</span></h3>'
            '<span class="problem-toggle">&#9660;</span></div>'
            '<div class="problem-card-excerpt"><p style="margin:0;">Every part you can pull, shown for '
            '<code>%s</code> (a Friday). All values run in real PostgreSQL.</p></div>'
            '<div class="problem-card-content">%s</div></div>' % (ACC_ID, E(TS), table(rows)))


def main():
    text = open(PATH).read()
    if 'id="%s"' % ACC_ID in text:
        print('accordion already present; nothing to do.'); return
    rows = compute()
    print('Computed', len(rows), 'EXTRACT fields:', {f: v for f, _, v in rows})
    before = eb.balance_report(text)
    # locate the fn-date-ref card, insert the accordion right after its reference table
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
    block = text[s:e]
    marker = block.rfind('</tbody></table>')
    if marker < 0:
        raise SystemExit('reference table not found in fn-date-ref')
    cut = s + marker + len('</tbody></table>')
    text = text[:cut] + accordion(rows) + text[cut:]
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE EXTRACT-fields accordion into fn-date-ref')


if __name__ == '__main__':
    main()
