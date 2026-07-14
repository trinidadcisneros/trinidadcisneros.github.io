# How to explain AQFS (approved language + worked example)

This is the exact wording and example Trinidad approved on July 9, 2026. Reuse this voice and this calculation in the blog post so the explanation is consistent. Rules: no jargon, no acronyms left undefined, no analogies, bullet points not paragraphs, plain language a 10 year old could follow.

## What AQFS is (plain definition)

- AQFS = Aggregated Quality Factor Score
- It is a report card grade for a health insurance plan
- It answers: how good is this plan at keeping its members healthy?
- It checks things like: did kids get their checkups, did people get their shots, did sick people get the care they needed
- All those checks get rolled into one number from 0 to 100
- Higher number = better care; 100 = one of the best plans in the whole country

## Why it matters

- Millions of low income families are assigned to these plans and cannot easily switch
- A low grade means real people get worse care
- The state can require improvement from plans that score too low

## What "the national top tier" means

- Line up every US plan on one quality measure, worst to best
- The "top tier" is the small group at the very best end (the level only the top 10% of plans reach)
- That level is the target bar the score is measured against
- It is NOT the same as scoring 90 to 100; it is the cutoff only the best 10% of plans clear

## The four step calculation (worked example, dummy data)

**Step 1 — each US plan's rate on each measure (higher = better)**

| Plan | Shots given | Checkups done | Diabetes control |
|---|---|---|---|
| A | 70% | 80% | 60% |
| B | 85% | 88% | 75% |
| C | 60% | 55% | 50% |

**Step 2 — the top tier bar for each measure (only the best plans reach it)**

| Measure | Top tier bar |
|---|---|
| Shots given | 90% |
| Checkups done | 85% |
| Diabetes control | 70% |

**Step 3 — for one plan (Plan A), score each measure as (plan rate divided by top bar) times 100**

| Measure | Plan A rate | Top bar | Measure score |
|---|---|---|---|
| Shots given | 70 | 90 | 78 |
| Checkups done | 80 | 85 | 94 |
| Diabetes control | 60 | 70 | 86 |

**Step 4 — average the measure scores into one number**

- (78 + 94 + 86) divided by 3 = 86
- Plan A's AQFS = 86

## Why divide the plan rate by the top bar

- The top bar is the goal (the score the best plans hit)
- Plan rate on top, goal on the bottom answers one question: how close did we get to the goal?
- Dividing turns it into a "how far along am I" percent: hit the goal = 100, halfway = 50, beat it = over 100
- Doing this puts every measure on the same 0 to 100 scale, so different measures (shots, checkups) can be fairly averaged together
- Without it you would be mixing measures with different normal levels, which would not be fair

## Key point about the direction

- The AQFS is the FINAL output; nothing is ranked or recalculated after it
- The top tier comparison happens BEFORE the score exists, using the individual measures
- A plan can score high without ever hitting a bar, if it gets close on all of them

## What our project does with it

- Our data already contains the finished AQFS score, one per plan per region per year
- We do NOT recompute it; we only average and compare the scores that are already there
- Example: averaging the 24 plans' scores in 2016 gives the statewide 55.455
