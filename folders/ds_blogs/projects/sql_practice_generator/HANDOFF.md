# Handoff message — paste this into the new Cowork chat

---

I'm continuing work from a prior Cowork session on my SQL Practice Generator project. The interview is on **2026-05-07** so I'm drilling daily and folding what I learn into the blog.

**Read these files before doing anything:**

1. `folders/ds_blogs/projects/sql_practice_generator/context.md` — full project context, what's worked, what to avoid, recipe card template, open work
2. `folders/ds_blogs/projects/sql_practice_generator/build/build_nb02.py` — the build script for the drill notebook (source of truth for the .ipynb)
3. `folders/ds_blogs/projects/sql_practice_generator/notebooks/nb02_drill_utils.py` — prompts, validators, graders
4. `folders/sql/pharmacy_problem_patterns.html` — companion blog with worked recipe cards (search for `id="materialization_choice"` for the most up-to-date card structure including the modeling-diagnostic section)

**The recurring workflow.** I generate a problem in nb02, drill it, ask for hints if stuck, submit my solution, get it graded. Then I usually ask to fold the worked solution into `pharmacy_problem_patterns.html` as a recipe card (8 standard sections, gotchas drawn from mistakes I actually made). I may also ask to refine prompts/validators/graders in `nb02_drill_utils.py` if a subtopic is producing inconsistent problems.

**Tone rules from context.md.**
- Be concise. Don't show me code unless I ask. I read diffs myself.
- No trailing summaries — lead with the result and a `computer://` link.
- No hyphens unless they're compound nouns.
- After any nb02 change: rebuild via `python3 build/build_nb02.py`, then verify all code cells parse with `ast.parse`.

**Right now I want to:** [fill in your specific request here — e.g., "drill the schema_design subtopic and then fold it into Tab 2", or "the cohort_retention validator keeps rejecting my answer, can you debug"]
