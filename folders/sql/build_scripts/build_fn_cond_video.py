"""Add a worked card to the fn-conditional container: 'Safe Completion Rate & Engagement Tier'
— COALESCE a NULL watch time to 0, NULLIF the denominator to dodge divide-by-zero (rate becomes
NULL), then a CASE tier where the NULL rate falls through to a 'no_data' branch. Postgres-verified.
Idempotent (replaces in place if present) + balance-checked.
Run:  python3 build_fn_cond_video.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Safe Completion Rate & Engagement Tier',
    'excerpt': "COALESCE a NULL watch time, NULLIF to dodge divide-by-zero, then a CASE tier with a no_data branch for the NULL rate.",
    'prompt': ["<code>video_analytics</code>: <code>watch_duration_sec</code> is NULL when a user did not watch, and <code>total_duration_sec</code> can be 0 from encoding errors.",
               "Return <code>video_id</code>, <code>safe_watch_duration</code> (NULL watch &rarr; 0), <code>completion_rate</code> (watch / total as a percent, 1 dp, but NULL when total is 0 to avoid divide-by-zero), and <code>engagement_tier</code>.",
               "Tier: 'high' if rate &ge; 75, 'medium' if &ge; 40, 'low' if &ge; 10, 'minimal' if below 10, and 'no_data' when the rate is NULL. Order by <code>video_id</code>."],
    'inputs': [{'name': 'video_analytics',
                'cols': [('video_id', 'VARCHAR(20)'), ('watch_duration_sec', 'INT'), ('total_duration_sec', 'INT')],
                'headers': ['video_id', 'watch_duration_sec', 'total_duration_sec'],
                'rows': [['V001', 45, 60], ['V002', None, 30], ['V003', 25, 50], ['V004', 58, 60],
                         ['V005', 8, 90], ['V006', 40, 0], ['V007', 12, 30]]}],
    'exp_headers': ['video_id', 'safe_watch_duration', 'completion_rate', 'engagement_tier'],
    'exp_rows': [['V001', 45, '75.0', 'high'],
                 ['V002', 0, '0.0', 'minimal'],
                 ['V003', 25, '50.0', 'medium'],
                 ['V004', 58, '96.7', 'high'],
                 ['V005', 8, '8.9', 'minimal'],
                 ['V006', 40, None, 'no_data'],
                 ['V007', 12, '40.0', 'medium']],
    'sol_comment': ("Three NULL tools in one query. COALESCE turns a NULL watch time into 0. NULLIF(total, 0) turns a 0\n"
                    "denominator into NULL, so the division yields NULL instead of erroring -- that is the safe completion\n"
                    "rate. The CASE then tiers it; the key trick is the NULL rate: every >= and < test against NULL is\n"
                    "'not true', so a NULL rate skips all the number branches and falls through to WHEN ... IS NULL ->\n"
                    "'no_data'. Computing the rate once in a CTE lets the CASE read it by name. Verified."),
    'sol_sql': ("WITH base AS (\n"
                "    SELECT video_id,\n"
                "           COALESCE(watch_duration_sec, 0) AS safe_watch_duration,\n"
                "           ROUND(COALESCE(watch_duration_sec, 0)::numeric\n"
                "                 / NULLIF(total_duration_sec, 0) * 100, 1) AS completion_rate\n"
                "    FROM video_analytics\n"
                ")\n"
                "SELECT video_id,\n"
                "       safe_watch_duration,\n"
                "       completion_rate,\n"
                "       CASE WHEN completion_rate >= 75 THEN 'high'\n"
                "            WHEN completion_rate >= 40 THEN 'medium'\n"
                "            WHEN completion_rate >= 10 THEN 'low'\n"
                "            WHEN completion_rate < 10  THEN 'minimal'\n"
                "            WHEN completion_rate IS NULL THEN 'no_data'\n"
                "       END AS engagement_tier\n"
                "FROM base\n"
                "ORDER BY video_id;"),
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
        s, e = eb.find_block(text, 'Payment Health Score with Cleanup')
        text = text[:e] + '\n              ' + eb.build_card(CARD) + text[e:]
        print('inserted new card after the payment card.')
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE video-engagement card into fn-conditional')


if __name__ == '__main__':
    main()
