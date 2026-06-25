"""Full treatment for the Period-over-period growth container (period_over_period qtype).
Replaces the 4 stub leaves (pop-leaf-prior / -yoy / -gapsafe / -share) with, for each:
a fresh template + a Postgres-verified worked card + a step-by-step walkthrough accordion.
Mirrors build_ml_leaves.py. Idempotent-ish (re-run replaces the leaves again) + balance-checked.
Run:  python3 build_pop_leaves.py
"""
import re, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))


def esc_sql(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


# ---------- shared input schema ----------
SALES_COLS = [('sale_id', 'INT'), ('sale_date', 'DATE'), ('amount', 'INT')]
SALES_CAT_COLS = [('sale_id', 'INT'), ('category', 'TEXT'), ('sale_date', 'DATE'), ('amount', 'INT')]

PRIOR_ROWS = [[1, '2024-01-15', 200], [2, '2024-02-15', 250], [3, '2024-03-15', 200], [4, '2024-04-15', 300]]
YOY_ROWS = [[1, '2023-01-10', 100], [2, '2023-02-10', 150], [3, '2023-03-10', 120],
            [4, '2024-01-10', 130], [5, '2024-02-10', 150], [6, '2024-03-10', 180]]
GAP_ROWS = [[1, '2024-01-10', 100], [2, '2024-02-10', 120], [3, '2024-04-10', 200]]  # March missing
SHARE_ROWS = [[1, 'A', '2024-01-10', 60], [2, 'B', '2024-01-10', 40],
              [3, 'A', '2024-02-10', 90], [4, 'B', '2024-02-10', 30]]

SALES_IN = {'name': 'sales', 'cols': SALES_COLS, 'headers': ['sale_id', 'sale_date', 'amount'], 'rows': PRIOR_ROWS}
SALES_YOY_IN = dict(SALES_IN, rows=YOY_ROWS)
SALES_GAP_IN = dict(SALES_IN, rows=GAP_ROWS)
SALES_CAT_IN = {'name': 'sales', 'cols': SALES_CAT_COLS, 'headers': ['sale_id', 'category', 'sale_date', 'amount'], 'rows': SHARE_ROWS}


# ---------- worked cards ----------
CARD_PRIOR = {
    'diff': 'Easy', 'color': '#2e7d32', 'title': 'Month-over-Month Revenue Change',
    'excerpt': "Monthly revenue with each month's change and % change vs the month before.",
    'prompt': ["<code>sales</code> has one row per sale with a <code>sale_date</code> and an <code>amount</code>.",
               "Bucket sales into calendar months and total the amount per month.",
               "For each month return <code>period</code>, <code>revenue</code>, the previous month's <code>prev_revenue</code>, the <code>mom_change</code> (absolute), and the <code>mom_pct</code> (rounded to 1 dp). The first month has no prior month, so those are NULL. Order by period.",
               "Swap <code>'month'</code> for <code>'week'</code> / <code>'quarter'</code> / <code>'year'</code> to get WoW / QoQ / YoY."],
    'inputs': [SALES_IN], 'exp_headers': ['period', 'revenue', 'prev_revenue', 'mom_change', 'mom_pct'],
    'exp_rows': [['2024-01-01', 200, None, None, None],
                 ['2024-02-01', 250, 200, 50, '25.0'],
                 ['2024-03-01', 200, 250, -50, '-20.0'],
                 ['2024-04-01', 300, 200, 100, '50.0']],
    'sol_comment': ("Bucket into months and total (the CTE), then LAG one row to pull the prior month onto each row.\n"
                    "Subtract for the absolute change; divide by the prior value for the % change, guarding /0 with NULLIF.\n"
                    "The earliest month has no prior row so LAG is NULL and the change columns are NULL. Verified."),
    'sol_sql': ("WITH monthly AS (\n"
                "    SELECT date_trunc('month', sale_date)::date AS period,\n"
                "           SUM(amount) AS revenue\n"
                "    FROM sales\n"
                "    GROUP BY 1\n"
                ")\n"
                "SELECT period,\n"
                "       revenue,\n"
                "       LAG(revenue) OVER (ORDER BY period) AS prev_revenue,\n"
                "       revenue - LAG(revenue) OVER (ORDER BY period) AS mom_change,\n"
                "       ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY period))\n"
                "             / NULLIF(LAG(revenue) OVER (ORDER BY period), 0), 1) AS mom_pct\n"
                "FROM monthly\n"
                "ORDER BY period;"),
}

CARD_YOY = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Year-over-Year by Month (same month last year)',
    'excerpt': "Compare each month to the SAME month one year earlier, not to the previous month.",
    'prompt': ["<code>sales</code> spans two years with the same calendar months in each.",
               "Total revenue per month, then compare each month to the same month one year before.",
               "Return <code>period</code>, <code>revenue</code>, <code>revenue_last_year</code>, and <code>yoy_pct</code> (1 dp). Months in the first year have no prior-year match, so those are NULL. Order by period."],
    'inputs': [SALES_YOY_IN], 'exp_headers': ['period', 'revenue', 'revenue_last_year', 'yoy_pct'],
    'exp_rows': [['2023-01-01', 100, None, None],
                 ['2023-02-01', 150, None, None],
                 ['2023-03-01', 120, None, None],
                 ['2024-01-01', 130, 100, '30.0'],
                 ['2024-02-01', 150, 150, '0.0'],
                 ['2024-03-01', 180, 120, '50.0']],
    'sol_comment': ("Same monthly bucket, then self-join it to itself on period = the other row's period plus a year.\n"
                    "Joining on c.period - INTERVAL '1 year' is gap-safe (it matches by calendar date, not by row position),\n"
                    "so it keeps working even if some months are missing. The first year has no prior-year twin -> NULL. Verified."),
    'sol_sql': ("WITH monthly AS (\n"
                "    SELECT date_trunc('month', sale_date)::date AS period,\n"
                "           SUM(amount) AS revenue\n"
                "    FROM sales\n"
                "    GROUP BY 1\n"
                ")\n"
                "SELECT c.period,\n"
                "       c.revenue,\n"
                "       p.revenue AS revenue_last_year,\n"
                "       ROUND(100.0 * (c.revenue - p.revenue) / NULLIF(p.revenue, 0), 1) AS yoy_pct\n"
                "FROM monthly c\n"
                "LEFT JOIN monthly p ON p.period = c.period - INTERVAL '1 year'\n"
                "ORDER BY c.period;"),
}

