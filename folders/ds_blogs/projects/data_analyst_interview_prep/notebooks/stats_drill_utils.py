"""
stats_drill_utils.py — engine for nb03 Statistical Methods drills.

Peer of nb01/nb02: scenario-grounded problems with Topic + Scenario + Difficulty +
Source controls, a Diagnose step (walkthrough/solve), and a runnable Python
Implement step (auto-run numeric check + optional Claude rubric).

Public surface (used by the notebook):
  SUBTOPICS, subtopic_keys(), subtopic_label()
  SCENARIOS, scenario_options(), pick_scenario(key)
  DIFFICULTIES
  worked_example_html(subtopic)
  diagnose_spec(problem)            -> list of step dicts (walkthrough)
  strategy_summary(problem)         -> approach string
  reference(problem)                -> {approach, solution_code, answer_key, tol}
  generate_problem(subtopic, difficulty='moderate', scenario='random') -> problem dict
  starter_code(problem) -> str
  dataset_preview_html(problem) -> str
  problem_card_html(problem, compact=False) -> str
  check_numeric(problem, answers) -> (ok, rows)
  save_problem / list_problems / load_problem
  claude_available()
  claude_rubric(problem, user_code, run_output)
  claude_grade_diagnosis(problem, text)
"""
from __future__ import annotations
import os, math, json, random, uuid, glob, html
from datetime import datetime
from typing import Dict, Any, List, Tuple, Optional

import numpy as np
from scipy import stats

_rng = np.random.default_rng()

# ============================================================
# Scenarios (mirror nb01/nb02 industry list)
# ============================================================
SCENARIOS: Dict[str, Dict[str, Any]] = {
    "random":           {"label": "🎲 Random (any industry)", "phrases": None},
    "booedup":          {"label": "🎯 My App (BooedUp dating app)",
                         "phrases": ["the BooedUp dating app tracking match acceptance and first-message rate"]},
    "consumer_social":  {"label": "Consumer Social (dating, social, video, podcast)",
                         "phrases": ["a short-video app tracking watch-through and follow rate",
                                     "a podcast app tracking episode completion and subscribe rate",
                                     "a social feed app tracking post engagement and DAU"]},
    "marketplace":      {"label": "Marketplace (rideshare, delivery, listings)",
                         "phrases": ["a food-delivery app tracking checkout conversion and reorder rate",
                                     "a rideshare app tracking ride request-to-completion",
                                     "a listings marketplace tracking contact-seller conversion"]},
    "ecommerce":        {"label": "Ecommerce (D2C, fashion, grocery)",
                         "phrases": ["a D2C fashion store tracking add-to-cart and purchase conversion",
                                     "an online grocery tracking checkout completion and basket size"]},
    "fintech":          {"label": "Fintech (neobank, BNPL, robo, crypto)",
                         "phrases": ["a neobank tracking account funding and card activation",
                                     "a BNPL app tracking application approval and repayment"]},
    "b2b_saas":         {"label": "B2B SaaS (CRM, PM, HR, observability)",
                         "phrases": ["a project-management SaaS tracking trial-to-paid conversion",
                                     "an observability tool tracking onboarding completion and seat expansion"]},
    "productivity_media": {"label": "Productivity & Media (notes, streaming, news)",
                         "phrases": ["a notes app tracking activation and weekly retention",
                                     "a streaming service tracking trial conversion and watch time"]},
    "health_wellness":  {"label": "Health & Wellness (telehealth, fitness, sleep)",
                         "phrases": ["a telehealth app tracking visit booking-to-completion",
                                     "a fitness app tracking workout completion and active days",
                                     "a sleep-tracking app tracking sleep score and goal achievement"]},
    "gaming":           {"label": "Gaming (mobile, console)",
                         "phrases": ["a battle-royale mobile game tracking match completion and squad invites",
                                     "a free-to-play game tracking session length and ad impressions"]},
    "education":        {"label": "Education (courses, language, tutoring)",
                         "phrases": ["a language-learning app tracking daily streaks and lesson completion",
                                     "an online course platform tracking course completion and certification"]},
    "pharmacy_care":    {"label": "Pharmacy & Care (digital pharmacy, diagnostics)",
                         "phrases": ["a digital pharmacy tracking prescription submission through PBM adjudication",
                                     "a refill-adherence program tracking 30/60/90-day refill rates",
                                     "a telehealth visit funnel from booking to provider sign-off"]},
}

def scenario_options() -> List[Tuple[str, str]]:
    return [(v["label"], k) for k, v in SCENARIOS.items()]

