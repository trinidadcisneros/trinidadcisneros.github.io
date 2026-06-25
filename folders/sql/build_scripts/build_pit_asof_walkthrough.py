"""Into tw-tmpl-pit (the As-of-single-cutoff template): an inline collapsed accordion
that walks the DROP variant through date guard -> rank -> keep rn=1, with two routes
(ROW_NUMBER and DISTINCT ON). Mirrors the Default walkthrough. Every table computed in
real Postgres (pgserver). Idempotent + balance-checked.
Run:  python3 build_pit_asof_walkthrough.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
SENTINEL = 'id="pit-walk-asof"'

DATA = [
    (101, 'basic', '2024-03-01'), (101, 'premium', '2024-05-15'), (101, 'standard', '2024-07-01'),
    (102, 'premium', '2024-04-10'), (102, 'basic', '2024-06-10'),
    (103, 'standard', '2024-06-20'),   # only row is after the cutoff -> dropped
]
CUTOFF = '2024-06-15'


def rows_of(srv, q, ncols):
    out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + q)
    return [[None if c == '' else c for c in l.split('|')]
            for l in out.strip().splitlines()
            if l.count('|') == ncols - 1 and 'format is' not in l and 'separator is' not in l]


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
        srv.psql('CREATE TABLE subscription_history(viewer_id int, tier varchar(20), effective_date date);')
        for r in DATA:
            srv.psql("INSERT INTO subscription_history VALUES (%d,'%s','%s');" % r)
        DT = eb.data_table
        t_input = [list(r) for r in DATA]
        t_guard = rows_of(srv, "SELECT viewer_id, tier, effective_date FROM subscription_history WHERE effective_date <= '%s' ORDER BY viewer_id, effective_date;" % CUTOFF, 3)
        t_ranked = rows_of(srv, "SELECT viewer_id, tier, effective_date, ROW_NUMBER() OVER (PARTITION BY viewer_id ORDER BY effective_date DESC) AS rn FROM subscription_history WHERE effective_date <= '%s' ORDER BY viewer_id, rn;" % CUTOFF, 4)
        t_final = rows_of(srv, "SELECT viewer_id, tier AS active_tier FROM (SELECT viewer_id, tier, ROW_NUMBER() OVER (PARTITION BY viewer_id ORDER BY effective_date DESC) AS rn FROM subscription_history WHERE effective_date <= '%s') q WHERE rn=1 ORDER BY viewer_id;" % CUTOFF, 2)
        t_distinct = rows_of(srv, "SELECT DISTINCT ON (viewer_id) viewer_id, tier AS active_tier FROM subscription_history WHERE effective_date <= '%s' ORDER BY viewer_id, effective_date DESC;" % CUTOFF, 2)
    finally:
        srv.cleanup()

    DT = eb.data_table
    route_a = card('Route A &mdash; ROW_NUMBER staircase', 'Number each viewer&#x27;s surviving rows newest first, then keep rn = 1.',
                   '<p style="margin:0 0 6px;">Rank within each viewer, newest date first:</p>' + DT(['viewer_id', 'tier', 'effective_date', 'rn'], t_ranked) +
                   '<p style="margin:10px 0 6px;">Keep <code>rn = 1</code> &mdash; the latest as of the cutoff:</p>' + DT(['viewer_id', 'active_tier'], t_final),
                   mtop=10, border='#2e7d32')
    route_b = card('Route B &mdash; DISTINCT ON', 'Same answer in one step (Postgres).',
                   '<p style="margin:0 0 6px;"><code>DISTINCT ON (viewer_id) ... ORDER BY viewer_id, effective_date DESC</code> keeps the newest per viewer:</p>' + DT(['viewer_id', 'active_tier'], t_distinct),
                   mtop=10, border='#2e7d32')

    step1 = card('Step 1 &mdash; keep rows on or before the cutoff (date guard)', 'Future rows go; an entity with nothing left here will simply drop out.',
                 '<p style="margin:0 0 6px;">Cutoff = <code>%s</code>. Viewer 101&#x27;s 07-01 row and viewer 103&#x27;s only row (06-20) are in the future, so they are removed. Viewer 103 now has NO rows at all &mdash; that is how it gets dropped (no default here):</p>%s' % (CUTOFF, DT(['viewer_id', 'tier', 'effective_date'], t_guard)),
                 border='#1565c0')
    step2 = card('Step 2 &mdash; pick each entity&#x27;s newest survivor', 'Two routes, same answer. Open each.',
                 '<p style="margin:0 0 8px;">This is the only step where the two forms differ.</p>' + route_a + route_b,
                 border='#1565c0')
    step3 = card('Step 3 &mdash; the result', 'One row per entity that had a qualifying row; the rest are gone.',
                 '<p style="margin:0 0 6px;">Viewer 103 never appears &mdash; it had no record on or before the cutoff. (If the prompt wanted it kept with a default, that is the Default-when-no-history leaf.)</p>' + DT(['viewer_id', 'active_tier'], t_final),
                 border='#1565c0')

    intro = ('<p style="margin:0 0 8px;">The DROP variant: one snapshot per entity as of a single cutoff, and entities with no record by then disappear (no default). Cutoff <code>%s</code>.</p>'
             '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>subscription_history</code></strong> (viewer 103&#x27;s only row is after the cutoff):</p>'
             % CUTOFF) + eb.data_table(['viewer_id', 'tier', 'effective_date'], t_input)

    accordion = card('&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
                     'A single-cutoff snapshot, step by step &mdash; date guard, rank, keep the newest. The no-record entity drops.',
                     intro + step1 + step2 + step3,
                     mtop=14, border='#6a1b9a', cid='pit-walk-asof', fs='1.25rem')

    text = open(PATH).read()
    if SENTINEL in text:
        print('asof walkthrough already present; nothing to do.'); return
    cs = text.find('id="tw-tmpl-pit"')
    cs = text.rfind('<div', 0, cs)
    content = text.find('<div class="problem-card-content">', cs)
    depth = 0; close = None
    for m in re.finditer(r'<(/?)div\b', text[content:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            close = content + m.start(); break
    if close is None:
        raise SystemExit('could not locate tw-tmpl-pit content close')
    do0 = len(re.findall(r'<div\b', text)); dc0 = len(re.findall(r'</div\b', text))
    text = text[:close] + '\n                  ' + accordion + '\n                ' + text[close:]
    do1 = len(re.findall(r'<div\b', text)); dc1 = len(re.findall(r'</div\b', text))
    depth = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', text):
        depth += 1 if m.group(1) == '' else -1; mn = min(mn, depth)
    print('final:', [r for r in t_final], '| distinct route:', t_distinct)
    print('div %d/%d -> %d/%d depth %d min %d' % (do0, dc0, do1, dc1, depth, mn))
    if do1 != dc1 or depth != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE as-of walkthrough accordion into tw-tmpl-pit')


if __name__ == '__main__':
    main()
