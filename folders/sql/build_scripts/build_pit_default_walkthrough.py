"""Into pit-tmpl-default: add the Form B (LEFT JOIN LATERAL) code block AND an
inline collapsed accordion that walks the portfolio example through both routes,
with nested collapsible steps. Every intermediate table is computed in real
Postgres (pgserver) so the numbers are exact. Idempotent + balance-checked.
Run:  python3 build_pit_default_walkthrough.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
SENTINEL = 'id="pit-walk-default"'

DATA = [
    (101, '2024-01-10', 70, 30), (101, '2024-05-20', 80, 20), (101, '2024-07-01', 65, 35),
    (102, '2024-03-15', 50, 50), (102, '2024-06-10', 55, 45),
    (103, '2024-08-01', 90, 10),
    (104, '2024-02-28', 75, 25), (104, '2024-06-20', 70, 30),
]
CUTOFF = '2024-06-15'

FORM_B = (
    '''                    <p style="margin:14px 0 4px;"><strong>Form B &mdash; LEFT JOIN LATERAL</strong> <span style="color:#64748b;">(Postgres only; shorter, looks the value up per entity)</span></p>
                  <pre style="margin:0; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>SELECT e.key_col, COALESCE(h.val, :default_val) AS val_as_of
FROM (SELECT DISTINCT key_col FROM hist) e
LEFT JOIN LATERAL (
  SELECT val
  FROM hist
  WHERE key_col = e.key_col AND as_of_date &lt;= :cutoff
  ORDER BY as_of_date DESC
  LIMIT 1
) h ON true                                  -- matching already done inside, so ON true
ORDER BY e.key_col;</code></pre>
''')


def rows_of(srv, q, ncols):
    out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + q)
    res = []
    for l in out.strip().splitlines():
        if l.count('|') == ncols - 1 and 'format is' not in l and 'separator is' not in l:
            res.append([None if c == '' else c for c in l.split('|')])
    return res


def card(title, excerpt, inner, mtop=12, border='#cbd5e1', cid=None):
    idattr = (' id="%s"' % cid) if cid else ''
    return ('''<div%(id)s class="problem-card collapsed" style="margin: %(mt)spx 0 0; border-left:4px solid %(bd)s;">
                      <div class="problem-card-header">
                        <h3 class="problem-card-title" style="margin:0; font-size:1.15rem;">%(title)s</h3>
                        <span class="problem-toggle">&#9660;</span>
                      </div>
                      <div class="problem-card-excerpt"><p style="margin:0;">%(ex)s</p></div>
                      <div class="problem-card-content">
                        %(inner)s
                      </div>
                    </div>''' % {'id': idattr, 'mt': mtop, 'bd': border,
                                 'title': title, 'ex': excerpt, 'inner': inner})


def main():
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        srv.psql('CREATE TABLE portfolio_allocations(client_id int, effective_date varchar(20), equity_pct int, bond_pct int);')
        for r in DATA:
            srv.psql("INSERT INTO portfolio_allocations VALUES (%d,'%s',%d,%d);" % r)
        t_input = [list(r) for r in DATA]
        t_entities = rows_of(srv, 'SELECT DISTINCT client_id FROM portfolio_allocations ORDER BY client_id;', 1)
        t_ranked = rows_of(srv, (
            "SELECT client_id, effective_date, equity_pct, bond_pct, "
            "ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY effective_date DESC) AS rn "
            "FROM portfolio_allocations WHERE effective_date <= '%s' ORDER BY client_id, rn;" % CUTOFF), 5)
        t_rn1 = rows_of(srv, (
            "SELECT client_id, equity_pct, bond_pct FROM (SELECT client_id, equity_pct, bond_pct, "
            "ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY effective_date DESC) AS rn "
            "FROM portfolio_allocations WHERE effective_date <= '%s') q WHERE rn=1 ORDER BY client_id;" % CUTOFF), 3)
        t_join = rows_of(srv, (
            "SELECT e.client_id, r.equity_pct, r.bond_pct FROM (SELECT DISTINCT client_id FROM portfolio_allocations) e "
            "LEFT JOIN (SELECT client_id, equity_pct, bond_pct, ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY effective_date DESC) AS rn "
            "FROM portfolio_allocations WHERE effective_date <= '%s') r ON r.client_id=e.client_id AND r.rn=1 ORDER BY e.client_id;" % CUTOFF), 3)
        t_final = rows_of(srv, (
            "SELECT e.client_id, COALESCE(r.equity_pct,60) AS equity_pct, COALESCE(r.bond_pct,40) AS bond_pct "
            "FROM (SELECT DISTINCT client_id FROM portfolio_allocations) e "
            "LEFT JOIN (SELECT client_id, equity_pct, bond_pct, ROW_NUMBER() OVER (PARTITION BY client_id ORDER BY effective_date DESC) AS rn "
            "FROM portfolio_allocations WHERE effective_date <= '%s') r ON r.client_id=e.client_id AND r.rn=1 ORDER BY e.client_id;" % CUTOFF), 3)
    finally:
        srv.cleanup()

    DT = eb.data_table
    # nested routes inside step 2
    route_a = card(
        'Route A &mdash; ROW_NUMBER staircase',
        'Number each client’s on-or-before rows newest first, then keep rn = 1.',
        '<p style="margin:0 0 6px;"><strong>The <code>ranked</code> CTE</strong> &mdash; only rows on or before %s survive (the future-dated ones are already gone), numbered newest first:</p>%s'
        '<p style="margin:10px 0 6px;"><strong>Keep <code>rn = 1</code></strong> &mdash; the newest per client (note client 103 is absent, it had no qualifying row):</p>%s'
        % (CUTOFF, DT(['client_id', 'effective_date', 'equity_pct', 'bond_pct', 'rn'], t_ranked),
           DT(['client_id', 'equity_pct', 'bond_pct'], t_rn1)),
        mtop=10, border='#2e7d32')
    route_b = card(
        'Route B &mdash; LEFT JOIN LATERAL',
        'Look up each client’s single newest on-or-before row directly.',
        '<p style="margin:0 0 6px;">For each client the lateral subquery returns just its newest allocation on or before %s (client 103 finds nothing). Same result as Route A:</p>%s'
        % (CUTOFF, DT(['client_id', 'equity_pct', 'bond_pct'], t_rn1)),
        mtop=10, border='#2e7d32')

    step1 = card('Step 1 &mdash; the starting list (one row per client)',
                 'Both routes start the same way: <code>SELECT DISTINCT client_id</code>.',
                 '<p style="margin:0 0 6px;">This is the backbone so every client appears once, including ones we will later fill with the default:</p>' + DT(['client_id'], t_entities),
                 border='#1565c0')
    step2 = card('Step 2 &mdash; find each client’s latest value on or before the cutoff',
                 'Two routes, same answer. Open each.',
                 '<p style="margin:0 0 8px;">Cutoff = <code>%s</code>. This is the only step where the two forms differ.</p>%s%s' % (CUTOFF, route_a, route_b),
                 border='#1565c0')
    step3 = card('Step 3 &mdash; attach it to the client list (LEFT JOIN)',
                 'Staple each client’s value onto the backbone; no match leaves NULL.',
                 '<p style="margin:0 0 6px;">Client 103 had nothing, so the LEFT JOIN keeps it with empty slots instead of dropping it:</p>' + DT(['client_id', 'equity_pct', 'bond_pct'], t_join),
                 border='#1565c0')
    step4 = card('Step 4 &mdash; fill the default (COALESCE)',
                 'Turn the NULLs into 60 / 40 &mdash; the final answer.',
                 '<p style="margin:0 0 6px;">COALESCE swaps each NULL for the platform default, giving the expected output:</p>' + DT(['client_id', 'equity_pct', 'bond_pct'], t_final),
                 border='#1565c0')

    intro = ('<p style="margin:0 0 8px;">Worked on the same data you practised with: 4 clients, cutoff <code>%s</code>, default <code>60 / 40</code>. '
             'Both code forms above take the same path &mdash; only Step 2 differs. Open each step to watch the table change.</p>'
             '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>portfolio_allocations</code></strong></p>%s'
             % (CUTOFF, eb.data_table(['client_id', 'effective_date', 'equity_pct', 'bond_pct'], t_input)))

    accordion = card(
        '&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
        'Same data, two routes, one answer &mdash; open each step to see the table change.',
        intro + step1 + step2 + step3 + step4,
        mtop=14, border='#6a1b9a', cid='pit-walk-default')

    text = open(PATH).read()
    if SENTINEL in text:
        print('walkthrough already present; nothing to do.'); return
    do0 = len(re.findall(r'<div\b', text)); dc0 = len(re.findall(r'</div\b', text))
    anchor = 'ORDER BY e.key_col;</code></pre>'
    i = text.find(anchor)
    if i < 0:
        raise SystemExit('template anchor not found')
    j = i + len(anchor)
    insert = '\n' + FORM_B + '\n                    ' + accordion + '\n'
    text = text[:j] + insert + text[j:]
    do1 = len(re.findall(r'<div\b', text)); dc1 = len(re.findall(r'</div\b', text))
    depth = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', text):
        depth += 1 if m.group(1) == '' else -1; mn = min(mn, depth)
    print('div %d/%d -> %d/%d, depth %d, min %d' % (do0, dc0, do1, dc1, depth, mn))
    if do1 != dc1 or depth != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE Form B + walkthrough accordion into pit-tmpl-default')


if __name__ == '__main__':
    main()
