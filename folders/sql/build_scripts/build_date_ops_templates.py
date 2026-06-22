import sys, re
sys.path.insert(0,'/sessions/intelligent-quirky-volta/mnt/outputs')
from eabuild import esc, balance_report
from itree_content import CODE
PATH='/sessions/intelligent-quirky-volta/mnt/sql/sql_problem_patterns.html'

def tpl_card(subtitle, sql, excerpt='The generic shape with placeholder names &mdash; swap in your tables and columns.'):
    return ('<div class="problem-card collapsed" style="margin:0 0 12px 0;">\n'
            '                <div class="problem-card-header">\n'
            '                  <h3 class="problem-card-title" style="margin:0; display:flex; align-items:center; gap:15px;">\n'
            '                    <span style="display:inline-block; background-color:#6a1b9a; color:white; padding:4px 10px; border-radius:3px; font-size:1.328rem; font-weight:600;">Template</span>\n'
            '                    %s\n'
            '                  </h3>\n'
            '                  <button class="tpl-copy" type="button" onclick="event.stopPropagation(); copyTplCode(this);">Copy</button>\n'
            '                  <span class="problem-toggle">&#9660;</span>\n'
            '                </div>\n'
            '                <div class="problem-card-excerpt"><p style="margin:0;">%s</p></div>\n'
            '                <div class="problem-card-content">\n'
            '                  <pre style="margin:0 0 10px; background:#1e1e1e; color:#d4d4d4; padding:12px 14px; border-radius:4px; font-size:1.2rem; line-height:1.55; white-space:pre-wrap;"><code>%s</code></pre>\n'
            '                </div>\n'
            '              </div>\n') % (subtitle, excerpt, esc(sql))

def field_card(sig, ret, sql):
    return ('<div class="problem-card collapsed" style="margin:0 0 8px 0;">\n'
            '                  <div class="problem-card-header">\n'
            '                    <h3 class="problem-card-title" style="margin:0; font-family:ui-monospace,Menlo,monospace; font-size:1.18rem;">%s</h3>\n'
            '                    <span class="problem-toggle">&#9660;</span>\n'
            '                  </div>\n'
            '                  <div class="problem-card-excerpt"><p style="margin:0;">%s</p></div>\n'
            '                  <div class="problem-card-content">\n'
            '                    <pre style="margin:0; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.12rem; line-height:1.5; white-space:pre-wrap;"><code>%s</code></pre>\n'
            '                  </div>\n'
            '                </div>\n') % (esc(sig), esc(ret), esc(sql))

