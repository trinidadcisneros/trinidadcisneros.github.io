"""Add two leaves to Single-Table > Rank & Percentile (rank-percentile) for the
hypothetical-set aggregates that map to the new engine subtypes:
  rp-leaf-hyp-rank      <- percentile_metrics / hypothetical_rank      (rank / dense_rank WITHIN GROUP)
  rp-leaf-hyp-fraction  <- percentile_metrics / hypothetical_fraction  (percent_rank / cume_dist WITHIN GROUP)

DuckDB does NOT support hypothetical-set aggregates, so the worked cards are
verified against a real Postgres spun up via pgserver (these functions are
Postgres-only; nb01's validator is also real Postgres). build_card renders the
HTML; this script does its own Postgres verify (NOT eabuild.verify, which is DuckDB).

Run:  python3 build_hyp_leaves.py
Edit PATH below to the current mount if re-running in a new session.
"""
import re, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb  # build_card, balance_report

PATH = "/sessions/quirky-confident-allen/mnt/bitterscientist.com/folders/sql/sql_problem_patterns.html"

# ---------------- worked cards ----------------
CARD_RANK = {
    'diff': 'Medium', 'color': '#e65100',
    'title': "Where a New Applicant's Credit Score Would Rank by Region",
    'excerpt': "A hypothetical credit score of 720 ranked inside each region's existing scores, with gaps (rank) and without (dense_rank), no row inserted.",
    'prompt': [
        "A lender wants to know where a NEW applicant with a credit score of <code>720</code> would rank among existing applicants in each region, without adding them to the table yet.",
        "The <code>applications</code> table holds one row per existing applicant with their region and credit_score.",
        "For each region, compute the rank the value <code>720</code> would receive among the existing credit_score values sorted ascending (lowest score ranks 1), as BOTH a rank with gaps after ties (<code>hyp_rank</code>) and a dense rank with no gaps (<code>hyp_dense_rank</code>).",
        "Return <code>region</code>, <code>hyp_rank</code>, <code>hyp_dense_rank</code>, ordered by region.",
    ],
    'inputs': [{
        'name': 'applications',
        'cols': [('application_id', 'INTEGER'), ('region', 'VARCHAR'), ('credit_score', 'INTEGER')],
        'headers': ['application_id', 'region', 'credit_score'],
        'rows': [
            [1, 'west', 680], [2, 'west', 700], [3, 'west', 700], [4, 'west', 740], [5, 'west', 760],
            [6, 'east', 650], [7, 'east', 720], [8, 'east', 720], [9, 'east', 800],
        ],
    }],
    'exp_headers': ['region', 'hyp_rank', 'hyp_dense_rank'],
    'exp_rows': [['east', 2, 2], ['west', 4, 3]],
    'sol_comment': (
        "rank() / dense_rank() WITH the WITHIN GROUP clause are HYPOTHETICAL-SET aggregates:\n"
        "the argument (720) is a candidate value, WITHIN GROUP (ORDER BY credit_score) sorts each\n"
        "region's EXISTING scores, and the function returns the rank that candidate WOULD get if it\n"
        "were inserted -- without inserting anything. GROUP BY region gives one answer per region.\n"
        "  west scores 680,700,700,740,760: three are below 720 -> rank 4; two DISTINCT below -> dense_rank 3.\n"
        "  east scores 650,720,720,800: one below 720, and 720 ties the existing 720s -> rank 2, dense_rank 2.\n"
        "rank leaves a gap after ties, dense_rank does not. Note this is NOT rank() OVER (...): the window\n"
        "form ranks rows that already exist, one value per row, and there is no row for the candidate here."
    ),
    'sol_sql': (
        "SELECT region,\n"
        "       rank(720) WITHIN GROUP (ORDER BY credit_score)       AS hyp_rank,        -- gaps after ties\n"
        "       dense_rank(720) WITHIN GROUP (ORDER BY credit_score) AS hyp_dense_rank   -- no gaps\n"
        "FROM applications\n"
        "GROUP BY region\n"
        "ORDER BY region;"
    ),
}