CARD_GAP = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Gap-Safe Month-over-Month (a missing month must read 0)',
    'excerpt': "March has no sales. A correct MoM must show March = 0, not skip from February to April.",
    'prompt': ["<code>sales</code> has rows in January, February, and April &mdash; <strong>March is missing entirely</strong>.",
               "Report revenue for EVERY month in the range, with a month that has no sales shown as 0 (not skipped).",
               "Then the month-over-month change must be correct across the gap: April's previous month is March (0), not February.",
               "Return <code>period</code>, <code>revenue</code>, <code>prev_revenue</code>, <code>mom_change</code>, ordered by period."],
    'inputs': [SALES_GAP_IN], 'exp_headers': ['period', 'revenue', 'prev_revenue', 'mom_change'],
    'exp_rows': [['2024-01-01', 100, None, None],
                 ['2024-02-01', 120, 100, 20],
                 ['2024-03-01', 0, 120, -120],
                 ['2024-04-01', 200, 0, 200]],
    'sol_comment': ("The trap: a plain GROUP BY month produces no March row, so LAG jumps from February straight to April\n"
                    "and reports April's change as 80 instead of 200 -- the dip to 0 is invisible. Fix: build a COMPLETE month\n"
                    "spine with generate_series between the data's min and max month, LEFT JOIN the actuals, COALESCE to 0,\n"
                    "and ONLY THEN LAG. Now March exists as a real 0 row and every delta is correct. Verified."),
    'sol_sql': ("WITH bounds AS (\n"
                "    SELECT date_trunc('month', MIN(sale_date)) AS lo,\n"
                "           date_trunc('month', MAX(sale_date)) AS hi\n"
                "    FROM sales\n"
                "),\n"
                "spine AS (\n"
                "    SELECT gs::date AS period\n"
                "    FROM bounds, generate_series(lo, hi, INTERVAL '1 month') AS gs\n"
                "),\n"
                "monthly AS (\n"
                "    SELECT s.period, COALESCE(SUM(x.amount), 0) AS revenue\n"
                "    FROM spine s\n"
                "    LEFT JOIN sales x ON date_trunc('month', x.sale_date) = s.period\n"
                "    GROUP BY s.period\n"
                ")\n"
                "SELECT period,\n"
                "       revenue,\n"
                "       LAG(revenue) OVER (ORDER BY period) AS prev_revenue,\n"
                "       revenue - LAG(revenue) OVER (ORDER BY period) AS mom_change\n"
                "FROM monthly\n"
                "ORDER BY period;"),
}

