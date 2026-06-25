"""Add Trinidad's subscription-tier default-when-no-history solve as a worked card
in pit-leaf-default (ROW_NUMBER staircase form). Badge 1 -> 2. Verified in real
Postgres (pgserver). Idempotent + balance-checked.
Run:  python3 build_pit_default_subscription_card.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
SENTINEL = 'Active Subscription Tier as of a Cutoff'

CARD = {
    'diff': 'Medium', 'color': '#e65100',
    'title': "Active Subscription Tier as of a Cutoff (default 'free')",
    'excerpt': "Each viewer's tier as of one cutoff date; viewers with no change by then still appear with the default 'free'.",
    'prompt': [
        "<code>subscription_history</code> records each viewer's tier and the <code>effective_date</code> it took effect.",
        "Return every viewer's active tier as of <strong>2024-06-15</strong> &mdash; the most recent change on or before the cutoff.",
        "If a viewer has no record on or before the cutoff (all their changes are after it), return <code>'free'</code>.",
        "Return <code>viewer_id</code>, <code>active_tier</code>, ordered by <code>viewer_id</code>.",
    ],
    'inputs': [{
        'name': 'subscription_history',
        'cols': [('viewer_id', 'INTEGER'), ('tier', 'VARCHAR(20)'), ('effective_date', 'DATE')],
        'headers': ['viewer_id', 'tier', 'effective_date'],
        'rows': [
            [101, 'basic', '2024-03-01'], [101, 'premium', '2024-05-15'], [101, 'standard', '2024-07-01'],
            [102, 'premium', '2024-04-10'], [102, 'basic', '2024-06-10'],
            [103, 'standard', '2024-06-20'],
            [104, 'basic', '2024-02-01'], [104, 'premium', '2024-06-01'],
        ],
    }],
    'exp_headers': ['viewer_id', 'active_tier'],
    'exp_rows': [[101, 'premium'], [102, 'basic'], [103, 'free'], [104, 'premium']],
    'sol_comment': (
        "Single cutoff, one row per viewer, default for the missing ones -- the default-when-no-history shape.\n"
        "  viewers : DISTINCT viewer_id from the history itself, so every viewer is in scope (stays single-table).\n"
        "  ranked  : among rows on or before the cutoff (the date guard), number each viewer's rows newest first.\n"
        "  final   : LEFT JOIN to ranked WITH rn = 1 IN THE ON. Keeping rn = 1 in the ON (not WHERE) is what lets\n"
        "            the LEFT JOIN still keep a viewer who has no qualifying row; COALESCE then fills 'free'.\n"
        "101's 07-01 and 103's 06-20 are after the cutoff, so the guard drops them: 101 falls back to its 05-15\n"
        "premium, and 103 has nothing left, so it becomes 'free'. Verified against the example data."
    ),
    'sol_sql': (
        "WITH viewers AS (\n"
        "    SELECT DISTINCT viewer_id FROM subscription_history          -- every viewer in scope\n"
        "),\n"
        "ranked AS (\n"
        "    SELECT viewer_id, tier,\n"
        "           ROW_NUMBER() OVER (PARTITION BY viewer_id ORDER BY effective_date DESC) AS rn\n"
        "    FROM subscription_history\n"
        "    WHERE effective_date <= '2024-06-15'                         -- date guard\n"
        ")\n"
        "SELECT v.viewer_id,\n"
        "       COALESCE(r.tier, 'free') AS active_tier                   -- default when no history yet\n"
        "FROM viewers AS v\n"
        "LEFT JOIN ranked AS r\n"
        "    ON v.viewer_id = r.viewer_id AND r.rn = 1                    -- rn=1 in the ON keeps no-history viewers\n"
        "ORDER BY v.viewer_id;"
    ),
}


def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in card['inputs']:
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], ', '.join('%s %s' % (n, t) for n, t in inp['cols'])))
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


def main():
    ok, got, exp = verify_pg(CARD)
    print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', CARD['title']))
    if not ok:
        print('  GOT', got); print('  EXP', exp); raise SystemExit('verify failed')
    text = open(PATH).read()
    if SENTINEL in text:
        print('card already present; nothing to do.'); return
    before = balance(text)
    cs = text.find('id="pit-leaf-default"')
    cs = text.rfind('<div', 0, cs)
    content = text.find('<div class="problem-card-content">', cs)
    depth = 0; close = None
    for m in re.finditer(r'<(/?)div\b', text[content:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            close = content + m.start(); break
    if close is None:
        raise SystemExit('could not locate pit-leaf-default content close')
    text = text[:close] + '\n              ' + eb.build_card(CARD) + '\n              ' + text[close:]
    text = text.replace('Default when no history <span class="count-badge">1 problem</span>',
                        'Default when no history <span class="count-badge">2 problems</span>', 1)
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE subscription-tier default card into pit-leaf-default (badge -> 2 problems)')


if __name__ == '__main__':
    main()
