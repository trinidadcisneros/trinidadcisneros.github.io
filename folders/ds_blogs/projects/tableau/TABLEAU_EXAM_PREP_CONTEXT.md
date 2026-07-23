# Tableau Exam Prep — Project Context (read this first)

Durable context for the Tableau certification prep track. It lives in the repo (git), so it persists even if the Cowork session changes. Claude should read this at the start of any session on this work.

Last updated: July 22, 2026.

---

## 1. Response and format preferences (how Claude should communicate)

- **Be concise and direct.** Minimal verbosity. If a word can be removed without losing meaning, remove it.
- **Answer a direct question in ONE plain sentence** unless elaboration is requested.
- **Bullet points over long paragraphs.** No large blocks of text.
- **No hyphens or dashes except in compound nouns** (e.g. "year-over-year" is fine; avoid gratuitous hyphenation and never use em dashes).
- **No "we"** in any blog or written output. Use first person "I" or third person.
- **Show title and tab-name options and WAIT for approval** before applying a name across the page, landing page, and posts.json. Do not make global naming changes unilaterally.
- **Instructions must be executable in order:** never reference a field, parameter, or variable that was not created in an earlier step; state prerequisites at the top.
- **Verify every figure programmatically** (DuckDB SQL and pandas) before it appears in a post; the user has caught rounding errors, so accuracy matters.
- **No jargon or acronyms left undefined;** no analogies unless asked. Health-care and business terms (capitation, managed care, penetration, market share, etc.) must be defined in lay language on first use.
- **No post in this series references a notebook.** Never mention `nb00`/`nb01`/`nb02`, `.ipynb`, or the word "notebook" in a published post. Frame data prep as "data prep" or "the cleaning step," and describe the workflow as "Python to prepare the data, Tableau to join and visualize." All four posts were scrubbed of notebook references on July 22, 2026; keep new posts clean from the start.
- **Section headers are concise statements, not questions.** Use short bold `.subhead` labels followed by bullets, not blocks of text.

### Tableau walkthrough format (STRICT — this is how the build sessions run)

Trinidad builds every sheet herself in Tableau Desktop. Claude guides her **one small instruction set at a time**. Violating this is the most common mistake.

- **Every instruction set opens with a Purpose block: at most 3 bullets, plain non-technical language, fewer if the step is simple.** Trinidad must understand WHY she is doing the step, not blindly follow clicks. Keep it short.
- **ONE STEP per reply. Not one instruction set, ONE STEP.** She said plainly: "DO NOT SHOW ME MORE THAN 1 STEP." Give a single action, wait for her to do it, confirm, then give the next one. Never dump a whole sheet, never dump multiple sheets, and never batch steps together even if they feel small.
- **She will not always send a screenshot.** Do not stall waiting for one; if she says the step is done, confirm briefly and continue.
- **STOP after each set and wait.** Trinidad implements it, sends a screenshot, and says something like "confirm and next set of instructions." Only then does Claude confirm and give the next set.
- **EVERY step must name WHERE the action happens: the tab AND the panel.** Never just say "in the Data pane." Say which tab (the Data Source tab, or the specific worksheet by name) and which panel or section (Data pane / Tables list, Columns shelf, Rows shelf, Filters shelf, Marks card, Measure Values card, Analytics tab). She has called this out more than once. Useful fact: **group and calculated fields do NOT appear in the Data Source tab grid**, they only exist in the Data pane inside a worksheet, so those edits must be done from a worksheet.
- Use **exact Tableau UI names**: Data pane, Columns shelf, Rows shelf, Filters shelf, Marks card, Analytics tab, Show Me.
- **State the expected values** so she can verify the result herself.
- **End every set with Save (Cmd+S).**
- **Rename every new sheet BEFORE building anything on it.**
- Do not explain the teaching point or the pitfall until the step that demonstrates it is actually reached. No previewing what comes later.
- Every formula may only reference fields created in an earlier step; state prerequisites at the top of the set.

## 2. The project and goals

**Primary goal:** pass the **Salesforce Certified Tableau Data Analyst** exam (60 questions, 105 minutes, 65% to pass, tests on product version 2024.2, no prerequisites).

**Exam domains and weights:**
- Explore and Analyze Data — 41% (the emphasis)
- Create Content — 26%
- Connect and Transform Data — 24%
- Publish and Manage Content — 9%

**Approach:** build three health-plan analytics projects on public data that double as practice for the analyst work at L.A. Care, each covering exam objectives.
- Explore and Analyze is emphasized in every project.
- **LOD (Level of Detail) appears in every project.**
- **A dedicated Context (context filters) section appears in every project,** taught as the WHERE-clause analog with a worked pitfall (a FIXED benchmark or a Top N that comes out wrong until the filter is added to context).
- SQL and pandas analogs are shown wherever they illuminate; dropped for GUI-only topics (maps, Prep, publishing).
- **No drill questions or practice-exam simulator from Claude.** The user sources reputable external questions to train on.

