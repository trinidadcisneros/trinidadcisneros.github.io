"""Add gi-leaf-streak to the Gaps-and-Islands recipe: the streak-membership shape
(output is a LIST of entities who had >= N days in a row, no start/end). Maps to
engine union_islands subtype consecutive_day_streak_per_entity.

DuckDB can run this, but date arithmetic is verified against real Postgres
(pgserver) to match nb01's validator. build_card renders the HTML.

Inserted right before the gi-leaf-adjacency container. Idempotent + balance-checked.
Run:  python3 build_gi_streak_leaf.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Medium', 'color': '#e65100',
    'title': 'Members With at Least 3 Workout Days in a Row',
    'excerpt': "Output is just the members who hit a 3-day streak — a list of ids, no start/end. Dedupe duplicate same-day rows first, group each segment, keep COUNT &gt;= 3.",
    'prompt': [
        "A gym wants the members who worked out on at least 3 CONSECUTIVE calendar days at any point.",
        "<code>members</code> has one row per member. <code>workouts</code> has one row per logged workout, and a member can log MULTIPLE workouts on the same day, so DUPLICATE <code>(member_id, workout_date)</code> rows can appear.",
        "A streak is 3 or more back-to-back calendar days. Find every member with at least one such streak.",
        "Return <code>member_id</code>, <code>member_name</code>, ordered by <code>member_id</code>. The output is just the qualifying members &mdash; no start or end dates.",
    ],
    'inputs': [
        {'name': 'members',
         'cols': [('member_id', 'INTEGER'), ('member_name', 'VARCHAR')],
         'headers': ['member_id', 'member_name'],
         'rows': [[1, 'Ana'], [2, 'Ben'], [3, 'Cy'], [4, 'Dee']]},
        {'name': 'workouts',
         'cols': [('member_id', 'INTEGER'), ('workout_date', 'DATE')],
         'headers': ['member_id', 'workout_date'],
         'rows': [
             [1, '2024-03-01'], [1, '2024-03-01'], [1, '2024-03-02'], [1, '2024-03-03'],
             [2, '2024-03-01'], [2, '2024-03-02'],
             [3, '2024-03-01'], [3, '2024-03-02'], [3, '2024-03-03'],
             [3, '2024-03-10'], [3, '2024-03-11'], [3, '2024-03-12'],
         ]},
    ],
    'exp_headers': ['member_id', 'member_name'],
    'exp_rows': [[1, 'Ana'], [3, 'Cy']],
    'sol_comment': (
        "Output is a LIST of members, not collapsed date ranges — a membership gate.\n"
        "Four steps:\n"
        "  base    : SELECT DISTINCT removes duplicate same-day rows FIRST. Without this, Ana's two\n"
        "            03-01 rows push ROW_NUMBER to 1,2,3,4 over only 3 real days and the streak math breaks.\n"
        "  grouped : day - ROW_NUMBER() (per member) gives every day in one back-to-back segment the SAME\n"
        "            grp value; a skipped day shifts grp. PARTITION BY member_id keeps members independent.\n"
        "  streaks : GROUP BY member_id, grp then HAVING COUNT(*) >= 3 keeps only segments 3+ days long.\n"
        "  final   : EXISTS (or IN) returns each qualifying member ONCE. Cy has TWO 3-day streaks; without\n"
        "            membership semantics he'd appear twice. Ben (2 days) and Dee (no workouts) drop out.\n"
        "Verified against the example data: Ana and Cy qualify."
    ),
    'sol_sql': (
        "WITH base AS (\n"
        "  SELECT DISTINCT member_id, workout_date          -- dedupe same-day rows first\n"
        "  FROM workouts\n"
        "),\n"
        "grouped AS (\n"
        "  SELECT member_id,\n"
        "         workout_date - (ROW_NUMBER() OVER (PARTITION BY member_id ORDER BY workout_date))::int AS grp\n"
        "  FROM base\n"
        "),\n"
        "streaks AS (\n"
        "  SELECT member_id\n"
        "  FROM grouped\n"
        "  GROUP BY member_id, grp\n"
        "  HAVING COUNT(*) >= 3                              -- a segment of 3+ back-to-back days\n"
        ")\n"
        "SELECT m.member_id, m.member_name\n"
        "FROM members m\n"
        "WHERE EXISTS (SELECT 1 FROM streaks s WHERE s.member_id = m.member_id)  -- once per member\n"
        "ORDER BY m.member_id;"
    ),
}

TEMPLATE = '''<div id="gi-tmpl-streak" class="problem-card collapsed" style="margin: 0 0 10px 0;">
                      <div class="problem-card-header">
                        <h3 class="problem-card-title" style="margin: 0;">Streak membership: who had N days in a row (output is a LIST, no start/end)</h3>
                        <span class="problem-toggle">&#9660;</span>
                      </div>
                      <div class="problem-card-excerpt">
                        <p style="margin:0;">Use when: the output is just the entities that hit a run of at least N consecutive days &mdash; no period_start / period_end. It is a membership gate built on top of the segment trick.</p>
                      </div>
                      <div class="problem-card-content">
                        <p style="margin:0 0 6px;"><strong>What this template does, step by step:</strong></p>
                        <ol style="margin:0 0 10px 18px; line-height:1.7;">
                          <li><strong>Dedupe first.</strong> <code>SELECT DISTINCT entity, day</code> &mdash; a duplicate same-day row would advance ROW_NUMBER without advancing the date and break the math.</li>
                          <li><strong>Make the segment key.</strong> <code>day - ROW_NUMBER() OVER (PARTITION BY entity ORDER BY day)</code> gives every day in one back-to-back run the same <code>grp</code>.</li>
                          <li><strong>Gate the length.</strong> <code>GROUP BY entity, grp HAVING COUNT(*) &gt;= N</code> keeps only runs of N or more days.</li>
                          <li><strong>Return entities once.</strong> <code>EXISTS</code> or <code>IN</code> against the dim table &mdash; an entity with two qualifying runs still appears a single time.</li>
                        </ol>
                        <pre style="margin:0 0 6px; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>WITH base AS (
  SELECT DISTINCT entity_id, event_date     -- dedupe same-day rows FIRST
  FROM facts
),
grouped AS (
  SELECT entity_id,
         event_date - (ROW_NUMBER() OVER (PARTITION BY entity_id ORDER BY event_date))::int AS grp
  FROM base
),
streaks AS (
  SELECT entity_id FROM grouped
  GROUP BY entity_id, grp
  HAVING COUNT(*) &gt;= 3                        -- N consecutive days
)
SELECT d.id, d.name
FROM dim d
WHERE EXISTS (SELECT 1 FROM streaks s WHERE s.entity_id = d.id)
ORDER BY d.id;</code></pre>
                      </div>
                    </div>'''

CODE_LABEL = ('<code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">'
              'nb01 qtype: union_islands (consecutive_day_streak_per_entity flavor)</code>')

LEAF_OPEN = '''<div id="gi-leaf-streak" class="problem-card collapsed qtype-group">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0;">Streak membership: which entities had N days in a row <span class="count-badge">1 problem</span></h3>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt">
                  <p style="margin: 0;">%s &mdash; the output is a LIST of identifiers (the entities that hit a run of at least N consecutive days), NOT collapsed date ranges. Dedupe same-day rows, build the segment key, gate with <code>HAVING COUNT(*) &gt;= N</code>, then return each entity once.</p>
                </div>
                <div class="problem-card-content">
                    %s
                ''' % (CODE_LABEL, TEMPLATE)

LEAF_CLOSE = '''
                </div>
              </div>'''


def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in card['inputs']:
            coldefs = ', '.join('%s %s' % (n, t) for n, t in inp['cols'])
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], coldefs))
            cn = ', '.join(n for n, _ in inp['cols'])
            for row in inp['rows']:
                vals = ', '.join(_lit(v) for v in row)
                srv.psql('INSERT INTO %s (%s) VALUES (%s);' % (inp['name'], cn, vals))
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
    if re.match(r'^-?\d+(\.\d+)?$', s):
        return s
    return "'" + s.replace("'", "''") + "'"


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
        print('  GOT', got); print('  EXP', exp); raise SystemExit('verify failed; nothing written')
    text = open(PATH).read()
    if 'id="gi-leaf-streak"' in text:
        print('gi-leaf-streak already present; nothing to do.'); return
    before = balance(text)
    leaf = LEAF_OPEN + '              ' + eb.build_card(CARD) + LEAF_CLOSE
    marker = '<div class="problem-card collapsed qtype-group" id="gi-leaf-adjacency">'
    idx = text.find(marker)
    if idx < 0:
        raise SystemExit('gi-leaf-adjacency marker not found')
    text = text[:idx] + leaf + '\n\n          ' + text[idx:]
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE gi-leaf-streak to', PATH)


if __name__ == '__main__':
    main()
