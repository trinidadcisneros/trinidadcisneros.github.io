# Custom Apps with AI

Two small, single purpose apps built conversationally with an AI assistant, used as worked examples for the blog post on creating custom simple apps with AI. Each one solves a real personal need, pulls from my own data, and took a single working session to build.

## Why these examples

Both apps share the same pattern that makes them good blog material: a clear daily decision, a personal data source already sitting in Google (a Doc and a Sheet), and a need to randomize or narrow choices. Neither required a backend, a database, or a deploy step. One is a zero dependency HTML file; the other is a notebook that reuses an API key I already had configured.

## App 1: Muay Thai workout generator

A self contained HTML file that builds a roughly 40 minute heavy bag workout on demand.

What it does: pick a difficulty (basic, intermediate, advance), click Generate, and copy the result straight into Google Keep. It keeps a fixed warmup, adds 3 random burnouts, and selects 7 drills that satisfy two constraints at once: a difficulty mix (for example advance = 5 advanced, 1 intermediate, 1 basic) and a category mix (2 strikes, 2 lower body, 3 combinations).

Source data: the drill catalog (99 drills plus burnouts) came from my Muay Thai drills Google Doc.

How it works under the hood: all 99 drills are tagged by level and by type. A small constraint solver picks a set that meets both the level and category targets, falling back gracefully if a perfect match is not possible. Verified across 5000 runs per difficulty with no failures.

Two versions:
- `muay_thai_workout_generator/muay_thai_workout_generator.html` — standalone, no-Python, open in any browser. No internet or install needed.
- `muay_thai_workout_generator/muay_thai_workout_generator.ipynb` + `muay_thai_lib.py` — modular notebook version (same pattern as the fragrance picker) with an interactive GUI, a copy-ready output and Copy button, and drill tracking: tick what you did, favor drills you haven't done yet, and see your most practiced. Logs to `muay_thai_usage_log.csv` and `muay_thai_workout_log.csv`.

To use the notebook: open it, run the load cell, then `mt.launch()`.

## App 2: Fragrance picker

A Jupyter notebook that recommends a 5 ml decant to wear based on the occasion.

What it does: choose an activity (gym, bar/social/date/dinner, home/lounge, work function), a container category, size (defaults to 5 ml), season, and time of day. It returns 3 fragrances to try. Two modes: an offline weighted random pick by Fragrantica score, and a Claude powered mode that reads the filtered shortlist and picks the 3 best for the occasion with a one line reason each, weighing projection and sillage fit.

Source data: my Fragrances Google Sheet (413 unique fragrances after cleaning, 288 of them at 5 ml).

API key handling: the notebook reads `ANTHROPIC_API_KEY` from the environment using `python-dotenv` and `anthropic.Anthropic()`, the same pattern as my other notebooks. Nothing is hardcoded. The offline mode works with no key at all.

The code is modular: the notebook is a thin shell (import, `setup()`, `launch()`) and all the logic lives in a library module, the same pattern as the interview-prep project's `sql_practice_utils.py`.

Files:
- `fragrance_picker/fragrance_picker.ipynb` — thin notebook: import, setup, launch
- `fragrance_picker/fragrance_picker_lib.py` — all the logic (data load, filters, recommendations, usage tracking, GUI)
- `fragrance_picker/fragrances_raw.csv` — offline fallback inventory
- `fragrance_picker/fragrances_clean.csv` — extra cleaned export
- `fragrance_picker/archive/` — stashed code-only usage snippets

To use: open the notebook, run the two cells, then use the dropdown picker. Set the model with `fp.MODEL` in the load cell (defaults to `claude-sonnet-4-5`). Edit `fragrance_picker_lib.py` for any logic change and re-run the load cell.

## Takeaways for the post

The work that mattered was not the code, it was specifying the rules clearly (the drill mixes, the filter columns, what counts as a good scent for the gym) and pointing the assistant at the right data. The deliverable format also matters: a copy ready text block for Keep, and a notebook that fits an existing key setup, both lowered the friction of actually using the apps day to day.
