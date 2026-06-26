"""Add a worked card to the Date Operations duration leaf (do-leaf-duration), after the
duration-decide accordion: 'Average Kit Turnaround Hours' — EXTRACT(EPOCH ...)/3600 for total
hours, plus TRIM/INITCAP clean, customer_id::int cast, test_type[1] array index, TO_CHAR month,
and AVG/ROUND/HAVING. Postgres-verified. Idempotent (replace-in-place) + balance-checked.
Run:  python3 build_do_duration_kit.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Hard', 'color': '#b71c1c', 'title': 'Average Kit Turnaround Hours (duration + clean + array)',
    'excerpt': "Total hours from ship to result via EXTRACT(EPOCH)/3600, then averaged per customer/test — with a clean, a cast, and an array index.",
    'prompt': ["<code>kit_shipments</code> tracks <code>ship_date</code> (DATE) and <code>result_released_at</code> (TIMESTAMP). <code>customer_id</code> is TEXT-but-numeric, <code>customer_name</code> has messy case/spaces, and <code>test_type</code> is a TEXT[] whose first element is the primary code.",
               "Turnaround = hours from ship to result. For customers with multiple kits, average it (1 dp); keep only averages &ge; 72 hours.",
               "Return <code>customer_id</code> (INTEGER), <code>customer_name</code> (trimmed + title-cased), <code>primary_test_code</code> (first array element), <code>ship_month</code> (their first shipment month as 'YYYY-MM'), <code>avg_turnaround_hours</code> (NUMERIC, 1 dp).",
               "Order by <code>avg_turnaround_hours</code> desc, then <code>customer_id</code> asc."],
    'inputs': [{'name': 'kit_shipments',
                'cols': [('shipment_id', 'INT'), ('customer_id', 'TEXT'), ('customer_name', 'TEXT'),
                         ('ship_date', 'DATE'), ('result_released_at', 'TIMESTAMP'), ('test_type', 'TEXT[]')],
                'headers': ['shipment_id', 'customer_id', 'customer_name', 'ship_date', 'result_released_at', 'test_type'],
                'rows': [[1, '101', 'alice BROWN', '2024-01-15', '2024-01-18 10:30:00', '{COVID-19,PCR}'],
                         [2, '102', 'bob Green', '2024-02-01', '2024-02-05 14:00:00', '{FLU-A,Rapid}'],
                         [3, '101', 'alice BROWN', '2024-03-10', '2024-03-14 09:00:00', '{COVID-19,Antigen}'],
                         [4, '103', 'CAROL white', '2024-01-20', '2024-01-23 16:45:00', '{STREP,Culture}'],
                         [5, '102', 'bob Green', '2024-02-15', '2024-02-18 11:30:00', '{FLU-B,PCR}'],
                         [6, '104', 'Dan Black', '2024-03-01', '2024-03-02 08:00:00', '{RSV,PCR}']]}],
    'exp_headers': ['customer_id', 'customer_name', 'primary_test_code', 'ship_month', 'avg_turnaround_hours'],
    'exp_rows': [[102, 'Bob Green', 'FLU-A', '2024-02', '110.0'],
                 [101, 'Alice Brown', 'COVID-19', '2024-01', '93.8'],
                 [103, 'Carol White', 'STREP', '2024-01', '88.8'],
                 [102, 'Bob Green', 'FLU-B', '2024-02', '83.5']],
    'sol_comment': ("A CTE does the per-row cleaning + the duration, then the outer query aggregates. The duration is\n"
                    "EXTRACT(EPOCH FROM (result_released_at - ship_date::timestamp)) / 3600 = TOTAL hours (EPOCH/3600,\n"
                    "not EXTRACT(HOUR), which would give only the hour slot). ship_date::timestamp is midnight, so a\n"
                    "3-day-10:30 gap is 82.5 h. Also: customer_id::int (cast), INITCAP(TRIM(name)) (clean), test_type[1]\n"
                    "(1-based array), TO_CHAR(ship_date,'YYYY-MM') (format). Then GROUP BY, ROUND(AVG,1), HAVING >= 72.\n"
                    "Customer 102 appears twice because primary_test_code (FLU-A vs FLU-B) is in the GROUP BY. Verified."),
    'sol_sql': ("WITH base AS (\n"
                "    SELECT customer_id::int,\n"
                "           INITCAP(TRIM(customer_name))               AS customer_name,\n"
                "           test_type[1]                               AS primary_test_code,\n"
                "           TO_CHAR(ship_date, 'YYYY-MM')              AS ship_month,\n"
                "           EXTRACT(EPOCH FROM (result_released_at::timestamp - ship_date::timestamp)) / 3600\n"
                "                                                      AS turnaround_hours\n"
                "    FROM kit_shipments\n"
                ")\n"
                "SELECT customer_id,\n"
                "       customer_name,\n"
                "       primary_test_code,\n"
                "       MIN(ship_month)                  AS ship_month,\n"
                "       ROUND(AVG(turnaround_hours), 1)  AS avg_turnaround_hours\n"
                "FROM base\n"
                "GROUP BY 1, 2, 3\n"
                "HAVING ROUND(AVG(turnaround_hours::numeric), 1) >= 72\n"
                "ORDER BY avg_turnaround_hours DESC, customer_id ASC;"),
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
        # insert right after the duration-decide accordion (keeps it inside do-leaf-duration)
        s = text.find('id="do-duration-decide"')
        s = text.rfind('<div', 0, s)
        e = _balanced_end(text, s)
        text = text[:e] + '\n              ' + eb.build_card(CARD) + text[e:]
        print('inserted after do-duration-decide.')
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE kit-turnaround card into do-leaf-duration')


if __name__ == '__main__':
    main()