# EXTRACT field reference (the accordion)
FIELDS=[
 ('EXTRACT(YEAR FROM d)','Calendar year, e.g. 2024',"SELECT EXTRACT(YEAR FROM d)::int AS yr, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(QUARTER FROM d)','Quarter 1-4',"SELECT EXTRACT(QUARTER FROM d)::int AS q, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(MONTH FROM d)','Month NUMBER 1-12 (for a month BUCKET use DATE_TRUNC)',"SELECT EXTRACT(MONTH FROM d)::int AS mon, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(WEEK FROM d)','ISO week of year 1-53',"SELECT EXTRACT(WEEK FROM d)::int AS wk, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(DAY FROM d)','Day of the MONTH 1-31',"SELECT EXTRACT(DAY FROM d)::int AS dom, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(DOW FROM d)','Day of WEEK 0=Sun .. 6=Sat',"SELECT EXTRACT(DOW FROM d)::int AS dow, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(DOY FROM d)','Day of YEAR 1-366',"SELECT EXTRACT(DOY FROM d)::int AS doy, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(HOUR FROM ts)','Hour of day 0-23 (needs a TIMESTAMP)',"SELECT EXTRACT(HOUR FROM ts)::int AS hr, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(MINUTE FROM ts)','Minute 0-59',"SELECT EXTRACT(MINUTE FROM ts)::int AS mn, COUNT(*)\nFROM tbl GROUP BY 1 ORDER BY 1;"),
 ('EXTRACT(SECOND FROM ts)','Second 0-59',"SELECT EXTRACT(SECOND FROM ts)::int AS sec\nFROM tbl;"),
 ('EXTRACT(EPOCH FROM ts)','Seconds since 1970 — subtract two to get a DURATION',"-- raw epoch seconds of one timestamp:\nSELECT EXTRACT(EPOCH FROM ts) AS epoch_secs FROM tbl;\n-- duration between two (see the Duration leaf):\nSELECT EXTRACT(EPOCH FROM (b_ts - a_ts)) / 3600 AS hours FROM tbl;"),
]

def accordion():
    items=''.join(field_card(s,r,q) for s,r,q in FIELDS)
    return ('<div class="problem-card collapsed" style="margin:0 0 12px 0;">\n'
            '                <div class="problem-card-header">\n'
            '                  <h3 class="problem-card-title" style="margin:0; display:flex; align-items:center; gap:15px;">\n'
            '                    <span style="display:inline-block; background-color:#0d47a1; color:white; padding:4px 10px; border-radius:3px; font-size:1.328rem; font-weight:600;">Reference</span>\n'
            '                    EXTRACT field cheatsheet — tap a part to see its template\n'
            '                  </h3>\n'
            '                  <span class="problem-toggle">&#9660;</span>\n'
            '                </div>\n'
            '                <div class="problem-card-excerpt"><p style="margin:0;">Each row expands to a copy-ready snippet for that date part (year, month, week, day, weekday, hour, seconds/epoch).</p></div>\n'
            '                <div class="problem-card-content">\n'
            '                  <div class="do-acc">\n'
            '                    <button type="button" onclick="event.stopPropagation(); collapseAllInBox(this);" style="background:#0969da; color:white; padding:4px 12px; border:none; border-radius:4px; cursor:pointer; font-size:1.05rem; margin-bottom:10px;">Collapse all</button>\n'
            '                    %s\n'
            '                  </div>\n'
            '                </div>\n'
            '              </div>\n') % items

REL_SQL=("-- \"happened more than N days before\" WITHOUT CURRENT_DATE.\n"
 "-- Anchor to the latest date in the data (or a literal), then subtract N.\n"
 "WITH ref AS (SELECT MAX(event_date) AS anchor FROM events)\n"
 "SELECT e.*\n"
 "FROM events e CROSS JOIN ref\n"
 "WHERE e.event_date <  ref.anchor - 90      -- older than 90 days\n"
 "  -- e.event_date >= ref.anchor - 90       -- within the LAST 90 days\n"
 "  -- e.event_date <  DATE '2024-01-01'     -- or a fixed literal cutoff\n"
 ";\n"
 "-- Same test inside a JOIN ON when the date lives on the JOINED table:\n"
 "--   LEFT JOIN events e ON e.user_id = u.id AND e.event_date >= ref.anchor - 90")

INSERTS={
 'do-leaf-trunc':     tpl_card('DATE_TRUNC cohort bucket', CODE['do-leaf-trunc']),
 'do-leaf-extract':   tpl_card('EXTRACT a component', CODE['do-leaf-extract']) + '                            ' + accordion(),
 'do-leaf-arithmetic':(tpl_card('Date arithmetic', CODE['do-leaf-arithmetic'])
                       + '                            '
                       + tpl_card("&ldquo;Before / within N days&rdquo; cutoff (WHERE or ON)", REL_SQL,
                                  excerpt='The pattern for &ldquo;event older than N days&rdquo; without CURRENT_DATE &mdash; anchor to a literal or the data&rsquo;s MAX date, then subtract.')),
 'do-leaf-duration':  tpl_card('Duration via EXTRACT EPOCH', CODE['do-leaf-duration']),
 'do-leaf-daycount':  tpl_card('Inclusive day count', CODE['do-leaf-daycount']),
}

text=open(PATH).read()
before=balance_report(text)
for leaf_id, block in INSERTS.items():
    i=text.find('id="%s"'%leaf_id); assert i>0, leaf_id
    co=text.find('<div class="problem-card-content">', i); co_end=co+len('<div class="problem-card-content">')
    text=text[:co_end]+'\n\n                            '+block+text[co_end:]

# add collapseAllInBox JS right after collapseAllInTab
anchor='      btn.textContent = anyOpen ? \'Expand all\' : \'Collapse all\';\n    }\n'
js_new=anchor+('\n    function collapseAllInBox(btn){\n'
 '      var box = btn.closest(\'.do-acc\'); if(!box) return;\n'
 '      var cards = box.querySelectorAll(\'.problem-card\');\n'
 '      var anyOpen = Array.prototype.some.call(cards, function(c){ return !c.classList.contains(\'collapsed\'); });\n'
 '      cards.forEach(function(c){ if(anyOpen){ c.classList.add(\'collapsed\'); } else { c.classList.remove(\'collapsed\'); } });\n'
 '      btn.textContent = anyOpen ? \'Expand all\' : \'Collapse all\';\n'
 '    }\n')
assert text.count(anchor)==1, ('anchor count', text.count(anchor))
text=text.replace(anchor, js_new, 1)

after=balance_report(text)
print('before',before); print('after ',after)
assert after['div_open']==after['div_close'] and after['final_depth']==0 and after['min_depth']>=0
assert text.count('<svg')==text.count('</svg>')
assert text.count('function collapseAllInBox')==1
open(PATH,'w').write(text)
print('templates+accordion added; collapseAllInBox present:', 'function collapseAllInBox' in text)
