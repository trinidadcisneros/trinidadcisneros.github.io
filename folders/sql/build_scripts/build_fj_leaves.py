import sys, re
sys.path.insert(0,'/sessions/intelligent-quirky-volta/mnt/outputs')
from eabuild import build_card, verify, balance_report
PATH='/sessions/intelligent-quirky-volta/mnt/sql/sql_problem_patterns.html'

CARDS=[
 dict(anchor='__B__', diff='Medium', color='#e65100',
  title='Resolved Tickets per Team',
  excerpt='Count only resolved tickets per team; teams with none still read 0.',
  prompt=[
    'A support dashboard lists every team and how many of its tickets are <strong>resolved</strong>. A team with no resolved tickets must still appear with 0.',
    '<code>teams</code> names each team; <code>tickets</code> logs each ticket\'s team and status.',
    'Return <code>team_id</code>, <code>team_name</code>, <code>resolved_count</code>, ordered by <code>team_id</code>.'],
  inputs=[
    {'name':'teams','cols':[('team_id','INT'),('team_name','VARCHAR')],
     'headers':['team_id','team_name'],'rows':[[1,'Alpha'],[2,'Beta'],[3,'Gamma']]},
    {'name':'tickets','cols':[('ticket_id','INT'),('team_id','INT'),('status','VARCHAR')],
     'headers':['ticket_id','team_id','status'],'rows':[[1,1,'resolved'],[2,1,'open'],[3,1,'resolved'],[4,2,'open']]}],
  exp_headers=['team_id','team_name','resolved_count'],
  exp_rows=[[1,'Alpha',2],[2,'Beta',0],[3,'Gamma',0]],
  sol_comment="The status filter (status = 'resolved') is on the RIGHT table, so it rides in the ON next to the join key. Beta's only ticket is open and Gamma has none, but the LEFT JOIN keeps both teams and COUNT(t.ticket_id) -- a right-side column, not * -- reports 0. Put status in WHERE and both teams vanish.",
  sol_sql="""SELECT tm.team_id, tm.team_name, COUNT(t.ticket_id) AS resolved_count
FROM teams AS tm
LEFT JOIN tickets AS t
    ON t.team_id = tm.team_id AND t.status = 'resolved'   -- right-side filter in ON
GROUP BY tm.team_id, tm.team_name
ORDER BY tm.team_id;"""),

 dict(anchor='__C__', diff='Medium', color='#e65100',
  title='Large Orders per Store',
  excerpt='Count only orders of $100 or more per store; stores with none still read 0.',
  prompt=[
    'Report every store with the count of its orders worth <strong>at least $100</strong>. A store with no qualifying order must still appear with 0.',
    '<code>stores</code> names each store; <code>orders</code> logs each order\'s store and amount.',
    'Return <code>store_id</code>, <code>store_name</code>, <code>big_orders</code>, ordered by <code>store_id</code>.'],
  inputs=[
    {'name':'stores','cols':[('store_id','INT'),('store_name','VARCHAR')],
     'headers':['store_id','store_name'],'rows':[[1,'North'],[2,'South'],[3,'East']]},
    {'name':'orders','cols':[('order_id','INT'),('store_id','INT'),('amount','INT')],
     'headers':['order_id','store_id','amount'],'rows':[[1,1,150],[2,1,80],[3,1,200],[4,2,50]]}],
  exp_headers=['store_id','store_name','big_orders'],
  exp_rows=[[1,'North',2],[2,'South',0],[3,'East',0]],
  sol_comment="The numeric threshold (amount >= 100) tests the RIGHT table, so it belongs in the ON. South's only order is $50 and East has none; the LEFT JOIN keeps them and COUNT(o.order_id) reports 0. Moving the threshold to WHERE drops every store with no big order.",
  sol_sql="""SELECT s.store_id, s.store_name, COUNT(o.order_id) AS big_orders
FROM stores AS s
LEFT JOIN orders AS o
    ON o.store_id = s.store_id AND o.amount >= 100   -- right-side threshold in ON
GROUP BY s.store_id, s.store_name
ORDER BY s.store_id;"""),

 dict(anchor='__D__', diff='Hard', color='#b71c1c',
  title='Q1 Training for 2024 Hires',
  excerpt='Left filter (hired in 2024) goes in WHERE; right filter (Q1 sessions) goes in ON.',
  prompt=[
    'For employees <strong>hired in 2024</strong>, count their training sessions completed in <strong>Q1 2024</strong> (Jan 1 to Mar 31). A 2024 hire with no Q1 session must still appear with 0.',
    'The hire-date test is about the LEFT (employee) table; the Q1 test is about the RIGHT (session) table.',
    '<code>employees</code> lists each hire; <code>sessions</code> logs completed training.',
    'Return <code>emp_id</code>, <code>name</code>, <code>q1_sessions</code>, ordered by <code>emp_id</code>.'],
  inputs=[
    {'name':'employees','cols':[('emp_id','INT'),('name','VARCHAR'),('hire_date','DATE')],
     'headers':['emp_id','name','hire_date'],'rows':[[1,'Ann','2024-02-01'],[2,'Bob','2023-05-01'],[3,'Cara','2024-06-01']]},
    {'name':'sessions','cols':[('session_id','INT'),('emp_id','INT'),('completed_date','DATE')],
     'headers':['session_id','emp_id','completed_date'],'rows':[[1,1,'2024-01-10'],[2,1,'2024-05-01'],[3,2,'2024-01-15']]}],
  exp_headers=['emp_id','name','q1_sessions'],
  exp_rows=[[1,'Ann',1],[3,'Cara',0]],
  sol_comment="Two filters, two clauses. The LEFT-table filter (hired in 2024) removes Bob for real, so it MUST go in WHERE. The RIGHT-table filter (session in Q1) must go in ON so Cara -- a 2024 hire with no Q1 session -- still appears with 0. Swap them and it breaks: a left filter in ON is a no-op (Bob would sneak back), a right filter in WHERE drops Cara. Half-open date ranges throughout.",
  sol_sql="""SELECT e.emp_id, e.name, COUNT(s.session_id) AS q1_sessions
FROM employees AS e
LEFT JOIN sessions AS s
    ON s.emp_id = e.emp_id
   AND s.completed_date >= DATE '2024-01-01'      -- RIGHT filter -> ON
   AND s.completed_date <  DATE '2024-04-01'
WHERE e.hire_date >= DATE '2024-01-01'            -- LEFT filter -> WHERE
  AND e.hire_date <  DATE '2025-01-01'
GROUP BY e.emp_id, e.name
ORDER BY e.emp_id;"""),

 dict(anchor='__E__', diff='Medium', color='#e65100',
  title='Completed Spend per Customer',
  excerpt='SUM a right-side column, wrapped in COALESCE so no-spend customers read 0, not NULL.',
  prompt=[
    'Report every customer\'s total spend on <strong>completed</strong> orders. A customer with no completed order must read <strong>0</strong>, not NULL.',
    '<code>customers</code> names each customer; <code>orders</code> logs status and amount.',
    'Return <code>cust_id</code>, <code>name</code>, <code>completed_spend</code>, ordered by <code>cust_id</code>.'],
  inputs=[
    {'name':'customers','cols':[('cust_id','INT'),('name','VARCHAR')],
     'headers':['cust_id','name'],'rows':[[1,'Amy'],[2,'Ben'],[3,'Cy']]},
    {'name':'orders','cols':[('order_id','INT'),('cust_id','INT'),('status','VARCHAR'),('amount','INT')],
     'headers':['order_id','cust_id','status','amount'],'rows':[[1,1,'completed',100],[2,1,'completed',50],[3,1,'cancelled',999],[4,2,'cancelled',30]]}],
  exp_headers=['cust_id','name','completed_spend'],
  exp_rows=[[1,'Amy',150],[2,'Ben',0],[3,'Cy',0]],
  sol_comment="The status filter rides in the ON so Ben (only a cancelled order) and Cy (no orders) survive. For a SUM the danger is NULL, not a miscount: with no qualifying row SUM returns NULL, so wrap it in COALESCE(SUM(...), 0). Amy's cancelled $999 never enters because the ON already filtered it out.",
  sol_sql="""SELECT c.cust_id, c.name, COALESCE(SUM(o.amount), 0) AS completed_spend
FROM customers AS c
LEFT JOIN orders AS o
    ON o.cust_id = c.cust_id AND o.status = 'completed'   -- right-side filter in ON
GROUP BY c.cust_id, c.name
ORDER BY c.cust_id;"""),

 dict(anchor='__F__', diff='Medium', color='#e65100',
  title='Did Each User Order in 2024?',
  excerpt='A 1/0 existence flag per user; the date filter still rides in the ON.',
  prompt=[
    'For every user, output <strong>1</strong> if they placed any order in <strong>2024</strong>, else <strong>0</strong>. Every user must appear.',
    '<code>users</code> names each user; <code>orders</code> logs each order\'s date.',
    'Return <code>user_id</code>, <code>name</code>, <code>ordered_2024</code>, ordered by <code>user_id</code>.'],
  inputs=[
    {'name':'users','cols':[('user_id','INT'),('name','VARCHAR')],
     'headers':['user_id','name'],'rows':[[1,'Uma'],[2,'Val'],[3,'Wes']]},
    {'name':'orders','cols':[('order_id','INT'),('user_id','INT'),('order_date','DATE')],
     'headers':['order_id','user_id','order_date'],'rows':[[1,1,'2024-03-01'],[2,2,'2023-12-01']]}],
  exp_headers=['user_id','name','ordered_2024'],
  exp_rows=[[1,'Uma',1],[2,'Val',0],[3,'Wes',0]],
  sol_comment="The 2024 date window rides in the ON, so Val (only a 2023 order) and Wes (none) stay in the result. Turn the count into a yes/no with CASE WHEN COUNT(o.order_id) > 0 THEN 1 ELSE 0 END (BOOL_OR or COUNT(...) > 0 work too). A date filter in WHERE would drop Val and Wes entirely.",
  sol_sql="""SELECT u.user_id, u.name,
       CASE WHEN COUNT(o.order_id) > 0 THEN 1 ELSE 0 END AS ordered_2024
FROM users AS u
LEFT JOIN orders AS o
    ON o.user_id = u.user_id
   AND o.order_date >= DATE '2024-01-01'    -- right-side date window in ON
   AND o.order_date <  DATE '2025-01-01'
GROUP BY u.user_id, u.name
ORDER BY u.user_id;"""),
]