CARD_FRAC = {
    'diff': 'Medium', 'color': '#e65100',
    'title': "Where a 45-Minute Resolution Would Stand by Team",
    'excerpt': "A hypothetical 45-minute ticket placed inside each team's resolution times as a fraction 0..1, percent_rank vs cume_dist, no row inserted.",
    'prompt': [
        "A support lead wants to know where a new ticket resolved in <code>45</code> minutes would stand within each team's existing resolution times, as a fraction from 0 to 1, without logging the ticket yet.",
        "The <code>support_tickets</code> table holds one row per resolved ticket with its team and resolution_minutes.",
        "For each team, compute <code>percent_rank</code> and <code>cume_dist</code> for the value <code>45</code> among the existing resolution_minutes sorted ascending (faster first), each rounded to 4 decimals.",
        "Return <code>team</code>, <code>hyp_percent_rank</code>, <code>hyp_cume_dist</code>, ordered by team.",
    ],
    'inputs': [{
        'name': 'support_tickets',
        'cols': [('ticket_id', 'INTEGER'), ('team', 'VARCHAR'), ('resolution_minutes', 'INTEGER')],
        'headers': ['ticket_id', 'team', 'resolution_minutes'],
        'rows': [
            [1, 'alpha', 10], [2, 'alpha', 30], [3, 'alpha', 50], [4, 'alpha', 60],
            [5, 'beta', 20], [6, 'beta', 40], [7, 'beta', 40], [8, 'beta', 90], [9, 'beta', 100],
        ],
    }],
    'exp_headers': ['team', 'hyp_percent_rank', 'hyp_cume_dist'],
    'exp_rows': [['alpha', '0.5000', '0.6000'], ['beta', '0.6000', '0.6667']],
    'sol_comment': (
        "percent_rank() and cume_dist() WITH the WITHIN GROUP clause are HYPOTHETICAL-SET aggregates,\n"
        "the fraction cousins of rank: where would 45 stand within each team's existing times, 0..1,\n"
        "without inserting a row. GROUP BY team gives one answer per team.\n"
        "  percent_rank = (hypothetical rank - 1) / number of existing rows. It is 0 when the value\n"
        "  would tie for first. alpha: existing 10,30,50,60; 45 ranks 3rd -> (3-1)/4 = 0.5000.\n"
        "  cume_dist = (existing rows at-or-before 45, PLUS the candidate itself) / (existing rows + 1).\n"
        "  alpha: two existing <= 45 plus the candidate -> 3/5 = 0.6000. cume_dist is always a bit\n"
        "  larger because it counts the candidate. beta diverges the same way: 0.6000 vs 0.6667.\n"
        "These are NOT the window forms percent_rank() OVER (...) / cume_dist() OVER (...), which score\n"
        "rows that already exist; here the 45-minute ticket does not exist in the table."
    ),
    'sol_sql': (
        "SELECT team,\n"
        "       ROUND(percent_rank(45) WITHIN GROUP (ORDER BY resolution_minutes)::numeric, 4) AS hyp_percent_rank, -- (rank-1)/N\n"
        "       ROUND(cume_dist(45)    WITHIN GROUP (ORDER BY resolution_minutes)::numeric, 4) AS hyp_cume_dist     -- (rows<=v, +candidate)/(N+1)\n"
        "FROM support_tickets\n"
        "GROUP BY team\n"
        "ORDER BY team;"
    ),
}

