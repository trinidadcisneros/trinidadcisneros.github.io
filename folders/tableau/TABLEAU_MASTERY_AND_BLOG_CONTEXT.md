# Tableau Mastery + Blog Series Context

Portable context file. Read this first when starting the blog post project. It summarizes every Tableau topic Trinidad covered in the DataCamp "Data Analyst in Tableau" track, maps the calculation methods to their SQL and pandas equivalents, and lays out the blog series and interview prep plan.

## Who this is for
Trinidad completed the full **Data Analyst in Tableau** career track on DataCamp (July 2026). Goal now: build a data driven blog post series that (1) shows off Tableau skill for a portfolio, (2) deepens understanding, and (3) preps for a Tableau interview with technical tests on **Thursday July 9, 2026**. Calculations and dashboards are the highest priority.

## The blog series' unique angle
Explain each Tableau calculation method side by side with the equivalent **SQL** and **Python pandas** approach, so a reader (and Trinidad) understands HOW the data is transformed to reach the result, not just which buttons to click. This "three languages, one result" framing resonated strongly in earlier sessions. LOD expressions, statistics, and dashboarding are the pillars.

---

## PART 1 — Complete inventory of Tableau content mastered

### Course: Introduction to Tableau
Getting started, building/customizing visualizations, digging deeper, presenting data. Core viz building, the Marks card, Show Me, basic dashboards.

### Course: Analyzing Data in Tableau
Preparing for analysis, exploring visualizations, mapping analysis, groups/sets/parameters. Deeper analytics, spatial, and interactivity building blocks.

### Course: Creating Dashboards in Tableau
Getting started with dashboards, sharing data insights. Dashboard objects, layout, actions, publishing.

### Case Study: Analyzing Customer Churn in Tableau (Databel)
Exploratory analysis, churn patterns, visualizing analysis. Built Overview, Age & Groups, Payment & Contract, Data & International dashboards, combined into a Story. Key finding: Month-to-Month contracts are the top churn driver.

### Course: Connecting Data in Tableau
Combining and saving data, managing and connecting data. Joins, unions, blends, relationships, extracts vs live.

### Course: Data Visualization in Tableau (IMDb dataset)
- Start to Visualize: stacked bar, line, combo (dual axis bars+line), treemaps, distribution (histogram + box plot), quadrant scatter, heat map (highlight table), waterfall (running total + Gantt).
- Best Practices: pie/area, formatting, interactivity, dashboard actions (Filter/Highlight/Go to URL), Viz in Tooltip, word cloud, web action URL calc.
- Maps: point maps, filled/polygon maps, GeoJSON geometry, map layers, background layers, custom background images.
- Advanced Viz: waffle chart, DNA/dumbbell chart, sparklines, viz in tooltip, dashboard + story assembly.

### Course: Calculations in Tableau (Fitbit + retail data) — CORE FOR INTERVIEW
Four chapters. Full concept detail in PART 2 below.
1. Start to Calculate (row level vs aggregate, string/logic/null functions)
2. Level of Detail Expressions (FIXED/INCLUDE/EXCLUDE)
3. Table Calculations and Parameters
4. Time Series Analysis (date functions, seasonality, moving average, CAGR, indexed growth)

### Case Study: Analyzing Job Market Data in Tableau (DataSearch)
Exploratory analysis, market trends, dashboards and insights. 25,114 job postings, 19 columns. Built a KPI + bubble + line + box plot + area chart dashboard with filter actions.

### Course: Statistical Techniques in Tableau — CORE FOR INTERVIEW
Four chapters. Full concept detail in PART 3 below.
1. Univariate EDA (tables, bar plots, histograms, box plots)
2. Measures of spread and confidence intervals
3. Bivariate EDA (correlation, trend lines, regression)
4. Forecasting and clustering

### Course: Tableau Prep Builder (data prep and loading)
Preparing and loading data into Tableau with Prep Builder.

---

## PART 2 — Calculations reference with SQL + pandas equivalents (blog gold)

