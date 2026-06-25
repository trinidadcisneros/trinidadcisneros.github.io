"""Add a worked card to the fn-date container: 'Parse Cart Event Timestamps for a Trend Report'
— EXTRACT year/day/hour + TO_CHAR FMMonth for the month name, with COALESCE fallbacks ('N/A'
for the text parts, -1 for the hour) on NULL timestamps. Postgres-verified. Idempotent + balanced.
Run:  python3 build_fn_date_cart.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Parse Cart Event Timestamps for a Trend Report',
    'excerpt': "Year, month NAME, day, and hour from a timestamp, with N/A / -1 fallbacks for NULL rows.",
    'prompt': ["<code>cart_events</code> logs an <code>event_timestamp</code> that is sometimes NULL (failed logging).",
               "Return the <code>event_year</code> (integer), <code>event_month</code> (full name, e.g. 'January'), <code>event_day</code> (integer), and <code>event_hour</code> (0-23).",
               "For a NULL timestamp, show <code>'N/A'</code> for year/month/day and <code>-1</code> for the hour.",
               "Columns: <code>event_id</code>, <code>event_year</code>, <code>event_month</code>, <code>event_day</code>, <code>event_hour</code>; order by <code>event_id</code>."],
    'inputs': [{'name': 'cart_events',
                'cols': [('event_id', 'INT'), ('event_timestamp', 'TIMESTAMP')],
                'headers': ['event_id', 'event_timestamp'],
                'rows': [[1, '2024-03-15 14:23:00'], [2, '2024-01-08 09:05:30'], [3, None],
                         [4, '2023-12-25 23:59:59'], [5, '2024-03-01 00:00:00'], [6, '2024-02-29 18:45:12']]}],
    'exp_headers': ['event_id', 'event_year', 'event_month', 'event_day', 'event_hour'],
    'exp_rows': [[1, '2024', 'March', '15', 14],
                 [2, '2024', 'January', '8', 9],
                 [3, 'N/A', 'N/A', 'N/A', -1],
                 [4, '2023', 'December', '25', 23],
                 [5, '2024', 'March', '1', 0],
                 [6, '2024', 'February', '29', 18]],
    'sol_comment': ("EXTRACT pulls the numeric parts; TO_CHAR(ts,'FMMonth') gives the month NAME (FM trims the\n"
                    "padding). The fallback is the trick: to show 'N/A' you must mix text with the number, so the\n"
                    "year/day are cast ::VARCHAR first, then COALESCE swaps NULL -> 'N/A' (those columns become text).\n"
                    "The hour stays a number, so its COALESCE uses -1, not 'N/A'. EXTRACT(... FROM NULL) is NULL, which\n"
                    "is what makes the COALESCE fire on the NULL row. Verified."),
    'sol_sql': ("SELECT event_id,\n"
                "       COALESCE(EXTRACT(year FROM event_timestamp)::varchar, 'N/A') AS event_year,\n"
                "       COALESCE(TO_CHAR(event_timestamp, 'FMMonth'), 'N/A')         AS event_month,\n"
                "       COALESCE(EXTRACT(day FROM event_timestamp)::varchar, 'N/A')  AS event_day,\n"
                "       COALESCE(EXTRACT(hour FROM event_timestamp)::int, -1)        AS event_hour\n"
                "FROM cart_events\n"
                "ORDER BY event_id;"),
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
        s, e = eb.find_block(text, CARD['title'])
        text = text[:s] + eb.build_card(CARD) + text[e:]
        print('replaced existing card in place.')
    else:
        s, e = eb.find_block(text, 'Break a Timestamp into Parts')
        text = text[:e] + '\n              ' + eb.build_card(CARD) + text[e:]
        print('inserted new card after the existing fn-date card.')
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE cart-events card into fn-date')


if __name__ == '__main__':
    main()