**The three projects** (scaffolded READMEs under `folders/ds_blogs/projects/tableau/`):
1. `tableau_star_ratings` — CMS Medicare Advantage and Part D Star Ratings (plan quality). The designated **live Snowflake connection** project.
2. `tableau_ma_enrollment` — CMS Medicare Advantage enrollment and market share. Heaviest on unions and a Tableau Prep flow.
3. `tableau_county_health` — County Health Rankings population health. Heaviest on maps and the Analytics pane.

**Every project must include a Tableau-native cleaning step, not just notebook prep.** Connect and Transform is 24% of the exam, so each project practices cleaning inside Tableau: **Aliases** (rename dimension members, e.g. fixing ALL CAPS names), **Groups** (merge duplicate/misspelled members), **Split / Custom Split**, **Data Interpreter**, renaming fields, and changing default field properties. Reach these from the field dropdown in the **Data Source tab** or by right clicking the field in the **Data pane**, so the fix applies workbook-wide rather than per sheet.

**ORDER MATTERS when cleaning in Tableau: GROUP FIRST, THEN ALIAS.** An alias attaches to one specific field. Creating a Group makes a **brand new field** (`Field (group)`), and that new field's member list is built from the base field's **raw values**, not its aliases. So aliases applied to the base field do NOT carry over to the group field, and the work has to be redone. Always: merge duplicates with a Group first, then apply aliases to the resulting group field (the one actually used on the sheet).