### 2.1 Calculation types
- **Row level**: computed per row, like a spreadsheet formula. SQL: an expression in SELECT. pandas: `df['a'] / df['b']`.
- **Aggregate**: SUM/AVG/COUNTD, collapses rows, recomputes per dimensions in the view. SQL: aggregate + GROUP BY. pandas: `df.groupby(dims).agg(...)`.
- Cannot mix row level and aggregate in one formula (aggregate both sides, e.g. `SUM([Distance]) / COUNTD([Activity Date])`).
- **Average of averages trap**: row level ratio then AVG (wrong) vs SUM/SUM (correct). SQL/pandas: always `SUM(x)/SUM(y)`, never `AVG(x/y)` for weighted ratios.
- `SUM` of a 1/0 condition = count of matching rows. SQL: `SUM(CASE WHEN cond THEN 1 ELSE 0 END)`. pandas: `(cond).sum()`.

### 2.2 String / logic / null functions
- Strings: `+` concatenate, SPLIT, LEFT/RIGHT/MID. SQL: `||`/CONCAT, SPLIT_PART, LEFT/RIGHT/SUBSTRING. pandas: `str.cat`, `str.split`, `str.slice`.
- Logic: IF/ELSEIF/THEN/END, IIF, CASE (exact matches only), AND/OR, `!=`/`<>`. SQL: CASE WHEN. pandas: `np.select`, `np.where`.
- Nulls: ISNULL, IFNULL, ZN (null→0), ISDATE. SQL: IS NULL, COALESCE. pandas: `isna`, `fillna`.

### 2.3 Level of Detail (LOD) expressions — THE headline blog post
Granularity = number of dimensions in view; more dims = finer detail.

- **{ FIXED [dims] : AGG(x) }** — computes at the listed dims only, IGNORES the view and dimension filters (runs early in order of operations).
  - SQL: window function `AGG(x) OVER (PARTITION BY dims)`, or a grouped subquery joined back.
  - pandas: `df.groupby(dims)['x'].transform('agg')`.
- **{ INCLUDE [dims] : AGG(x) }** — view dims PLUS the extras, then re-aggregate up (e.g. avg per customer inside region).
  - SQL/pandas: two step groupby (group finer, then aggregate coarser).
- **{ EXCLUDE [dims] : AGG(x) }** — view dims MINUS named ones (subtotals/benchmarks reusable in math).
  - SQL: window over FEWER columns than the view. pandas: window/transform over fewer keys.
- Applications: % of total (`SUM(x)/SUM({FIXED : SUM(x)})`), cohort analysis (`{FIXED [user] : MIN(order date)}`), survival curves, benchmarks with EXCLUDE + reference lines, "above benchmark?" boolean on Color.
- `ATTR()` = "all rows in this group share one value."

### 2.4 Table calculations and parameters
- Table calcs transform what is ALREADY in the view (a virtual table); LODs reach into raw data. SQL analogy: table calc = window function over the result set; LOD = subquery/window over the base table.
- Quick table calcs: Running Total, Percent Difference, Percent of Total, Rank, Moving Average, YTD, Compound Growth Rate, Year over Year.
- Partitioning (where the calc restarts) vs addressing (direction it walks) = PARTITION BY vs ORDER BY.
- Compute Using: Table across/down/across-then-down (snake)/Pane; changing layout or SORT changes results.
- WINDOW_SUM etc = reusable totals; RANK(agg,'desc'). Nested table calcs via Add Secondary Calculation (e.g. % difference on a running total = growth index).
- Parameters: Integer/Float/String; All/List/Range; do NOTHING until wired into a filter, calc, or reference line. Uses: TOP N filter, CASE to switch measures, threshold reference lines, dynamic titles, quadrant chart (2 params + 2 ref lines + IF color calc).

### 2.5 Date/time and time series
- MAKEDATE, MAKETIME, MAKEDATETIME, DATEPARSE. DATEPART (number) vs DATETRUNC (date); DATEADD (date) vs DATEDIFF (number).
- Literal dates `#2017-05-31#` always Year-Month-Day. Data locale vs workbook locale.
- Seasonality: discrete months on Columns + YEAR on Color = year over year overlay.
- Moving average: Quick Table Calc, edit Previous/Next (centered vs trailing). YTD = running sum restarting per year. CAGR = Compound Growth Rate quick calc `((end/start)^(1/n) - 1)`. Indexed growth = moving average + secondary % difference from FIRST.
- Dual axis: right click 2nd pill > Dual Axis; watch label pills on the All marks card.

