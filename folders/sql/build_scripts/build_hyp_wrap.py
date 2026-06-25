"""Wrap the two hypothetical-set leaves (rp-leaf-hyp-rank, rp-leaf-hyp-fraction)
in a single nested parent container rp-grp-hyp under Rank & Percentile, with a
recipe overview and an explicit note on where future cards go. Idempotent: does
nothing if rp-grp-hyp already exists. Balance-checked.

Run:  python3 build_hyp_wrap.py
"""
import re, os

HERE = os.path.dirname(os.path.abspath(__file__))
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

PARENT_OPEN = '''<div id="rp-grp-hyp" class="problem-card collapsed qtype-group">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0;">Hypothetical-set aggregates: where a value WOULD rank (<code>WITHIN GROUP</code>) <span class="count-badge">2 recipes</span></h3>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt">
                  <p style="margin: 0;"><code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">nb01 qtype: percentile_metrics (hypothetical_rank / hypothetical_fraction flavors)</code> &mdash; Postgres only. These answer "where would a value that is NOT in the table land inside each group?" without inserting a row.</p>
                </div>
                <div class="problem-card-content">
                  <p style="margin:0 0 10px; line-height:1.7;">Both recipes share one shape: the candidate value is the function argument, <code>WITHIN GROUP (ORDER BY metric)</code> sorts each group's EXISTING rows, and <code>GROUP BY</code> returns one answer per group &mdash; no row is ever inserted. This is different from the window forms (<code>rank() OVER</code>, <code>percent_rank() OVER</code>), which score rows that already exist. Pick the <strong>integer-rank</strong> recipe when you want a position (4th, 3rd), or the <strong>fraction</strong> recipe when you want a 0&ndash;1 standing. As you generate and solve more of these, drop each new worked card into the matching leaf below.</p>
'''

PARENT_CLOSE = '''
                </div>
              </div>'''


def find_leaf_span(text, leaf_id):
    start = text.find('<div id="%s"' % leaf_id)
    if start < 0:
        raise ValueError('leaf id not found: ' + leaf_id)
    pos, depth, end = start, 0, None
    tag = re.compile(r'<(/?)div\b', re.I)
    while True:
        m = tag.search(text, pos)
        if not m:
            break
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            end = text.find('>', m.start()) + 1
            break
        pos = m.end()
    if end is None:
        raise ValueError('unbalanced div for: ' + leaf_id)
    return start, end


def balance(text):
    do = len(re.findall(r'<div\b', text)); dc = len(re.findall(r'</div\b', text))
    det_o = len(re.findall(r'<details\b', text)); det_c = len(re.findall(r'</details\b', text))
    depth = 0; mn = 0
    for m in re.finditer(r'<(/?)div\b', text):
        depth += 1 if m.group(1) == '' else -1; mn = min(mn, depth)
    return do, dc, det_o, det_c, depth, mn


def main():
    text = open(PATH).read()
    if 'id="rp-grp-hyp"' in text:
        print('rp-grp-hyp already present; nothing to do.')
        return
    before = balance(text)
    s1, _ = find_leaf_span(text, 'rp-leaf-hyp-rank')
    _, e2 = find_leaf_span(text, 'rp-leaf-hyp-fraction')
    inner = text[s1:e2]  # the two leaf blocks (+ whitespace between them)
    wrapped = PARENT_OPEN + '                  ' + inner + PARENT_CLOSE
    text = text[:s1] + wrapped + text[e2:]
    after = balance(text)
    print('before:', before)
    print('after :', after)
    do, dc, det_o, det_c, depth, mn = after
    if do != dc or det_o != det_c or depth != 0 or mn < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE rp-grp-hyp wrapper to', PATH)


if __name__ == '__main__':
    main()