CARD_SHARE = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Share of Month + Month-over-Month, per Category',
    'excerpt': "Each category's share of the month's total alongside its own month-over-month change.",
    'prompt': ["<code>sales</code> has a <code>category</code>, a <code>sale_date</code>, and an <code>amount</code>.",
               "Per category per month, total the revenue.",
               "On each row show the category's <code>pct_of_month</code> (its share of that month's total, 1 dp) AND its own <code>cat_mom_change</code> vs the same category last month.",
               "Return <code>category</code>, <code>period</code>, <code>revenue</code>, <code>pct_of_month</code>, <code>cat_mom_change</code>, ordered by period then category."],
    'inputs': [SALES_CAT_IN], 'exp_headers': ['category', 'period', 'revenue', 'pct_of_month', 'cat_mom_change'],
    'exp_rows': [['A', '2024-01-01', 60, '60.0', None],
                 ['B', '2024-01-01', 40, '40.0', None],
                 ['A', '2024-02-01', 90, '75.0', 30],
                 ['B', '2024-02-01', 30, '25.0', -10]],
    'sol_comment': ("Two window functions on the same per-(category, month) aggregate. SUM(revenue) OVER (PARTITION BY period)\n"
                    "with NO order by is the whole-month total on every row -> divide for the share. LAG partitioned BY category,\n"
                    "ordered by period, gives each category its own month-over-month delta. The shares within a month sum to 100%. Verified."),
    'sol_sql': ("WITH monthly AS (\n"
                "    SELECT category,\n"
                "           date_trunc('month', sale_date)::date AS period,\n"
                "           SUM(amount) AS revenue\n"
                "    FROM sales\n"
                "    GROUP BY 1, 2\n"
                ")\n"
                "SELECT category,\n"
                "       period,\n"
                "       revenue,\n"
                "       ROUND(100.0 * revenue / SUM(revenue) OVER (PARTITION BY period), 1) AS pct_of_month,\n"
                "       revenue - LAG(revenue) OVER (PARTITION BY category ORDER BY period) AS cat_mom_change\n"
                "FROM monthly\n"
                "ORDER BY period, category;"),
}