def pick_scenario(key: str = "random") -> str:
    if key == "random" or key not in SCENARIOS or not SCENARIOS[key]["phrases"]:
        pool = []
        for k, v in SCENARIOS.items():
            if v["phrases"]:
                pool += v["phrases"]
        return random.choice(pool)
    return random.choice(SCENARIOS[key]["phrases"])

DIFFICULTIES = [("🟢 Easy", "easy"), ("🟡 Moderate", "moderate"), ("🔴 Hard", "hard")]

# ============================================================
# Catalog
# ============================================================
SUBTOPICS = {
    "ab_testing":        {"label": "A/B testing — two-proportion z-test"},
    "power_sample_size": {"label": "Power & sample size"},
    "hypothesis_tests":  {"label": "Hypothesis tests — choose & run the right test"},
    "regression":        {"label": "Regression — fit & interpret"},
    "claims_metrics":    {"label": "Claims metrics — PDC adherence / PMPM"},
}
def subtopic_keys() -> List[str]:
    return list(SUBTOPICS.keys())
def subtopic_label(s: str) -> str:
    return SUBTOPICS[s]["label"]

def _r(x, n=4):
    return float(np.round(x, n))

# ============================================================
# Generators (scenario + difficulty aware)
# ============================================================
def generate_problem(subtopic: str, difficulty: str = "moderate", scenario: str = "random") -> Dict[str, Any]:
    ctx = pick_scenario(scenario)
    pid = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid.uuid4().hex[:8]
    base = {"id": pid, "subtopic": subtopic, "difficulty": difficulty,
            "scenario_key": scenario, "scenario": ctx, "kind": "python"}

    if subtopic == "ab_testing":
        n = {"easy": int(_rng.integers(12000, 30000)),
             "moderate": int(_rng.integers(4000, 14000)),
             "hard": int(_rng.integers(1500, 5000))}[difficulty]
        n2 = n if difficulty != "hard" else int(n * float(_rng.uniform(0.7, 1.0)))
        p1 = float(_rng.uniform(0.08, 0.28))
        lift = {"easy": _rng.uniform(0.03, 0.06), "moderate": _rng.uniform(0.012, 0.03),
                "hard": _rng.uniform(-0.01, 0.012)}[difficulty]
        p2 = min(max(p1 + lift, 0.001), 0.99)
        x1, x2 = int(_rng.binomial(n, p1)), int(_rng.binomial(n2, p2))
        pe1, pe2 = x1/n, x2/n2
        pool = (x1+x2)/(n+n2); se = math.sqrt(pool*(1-pool)*(1/n+1/n2))
        z = (pe2-pe1)/se; pv = 2*(1-stats.norm.cdf(abs(z)))
        base.update({
            "title": "Did the treatment move the conversion rate?",
            "prompt": [
                f"You ran an A/B test on {ctx}.",
                "The treatment changed the primary call-to-action; the control kept the existing flow.",
                f"Control converted **{x1:,} of {n:,}** users ({pe1:.2%}); "
                f"treatment converted **{x2:,} of {n2:,}** ({pe2:.2%}).",
                "Compute the two-proportion **z statistic** and its two-sided **p-value**, "
                "and be ready to state the absolute/relative lift and whether you'd ship.",
                "Store your result as `answers = {'z': ..., 'p_value': ...}`.",
            ],
            "data": {"n1": n, "n2": n2, "x1": x1, "x2": x2},
            "preview": [("control vs treatment", ["arm", "users (n)", "converted (x)", "rate"],
                         [["control", f"{n:,}", f"{x1:,}", f"{pe1:.2%}"],
                          ["treatment", f"{n2:,}", f"{x2:,}", f"{pe2:.2%}"]])],
            "answer_key": {"z": _r(z), "p_value": _r(pv)},
            "tol": {"z": 0.02, "p_value": 0.01},
        })
        return base

    if subtopic == "power_sample_size":
        p1 = round(float(_rng.uniform(0.05, 0.30)), 3)
        mde = {"easy": 0.20, "moderate": float(_rng.choice([0.10, 0.15])),
               "hard": float(_rng.choice([0.05, 0.07]))}[difficulty]
        p2 = p1*(1+mde)
        za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
        pbar = (p1+p2)/2
        n = (za*math.sqrt(2*pbar*(1-pbar)) + zb*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2 / (p2-p1)**2
        base.update({
            "title": "How many users per arm do you need?",
            "prompt": [
                f"You're planning an A/B test on {ctx}.",
                f"Baseline conversion is **{p1:.1%}**; you want to detect at least a **{mde:.0%} relative** lift.",
                "Use α = 0.05 (two-sided) and power = 80%.",
                "Compute the required sample size **per arm** (round up). "
                "Store `answers = {'n_per_arm': ...}`.",
            ],
            "data": {"p1": p1, "mde": mde, "alpha": 0.05, "power": 0.80},
            "preview": [("inputs", ["baseline p1", "MDE (rel)", "alpha", "power"],
                         [[f"{p1:.1%}", f"{mde:.0%}", "0.05", "0.80"]])],
            "answer_key": {"n_per_arm": int(math.ceil(n))},
            "tol": {"n_per_arm": max(2, int(math.ceil(n)*0.02))},
        })
        return base

    if subtopic == "hypothesis_tests":
        paired = (difficulty == "hard" and _rng.random() < 0.5)
        nn = {"easy": int(_rng.integers(150, 300)), "moderate": int(_rng.integers(80, 180)),
              "hard": int(_rng.integers(40, 100))}[difficulty]
        mu = float(_rng.uniform(95, 105)); sd = float(_rng.uniform(10, 18))
        delta = {"easy": _rng.uniform(4, 8), "moderate": _rng.uniform(2, 4.5),
                 "hard": _rng.uniform(0.5, 2.5)}[difficulty] * (1 if _rng.random() < 0.5 else -1)
        if paired:
            before = _rng.normal(mu, sd, nn)
            after = before + delta + _rng.normal(0, sd*0.4, nn)
            t, p = stats.ttest_rel(after, before)
            base["data"] = {"before": before.tolist(), "after": after.tolist()}
            unit = "the same users measured before and after a change"
            prev = [("first 6 of each", ["before", "after"],
                     [[f"{b:.1f}", f"{a:.1f}"] for b, a in list(zip(before, after))[:6]])]
        else:
            a = _rng.normal(mu, sd, nn); b = _rng.normal(mu+delta, sd, nn)
            t, p = stats.ttest_ind(b, a)
            base["data"] = {"group_a": a.tolist(), "group_b": b.tolist()}
            unit = "two independent groups of users"
            prev = [("first 6 of each", ["group_a", "group_b"],
                     [[f"{x:.1f}", f"{y:.1f}"] for x, y in list(zip(a, b))[:6]])]
        metric = random.choice(["session length (min)", "time-to-complete (s)", "order value ($)", "engagement score"])
        base.update({
            "title": "Is the difference in means real?",
            "prompt": [
                f"On {ctx}, you compare **{metric}** across {unit}.",
                "Decide whether the data is **independent** or **paired**, run the correct test for a difference in means, "
                "and store `answers = {'t': ..., 'p_value': ...}`.",
                "Be ready to justify the test choice and report the effect, not just p.",
            ],
            "preview": prev,
            "answer_key": {"t": _r(t), "p_value": _r(p)},
            "tol": {"t": 0.05, "p_value": 0.02},
            "_paired": bool(paired),
        })
        return base

    if subtopic == "regression":
        nn = {"easy": int(_rng.integers(150, 250)), "moderate": int(_rng.integers(90, 160)),
              "hard": int(_rng.integers(50, 90))}[difficulty]
        b0 = float(_rng.uniform(-5, 5)); b1 = float(_rng.uniform(-3, 3))
        noise = {"easy": 3.0, "moderate": 6.0, "hard": 11.0}[difficulty]
        x = _rng.uniform(0, 20, nn); y = b0 + b1*x + _rng.normal(0, noise, nn)
        res = stats.linregress(x, y)
        xname = random.choice(["sessions per week", "days since signup", "lessons completed", "support tickets"])
        yname = random.choice(["monthly spend ($)", "retention score", "satisfaction score"])
        base.update({
            "title": "Fit a line and interpret the slope",
            "prompt": [
                f"On {ctx}, you have `x` = **{xname}** and `y` = **{yname}** for {nn} users.",
                "Fit a simple linear regression (y ~ x) and store `answers = {'slope': ..., 'intercept': ...}`.",
                "Then interpret the slope in one sentence (direction + magnitude, holding others constant).",
            ],
            "data": {"x": x.tolist(), "y": y.tolist()},
            "preview": [("first 6 rows", ["x", "y"], [[f"{xi:.1f}", f"{yi:.1f}"] for xi, yi in list(zip(x, y))[:6]])],
            "answer_key": {"slope": _r(res.slope), "intercept": _r(res.intercept)},
            "tol": {"slope": 0.05, "intercept": 0.5},
            "_xname": xname, "_yname": yname,
        })
        return base

    if subtopic == "claims_metrics":
        which = random.choice(["pdc", "pmpm"])
        if which == "pdc":
            covered = int(_rng.integers(150, 365)); period = 365
            base.update({
                "title": "Compute medication adherence (PDC)",
                "prompt": [
                    f"On {ctx}, a member had medication on hand **{covered} of {period}** days in the measurement period.",
                    "Compute **PDC** (proportion of days covered) and whether they are **adherent** (≥ 80%).",
                    "Store `answers = {'pdc': ..., 'adherent': True/False}`.",
                ],
                "data": {"covered_days": covered, "period_days": period},
                "preview": [("inputs", ["covered days", "period days"], [[str(covered), str(period)]])],
                "answer_key": {"pdc": _r(covered/period), "adherent": covered/period >= 0.8},
                "tol": {"pdc": 0.005, "adherent": 0},
                "_metric": "pdc",
            })
        else:
            members = int(_rng.integers(5000, 60000)); months = 12
            total = float(_rng.integers(2_000_000, 30_000_000))
            base.update({
                "title": "Compute PMPM cost",
                "prompt": [
                    f"On {ctx}, total spend over the year was **${total:,.0f}** with **{members:,}** average members across **{months}** months.",
                    "Compute **PMPM** (per-member-per-month) cost. Store `answers = {'pmpm': ...}`.",
                ],
                "data": {"total_spend": total, "avg_members": members, "months": months},
                "preview": [("inputs", ["total spend", "avg members", "months"],
                             [[f"${total:,.0f}", f"{members:,}", str(months)]])],
                "answer_key": {"pmpm": _r(total/(members*months), 2)},
                "tol": {"pmpm": 0.05},
                "_metric": "pmpm",
            })
        return base

    raise ValueError(f"unknown subtopic {subtopic}")

# ============================================================
# Diagnose specs (walkthrough)
# ============================================================
def diagnose_spec(problem: Dict[str, Any]) -> List[Dict[str, Any]]:
    s = problem["subtopic"]
    if s == "ab_testing":
        return [
            {"q": "What kind of comparison is this?",
             "options": ["Two proportions (rates)", "Two means", "A trend over time", "A single proportion"],
             "correct": 0, "why": "Conversion is a yes/no event per user → you're comparing two rates."},
            {"q": "Which test fits?",
             "options": ["Two-sample t-test", "Two-proportion z-test", "Chi-square goodness-of-fit", "Paired t-test"],
             "correct": 1, "why": "Two independent groups, binary outcome → pooled two-proportion z-test."},
            {"q": "State the hypotheses.",
             "options": ["H0: rates equal; H1: rates differ", "H0: rates differ; H1: equal",
                         "H0: lift > 0; H1: lift = 0", "No hypotheses needed"],
             "correct": 0, "why": "Null = no difference; alternative = a difference exists."},
            {"q": "One-sided or two-sided?",
             "options": ["Two-sided", "One-sided (greater)", "One-sided (less)", "Doesn't matter"],
             "correct": 0, "why": "Default to two-sided unless a directional hypothesis was pre-registered."},
            {"q": "What do you report beyond the p-value?",
             "options": ["Just the p-value", "Effect size (lift) + 95% CI", "Only the sample size", "The raw counts only"],
             "correct": 1, "why": "Significance ≠ importance — report the lift and its CI, and check guardrails."},
        ]
    if s == "power_sample_size":
        return [
            {"q": "What are you solving for?",
             "options": ["The p-value", "Required sample size n", "The effect size", "The power"],
             "correct": 1, "why": "You fix α, power, baseline and MDE, then solve for n."},
            {"q": "Which inputs do you need?",
             "options": ["baseline, MDE, α, power", "just baseline and n", "only the p-value", "mean and SD"],
             "correct": 0, "why": "n depends on baseline rate, the effect to detect (MDE), α and power."},
            {"q": "How does n scale with the effect size?",
             "options": ["n ∝ effect", "n ∝ 1/effect", "n ∝ 1/effect²", "independent of effect"],
             "correct": 2, "why": "Halving the MDE roughly quadruples n (n ∝ 1/effect²)."},
        ]
    if s == "hypothesis_tests":
        paired = problem.get("_paired", False)
        return [
            {"q": "Are the two groups independent or paired?",
             "options": ["Independent", "Paired (same units before/after)"],
             "correct": 1 if paired else 0,
             "why": ("Same users measured twice → paired." if paired else "Two separate groups → independent.")},
            {"q": "What is the outcome type?",
             "options": ["Continuous (a mean)", "Binary (a rate)", "Categorical (3+ groups)"],
             "correct": 0, "why": "You're comparing a numeric mean → a t-test family."},
            {"q": "Which test?",
             "options": ["Two-sample t-test", "Paired t-test", "Chi-square", "Two-proportion z"],
             "correct": 1 if paired else 0,
             "why": ("Paired data → paired t-test (ttest_rel)." if paired else "Independent means → two-sample t-test (ttest_ind).")},
            {"q": "What else do you report?",
             "options": ["Effect size + CI", "Only the p-value", "Only the t statistic"],
             "correct": 0, "why": "Report the mean difference and its CI alongside p."},
        ]
    if s == "regression":
        return [
            {"q": "What is the outcome type?",
             "options": ["Continuous → linear regression", "Binary → logistic regression", "Categorical → chi-square"],
             "correct": 0, "why": "A numeric outcome → ordinary linear regression."},
            {"q": "What does the slope mean?",
             "options": ["Change in y per +1 x, holding others fixed", "The correlation r", "The p-value", "The intercept"],
             "correct": 0, "why": "Slope = average change in y for a one-unit increase in x."},
            {"q": "What caveat must you state?",
             "options": ["Correlation ≠ causation", "n must be < 30", "Always one-sided", "Slope must be positive"],
             "correct": 0, "why": "A regression slope is associational unless the design supports causal claims."},
        ]
    if s == "claims_metrics":
        if problem.get("_metric", "pdc") == "pdc":
            return [
                {"q": "Which metric is asked for?",
                 "options": ["PDC (adherence)", "PMPM (cost)", "Utilization per 1000"],
                 "correct": 0, "why": "Days-on-hand over a period → PDC."},
                {"q": "What's the formula?",
                 "options": ["covered days / period days", "period / covered", "fills / members"],
                 "correct": 0, "why": "PDC = days with medication on hand ÷ days in the period."},
                {"q": "What's the adherence threshold?",
                 "options": ["≥ 80%", "≥ 50%", "≥ 95%"],
                 "correct": 0, "why": "PDC ≥ 80% is the standard adherence cutoff."},
            ]
        return [
            {"q": "Which metric is asked for?",
             "options": ["PMPM (cost)", "PDC (adherence)", "Conversion rate"],
             "correct": 0, "why": "Total spend normalized by members and months → PMPM."},
            {"q": "What's the denominator?",
             "options": ["members × months (member-months)", "members only", "months only"],
             "correct": 0, "why": "PMPM = total spend ÷ (avg members × months)."},
        ]
    return []

def strategy_summary(problem: Dict[str, Any]) -> str:
    s = problem["subtopic"]; paired = problem.get("_paired", False)
    return {
        "ab_testing": "Pooled two-proportion z-test, two-sided. Compute pooled p, SE, z, then the two-sided p-value; also report absolute & relative lift and the 95% CI on the difference.",
        "power_sample_size": "Solve the sample-size formula for a two-proportion test at α=0.05, power=0.80: n_per_arm = (z.975·√(2·p̄(1−p̄)) + z.80·√(p1(1−p1)+p2(1−p2)))² / (p2−p1)².",
        "hypothesis_tests": ("Paired t-test (ttest_rel) on after−before; report t, p, and the mean difference + CI."
                              if paired else
                              "Independent two-sample t-test (ttest_ind); report t, p, and the mean difference + CI."),
        "regression": "Fit y ~ x with least squares (stats.linregress); report slope, intercept, r; interpret slope as Δy per +1 x holding others fixed.",
        "claims_metrics": ("PDC = covered_days / period_days; adherent if ≥ 0.80."
                            if problem.get("_metric") == "pdc" else
                            "PMPM = total_spend / (avg_members × months)."),
    }[s]

# ============================================================
# Worked examples — formatted HTML cards
# ============================================================
def _card(title: str, body: str) -> str:
    return (f"<div style='border:1px solid #d0d7de;border-radius:8px;padding:14px 16px;margin:6px 0;background:#fff'>"
            f"<div style='font-weight:700;font-size:15px;margin-bottom:8px'>{title}</div>{body}</div>")

def _codeblk(code: str) -> str:
    return (f"<pre style='background:#0d1117;color:#c9d1d9;padding:10px 12px;border-radius:6px;"
            f"overflow:auto;font-size:12.5px;line-height:1.5'>{html.escape(code)}</pre>")

_WORKED_HTML = {
"ab_testing": _card("A/B test — two-proportion z-test",
    "<p>Control 1,320/12,000 (11.0%); Treatment 1,500/12,000 (12.5%).</p>"
    "<ol style='margin:4px 0 8px 18px'>"
    "<li><b>Lift</b>: absolute +1.5 pts; relative +13.6%.</li>"
    "<li><b>Pooled</b> p = (1320+1500)/24000 = 0.1175.</li>"
    "<li><b>SE</b> = √(p(1−p)(1/n₁+1/n₂)); <b>z</b> = (p₂−p₁)/SE.</li>"
    "<li><b>p-value</b> = 2·(1−Φ(|z|)).</li>"
    "<li><b>95% CI</b> on the diff = (p₂−p₁) ± 1.96·√(p₁(1−p₁)/n₁ + p₂(1−p₂)/n₂).</li>"
    "<li><b>Decide</b>: significant if p&lt;0.05, but a tiny lift can be meaningless — judge effect size + guardrails.</li></ol>"
    + _codeblk("pool=(x1+x2)/(n1+n2)\nse=(pool*(1-pool)*(1/n1+1/n2))**0.5\nz=(p2-p1)/se\np=2*(1-stats.norm.cdf(abs(z)))")),
"power_sample_size": _card("Sample size for a proportion test",
    "<p>Inputs: baseline p₁, relative MDE, α=0.05 two-sided, power=0.80.</p>"
    "<p>p₂ = p₁(1+MDE), z_a=1.96, z_b=0.84, p̄=(p₁+p₂)/2.</p>"
    + _codeblk("n = (1.96*math.sqrt(2*pbar*(1-pbar)) + 0.84*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2 / (p2-p1)**2")
    + "<p style='margin-top:6px'>Smaller MDE or lower baseline → n grows ~ 1/effect².</p>"),
"hypothesis_tests": _card("Which test, and a t-test",
    "<table style='border-collapse:collapse;font-size:13px'>"
    "<tr><th style='text-align:left;padding:3px 10px'>Situation</th><th style='padding:3px 10px'>Test</th></tr>"
    "<tr><td style='padding:3px 10px'>2 means, independent</td><td style='padding:3px 10px'>two-sample t (ttest_ind)</td></tr>"
    "<tr><td style='padding:3px 10px'>before/after, same units</td><td style='padding:3px 10px'>paired t (ttest_rel)</td></tr>"
    "<tr><td style='padding:3px 10px'>2 rates</td><td style='padding:3px 10px'>two-proportion z</td></tr>"
    "<tr><td style='padding:3px 10px'>3+ group means</td><td style='padding:3px 10px'>ANOVA</td></tr>"
    "<tr><td style='padding:3px 10px'>2 categoricals</td><td style='padding:3px 10px'>chi-square</td></tr></table>"
    + _codeblk("t,p = stats.ttest_ind(group_b, group_a)   # independent\nt,p = stats.ttest_rel(after, before)      # paired")),
"regression": _card("Simple linear regression",
    "<p>Fit y = b₀ + b₁·x; slope b₁ = average change in y per +1 x, holding others fixed. "
    "Logistic coef is log-odds; exp(coef) = odds ratio.</p>"
    + _codeblk("res = stats.linregress(x, y)\nslope, intercept, r = res.slope, res.intercept, res.rvalue")),
"claims_metrics": _card("PDC adherence & PMPM",
    "<p><b>PDC</b> = covered days / period days; adherent if ≥ 80% (cap days-on-hand at the period). "
    "<b>PMPM</b> = total spend / (avg members × months).</p>"
    + _codeblk("pdc  = covered_days / period_days\npmpm = total_spend / (avg_members * months)")),
}
def worked_example_html(subtopic: str) -> str:
    return _WORKED_HTML.get(subtopic, "")

# ============================================================
# Rendering — problem card + dataset preview
# ============================================================
def _md_inline(text: str) -> str:
    import re
    text = html.escape(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"`(.+?)`", r"<code style='background:#eaeef2;padding:0 3px;border-radius:3px'>\1</code>", text)
    return text

def _table_html(title: str, cols: List[str], rows: List[List[str]]) -> str:
    h = f"<div style='margin:6px 0'><div style='font-size:12px;color:#57606a;margin-bottom:2px'>{html.escape(title)}</div>"
    h += "<table style='border-collapse:collapse;font-size:13px'><tr>"
    h += "".join(f"<th style='border:1px solid #d0d7de;padding:3px 10px;background:#f6f8fa'>{html.escape(c)}</th>" for c in cols)
    h += "</tr>"
    for r in rows:
        h += "<tr>" + "".join(f"<td style='border:1px solid #d0d7de;padding:3px 10px'>{html.escape(str(c))}</td>" for c in r) + "</tr>"
    return h + "</table></div>"

def dataset_preview_html(problem: Dict[str, Any]) -> str:
    return "".join(_table_html(t, c, r) for (t, c, r) in problem.get("preview", []))

def problem_card_html(problem: Dict[str, Any], compact: bool = False) -> str:
    diff = {"easy": "🟢 Easy", "moderate": "🟡 Moderate", "hard": "🔴 Hard"}.get(problem["difficulty"], problem["difficulty"])
    meta = f"{problem['subtopic']} · {diff} · scenario: {problem['scenario_key']} · id {problem['id'][-8:]}"
    bullets = "".join(f"<li style='margin:3px 0'>{_md_inline(b)}</li>" for b in problem["prompt"])
    body = (f"<div style='font-size:11.5px;color:#8b949e;margin-bottom:4px'>{html.escape(meta)}</div>"
            f"<div style='font-size:17px;font-weight:700;margin-bottom:6px'>{html.escape(problem['title'])}</div>"
            f"<ul style='margin:4px 0 8px 18px'>{bullets}</ul>")
    if not compact:
        body += dataset_preview_html(problem)
    return f"<div style='border:1px solid #d0d7de;border-radius:8px;padding:14px 16px;background:#f8fafc'>{body}</div>"

# ============================================================
# Reference solution + starter code
# ============================================================
_REF_CODE = {
"ab_testing": "import math\nfrom scipy import stats\nn1,n2,x1,x2 = data['n1'],data['n2'],data['x1'],data['x2']\np1,p2 = x1/n1, x2/n2\npool=(x1+x2)/(n1+n2); se=math.sqrt(pool*(1-pool)*(1/n1+1/n2))\nz=(p2-p1)/se\np_value=2*(1-stats.norm.cdf(abs(z)))\nanswers={'z':z,'p_value':p_value}\nprint(f'lift {p2-p1:+.2%} (rel {(p2-p1)/p1:+.1%}), z={z:.3f}, p={p_value:.4f}')",
"power_sample_size": "import math\nfrom scipy import stats\np1,mde=data['p1'],data['mde']; p2=p1*(1+mde)\nza,zb=stats.norm.ppf(0.975),stats.norm.ppf(0.80); pbar=(p1+p2)/2\nn=(za*math.sqrt(2*pbar*(1-pbar))+zb*math.sqrt(p1*(1-p1)+p2*(1-p2)))**2/(p2-p1)**2\nanswers={'n_per_arm':math.ceil(n)}\nprint('n per arm:', math.ceil(n))",
"hypothesis_tests_ind": "from scipy import stats\nt,p_value=stats.ttest_ind(data['group_b'], data['group_a'])\nanswers={'t':t,'p_value':p_value}\nprint(f'two-sample t={t:.3f}, p={p_value:.4f}')",
"hypothesis_tests_paired": "from scipy import stats\nt,p_value=stats.ttest_rel(data['after'], data['before'])\nanswers={'t':t,'p_value':p_value}\nprint(f'paired t={t:.3f}, p={p_value:.4f}')",
"regression": "from scipy import stats\nres=stats.linregress(data['x'], data['y'])\nanswers={'slope':res.slope,'intercept':res.intercept}\nprint(f'slope={res.slope:.3f}, intercept={res.intercept:.3f}, r={res.rvalue:.3f}')",
"claims_metrics_pdc": "pdc=data['covered_days']/data['period_days']\nanswers={'pdc':pdc,'adherent':pdc>=0.8}\nprint('PDC=%.1f%% -> %s' % (pdc*100, 'adherent' if pdc>=0.8 else 'non-adherent'))",
"claims_metrics_pmpm": "pmpm=data['total_spend']/(data['avg_members']*data['months'])\nanswers={'pmpm':pmpm}\nprint('PMPM=$%.2f' % pmpm)",
}
def _ref_key(problem):
    s = problem["subtopic"]
    if s == "hypothesis_tests":
        return "hypothesis_tests_paired" if problem.get("_paired") else "hypothesis_tests_ind"
    if s == "claims_metrics":
        return "claims_metrics_pmpm" if problem.get("_metric") == "pmpm" else "claims_metrics_pdc"
    return s

def reference(problem: Dict[str, Any]) -> Dict[str, Any]:
    return {"approach": strategy_summary(problem),
            "solution_code": _REF_CODE[_ref_key(problem)],
            "answer_key": problem["answer_key"], "tol": problem["tol"]}

def starter_code(problem: Dict[str, Any]) -> str:
    keys = ", ".join(f"'{k}': ..." for k in problem["answer_key"])
    return (f"# `data` keys: {list(problem['data'].keys())}\n"
            f"# np, stats, math are available.\n"
            f"answers = {{{keys}}}\n")

# ============================================================
# Auto-run numeric checker
# ============================================================
def check_numeric(problem: Dict[str, Any], answers: Any) -> Tuple[bool, List[Dict[str, Any]]]:
    key = problem["answer_key"]; tol = problem.get("tol", {})
    if not isinstance(answers, dict):
        return False, [{"field": "(answers)", "your": repr(answers), "expected": "a dict", "pass": False}]
    rows, ok = [], True
    for k, exp in key.items():
        got = answers.get(k, None)
        if isinstance(exp, bool):
            passed = (bool(got) == exp)
        elif got is None:
            passed = False
        else:
            try:
                passed = abs(float(got) - float(exp)) <= float(tol.get(k, 1e-6))
            except (TypeError, ValueError):
                passed = False
        ok = ok and passed
        rows.append({"field": k, "your": got, "expected": exp, "pass": passed})
    return ok, rows

# ============================================================
# Save / list / load (Source: New vs Solved)
# ============================================================
def _out_dir() -> str:
    d = os.path.join(os.getcwd(), "data", "outputs", "stats_problems")
    os.makedirs(d, exist_ok=True)
    return d

def save_problem(problem: Dict[str, Any]) -> str:
    path = os.path.join(_out_dir(), f"{problem['id']}.json")
    with open(path, "w") as f:
        json.dump(problem, f)
    return path

def list_problems(subtopic: Optional[str] = None) -> List[Tuple[str, str]]:
    out = []
    for p in sorted(glob.glob(os.path.join(_out_dir(), "*.json")), reverse=True):
        try:
            d = json.load(open(p))
        except Exception:
            continue
        if subtopic and d.get("subtopic") != subtopic:
            continue
        out.append((f"{d.get('subtopic')} · {d.get('difficulty')} · {d.get('title','')[:38]} · {d.get('id','')[-8:]}", p))
    return out

def load_problem(path: str) -> Dict[str, Any]:
    return json.load(open(path))

# ============================================================
# Claude (optional) — rubric + diagnosis grading
# ============================================================
def claude_available() -> bool:
    return bool(os.environ.get("ANTHROPIC_API_KEY"))

def _claude(system: str, user: str, max_tokens: int = 600) -> Optional[str]:
    try:
        import anthropic
        client = anthropic.Anthropic()
        mdl = os.environ.get("DRILL_MODEL", "claude-sonnet-4-6")
        msg = client.messages.create(model=mdl, max_tokens=max_tokens, system=system,
                                      messages=[{"role": "user", "content": user}])
        return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    except Exception as e:  # noqa
        return f"__ERR__{type(e).__name__}"

def _wrap(body: str, color: str, label: str) -> str:
    return (f"<div style='padding:8px 10px;border-left:3px solid {color};background:#f6f8fa'>"
            f"<b>{label}</b><br>{body}</div>")

def claude_rubric(problem: Dict[str, Any], user_code: str, run_output: str) -> str:
    if not claude_available():
        return _wrap("Claude rubric is off (no <code>ANTHROPIC_API_KEY</code>). The auto-run numeric check still "
                     "verifies your numbers. Add the key to the project <code>.env</code> for reasoning feedback.",
                     "#b58105", "Rubric (off)")
    out = _claude(
        "You are a precise statistics interview grader. Grade the candidate's Python answer on "
        "(1) correct method/test choice, (2) correct computation, (3) assumptions stated, (4) interpretation. "
        "Concise HTML: one-line verdict, 2-4 bullets, one tip. No preamble.",
        f"SUBTOPIC: {problem['subtopic']}\nPROMPT: {' '.join(problem['prompt'])}\n"
        f"EXPECTED: {json.dumps(problem['answer_key'])}\nCODE:\n{user_code}\nOUTPUT:\n{run_output[:1500]}")
    if out and out.startswith("__ERR__"):
        return _wrap(f"Claude unavailable ({out[7:]}). Auto-run check still applies.", "#b00", "Rubric")
    return _wrap(out or "", "#0969da", "Claude rubric")

def claude_grade_diagnosis(problem: Dict[str, Any], text: str) -> str:
    if not text.strip():
        return _wrap("Write your diagnosis first.", "#b58105", "Diagnosis")
    if not claude_available():
        return _wrap("Claude grading is off — compare against the reference approach:<br><br>"
                     + html.escape(strategy_summary(problem)), "#b58105", "Reference approach")
    out = _claude(
        "Grade a candidate's verbal diagnosis of a stats problem BEFORE they code. Did they pick the right "
        "test, state hypotheses/assumptions, and a sound plan? Concise HTML: verdict + 2-3 bullets + the one thing to fix.",
        f"PROMPT: {' '.join(problem['prompt'])}\nREFERENCE APPROACH: {strategy_summary(problem)}\nCANDIDATE DIAGNOSIS:\n{text}")
    if out and out.startswith("__ERR__"):
        return _wrap("Claude unavailable. Reference approach:<br>" + html.escape(strategy_summary(problem)), "#b00", "Diagnosis")
    return _wrap(out or "", "#0969da", "Claude diagnosis feedback")
