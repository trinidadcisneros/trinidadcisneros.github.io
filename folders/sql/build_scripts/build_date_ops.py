import sys, re
sys.path.insert(0,'/sessions/intelligent-quirky-volta/mnt/outputs')
from eabuild import build_card, verify, balance_report
PATH='/sessions/intelligent-quirky-volta/mnt/sql/sql_problem_patterns.html'

CARDS=[
 dict(anchor='__T__', diff='Medium', color='#e65100',
  title='Monthly Writing Streak Days by User',
  excerpt='Bucket sessions into months with DATE_TRUNC, count distinct active days, keep months with 5+.',
  prompt=[
    'A note-taking app logs one row per user per day they wrote. Group sessions into <strong>monthly cohorts</strong> and count the distinct days each user wrote that month.',
    'Only keep month-user combinations with at least <strong>5 distinct days</strong>.',
    'Return <code>user_id</code>, <code>writing_month</code> (first day of the month as a DATE), <code>days_written</code>, ordered by <code>user_id</code> then <code>writing_month</code>.'],
  inputs=[
    {'name':'users','cols':[('user_id','INT'),('username','VARCHAR'),('signup_date','DATE')],
     'headers':['user_id','username','signup_date'],'rows':[[1,'alice','2024-01-05'],[2,'bob','2024-01-10'],[3,'charlie','2024-02-01']]},
    {'name':'writing_sessions','cols':[('session_id','INT'),('user_id','INT'),('session_date','DATE'),('notes_written','INT')],
     'headers':['session_id','user_id','session_date','notes_written'],
     'rows':[[101,1,'2024-01-10',3],[102,1,'2024-01-12',2],[103,1,'2024-01-15',1],[104,1,'2024-01-20',4],[105,1,'2024-01-25',2],[106,1,'2024-02-03',1],[107,2,'2024-01-11',5],[108,2,'2024-01-12',3],[109,2,'2024-01-18',2],[110,3,'2024-02-05',1]]}],
  exp_headers=['user_id','writing_month','days_written'],
  exp_rows=[[1,'2024-01-01',5]],
  sol_comment="DATE_TRUNC('month', session_date) collapses every date to the first of its month, so GROUP BY that bucket forms monthly cohorts. COUNT(DISTINCT session_date) counts active days (not sessions). The HAVING runs after grouping to keep only buckets with 5+ days -- only alice's January (5 days) qualifies; bob has 3, charlie has 1. Cast the bucket to ::date so it prints as a plain date.",
  sol_sql="""SELECT
    user_id,
    DATE_TRUNC('month', session_date)::date AS writing_month,   -- month bucket
    COUNT(DISTINCT session_date) AS days_written                -- active days, not sessions
FROM writing_sessions
GROUP BY user_id, DATE_TRUNC('month', session_date)
HAVING COUNT(DISTINCT session_date) >= 5                        -- keep 5+ day months
ORDER BY user_id, writing_month;"""),

 dict(anchor='__E__', diff='Easy', color='#2e7d32',
  title='Orders by Day of Week',
  excerpt='Pull the weekday out of each date with EXTRACT(DOW ...) and group on it.',
  prompt=[
    'Count how many orders fall on each <strong>day of week</strong> (0 = Sunday … 6 = Saturday).',
    'Return <code>dow</code> and <code>orders</code>, ordered by <code>dow</code>. Only days that occur appear.'],
  inputs=[
    {'name':'orders','cols':[('order_id','INT'),('order_date','DATE')],
     'headers':['order_id','order_date'],'rows':[[1,'2024-01-07'],[2,'2024-01-08'],[3,'2024-01-15'],[4,'2024-01-13']]}],
  exp_headers=['dow','orders'],
  exp_rows=[[0,1],[1,2],[6,1]],
  sol_comment="EXTRACT(DOW FROM order_date) returns the weekday as a number (0 = Sunday). Grouping on that same expression buckets the orders by weekday. Jan 7 is a Sunday (0), Jan 8 and Jan 15 are Mondays (1), Jan 13 is a Saturday (6). Cast to ::int for a clean integer column.",
  sol_sql="""SELECT
    EXTRACT(DOW FROM order_date)::int AS dow,   -- 0 = Sunday .. 6 = Saturday
    COUNT(*) AS orders
FROM orders
GROUP BY EXTRACT(DOW FROM order_date)
ORDER BY dow;"""),

 dict(anchor='__A__', diff='Medium', color='#e65100',
  title='Subscriptions Ending by a Cutoff',
  excerpt='Add a day count to a date (start_date + term_days), then filter against a literal cutoff.',
  prompt=[
    'Each subscription runs <code>term_days</code> from its <code>start_date</code>. Its end date is <code>start_date + term_days</code>.',
    'Return <code>sub_id</code> and <code>end_date</code> for subscriptions ending <strong>on or before 2024-02-01</strong>, ordered by <code>sub_id</code>.'],
  inputs=[
    {'name':'subscriptions','cols':[('sub_id','INT'),('start_date','DATE'),('term_days','INT')],
     'headers':['sub_id','start_date','term_days'],'rows':[[1,'2024-01-01',30],[2,'2024-02-15',7],[3,'2024-01-10',5]]}],
  exp_headers=['sub_id','end_date'],
  exp_rows=[[1,'2024-01-31'],[3,'2024-01-15']],
  sol_comment="Adding an integer to a DATE moves it forward that many days, so start_date + term_days is the end date -- no INTERVAL needed for whole days. The same expression in WHERE keeps only subscriptions ending by the LITERAL cutoff (never CURRENT_DATE, so the result is reproducible). Sub 2 ends Feb 22 and is dropped.",
  sol_sql="""SELECT
    sub_id,
    start_date + term_days AS end_date          -- DATE + INT moves forward N days
FROM subscriptions
WHERE start_date + term_days <= DATE '2024-02-01'   -- literal cutoff, not CURRENT_DATE
ORDER BY sub_id;"""),

 dict(anchor='__D__', diff='Medium', color='#e65100',
  title='Ticket Resolution Time in Hours',
  excerpt='Subtract two timestamps and convert the interval to hours with EXTRACT(EPOCH ...).',
  prompt=[
    'For each ticket, compute how long it took to resolve, in <strong>hours</strong>.',
    'Return <code>ticket_id</code> and <code>hours</code>, ordered by <code>ticket_id</code>.'],
  inputs=[
    {'name':'tickets','cols':[('ticket_id','INT'),('opened_at','TIMESTAMP'),('resolved_at','TIMESTAMP')],
     'headers':['ticket_id','opened_at','resolved_at'],
     'rows':[[1,'2024-01-01 09:00:00','2024-01-01 12:00:00'],[2,'2024-01-02 08:00:00','2024-01-03 08:00:00']]}],
  exp_headers=['ticket_id','hours'],
  exp_rows=[[1,3.0],[2,24.0]],
  sol_comment="Subtracting two timestamps yields an INTERVAL, which is awkward to compare. EXTRACT(EPOCH FROM (resolved_at - opened_at)) turns it into total seconds; dividing by 3600 gives hours (use 86400 for days). Ticket 1 took 3 hours, ticket 2 a full 24.",
  sol_sql="""SELECT
    ticket_id,
    EXTRACT(EPOCH FROM (resolved_at - opened_at)) / 3600 AS hours   -- seconds -> hours
FROM tickets
ORDER BY ticket_id;"""),

 dict(anchor='__C__', diff='Easy', color='#2e7d32',
  title='Inclusive Trial Length in Days',
  excerpt='The off-by-one: an inclusive span is (end - start) + 1 days.',
  prompt=[
    'Each trial runs from <code>start_date</code> to <code>end_date</code> inclusive (both days count).',
    'Return <code>trial_id</code> and <code>days_inclusive</code>, ordered by <code>trial_id</code>.'],
  inputs=[
    {'name':'trials','cols':[('trial_id','INT'),('start_date','DATE'),('end_date','DATE')],
     'headers':['trial_id','start_date','end_date'],'rows':[[1,'2024-01-01','2024-01-10'],[2,'2024-03-01','2024-03-01']]}],
  exp_headers=['trial_id','days_inclusive'],
  exp_rows=[[1,10],[2,1]],
  sol_comment="Subtracting two dates gives the number of nights BETWEEN them: Jan 10 - Jan 1 = 9. But a trial that runs Jan 1 through Jan 10 inclusive lasts 10 days, so add 1. A single-day trial (start = end) is 0 + 1 = 1. The + 1 is the whole point of this shape.",
  sol_sql="""SELECT
    trial_id,
    (end_date - start_date) + 1 AS days_inclusive   -- +1 makes the span inclusive
FROM trials
ORDER BY trial_id;"""),
]

