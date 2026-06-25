"""Add a second worked card to the fn-cast (Type casting & conversion) container:
'Parse & Convert Messy Enrollment Records' — DD.MM.YYYY dates, comma-grouped amounts,
and blank strings that must become NULL (NULLIF before ::int). Plus a display note about
the pandas int->float (1.0 / NaN) quirk. Postgres-verified. Idempotent + balance-checked.
Run:  python3 build_fn_cast_enroll.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Parse & Convert Messy Enrollment Records',
    'excerpt': "Three cast quirks at once: DD.MM.YYYY dates, comma-grouped amounts, and blank strings that must become NULL.",
    'prompt': ["<code>enrollment_submissions</code> arrived from a legacy system as all-TEXT fields.",
               "Return <code>employee_id</code>, <code>submission_date</code> as a real DATE (the text is DD.MM.YYYY), <code>monthly_premium</code> as NUMERIC (amounts carry a thousands comma like '1,245'), and <code>dependents_count</code> as INTEGER with blank strings turned into NULL.",
               "Order by <code>submission_date</code> ascending, then <code>employee_id</code> ascending."],
    'inputs': [{'name': 'enrollment_submissions',
                'cols': [('employee_id', 'INTEGER'), ('submission_date_text', 'TEXT'), ('monthly_premium_text', 'TEXT'), ('dependents_count_text', 'TEXT')],
                'headers': ['employee_id', 'submission_date_text', 'monthly_premium_text', 'dependents_count_text'],
                'rows': [[101, '15.03.2024', '1,245', '2'], [102, '12.03.2024', '875', ''],
                         [103, '20.03.2024', '2,100', '3'], [104, '12.03.2024', '650', '1'],
                         [105, '18.03.2024', '1,050', ''], [106, '15.03.2024', '3,200', '4']]}],
    'exp_headers': ['employee_id', 'submission_date', 'monthly_premium', 'dependents_count'],
    'exp_rows': [[102, '2024-03-12', 875, None],
                 [104, '2024-03-12', 650, 1],
                 [101, '2024-03-15', 1245, 2],
                 [106, '2024-03-15', 3200, 4],
                 [105, '2024-03-18', 1050, None],
                 [103, '2024-03-20', 2100, 3]],
    'sol_comment': ("TO_DATE reads the DD.MM.YYYY mask into a real date. REPLACE strips the thousands comma, then\n"
                    "::numeric makes it a number. For the count, you cannot cast '' straight to int, so NULLIF turns the\n"
                    "blank into NULL FIRST, then ::int converts (casting NULL is always safe). Verified."),
    'sol_sql': ("SELECT employee_id,\n"
                "       TO_DATE(submission_date_text, 'DD.MM.YYYY')   AS submission_date,\n"
                "       REPLACE(monthly_premium_text, ',', '')::numeric AS monthly_premium,\n"
                "       NULLIF(dependents_count_text, '')::int        AS dependents_count\n"
                "FROM enrollment_submissions\n"
                "ORDER BY submission_date, employee_id;"),
}

NOTE = ('<p style="margin: 6px 0 18px; padding: 10px 14px; background: #eef4fb; border-left: 4px solid #1565c0; font-size: 1.2rem; color: #1a237e;">'
        '<strong>Display note &mdash; why you may see 1.0 / NaN instead of 1 / NULL.</strong> '
        'PostgreSQL returns real integers here (1, 2, NULL). The decimals appear only in the practice notebook: it loads the '
        'result into pandas, and a pandas integer column cannot hold a NULL. To make room for the NULL, pandas promotes the '
        'whole column to float, so 1 prints as 1.0 and NULL prints as NaN. It is a display artifact, not a bug in your SQL &mdash; '
        'and the expected output is generated the same way, so 1.0 / NaN still matches.</p>')


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
    if CARD['title'] in text:
        print('card already present; nothing to do.'); return
    before = eb.balance_report(text)
    # insert after the existing fn-cast worked card ("Parse Messy Text into Real Types")
    s, e = eb.find_block(text, 'Parse Messy Text into Real Types')
    new = '\n              ' + eb.build_card(CARD) + '\n              ' + NOTE
    text = text[:e] + new + text[e:]
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE enrollment card into fn-cast')


if __name__ == '__main__':
    main()