---

## PART 3 — Statistics reference (Statistical Techniques course)

### 3.1 Univariate EDA
- Tables vs bar plots: tables win when exact values matter or a large value squashes small ones.
- Histograms: right click measure > Create > Bins (or Show Me); discrete bins show start value only, switch pill to Continuous for full range; bin size via a parameter slider (narrow = noisy, wide = hides detail); modality = number of peaks; mode = most common value.
- Box plots: disaggregate first (unique ID on Detail OR Analysis > untick Aggregate Measures); box = IQR (50% of data), whiskers 1.5×IQR, points beyond = outliers; NO mean shown; Tableau uses Tukey hinges. Read skew from which hinge sits closer to the median; kurtosis from how many points fall outside the whiskers.

### 3.2 Spread and confidence intervals
- Worksheet > Show Summary card (dropdown adds StdDev, quartiles, skewness, excess kurtosis). Both ~0 = normal; both + = right skew with high outliers (leptokurtic); both − = left skew, no outliers (platykurtic).
- Variance NOT on the card: right click measure pill > Measure > Variance / Variance (Pop.).
- Tableau defaults to SAMPLE stats (divide by n−1); use population (n) only when the data IS the whole group. Difference negligible for large n.
- Variance = avg squared distance from mean; SD = √variance (same units). Normal rule: 68% within 1 SD, 95% within 2, 99.7% within 3.
- Standard error = SD/√n; 95% CI = mean ± 1.96×SE; only meaningful for samples.
- Analytics pane: reference line, reference band, distribution band (StdDev with Factors like −4,4, sample vs population, Computation label). Scope Table/Pane/Cell when dropping. Average/Median with 95% CI shortcuts.