LEAFMETA=[
 ('do-leaf-trunc','DATE_TRUNC cohort buckets (month / week / quarter)',
  'Collapse each date to the start of its period with <code>DATE_TRUNC(\'month\', d)::date</code>, then GROUP BY that bucket. Optionally a HAVING on the per-bucket aggregate.'),
 ('do-leaf-extract','EXTRACT a date component (year, day-of-week, hour)',
  'Pull one part out of a date with <code>EXTRACT(DOW FROM d)</code> / <code>YEAR</code> / <code>HOUR</code> and GROUP BY or filter on it.'),
 ('do-leaf-arithmetic','Date arithmetic (DATE +/- days / INTERVAL, cutoffs)',
  'Move a date by whole days (<code>d + n</code>) or an <code>INTERVAL</code>, or filter against a LITERAL / data-derived cutoff. Never <code>CURRENT_DATE</code>.'),
 ('do-leaf-duration','Duration between two timestamps (EXTRACT EPOCH)',
  'Subtract two timestamps and convert the interval with <code>EXTRACT(EPOCH FROM (b - a)) / 3600</code> for hours (<code>/ 86400</code> for days).'),
 ('do-leaf-daycount','Inclusive vs exclusive day counts',
  'The off-by-one: <code>end - start</code> counts the nights between; an inclusive span is <code>(end - start) + 1</code> days.'),
]

