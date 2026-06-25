"""Restructure Matchup & Leaderboard into 4 scoring-scheme leaves (PIT-style), each a
qtype-group with a template + a Postgres-verified worked card. The soccer-points leaf
also carries a shared step-by-step walkthrough (unpivot -> score -> group). Replaces the
single ml-leaf-leaderboard leaf. Idempotent + balance-checked.
Run:  python3 build_ml_leaves.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

TEAMS = [['A'], ['B'], ['C'], ['D']]            # D never plays -> zero-fill
MATCHES = [[1, 'A', 'B', 2, 1], [2, 'B', 'C', 0, 0], [3, 'C', 'A', 3, 1], [4, 'A', 'B', 1, 1]]
SHOTS = [[1, 'A', 'B', 10, 5], [2, 'B', 'C', 8, 8], [3, 'C', 'A', 12, 6], [4, 'A', 'B', 7, 9]]
SIDES = ("SELECT home_team AS team, home_goals AS gf, away_goals AS ga FROM matches\n"
         "  UNION ALL\n"
         "  SELECT away_team, away_goals, home_goals FROM matches")

TEAMS_IN = {'name': 'teams', 'cols': [('team_name', 'TEXT')], 'headers': ['team_name'], 'rows': TEAMS}
MATCHES_IN = {'name': 'matches', 'cols': [('match_id', 'INT'), ('home_team', 'TEXT'), ('away_team', 'TEXT'), ('home_goals', 'INT'), ('away_goals', 'INT')],
              'headers': ['match_id', 'home_team', 'away_team', 'home_goals', 'away_goals'], 'rows': MATCHES}
SHOTS_IN = {'name': 'shot_log', 'cols': [('match_id', 'INT'), ('home_team', 'TEXT'), ('away_team', 'TEXT'), ('home_shots', 'INT'), ('away_shots', 'INT')],
            'headers': ['match_id', 'home_team', 'away_team', 'home_shots', 'away_shots'], 'rows': SHOTS}

PROMPT_COMMON = ["Each <code>matches</code> row holds BOTH teams of a game (home and away) and each side's goals. Team <code>D</code> is in <code>teams</code> but never played.",
                 "Split every match into its two sides (home and away), score each side, then total per team.",
                 "Every team in <code>teams</code> must appear, including ones that never played (zero-fill with a LEFT JOIN + COALESCE)."]

CARD_POINTS = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'League Table by Points (win 3, tie 1, loss 0)',
    'excerpt': "Each team's total league points: win = 3, tie = 1, loss = 0, with non-players zero-filled.",
    'prompt': PROMPT_COMMON + ["Scoring: a win is 3 points, a tie 1, a loss 0. Return <code>team</code>, <code>points</code>, ordered by points DESC then team."],
    'inputs': [TEAMS_IN, MATCHES_IN], 'exp_headers': ['team', 'points'],
    'exp_rows': [['A', 4], ['C', 4], ['B', 2], ['D', 0]],
    'sol_comment': ("Split each match into two sides (UNION ALL), score each side's own goals vs the opponent's with a\n"
                    "CASE (win 3 / tie 1 / loss 0), then GROUP BY team and SUM. Drive the final select off teams with a\n"
                    "LEFT JOIN so D (never played) survives, and COALESCE its points to 0.\n"
                    "A beats B and ties B, loses to C -> 3+1+0 = 4. C ties B, beats A -> 1+3 = 4. Verified."),
    'sol_sql': ("WITH sides AS (\n  %s\n),\n"
                "scored AS (\n  SELECT team, CASE WHEN gf > ga THEN 3 WHEN gf = ga THEN 1 ELSE 0 END AS pts FROM sides\n)\n"
                "SELECT t.team_name AS team, COALESCE(SUM(s.pts), 0) AS points\n"
                "FROM teams t\nLEFT JOIN scored s ON s.team = t.team_name\n"
                "GROUP BY t.team_name\nORDER BY points DESC, team;" % SIDES),
}
CARD_WINLOSS = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Win / Loss / Tie Record per Team',
    'excerpt': "Separate count columns: wins, losses, ties per team (not a single points total).",
    'prompt': PROMPT_COMMON + ["Return <code>team</code>, <code>wins</code>, <code>losses</code>, <code>ties</code> (each a count), ordered by team."],
    'inputs': [TEAMS_IN, MATCHES_IN], 'exp_headers': ['team', 'wins', 'losses', 'ties'],
    'exp_rows': [['A', 1, 1, 1], ['B', 0, 1, 2], ['C', 1, 0, 1], ['D', 0, 0, 0]],
    'sol_comment': ("Same UNION ALL split, but instead of points each outcome gets its OWN counting column via three\n"
                    "conditional sums. GROUP BY team; LEFT JOIN from teams so D shows 0/0/0. Note ties counts BOTH\n"
                    "sides of a drawn match, which is correct (each team earns a tie). Verified."),
    'sol_sql': ("WITH sides AS (\n  %s\n)\n"
                "SELECT t.team_name AS team,\n"
                "       COALESCE(SUM(CASE WHEN gf > ga THEN 1 ELSE 0 END), 0) AS wins,\n"
                "       COALESCE(SUM(CASE WHEN gf < ga THEN 1 ELSE 0 END), 0) AS losses,\n"
                "       COALESCE(SUM(CASE WHEN gf = ga THEN 1 ELSE 0 END), 0) AS ties\n"
                "FROM teams t\nLEFT JOIN sides s ON s.team = t.team_name\n"
                "GROUP BY t.team_name\nORDER BY team;" % SIDES),
}
CARD_GFGA = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Goals For / Against / Differential per Team',
    'excerpt': "Carry BOTH score columns through the split: goals scored, goals conceded, and the difference.",
    'prompt': PROMPT_COMMON + ["Return <code>team</code>, <code>goals_for</code>, <code>goals_against</code>, <code>goal_diff</code>, ordered by team."],
    'inputs': [TEAMS_IN, MATCHES_IN], 'exp_headers': ['team', 'goals_for', 'goals_against', 'goal_diff'],
    'exp_rows': [['A', 4, 5, -1], ['B', 2, 3, -1], ['C', 3, 1, 2], ['D', 0, 0, 0]],
    'sol_comment': ("No win/loss CASE here -- the lesson is carrying BOTH values through the split: each side branch\n"
                    "keeps its own goals (gf) AND the opponent's (ga). Then SUM(gf), SUM(ga), and their difference.\n"
                    "LEFT JOIN from teams zero-fills D. Verified."),
    'sol_sql': ("WITH sides AS (\n  %s\n)\n"
                "SELECT t.team_name AS team,\n"
                "       COALESCE(SUM(gf), 0) AS goals_for,\n"
                "       COALESCE(SUM(ga), 0) AS goals_against,\n"
                "       COALESCE(SUM(gf) - SUM(ga), 0) AS goal_diff\n"
                "FROM teams t\nLEFT JOIN sides s ON s.team = t.team_name\n"
                "GROUP BY t.team_name\nORDER BY team;" % SIDES),
}
CARD_SUMCOL = {
    'diff': 'Easy', 'color': '#2e7d32', 'title': 'Total Shots per Team (sum a column, no win/loss)',
    'excerpt': "Just the UNION ALL split, then sum one per-side stat. No scoring logic on top.",
    'prompt': ["Each <code>shot_log</code> row holds both teams of a game and each side's shot count. Team <code>D</code> never played.",
               "Total each team's shots across all games (home and away). No win/loss logic &mdash; just sum the one stat.",
               "Return <code>team</code>, <code>total_shots</code>, ordered by total_shots DESC then team. Zero-fill non-players."],
    'inputs': [TEAMS_IN, SHOTS_IN], 'exp_headers': ['team', 'total_shots'],
    'exp_rows': [['A', 23], ['B', 22], ['C', 20], ['D', 0]],
    'sol_comment': ("The simplest scheme: split the two sides with UNION ALL, then SUM one stat per team. No CASE, no\n"
                    "opponent comparison -- this isolates the matchup-unpivot move itself. LEFT JOIN zero-fills D. Verified."),
    'sol_sql': ("SELECT t.team_name AS team, COALESCE(SUM(s.shots), 0) AS total_shots\n"
                "FROM teams t\nLEFT JOIN (\n"
                "  SELECT home_team AS team, home_shots AS shots FROM shot_log\n"
                "  UNION ALL\n"
                "  SELECT away_team, away_shots FROM shot_log\n"
                ") s ON s.team = t.team_name\n"
                "GROUP BY t.team_name\nORDER BY total_shots DESC, team;"),
}


def tmpl(tid, title, use_when, steps, code):
    lis = ''.join('\n                          <li>%s</li>' % s for s in steps)
    return ('''<div id="%s" class="problem-card collapsed" style="margin: 0 0 10px 0;">
                      <div class="problem-card-header"><h3 class="problem-card-title" style="margin: 0;">%s</h3><span class="problem-toggle">&#9660;</span></div>
                      <div class="problem-card-excerpt"><p style="margin:0;">%s</p></div>
                      <div class="problem-card-content">
                        <p style="margin:0 0 6px;"><strong>What this template does, step by step:</strong></p>
                        <ol style="margin:0 0 10px 18px; line-height:1.7;">%s
                        </ol>
                        <pre style="margin:0 0 6px; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>%s</code></pre>
                      </div>
                    </div>''' % (tid, title, use_when, lis, code))


SHARED_STEPS = ["<strong>Split the two sides</strong> with <code>UNION ALL</code>: one branch per side, each carrying its own value and the opponent's.",
                "<strong>Score each side</strong> &mdash; this is the ONLY step that changes between schemes (points CASE, win/loss counts, goals for/against, or just a sum).",
                "<strong>Group per team</strong> and aggregate.",
                "<strong>Zero-fill</strong>: drive off the dimension table with a LEFT JOIN and COALESCE so teams that never played still appear."]

T_POINTS = tmpl('ml-tmpl-points', 'Soccer points (win 3, tie 1, loss 0)',
                'Use when: the leaderboard column is a single league-points total.',
                SHARED_STEPS,
                "WITH sides AS (\n  SELECT home_team AS team, home_goals AS gf, away_goals AS ga FROM matches\n  UNION ALL\n  SELECT away_team, away_goals, home_goals FROM matches\n)\nSELECT t.team_name AS team,\n       COALESCE(SUM(CASE WHEN gf>ga THEN 3 WHEN gf=ga THEN 1 ELSE 0 END),0) AS points\nFROM teams t LEFT JOIN sides s ON s.team=t.team_name\nGROUP BY t.team_name ORDER BY points DESC, team;")
T_WINLOSS = tmpl('ml-tmpl-winloss2', 'Win / loss / tie record (separate counts)',
                 'Use when: the output has separate wins, losses, ties columns &mdash; not one total.',
                 SHARED_STEPS,
                 "-- after the same sides CTE:\nSELECT t.team_name AS team,\n       COALESCE(SUM(CASE WHEN gf>ga THEN 1 ELSE 0 END),0) AS wins,\n       COALESCE(SUM(CASE WHEN gf<ga THEN 1 ELSE 0 END),0) AS losses,\n       COALESCE(SUM(CASE WHEN gf=ga THEN 1 ELSE 0 END),0) AS ties\nFROM teams t LEFT JOIN sides s ON s.team=t.team_name\nGROUP BY t.team_name ORDER BY team;")
T_GFGA = tmpl('ml-tmpl-gfga2', 'Goals for / against / differential',
              'Use when: the output sums each side\'s own value AND the opponent\'s.',
              SHARED_STEPS,
              "-- after the same sides CTE (each branch carries gf AND ga):\nSELECT t.team_name AS team,\n       COALESCE(SUM(gf),0) AS goals_for,\n       COALESCE(SUM(ga),0) AS goals_against,\n       COALESCE(SUM(gf)-SUM(ga),0) AS goal_diff\nFROM teams t LEFT JOIN sides s ON s.team=t.team_name\nGROUP BY t.team_name ORDER BY goal_diff DESC, team;")
T_SUMCOL = tmpl('ml-tmpl-sumcol2', 'Sum a column per side (no win/loss logic)',
                'Use when: you just total one per-side stat &mdash; no scoring, no opponent comparison.',
                SHARED_STEPS,
                "SELECT t.team_name AS team, COALESCE(SUM(s.stat),0) AS total\nFROM teams t LEFT JOIN (\n  SELECT home_team AS team, home_stat AS stat FROM games\n  UNION ALL\n  SELECT away_team, away_stat FROM games\n) s ON s.team=t.team_name\nGROUP BY t.team_name ORDER BY total DESC, team;")


def leaf(lid, title, flavor, tail, tmpl_html, card, extra=''):
    label = '<code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">nb01 qtype: matchup_unpivot (%s flavor)</code>' % flavor
    return ('''<div id="%(lid)s" class="problem-card collapsed qtype-group">
                <div class="problem-card-header"><h3 class="problem-card-title" style="margin: 0;">%(title)s <span class="count-badge">1 problem</span></h3><span class="problem-toggle">&#9660;</span></div>
                <div class="problem-card-excerpt"><p style="margin: 0;">%(label)s &mdash; %(tail)s</p></div>
                <div class="problem-card-content">
                    %(tmpl)s
              %(card)s%(extra)s
                </div>
              </div>''' % {'lid': lid, 'title': title, 'label': label, 'tail': tail, 'tmpl': tmpl_html, 'card': eb.build_card(card), 'extra': extra})


def accordion_step(title, excerpt, inner, mtop=12, border='#1565c0', cid=None):
    idattr = (' id="%s"' % cid) if cid else ''
    return ('<div%s class="problem-card collapsed" style="margin: %spx 0 0; border-left:4px solid %s;">'
            '<div class="problem-card-header"><h3 class="problem-card-title" style="margin:0; font-size:1.15rem;">%s</h3><span class="problem-toggle">&#9660;</span></div>'
            '<div class="problem-card-excerpt"><p style="margin:0;">%s</p></div>'
            '<div class="problem-card-content">%s</div></div>' % (idattr, mtop, border, title, excerpt, inner))


def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in card['inputs']:
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], ', '.join('%s %s' % (n, t) for n, t in inp['cols'])))
            for row in inp['rows']:
                srv.psql('INSERT INTO %s VALUES (%s);' % (inp['name'], ', '.join(_lit(v) for v in row)))
        out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + card['sol_sql'])
        ncols = len(card['exp_headers'])
        got = [tuple(l.split('|')) for l in out.strip().splitlines() if l.count('|') == ncols - 1 and 'format is' not in l and 'separator is' not in l]
        exp = [tuple(str(x) for x in r) for r in card['exp_rows']]
        return got == exp, got, exp
    finally:
        srv.cleanup()


def _lit(v):
    s = str(v)
    return s if re.match(r'^-?\d+$', s) else "'" + s.replace("'", "''") + "'"


def build_walkthrough():
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in (TEAMS_IN, MATCHES_IN):
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], ', '.join('%s %s' % (n, t) for n, t in inp['cols'])))
            for row in inp['rows']:
                srv.psql('INSERT INTO %s VALUES (%s);' % (inp['name'], ', '.join(_lit(v) for v in row)))
        def rows(q, nc):
            out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + q)
            return [[None if c == '' else c for c in l.split('|')] for l in out.strip().splitlines() if l.count('|') == nc - 1 and 'format is' not in l and 'separator is' not in l]
        t_sides = rows("SELECT home_team AS team, home_goals AS gf, away_goals AS ga FROM matches UNION ALL SELECT away_team, away_goals, home_goals FROM matches ORDER BY team", 3)
        t_scored = rows("SELECT team, gf, ga, CASE WHEN gf>ga THEN 3 WHEN gf=ga THEN 1 ELSE 0 END AS pts FROM (SELECT home_team AS team, home_goals AS gf, away_goals AS ga FROM matches UNION ALL SELECT away_team, away_goals, home_goals FROM matches) z ORDER BY team", 4)
        t_final = rows("WITH sides AS (SELECT home_team AS team, home_goals AS gf, away_goals AS ga FROM matches UNION ALL SELECT away_team, away_goals, home_goals FROM matches), scored AS (SELECT team, CASE WHEN gf>ga THEN 3 WHEN gf=ga THEN 1 ELSE 0 END AS pts FROM sides) SELECT t.team_name AS team, COALESCE(SUM(s.pts),0) AS points FROM teams t LEFT JOIN scored s ON s.team=t.team_name GROUP BY t.team_name ORDER BY points DESC, team", 2)
    finally:
        srv.cleanup()
    DT = eb.data_table
    intro = ('<p style="margin:0 0 8px;">Same four matches, scored as league points. The flow is the same for every scheme &mdash; only Step 2 changes. Team D is in <code>teams</code> but never played.</p>'
             '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>matches</code></strong> (each row is one game, both teams):</p>' + DT(MATCHES_IN['headers'], MATCHES))
    s1 = accordion_step('Step 1 &mdash; split the two sides (UNION ALL)', 'Each match becomes two rows: a team, its goals, the opponent\'s goals.',
                        '<p style="margin:0 0 6px;">4 matches &rarr; 8 side-rows. Now every game is seen from each team\'s point of view:</p>' + DT(['team', 'gf', 'ga'], t_sides))
    s2 = accordion_step('Step 2 &mdash; score each side (THIS is the step that varies)', 'Soccer points: win 3, tie 1, loss 0.',
                        '<p style="margin:0 0 6px;">A CASE turns own-vs-opponent into points. Swap this step for counts / goals-for-against / a plain sum to get the other schemes:</p>' + DT(['team', 'gf', 'ga', 'pts'], t_scored), border='#2e7d32')
    s3 = accordion_step('Step 3 &mdash; group per team and zero-fill', 'GROUP BY team, SUM the points; LEFT JOIN from teams so D appears at 0.',
                        '<p style="margin:0 0 6px;">A and C both reach 4; D never played so COALESCE gives it 0:</p>' + DT(['team', 'points'], t_final))
    return accordion_step('&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
                          'Unpivot &rarr; score &rarr; group, step by step. Only the scoring step differs between the four leaves.',
                          intro + s1 + s2 + s3, mtop=14, border='#6a1b9a', cid='ml-walk')


def balance(t):
    do = len(re.findall(r'<div\b', t)); dc = len(re.findall(r'</div\b', t))
    deto = len(re.findall(r'<details\b', t)); detc = len(re.findall(r'</details\b', t))
    d = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', t):
        d += 1 if m.group(1) == '' else -1; mn = min(mn, d)
    return do, dc, deto, detc, d, mn


def main():
    for c in (CARD_POINTS, CARD_WINLOSS, CARD_GFGA, CARD_SUMCOL):
        ok, got, exp = verify_pg(c)
        print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', c['title']))
        if not ok:
            print('  GOT', got); print('  EXP', exp); raise SystemExit('verify failed')
    text = open(PATH).read()
    if 'id="ml-leaf-points"' in text:
        print('already present; nothing to do.'); return
    before = balance(text)
    walk = build_walkthrough()
    leaves = (
        leaf('ml-leaf-points', 'League table by points (win 3, tie 1, loss 0)', 'soccer_points',
             'the leaderboard column is a single points total. Win 3, tie 1, loss 0, summed per team, non-players zero-filled.', T_POINTS, CARD_POINTS, extra='\n              ' + walk) + '\n\n              ' +
        leaf('ml-leaf-winloss', 'Win / loss / tie record', 'win_loss',
             'separate wins / losses / ties count columns per team, not a single total.', T_WINLOSS, CARD_WINLOSS) + '\n\n              ' +
        leaf('ml-leaf-gfga', 'Goals for / against / differential', 'goals_for_against',
             'sum each side\'s own goals AND the opponent\'s, then the difference.', T_GFGA, CARD_GFGA) + '\n\n              ' +
        leaf('ml-leaf-sumcol', 'Sum a column per side (no win/loss logic)', 'sum_column',
             'just total one per-side stat after the split &mdash; the bare matchup-unpivot move.', T_SUMCOL, CARD_SUMCOL)
    )
    # replace the whole ml-leaf-leaderboard leaf
    s = text.find('<div id="ml-leaf-leaderboard"')
    depth = 0; e = None
    for m in re.finditer(r'<(/?)div\b', text[s:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            e = text.find('>', s + m.start()) + 1; break
    if e is None:
        raise SystemExit('could not balance ml-leaf-leaderboard')
    text = text[:s] + leaves + text[e:]
    text = text.replace('Matchup &amp; Leaderboard <span class="count-badge">1 problem</span>',
                        'Matchup &amp; Leaderboard <span class="count-badge">4 problems</span>', 1)
    after = balance(text)
    print('before:', before); print('after :', after)
    do, dc, deto, detc, d, mn = after
    if do != dc or deto != detc or d != 0 or mn < 0:
        raise SystemExit('balance failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE 4 matchup leaves (+ walkthrough), replaced ml-leaf-leaderboard')


if __name__ == '__main__':
    main()