# ---------- templates (reuse the verified canonical SQL) ----------
def tmpl(tid, tmpl_title, use_when, steps, sql):
    lis = ''.join('\n                      <li>%s</li>' % s for s in steps)
    return ('''<div id="%s" class="problem-card collapsed" style="margin: 0 0 16px 0; border-left-color:#6a1b9a;">
                  <div class="problem-card-header">
                    <h3 class="problem-card-title" style="margin: 0; display: flex; align-items: center; gap: 15px;">
                      <span style="display: inline-block; background-color: #6a1b9a; color: white; padding: 4px 10px; border-radius: 3px; font-size: 1.328rem; font-weight: 600;">Template</span>
                      %s
                    </h3>
                    <button class="tpl-copy" type="button" onclick="event.stopPropagation(); copyTplCode(this);">Copy</button>
                    <span class="problem-toggle">&#9660;</span>
                  </div>
                  <div class="problem-card-excerpt"><p style="margin:0;">%s</p></div>
                  <div class="problem-card-content">
                    <p style="margin:0 0 6px;"><strong>What this template does, step by step:</strong></p>
                    <ol style="margin:0 0 10px 18px; line-height:1.7;">%s
                    </ol>
                    <pre style="margin:0 0 6px; background:#1e1e1e; color:#d4d4d4; padding:10px 12px; border-radius:4px; font-size:1.15rem; line-height:1.5; white-space:pre-wrap;"><code>%s</code></pre>
                  </div>
                </div>''' % (tid, tmpl_title, use_when, lis, esc_sql(sql)))


T_PRIOR = tmpl('pop-tmpl-prior', 'Prior-period delta template',
               "Use when: each period is compared to the one immediately before it. Swap 'month' for week / quarter / year.",
               ["Bucket rows into periods with <code>DATE_TRUNC</code> and aggregate the metric per period.",
                "<code>LAG(metric) OVER (ORDER BY period)</code> pulls the previous period's value onto each row.",
                "Subtract for the absolute change; divide with <code>NULLIF(prev,0)</code> for the % change. The first period has no prior, so its delta is NULL."],
               CARD_PRIOR['sol_sql'])
T_YOY = tmpl('pop-tmpl-yoy', 'Same period last year template',
             "Use when: the comparison is seasonal (this December vs last December). Self-join the period series one year back.",
             ["Build the same DATE_TRUNC + aggregate CTE as month over month.",
              "Self-join it to itself on <code>p.period = c.period - INTERVAL '1 year'</code> so each row meets its prior-year twin.",
              "The first year has no prior-year match, so those rows are NULL. <code>LAG(metric, 12)</code> only works if every month is present."],
             CARD_YOY['sol_sql'])
T_GAP = tmpl('pop-tmpl-gapsafe', 'Gap-safe template',
             "Use when: some periods may have no rows. Without a spine, LAG jumps over the gap and the delta is wrong.",
             ["<code>generate_series</code> between the data's min and max period builds a complete spine (never CURRENT_DATE).",
              "LEFT JOIN the actuals onto the spine and <code>COALESCE</code> the metric to 0 so the empty period becomes a real 0 row.",
              "Only THEN apply LAG, so the period after a gap correctly compares against 0 instead of skipping back."],
             CARD_GAP['sol_sql'])
T_SHARE = tmpl('pop-tmpl-share', 'Share of total + period delta template',
               "Use when: the question stacks share-of-total with the period change (a common multi-part assessment ask).",
               ["Aggregate per (category, period).",
                "<code>SUM(metric) OVER (PARTITION BY period)</code> (no ORDER BY) is the period total; divide for each row's share.",
                "<code>LAG(metric) OVER (PARTITION BY category ORDER BY period)</code> gives each category its own period delta. Shares within a period sum to ~100%."],
               CARD_SHARE['sol_sql'])


# ---------- Postgres verify (NULL-aware) + walkthrough ----------
def _lit(v):
    s = str(v)
    return s if re.match(r'^-?\d+$', s) else "'" + s.replace("'", "''") + "'"


def _pg_rows(srv, q, ncols):
    out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + q)
    rows = []
    for l in out.strip().splitlines():
        if 'format is' in l or 'separator is' in l:
            continue
        if l.count('|') != ncols - 1:
            continue
        rows.append([None if c == '' else c for c in l.split('|')])
    return rows


