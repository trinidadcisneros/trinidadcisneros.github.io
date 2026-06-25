"""Primary: add rp-multi-distincton leaf (template + Postgres-verified worked card)
to the Rank Within Groups recipe. Pointer: add a signpost in the Single-Table Filter
recipe linking to it. Idempotent + balance-checked.
Run:  python3 build_rp_distincton.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Easy', 'color': '#2e7d32',
    'title': 'Most Recent Order per Customer (DISTINCT ON)',
    'excerpt': "One row per customer — their latest order — with the Postgres DISTINCT ON shortcut.",
    'prompt': [
        "Return each customer's MOST RECENT order: exactly one row per customer.",
        "The <code>orders</code> table has one row per order with its <code>order_date</code> and <code>amount</code>.",
        "Use the order with the latest <code>order_date</code> for each customer (no two of a customer's orders share a date here).",
        "Return <code>customer_id</code>, <code>order_id</code>, <code>amount</code>, ordered by <code>customer_id</code>.",
    ],
    'inputs': [{
        'name': 'orders',
        'cols': [('order_id', 'INTEGER'), ('customer_id', 'INTEGER'), ('order_date', 'DATE'), ('amount', 'DECIMAL(8,2)')],
        'headers': ['order_id', 'customer_id', 'order_date', 'amount'],
        'rows': [
            [1, 101, '2024-03-01', '50.00'], [2, 101, '2024-03-10', '80.00'],
            [3, 102, '2024-02-15', '30.00'],
            [4, 103, '2024-03-05', '20.00'], [5, 103, '2024-03-20', '40.00'],
        ],
    }],
    'exp_headers': ['customer_id', 'order_id', 'amount'],
    'exp_rows': [[101, 2, '80.00'], [102, 3, '30.00'], [103, 5, '40.00']],
    'sol_comment': (
        "DISTINCT ON (customer_id) keeps ONE row per customer -- the FIRST one in the sort order. The\n"
        "ORDER BY does two jobs: it must START with customer_id (the DISTINCT ON column -- Postgres\n"
        "errors otherwise), and then order_date DESC decides WHICH of that customer's rows is first, so\n"
        "the newest order survives and order_id / amount ride along from that row.\n"
        "Portable equivalent: ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) and\n"
        "keep rn = 1. If two orders could share the latest date, add a tiebreaker (e.g. order_id DESC)\n"
        "as a second ORDER BY key. Verified against the example data."
    ),
    'sol_sql': (
        "SELECT DISTINCT ON (customer_id)         -- one row per customer ...\n"
        "       customer_id, order_id, amount\n"
        "FROM orders\n"
        "ORDER BY customer_id,                    -- ... ORDER BY must start with the DISTINCT ON column ...\n"
        "         order_date DESC;                -- ... then newest first picks the winner"
    ),
}

TEMPLATE = '''<div id="rp-tmpl-distincton" class="problem-card collapsed" style="margin: 0 0 10px 0;">
                      <div class="problem-card-header">
                        <h3 class="problem-card-title" style="margin: 0;">DISTINCT ON: one row per group, the Postgres shortcut</h3>
                        <span class="problem-toggle">&#9660;</span>
                      </div>
                      <div class="problem-card-excerpt">
                        <p style="margin:0;">Use when: you want a single representative row per group &mdash; the newest by a date, or the highest by a value &mdash; and you are on Postgres.</p>
                      </div>
                      <div class="problem-card-content">
                        <p style="margin:0 0 6px;"><strong>What this template does, step by step:</strong></p>
                        <ol style="margin:0 0 10px 18px; line-height:1.7;">
                          <li><code>DISTINCT ON (group_col)</code> keeps ONE row per group &mdash; the FIRST one in the sort order.</li>
                          <li>The <code>ORDER BY</code> MUST start with the same <code>group_col</code>, then the column that decides the winner (<code>date DESC</code> for newest, <code>value DESC</code> for highest). Postgres errors if the ORDER BY does not begin with the DISTINCT ON column.</li>
                          <li>This is the Postgres one-liner for top-1-per-group; the portable equivalent is <code>ROW_NUMBER() OVER (PARTITION BY group_col ORDER BY winner_col DESC)</code> with <code>WHERE rn = 1</code>.</li>
                          <li>Ties on the winner column: add a second ORDER BY key (e.g. <code>id DESC</code>) so the choice is deterministic.</li>
                        </ol>
                        <pre style="margin:0 0 6px; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>SELECT DISTINCT ON (group_col) group_col, val
FROM t
ORDER BY group_col, winner_col DESC;   -- one row per group, the newest / highest</code></pre>
                      </div>
                    </div>'''

LEAF = '''<div id="rp-multi-distincton" class="problem-card collapsed qtype-group">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0;">Top 1 per group with <code>DISTINCT ON</code> (Postgres shortcut) <span class="count-badge">1 problem</span></h3>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt">
                  <p style="margin: 0;"><code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">nb01 qtype: window_top_n_per_group (distinct_on flavor)</code> &mdash; keep ONE representative row per group (newest by date or highest by value) using <code>SELECT DISTINCT ON (group) ... ORDER BY group, winner DESC</code>. Same result as ROW_NUMBER rn=1, fewer keystrokes. Postgres only.</p>
                </div>
                <div class="problem-card-content">
                    %s
              %s
                </div>
              </div>''' % (TEMPLATE, eb.build_card(CARD))

POINTER = '''<div style="margin: 12px 0; padding: 12px 16px; background: #fff8e1; border-left: 4px solid #f57f17; font-size: 1.1rem; color: #5d4037; border-radius: 4px;">
                <strong>Looking for <code>DISTINCT ON</code> (keep one row per group)?</strong> That is not a WHERE filter &mdash; it picks one representative row per group (the newest or highest), so it lives in <a href="#rp-multi-distincton" style="color:#1565c0; font-weight:600;">Multi-Table &rsaquo; Rank Within Groups &rsaquo; Top 1 with DISTINCT ON &rarr;</a>
              </div>'''


def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        inp = card['inputs'][0]
        srv.psql('CREATE TABLE %s (%s);' % (inp['name'], ', '.join('%s %s' % (n, t) for n, t in inp['cols'])))
        cn = ', '.join(n for n, _ in inp['cols'])
        for row in inp['rows']:
            srv.psql('INSERT INTO %s (%s) VALUES (%s);' % (inp['name'], cn, ', '.join(_lit(v) for v in row)))
        out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + card['sol_sql'])
        ncols = len(card['exp_headers'])
        got = [tuple(l.split('|')) for l in out.strip().splitlines()
               if l.count('|') == ncols - 1 and 'format is' not in l and 'separator is' not in l]
        exp = [tuple(str(x) for x in r) for r in card['exp_rows']]
        return got == exp, got, exp
    finally:
        srv.cleanup()


def _lit(v):
    s = str(v)
    return s if re.match(r'^-?\d+(\.\d+)?$', s) else "'" + s.replace("'", "''") + "'"


def balance(t):
    do = len(re.findall(r'<div\b', t)); dc = len(re.findall(r'</div\b', t))
    deto = len(re.findall(r'<details\b', t)); detc = len(re.findall(r'</details\b', t))
    d = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', t):
        d += 1 if m.group(1) == '' else -1; mn = min(mn, d)
    return do, dc, deto, detc, d, mn


def div_end(text, start):
    depth = 0
    for m in re.finditer(r'<(/?)div\b', text[start:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            return text.find('>', start + m.start()) + 1
    raise SystemExit('unbalanced div from %d' % start)


def main():
    ok, got, exp = verify_pg(CARD)
    print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', CARD['title']))
    if not ok:
        print('  GOT', got); print('  EXP', exp); raise SystemExit('verify failed')
    text = open(PATH).read()
    if 'id="rp-multi-distincton"' in text:
        print('already present; nothing to do.'); return
    before = balance(text)
    # 1) insert leaf after rp-multi-special
    s = text.find('<div class="problem-card collapsed qtype-group" id="rp-multi-special">')
    if s < 0:
        s = text.find('id="rp-multi-special"'); s = text.rfind('<div', 0, s)
    e = div_end(text, s)
    text = text[:e] + '\n\n              ' + LEAF + '\n' + text[e:]
    # 2) insert pointer after the rf-decide container
    rs = text.find('id="rf-decide"'); rs = text.rfind('<div', 0, rs)
    re_ = div_end(text, rs)
    text = text[:re_] + '\n              ' + POINTER + '\n' + text[re_:]
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE rp-multi-distincton leaf + Filter pointer')


if __name__ == '__main__':
    main()
