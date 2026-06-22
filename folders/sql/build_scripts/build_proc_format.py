import re
PATH='/sessions/intelligent-quirky-volta/mnt/sql/sql_problem_patterns.html'
text=open(PATH).read()

# (id, pill, title, old_count_badge_text, new_count or None, excerpt)
TOPICS=[
 ('topic-functions','Topic','Functions','17 problems','17 problems',
  'Wrap reusable logic in a function &mdash; <code>RETURNS</code> scalar returns a single value, <code>RETURNS TABLE</code> returns a result set. Pick the shape with the decision tree, then study the worked examples.'),
 ('topic-recursive-queries','Topic','Recursive Queries','1 problem','1 problem',
  'Walk a hierarchy or build a sequence with a recursive CTE: an anchor row plus a recursive member that joins back to itself with <code>UNION ALL</code>.'),
 ('topic-dml','Topic','Updates, Deletes, and Inserts','22 problems','22 problems',
  'Change data in place &mdash; <code>UPDATE</code> columns, <code>DELETE</code> rows, <code>INSERT</code> new rows, and multi-statement <code>DO</code> blocks &mdash; written to be safe and re-runnable.'),
 ('topic-window-edges','Reference','Window Function Edges','reference',None,
  'Reference notes on the tricky parts of window functions: frame clauses (<code>ROWS</code> vs <code>RANGE</code>), default frames, and ordering edge cases.'),
]

PILL='<span style="display: inline-block; background-color: #1565c0; color: white; padding: 4px 10px; border-radius: 3px; font-size: 1.328rem; font-weight: 600;">%s</span>'

for tid, pill, title, old_cnt, new_cnt, excerpt in TOPICS:
    old_h3='<h3 class="problem-card-title" style="margin: 0;">%s <span class="count-badge">%s</span></h3>' % (title, old_cnt)
    assert text.count(old_h3)==1, ('old h3 not unique/found', tid)
    cb=(' <span class="count-badge">%s</span>'%new_cnt) if new_cnt else ''
    new_h3=('<h3 class="problem-card-title" style="margin: 0; display: flex; align-items: center; gap: 15px;">'
            +(PILL%pill)+title+cb+'</h3>')
    text=text.replace(old_h3,new_h3,1)
    # insert excerpt between header and content
    i=text.find('id="%s"'%tid); ci=text.find('<div class="problem-card-content">', i)
    exc=('<div class="problem-card-excerpt">\n'
         '              <p>%s</p>\n'
         '            </div>\n            ' % excerpt)
    text=text[:ci]+exc+text[ci:]

# CSS: mirror the Reshape root-card look for #tab-procedural topic containers
CSS='''    /* Top-level topic containers — mirror the Reshape root cards (pill + big title + excerpt) */
    #tab-procedural .problem-card[id^="topic-"] > .problem-card-header {
      padding: 14px 18px;
      background-color: #fafafa;
    }
    #tab-procedural .problem-card[id^="topic-"] > .problem-card-header > .problem-card-title {
      font-size: 2.36rem !important;
      letter-spacing: -0.01em;
    }
    #tab-procedural .problem-card[id^="topic-"] > .problem-card-header > .problem-card-title > span[style*="background-color"] {
      background-color: #64748b !important;
      color: #ffffff !important;
      font-size: 0.944rem !important;
      padding: 2px 8px !important;
      letter-spacing: 0.04em !important;
      text-transform: uppercase;
      font-weight: 600 !important;
    }
    #tab-procedural .problem-card[id^="topic-"] > .problem-card-header .count-badge {
      margin-left: auto !important;
      background-color: #eef2f7 !important;
      color: #475569 !important;
      border: 1px solid #d8dee9 !important;
      border-radius: 12px !important;
      font-weight: 500 !important;
    }
    #tab-procedural .problem-card[id^="topic-"] > .problem-card-excerpt {
      padding: 12px 18px;
      font-size: 1.452rem;
      color: #475569;
    }
'''
anchor='    #tab-procedural .count-badge {'
assert text.count(anchor)==1
text=text.replace(anchor, CSS+anchor, 1)

# balance
do=len(re.findall(r'<div\b',text)); dc=len(re.findall(r'</div\b',text))
d=0;mn=0
for m in re.finditer(r'<(/?)div\b',text):
    d+=1 if m.group(1)=='' else -1; mn=min(mn,d)
assert do==dc and d==0 and mn>=0 and text.count('<svg')==text.count('</svg>'), (do,dc,d,mn)
open(PATH,'w').write(text)
print('updated 4 topic containers (pill + excerpt + CSS); div',do,dc)