def leaf(anchor,title,excerpt,card_html):
    return ('<div id="%s" class="problem-card collapsed qtype-group">\n'
            '                <div class="problem-card-header">\n'
            '                  <h3 class="problem-card-title" style="margin: 0;">%s <span class="count-badge">1 problem</span></h3>\n'
            '                  <span class="problem-toggle">&#9660;</span>\n'
            '                </div>\n'
            '                <div class="problem-card-excerpt">\n'
            '                  <p style="margin: 0;">%s</p>\n'
            '                </div>\n'
            '                <div class="problem-card-content">\n\n'
            '                            %s\n'
            '                </div>\n'
            '              </div>\n') % (anchor, title, excerpt, card_html)

for c in CARDS:
    ok, got, exp = verify(c)
    print(('OK  ' if ok else 'FAIL ')+c['title'])
    if not ok:
        print('  got',got,'\n  exp',exp); raise SystemExit('verify failed')

leaves_html=''.join(leaf(LEAFMETA[i][0], LEAFMETA[i][1], LEAFMETA[i][2], build_card(CARDS[i])) for i in range(5))

CONTAINER='''
<!-- RECIPE: date-operations -->
          <div class="problem-card" id="date-operations">
            <div class="problem-card-header">
              <h3 class="problem-card-title" style="margin: 0;">Date Operations <span class="count-badge">5 patterns</span></h3>
              <span class="problem-toggle">&#9660;</span>
            </div>
            <div class="problem-card-excerpt">
              <p>Single-table date and timestamp math: bucket rows into periods, pull out date parts, add or subtract days, and measure durations &mdash; no joins, no reshape.</p>
            </div>
            <div class="problem-card-content">

              <div id="do-decide" class="problem-card collapsed qtype-group" style="border-left-color:#6a1b9a;">
                <div class="problem-card-header">
                  <h3 class="problem-card-title" style="margin:0;">How to pick: decision tree</h3>
                  <span class="problem-toggle">&#9660;</span>
                </div>
                <div class="problem-card-excerpt"><p style="margin:0;">Answer each question — the next one appears, ending on the exact technique to use.</p></div>
                <div class="problem-card-content">
<div id="do-decide-itree" class="itree"></div>
                </div>
              </div>
''' + leaves_html + '''            </div>
          </div>
'''

text=open(PATH).read()
before=balance_report(text)
# end of row-transform container (the element, not the CSS selectors)
start=text.find('<div class="problem-card" id="row-transform">')
assert start>0, 'row-transform container not found'
depth=0; end=None
for m in re.finditer(r'<(/?)div\b', text[start:]):
    depth += 1 if m.group(1)=='' else -1
    if depth==0: end=start+text[start:].find('>',m.start())+1; break
assert end, 'no row-transform end'
text=text[:end]+'\n'+CONTAINER+text[end:]
# CSS: add date-operations to the two single-tab header selector lists
text=text.replace(
 '    #tab-single .problem-card[id="delete-duplicates"] > .problem-card-header {',
 '    #tab-single .problem-card[id="date-operations"] > .problem-card-header,\n    #tab-single .problem-card[id="delete-duplicates"] > .problem-card-header {')
text=text.replace(
 '    #tab-single .problem-card[id="delete-duplicates"] > .problem-card-header > .problem-card-title {',
 '    #tab-single .problem-card[id="date-operations"] > .problem-card-header > .problem-card-title,\n    #tab-single .problem-card[id="delete-duplicates"] > .problem-card-header > .problem-card-title {')
after=balance_report(text)
print('before',before); print('after ',after)
assert after['div_open']==after['div_close'] and after['final_depth']==0 and after['min_depth']>=0
assert text.count('<svg')==text.count('</svg>')
open(PATH,'w').write(text)
print('container inserted; leaves present:', all(('id="%s"'%a) in text for a,_,_ in LEAFMETA), '| do-decide-itree:', 'id="do-decide-itree"' in text)
