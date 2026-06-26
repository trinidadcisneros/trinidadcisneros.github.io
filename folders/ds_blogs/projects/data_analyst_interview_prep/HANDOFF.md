# Handoff message — paste this into a new Cowork chat

---

I'm continuing work from a prior Cowork session on my **Data Analyst Interview Prep** framework (it used to be called `sql_practice_generator`). I've moved it into my dedicated coding-projects folder.

**Project location:** `<this project folder>/data_analyst_interview_prep/`. Connect/grant access to the **repo root `bitterscientist.com`** — the SQL recipe playbook lives outside this project at `folders/sql/sql_problem_patterns.html`, so the next session needs the common ancestor to reach both.

**Read these before doing anything:**
1. `data_analyst_interview_prep/context.md` — full project context (start at "CURRENT STATE — read this first"): what each notebook is, the statistical methods notebook design (nb05), the roadmap, and the tone rules.
2. `data_analyst_interview_prep/cowork_handoff.md` — folder layout + statistical methods flow (nb05) + architecture notes.
3. The engine for whatever I'm working on: `notebooks/stats_drill_utils.py` (nb05 statistics), `notebooks/nb04_drill_utils.py` (nb04 analyst), `notebooks/nb03_modeling_drill_utils.py` (nb03 data cleaning and modeling), or `notebooks/sql_practice_utils.py` (nb01 SQL).
4. If working on SQL recipes or the playbook: `folders/sql/HANDOFF.md` is canonical for `folders/sql/sql_problem_patterns.html` — read its 2026-06-16 entry first (Single-Table tab grouped into technique leaves with templates + decision trees; Sessionization picked by expected output shape; nb01 engine now 32 qtypes).

**What this is.** A reusable interview-drill framework — one shared pattern (catalog → generate → diagnose → grade) behind focused notebooks:
- `nb01_sql_practice.ipynb` — SQL drills (Postgres/MySQL sandbox).
- `nb02_python_practice.ipynb`: NEW Python practice (pandas, numpy, basic Python array and string operations). Built separately.
- `nb03_data_cleaning_modeling_drills.ipynb`: clean messy raw data, build the target model (CREATE TABLE AS SELECT). Engine `nb03_modeling_drill_utils.py`.
- `nb04_analyst_interview_drills.ipynb`: modeling, critical-reasoning SQL, product metrics & KPIs, version control. Engine `nb04_drill_utils.py`.
- `nb05_statistical_methods_drills.ipynb`: A/B testing, power & sample size, hypothesis tests, regression, claims metrics. 3-step UX (Pick a problem → Diagnose → Implement) with a runnable Python editor, auto-run numeric check, and Claude rubric/diagnosis feedback (needs `ANTHROPIC_API_KEY` in `.env`).
- `nb06_sql_error_review.ipynb`: reviews every failed Submit logged from nb01, ranked by error type.
- `interview_practice_tool/` — a parked mock case-study coaching tool (voice-to-text, rubric scoring) I'm still evaluating.

**My situation.** Active healthcare data-analyst job search. Near-term interviews: MDCalc (Senior Data Analyst) and Judi Health / Capital Rx. I'm drilling statistical methods (nb05) and SQL (nb01).

**Tone rules (from context.md).**
- Be concise. Don't show code unless I ask — I read diffs myself.
- No trailing summary of what you just did. Lead with the result and a `computer://` link.
- No hyphens unless they're compound nouns.
- After editing a notebook, validate it executes (nbclient) or that all code cells parse, before handing back. For big changes, build in an isolated copy and let me approve before adopting.

**Roadmap if I ask for "next":** flesh out the new `nb02_python_practice.ipynb` (pandas, numpy, basic Python array and string operations), then keep splitting the analyst notebook's four categories into their own thin notebooks on the shared engine (target lineup: SQL, Python, statistical methods, product metrics, dbt/data modeling, version control). Copy nb05's pattern.

**Right now I want to:** [fill in — e.g., "drill A/B testing on Hard difficulty and tune the difficulty curve", "add a chi-square + confidence-interval subtopic to nb03", or "split the analyst notebook's Product Metrics category into its own notebook on the shared engine"].