# ---------------- templates (top of each leaf) ----------------
TMPL_RANK = '''<div id="rp-tmpl-hyp-rank" class="problem-card collapsed" style="margin: 0 0 10px 0;">
                      <div class="problem-card-header">
                        <h3 class="problem-card-title" style="margin: 0;">rank / dense_rank WITHIN GROUP (hypothetical rank per group)</h3>
                        <span class="problem-toggle">&#9660;</span>
                      </div>
                      <div class="problem-card-excerpt">
                        <p style="margin:0;">Use when: you have a candidate value and want the rank it WOULD get inside each group, without inserting a row. <code>rank</code> leaves gaps after ties; <code>dense_rank</code> does not.</p>
                      </div>
                      <div class="problem-card-content">
                        <p style="margin:0 0 6px;"><strong>What this template does, step by step:</strong></p>
                        <ol style="margin:0 0 10px 18px; line-height:1.7;">
                          <li>Pass the candidate value as the function argument: <code>rank(720)</code> / <code>dense_rank(720)</code>.</li>
                          <li><code>WITHIN GROUP (ORDER BY metric)</code> sorts each group's EXISTING rows; the candidate is slotted in without being inserted.</li>
                          <li><code>GROUP BY</code> the group column returns one rank per group (it is an aggregate, not a per-row window function).</li>
                          <li><code>rank</code> skips numbers after a tie; <code>dense_rank</code> keeps them consecutive. Neither needs a row for the candidate to exist.</li>
                        </ol>
                        <pre style="margin:0 0 6px; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>-- Where would the value 720 rank inside each region, without inserting it?
SELECT region,
       rank(720) WITHIN GROUP (ORDER BY credit_score)       AS hyp_rank,        -- gaps after ties
       dense_rank(720) WITHIN GROUP (ORDER BY credit_score) AS hyp_dense_rank   -- no gaps
FROM applications
GROUP BY region;</code></pre>
                      </div>
                    </div>'''

TMPL_FRAC = '''<div id="rp-tmpl-hyp-fraction" class="problem-card collapsed" style="margin: 0 0 10px 0;">
                      <div class="problem-card-header">
                        <h3 class="problem-card-title" style="margin: 0;">percent_rank / cume_dist WITHIN GROUP (hypothetical fraction per group)</h3>
                        <span class="problem-toggle">&#9660;</span>
                      </div>
                      <div class="problem-card-excerpt">
                        <p style="margin:0;">Use when: you want where a candidate value would stand inside each group as a fraction 0..1, without inserting a row. <code>percent_rank</code> = relative standing; <code>cume_dist</code> = cumulative share.</p>
                      </div>
                      <div class="problem-card-content">
                        <p style="margin:0 0 6px;"><strong>What this template does, step by step:</strong></p>
                        <ol style="margin:0 0 10px 18px; line-height:1.7;">
                          <li>Same hypothetical-set shape as rank, but the answer is a fraction from 0 to 1.</li>
                          <li><code>percent_rank</code> = (hypothetical rank - 1) / number of existing rows; it is 0 when the value would tie for first.</li>
                          <li><code>cume_dist</code> counts existing rows at-or-before the value PLUS the candidate itself, over (existing rows + 1); always a touch larger than percent_rank.</li>
                          <li>Wrap in <code>ROUND(...::numeric, d)</code> for a clean number; <code>GROUP BY</code> gives one row per group.</li>
                        </ol>
                        <pre style="margin:0 0 6px; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>-- Where would 45 stand inside each team, as a fraction, without inserting it?
SELECT team,
       ROUND(percent_rank(45) WITHIN GROUP (ORDER BY resolution_minutes)::numeric, 4) AS hyp_percent_rank, -- (rank-1)/N
       ROUND(cume_dist(45)    WITHIN GROUP (ORDER BY resolution_minutes)::numeric, 4) AS hyp_cume_dist     -- (rows<=v, +candidate)/(N+1)
FROM support_tickets
GROUP BY team;</code></pre>
                      </div>
                    </div>'''


def leaf(leaf_id, title, flavor, excerpt_tail, tmpl_html, card):
    code_label = ('<code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">'
                  'nb01 qtype: percentile_metrics (%s flavor)</code>' % flavor)
    body = build_card_indented(card)
    return ('''<div id="%(lid)s" class="problem-card collapsed qtype-group">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0;">%(title)s <span class="count-badge">1 problem</span></h3>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt">
                  <p style="margin: 0;">%(label)s &mdash; %(tail)s</p>
                </div>
                <div class="problem-card-content">
                    %(tmpl)s
                %(card)s
                </div>
              </div>''' % {
        'lid': leaf_id, 'title': title, 'label': code_label,
        'tail': excerpt_tail, 'tmpl': tmpl_html, 'card': body,
    })