### 3.3 Bivariate EDA
- Scatter plot: predictor on x, thing being predicted on y. Correlation coefficient −1 to 1 (sign = direction, magnitude = strength).
- Trend lines: Analytics > Trend Line; right click > Edit All Trend Lines to cycle Linear, Logarithmic, Exponential, Power, Polynomial (degree 2 to 8). Right click > Describe Trend Model for R², p value, and RSE (labeled "standard error").
- Assess: R² = share of variation explained (higher better); RSE = typical miss in y's units (compare models); p < 0.05 = significant. Never judge on p alone.
- Power model needs both variables log transformed for CIs (Tableau can't put CIs on a raw power model).
- GOTCHA: Describe Trend Model reports ONE overall R² even when colored by a factor (e.g. clade); the individual line's R² only appears on hover.

### 3.4 Forecasting and clustering
- Forecasting = predict future from a time series; autocorrelation/seasonality repeats over time. Analytics > Forecast (exponential smoothing, auto picks best of up to 8 models). Metrics: MAE (avg miss) and MASE (vs naive forecast; near 0 = accurate, near 1 = no better than naive, >1 = worse). Forecast Options set length, hold-out periods, interval %; Forecast Result fields in tooltip.
- Clustering = unsupervised, groups similar rows. Analytics > Clusters, set k (or auto). k-means: random centers, assign nearest, move center, repeat until stable. Quality: between-group SS (bigger = better separation), within-group SS (smaller = tighter); Describe Clusters gives centers (= averages) and per variable p values. Save cluster group to Data pane to reuse (e.g. color a map, build a table).

---

## PART 4 — Dashboard + storytelling reference (interview critical)
- Build sheets first, then a Dashboard: drag sheets in, set size (Fixed/Automatic/Range), use containers and padding for spacing.
- Swap a sheet via the Sheets pane double arrow icon; floating vs tiled objects; floating legends and filters.
- Dashboard actions: Filter (Select/Hover/Menu), Highlight, Go to URL. Set source and target sheets; "Use as Filter" on a chart. Apply filter to Worksheets > All Using This Data Source when a filter should propagate.
- KPI cards: remove stray filter pills so the chart's action drives them; watch stale filters skewing numbers.
- Dynamic title: axis titles are static, so blank the axis and insert a parameter/field into the worksheet or dashboard title instead.
- Stories: sequence dashboards into story points; duplicate a point to show a zoomed/filtered state; style captions via Format > Story.
- Recurring gotchas: highlight tables need Square marks; filled maps via Marks > Map with the measure on Color; a Line mark's Size controls line+marker together (split into Line+Circle on dual axis to size markers independently); a stray % of Total table calc on a rate gives >100%.

---

## PART 5 — Recommended interview prep projects (do 1 to 3 before July 9)
Priority: calculations and dashboards. Use Tableau Public Desktop (already installed) with a free sample dataset (Superstore is ideal and interviewers know it) or your own CSV.

1. **Superstore Calculations Workbook (highest priority, ~2 hrs).** One workbook, one sheet per technique: (a) profit ratio done wrong (AVG of ratio) vs right (SUM/SUM), (b) `% of category sales` with FIXED, (c) running total + YoY growth via nested table calc, (d) TOP N customers via a parameter, (e) a CASE parameter that swaps the measure shown. Goal: be able to explain each out loud and reproduce under time pressure. Directly rehearses the most common calculation interview questions.

2. **Sales Dashboard with Actions (high priority, ~2 hrs).** KPI text tiles + a bar chart + a line trend + a map, wired with a Filter action and a Highlight action, dynamic title driven by a parameter, one guardrail (e.g. profit ratio) as a reference line. Rehearses dashboard assembly, actions, and layout, the second big interview theme.

3. **LOD Deep Dive Mini Project (learning + blog fuel, ~1.5 hrs).** Recreate the three LOD types on one dataset: FIXED for % of total, INCLUDE for avg-per-customer-in-region, EXCLUDE for a regional benchmark reference line. Export the numbers and reproduce them in SQL and pandas to prove they match. This doubles as the flagship blog post.

4. **Time Series + Forecast (optional, ~1 hr).** Monthly sales line, seasonality overlay (month on Columns, year on Color), moving average, a forecast with MASE read from Describe Forecast. Good if the role touches trends/forecasting.

Interview tip: practice narrating WHY you pick a calculation type (row vs aggregate vs LOD vs table calc) and be ready to whiteboard the SQL/pandas equivalent, since that shows true understanding.

---

## PART 6 — Blog post series plan
Theme: "The same answer in three languages: Tableau, SQL, and pandas." Each post takes one Tableau technique, shows the calc, then the SQL and pandas that produce the identical result, with a small before/after data table.

Suggested posts (order = build difficulty):
1. **Row level vs aggregate, and the average-of-averages trap.** Foundation. SUM/SUM vs AVG(ratio), with the 1/0 = COUNT trick.
2. **LOD expressions demystified: FIXED / INCLUDE / EXCLUDE** (flagship). Map FIXED→window PARTITION BY / groupby.transform, INCLUDE→two step groupby, EXCLUDE→window over fewer keys. Worked % of total, cohort, and benchmark examples.
3. **Table calculations vs LODs: virtual table vs raw data.** Running total, % of total, rank, moving average as SQL window functions; partition vs address = PARTITION BY vs ORDER BY.
4. **Parameters that make dashboards interactive.** TOP N, measure swapping via CASE, threshold reference lines, dynamic titles.
5. **Statistics in Tableau without the black box.** Variance/SD/CI, trend lines and R²/RSE/p, forecasting MASE, clustering, each with the pandas/statsmodels equivalent.
6. **Designing a dashboard that tells a story.** Actions, layout, guardrails, dynamic titles; a portfolio-ready build.

Publishing: build vizzes in Tableau Public Desktop, publish to the personal Tableau Public profile for the public link, embed those in each blog post, and host the written posts on the portfolio site. (Sandbox cannot save or share, so it is only for throwaway practice.)

---

## PART 7 — How Trinidad likes to work / response rules (carry into the blog project)
- Answers to concept questions: ONE plain sentence at ~10th grade level unless more is requested; scannable bullets, never dense paragraphs.
- No hyphens/dashes except compound nouns (e.g. "five-step" ok). Be concise, cut filler.
- For any Tableau click path: name UI parts properly (Columns shelf, Marks card, Filters shelf), one action per sub bullet, specify drop position relative to named pills. Prefer menu paths over clicking empty space. Never instruct dragging pills off shelves (remove via right click > Remove).
- The SQL + pandas comparison framing is the thing Trinidad values most; keep leaning on it.
- Related memory notes: datacamp-tableau-context, lod-blog-post-plan, calculations-concepts-log.