def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in card['inputs']:
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], ', '.join('%s %s' % (n, t) for n, t in inp['cols'])))
            for row in inp['rows']:
                srv.psql('INSERT INTO %s VALUES (%s);' % (inp['name'], ', '.join(_lit(v) for v in row)))
        got = _pg_rows(srv, card['sol_sql'], len(card['exp_headers']))
        got = [tuple('' if c is None else c for c in r) for r in got]
        exp = [tuple('' if v is None else str(v) for v in r) for r in card['exp_rows']]
        return got == exp, got, exp
    finally:
        srv.cleanup()


def accordion_step(title, excerpt, inner, mtop=12, border='#1565c0', cid=None):
    idattr = (' id="%s"' % cid) if cid else ''
    return ('<div%s class="problem-card collapsed" style="margin: %spx 0 0; border-left:4px solid %s;">'
            '<div class="problem-card-header"><h3 class="problem-card-title" style="margin:0; font-size:1.15rem;">%s</h3><span class="problem-toggle">&#9660;</span></div>'
            '<div class="problem-card-excerpt"><p style="margin:0;">%s</p></div>'
            '<div class="problem-card-content">%s</div></div>' % (idattr, mtop, border, title, excerpt, inner))


def build_walkthroughs():
    """Compute every step table in real Postgres; return {leaf_id: walkthrough_html}."""
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    DT = eb.data_table
    out = {}
    try:
        # ----- prior_period -----
        srv.psql('CREATE TABLE sales (sale_id INT, sale_date DATE, amount INT);')
        for r in PRIOR_ROWS:
            srv.psql("INSERT INTO sales VALUES (%d,'%s',%d);" % (r[0], r[1], r[2]))
        s1 = _pg_rows(srv, "SELECT date_trunc('month',sale_date)::date AS period, SUM(amount) AS revenue FROM sales GROUP BY 1 ORDER BY 1;", 2)
        s2 = _pg_rows(srv, "WITH m AS (SELECT date_trunc('month',sale_date)::date AS period, SUM(amount) AS revenue FROM sales GROUP BY 1) SELECT period,revenue,LAG(revenue) OVER (ORDER BY period) AS prev_revenue FROM m ORDER BY period;", 3)
        s3 = _pg_rows(srv, CARD_PRIOR['sol_sql'], 5)
        intro = ('<p style="margin:0 0 8px;">Four months of revenue. Bucket, look back one period, subtract.</p>'
                 '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>sales</code></strong>:</p>' + DT(SALES_IN['headers'], PRIOR_ROWS))
        st1 = accordion_step('Step 1 &mdash; bucket into months and total', 'DATE_TRUNC the date to the first of the month, SUM per month.',
                             '<p style="margin:0 0 6px;">One row per month:</p>' + DT(['period', 'revenue'], s1))
        st2 = accordion_step('Step 2 &mdash; look back one month with LAG', 'LAG(revenue) OVER (ORDER BY period) copies the previous month onto each row.',
                             '<p style="margin:0 0 6px;">January has no prior month, so its prev is NULL:</p>' + DT(['period', 'revenue', 'prev_revenue'], s2), border='#2e7d32')
        st3 = accordion_step('Step 3 &mdash; subtract for the change, divide for the %', 'mom_change = revenue - prev; mom_pct = 100 * change / prev (NULLIF guards /0).',
                             '<p style="margin:0 0 6px;">Feb +50 (+25%), Mar -50 (-20%), Apr +100 (+50%):</p>' + DT(CARD_PRIOR['exp_headers'], s3))
        out['pop-leaf-prior'] = accordion_step('&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
                                               'Bucket &rarr; LAG one period &rarr; subtract, step by step.', intro + st1 + st2 + st3, mtop=14, border='#6a1b9a', cid='pop-walk-prior')
        srv.psql('DROP TABLE sales;')

        # ----- same_period_last_year -----
        srv.psql('CREATE TABLE sales (sale_id INT, sale_date DATE, amount INT);')
        for r in YOY_ROWS:
            srv.psql("INSERT INTO sales VALUES (%d,'%s',%d);" % (r[0], r[1], r[2]))
        y1 = _pg_rows(srv, "SELECT date_trunc('month',sale_date)::date AS period, SUM(amount) AS revenue FROM sales GROUP BY 1 ORDER BY 1;", 2)
        y2 = _pg_rows(srv, "WITH m AS (SELECT date_trunc('month',sale_date)::date AS period, SUM(amount) AS revenue FROM sales GROUP BY 1) SELECT c.period AS this_month, c.revenue, (c.period - INTERVAL '1 year')::date AS looks_for, p.revenue AS revenue_last_year FROM m c LEFT JOIN m p ON p.period=c.period-INTERVAL '1 year' ORDER BY c.period;", 4)
        y3 = _pg_rows(srv, CARD_YOY['sol_sql'], 4)
        intro = ('<p style="margin:0 0 8px;">The same three months in two years. Each 2024 month looks back to its 2023 twin.</p>'
                 '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>sales</code></strong>:</p>' + DT(SALES_IN['headers'], YOY_ROWS))
        st1 = accordion_step('Step 1 &mdash; bucket into months', 'SUM per month across both years.',
                             '<p style="margin:0 0 6px;">Six monthly totals:</p>' + DT(['period', 'revenue'], y1))
        st2 = accordion_step('Step 2 &mdash; self-join to the same month last year', "Join the table to itself on p.period = this month minus one year.",
                             '<p style="margin:0 0 6px;"><code>looks_for</code> is the month one year back; 2023 rows find no twin (NULL):</p>' + DT(['this_month', 'revenue', 'looks_for', 'revenue_last_year'], y2), border='#2e7d32')
        st3 = accordion_step('Step 3 &mdash; year-over-year %', '100 * (this year - last year) / last year.',
                             '<p style="margin:0 0 6px;">Jan +30%, Feb 0%, Mar +50%:</p>' + DT(CARD_YOY['exp_headers'], y3))
        out['pop-leaf-yoy'] = accordion_step('&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
                                             'Bucket &rarr; self-join one year back &rarr; year-over-year %.', intro + st1 + st2 + st3, mtop=14, border='#6a1b9a', cid='pop-walk-yoy')
        srv.psql('DROP TABLE sales;')

        # ----- gap_safe -----
        srv.psql('CREATE TABLE sales (sale_id INT, sale_date DATE, amount INT);')
        for r in GAP_ROWS:
            srv.psql("INSERT INTO sales VALUES (%d,'%s',%d);" % (r[0], r[1], r[2]))
        g_naive = _pg_rows(srv, "WITH m AS (SELECT date_trunc('month',sale_date)::date AS period, SUM(amount) AS revenue FROM sales GROUP BY 1) SELECT period,revenue,LAG(revenue) OVER (ORDER BY period) AS prev_revenue, revenue-LAG(revenue) OVER (ORDER BY period) AS mom_change FROM m ORDER BY period;", 4)
        g1 = _pg_rows(srv, "SELECT gs::date AS period FROM (SELECT date_trunc('month',MIN(sale_date)) lo, date_trunc('month',MAX(sale_date)) hi FROM sales) b, generate_series(b.lo,b.hi,INTERVAL '1 month') gs ORDER BY 1;", 1)
        g2 = _pg_rows(srv, "WITH bounds AS (SELECT date_trunc('month',MIN(sale_date)) lo, date_trunc('month',MAX(sale_date)) hi FROM sales), spine AS (SELECT gs::date AS period FROM bounds, generate_series(lo,hi,INTERVAL '1 month') gs) SELECT s.period, COALESCE(SUM(x.amount),0) AS revenue FROM spine s LEFT JOIN sales x ON date_trunc('month',x.sale_date)=s.period GROUP BY s.period ORDER BY s.period;", 2)
        g3 = _pg_rows(srv, CARD_GAP['sol_sql'], 4)
        intro = ('<p style="margin:0 0 8px;">Sales in Jan, Feb, and Apr &mdash; <strong>March is missing</strong>. A plain GROUP BY drops March, so LAG would compare April to February:</p>'
                 '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>sales</code></strong>:</p>' + DT(SALES_IN['headers'], GAP_ROWS)
                 + '<p style="margin:8px 0 6px; padding:8px 12px; background:#fff3e0; border-left:4px solid #e65100;"><strong>The wrong answer</strong> (no spine): April&rsquo;s previous is February, so the change reads +80 and the dip to 0 vanishes:</p>' + DT(['period', 'revenue', 'prev_revenue', 'mom_change'], g_naive))
        st1 = accordion_step('Step 1 &mdash; build a complete month spine', 'generate_series from the min to the max month gives every month, present or not.',
                             '<p style="margin:0 0 6px;">All four months exist now, including March:</p>' + DT(['period'], g1))
        st2 = accordion_step('Step 2 &mdash; LEFT JOIN actuals, COALESCE to 0', 'Attach real revenue to the spine; months with no sales become a real 0 row.',
                             '<p style="margin:0 0 6px;">March is a genuine 0, not a missing row:</p>' + DT(['period', 'revenue'], g2), border='#2e7d32')
        st3 = accordion_step('Step 3 &mdash; now LAG is gap-correct', 'April&rsquo;s previous month is March (0), so the change is +200 and the dip is visible.',
                             '<p style="margin:0 0 6px;">Correct deltas across the gap:</p>' + DT(CARD_GAP['exp_headers'], g3))
        out['pop-leaf-gapsafe'] = accordion_step('&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
                                                 'Spine &rarr; COALESCE 0 &rarr; LAG, so a missing month reads 0.', intro + st1 + st2 + st3, mtop=14, border='#6a1b9a', cid='pop-walk-gapsafe')
        srv.psql('DROP TABLE sales;')

        # ----- pct_of_total_pop -----
        srv.psql('CREATE TABLE sales (sale_id INT, category TEXT, sale_date DATE, amount INT);')
        for r in SHARE_ROWS:
            srv.psql("INSERT INTO sales VALUES (%d,'%s','%s',%d);" % (r[0], r[1], r[2], r[3]))
        h1 = _pg_rows(srv, "SELECT category, date_trunc('month',sale_date)::date AS period, SUM(amount) AS revenue FROM sales GROUP BY 1,2 ORDER BY 2,1;", 3)
        h2 = _pg_rows(srv, "WITH m AS (SELECT category, date_trunc('month',sale_date)::date AS period, SUM(amount) AS revenue FROM sales GROUP BY 1,2) SELECT category,period,revenue,SUM(revenue) OVER (PARTITION BY period) AS month_total, ROUND(100.0*revenue/SUM(revenue) OVER (PARTITION BY period),1) AS pct_of_month FROM m ORDER BY period,category;", 5)
        h3 = _pg_rows(srv, CARD_SHARE['sol_sql'], 5)
        intro = ('<p style="margin:0 0 8px;">Two categories over two months. Each row needs both its share of the month and its own month-over-month change.</p>'
                 '<p style="margin:0 0 6px;"><strong>The data &mdash; <code>sales</code></strong>:</p>' + DT(SALES_CAT_IN['headers'], SHARE_ROWS))
        st1 = accordion_step('Step 1 &mdash; aggregate per category per month', 'GROUP BY category, month.',
                             '<p style="margin:0 0 6px;">One row per category per month:</p>' + DT(['category', 'period', 'revenue'], h1))
        st2 = accordion_step('Step 2 &mdash; share of the month total (window SUM)', 'SUM(revenue) OVER (PARTITION BY period) is the whole-month total on every row; divide for the share.',
                             '<p style="margin:0 0 6px;">Shares within a month sum to 100%:</p>' + DT(['category', 'period', 'revenue', 'month_total', 'pct_of_month'], h2), border='#2e7d32')
        st3 = accordion_step('Step 3 &mdash; each category&rsquo;s month-over-month delta', 'LAG partitioned BY category, ordered by period.',
                             '<p style="margin:0 0 6px;">A +30, B -10 from January to February:</p>' + DT(CARD_SHARE['exp_headers'], h3))
        out['pop-leaf-share'] = accordion_step('&#128270; Walk through it with the example data <span style="color:#64748b; font-weight:400; font-size:0.95rem;">(click to learn more)</span>',
                                               'Aggregate &rarr; window share &rarr; per-category LAG delta.', intro + st1 + st2 + st3, mtop=14, border='#6a1b9a', cid='pop-walk-share')
        srv.psql('DROP TABLE sales;')
    finally:
        srv.cleanup()
    return out


