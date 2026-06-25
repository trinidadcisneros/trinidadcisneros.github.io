"""Append a SECOND annotated solution (Trinidad's LEFT JOIN + ROW_NUMBER variant)
to the existing 'Daily Price per SKU' fill-forward card in pit-leaf-fill. Same
problem, the 'rank the candidates' route. Verified in real Postgres (pgserver).
Inserted as the last child of that card's content. Idempotent + balance-checked.
Run:  python3 build_pit_fill_rownumber_sol.py
"""
import re, os, sys, html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
CARD_TITLE = 'Daily Price per SKU (Fill Forward, keeping NULL before the first change)'
SENTINEL = 'rank the candidates per (SKU, day)'   # unique to this new solution card

SQL = """/*
  Same result as the as-of subquery above, the \"rank the candidates\" way.
  spine        : every SKU x every day in the range.
  candidates   : LEFT JOIN every price effective on/before each day, matched on the SKU.
                 A day with no earlier price keeps one NULL row -- this is what preserves the NULLs.
  newest_first : ROW_NUMBER per (sku, day), newest effective_date first.
  final        : keep rn = 1 -> the price in effect, or NULL before the SKU's first change.
  Two bugs to avoid: p.sku = p.sku (self-compare matches EVERY SKU) and PARTITION BY date alone
  (must be PARTITION BY sku, date). Verified against the example data -- 30 rows, 12 NULL.
*/

WITH spine AS (
    SELECT s.sku, d.date
    FROM (SELECT DISTINCT sku FROM kit_pricing) AS s
    CROSS JOIN (
        SELECT generate_series(DATE '2024-01-01', DATE '2024-01-10', INTERVAL '1 day')::date AS date
    ) AS d
),
candidates AS (
    SELECT sp.sku,
           sp.date,
           p.effective_date,                  -- kept visible so you can see what matched
           p.price
    FROM spine sp
    LEFT JOIN kit_pricing p
           ON p.sku = sp.sku                   -- correlate on the SKU ...
          AND p.effective_date <= sp.date      -- ... and on or before the day
),
newest_first AS (
    SELECT sku, date, effective_date, price,
           ROW_NUMBER() OVER (PARTITION BY sku, date ORDER BY effective_date DESC) AS rn
    FROM candidates
)
SELECT sku,
       date,
       price AS price_in_effect               -- keep the newest; NULL stays when nothing in effect yet
FROM newest_first
WHERE rn = 1
ORDER BY sku, date;"""

SOLUTION_CARD = '''<!-- SOLUTION 2 (LEFT JOIN + ROW_NUMBER variant) -->
              <div class="problem-card collapsed" style="margin: 12px 0 0;">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0; display: flex; align-items: center; gap: 15px;">
                    <span style="display: inline-block; background-color: #2e7d32; color: white; padding: 4px 10px; border-radius: 3px; font-size: 1.328rem; font-weight: 600;">Solution 2</span>
                    Annotated SQL &mdash; LEFT JOIN + ROW_NUMBER (rank the candidates per (SKU, day))
                  </h3>
                  <button class="tpl-copy" type="button" onclick="event.stopPropagation(); copyTplCode(this);">Copy</button>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt"><p style="margin:0;">Same answer, a different route: instead of an as-of subquery, attach every earlier price to each day and keep the newest with <code>ROW_NUMBER</code>.</p></div>
                <div class="problem-card-content">
                  <p style="margin:0 0 6px;"><strong>How it works, step by step:</strong></p>
                  <ol style="margin:0 0 10px 18px; line-height:1.7;">
                    <li><strong>spine</strong> &mdash; every SKU paired with every day in the range (<code>DISTINCT</code> skus <code>CROSS JOIN</code> the date series).</li>
                    <li><strong>candidates</strong> &mdash; <code>LEFT JOIN</code> every price that took effect on or before each day, matched on the SKU. A (sku, day) with no earlier price keeps a single NULL row &mdash; this is what preserves the NULLs.</li>
                    <li><strong>newest_first</strong> &mdash; <code>ROW_NUMBER()</code> per <code>(sku, date)</code>, newest <code>effective_date</code> first.</li>
                    <li>Keep <code>rn = 1</code>: the most recent price, or NULL when nothing was in effect yet.</li>
                  </ol>
                  <pre style="margin:0 0 10px; background:#1e1e1e; color:#d4d4d4; padding:12px 14px; border-radius:4px; font-size:1.2rem; line-height:1.55; white-space:pre-wrap;"><code>%s</code></pre>
                </div>
              </div>''' % _html.escape(SQL, quote=False)


def verify_pg():
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        srv.psql('CREATE TABLE kit_pricing(sku varchar(20), effective_date date, price decimal(10,2));')
        srv.psql("INSERT INTO kit_pricing VALUES "
                 "('KIT-A','2024-01-01',49.99),('KIT-A','2024-01-05',54.99),('KIT-A','2024-01-08',52.99),"
                 "('KIT-B','2024-01-03',39.99),('KIT-B','2024-01-07',44.99),('KIT-C','2024-01-12',29.99);")
        runnable = SQL[SQL.index('WITH'):]
        out = srv.psql('\\pset tuples_only on\n\\pset format unaligned\n\\pset fieldsep |\n' + runnable)
        rows = [r for r in out.strip().splitlines() if '|' in r and 'format' not in r and 'separator' not in r]
        nulls = [r for r in rows if r.endswith('|')]
        return len(rows) == 30 and len(nulls) == 12
    finally:
        srv.cleanup()


def balance(t):
    do = len(re.findall(r'<div\b', t)); dc = len(re.findall(r'</div\b', t))
    deto = len(re.findall(r'<details\b', t)); detc = len(re.findall(r'</details\b', t))
    d = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', t):
        d += 1 if m.group(1) == '' else -1; mn = min(mn, d)
    return do, dc, deto, detc, d, mn


def card_content_close(text, title):
    ti = text.find(title)
    if ti < 0:
        raise SystemExit('card title not found')
    cstart = text.rfind('<div class="problem-card collapsed" style="margin: 0 0 16px 0;">', 0, ti)
    content = text.find('<div class="problem-card-content">', cstart)
    depth = 0
    for m in re.finditer(r'<(/?)div\b', text[content:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            return content + m.start()
    raise SystemExit('could not balance the card content')


def main():
    if not verify_pg():
        raise SystemExit('pg verify failed (expected 30 rows / 12 NULL); nothing written')
    print('[pg-verify OK] LEFT JOIN + ROW_NUMBER variant (30 rows, 12 NULL)')
    text = open(PATH).read()
    if SENTINEL in text:
        print('solution 2 already present; nothing to do.'); return
    before = balance(text)
    ins = card_content_close(text, CARD_TITLE)
    text = text[:ins] + '\n              ' + SOLUTION_CARD + '\n              ' + text[ins:]
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE Solution 2 (ROW_NUMBER variant) into the Daily Price per SKU card')


if __name__ == '__main__':
    main()