LEAFMETA=[
 ('fj-leaf-status','Right-side status / category in the ON',
  'The right-side filter is a status or category equality (<code>status = \'resolved\'</code>). It rides in the <code>ON</code> so non-matching entities survive with a 0.'),
 ('fj-leaf-threshold','Right-side numeric threshold in the ON',
  'The right-side filter is a numeric comparison (<code>amount &gt;= 100</code>). It rides in the <code>ON</code>; in <code>WHERE</code> it would drop every entity with no qualifying row.'),
 ('fj-leaf-bothsides','Left filter in WHERE + right filter in ON',
  'Two filters, two clauses: the LEFT (driver) filter belongs in <code>WHERE</code> (it really removes rows), the RIGHT (joined) filter belongs in <code>ON</code> (it keeps the survivors).'),
 ('fj-leaf-sumcoalesce','SUM / AVG with COALESCE (not COUNT)',
  'Same ON placement, but the metric is a <code>SUM</code>/<code>AVG</code> of a right column. With no qualifying row the aggregate is NULL, so wrap it in <code>COALESCE(SUM(...), 0)</code>.'),
 ('fj-leaf-existence','Boolean / existence flag per entity',
  'The output is a 1/0 (or true/false) per entity: does it have ANY qualifying right row? Use <code>COUNT(...) &gt; 0</code>, <code>BOOL_OR</code>, or <code>MAX(CASE ...)</code>; the filter still rides in the <code>ON</code>.'),
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

# verify all cards
for c in CARDS:
    ok, got, exp = verify(c)
    print(('OK  ' if ok else 'FAIL ')+c['title'])
    if not ok:
        print('  got',got,'\n  exp',exp); raise SystemExit('verify failed')

leaves_html=''.join(leaf(LEAFMETA[i][0], LEAFMETA[i][1], LEAFMETA[i][2], build_card(CARDS[i])) for i in range(5))

text=open(PATH).read()
# find end of ea-leaf-leftjoin-on container (balanced div from its id)
i=text.find('id="ea-leaf-leftjoin-on"'); start=text.rfind('<div',0,i)
depth=0; end=None
for m in re.finditer(r'<(/?)div\b', text[start:]):
    depth += 1 if m.group(1)=='' else -1
    if depth==0: end=start+text[start:].find('>',m.start())+1; break
assert end, 'no end for ea-leaf-leftjoin-on'
before=balance_report(text)
text=text[:end]+'\n'+leaves_html+text[end:]
# update container badge 2 problems -> 6 patterns
text=text.replace('Filtered Join (filter in the JOIN ON) <span class="count-badge">2 problems</span>',
                  'Filtered Join (filter in the JOIN ON) <span class="count-badge">6 patterns</span>')
after=balance_report(text)
print('before',before); print('after ',after)
assert after['div_open']==after['div_close'] and after['final_depth']==0 and after['min_depth']>=0
assert text.count('<svg')==text.count('</svg>')
open(PATH,'w').write(text)
print('inserted 5 leaves; ids present:', all(('id="%s"'%a) in text for a,_,_ in LEAFMETA))