# ---------- leaf assembly ----------
def leaf(lid, title, subtype, tail, tmpl_html, card, walk):
    label = '<code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">nb01 qtype: period_over_period (%s)</code>' % subtype
    return ('''<div id="%(lid)s" class="problem-card collapsed qtype-group">
                <div class="problem-card-header"><h3 class="problem-card-title" style="margin: 0;">%(title)s <span class="count-badge">1 problem</span></h3><span class="problem-toggle">&#9660;</span></div>
                <div class="problem-card-excerpt"><p style="margin: 0;">%(label)s &mdash; %(tail)s</p></div>
                <div class="problem-card-content">
                %(tmpl)s
              %(card)s
              %(walk)s
                </div>
              </div>''' % {'lid': lid, 'title': title, 'label': label, 'tail': tail,
                           'tmpl': tmpl_html, 'card': eb.build_card(card), 'walk': walk})


def replace_leaf(text, lid, new_html):
    s = text.find('<div id="%s"' % lid)
    if s < 0:
        raise SystemExit('leaf not found: ' + lid)
    depth = 0
    e = None
    for m in re.finditer(r'<(/?)div\b', text[s:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            e = text.find('>', s + m.start()) + 1
            break
    if e is None:
        raise SystemExit('could not balance leaf: ' + lid)
    return text[:s] + new_html + text[e:]


def main():
    cards = [CARD_PRIOR, CARD_YOY, CARD_GAP, CARD_SHARE]
    for c in cards:
        ok, got, exp = verify_pg(c)
        print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', c['title']))
        if not ok:
            print('  GOT', got)
            print('  EXP', exp)
            raise SystemExit('verify failed; nothing written')

    walks = build_walkthroughs()
    text = open(PATH).read()
    before = eb.balance_report(text)

    leaves = {
        'pop-leaf-prior': leaf('pop-leaf-prior', 'Prior-period delta (MoM / WoW / QoQ / YoY)', 'prior_period',
                               'compare each period to the one immediately before it; swap the grain for WoW / QoQ / YoY.', T_PRIOR, CARD_PRIOR, walks['pop-leaf-prior']),
        'pop-leaf-yoy': leaf('pop-leaf-yoy', 'Same period last year (seasonal)', 'same_period_last_year',
                             'compare each month to the same month a year earlier via a self-join one year back.', T_YOY, CARD_YOY, walks['pop-leaf-yoy']),
        'pop-leaf-gapsafe': leaf('pop-leaf-gapsafe', 'Gap-safe over a date spine', 'gap_safe',
                                 'a period with no rows must read 0, not be skipped; build a full spine before LAG.', T_GAP, CARD_GAP, walks['pop-leaf-gapsafe']),
        'pop-leaf-share': leaf('pop-leaf-share', 'Share of total + period delta', 'pct_of_total_pop',
                               'each category&rsquo;s share of the period total alongside its own period delta.', T_SHARE, CARD_SHARE, walks['pop-leaf-share']),
    }
    for lid, html in leaves.items():
        text = replace_leaf(text, lid, html)

    after = eb.balance_report(text)
    print('\nBalance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('\nWROTE 4 full-treatment leaves to %s' % PATH)


if __name__ == '__main__':
    main()
