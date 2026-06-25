"""Add a per-entity (multi-SKU) fill-forward worked card to pit-leaf-fill, the
'keep NULL before the first change' case. Maps to engine point_in_time/fill_forward.

Verified in real Postgres (pgserver). Inserted as the LAST child of the
pit-leaf-fill content; badge 1 -> 2. Idempotent + balance-checked.
Run:  python3 build_pit_fill_perentity.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
SENTINEL = 'Daily Price per SKU (Fill Forward, keeping NULL before the first change)'

# Build the 30 expected rows (3 SKUs x 10 days)
def _exp():
    rows = []
    a = {1:'49.99',2:'49.99',3:'49.99',4:'49.99',5:'54.99',6:'54.99',7:'54.99',8:'52.99',9:'52.99',10:'52.99'}
    b = {1:None,2:None,3:'39.99',4:'39.99',5:'39.99',6:'39.99',7:'44.99',8:'44.99',9:'44.99',10:'44.99'}
    for d in range(1, 11):
        rows.append(['KIT-A', '2024-01-%02d' % d, a[d]])
    for d in range(1, 11):
        rows.append(['KIT-B', '2024-01-%02d' % d, b[d]])
    for d in range(1, 11):
        rows.append(['KIT-C', '2024-01-%02d' % d, None])
    return rows

CARD = {
    'diff': 'Medium', 'color': '#e65100',
    'title': 'Daily Price per SKU (Fill Forward, keeping NULL before the first change)',
    'excerpt': "Fill forward PER SKU across a date range; a SKU shows NULL on days before its first price change. This is the multi-entity version of the template.",
    'prompt': [
        "The <code>kit_pricing</code> table records every price change for each kit SKU with an <code>effective_date</code>.",
        "Return the price in effect for EVERY day from <strong>2024-01-01 through 2024-01-10 inclusive</strong> for each SKU.",
        "On a day with no change, fill forward the most recent prior price. For days before a SKU's first change, return NULL.",
        "Return <code>sku</code>, <code>date</code>, <code>price_in_effect</code>, ordered by <code>sku</code>, <code>date</code>.",
    ],
    'inputs': [{
        'name': 'kit_pricing',
        'cols': [('sku', 'VARCHAR(20)'), ('effective_date', 'DATE'), ('price', 'DECIMAL(10,2)')],
        'headers': ['sku', 'effective_date', 'price'],
        'rows': [
            ['KIT-A', '2024-01-01', '49.99'], ['KIT-A', '2024-01-05', '54.99'], ['KIT-A', '2024-01-08', '52.99'],
            ['KIT-B', '2024-01-03', '39.99'], ['KIT-B', '2024-01-07', '44.99'],
            ['KIT-C', '2024-01-12', '29.99'],
        ],
    }],
    'exp_headers': ['sku', 'date', 'price_in_effect'],
    'exp_rows': _exp(),
    'sol_comment': (
        "Per-SKU fill forward, NULLs kept. Two moving parts:\n"
        "  calendar : every SKU paired with every day in the range (DISTINCT skus CROSS JOIN the spine).\n"
        "             This is what forces a row to exist on days a SKU had no change.\n"
        "  subquery : for each (sku, day) grab THAT sku's most recent price on or before the day. The\n"
        "             two correlations are the whole trick: p.sku = c.sku AND p.effective_date <= c.date.\n"
        "KIT-B has no change until Jan 3, so Jan 1-2 find nothing and come back NULL. KIT-C's first change\n"
        "is Jan 12, outside the window, so all 10 days are NULL. No COALESCE because the prompt wants NULL.\n"
        "Common bugs: writing p.sku = p.sku (always true -> mixes every SKU); partitioning / correlating on\n"
        "the date only and forgetting the sku.\n"
        "Verified against the example data -- 30 rows, KIT-B's first two days and all of KIT-C are NULL."
    ),
    'sol_sql': (
        "WITH calendar AS (                                  -- every SKU x every day in the range\n"
        "  SELECT s.sku, g.day::date AS date\n"
        "  FROM (SELECT DISTINCT sku FROM kit_pricing) s\n"
        "  CROSS JOIN generate_series(DATE '2024-01-01', DATE '2024-01-10', INTERVAL '1 day') AS g(day)\n"
        ")\n"
        "SELECT c.sku,\n"
        "       c.date,\n"
        "       (SELECT p.price                              -- this SKU's latest price on/before the day\n"
        "        FROM kit_pricing p\n"
        "        WHERE p.sku = c.sku                         -- correlate on the SKU ...\n"
        "          AND p.effective_date <= c.date            -- ... and on or before the day\n"
        "        ORDER BY p.effective_date DESC\n"
        "        LIMIT 1) AS price_in_effect                 -- before the first change -> NULL\n"
        "FROM calendar c\n"
        "ORDER BY c.sku, c.date;"
    ),
}


def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in card['inputs']:
            coldefs = ', '.join('%s %s' % (n, t) for n, t in inp['cols'])
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], coldefs))
            cn = ', '.join(n for n, _ in inp['cols'])
            for row in inp['rows']:
                srv.psql('INSERT INTO %s (%s) VALUES (%s);' % (inp['name'], cn, ', '.join(_lit(v) for v in row)))
        out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + card['sol_sql'])
        ncols = len(card['exp_headers'])
        got = [tuple(l.split('|')) for l in out.strip().splitlines()
               if l.count('|') == ncols - 1 and 'format is' not in l and 'separator is' not in l]
        exp = [tuple('' if x is None else str(x) for x in r) for r in card['exp_rows']]
        return got == exp, got[:3], exp[:3], len(got), len(exp)
    finally:
        srv.cleanup()


def _lit(v):
    if v is None:
        return 'NULL'
    s = str(v)
    return s if re.match(r'^-?\d+(\.\d+)?$', s) else "'" + s.replace("'", "''") + "'"


def balance(t):
    do = len(re.findall(r'<div\b', t)); dc = len(re.findall(r'</div\b', t))
    deto = len(re.findall(r'<details\b', t)); detc = len(re.findall(r'</details\b', t))
    d = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', t):
        d += 1 if m.group(1) == '' else -1; mn = min(mn, d)
    return do, dc, deto, detc, d, mn


def leaf_content_close(text, leaf_id):
    cstart = text.find('id="%s"' % leaf_id)
    cstart = text.rfind('<div', 0, cstart)
    content = text.find('<div class="problem-card-content">', cstart)
    depth = 0
    for m in re.finditer(r'<(/?)div\b', text[content:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            return content + m.start()
    raise SystemExit('could not balance pit-leaf-fill content')


def main():
    ok, g3, e3, gn, en = verify_pg(CARD)
    print('[pg-verify %s] %s  (got %d / exp %d rows)' % ('OK ' if ok else 'FAIL', CARD['title'], gn, en))
    if not ok:
        print('  GOT', g3); print('  EXP', e3); raise SystemExit('verify failed; nothing written')
    text = open(PATH).read()
    if SENTINEL in text:
        print('card already present; nothing to do.'); return
    before = balance(text)
    ins = leaf_content_close(text, 'pit-leaf-fill')
    text = text[:ins] + '\n              ' + eb.build_card(CARD) + '\n              ' + text[ins:]
    text = text.replace(
        'Fill forward over a date spine <span class="count-badge">1 problem</span>',
        'Fill forward over a date spine <span class="count-badge">2 problems</span>', 1)
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE per-entity fill card into pit-leaf-fill (badge -> 2 problems)')


if __name__ == '__main__':
    main()
