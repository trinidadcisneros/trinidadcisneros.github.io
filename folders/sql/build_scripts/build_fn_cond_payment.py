"""Add a second worked card to the fn-conditional (Conditional & NULL handling) container:
'Payment Health Score with Cleanup' — COALESCE a NULL count to 0, a CASE penalty keyed on a
trimmed/lowercased status, and SPLIT_PART the first scheduled amount, combined into a score.
Postgres-verified. Idempotent + balance-checked.
Run:  python3 build_fn_cond_payment.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Hard', 'color': '#b71c1c', 'title': 'Payment Health Score with Cleanup',
    'excerpt': "COALESCE a NULL count to 0, a CASE penalty by normalized status, and the first scheduled amount — combined into a score.",
    'prompt': ["<code>payment_plans</code> needs cleaning: <code>plan_status</code> has mixed case/whitespace, <code>payment_schedule</code> is a comma-separated list of amounts, and <code>missed_count</code> may be NULL (meaning 0 missed).",
               "Compute <code>health_score = 100 - (missed_count * 15) - late_penalty</code>, where late_penalty is 10 when the normalized (trimmed + lowercased) status is 'overdue', 5 when 'warning', else 0. Treat a NULL missed_count as 0.",
               "Output <code>plan_id</code>, <code>customer_email</code>, <code>clean_status</code> (trimmed + title-cased), <code>next_payment_amount</code> (the first amount in the schedule), and <code>health_score</code>.",
               "Order by <code>health_score</code> descending, then <code>plan_id</code>."],
    'inputs': [{'name': 'payment_plans',
                'cols': [('plan_id', 'INT'), ('customer_email', 'TEXT'), ('plan_status', 'TEXT'), ('payment_schedule', 'TEXT'), ('missed_count', 'INT')],
                'headers': ['plan_id', 'customer_email', 'plan_status', 'payment_schedule', 'missed_count'],
                'rows': [[1, 'alice@example.com', 'Active', '125.00,125.00,125.00', 0],
                         [2, 'bob@example.com', 'WARNING', '200.00,200.00', 1],
                         [3, 'carol@example.com', 'overdue', '75.50,75.50,75.50,75.50', 2],
                         [4, 'dave@example.com', 'ACTIVE', '300.00,300.00,300.00', None],
                         [5, 'eve@example.com', 'warning', '150.00,150.00', 3],
                         [6, 'frank@example.com', 'Active', '100.00,100.00,100.00,100.00', 0]]}],
    'exp_headers': ['plan_id', 'customer_email', 'clean_status', 'next_payment_amount', 'health_score'],
    'exp_rows': [[1, 'alice@example.com', 'Active', '125.00', 100],
                 [4, 'dave@example.com', 'Active', '300.00', 100],
                 [6, 'frank@example.com', 'Active', '100.00', 100],
                 [2, 'bob@example.com', 'Warning', '200.00', 80],
                 [3, 'carol@example.com', 'Overdue', '75.50', 60],
                 [5, 'eve@example.com', 'Warning', '150.00', 50]],
    'sol_comment': ("Clean once, score once. A CTE normalizes every messy field a single time: TRIM + lower for the\n"
                    "status, COALESCE the NULL missed_count to 0, and SPLIT_PART the first scheduled amount. The outer\n"
                    "query then just reads those tidy columns -- INITCAP for the display status, a compact\n"
                    "CASE status_norm WHEN ... for the penalty, and the 100 - missed*15 - penalty formula (already an\n"
                    "integer, so no cast needed). Cleaning once avoids repeating TRIM/lower and the mistakes that invites. Verified."),
    'sol_sql': ("WITH cleaned AS (\n"
                "    SELECT plan_id,\n"
                "           customer_email,\n"
                "           TRIM(plan_status)                             AS status_trimmed,\n"
                "           lower(TRIM(plan_status))                      AS status_norm,\n"
                "           SPLIT_PART(payment_schedule, ',', 1)::numeric AS next_payment_amount,\n"
                "           COALESCE(missed_count, 0)                     AS missed\n"
                "    FROM payment_plans\n"
                ")\n"
                "SELECT plan_id,\n"
                "       customer_email,\n"
                "       INITCAP(status_trimmed) AS clean_status,\n"
                "       next_payment_amount,\n"
                "       100 - missed * 15\n"
                "           - CASE status_norm WHEN 'overdue' THEN 10 WHEN 'warning' THEN 5 ELSE 0 END AS health_score\n"
                "FROM cleaned\n"
                "ORDER BY health_score DESC, plan_id;"),
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


def main():
    ok, got, exp = verify_pg(CARD)
    print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', CARD['title']))
    if not ok:
        print('GOT', got); print('EXP', exp); raise SystemExit('verify failed')
    text = open(PATH).read()
    before = eb.balance_report(text)
    if CARD['title'] in text:
        # replace the existing card in place
        s, e = eb.find_block(text, CARD['title'])
        text = text[:s] + eb.build_card(CARD) + text[e:]
        print('replaced existing card in place.')
    else:
        # insert after the existing fn-conditional worked card
        s, e = eb.find_block(text, 'Grade with CASE, Fill NULLs with COALESCE')
        text = text[:e] + '\n              ' + eb.build_card(CARD) + text[e:]
        print('inserted new card.')
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE payment-health card into fn-conditional')


if __name__ == '__main__':
    main()
