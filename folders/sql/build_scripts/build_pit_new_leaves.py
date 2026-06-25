"""Add 3 new Point-in-Time subtype leaves (qtype-group, template + Postgres-verified
worked card) and restyle the existing 3 leaves to qtype-group, mirroring gaps-and-islands.

  pit-leaf-intervals  <- point_in_time/validity_intervals  (change list -> valid_from/valid_to via LEAD)
  pit-leaf-asofjoin   <- point_in_time/asof_join           (value at each event's date, 2nd table)
  pit-leaf-latest     <- point_in_time/latest_snapshot     (single newest value per entity, no cutoff)

Verified in real Postgres (pgserver). Inserted after pit-leaf-fill. Idempotent + balance-checked.
Run:  python3 build_pit_new_leaves.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

# ---------------- worked cards ----------------
CARD_INTERVALS = {
    'diff': 'Medium', 'color': '#e65100',
    'title': 'Price Validity Windows per SKU',
    'excerpt': "Turn each price change into the date range it was active: valid_from on the change, valid_to the day before the next change, NULL while still active.",
    'prompt': [
        "The <code>price_changes</code> table logs each price a SKU took and the date it took effect.",
        "Produce one row per price showing the window it was in effect: <code>valid_from</code> is the change date, <code>valid_to</code> is the day BEFORE that SKU's next change.",
        "The current (newest) price for each SKU has no next change, so its <code>valid_to</code> is NULL (still active).",
        "Return <code>sku</code>, <code>price</code>, <code>valid_from</code>, <code>valid_to</code>, ordered by <code>sku</code>, <code>valid_from</code>.",
    ],
    'inputs': [{
        'name': 'price_changes',
        'cols': [('sku', 'VARCHAR(10)'), ('effective_date', 'DATE'), ('price', 'DECIMAL(10,2)')],
        'headers': ['sku', 'effective_date', 'price'],
        'rows': [
            ['KIT-A', '2024-01-01', '49.99'], ['KIT-A', '2024-01-05', '54.99'], ['KIT-A', '2024-01-08', '52.99'],
            ['KIT-B', '2024-01-03', '39.99'], ['KIT-B', '2024-01-07', '44.99'],
        ],
    }],
    'exp_headers': ['sku', 'price', 'valid_from', 'valid_to'],
    'exp_rows': [
        ['KIT-A', '49.99', '2024-01-01', '2024-01-04'],
        ['KIT-A', '54.99', '2024-01-05', '2024-01-07'],
        ['KIT-A', '52.99', '2024-01-08', None],
        ['KIT-B', '39.99', '2024-01-03', '2024-01-06'],
        ['KIT-B', '44.99', '2024-01-07', None],
    ],
    'sol_comment': (
        "No cutoff here -- you are reshaping a list of changes into the windows each value was active.\n"
        "valid_from is just the change's own date. valid_to is the day BEFORE the next change for the\n"
        "same SKU: LEAD() looks ahead to the next row's effective_date (PARTITION BY sku so it never\n"
        "peeks at another SKU), and you subtract 1 day. The newest row per SKU has no next change, so\n"
        "LEAD is NULL and valid_to is NULL = still in effect. MySQL: DATE_SUB(LEAD(...) OVER (...), INTERVAL 1 DAY).\n"
        "Verified against the example data."
    ),
    'sol_sql': (
        "SELECT sku,\n"
        "       price,\n"
        "       effective_date AS valid_from,                                   -- starts on the change\n"
        "       LEAD(effective_date) OVER (PARTITION BY sku ORDER BY effective_date) - 1 AS valid_to  -- day before next change; NULL = still active\n"
        "FROM price_changes\n"
        "ORDER BY sku, valid_from;"
    ),
}

CARD_ASOFJOIN = {
    'diff': 'Medium', 'color': '#e65100',
    'title': 'Price Charged at Each Sale (As-of Join)',
    'excerpt': "For each sale, attach the price that was in effect on the day the sale happened, looked up from a separate price history table.",
    'prompt': [
        "<code>sales</code> has one row per sale (sale_id, sku, sale_date). <code>price_history</code> logs each SKU's price changes by effective_date.",
        "For each sale, return the price that was in effect on the sale's own date: the latest price change for that SKU on or before <code>sale_date</code>.",
        "If a sale happened before that SKU's first price change, the price is NULL.",
        "Return <code>sale_id</code>, <code>sku</code>, <code>sale_date</code>, <code>price_at_sale</code>, ordered by <code>sale_id</code>.",
    ],
    'inputs': [
        {'name': 'sales',
         'cols': [('sale_id', 'INTEGER'), ('sku', 'VARCHAR(10)'), ('sale_date', 'DATE')],
         'headers': ['sale_id', 'sku', 'sale_date'],
         'rows': [[1, 'KIT-A', '2024-01-06'], [2, 'KIT-A', '2024-01-02'], [3, 'KIT-B', '2024-01-04'], [4, 'KIT-A', '2024-01-09']]},
        {'name': 'price_history',
         'cols': [('sku', 'VARCHAR(10)'), ('effective_date', 'DATE'), ('price', 'DECIMAL(10,2)')],
         'headers': ['sku', 'effective_date', 'price'],
         'rows': [['KIT-A', '2024-01-01', '49.99'], ['KIT-A', '2024-01-05', '54.99'], ['KIT-A', '2024-01-08', '52.99'],
                  ['KIT-B', '2024-01-03', '39.99'], ['KIT-B', '2024-01-07', '44.99']]},
    ],
    'exp_headers': ['sale_id', 'sku', 'sale_date', 'price_at_sale'],
    'exp_rows': [
        [1, 'KIT-A', '2024-01-06', '54.99'],
        [2, 'KIT-A', '2024-01-02', '49.99'],
        [3, 'KIT-B', '2024-01-04', '39.99'],
        [4, 'KIT-A', '2024-01-09', '52.99'],
    ],
    'sol_comment': (
        "The cutoff is different for every row: each sale's own date. So you cannot use one fixed\n"
        "date -- you look up, per sale, the latest price change for that SKU on or before that sale's\n"
        "date. The correlated subquery does exactly that (matched on the SKU, dated on/before the sale,\n"
        "newest first, take 1). A sale before the SKU's first change finds nothing and returns NULL.\n"
        "Sale 1 (Jan 6, KIT-A): changes Jan 1 / Jan 5 / Jan 8 -> the Jan 5 price 54.99. Verified.\n"
        "LEFT JOIN LATERAL (...) ON true is an equivalent form."
    ),
    'sol_sql': (
        "SELECT s.sale_id,\n"
        "       s.sku,\n"
        "       s.sale_date,\n"
        "       (SELECT p.price                              -- the price in effect at this sale's date\n"
        "        FROM price_history p\n"
        "        WHERE p.sku = s.sku                         -- same SKU ...\n"
        "          AND p.effective_date <= s.sale_date       -- ... effective on or before the sale\n"
        "        ORDER BY p.effective_date DESC\n"
        "        LIMIT 1) AS price_at_sale                   -- before the first change -> NULL\n"
        "FROM sales s\n"
        "ORDER BY s.sale_id;"
    ),
}

CARD_LATEST = {
    'diff': 'Easy', 'color': '#2e7d32',
    'title': "Each Team's Most Recent Velocity",
    'excerpt': "The single newest value per entity, no cutoff date: keep one row per team, the latest by date.",
    'prompt': [
        "The <code>velocity_log</code> table logs each team's velocity at various dates.",
        "Return each team's MOST RECENT velocity (the row with the latest <code>effective_date</code>). There is no cutoff date.",
        "Return <code>team_id</code>, <code>velocity</code>, ordered by <code>team_id</code>.",
    ],
    'inputs': [{
        'name': 'velocity_log',
        'cols': [('team_id', 'INTEGER'), ('effective_date', 'DATE'), ('velocity', 'INTEGER')],
        'headers': ['team_id', 'effective_date', 'velocity'],
        'rows': [
            [101, '2024-05-01', 20], [101, '2024-06-10', 25], [101, '2024-06-20', 30],
            [102, '2024-04-15', 18], [102, '2024-06-14', 22],
        ],
    }],
    'exp_headers': ['team_id', 'velocity'],
    'exp_rows': [[101, 30], [102, 22]],
    'sol_comment': (
        "No cutoff and no date range -- you just want each team's newest row. DISTINCT ON (team_id)\n"
        "with ORDER BY team_id, effective_date DESC keeps the first row it sees per team, which is the\n"
        "newest. Portable form for any database: ROW_NUMBER() OVER (PARTITION BY team_id ORDER BY\n"
        "effective_date DESC) and keep rn = 1. Team 101's newest is 2024-06-20 -> 30. Verified."
    ),
    'sol_sql': (
        "SELECT DISTINCT ON (team_id) team_id, velocity   -- one row per team ...\n"
        "FROM velocity_log\n"
        "ORDER BY team_id, effective_date DESC;            -- ... the newest, because of DESC"
    ),
}

# ---------------- templates ----------------
def tmpl(tid, title, use_when, steps, code):
    lis = ''.join('\n                          <li>%s</li>' % s for s in steps)
    return ('''<div id="%(tid)s" class="problem-card collapsed" style="margin: 0 0 10px 0;">
                      <div class="problem-card-header">
                        <h3 class="problem-card-title" style="margin: 0;">%(title)s</h3>
                        <span class="problem-toggle">&#9660;</span>
                      </div>
                      <div class="problem-card-excerpt">
                        <p style="margin:0;">%(use_when)s</p>
                      </div>
                      <div class="problem-card-content">
                        <p style="margin:0 0 6px;"><strong>What this template does, step by step:</strong></p>
                        <ol style="margin:0 0 10px 18px; line-height:1.7;">%(lis)s
                        </ol>
                        <pre style="margin:0 0 6px; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>%(code)s</code></pre>
                      </div>
                    </div>''' % {'tid': tid, 'title': title, 'use_when': use_when, 'lis': lis, 'code': code})

TMPL_INTERVALS = tmpl('pit-tmpl-intervals',
    'Validity intervals: change list &rarr; valid_from / valid_to',
    'Use when: the output is one row per value with the dates it was active (a start and an end), built from a list of changes. No cutoff.',
    ["<code>valid_from</code> is the change's own date.",
     "<code>valid_to</code> is the day BEFORE the next change for the same entity: <code>LEAD(effective_date) OVER (PARTITION BY entity ORDER BY effective_date) - 1</code>.",
     "The newest row per entity has no next change, so <code>LEAD</code> is NULL and <code>valid_to</code> is NULL (still active).",
     "MySQL: use <code>DATE_SUB(LEAD(...) OVER (...), INTERVAL 1 DAY)</code>."],
    "SELECT entity, val,\n"
    "       effective_date AS valid_from,\n"
    "       LEAD(effective_date) OVER (PARTITION BY entity ORDER BY effective_date) - 1 AS valid_to  -- NULL = still active\n"
    "FROM history\n"
    "ORDER BY entity, valid_from;")

TMPL_ASOFJOIN = tmpl('pit-tmpl-asofjoin',
    'As-of join: the value in effect at each event&#x27;s date',
    'Use when: each output row is an event, with a value pulled from a SECOND table that was true at that event&#x27;s own date.',
    ["Start from the events table &mdash; one row per event.",
     "For each event, look up the history value with the latest <code>effective_date</code> on or before the event's date, for the same entity.",
     "A correlated subquery (<code>ORDER BY effective_date DESC LIMIT 1</code>) or <code>LEFT JOIN LATERAL</code> keeps the event even when nothing matches (NULL)."],
    "SELECT e.event_id, e.event_date,\n"
    "       (SELECT h.val FROM history h\n"
    "        WHERE h.entity = e.entity AND h.effective_date &lt;= e.event_date\n"
    "        ORDER BY h.effective_date DESC\n"
    "        LIMIT 1) AS val_at_event   -- before the first history row -&gt; NULL\n"
    "FROM events e\n"
    "ORDER BY e.event_id;")

TMPL_LATEST = tmpl('pit-tmpl-latest',
    'Latest snapshot: the most recent value per entity (no cutoff)',
    'Use when: you want exactly one row per entity &mdash; its single newest value &mdash; with no cutoff date.',
    ["No cutoff and no range; you just want each entity's newest row.",
     "<code>DISTINCT ON (entity) ... ORDER BY entity, effective_date DESC</code> keeps one row per entity, the newest (Postgres).",
     "Portable form: <code>ROW_NUMBER() OVER (PARTITION BY entity ORDER BY effective_date DESC)</code>, keep <code>rn = 1</code>."],
    "SELECT DISTINCT ON (entity) entity, val\n"
    "FROM history\n"
    "ORDER BY entity, effective_date DESC;\n"
    "-- portable: ROW_NUMBER() OVER (PARTITION BY entity ORDER BY effective_date DESC) = 1")

LEAVES = [
    ('pit-leaf-intervals', 'Validity intervals: change list &rarr; date ranges', 'validity_intervals',
     "the output is one row per value with a <code>valid_from</code> and <code>valid_to</code>; <code>valid_to</code> is the day before the next change, NULL while still active. No cutoff.",
     TMPL_INTERVALS, CARD_INTERVALS),
    ('pit-leaf-asofjoin', "As-of join: the value in effect at each event's date", 'asof_join',
     "each output row is an EVENT with a value pulled from a SECOND table that was true at that event's own date (a per-row cutoff).",
     TMPL_ASOFJOIN, CARD_ASOFJOIN),
    ('pit-leaf-latest', "Latest snapshot: the most recent value per entity", 'latest_snapshot',
     "exactly one row per entity, its single newest value, with NO cutoff date. Overlaps the Rank recipe's top-1-by-date.",
     TMPL_LATEST, CARD_LATEST),
]


def leaf_html(lid, title, flavor, tail, tmpl_html, card):
    label = ('<code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">'
             'nb01 qtype: point_in_time (%s flavor)</code>' % flavor)
    return ('''<div id="%(lid)s" class="problem-card collapsed qtype-group">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0;">%(title)s <span class="count-badge">1 problem</span></h3>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt">
                  <p style="margin: 0;">%(label)s &mdash; %(tail)s</p>
                </div>
                <div class="problem-card-content">
                    %(tmpl)s
              %(card)s
                </div>
              </div>''' % {'lid': lid, 'title': title, 'label': label, 'tail': tail,
                           'tmpl': tmpl_html, 'card': eb.build_card(card)})


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
        return got == exp, got, exp
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


def leaf_end(text, lid):
    s = text.find('<div class="problem-card collapsed" id="%s">' % lid)
    if s < 0:
        s = text.find('<div id="%s"' % lid)
    if s < 0:
        raise SystemExit('leaf not found: ' + lid)
    depth = 0
    for m in re.finditer(r'<(/?)div\b', text[s:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            return text.find('>', s + m.start()) + 1
    raise SystemExit('unbalanced ' + lid)


def main():
    for _, _, _, _, _, card in LEAVES:
        ok, got, exp = verify_pg(card)
        print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', card['title']))
        if not ok:
            print('  GOT', got[:3]); print('  EXP', exp[:3]); raise SystemExit('verify failed')
    text = open(PATH).read()
    if 'id="pit-leaf-intervals"' in text:
        print('new pit leaves already present; nothing to do.'); return
    before = balance(text)
    blocks = '\n\n              '.join(leaf_html(*L) for L in LEAVES)
    end = leaf_end(text, 'pit-leaf-fill')
    text = text[:end] + '\n\n              ' + blocks + '\n' + text[end:]
    # restyle the existing 3 leaves to qtype-group
    for lid in ('pit-leaf-asof', 'pit-leaf-default', 'pit-leaf-fill'):
        text = text.replace('<div class="problem-card collapsed" id="%s">' % lid,
                            '<div class="problem-card collapsed qtype-group" id="%s">' % lid, 1)
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE 3 new pit leaves + restyled 3 existing to qtype-group')


if __name__ == '__main__':
    main()
