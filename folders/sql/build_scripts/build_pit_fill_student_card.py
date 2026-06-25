"""Add Trinidad's preferred 'named spine CTE + per-entity lookup' fill-forward as a
worked card in pit-leaf-fill (the multi-student, keep-NULL example). Badge 2 -> 3.
Verified in real Postgres (pgserver). Idempotent + balance-checked.
Run:  python3 build_pit_fill_student_card.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
SENTINEL = 'Daily Difficulty Level per Student'


def build_exp():
    L101 = ['beginner', 'beginner', 'intermediate', 'intermediate', 'intermediate',
            'intermediate', 'advanced', 'advanced', 'advanced', 'advanced']
    L102 = [None, 'beginner', 'beginner', 'beginner', 'intermediate', 'intermediate',
            'intermediate', 'intermediate', 'intermediate', 'intermediate']
    rows = []
    for i in range(10):
        rows.append([101, '2024-03-%02d' % (i + 1), L101[i]])
    for i in range(10):
        rows.append([102, '2024-03-%02d' % (i + 1), L102[i]])
    for i in range(10):
        rows.append([103, '2024-03-%02d' % (i + 1), None])
    return rows


CARD = {
    'diff': 'Medium', 'color': '#e65100',
    'title': 'Daily Difficulty Level per Student (Fill Forward, named spine)',
    'excerpt': "Per-student daily snapshot using a named spine CTE plus a per-student lookup. Students with no row yet show NULL; the last preference carries forward.",
    'prompt': [
        "<code>student_difficulty_history</code> records each student's difficulty preference and the <code>effective_date</code> it took effect.",
        "Produce a daily report for EVERY student and EVERY day from 2024-03-01 to 2024-03-10, showing the level in effect that day.",
        "On a day with no new row, carry forward the most recent earlier preference. For days before a student's first row, show NULL.",
        "Return <code>student_id</code>, <code>report_date</code>, <code>difficulty_level</code>, ordered by <code>student_id</code>, <code>report_date</code>.",
    ],
    'inputs': [{
        'name': 'student_difficulty_history',
        'cols': [('student_id', 'INT'), ('difficulty_level', 'VARCHAR(20)'), ('effective_date', 'DATE')],
        'headers': ['student_id', 'difficulty_level', 'effective_date'],
        'rows': [
            [101, 'beginner', '2024-02-28'], [101, 'intermediate', '2024-03-03'], [101, 'advanced', '2024-03-07'],
            [102, 'beginner', '2024-03-02'], [102, 'intermediate', '2024-03-05'],
            [103, 'advanced', '2024-03-12'],
        ],
    }],
    'exp_headers': ['student_id', 'report_date', 'difficulty_level'],
    'exp_rows': build_exp(),
    'sol_comment': (
        "This is the readable 'named spine' layout: build the every-student-by-every-day grid in its own\n"
        "CTE (spine), then in the main query look up each (student, day)'s value separately. Splitting the\n"
        "two jobs makes the logic easy to read.\n"
        "  spine    : DISTINCT students CROSS JOIN the 10-day series = one row per student per day.\n"
        "  subquery : for THIS student, the newest preference on or before THIS day (ORDER BY effective_date\n"
        "             DESC, take 1). A day before the student's first row finds nothing and stays NULL.\n"
        "Student 102 has no row until 03-02, so 03-01 is NULL. Student 103's only row (03-12) is outside the\n"
        "window, so all 10 days are NULL. The carry forward is automatic: a quiet day keeps finding the same\n"
        "newest earlier row. Same logic as the template above, just laid out as a named spine. Verified: 30 rows."
    ),
    'sol_sql': (
        "WITH spine AS (                                    -- one row per student per day\n"
        "    SELECT s.student_id, d.report_date\n"
        "    FROM (SELECT generate_series('2024-03-01'::date, '2024-03-10'::date, INTERVAL '1 day')::date AS report_date) AS d\n"
        "    CROSS JOIN (SELECT DISTINCT student_id FROM student_difficulty_history) AS s\n"
        ")\n"
        "SELECT s.student_id,\n"
        "       s.report_date,\n"
        "       (SELECT h.difficulty_level                  -- this student's latest level on/before the day\n"
        "        FROM student_difficulty_history AS h\n"
        "        WHERE h.student_id = s.student_id\n"
        "          AND h.effective_date <= s.report_date\n"
        "        ORDER BY h.effective_date DESC\n"
        "        LIMIT 1) AS difficulty_level               -- before the first row -> NULL\n"
        "FROM spine AS s\n"
        "ORDER BY s.student_id, s.report_date;"
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
        return got == exp, len(got), len(exp)
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
    ok, gn, en = verify_pg(CARD)
    print('[pg-verify %s] %s  (%d/%d rows)' % ('OK ' if ok else 'FAIL', CARD['title'], gn, en))
    if not ok:
        raise SystemExit('verify failed; nothing written')
    text = open(PATH).read()
    if SENTINEL in text:
        print('student card already present; nothing to do.'); return
    before = balance(text)
    # last child of pit-leaf-fill content
    cs = text.find('id="pit-leaf-fill"')
    cs = text.rfind('<div', 0, cs)
    content = text.find('<div class="problem-card-content">', cs)
    depth = 0; close = None
    for m in re.finditer(r'<(/?)div\b', text[content:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            close = content + m.start(); break
    if close is None:
        raise SystemExit('could not locate pit-leaf-fill content close')
    text = text[:close] + '\n              ' + eb.build_card(CARD) + '\n              ' + text[close:]
    text = text.replace('Fill forward over a date spine <span class="count-badge">2 problems</span>',
                        'Fill forward over a date spine <span class="count-badge">3 problems</span>', 1)
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE student named-spine fill card into pit-leaf-fill (badge -> 3 problems)')


if __name__ == '__main__':
    main()
