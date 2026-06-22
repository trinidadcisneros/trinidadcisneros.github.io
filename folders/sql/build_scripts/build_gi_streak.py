import sys, re
sys.path.insert(0,'/sessions/intelligent-quirky-volta/mnt/outputs')
from eabuild import build_card, verify, balance_report
PATH='/sessions/intelligent-quirky-volta/mnt/sql/sql_problem_patterns.html'

c=dict(
 diff='Medium', color='#e65100',
 title='Consecutive Streaks by State (two-table merged timeline)',
 excerpt='Two source tables stacked into one labelled timeline; find consecutive streaks per state with rn_overall &minus; rn_per_state.',
 prompt=[
   'Two tables log events: <code>submitted_assignments</code> and <code>revised_assignments</code> (one event type per day; some days have none).',
   'Find consecutive date streaks for each <strong>state</strong>, where "consecutive" means consecutive in the <strong>combined timeline of all events</strong>, ignoring missing days.',
   'Return <code>state</code>, <code>start_date</code> (earliest in the streak), <code>end_date</code> (latest), ordered by <code>start_date</code>.',
   '<strong>Who is the entity?</strong> The streaks are per <code>state</code> on one shared timeline. <code>student_id</code> never appears in the output &mdash; it is a passenger column, not the entity.'],
 inputs=[
   {'name':'submitted_assignments','cols':[('student_id','INT'),('submission_date','DATE')],
    'headers':['student_id','submission_date'],
    'rows':[[101,'2024-03-01'],[102,'2024-03-02'],[103,'2024-03-05'],[104,'2024-03-08'],[105,'2024-03-09']]},
   {'name':'revised_assignments','cols':[('student_id','INT'),('revision_date','DATE')],
    'headers':['student_id','revision_date'],
    'rows':[[201,'2024-03-03'],[202,'2024-03-04'],[203,'2024-03-10']]}],
 exp_headers=['state','start_date','end_date'],
 exp_rows=[
   ['submitted','2024-03-01','2024-03-02'],
   ['revised','2024-03-03','2024-03-04'],
   ['submitted','2024-03-05','2024-03-09'],
   ['revised','2024-03-10','2024-03-10']],
 sol_comment=("Stack the two tables into one timeline carrying a state label (UNION ALL). The gaps-and-islands "
   "move: number the rows over the WHOLE timeline, then again per state; within an unbroken run of one state "
   "both counters step together, so their DIFFERENCE stays constant -- a row's grp id. GROUP BY state and grp, "
   "then MIN/MAX the dates. The entity is the STATE, not student_id: student_id is never selected. This is the "
   "'merged states on a shared timeline' form (rn_overall - rn_per_status), distinct from per-entity streaks "
   "(which partition the overall counter too) and from calendar-consecutive (date - rn). Assumes one event per "
   "day in the combined timeline, so the overall ORDER BY date is unambiguous. Verified against the example data."),
 sol_sql="""WITH events AS (
    SELECT 'submitted' AS state, submission_date AS event_date FROM submitted_assignments
    UNION ALL
    SELECT 'revised'   AS state, revision_date   AS event_date FROM revised_assignments
),
grouped AS (
    SELECT state, event_date,
           ROW_NUMBER() OVER (ORDER BY event_date)                          -- position in the whole timeline
         - ROW_NUMBER() OVER (PARTITION BY state ORDER BY event_date) AS grp -- position within the state
    FROM events                                                             -- (difference is constant per run)
)
SELECT state, MIN(event_date) AS start_date, MAX(event_date) AS end_date
FROM grouped
GROUP BY state, grp
ORDER BY start_date;""",
)

ok, got, exp = verify(c)
print(('OK' if ok else 'FAIL'), c['title'])
if not ok:
    print('got',got); print('exp',exp); raise SystemExit('verify failed')

text=open(PATH).read()
before=balance_report(text)

# entity-vs-label note in the leaf excerpt
needle='their difference is constant across a run.</p>'
assert text.count(needle)==1, 'gi-leaf-date-gap excerpt not found'
text=text.replace(needle,
  'their difference is constant across a run. <strong>The entity here is the STATE label on one shared timeline; columns that never appear in the output (e.g. student_id) are passengers, not the entity.</strong></p>',1)

# bump badge 2 -> 3
text=text.replace('Consecutive dates with gaps / merged states <span class="count-badge">2 problems</span>',
                  'Consecutive dates with gaps / merged states <span class="count-badge">3 problems</span>',1)

# insert worked card at end of the gi-leaf-date-gap leaf content
hi=text.find('id="gi-leaf-date-gap"')           # id sits on the header
cs=text.rfind('<div class="problem-card', 0, hi)  # enclosing leaf container
co=text.find('<div class="problem-card-content">', hi); co_end=co+len('<div class="problem-card-content">')
depth=1; cc=None
for m in re.finditer(r'<(/?)div\b', text[co_end:]):
    depth += 1 if m.group(1)=='' else -1
    if depth==0: cc=co_end+m.start(); break
assert cc, 'leaf content end not found'
card='\n                            '+build_card(c)+'\n              '
text=text[:cc]+card+text[cc:]

after=balance_report(text)
print('before',before['div_open'],before['div_close']); print('after ',after['div_open'],after['div_close'])
assert after['div_open']==after['div_close'] and after['final_depth']==0 and after['min_depth']>=0
assert text.count('<svg')==text.count('</svg>')
open(PATH,'w').write(text)
print('added gi-leaf-date-gap worked recipe + entity note')
