# Shared spec/code data for the interactive trees (no file IO).
def step(q,label,leaf,downlabel=None):
    br=[{'label':label,'leaf':leaf}]
    if downlabel is not None: br.append({'label':downlabel,'down':True})
    return {'q':q,'branches':br}
def s(q,lab,leaf,dn='no'): return {'q':q,'branches':[{'label':lab,'leaf':leaf},{'label':dn,'down':True}]}
def last(q,la,lfa,lb,lfb): return {'q':q,'branches':[{'label':la,'leaf':lfa},{'label':lb,'leaf':lfb}]}

SPECS={
 'dd-decide':[
   {'q':['What decides which row SURVIVES in each duplicate group?'],'branches':[
     {'label':'The latest / earliest one, or any rule on a non-id column (timestamp, value)','leaf':('ROW_NUMBER then delete rn > 1','number rows per key by your ORDER BY, keep rn = 1, delete the rest — handles ANY survivor rule and breaks ties cleanly','dd-leaf-rownumber')},
     {'label':'Strictly the lowest (or highest) id','down':True}]},
   {'q':['Lowest-id survivor — pick a style (ROW_NUMBER works here too)'],'branches':[
     {'label':'General & tie-safe: ROW_NUMBER, keep rn = 1, delete rn > 1','leaf':('ROW_NUMBER then delete rn > 1','ORDER BY id; the workhorse that also covers the lowest-id case','dd-leaf-rownumber')},
     {'label':'Shortest portable one-liner: keep MIN(id), delete the rest','leaf':('Keep the lowest id (NOT IN MIN)','MIN(id) per key survives; delete signup_id NOT IN those','dd-leaf-minid')},
     {'label':'Pairwise inequality with a self-join','leaf':('Self-join delete','delete the higher-id twin where two rows share the key','dd-leaf-selfjoin')}]}],
 'pit-decide':[
   {'q':['Need a value for EVERY','day in a range?'],'branches':[
     {'label':'yes','leaf':('Fill forward over a date spine','carry the last known value across empty days','pit-leaf-fill')},
     {'label':'no','down':True}]},
   {'q':['Must no-history entities','still appear (a default)?'],'branches':[
     {'label':'yes','leaf':('Default when no history','entity appears with a default / NULL','pit-leaf-default')},
     {'label':'no','leaf':('As of a single cutoff','latest row on or before one cutoff','pit-leaf-asof')}]}],
 'up-decide':[
   {'q':['Rolling up across the','columns (count / sum)?'],'branches':[
     {'label':'yes','leaf':('Unpivot then aggregate','stack in a CTE, then one GROUP BY','up-leaf-aggregate')},
     {'label':'no','down':True}]},
   {'q':['Keep NULL cells as rows,','or drop them?'],'branches':[
     {'label':'keep','leaf':('Columns to rows, keep the empties','NULL cells stay as rows','up-leaf-keep')},
     {'label':'drop','leaf':('Columns to rows, drop the empties','WHERE col IS NOT NULL drops the blanks','up-leaf-drop')}]}],
 'ej-decide':[
   {'q':"Output like (employee, their manager) or (player, who they beat) — two rows from the SAME table paired up?",'sub':"Your output shows two of the same kind of thing side by side, both pulled from one table.",'branches':[
     {'label':'yes','leaf':('Self-join: one table, two roles','alias the table twice (manager, pair)','ej-leaf-selfjoin')},
     {'label':'no','down':True}]},
   {'q':"Output like every (store, month) pair with 0 where nothing sold — one row per combination, empties included?",'sub':"Your output has a row for every pairing of two sets, even the ones with no data (gaps filled with 0).",'branches':[
     {'label':'yes','leaf':('Cross join: all combinations','every combo, then LEFT JOIN actuals','ej-leaf-cross')},
     {'label':'no','down':True}]},
   {'q':"Output like each sale with its store's average beside it — same rows as the detail, plus a group number column?",'sub':"Your output keeps every detail row and just adds a column with that group's number (average, smallest, earliest) next to it.",'branches':[
     {'label':'yes','leaf':('Match a per-group value','aggregate, then join it back to each row','ej-leaf-pergroup')},
     {'label':'no','down':True}]},
   {'q':"Output like the few customers who bought ALL categories — one row per entity that cleared multiple conditions?",'sub':"A short list of entities that each had to pass several tests; the ones that fail just disappear. Includes 'clears a threshold AND never did B' — a NOT EXISTS anti-join in WHERE, not a date in the join ON.",'branches':[
     {'label':'yes','leaf':('Compound eligibility','roll up / threshold, then qualify (incl. AND never did B anti-join)','ej-leaf-compound')},
     {'label':'no','leaf':('Straight lookup / enrich','pull a column onto each row via JOIN','ej-leaf-lookup')}]}],
 'sc-decide':[
   {'q':['One aggregate over','the whole table?'],'branches':[
     {'label':'yes','leaf':('Single aggregate','one MAX / MIN / SUM / COUNT','sc-leaf-aggregate')},
     {'label':'no','down':True}]},
   {'q':['A ratio / percentage','over the table?'],'branches':[
     {'label':'yes','leaf':('Ratio / percentage','one rate over the whole table','sc-leaf-ratio')},
     {'label':'no','down':True}]},
   {'q':['The single winner,','or the Nth highest?'],'branches':[
     {'label':'Nth','leaf':('Second / Nth highest','the Nth largest distinct value','sc-leaf-nth')},
     {'label':'winner','leaf':('Top-1 row','the one row that wins a ranking','sc-leaf-top1')}]}],
 'rp-multi-decide':[
   {'q':['A special pattern (median,','threshold, rank deltas)?'],'branches':[
     {'label':'yes','leaf':('Special rank patterns','median, threshold-from-rank, rank deltas','rp-multi-special')},
     {'label':'no','down':True}]},
   {'q':['More than one row','per group (top N)?'],'branches':[
     {'label':'yes','leaf':('Top N per group (N > 1)','rn <= N rows per group','rp-multi-topn')},
     {'label':'no','down':True}]},
   {'q':['Exactly the Nth row','(not the top)?'],'branches':[
     {'label':'yes','leaf':('Nth position','the 2nd most recent, the 3rd highest, etc.','rp-multi-nth')},
     {'label':'no','down':True}]},
   {'q':['Ranked by a value,','or by a date?'],'branches':[
     {'label':'date','leaf':('Top 1 by date','most recent / earliest per group','rp-multi-top1-by-date')},
     {'label':'value','leaf':('Top 1 by value','single winner by a metric','rp-multi-top1-by-value')}]}],
 'rf-decide':[
   step(['Match text against','a pattern?'],'yes',('Pattern (LIKE / regex)','match text against a pattern','rf-leaf-pattern'),'no'),
   step(['Hinges on a value being','missing (NULL)?'],'yes',('NULL-aware','a NULL / missing-value test','rf-leaf-null'),'no'),
   step(['Keep rows that DO appear','in another set?'],'yes',('Membership (IN / EXISTS)','row appears in the other set','rf-leaf-membership'),'no'),
   step(['Keep rows with NO match','(never / did not)?'],'yes',('Anti-join','no match: never / did not','rf-leaf-antijoin'),'no'),
   {'q':['Qualify on a threshold','across rows (HAVING)?'],'branches':[
     {'label':'yes','leaf':('Thresholds across rows','a HAVING gate on distinct rows','rf-leaf-having')},
     {'label':'no','leaf':('Comparison & boolean','=, !=, <, >, BETWEEN, IN, AND/OR','rf-leaf-compare')}]}],
 'ag-decide':[
   step(['Filter GROUPS by their','aggregate (HAVING)?'],'yes',('Filter groups (HAVING)','keep groups passing a test','ag-leaf-having'),'no'),
   step(['Split a metric by category','(CASE inside the aggregate)?'],'yes',('Conditional aggregation (CASE)','SUM/COUNT of a CASE per category','ag-leaf-conditional'),'no'),
   step(['A ratio / percentage','per group?'],'yes',('Ratio / percentage','numerator over denominator','ag-leaf-ratio'),'no'),
   step(['Count DISTINCT values','per group?'],'yes',('Count distinct per group','COUNT(DISTINCT col)','ag-leaf-countdistinct'),'no'),
   {'q':['Just count rows,','or sum / avg / min / max?'],'branches':[
     {'label':'count rows','leaf':('Count rows per group','COUNT(*) per group','ag-leaf-count')},
     {'label':'numeric rollup','leaf':('Sum / Avg / Min / Max','numeric rollup per group','ag-leaf-sumavg')}]}],
 'rp-decide':[
   step(['The MEDIAN','per group?'],'yes',('Median','middle value per group','rp-leaf-median'),'no'),
   step(['A percentile cutoff','(median, P90)?'],'yes',('PERCENTILE_CONT / DISC','one percentile value per group','rp-leaf-pct-agg'),'no'),
   step(['Top X% of rows','per group?'],'yes',('PERCENT_RANK (top X%)','keep the top fraction of rows','rp-leaf-pctrank'),'no'),
   step(['Which quartile / decile','each row falls in?'],'yes',('NTILE(n)','bucket each row into n bands','rp-leaf-ntile'),'no'),
   step(['Top N exact rows','per group?'],'yes',('ROW_NUMBER (rn <= N)','exactly N rows per group','rp-leaf-rownum'),'no'),
   {'q':['Ties share the rank','and skip the next?'],'branches':[
     {'label':'skip after ties','leaf':('RANK','Nth highest, ranks skip after a tie','rp-leaf-rank')},
     {'label':'no gaps','leaf':('DENSE_RANK','Nth distinct value, no skipped ranks','rp-leaf-denserank')}]}],
 'un-decide':[
   step(['Hand-build a fixed label set','(all labels must appear)?'],'yes',('Hand-build a label set','VALUES list of labels, LEFT JOIN data','un-leaf-labels'),'no'),
   {'q':['Reconcile rows in one','source but not the other?'],'branches':[
     {'label':'reconcile','leaf':('Reconcile two one-sided sets','one anti-join per direction, stacked','un-leaf-reconcile')},
     {'label':'two answers','leaf':('Stack two separate answers','two asks sharing one output column','un-leaf-stack')}]}],
 'tx-decide':[
   s(['Modify a column in place','(write to the table)?'],'yes',('UPDATE','modify a column in place','tx-leaf-update')),
   s(['Supply a fallback when','a column is NULL?'],'yes',('COALESCE','fallback when a column is NULL','tx-leaf-coalesce')),
   s(['Classify / relabel','with if-else?'],'yes',('CASE WHEN','classify or remap a value','tx-leaf-case')),
   s(['Combine columns','into one string?'],'yes',('CONCAT','join columns into a string','tx-leaf-concat')),
   s(['Pull a fixed part','of a string?'],'yes',('SUBSTRING / LEFT / RIGHT','a prefix / slice of a string','tx-leaf-substring')),
   last(['Change text case,','or clean messy text?'],'change case',('UPPER / LOWER','title / upper / lower case','tx-leaf-upperlower'),'clean text',('REPLACE / TRIM','swap chars or strip whitespace','tx-leaf-replace'))],
 'tw-decide':[
   s(['Group events into','sessions (gap-based)?'],'yes',('Sessionization','split events into sessions on a gap','sess-start')),
   s(['Compare each row to its','previous / next row?'],'yes',('LAG / LEAD','compare to the neighbour row','tw-tmpl-laglead')),
   s(['First / last value','in the partition?'],'yes',('FIRST_VALUE / LAST_VALUE','first / last row of the group','tw-tmpl-firstlast')),
   s(['Value as of a','cutoff date (as-of)?'],'yes',('Point in Time','most recent value as of a cutoff','tw-tmpl-pit')),
   s(['Rolling window of a','fixed N rows / days?'],'yes',('Sliding window (rolling N)','fixed N preceding rows','tw-tmpl-sliding')),
   last(['Compare to the group','benchmark, or running total?'],'group benchmark',('Group benchmark compare','AVG/MIN/MAX over the whole group','tw-tmpl-benchmark'),'running total',('Running / cumulative total','SUM/AVG/COUNT, growing window','tw-tmpl-running'))],
 'gbc-decide':[
   last(['Is there an ORDER BY in','the same OVER (ranking too)?'],'yes, has ORDER BY',('Explicit full frame','ROWS BETWEEN UNBOUNDED … UNBOUNDED','tw-tmpl-benchmark-frame'),'no ORDER BY',('No ORDER BY','default frame = the whole partition','tw-tmpl-benchmark'))],
 'nb-decide':[
   s(['Score each side of a','two-sided (matchup) row?'],'yes',('Matchup unpivot','split, score each side, group','nb-leaf-matchup')),
   last(['Treat (A,B) and (B,A)','as the same pair?'],'same pair',('Canonicalize the pair','LEAST / GREATEST, then group','nb-leaf-canon'),'pool both',('Pool both columns, count','UNION ALL ids, count per entity','nb-leaf-pool'))],
 'fj-decide':[
   {'q':['What are you producing per entity?'],'branches':[
     {'label':'A yes / no (1 or 0) — did it ever happen?','leaf':('Boolean / existence flag','COUNT(...) > 0 or BOOL_OR, filter still in ON','fj-leaf-existence')},
     {'label':'A SUM or AVG of a number','leaf':('SUM / AVG with COALESCE','wrap the aggregate so no-match reads 0','fj-leaf-sumcoalesce')},
     {'label':'A COUNT of qualifying rows','down':True}]},
   {'q':['Is the DRIVER (left) table also filtered?'],'branches':[
     {'label':'Yes — the left table has its own filter too','leaf':('Left in WHERE + right in ON','two filters, two clauses','fj-leaf-bothsides')},
     {'label':'No — only the joined rows are filtered','down':True}]},
   {'q':['What kind of filter is on the joined (right) table?'],'branches':[
     {'label':'A date range / window','leaf':('Right-side date window','count rows inside a date range','ea-leaf-leftjoin-on')},
     {'label':'A status or category equality','leaf':('Right-side status / category','status = … in the ON','fj-leaf-status')},
     {'label':'A numeric threshold (>, >=)','leaf':('Right-side numeric threshold','amount >= N in the ON','fj-leaf-threshold')}]}],
 'ea-decide':[
   s(['Keep non-matchers, filtering','the right table in the ON?'],'yes',('LEFT JOIN filter in ON','keep non-matchers, filter in ON','ea-leaf-leftjoin-on')),
   s(['Set membership','(has ALL of X, none of Y)?'],'yes',('Set membership (ALL / NONE)','HAVING MAX(CASE) gate','ea-leaf-membership')),
   s(['Aggregate within a','date window / cohort?'],'yes',('Date-window / cohort','join inside a date window','ea-leaf-datewin')),
   s(['A rate / ratio (num & denom','both from joins)?'],'yes',('Rate / ratio / percentage','numerator and denominator from joins','ea-leaf-rate')),
   s(['Filter on / inside','the aggregate (HAVING)?'],'yes',('Aggregate + filter (HAVING)','filter on or inside the aggregate','ea-leaf-filter')),
   last(['Just a count of joined rows,','or sum / avg / min / max?'],'count',('COUNT per group','count joined rows per entity','ea-leaf-count'),'rollup',('SUM / AVG / MIN / MAX','numeric rollup of a joined column','ea-leaf-sumavg'))],
 'ml-decide':[
   s(['Soccer-style points','(win 3, tie 1, loss 0)?'],'yes',('Soccer points','win 3, tie 1, loss 0','ml-tmpl-310')),
   s(['Win / loss records','(no ties scored)?'],'yes',('Win / loss records','no ties scored','ml-tmpl-winloss')),
   last(['Goals for / against,','or just sum a column?'],'goals for/against',('Goals for / against','differential per team','ml-tmpl-gfga'),'sum a column',('Sum a column per side','no win / loss logic','ml-tmpl-sumcol'))],
 'pv-decide':[
   s(['Net of opposing categories','(credit − debit)?'],'yes',('Signed aggregate (net)','credit − debit → one net total','pv-leaf-signed')),
   s(['Has ALL of X / none of Y','(set membership)?'],'yes',('Set membership (ALL / NONE)','has X and Y but never Z','pv-leaf-membership')),
   s(['Threshold per category','(spent ≥ N in EACH)?'],'yes',('Threshold per category','SUM(CASE) ≥ N per category','pv-leaf-threshold')),
   s(['Column key computed','from a date (weekday/month)?'],'yes',('Computed column key','weekday / month from a date','pv-leaf-derived')),
   last(['Empty cells must read 0,','or a plain stored-key pivot?'],'zero-fill',('Zero-fill the pivot','missing cells read 0','pv-leaf-zerofill'),'stored key',('Stored category to columns','key is already a column','pv-leaf-stored'))],
 'sg-decide':[
   s(['Active in every period','it spans (overlap)?'],'yes',('Period overlap','active in every period it overlaps','sg-leaf-overlap')),
   s(['Each row carries its own','[start, end] window (LATERAL)?'],'yes',('Per-row range (LATERAL)','expand each row across its window','sg-leaf-lateral')),
   s(['A fixed set of categorical','labels (bins / tiers)?'],'yes',('Categorical label spine','fixed labels via a VALUES list','sg-leaf-labels')),
   s(['Only entities that did','something in the window?'],'yes',('Spine × filtered entities','only active entities appear','sg-leaf-filtered')),
   last(['Bounds derived from the data,','or literal bounds × all entities?'],'from the data',('Bounds from the data','spine hugs the data range','sg-leaf-databounds'),'literal × all',('Full spine × all entities','literal bounds, every entity','sg-leaf-fullrange'))],
 'fn-decide':[
   {'q':['Does the function return one value, or a whole set of rows?'],'branches':[
     {'label':'One value (a rate, a count, the Nth thing)','leaf':('RETURNS scalar','wrap a single computed value','function-wrapped-scalar')},
     {'label':'A set of rows (filtered / ranked rows)','leaf':('RETURNS TABLE','wrap a whole result set','function-wrapped')}]}],
 'rc-decide':[
   {'q':['What do you do with the neighbour row?'],'branches':[
     {'label':'Compare to its value (bigger / smaller / equal)','leaf':('Compare to neighbour value','LAG / LEAD, then compare','rc-leaf-neighbor-value')},
     {'label':'Measure the gap or delta between them','leaf':('Gap / delta','t - LAG(t) per group','rc-leaf-gap-delta')},
     {'label':'Detect a fixed-length run of N in a row','leaf':('Fixed-length run of N','val = LAG and val = LEAD','rc-leaf-fixed-run')},
     {'label':'Pair two rows by role (start / end)','leaf':('Pair rows by role','MAX(CASE end) - MAX(CASE start)','rc-leaf-pair-role')}]}],
 'gi-decide':[
   {'q':['What column drives the run — an id (integer) or a date?'],'branches':[
     {'label':'Consecutive integers','leaf':('Consecutive integer ids','id - ROW_NUMBER()','gi-leaf-int')},
     {'label':'Dates / a timeline','down':True},
     {'label':"No run — I'm just comparing each row to its neighbour",'leaf':('Adjacency & gap checks','LAG / LEAD or self-join (within N days, biggest gap)','rc-decide')}]},
   {'q':['Whose streaks? A separate date line per entity, or ONE shared timeline?'],
    'sub':"The ENTITY is the thing that gets its OWN independent date line (e.g. each student). A status / label like submitted vs revised is NOT the entity — it just segments one shared timeline. Columns that never appear in the output (here student_id) are passengers, not the entity.",
    'branches':[
     {'label':'Each entity on its OWN date line (per-student / per-account streaks)','leaf':('Per-entity island timelines','ROW_NUMBER PARTITION BY entity  -  ROW_NUMBER PARTITION BY entity, status','gi-leaf-entity')},
     {'label':'ONE shared timeline of all rows (optionally split by a status/label)','down':True}]},
   {'q':['On that shared timeline, must the run be CALENDAR-consecutive, or just consecutive in the data sequence?'],
    'sub':"Calendar-consecutive = every day must be present, a missing day breaks the run. Sequence-consecutive = ignore missing days; a run is broken instead by a status/label changing (e.g. submitted -> revised -> submitted).",
    'branches':[
     {'label':'Calendar-consecutive — no missing days allowed','leaf':('Calendar dates, no gaps','(date - ROW_NUMBER())::int','gi-leaf-date-nogap')},
     {'label':'Sequence-consecutive — ignore gaps, and/or break runs by a status label (submitted vs revised)','leaf':('Dates with gaps / merged states','ROW_NUMBER() OVER (whole timeline)  -  ROW_NUMBER() OVER (PARTITION BY status)','gi-leaf-date-gap')}]}],
 'aj-method':[
   {'q':['What is the rule that keeps a row?'],'branches':[
     {'label':'It appears EXACTLY N times / never a SECOND time (a count)','leaf':('Not an anti-join — use HAVING COUNT','GROUP BY the key, then HAVING COUNT(*) = N. A count threshold, NOT a no-match test.','rf-leaf-having')},
     {'label':'It never appears in the other set AT ALL (zero matches)','down':True}]},
   {'q':['Do you also need columns FROM the other table in the output?'],'branches':[
     {'label':'Yes — surface matched values, reads as a join','leaf':('LEFT JOIN … WHERE right IS NULL','keep non-matchers and expose other columns','rf-antijoin-leftnull')},
     {'label':'No — just a keep / drop test','down':True}]},
   {'q':['Could the matched key ever be NULL?'],'branches':[
     {'label':'Yes, or not sure — the NULL-safe default','leaf':('NOT EXISTS','states "keep rows where none matches"; NULL-safe','rf-antijoin-notexists')},
     {'label':'No — guaranteed NOT NULL (e.g. a PK), want the shortest','leaf':('NOT IN','shortest read; one stray NULL returns zero rows','rf-antijoin-notin')}]}],
 'do-decide':[
   {'q':['What are you doing with the date?'],'branches':[
     {'label':'Group rows into time periods (month / week / quarter)','leaf':('DATE_TRUNC cohort buckets','collapse to the period start, GROUP BY it','do-leaf-trunc')},
     {'label':'Pull out one part (weekday, year, hour)','leaf':('EXTRACT a component','EXTRACT(DOW / YEAR / HOUR ...)','do-leaf-extract')},
     {'label':'Shift a date or filter against a cutoff','leaf':('Date arithmetic','d + n days, or compare to a literal cutoff','do-leaf-arithmetic')},
     {'label':'Measure the span between two dates / times','down':True}]},
   {'q':['What unit is the span in?'],'branches':[
     {'label':'Hours / minutes (between two timestamps)','leaf':('Duration via EXTRACT EPOCH','EXTRACT(EPOCH FROM (b - a)) / 3600','do-leaf-duration')},
     {'label':'Whole days, counting both endpoints','leaf':('Inclusive day count','(end - start) + 1','do-leaf-daycount')}]}],
}
