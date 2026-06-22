"""Reusable two-container (Problem + Solution) card builder + DuckDB verifier
for the recipe-card refactor of sql_problem_patterns.html.

A card dict looks like:
{
  'diff': 'Medium', 'color': '#e65100',
  'title': 'Card Title',
  'excerpt': 'one-line outer-card excerpt',
  'prompt': ['bullet 1', 'bullet 2', ...],
  'inputs': [
     {'name':'matches', 'cols':[('match_id','INTEGER'),...],
      'headers':['match_id',...], 'rows':[[...],[...]]},
     ...
  ],
  'exp_headers': ['match_id', 'earliest_message_time'],
  'exp_rows': [[1,'10:03'], ...],
  'sol_comment': 'free text explaining the key lines (no /* */)',
  'sol_sql': 'SELECT ... -- inline comments',
  # optional: 'verify_sql' if the runnable SQL differs from the displayed SQL
  # optional: 'check_sql'  a trailing SELECT to run after a DELETE/UPDATE
  'anchor': 'unique substring of the OLD card title used to locate it',
}
"""
import re, html as _html
import duckdb

# ---------- display helpers ----------
def esc(s):
    return _html.escape(s, quote=False)

_NUMRE = re.compile(r'^-?\d+(\.\d+)?$')

def _to_cell(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    return str(v)

def schema_table(cols):
    head = ('<table style="border-collapse:collapse; font-size:1.2rem; margin:0 0 16px;">'
            '<thead><tr style="border-bottom:2px solid #cbd5e1;">'
            '<th style="text-align:left; padding:5px 28px 5px 0;">Column</th>'
            '<th style="text-align:left; padding:5px 0;">Type</th></tr></thead><tbody>')
    body = ''
    for i,(name,typ) in enumerate(cols):
        zebra = ' background:#f7f9fb;' if i % 2 == 1 else ''
        body += ('<tr style="border-bottom:1px solid #eef2f7;%s">'
                 '<td style="padding:5px 28px 5px 0;"><code>%s</code></td>'
                 '<td style="padding:5px 0;">%s</td></tr>' % (zebra, esc(name), esc(typ)))
    return head + body + '</tbody></table>'

def data_table(headers, rows):
    th = ''.join('<th style="padding:5px 18px 5px 0; text-align:left;">%s</th>' % esc(str(h)) for h in headers)
    head = ('<table style="border-collapse:collapse; font-size:1.2rem; margin:0 0 16px;">'
            '<thead><tr style="border-bottom:2px solid #cbd5e1;">' + th + '</tr></thead><tbody>')
    body = ''
    for i,row in enumerate(rows):
        zebra = ' background:#f7f9fb;' if i % 2 == 1 else ''
        tds = ''.join('<td style="padding:5px 18px 5px 0;">%s</td>' % esc(_to_cell(c)) for c in row)
        body += '<tr style="border-bottom:1px solid #eef2f7;%s">%s</tr>' % (zebra, tds)
    return head + body + '</tbody></table>'

# ---------- card HTML ----------
def build_card(c):
    inputs_html = ''
    for inp in c['inputs']:
        inputs_html += ('\n                  <p style="margin:0 0 6px;"><strong>Schema &mdash; <code>%s</code></strong></p>\n\n                  %s\n'
                        % (esc(inp['name']), schema_table(inp['cols'])))
    for inp in c['inputs']:
        inputs_html += ('\n                  <p style="margin:0 0 6px;"><strong>Example input &mdash; <code>%s</code></strong></p>\n\n                  %s\n'
                        % (esc(inp['name']), data_table(inp['headers'], inp['rows'])))
    prompt_li = ''.join('\n                        <li>%s</li>' % p for p in c['prompt'])
    exp_tbl = data_table(c['exp_headers'], c['exp_rows'])

    code = '/*\n' + c['sol_comment'].rstrip() + '\n*/\n\n' + c['sol_sql'].strip()

    return '''<div class="problem-card collapsed" style="margin: 0 0 16px 0;">
            <div class="problem-card-header">
              <h3 class="problem-card-title" style="margin: 0; display: flex; align-items: center; gap: 15px;">
                <span style="display: inline-block; background-color: %(color)s; color: white; padding: 4px 10px; border-radius: 3px; font-size: 1.328rem; font-weight: 600;">%(diff)s</span>
                %(title)s
              </h3>
              <span class="problem-toggle">&#9660;</span>
            </div>
            <div class="problem-card-excerpt">
              <p style="margin:0;">%(excerpt)s</p>
            </div>
            <div class="problem-card-content">

              <!-- PROBLEM (case study + test data) -->
              <div class="problem-card collapsed" style="margin: 0 0 12px 0;">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0; display: flex; align-items: center; gap: 15px;">
                    <span style="display: inline-block; background-color: #2c5f8a; color: white; padding: 4px 10px; border-radius: 3px; font-size: 1.328rem; font-weight: 600;">Problem</span>
                    Case study &amp; test data
                  </h3>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt"><p style="margin:0;">The prompt, schema, example input, and expected output &mdash; the same view you get in the practice notebook.</p></div>
                <div class="problem-card-content">
                  <p style="margin:0 0 6px;"><strong>Prompt</strong></p>
                  <ul style="margin:0 0 16px 18px; line-height:1.7;">%(prompt_li)s
                  </ul>
%(inputs_html)s
                  <p style="margin:0 0 6px;"><strong>Expected output</strong></p>
                  %(exp_tbl)s
                </div>
              </div>

              <!-- SOLUTION (annotated) -->
              <div class="problem-card collapsed" style="margin: 0;">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin: 0; display: flex; align-items: center; gap: 15px;">
                    <span style="display: inline-block; background-color: #2e7d32; color: white; padding: 4px 10px; border-radius: 3px; font-size: 1.328rem; font-weight: 600;">Solution</span>
                    Annotated SQL
                  </h3>
                  <button class="tpl-copy" type="button" onclick="event.stopPropagation(); copyTplCode(this);">Copy</button>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt"><p style="margin:0;">The query with inline comments on the lines that do the work.</p></div>
                <div class="problem-card-content">
                  <pre style="margin:0 0 10px; background:#1e1e1e; color:#d4d4d4; padding:12px 14px; border-radius:4px; font-size:1.2rem; line-height:1.55; white-space:pre-wrap;"><code>%(code)s</code></pre>
                </div>
              </div>

            </div>
          </div>''' % {
        'color': c['color'], 'diff': esc(c['diff']), 'title': esc(c['title']),
        'excerpt': c['excerpt'], 'prompt_li': prompt_li, 'inputs_html': inputs_html,
        'exp_tbl': exp_tbl, 'code': esc(code),
    }

# ---------- DuckDB verification ----------
def _lit(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'TRUE' if v else 'FALSE'
    if isinstance(v, (int, float)):
        return repr(v)
    s = str(v)
    if _NUMRE.match(s):
        return s
    return "'" + s.replace("'", "''") + "'"

def _norm(v):
    if v is None:
        return 'NULL'
    if isinstance(v, bool):
        return 'true' if v else 'false'
    s = str(v)
    if _NUMRE.match(s):
        f = float(s)
        if f == int(f):
            return str(int(f))
        return ('%.6f' % f).rstrip('0').rstrip('.')
    return s.strip()

def verify(c):
    con = duckdb.connect()
    for inp in c['inputs']:
        coldefs = ', '.join('%s %s' % (n, t) for n, t in inp['cols'])
        con.execute('CREATE TABLE %s (%s);' % (inp['name'], coldefs))
        colnames = ', '.join(n for n, _ in inp['cols'])
        for row in inp['rows']:
            vals = ', '.join(_lit(v) for v in row)
            con.execute('INSERT INTO %s (%s) VALUES (%s);' % (inp['name'], colnames, vals))
    run_sql = c.get('verify_sql', c['sol_sql'])
    con.execute(run_sql)
    if 'check_sql' in c:
        got = con.execute(c['check_sql']).fetchall()
    else:
        got = con.cursor().execute(run_sql).fetchall()
    con.close()
    got_n = [tuple(_norm(x) for x in r) for r in got]
    exp_n = [tuple(_norm(x) for x in r) for r in c['exp_rows']]
    ok = got_n == exp_n
    return ok, got_n, exp_n

# ---------- splice ----------
def find_block(text, search):
    """Locate the <div class="problem-card collapsed"...> that contains `search`
    in its header title, and return (start, end) covering the balanced div."""
    idx = text.find(search)
    if idx < 0:
        raise ValueError('anchor not found: %r' % search)
    # back up to the nearest enclosing '<div class="problem-card collapsed"'
    start = text.rfind('<div class="problem-card collapsed"', 0, idx)
    if start < 0:
        raise ValueError('no enclosing problem-card for: %r' % search)
    # walk div balance from start
    pos = start
    depth = 0
    tag = re.compile(r'<(/?)div\b', re.I)
    end = None
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
        raise ValueError('unbalanced div for: %r' % search)
    return start, end

def balance_report(text):
    d_open = len(re.findall(r'<div\b', text))
    d_close = len(re.findall(r'</div\b', text))
    det_open = len(re.findall(r'<details\b', text))
    det_close = len(re.findall(r'</details\b', text))
    # depth walk
    depth = 0; mind = 0
    for m in re.finditer(r'<(/?)div\b', text):
        depth += 1 if m.group(1) == '' else -1
        mind = min(mind, depth)
    return {'div_open': d_open, 'div_close': d_close, 'details_open': det_open,
            'details_close': det_close, 'final_depth': depth, 'min_depth': mind}

def run(CARDS, path):
    """Verify every card, then splice each into the file. Aborts on any failure."""
    # 1. verify all
    for c in CARDS:
        ok, got, exp = verify(c)
        status = 'OK ' if ok else 'FAIL'
        print('[verify %s] %s' % (status, c['title']))
        if not ok:
            print('   GOT:', got)
            print('   EXP:', exp)
            raise SystemExit('verification failed; nothing written')
    # 2. splice all
    text = open(path).read()
    before = balance_report(text)
    for c in CARDS:
        s, e = find_block(text, c['anchor'])
        new = build_card(c)
        text = text[:s] + new + text[e:]
    after = balance_report(text)
    print('\nBalance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(path, 'w').write(text)
    print('\nWROTE %d cards to %s' % (len(CARDS), path))
