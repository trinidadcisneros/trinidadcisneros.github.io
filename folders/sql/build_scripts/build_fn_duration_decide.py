"""Add a collapsible 'duration: total elapsed vs one component' decision accordion to BOTH the
Date Operations duration leaf (do-leaf-duration) and the fn-date Function reference (after the
TO_CHAR accordion). Explains EXTRACT(EPOCH ...)/divisor (TOTAL) vs EXTRACT(part ...) (one slot),
with a verified worked contrast. Idempotent + balance-checked.
Run:  python3 build_fn_duration_decide.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

PRE = 'margin:0; background:#1e1e1e; color:#d4d4d4; padding:9px 11px; border-radius:4px; font-size:1.05rem; line-height:1.5; white-space:pre-wrap;'

# verified for  a - b = 2 days 03:00:00  (a gap of 51 hours)
EXAMPLE = [
    ("EXTRACT(HOUR FROM diff)", "3", "just the HOUR slot"),
    ("EXTRACT(EPOCH FROM diff) / 3600", "51", "TOTAL hours"),
    ("EXTRACT(DAY FROM diff)", "2", "just the DAY slot"),
    ("EXTRACT(EPOCH FROM diff) / 86400", "2.125", "TOTAL days"),
    ("EXTRACT(MINUTE FROM diff)", "0", "just the MINUTE slot"),
    ("AGE(a, b)", "2 days 03:00:00", "human y / m / d interval"),
]


def _ex_table():
    head = ('<table style="border-collapse:collapse; font-size:1.1rem; margin:0;">'
            '<thead><tr style="border-bottom:2px solid #cbd5e1;">'
            '<th style="text-align:left; padding:6px 18px 6px 0;">Expression</th>'
            '<th style="text-align:left; padding:6px 18px 6px 0;">Result</th>'
            '<th style="text-align:left; padding:6px 0;">What it is</th></tr></thead><tbody>')
    body = ''
    for i, (e, r, w) in enumerate(EXAMPLE):
        z = ' background:#f7f9fb;' if i % 2 else ''
        body += ('<tr style="border-bottom:1px solid #eef2f7;%s">'
                 '<td style="padding:6px 18px 6px 0;"><code>%s</code></td>'
                 '<td style="padding:6px 18px 6px 0;"><code>%s</code></td>'
                 '<td style="padding:6px 0; color:#475569;">%s</td></tr>' % (z, e, r, w))
    return head + body + '</tbody></table>'


def accordion(acc_id):
    return (
        '<div id="%s" class="problem-card collapsed" style="margin: 12px 0 4px; border-left:4px solid #6a1b9a;">'
        '<div class="problem-card-header"><h3 class="problem-card-title" style="margin:0; font-size:1.15rem;">'
        '&#128270; Duration: TOTAL elapsed time vs ONE component &mdash; which EXTRACT? '
        '<span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to expand)</span></h3>'
        '<span class="problem-toggle">&#9660;</span></div>'
        '<div class="problem-card-excerpt"><p style="margin:0;">Subtracting two timestamps gives an INTERVAL &mdash; '
        'what you pull out of it changes the answer a lot.</p></div>'
        '<div class="problem-card-content">'
        '<p style="margin:0 0 8px;"><strong>What do you need from the gap between two timestamps (call it <code>diff = a - b</code>)?</strong></p>'
        '<div style="display:flex; gap:12px; flex-wrap:wrap; margin:0 0 12px;">'
        # branch 1: total
        '<div style="flex:1 1 290px; border:1px solid #cdddf0; border-left:4px solid #1565c0; border-radius:6px; padding:10px 12px; background:#f5f9fe;">'
        '<div style="font-weight:700; color:#0d47a1; margin-bottom:4px;">TOTAL elapsed time</div>'
        '<p style="margin:0 0 6px; color:#1a237e;">&ldquo;how many hours / days in all.&rdquo; Turn the whole interval into seconds, then divide:</p>'
        '<pre style="%s"><code>EXTRACT(EPOCH FROM diff) / 3600    -- total HOURS\nEXTRACT(EPOCH FROM diff) / 86400   -- total DAYS\nEXTRACT(EPOCH FROM diff) / 60      -- total MINUTES</code></pre>'
        '<p style="margin:6px 0 0; color:#475569;">Want a human y / m / d breakdown instead? Use <code>AGE(a, b)</code>.</p>'
        '</div>'
        # branch 2: component
        '<div style="flex:1 1 290px; border:1px solid #f3d9c0; border-left:4px solid #e65100; border-radius:6px; padding:10px 12px; background:#fff8f2;">'
        '<div style="font-weight:700; color:#b45309; margin-bottom:4px;">ONE component (a single slot)</div>'
        '<p style="margin:0 0 6px; color:#7c3a06;">&ldquo;just the hours part.&rdquo; Reads only that field of the interval &mdash; it does NOT roll the days in:</p>'
        '<pre style="%s"><code>EXTRACT(HOUR FROM diff)     -- only the HOUR slot\nEXTRACT(DAY FROM diff)      -- only the DAY slot\nEXTRACT(MINUTE FROM diff)   -- only the MINUTE slot</code></pre>'
        '</div></div>'
        '<p style="margin:0 0 6px;"><strong>Same gap, very different answers</strong> &mdash; for <code>diff = 2 days 03:00:00</code> (a gap of 51 hours), run in real PostgreSQL:</p>'
        '%s'
        '<p style="margin:10px 0 0; padding:9px 13px; background:#f3e9f7; border-left:4px solid #6a1b9a; color:#4a148c;">'
        '<strong>Takeaway:</strong> <code>EXTRACT(part FROM interval)</code> reads ONE slot (3 here); '
        '<code>EXTRACT(EPOCH FROM interval) / divisor</code> gives the WHOLE elapsed total (51 here). '
        'For &ldquo;turnaround in hours&rdquo; you almost always want <code>EPOCH / 3600</code>.</p>'
        '</div></div>'
        % (acc_id, PRE, PRE, _ex_table())
    )


def _balanced_end(text, start_div):
    depth = 0
    for m in re.finditer(r'<(/?)div\b', text[start_div:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            return text.find('>', start_div + m.start()) + 1
    raise SystemExit('unbalanced from %d' % start_div)


def main():
    text = open(PATH).read()
    before = eb.balance_report(text)

    # 1) Date Operations duration leaf — after the EPOCH worked card, inside the leaf
    if 'id="do-duration-decide"' not in text:
        anchor = "FROM tickets\nORDER BY ticket_id;</code></pre>\n                </div>\n              </div>\n"
        assert text.count(anchor) == 1, ('do anchor', text.count(anchor))
        text = text.replace(anchor, anchor + "              " + accordion('do-duration-decide') + "\n", 1)
        print('inserted do-duration-decide')
    else:
        print('do-duration-decide already present')

    # 2) fn-date reference — after the TO_CHAR formats accordion
    if 'id="fn-date-duration-decide"' not in text:
        s = text.find('id="fn-date-tochar-formats"')
        s = text.rfind('<div', 0, s)
        e = _balanced_end(text, s)
        text = text[:e] + accordion('fn-date-duration-decide') + text[e:]
        print('inserted fn-date-duration-decide')
    else:
        print('fn-date-duration-decide already present')

    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE duration-decide accordion into both containers')


if __name__ == '__main__':
    main()
