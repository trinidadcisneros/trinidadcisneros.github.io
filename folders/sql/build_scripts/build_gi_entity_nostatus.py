"""Add a no-status worked card to gi-leaf-entity: each user's consecutive login
date ranges (single table, no status label, a calendar gap breaks the run).
Maps to the new engine union_islands subtype entity_date_periods.

Inserted as the LAST child of the gi-leaf-entity leaf content; badge 3 -> 4.
Verified in real Postgres (pgserver). Idempotent + balance-checked.
Run:  python3 build_gi_entity_nostatus.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
SENTINEL = 'Each User&#x27;s Consecutive Login Date Ranges'  # esc() output of the title's apostrophe

CARD = {
    'diff': 'Easy', 'color': '#2e7d32',
    'title': "Each User's Consecutive Login Date Ranges",
    'excerpt': "Per-entity segments with NO status: collapse each user's back-to-back login days into one start/end. A missing day breaks the run.",
    'prompt': [
        "A product team wants each user's stretches of consecutive login days, collapsed into one row per stretch.",
        "<code>logins</code> has one row per user per day they logged in (at most one row per user per date, no duplicates).",
        "A stretch is back-to-back calendar days; a missing day ends it. There is NO status column here.",
        "Return <code>user_id</code>, <code>period_start</code>, <code>period_end</code>, ordered by <code>user_id</code> then <code>period_start</code>.",
    ],
    'inputs': [{
        'name': 'logins',
        'cols': [('user_id', 'INTEGER'), ('login_date', 'DATE')],
        'headers': ['user_id', 'login_date'],
        'rows': [
            [1, '2024-03-01'], [1, '2024-03-02'], [1, '2024-03-03'], [1, '2024-03-06'], [1, '2024-03-07'],
            [2, '2024-03-02'], [2, '2024-03-05'], [2, '2024-03-06'], [2, '2024-03-07'],
        ],
    }],
    'exp_headers': ['user_id', 'period_start', 'period_end'],
    'exp_rows': [
        [1, '2024-03-01', '2024-03-03'],
        [1, '2024-03-06', '2024-03-07'],
        [2, '2024-03-02', '2024-03-02'],
        [2, '2024-03-05', '2024-03-07'],
    ],
    'sol_comment': (
        "No status label, single table: a stretch is just consecutive calendar days for one user.\n"
        "The trick: subtract a per-user ROW_NUMBER from the date. Inside one back-to-back stretch the\n"
        "date climbs by 1 each row and so does the row number, so date - rn stays CONSTANT; a skipped\n"
        "day makes the date jump while rn does not, so grp changes and a new stretch starts.\n"
        "PARTITION BY user_id keeps each user's row numbers independent — without it user 2's rows would\n"
        "shift user 1's math. GROUP BY user_id, grp then MIN/MAX gives the start and end of each stretch.\n"
        "This is the same shape as the status version (gi-leaf-entity) minus the status partition.\n"
        "Verified against the example data: user 1 -> [03-01,03-03] and [03-06,03-07]; user 2 -> "
        "[03-02,03-02] and [03-05,03-07]."
    ),
    'sol_sql': (
        "SELECT user_id,\n"
        "       MIN(login_date) AS period_start,\n"
        "       MAX(login_date) AS period_end\n"
        "FROM (\n"
        "  SELECT user_id, login_date,\n"
        "         login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date))::int AS grp\n"
        "  FROM logins                                  -- date - per-user row number = stretch key\n"
        ") s\n"
        "GROUP BY user_id, grp\n"
        "ORDER BY user_id, period_start;"
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
        exp = [tuple(str(x) for x in r) for r in card['exp_rows']]
        return got == exp, got, exp
    finally:
        srv.cleanup()


def _lit(v):
    if v is None:
        return 'NULL'
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    return s if re.match(r'^-?\d+(\.\d+)?$', s) else "'" + s.replace("'", "''") + "'"


def balance(t):
    do = len(re.findall(r'<div\b', t)); dc = len(re.findall(r'</div\b', t))
    deto = len(re.findall(r'<details\b', t)); detc = len(re.findall(r'</details\b', t))
    d = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', t):
        d += 1 if m.group(1) == '' else -1; mn = min(mn, d)
    return do, dc, deto, detc, d, mn


def leaf_content_close(text):
    """Index of the </div> that closes gi-leaf-entity's OWN problem-card-content."""
    hid = text.find('id="gi-leaf-entity"')
    cstart = text.rfind('<div', 0, hid)                       # leaf container open
    content = text.find('<div class="problem-card-content">', cstart)
    pos, depth = content, 0
    for m in re.finditer(r'<(/?)div\b', text[content:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            return content + m.start()
    raise SystemExit('could not balance gi-leaf-entity content')


def main():
    ok, got, exp = verify_pg(CARD)
    print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', CARD['title']))
    if not ok:
        print('  GOT', got); print('  EXP', exp); raise SystemExit('verify failed; nothing written')
    text = open(PATH).read()
    if SENTINEL in text:
        print('card already present; nothing to do.'); return
    before = balance(text)
    ins = leaf_content_close(text)
    card_html = '\n              ' + eb.build_card(CARD) + '\n              '
    text = text[:ins] + card_html + text[ins:]
    # bump the gi-leaf-entity badge 3 -> 4
    text = text.replace(
        'Per-entity island timelines <span class="count-badge">3 problems</span>',
        'Per-entity island timelines <span class="count-badge">4 problems</span>', 1)
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE no-status card into gi-leaf-entity (badge -> 4 problems)')


if __name__ == '__main__':
    main()
