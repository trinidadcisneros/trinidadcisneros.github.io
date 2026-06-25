"""Into pit-tmpl-fill: an inline collapsed accordion that walks a single-series
fill-forward (sprint velocity) through filter -> sort -> pick, plus a traps panel
(cast text columns; order by date not value; same-day corrections -> recorded_at
tiebreak). Every table computed in real Postgres (pgserver). Idempotent + balance-checked.
Run:  python3 build_pit_fill_walkthrough.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
SENTINEL = 'id="pit-walk-fill"'

# sprint_id, effective_date (TEXT), story_points (TEXT), recorded_at
DATA = [
    ('SPRINT-42', '2024-03-01', '0',  '2024-03-01 08:00:00'),
    ('SPRINT-42', '2024-03-03', '5',  '2024-03-03 10:00:00'),
    ('SPRINT-42', '2024-03-03', '6',  '2024-03-03 16:00:00'),   # same-day correction
    ('SPRINT-42', '2024-03-05', '13', '2024-03-05 14:00:00'),
    ('SPRINT-42', '2024-03-09', '21', '2024-03-09 16:00:00'),
    ('SPRINT-99', '2024-03-02', '8',  '2024-03-02 09:00:00'),   # decoy: different sprint
    ('SPRINT-99', '2024-03-06', '15', '2024-03-06 11:00:00'),
]
ORDER = "h.effective_date::date DESC, h.recorded_at DESC"


def rows_of(srv, q, ncols):
    out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + q)
    res = []
    for l in out.strip().splitlines():
        if l.count('|') == ncols - 1 and 'format is' not in l and 'separator is' not in l:
            res.append([None if c == '' else c for c in l.split('|')])
    return res


def card(title, excerpt, inner, mtop=12, border='#cbd5e1', cid=None, fs='1.15rem'):
    idattr = (' id="%s"' % cid) if cid else ''
    return ('''<div%(id)s class="problem-card collapsed" style="margin: %(mt)spx 0 0; border-left:4px solid %(bd)s;">
                      <div class="problem-card-header">
                        <h3 class="problem-card-title" style="margin:0; font-size:%(fs)s;">%(title)s</h3>
                        <span class="problem-toggle">&#9660;</span>
                      </div>
                      <div class="problem-card-excerpt"><p style="margin:0;">%(ex)s</p></div>
                      <div class="problem-card-content">
                        %(inner)s
                      </div>
                    </div>''' % {'id': idattr, 'mt': mtop, 'bd': border, 'fs': fs,
                                 'title': title, 'ex': excerpt, 'inner': inner})


def main():
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        srv.psql('CREATE TABLE sprint_velocity_history(sprint_id varchar(50), effective_date text, story_points_completed text, recorded_at timestamp);')
        for r in DATA:
            srv.psql("INSERT INTO sprint_velocity_history VALUES ('%s','%s','%s','%s');" % r)
        DT = eb.data_table
        t_input = [list(r) for r in DATA]
        t_spine = rows_of(srv, "SELECT generate_series('2024-03-01'::date,'2024-03-10'::date,INTERVAL '1 day')::date AS report_date;", 1)
        # zoom on 2024-03-04
        t_2a = rows_of(srv, "SELECT effective_date, story_points_completed, recorded_at FROM sprint_velocity_history h WHERE h.sprint_id='SPRINT-42' AND h.effective_date::date <= '2024-03-04' ORDER BY effective_date;", 3)
        t_2b = rows_of(srv, "SELECT effective_date, story_points_completed, recorded_at FROM sprint_velocity_history h WHERE h.sprint_id='SPRINT-42' AND h.effective_date::date <= '2024-03-04' ORDER BY %s;" % ORDER, 3)
        # all 10 days: report_date | change used (date) | velocity
        t_all = rows_of(srv, (
            "SELECT d.report_date, "
            "(SELECT h.effective_date::date FROM sprint_velocity_history h WHERE h.sprint_id='SPRINT-42' AND h.effective_date::date <= d.report_date ORDER BY %s LIMIT 1) AS change_used, "
            "(SELECT h.story_points_completed::int FROM sprint_velocity_history h WHERE h.sprint_id='SPRINT-42' AND h.effective_date::date <= d.report_date ORDER BY %s LIMIT 1) AS velocity_on_date "
            "FROM (SELECT generate_series('2024-03-01'::date,'2024-03-10'::date,INTERVAL '1 day')::date AS report_date) d ORDER BY d.report_date;" % (ORDER, ORDER)), 3)
        t_final = rows_of(srv, (
            "SELECT d.report_date, "
            "(SELECT h.story_points_completed::int FROM sprint_velocity_history h WHERE h.sprint_id='SPRINT-42' AND h.effective_date::date <= d.report_date ORDER BY %s LIMIT 1) AS velocity_on_date "
            "FROM (SELECT generate_series('2024-03-01'::date,'2024-03-10'::date,INTERVAL '1 day')::date AS report_date) d ORDER BY d.report_date;" % ORDER), 2)
        # trap 4c: the 03-03 tie
        t_tie = rows_of(srv, "SELECT effective_date, story_points_completed, recorded_at FROM sprint_velocity_history h WHERE h.sprint_id='SPRINT-42' AND h.effective_date='2024-03-03' ORDER BY recorded_at DESC;", 3)
    finally:
        srv.cleanup()

    DT = eb.data_table
    # ---- Step 2 zoomed on 03-04 ----
    s2a = card('Move 1 &mdash; keep this sprint&#x27;s changes on or before the day', 'WHERE sprint = SPRINT-42 AND effective_date &le; 2024-03-04.',
               '<p style="margin:0 0 6px;">SPRINT-99 is filtered out, and 03-05 / 03-09 are still in the future, so three rows survive (note 03-03 appears twice &mdash; a same-day correction):</p>' + DT(['effective_date', 'story_points', 'recorded_at'], t_2a), mtop=10, border='#2e7d32')
    s2b = card('Move 2 &mdash; sort newest first, latest-recorded breaking ties', 'ORDER BY effective_date DESC, recorded_at DESC.',
               '<p style="margin:0 0 6px;">Newest date on top; where 03-03 ties, the later <code>recorded_at</code> (the 16:00 correction) wins:</p>' + DT(['effective_date', 'story_points', 'recorded_at'], t_2b), mtop=10, border='#2e7d32')
    s2c = card('Move 3 &mdash; take the top one (LIMIT 1)', 'The single winner becomes this day&#x27;s value.',
               '<p style="margin:0;">Top row is <strong>2024-03-03 &rarr; 6</strong>, so 03-04 = <strong>6</strong>. Two things happened at once: 03-04 had no change of its own so it <em>borrowed</em> 03-03 (the carry forward), and among 03-03&#x27;s two rows the later-recorded <strong>6</strong> beat the earlier 5 (the tiebreak).</p>', mtop=10, border='#2e7d32')

    step1 = card('Step 1 &mdash; build the date spine', 'One row per day, nothing attached yet.',
                 '<p style="margin:0 0 6px;">generate_series gives all 10 calendar days:</p>' + DT(['report_date'], t_spine), border='#1565c0')
    step2 = card('Step 2 &mdash; the per-day lookup, zoomed in on 2024-03-04', 'The engine of the query: filter &rarr; sort &rarr; pick. Open each move.',
                 '<p style="margin:0 0 8px;">This subquery runs once per spine day. Here it is for 03-04 in three moves:</p>' + s2a + s2b + s2c, border='#1565c0')
    step3 = card('Step 3 &mdash; do that lookup for all 10 days', 'The change used repeats on quiet days &mdash; that is the carry forward.',
                 '<p style="margin:0 0 6px;">Each day shows which change it landed on and the value it carries:</p>' + DT(['report_date', 'change_used', 'velocity_on_date'], t_all), border='#1565c0')

    # ---- Step 4 traps ----
    t4a = card('Trap A &mdash; cast the TEXT columns', 'effective_date and story_points are stored as text.',
               '<p style="margin:0;">The schema stores <code>effective_date</code> and <code>story_points_completed</code> as TEXT. Cast them: <code>effective_date::date</code> so dates compare and sort as dates, and <code>story_points_completed::int</code> so the value is a number, not a string.</p>', mtop=10, border='#e65100')
    t4b = card('Trap B &mdash; order by DATE, not by value', 'Sorting by the value picks the wrong row when velocity drops.',
               '<p style="margin:0 0 6px;">If velocity ever falls, "biggest so far" and "most recent" diverge. With changes 10 &rarr; 30 &rarr; 12:</p>' + DT(['day', 'by value (wrong)', 'by date (right)'], [['2024-03-05', '30', '12'], ['2024-03-06', '30', '12']]) + '<p style="margin:6px 0 0;">"Most recent" means newest <em>date</em>, never the largest number.</p>', mtop=10, border='#e65100')
    t4c = card('Trap C &mdash; same-day corrections: break the tie with recorded_at', 'Two rows can share an effective_date; pick the latest-recorded.',
               '<p style="margin:0 0 6px;">03-03 has two rows. Ordering by date alone leaves them tied and LIMIT 1 grabs a random one. <code>recorded_at DESC</code> takes the correction logged at 16:00:</p>' + DT(['effective_date', 'story_points', 'recorded_at'], t_tie) + '<p style="margin:6px 0 0;">So the value in effect for 03-03 is <strong>6</strong>, not 5.</p>', mtop=10, border='#e65100')
    step4 = card('Step 4 &mdash; the three traps', 'Easy to miss, each one fails a hidden test.',
                 t4a + t4b + t4c, border='#1565c0')

    step5 = card('Step 5 &mdash; the final two columns', 'Drop the helper column for the answer.',
                 DT(['report_date', 'velocity_on_date'], t_final), border='#1565c0')

    intro = ('<p style="margin:0 0 8px;">A single-series fill forward: one sprint (SPRINT-42), all 10 days from 2024-03-01 to 2024-03-10. '
             'For multiple entities you would add the entity to the spine and the lookup, as the template above shows.</p>'
             '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>sprint_velocity_history</code></strong> (note the TEXT columns, a SPRINT-99 decoy, and two rows for 03-03):</p>'
             + eb.data_table(['sprint_id', 'effective_date', 'story_points_completed', 'recorded_at'], t_input))

    accordion = card('&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
                     'A 10-day sprint snapshot, step by step &mdash; filter, sort, pick, plus the three traps.',
                     intro + step1 + step2 + step3 + step4 + step5,
                     mtop=14, border='#6a1b9a', cid='pit-walk-fill', fs='1.25rem')

    text = open(PATH).read()
    if SENTINEL in text:
        print('fill walkthrough already present; nothing to do.'); return
    # insert as last child of pit-tmpl-fill content
    cs = text.find('id="pit-tmpl-fill"')
    cs = text.rfind('<div', 0, cs)
    content = text.find('<div class="problem-card-content">', cs)
    depth = 0; close = None
    for m in re.finditer(r'<(/?)div\b', text[content:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            close = content + m.start(); break
    if close is None:
        raise SystemExit('could not locate pit-tmpl-fill content close')
    do0 = len(re.findall(r'<div\b', text)); dc0 = len(re.findall(r'</div\b', text))
    text = text[:close] + '\n                    ' + accordion + '\n                  ' + text[close:]
    do1 = len(re.findall(r'<div\b', text)); dc1 = len(re.findall(r'</div\b', text))
    depth = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', text):
        depth += 1 if m.group(1) == '' else -1; mn = min(mn, depth)
    print('expected final:', [r[1] for r in t_final])
    print('div %d/%d -> %d/%d depth %d min %d' % (do0, dc0, do1, dc1, depth, mn))
    if do1 != dc1 or depth != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE fill-forward walkthrough accordion into pit-tmpl-fill')


if __name__ == '__main__':
    main()
