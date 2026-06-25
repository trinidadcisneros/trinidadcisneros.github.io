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
   {'q':"What does your expected output contain? (read your columns)",
    'sub':"Point-in-time = the value that was in effect at a moment. Read your output rows to pick the shape.",
    'branches':[
     {'label':'One row per entity for EVERY day in a date range (a dense calendar) with the value in effect that day — empty days carry the last value forward, days before the first change are NULL','leaf':('Fill forward over a date spine','build the per-entity calendar, look up the latest value on/before each day (e.g. sku, date, price_in_effect)','pit-leaf-fill')},
     {'label':'One row per value with the dates it was active — a start date and an end date (valid_to = the day before the next change, NULL while still active)','leaf':('Validity intervals','LEAD the next change date, subtract a day for valid_to (e.g. sku, price, valid_from, valid_to)','pit-leaf-intervals')},
     {'label':"One row per EVENT, with the value that was true at that event's own date, pulled from a SECOND table",'leaf':('As-of join','per event, the latest history value on/before its date (e.g. sale_id, sale_date, price_at_sale)','pit-leaf-asofjoin')},
     {'label':'One row per entity — its single most recent value, with NO cutoff date','leaf':('Latest snapshot','DISTINCT ON / ROW_NUMBER newest per entity (e.g. team_id, latest_velocity)','pit-leaf-latest')},
     {'label':"One row per entity — the value as of a SINGLE cutoff date; entities with NO record by then still appear with a default / NULL (e.g. viewer_id, active_tier with 'free' for the missing)",'leaf':('Default when no history','one snapshot per entity as of the cutoff; keep no-history entities, COALESCE to a default (or NULL)','pit-leaf-default')},
     {'label':'One row per entity — the value as of a SINGLE cutoff date; entities with NO record by then are DROPPED (e.g. viewer_id, active_tier, only those with a row)','leaf':('As of a single cutoff','one snapshot per entity as of the cutoff; drop entities with no row (ROW_NUMBER rn=1 / DISTINCT ON)','pit-leaf-asof')}]}],
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
   {'q':['Top 1 per group — by a value, by a date,','or the short Postgres way?'],
    'sub':"DISTINCT ON is the Postgres one-liner for 'one row per group, the newest or highest'. Same result as the ROW_NUMBER rn=1 forms, fewer keystrokes.",
    'branches':[
     {'label':'by a date (most recent / earliest)','leaf':('Top 1 by date','most recent / earliest per group','rp-multi-top1-by-date')},
     {'label':'by a value (single winner by a metric)','leaf':('Top 1 by value','single winner by a metric','rp-multi-top1-by-value')},
     {'label':'either way, written with DISTINCT ON (Postgres shortcut)','leaf':('Top 1 with DISTINCT ON','one row per group, the Postgres one-liner','rp-multi-distincton')}]}],
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
   {'q':"Output like one row per region saying a NEW score of 720 would land at rank 4 — scoring a value that ISN'T in the table?",
    'sub':"Hypothetical-set aggregate: where a candidate value WOULD rank or stand inside each group, no row inserted (WITHIN GROUP). Not the same as ranking rows that already exist.",
    'branches':[
      {'label':'yes — as an integer rank (4th, 3rd)','leaf':('rank / dense_rank WITHIN GROUP','where a hypothetical value would rank per group, no row inserted','rp-leaf-hyp-rank')},
      {'label':'yes — as a fraction 0 to 1','leaf':('percent_rank / cume_dist WITHIN GROUP','where a hypothetical value would stand per group, as 0..1','rp-leaf-hyp-fraction')},
      {'label':'no — rank rows that already exist','down':True}]},
   step(['The MEDIAN','per group?'],'yes',('Median','middle value per group','rp-leaf-median'),'no'),
   step(['A percentile cutoff','(median, P90)?'],'yes',('PERCENTILE_CONT / DISC','one percentile value per group','rp-leaf-pct-agg'),'no'),
   step(['Top X% of existing rows','per group?'],'yes',('Window PERCENT_RANK() OVER','top fraction of rows that exist','rp-leaf-pctrank'),'no'),
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
   {'q':"What does your leaderboard column contain? (read your output)",
    'sub':"All four are the same move — split the two sides with UNION ALL, then group per team. Only the SCORING step differs; read the metric column to pick.",
    'branches':[
     {'label':'A single POINTS total (win 3, tie 1, loss 0)','leaf':('Soccer points','SUM(CASE 3 / 1 / 0) per team (e.g. team, points)','ml-leaf-points')},
     {'label':'Separate WINS / LOSSES / TIES count columns','leaf':('Win / loss / tie record','one conditional count per outcome (e.g. team, wins, losses, ties)','ml-leaf-winloss')},
     {'label':'GOALS FOR, GOALS AGAINST, and the difference','leaf':('Goals for / against / differential','sum own + opponent, subtract (e.g. team, goals_for, goals_against, goal_diff)','ml-leaf-gfga')},
     {'label':'Just a TOTAL of one per-side stat (shots, minutes) — no win/loss','leaf':('Sum a column per side','SUM one stat after the split (e.g. team, total_shots)','ml-leaf-sumcol')}]}],
 'pop-decide':[
   {'q':"What does the comparison look at? (read the question)",
    'sub':"All four bucket by period with DATE_TRUNC and aggregate first - the comparison step is what differs.",
    'branches':[
     {'label':'the PREVIOUS period - last month / week / quarter / year','leaf':('Prior-period delta (MoM / WoW / QoQ / YoY)','LAG one period, then the change and % change (period, revenue, mom_change, mom_pct)','pop-leaf-prior')},
     {'label':'the SAME period a YEAR ago (seasonal)','leaf':('Same period last year','self-join on period minus one year (period, revenue, revenue_last_year, yoy_pct)','pop-leaf-yoy')},
     {'label':'every period, including ones with NO rows (a missing month must read 0)','leaf':('Gap-safe over a date spine','generate_series spine, COALESCE 0, then LAG so the gap is a real 0','pop-leaf-gapsafe')},
     {'label':'a SHARE of the period total alongside the change','leaf':('Share of total + period delta','SUM() OVER (PARTITION BY period) for the share, plus LAG per category','pop-leaf-share')}]}],
 'fn-family-decide':[
   {'q':"What are you working with, or what do you need to do?",
    'sub':"Pick the data type or goal - each family has its own function set.",
    'branches':[
     {'label':'TEXT: slice, split, clean, change case, pad','leaf':('String / text functions','SUBSTRING, SPLIT_PART, INITCAP, TRIM, REPLACE, LPAD','fn-string')},
     {'label':'An ARRAY column: index, length, membership, unpack','leaf':('Array functions','arr[n], ARRAY_LENGTH, ANY, UNNEST','fn-array')},
     {'label':'A DATE / timestamp: parts, truncate, format','leaf':('Date / time functions','EXTRACT, DATE_TRUNC, TO_CHAR, AGE','fn-date')},
     {'label':'Text that SHOULD be a number or date (convert it)','leaf':('Type casting & conversion','::type, TO_NUMBER, TO_DATE, NULLIF','fn-cast')},
     {'label':'NUMBERS: round, modulo, careful division','leaf':('Numeric / math functions','ROUND, CEIL / FLOOR, MOD, the 7/2 = 3 trap','fn-numeric')},
     {'label':'Branch on a condition, or handle NULLs','leaf':('Conditional & NULL handling','CASE, COALESCE, NULLIF','fn-conditional')}]}],
 'fn-string-decide':[
   {'q':"What do you need to do to the text? (read the goal)",
    'sub':"Each goal maps to one function.",
    'branches':[
     {'label':'Take a piece by POSITION (start + length)','leaf':('SUBSTRING(s FROM a FOR n)','1-based slice of n characters','fn-string-ref')},
     {'label':'Take the Nth piece of a DELIMITED string','leaf':('SPLIT_PART(s, delim, n)','e.g. the domain of an email','fn-string-ref')},
     {'label':'Change CASE (title / upper / lower)','leaf':('INITCAP / UPPER / LOWER','INITCAP title-cases each word','fn-string-ref')},
     {'label':'Strip spaces or unwanted characters','leaf':('TRIM / BTRIM(s, chars)','remove padding','fn-string-ref')},
     {'label':'Swap or delete characters','leaf':('REPLACE / REGEXP_REPLACE','REPLACE(phone, dash, empty)','fn-string-ref')},
     {'label':'Find WHERE a substring sits','leaf':('POSITION(sub IN s)','1-based index, 0 if absent','fn-string-ref')},
     {'label':'Glue values together','leaf':('CONCAT_WS(sep, ...) or ||','join, optionally with a separator','fn-string-ref')},
     {'label':'Pad to a fixed width','leaf':('LPAD / RPAD','LPAD(seven, 3, zero) gives 007','fn-string-ref')}]}],
 'fn-array-decide':[
   {'q':"What do you need from the array?",
    'sub':"Postgres arrays are 1-based.",
    'branches':[
     {'label':'One specific element','leaf':('arr[n]','1-based index','fn-array-ref')},
     {'label':'How many elements','leaf':('ARRAY_LENGTH(arr, 1)','length along dimension 1','fn-array-ref')},
     {'label':'Whether a value is in it','leaf':('x = ANY(arr), @>, &&','membership / contains-all / overlap','fn-array-ref')},
     {'label':'One row per element','leaf':('UNNEST(arr)','expand the array into rows','fn-array-ref')},
     {'label':'Convert array to or from text','leaf':('ARRAY_TO_STRING / STRING_TO_ARRAY','join / split','fn-array-ref')}]}],
 'fn-date-decide':[
   {'q':"What do you need from the date?",
    'sub':"Trap: EXTRACT returns a NUMBER; DATE_TRUNC returns a truncated TIMESTAMP.",
    'branches':[
     {'label':'A numeric part (month, year, day of week)','leaf':('EXTRACT(part FROM ts)','returns a number','fn-date-ref')},
     {'label':'Bucket to the start of month / week / quarter','leaf':('DATE_TRUNC(unit, ts)','returns a truncated timestamp','fn-date-ref')},
     {'label':'How far apart two dates are','leaf':('AGE(a, b) or date - date','interval, or an integer day count','fn-date-ref')},
     {'label':'Shift a date by an amount','leaf':('date + INTERVAL','add / subtract days, months','fn-date-ref')},
     {'label':'Format the date as text','leaf':('TO_CHAR(ts, fmt)','e.g. YYYY-MM','fn-date-ref')}]}],
 'fn-cast-decide':[
   {'q':"What is stored, and what should it be?",
    'sub':"Most cleaning is text-into-a-real-type.",
    'branches':[
     {'label':'A clean value, just the wrong type','leaf':('x::type or CAST(x AS type)','42 from the text 42','fn-cast-ref')},
     {'label':'Text into a DATE (custom format)','leaf':('TO_DATE(s, fmt)','parse DD.MM.YYYY etc.','fn-cast-ref')},
     {'label':'Text with separators into a NUMBER','leaf':('TO_NUMBER(s, fmt)','reads the grouping comma','fn-cast-ref')},
     {'label':'A number into formatted TEXT','leaf':('TO_CHAR(n, fmt)','money / padding masks','fn-cast-ref')},
     {'label':'Blank strings that should be NULL','leaf':('NULLIF(col, empty) / COALESCE','empty to NULL, or fill a default','fn-cast-ref')}]}],
 'fn-numeric-decide':[
   {'q':"What do you need to do to the number?",
    'sub':"Watch integer division: 7/2 = 3, not 3.5.",
    'branches':[
     {'label':'Round to N decimals','leaf':('ROUND(n, d)','3.14159 to 3.14','fn-numeric-ref')},
     {'label':'Up or down to a whole number','leaf':('CEIL / FLOOR','round up / down','fn-numeric-ref')},
     {'label':'Cut decimals without rounding','leaf':('TRUNC(n, d)','4.78 to 4.7','fn-numeric-ref')},
     {'label':'Remainder / is-it-divisible','leaf':('MOD(a, b)','even when MOD(qty, 2) = 0','fn-numeric-ref')},
     {'label':'Divide and keep the fraction','leaf':('a::numeric / b','cast first so it is not truncated','fn-numeric-ref')},
     {'label':'Biggest / smallest of several values','leaf':('GREATEST / LEAST','across columns, skips NULL','fn-numeric-ref')}]}],
 'fn-conditional-decide':[
   {'q':"What is the conditional goal?",
    'sub':"Branch a value, or tame a NULL.",
    'branches':[
     {'label':'Map ranges or categories to labels','leaf':('CASE WHEN ... THEN ... END','grade bands, buckets','fn-conditional-ref')},
     {'label':'Fill a NULL with a default','leaf':('COALESCE(a, b, ...)','first non-NULL value','fn-conditional-ref')},
     {'label':'Turn a specific value into NULL','leaf':('NULLIF(a, b)','also guards divide-by-zero','fn-conditional-ref')},
     {'label':'Pick max / min ignoring NULLs','leaf':('GREATEST / LEAST','row-wise across arguments','fn-conditional-ref')}]}],
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
   {'q':"What does your expected output contain? (read your columns)",
    'sub':"A SEGMENT = back-to-back rows collapsed into one. Match your output columns to a shape below. An id that only NAMES a row or entity is not what forms the segment — it is either the per-entity split or a passenger.",
    'branches':[
     {'label':'An identifier + a date range (start & end), with or without a status — each identifier on its own timeline','leaf':('Per-entity segments','one row per back-to-back segment, per identifier (e.g. inquiry_id, status, period_start, period_end)','gi-leaf-entity')},
     {'label':'A start and end of plain consecutive whole numbers (no dates)','leaf':('Consecutive number segments','collapse 1,2,3 then 5,6 into start/end ids','gi-leaf-int')},
     {'label':'Just a list of identifiers — the ones with a run of at least N days in a row (no start/end shown)','leaf':('Streak membership (at least N in a row)','dedupe the days, group each segment, keep entities with COUNT >= N','gi-leaf-streak')},
     {'label':"One row per original event with a neighbour number added (days since the previous row, a gap size, a \"new group\" flag) — rows are NOT merged",'leaf':('Neighbour comparison (not segments)','LAG / LEAD or a self-join; nothing collapses into ranges','rc-decide')},
     {'label':'A status/label + a date range on ONE shared timeline (no per-row identifier)','down':True}]},
   {'q':"On that one shared timeline, must every calendar day be present, or do you ignore missing days / split when the status changes?",
    'sub':"Calendar-consecutive = a missing day ends the segment. Sequence-consecutive = ignore missing days; a status/label change ends it instead.",
    'branches':[
     {'label':'Every calendar day must be present — a missing day ends the segment','leaf':('Calendar-consecutive segments','(date - ROW_NUMBER())::int','gi-leaf-date-nogap')},
     {'label':'Ignore missing days, or split when a status/label changes','leaf':('Sequence segments / status breaks','ROW_NUMBER() OVER (whole timeline) - ROW_NUMBER() OVER (PARTITION BY status)','gi-leaf-date-gap')}]}],
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
