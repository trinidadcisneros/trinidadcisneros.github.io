import sys, re
sys.path.insert(0,'/sessions/intelligent-quirky-volta/mnt/outputs')
from eabuild import build_card, verify, balance_report
PATH='/sessions/intelligent-quirky-volta/mnt/sql/sql_problem_patterns.html'

c=dict(
 diff='Medium', color='#e65100',
 title='Remove Duplicate Refill Records per Patient (composite key)',
 excerpt='Duplicate key is three columns; keep the earliest <code>created_at</code>, delete the rest by primary key.',
 prompt=[
   'Import errors created duplicate refill rows. A duplicate is any rows sharing all of <code>patient_id</code>, <code>medication_code</code>, and <code>refill_date</code>.',
   'Reduce each duplicate set to one row: keep the <strong>earliest</strong> <code>created_at</code>; if tied, keep the lowest <code>record_id</code>. Single rows stay untouched.',
   'Write a DELETE, then <code>SELECT * FROM refill_records ORDER BY record_id;</code>.'],
 inputs=[
   {'name':'refill_records','cols':[('record_id','INT'),('patient_id','INT'),('medication_code','VARCHAR'),('refill_date','DATE'),('days_supply','INT'),('created_at','TIMESTAMP')],
    'headers':['record_id','patient_id','medication_code','refill_date','days_supply','created_at'],
    'rows':[
      [1,101,'MED-A','2024-01-15',30,'2024-01-15 08:00:00'],
      [2,101,'MED-A','2024-01-15',30,'2024-01-15 08:05:00'],
      [3,102,'MED-B','2024-01-20',60,'2024-01-20 09:00:00'],
      [4,103,'MED-C','2024-02-01',90,'2024-02-01 10:00:00'],
      [5,103,'MED-C','2024-02-01',90,'2024-02-01 10:00:00'],
      [6,103,'MED-C','2024-02-01',90,'2024-02-01 10:10:00'],
      [7,104,'MED-D','2024-02-10',30,'2024-02-10 11:00:00'],
      [8,101,'MED-A','2024-02-15',30,'2024-02-15 08:00:00']]}],
 exp_headers=['record_id','patient_id','medication_code','refill_date','days_supply','created_at'],
 exp_rows=[
   [1,101,'MED-A','2024-01-15',30,'2024-01-15 08:00:00'],
   [3,102,'MED-B','2024-01-20',60,'2024-01-20 09:00:00'],
   [4,103,'MED-C','2024-02-01',90,'2024-02-01 10:00:00'],
   [7,104,'MED-D','2024-02-10',30,'2024-02-10 11:00:00'],
   [8,101,'MED-A','2024-02-15',30,'2024-02-15 08:00:00']],
 sol_comment=("The duplicate key spans three columns, so list ALL three in PARTITION BY -- that is the only "
   "change from the single-key case. ROW_NUMBER orders each group by created_at then record_id, so rn = 1 "
   "is the earliest original. Delete the losers (rn > 1) by PRIMARY KEY with IN: leaner and NULL-safe than a "
   "multi-column NOT IN of the survivors, and you never need to carry the key columns into the delete set. "
   "Verified against the example data -- 3 duplicates removed, 5 rows survive."),
 verify_sql=("DELETE FROM refill_records WHERE record_id IN ("
   "SELECT record_id FROM ("
   "SELECT record_id, ROW_NUMBER() OVER (PARTITION BY patient_id, medication_code, refill_date "
   "ORDER BY created_at, record_id) AS rn FROM refill_records) d WHERE rn > 1);"),
 check_sql='SELECT * FROM refill_records ORDER BY record_id;',
 sol_sql="""DELETE FROM refill_records
WHERE record_id IN (                              -- delete the losers by PK
    SELECT record_id FROM (
        SELECT record_id,
               ROW_NUMBER() OVER (PARTITION BY patient_id, medication_code, refill_date  -- composite key
                                  ORDER BY created_at, record_id) AS rn                  -- earliest survives
        FROM refill_records
    ) d
    WHERE rn > 1
);

SELECT * FROM refill_records ORDER BY record_id;""",
)

ok, got, exp = verify(c)
print(('OK' if ok else 'FAIL'), c['title'])
if not ok:
    print('got',got); print('exp',exp); raise SystemExit('verify failed')

text=open(PATH).read()
before=balance_report(text)

# 1) composite-key note in the leaf excerpt
old_exc='<div class="problem-card-excerpt"><p style="margin: 0;">Number rows within each duplicate group and delete everything past the first. The flexible method when the survivor is ordered by a non-id column.</p></div>'
new_exc='<div class="problem-card-excerpt"><p style="margin: 0;">Number rows within each duplicate group and delete everything past the first. The flexible method when the survivor is ordered by a non-id column. <strong>For a multi-column duplicate key, list every key column in <code>PARTITION BY</code>.</strong></p></div>'
assert text.count(old_exc)==1, 'excerpt not found'
text=text.replace(old_exc,new_exc,1)

# 2) badge template only -> 1 problem
text=text.replace('ROW_NUMBER then delete rn &gt; 1 <span class="count-badge">template only</span>',
                  'ROW_NUMBER then delete rn &gt; 1 <span class="count-badge">1 problem</span>',1)

# 3) insert worked card at end of the leaf content
i=text.find('id="dd-leaf-rownumber"')
co=text.find('<div class="problem-card-content">', i); co_end=co+len('<div class="problem-card-content">')
depth=1; cc=None
for m in re.finditer(r'<(/?)div\b', text[co_end:]):
    depth += 1 if m.group(1)=='' else -1
    if depth==0: cc=co_end+m.start(); break
assert cc, 'leaf content end not found'
card='\n                            '+build_card(c)+'\n              '
text=text[:cc]+card+text[cc:]

after=balance_report(text)
print('before',before); print('after ',after)
assert after['div_open']==after['div_close'] and after['final_depth']==0 and after['min_depth']>=0
assert text.count('<svg')==text.count('</svg>')
open(PATH,'w').write(text)
print('added composite-key note + new worked recipe to dd-leaf-rownumber')