**The rule for where a fix belongs:**
- **Aliases are display only** and can never change a number. Safe to leave as a Tableau-only step.
- **Groups change numbers** (merging members changes that member's average and count). If a grouped value appears in the published post, `nb01` must perform the same merge, or `nb02` (SQL and pandas) will disagree with Tableau.
- General principle: anything that **changes a number** belongs in the notebook for reproducibility; anything **purely cosmetic** can live in Tableau.

**Per-project pipeline (same as the Medi-Cal posts):** `nb00` extract and profile → `nb01` clean → Tableau build (user drives) → dashboard → publish to Tableau Public → `nb02` SQL and pandas parity → blog page registered in `posts.json` and the Data Stories landing page.

**Background:** this grew out of an on-site SQL and Tableau assessment at L.A. Care for the Enterprise Support Analytics Solutions and Data Analyst III role (recruiter David Zandueta, hiring manager Alka Agarwal). Two finished Medi-Cal posts already live on the site and double as portfolio pieces.

## 3. Tools and resources on the user's computer

- **OS:** macOS on an Intel-based Mac (Darwin x64 25.5.0).
- **Tableau Public Desktop 2026.2.0** (free edition) for the builds; local `.twbx` save requires this version. Note the exam tests on version 2024.2, so behavior should be checked against exam-era features where they differ.
- **Snowflake personal account:** Enterprise edition on AWS, server version 10.23.103. Used for the live database connection practice in Project 1. The account identifier, login, and role are intentionally **kept out of this public repo** and live in private notes; the password or token is never stored anywhere and is entered by the user directly.
- **VS Code 1.128.0** (Universal) as the editor.
- **Jupyter Notebook 7.5.3**, launched locally from the terminal. **The user runs the notebooks (nb00 extract, nb01 clean, nb02 parity) on her own machine;** Claude writes them. Claude's sandbox is used only to draft and to reproduce parity once raw files are committed.
- **Tableau Public profile** for publishing: `https://public.tableau.com/app/profile/trinidad.cisneros`.
- **Git repository (public GitHub Pages):** `https://github.com/BitterScientist/trinidadcisneros.github.io`. A `CNAME` maps it to **trinidadcisneros.com**. Deploy = `git push` to this repo. Blog pages live at `folders/ds_blogs/<name>.html` and are reachable at `https://trinidadcisneros.com/folders/ds_blogs/<name>.html`. Because the repo is public, never commit secrets or private identifiers.
- **Gmail and Google Calendar** connectors are available (used for the job search side).

**Working division of labor:** the user drives all Tableau Desktop work herself, one step at a time, and returns screenshots, and runs the notebooks locally; Claude writes the data prep code, the SQL and pandas parity, and the blog HTML.

## 4. Standard project details and conventions

- **Repo and deploy:** blog HTML in `folders/ds_blogs/`; projects (data, notebooks, workbooks) in `folders/ds_blogs/projects/tableau/<project>/`; posts registered in `static/data/posts.json` and carded on `folders/ds_blogs/ds_blog_landing.html`.
- **Blog page skeleton:** tabbed single-file HTML modeled on `ds_tableau_sql_pandas_medi_cal.html`: collapsible `details.sec` sections, Expand/Collapse All per tab, one font with a strict size scale (body smaller than tab labels), muted table header fills, pitfalls shown as right vs wrong output tables, each tab opening with an Introduction and The Question container plus a roadmap.
- **Reproducibility:** `nb00` pulls raw files and writes `data/extraction_log.json`; re-running `nb01` from raw must reproduce the clean CSVs byte for byte; `nb02` asserts every blog figure matches across Tableau, DuckDB, and pandas.
- **Security:** never use `polyfill.io` (compromised CDN); use `cdnjs.cloudflare.com/polyfill`.
- **Tableau save rule:** save after every instruction set (Cmd+S); rename each new sheet before doing anything else.
- **Palette discipline:** set a color palette on the first sheet and reuse it on every sheet and the dashboard so a series never changes color.

## 5. Memory and continuity

- This Cowork has persistent file memory. The index and the project memory file `tableau-medi-cal-blog-project.md` track status across sessions.
- If switching Coworks, this file plus that memory entry are the two places to reload context from. Update both when a project phase completes.

## 6. Current status and next step

Last updated July 22, 2026.

**Four posts complete and live** (all published to Tableau Public, verified in DuckDB SQL and pandas, scrubbed of "we" and of all notebook references, registered in `posts.json` + the Data Stories landing):

1. `ds_tableau_sql_pandas_medi_cal.html` — "How Tableau Thinks" (Medi-Cal enrollment). Post 1.
2. `ds_tableau_sql_pandas_hedis.html` — Medi-Cal HEDIS plan quality. Post 2.
3. `ds_tableau_sql_pandas_star_ratings.html` — CMS Star Ratings (plan quality; the Snowflake live-connection project). Post 3.
4. `ds_tableau_sql_pandas_la_market_share.html` — "Medi-Cal Market Share in Los Angeles, from Enrollment to Quality". Post 4 (detail below).

**Post 4 detail (`tableau_la_market_share`), finished July 22, 2026.** Reframed from the original MA-enrollment idea to Medi-Cal LA County market share because Medi-Cal is L.A. Care's core business. Dashboard `Dashboard1` in workbook `la_medi_cal_market_share`, published at https://public.tableau.com/views/la_medi_cal_market_share/Dashboard1 (authored 1250x2427, embed uses `device=desktop`). Six panels: Enrollment Over Time; Market Share (FIXED LOD `{FIXED [Enrollment Month]:SUM([Enrollees])}`); Share vs Quality (join on Brand+Year, Kaiser absent because its 2024 line has no quality score yet); Penetration Map (join on County); Access Map (join on County + a context filter `>= 5,000` members, orange Percentile quantile coloring); LA Care Providers by Type. `nb02` parity = 18/18 pass. Three enrichment reference files are joined INSIDE Tableau (county population, HEDIS quality, provider counts). Blog has 3 top-level tabs: Overview, The Dashboard, and Methods (nested sub-tabs, default order: Context & Data Prep, Joins & Enrichment, Level of Detail).

**Framing rules established for Post 4 (reuse for any Medi-Cal market post):** scope every claim to the *Medi-Cal managed care market* (NOT all insurance — Kaiser is far larger overall via commercial coverage); define managed care vs fee-for-service; "commercial" describes the company, not the coverage (Health Net and Kaiser both run Medi-Cal lines); the Two-Plan Model is a California Medi-Cal construct and Los Angeles is one instance of it; Model 1 = L.A. Care (public Local Initiative, state-*created* in 1997), Model 2 = commercial companies that also contract to run Medi-Cal (Health Net *selected* 1997; Kaiser direct contract Jan 2024). Medi-Cal enrollment is year-round (no open-enrollment window); plan switching runs through an annual window with exceptions.

**Git note:** the raw provider extract is ~1.5 GB and exceeds GitHub's 100 MB limit. `folders/ds_blogs/projects/tableau/tableau_la_market_share/data/raw/` is now gitignored (also `*.twbr` Tableau autosave temps). Never commit raw extracts; they re-pull from the CalHHS / CA open-data API. The four-post commit was pushed after removing the raw folder from the commit.

**Not built (from the original 3-project plan):** `tableau_ma_enrollment` (superseded by `tableau_la_market_share`) and `tableau_county_health` (maps + Analytics-pane project) remain scaffolded READMEs only.

**Next:** starting a new post; topic is open. Preferred candidates are the `tableau_county_health` maps/Analytics-pane project, or another L.A. Care-relevant dataset (Trinidad starts a data analyst role at L.A. Care around late July 2026, so L.A. Care-relevant topics are best). Confirm the topic and dataset with Trinidad first, then run the standard pipeline: `nb00` extract → `nb01` clean → Tableau build (she drives, ONE step at a time) → publish to Tableau Public → `nb02` parity → blog page → register in `posts.json` + landing. There is a personal (NOT in the public repo) L.A. Care business briefing at `~/Documents/Claude/Projects/trinidadcisneros.com/la_care_business_and_data_briefing.html` with business-model context.