def build_card_indented(card):
    raw = eb.build_card(card)
    # build_card emits with a 10-space base indent already; keep as-is.
    return raw


# ---------------- Postgres verification (pgserver) ----------------
def verify_pg(card):
    import pgserver, tempfile
    d = tempfile.mkdtemp()
    srv = pgserver.get_server(d)
    try:
        for inp in card['inputs']:
            coldefs = ', '.join('%s %s' % (n, t) for n, t in inp['cols'])
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], coldefs))
            colnames = ', '.join(n for n, _ in inp['cols'])
            for row in inp['rows']:
                vals = ', '.join(_lit(v) for v in row)
                srv.psql('INSERT INTO %s (%s) VALUES (%s);' % (inp['name'], colnames, vals))
        out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + card['sol_sql'])
        ncols = len(card['exp_headers'])
        got = [tuple(line.split('|')) for line in out.strip().splitlines()
               if line.count('|') == ncols - 1 and 'format is' not in line and 'separator is' not in line]
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


def find_leaf_end(text, leaf_id):
    """Return end index just past the balanced div that opens with id="leaf_id"."""
    start = text.find('<div id="%s"' % leaf_id)
    if start < 0:
        raise ValueError('leaf id not found: ' + leaf_id)
    pos, depth, end = start, 0, None
    tag = re.compile(r'<(/?)div\b', re.I)
    while True:
        m = tag.search(text, pos)
        if not m:
            break
        if m.group(1) == '':
            depth += 1
        else:
            depth -= 1
            if depth == 0:
                end = text.find('>', m.start()) + 1
                break
        pos = m.end()
    if end is None:
        raise ValueError('unbalanced div for leaf: ' + leaf_id)
    return start, end


def main():
    # 1. verify both cards against real Postgres
    for c in (CARD_RANK, CARD_FRAC):
        ok, got, exp = verify_pg(c)
        print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', c['title']))
        if not ok:
            print('   GOT:', got)
            print('   EXP:', exp)
            raise SystemExit('verification failed; nothing written')

    # 2. build the two leaves
    leaf_rank = leaf('rp-leaf-hyp-rank',
                     'rank / dense_rank WITHIN GROUP: hypothetical rank per group',
                     'hypothetical_rank',
                     "<code>rank(value) WITHIN GROUP (ORDER BY metric)</code> and <code>dense_rank(value) WITHIN GROUP (...)</code> return the rank a candidate value would get inside each group, no row inserted. Postgres only. Not the window <code>rank() OVER</code>.",
                     TMPL_RANK, CARD_RANK)
    leaf_frac = leaf('rp-leaf-hyp-fraction',
                     'percent_rank / cume_dist WITHIN GROUP: hypothetical fraction per group',
                     'hypothetical_fraction',
                     "<code>percent_rank(value) WITHIN GROUP (...)</code> and <code>cume_dist(value) WITHIN GROUP (...)</code> return where a candidate value would stand inside each group as a fraction 0..1, no row inserted. Postgres only.",
                     TMPL_FRAC, CARD_FRAC)

    text = open(PATH).read()
    before = eb.balance_report(text)
    # insert AFTER the existing rp-leaf-pct-agg leaf, as a sibling
    _, end = find_leaf_end(text, 'rp-leaf-pct-agg')
    insert = '\n\n              ' + leaf_rank + '\n\n              ' + leaf_frac + '\n'
    text = text[:end] + insert + text[end:]
    after = eb.balance_report(text)
    print('\nBalance before:', before)
    print('Balance after :', after)
    if (after['div_open'] != after['div_close']
            or after['details_open'] != after['details_close']
            or after['final_depth'] != 0 or after['min_depth'] < 0):
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('\nWROTE 2 leaves (rp-leaf-hyp-rank, rp-leaf-hyp-fraction) to', PATH)


if __name__ == '__main__':
    main()
