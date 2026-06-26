"""Add a worked card to the Series Generation 'bounds from data' leaf (sg-leaf-databounds):
'Customers Active Per Tier Per Day' — data-bounds generate_series spine CROSS JOINed to the
distinct cleaned tiers, then range-joined back to count active customers per tier per day.
Tight 3-row dataset (the user's 5x31-day version makes 70 rows). Postgres-verified.
Idempotent (replace-in-place) + balance-checked.
Run:  python3 build_sg_active_per_day.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Hard', 'color': '#b71c1c', 'title': 'Customers Active Per Tier Per Day (data-bounds spine)',
    'excerpt': "Expand date ranges into a day spine from the data's own MIN/MAX, then count who is active per tier each day.",
    'prompt': ["<code>loyalty_tier_assignments</code> has one row per (customer, tier) membership with a <code>start_date</code> and <code>end_date</code>. <code>tier_name</code> has inconsistent case / spacing (Gold / gold / SILVER).",
               "For every day from the earliest start to the latest end, count how many customers held each tier that day.",
               "Return <code>tier_name</code> (title-cased), <code>day</code> (a date), <code>customer_count</code>. Keep only (tier, day) pairs that actually have someone active. Order by day, then tier_name."],
    'inputs': [{'name': 'loyalty_tier_assignments',
                'cols': [('assignment_id', 'INT'), ('customer_id', 'INT'), ('tier_name', 'TEXT'),
                         ('start_date', 'DATE'), ('end_date', 'DATE')],
                'headers': ['assignment_id', 'customer_id', 'tier_name', 'start_date', 'end_date'],
                'rows': [[1, 101, 'Gold', '2024-01-01', '2024-01-03'],
                         [2, 102, 'SILVER', '2024-01-02', '2024-01-04'],
                         [3, 103, 'gold', '2024-01-03', '2024-01-05']]}],
    'exp_headers': ['tier_name', 'day', 'customer_count'],
    'exp_rows': [['Gold', '2024-01-01', 1],
                 ['Gold', '2024-01-02', 1],
                 ['Silver', '2024-01-02', 1],
                 ['Gold', '2024-01-03', 2],
                 ['Silver', '2024-01-03', 1],
                 ['Gold', '2024-01-04', 1],
                 ['Silver', '2024-01-04', 1],
                 ['Gold', '2024-01-05', 1]],
    'sol_comment': ("bounds gets the span from the DATA (MIN start, MAX end) cast to date. generate_series fans that\n"
                    "span into one row per day. CROSS JOIN to the DISTINCT cleaned tiers (INITCAP(TRIM(...)) folds\n"
                    "Gold / gold / SILVER into one each) makes the full tier x day grid. Then JOIN back to the\n"
                    "assignments on day BETWEEN start and end AND the cleaned tier matches, and COUNT the customers.\n"
                    "The inner JOIN (with HAVING > 0) keeps only days a tier was active; to SHOW 0 for inactive days,\n"
                    "make it a LEFT JOIN and drop the HAVING. Verified."),
    'sol_sql': ("WITH bounds AS (\n"
                "    SELECT MIN(start_date)::date AS lo,\n"
                "           MAX(end_date)::date   AS hi\n"
                "    FROM loyalty_tier_assignments\n"
                "),\n"
                "spine AS (\n"
                "    SELECT l.tier_name, gs::date AS day\n"
                "    FROM bounds,\n"
                "         generate_series(bounds.lo, bounds.hi, INTERVAL '1 day') AS gs\n"
                "    CROSS JOIN (\n"
                "        SELECT DISTINCT INITCAP(TRIM(tier_name)) AS tier_name\n"
                "        FROM loyalty_tier_assignments\n"
                "    ) AS l\n"
                ")\n"
                "SELECT s.tier_name,\n"
                "       s.day,\n"
                "       COUNT(l.customer_id) AS customer_count\n"
                "FROM spine AS s\n"
                "JOIN loyalty_tier_assignments AS l\n"
                "  ON s.day >= l.start_date AND s.day <= l.end_date\n"
                " AND s.tier_name = INITCAP(TRIM(l.tier_name))\n"
                "GROUP BY 1, 2\n"
                "HAVING COUNT(l.customer_id) > 0\n"
                "ORDER BY day, tier_name;"),
}


def _lit(v):
    if v is None: return 'NULL'
    s = str(v)
    return s if re.match(r'^-?\d+$', s) else "'" + s.replace("'", "''") + "'"

def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in card['inputs']:
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], ', '.join('%s %s' % (n, t) for n, t in inp['cols'])))
            for row in inp['rows']:
                srv.psql('INSERT INTO %s VALUES (%s);' % (inp['name'], ', '.join(_lit(v) for v in row)))
        out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + card['sol_sql'])
        nc = len(card['exp_headers'])
        got = [tuple('' if c == '' else c for c in l.split('|')) for l in out.strip().splitlines()
               if l.count('|') == nc - 1 and 'format is' not in l and 'separator is' not in l]
        exp = [tuple('' if v is None else str(v) for v in r) for r in card['exp_rows']]
        return got == exp, got, exp
    finally:
        srv.cleanup()


def _balanced_end(text, s):
    depth = 0
    for m in re.finditer(r'<(/?)div\b', text[s:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            return text.find('>', s + m.start()) + 1
    raise SystemExit('unbalanced')


def main():
    ok, got, exp = verify_pg(CARD)
    print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', CARD['title']))
    if not ok:
        print('GOT', got); print('EXP', exp); raise SystemExit('verify failed')
    text = open(PATH).read()
    before = eb.balance_report(text)
    if CARD['title'] in text:
        s, e = eb.find_block(text, CARD['title'])
        text = text[:s] + eb.build_card(CARD) + text[e:]
        print('replaced existing card in place.')
    else:
        s = text.find('id="sg-tmpl-data-bounds"')   # the bounds-from-data template card
        s = text.rfind('<div', 0, s)
        e = _balanced_end(text, s)
        text = text[:e] + '\n              ' + eb.build_card(CARD) + text[e:]
        print('inserted after sg-tmpl-data-bounds.')
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE active-per-day card into sg-leaf-databounds')


if __name__ == '__main__':
    main()
