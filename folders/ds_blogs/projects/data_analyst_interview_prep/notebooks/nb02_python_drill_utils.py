"""
Python Drill Utilities: in-kernel pandas / numpy / basic-Python practice.

Mirrors the public shape of sql_practice_utils.py (a topic catalog, a
generate_problem entry point, a checker, and renderers) but needs NO Claude,
NO Docker, and NO database. Every problem builds a small in-memory DataFrame,
array, or list, computes the expected output, and ships an idiomatic reference
solution as a string. The checker compares the user's result to the expected
output robustly across DataFrame / Series / ndarray / scalar / list / dict.

Public surface:
    CATEGORIES                  dict of category key -> metadata (label, group, blurb)
    DIFFICULTIES                ordered list of (key, label)
    SCENARIO_THEMES             optional industry scenario flavor list (healthcare friendly)
    INDUSTRY_SCENARIOS          dict of vertical -> scenario list (mirrors nb01)
    category_keys()             list of category keys in display order
    generate_problem(category, difficulty, scenario=None, seed=None) -> Problem
    check_answer(problem, user_result) -> (ok: bool, message: str)
    render_problem_html(problem) -> str
    render_solution_html(problem) -> str
"""

import random
import textwrap
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pandas.testing as pdt


# ============================================================
# Topic catalog
# ============================================================
# group is one of: "pandas", "numpy", "python". The picker uses group to
# label the dropdown so the three families read as sections.

CATEGORIES: Dict[str, Dict[str, str]] = {
    # ---- pandas core ----
    "pd_filter": {"label": "Filtering / boolean indexing", "group": "pandas",
                  "blurb": "Keep rows that satisfy one or more conditions."},
    "pd_select": {"label": "Select rows / columns (loc / iloc)", "group": "pandas",
                  "blurb": "Pull specific columns and rows by label or position."},
    "pd_sort": {"label": "Sorting", "group": "pandas",
                "blurb": "Order rows by one or more columns."},
    "pd_value_counts": {"label": "value_counts / counting", "group": "pandas",
                        "blurb": "Tally how often each category appears."},
    "pd_groupby": {"label": "groupby + agg", "group": "pandas",
                   "blurb": "Split by a key, aggregate each group."},
    "pd_merge": {"label": "merge / join", "group": "pandas",
                 "blurb": "Combine two frames on a shared key."},
    "pd_pivot": {"label": "pivot_table / pivot", "group": "pandas",
                 "blurb": "Reshape long data into a wide grid."},
    "pd_apply_map": {"label": "apply / map", "group": "pandas",
                     "blurb": "Transform values with a function or mapping."},
    "pd_missing": {"label": "Missing data (fillna / dropna)", "group": "pandas",
                   "blurb": "Handle NaN by filling or dropping."},
    "pd_newcol": {"label": "New computed columns", "group": "pandas",
                  "blurb": "Derive a new column from existing ones."},
    "pd_rename": {"label": "Rename columns", "group": "pandas",
                  "blurb": "Relabel columns to a target naming."},
    "pd_datetime": {"label": "Datetime parse / extract", "group": "pandas",
                    "blurb": "Parse strings to dates, pull out parts."},
    # ---- numpy ----
    "np_create": {"label": "Array creation", "group": "numpy",
                  "blurb": "Build arrays with arange, linspace, zeros, etc."},
    "np_vectorized": {"label": "Vectorized arithmetic", "group": "numpy",
                      "blurb": "Element-wise math across whole arrays."},
    "np_mask": {"label": "Boolean masks", "group": "numpy",
                "blurb": "Select array elements with a condition."},
    "np_agg": {"label": "Aggregations (sum / mean / axis)", "group": "numpy",
               "blurb": "Reduce arrays along an axis."},
    "np_reshape": {"label": "Reshape", "group": "numpy",
                   "blurb": "Change array shape without changing data."},
    "np_where": {"label": "np.where", "group": "numpy",
                 "blurb": "Pick between two values on a condition."},
    "np_broadcast": {"label": "Broadcasting", "group": "numpy",
                     "blurb": "Combine arrays of different shapes."},
    # ---- basic python ----
    "py_strings": {"label": "String operations", "group": "python",
                   "blurb": "split, slice, join, case, f-strings."},
    "py_comprehension": {"label": "List / dict comprehensions", "group": "python",
                         "blurb": "Build lists and dicts in one expression."},
    "py_slicing": {"label": "Slicing", "group": "python",
                   "blurb": "Pull sub-sequences with start:stop:step."},
    "py_sort_key": {"label": "Sorting with keys", "group": "python",
                    "blurb": "Order with a key function or reverse."},
    "py_counting": {"label": "Counting", "group": "python",
                    "blurb": "Tally items into a dict / Counter."},
}

DIFFICULTIES: List[Tuple[str, str]] = [
    ("easy", "Easy"),
    ("moderate", "Moderate"),
    ("hard", "Hard"),
]


def category_keys() -> List[str]:
    return list(CATEGORIES.keys())


# ============================================================
# Scenario flavor (optional, healthcare friendly): mirrors nb01
# ============================================================

SCENARIO_THEMES = [
    "a hospital system tracking patient admissions and readmissions",
    "a telehealth platform tracking appointment scheduling and no-shows",
    "a clinical research platform tracking trial enrollment and adverse events",
    "a population health team tracking chronic-condition patient cohorts",
    "a digital pharmacy tracking prescription refills and adherence",
    "a fitness app tracking workout completion and member retention",
    "an e-commerce platform tracking customer orders and returns",
    "a B2B SaaS company tracking trial signups and conversion to paid plans",
    "a logistics company tracking shipment milestones and on-time delivery",
    "a streaming platform tracking content views and completion rates",
]

# Mirror of nb01's INDUSTRY_SCENARIOS keys so the Scenario dropdown can match.
INDUSTRY_SCENARIOS = {
    "consumer_social": ["a dating app tracking matches and messaging engagement"],
    "marketplace": ["a ride share app tracking request-to-acceptance match rate"],
    "ecommerce": ["an online grocery service tracking basket size and reorders"],
    "fintech": ["a neobank tracking debit swipes and the deposit funnel"],
    "b2b_saas": ["a CRM tracking pipeline coverage and won opportunities"],
    "productivity_media": ["a streaming video service tracking watch time"],
    "health_wellness": ["a telehealth platform tracking visit completion"],
    "gaming": ["a mobile game tracking session length and retention"],
    "education": ["an online course platform tracking course completion"],
    "pharmacy_care": ["a digital pharmacy tracking refill adherence rates"],
}


def _pick_scenario(scenario: Optional[str], rng: random.Random) -> str:
    """Return a scenario phrase. scenario can be None/'random', an
    INDUSTRY_SCENARIOS key, or a literal phrase already chosen upstream."""
    if not scenario or scenario == "random":
        return rng.choice(SCENARIO_THEMES)
    if scenario in INDUSTRY_SCENARIOS:
        return rng.choice(INDUSTRY_SCENARIOS[scenario])
    return scenario


# ============================================================
# Problem object
# ============================================================

@dataclass
class Problem:
    category: str
    difficulty: str
    prompt: str                       # what to compute
    setup_code: str                   # code the notebook runs to create inputs
    inputs: Dict[str, Any] = field(default_factory=dict)  # name -> live object
    expected: Any = None              # the expected result object
    solution: str = ""                # idiomatic reference solution (a string)
    result_var: str = "result"        # variable the user must assign
    scenario: str = ""
    hints: List[str] = field(default_factory=list)
    notes: str = ""                   # short explanation of the answer

    @property
    def label(self) -> str:
        return CATEGORIES.get(self.category, {}).get("label", self.category)

    @property
    def group(self) -> str:
        return CATEGORIES.get(self.category, {}).get("group", "")


# ============================================================
# Small helpers for building input frames
# ============================================================

_FIRST_NAMES = ["Ava", "Liam", "Noah", "Mia", "Zoe", "Eli", "Ruth", "Sam",
                "Ida", "Jon", "Kai", "Nia", "Omar", "Pia", "Rex", "Tess"]
_DEPTS = ["Cardiology", "Oncology", "Pediatrics", "Neurology", "Radiology"]
_CITIES = ["Austin", "Denver", "Reno", "Mesa", "Tulsa", "Akron"]


def _df_repr(df: pd.DataFrame) -> str:
    # repr of a dict that may contain np.nan would emit a bare `nan`, which is
    # not a valid name when the setup_code is exec'd. Swap it for np.nan so the
    # generated setup code runs standalone.
    body = repr(df.to_dict(orient="list")).replace("nan", "np.nan")
    return "pd.DataFrame(" + body + ")"


def _names(rng: random.Random, n: int) -> List[str]:
    return rng.sample(_FIRST_NAMES, n) if n <= len(_FIRST_NAMES) else \
        [rng.choice(_FIRST_NAMES) for _ in range(n)]


# ============================================================
# Per-category generators
# Each returns a dict with keys: prompt, setup_code, inputs, expected,
# solution, result_var, hints, notes.
# n_scale grows with difficulty (easy=small, hard=larger / more steps).
# ============================================================

def _g_pd_filter(rng, diff, scenario):
    n = {"easy": 6, "moderate": 9, "hard": 12}[diff]
    names = _names(rng, n)
    ages = [rng.randint(18, 85) for _ in range(n)]
    dept = [rng.choice(_DEPTS) for _ in range(n)]
    df = pd.DataFrame({"patient": names, "age": ages, "dept": dept})
    inputs = {"df": df}
    if diff == "easy":
        thr = 50
        prompt = (f"Scenario: {scenario}.\n\n"
                  f"From `df`, keep only the rows where `age` is greater than {thr}. "
                  f"Assign the filtered DataFrame to `result`.")
        expected = df[df["age"] > thr]
        sol = f"result = df[df['age'] > {thr}]"
        hints = ["Use a boolean mask inside df[...].",
                 f"df['age'] > {thr} returns a True/False Series."]
        notes = f"Boolean indexing keeps rows where age > {thr}."
    elif diff == "moderate":
        thr = 40
        target = rng.choice(_DEPTS)
        prompt = (f"Scenario: {scenario}.\n\n"
                  f"From `df`, keep rows where `age` >= {thr} AND `dept` == '{target}'. "
                  f"Assign to `result`.")
        expected = df[(df["age"] >= thr) & (df["dept"] == target)]
        sol = f"result = df[(df['age'] >= {thr}) & (df['dept'] == '{target}')]"
        hints = ["Combine masks with & and wrap each condition in parentheses.",
                 "Two conditions: age threshold and dept equality."]
        notes = "Two masks combined with & (parentheses are required)."
    else:
        lo, hi = 30, 65
        depts = rng.sample(_DEPTS, 2)
        prompt = (f"Scenario: {scenario}.\n\n"
                  f"From `df`, keep rows where `age` is between {lo} and {hi} inclusive "
                  f"AND `dept` is one of {depts}. Assign to `result`.")
        expected = df[df["age"].between(lo, hi) & df["dept"].isin(depts)]
        sol = (f"result = df[df['age'].between({lo}, {hi}) "
               f"& df['dept'].isin({depts})]")
        hints = ["Series.between(lo, hi) handles the range.",
                 "Series.isin([...]) handles membership in a list."]
        notes = "between() for the range, isin() for membership, combined with &."
    return dict(prompt=prompt, setup_code=f"df = {_df_repr(df)}", inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_select(rng, diff, scenario):
    n = {"easy": 6, "moderate": 8, "hard": 10}[diff]
    names = _names(rng, n)
    df = pd.DataFrame({
        "patient": names,
        "age": [rng.randint(20, 80) for _ in range(n)],
        "dept": [rng.choice(_DEPTS) for _ in range(n)],
        "visits": [rng.randint(1, 9) for _ in range(n)],
    })
    inputs = {"df": df}
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "From `df`, select just the `patient` and `visits` columns "
                  "(in that order). Assign to `result`.")
        expected = df[["patient", "visits"]]
        sol = "result = df[['patient', 'visits']]"
        hints = ["Pass a list of column names to df[...].",
                 "Order in the list controls output column order."]
        notes = "Column projection with a list of names."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Using `.loc`, select the `patient` and `age` columns for rows "
                  "where `visits` >= 3. Assign to `result`.")
        expected = df.loc[df["visits"] >= 3, ["patient", "age"]]
        sol = "result = df.loc[df['visits'] >= 3, ['patient', 'age']]"
        hints = [".loc takes [row_mask, column_list].",
                 "Row mask is df['visits'] >= 3."]
        notes = ".loc with a boolean row mask and a column list."
    else:
        k = 3
        prompt = (f"Scenario: {scenario}.\n\n"
                  f"Using `.iloc`, select the first {k} rows and the last 2 columns. "
                  "Assign to `result`.")
        expected = df.iloc[:k, -2:]
        sol = f"result = df.iloc[:{k}, -2:]"
        hints = [".iloc is purely positional: [row_slice, col_slice].",
                 "Last 2 columns is -2: on the column axis."]
        notes = ".iloc positional slicing on both axes."
    return dict(prompt=prompt, setup_code=f"df = {_df_repr(df)}", inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_sort(rng, diff, scenario):
    n = {"easy": 6, "moderate": 8, "hard": 10}[diff]
    df = pd.DataFrame({
        "patient": _names(rng, n),
        "age": [rng.randint(20, 80) for _ in range(n)],
        "visits": [rng.randint(1, 9) for _ in range(n)],
    })
    inputs = {"df": df}
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Sort `df` by `age` ascending. Assign to `result`.")
        expected = df.sort_values("age")
        sol = "result = df.sort_values('age')"
        hints = ["df.sort_values('col') sorts ascending by default."]
        notes = "Single-column ascending sort."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Sort `df` by `visits` descending. Assign to `result`.")
        expected = df.sort_values("visits", ascending=False)
        sol = "result = df.sort_values('visits', ascending=False)"
        hints = ["Pass ascending=False to reverse the order."]
        notes = "Single-column descending sort."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Sort `df` by `visits` descending, then by `age` ascending as a "
                  "tie-breaker. Assign to `result`.")
        expected = df.sort_values(["visits", "age"], ascending=[False, True])
        sol = ("result = df.sort_values(['visits', 'age'], "
               "ascending=[False, True])")
        hints = ["Pass lists to both by= and ascending=.",
                 "ascending is a list aligned to the by= columns."]
        notes = "Multi-key sort with per-key direction."
    return dict(prompt=prompt, setup_code=f"df = {_df_repr(df)}", inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_value_counts(rng, diff, scenario):
    n = {"easy": 8, "moderate": 12, "hard": 16}[diff]
    df = pd.DataFrame({
        "patient": [rng.choice(_FIRST_NAMES) for _ in range(n)],
        "dept": [rng.choice(_DEPTS) for _ in range(n)],
    })
    inputs = {"df": df}
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Count how many rows fall in each `dept`. Return the counts as a "
                  "Series (most frequent first). Assign to `result`.")
        expected = df["dept"].value_counts()
        sol = "result = df['dept'].value_counts()"
        hints = ["Series.value_counts() tallies and sorts descending."]
        notes = "value_counts returns a count-sorted Series."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Return the share (proportion) of rows in each `dept` as a Series. "
                  "Assign to `result`.")
        expected = df["dept"].value_counts(normalize=True)
        sol = "result = df['dept'].value_counts(normalize=True)"
        hints = ["Pass normalize=True to get proportions instead of counts."]
        notes = "normalize=True gives shares that sum to 1."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Return the name of the single most frequent `dept` (a string). "
                  "Assign to `result`.")
        expected = df["dept"].value_counts().index[0]
        sol = "result = df['dept'].value_counts().index[0]"
        hints = ["value_counts sorts descending, so .index[0] is the mode.",
                 "idxmax() on value_counts works too."]
        notes = "Top label of value_counts is the mode."
    return dict(prompt=prompt, setup_code=f"df = {_df_repr(df)}", inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_groupby(rng, diff, scenario):
    n = {"easy": 9, "moderate": 12, "hard": 15}[diff]
    df = pd.DataFrame({
        "dept": [rng.choice(_DEPTS) for _ in range(n)],
        "visits": [rng.randint(1, 9) for _ in range(n)],
        "cost": [round(rng.uniform(50, 500), 2) for _ in range(n)],
    })
    inputs = {"df": df}
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Compute the mean `cost` per `dept`. Return a Series indexed by "
                  "dept. Assign to `result`.")
        expected = df.groupby("dept")["cost"].mean()
        sol = "result = df.groupby('dept')['cost'].mean()"
        hints = ["df.groupby('dept')['cost'].mean()."]
        notes = "Group by dept, take the mean of cost."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "For each `dept`, compute total `visits` and mean `cost`. Name the "
                  "output columns `total_visits` and `avg_cost`. Assign the resulting "
                  "DataFrame to `result`.")
        expected = df.groupby("dept").agg(
            total_visits=("visits", "sum"),
            avg_cost=("cost", "mean"),
        )
        sol = ("result = df.groupby('dept').agg(\n"
               "    total_visits=('visits', 'sum'),\n"
               "    avg_cost=('cost', 'mean'),\n"
               ")")
        hints = ["Use named aggregation: agg(newname=(col, func)).",
                 "One entry per output column."]
        notes = "Named aggregation produces tidy, renamed columns."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Find, for each `dept`, the total `cost`, then return only the "
                  "departments whose total `cost` exceeds the overall mean of those "
                  "per-dept totals. Return a Series of those totals. Assign to `result`.")
        totals = df.groupby("dept")["cost"].sum()
        expected = totals[totals > totals.mean()]
        sol = ("totals = df.groupby('dept')['cost'].sum()\n"
               "result = totals[totals > totals.mean()]")
        hints = ["First build the per-dept totals Series.",
                 "Then filter that Series against its own mean."]
        notes = "Aggregate, then filter the aggregated Series."
    return dict(prompt=prompt, setup_code=f"df = {_df_repr(df)}", inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_merge(rng, diff, scenario):
    ids = list(range(1, {"easy": 5, "moderate": 6, "hard": 7}[diff] + 1))
    left = pd.DataFrame({"patient_id": ids,
                         "patient": _names(rng, len(ids))})
    # right has overlapping + extra ids to exercise join type
    right_ids = ids[:-1] + [max(ids) + 1]
    right = pd.DataFrame({"patient_id": right_ids,
                          "visits": [rng.randint(1, 9) for _ in right_ids]})
    inputs = {"left": left, "right": right}
    setup = f"left = {_df_repr(left)}\nright = {_df_repr(right)}"
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Inner-join `left` and `right` on `patient_id`. Assign to `result`.")
        expected = left.merge(right, on="patient_id")
        sol = "result = left.merge(right, on='patient_id')"
        hints = ["left.merge(right, on='patient_id') defaults to an inner join."]
        notes = "Inner join keeps only matching keys."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Left-join `left` with `right` on `patient_id` so every patient "
                  "stays. Assign to `result`.")
        expected = left.merge(right, on="patient_id", how="left")
        sol = "result = left.merge(right, on='patient_id', how='left')"
        hints = ["how='left' keeps all left rows; misses become NaN."]
        notes = "Left join preserves all left-side rows."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Left-join `left` with `right` on `patient_id`, then fill any "
                  "missing `visits` with 0 and cast `visits` to int. Assign to `result`.")
        m = left.merge(right, on="patient_id", how="left")
        m["visits"] = m["visits"].fillna(0).astype(int)
        expected = m
        sol = ("result = left.merge(right, on='patient_id', how='left')\n"
               "result['visits'] = result['visits'].fillna(0).astype(int)")
        hints = ["Join first, then fillna(0) the unmatched visits.",
                 "astype(int) after fillna to drop the float dtype."]
        notes = "Left join, then clean the unmatched rows."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_pivot(rng, diff, scenario):
    n = {"easy": 9, "moderate": 12, "hard": 12}[diff]
    df = pd.DataFrame({
        "dept": [rng.choice(_DEPTS[:3]) for _ in range(n)],
        "month": [rng.choice(["Jan", "Feb", "Mar"]) for _ in range(n)],
        "cost": [round(rng.uniform(50, 300), 2) for _ in range(n)],
    })
    inputs = {"df": df}
    setup = f"df = {_df_repr(df)}"
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Build a pivot table of mean `cost` with `dept` as rows and `month` "
                  "as columns. Assign to `result`.")
        expected = df.pivot_table(index="dept", columns="month", values="cost",
                                  aggfunc="mean")
        sol = ("result = df.pivot_table(index='dept', columns='month', "
               "values='cost', aggfunc='mean')")
        hints = ["pivot_table(index=, columns=, values=, aggfunc='mean')."]
        notes = "Long to wide with a mean aggregation."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Build a pivot table of total `cost` (dept rows, month columns), "
                  "filling empty cells with 0. Assign to `result`.")
        expected = df.pivot_table(index="dept", columns="month", values="cost",
                                  aggfunc="sum", fill_value=0)
        sol = ("result = df.pivot_table(index='dept', columns='month', "
               "values='cost', aggfunc='sum', fill_value=0)")
        hints = ["aggfunc='sum' and fill_value=0 for the empty cells."]
        notes = "Sum aggregation with empty cells filled."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Build a pivot table of total `cost` (dept rows, month columns, "
                  "fill empties with 0), then add a `total` column that sums each "
                  "row across months. Assign to `result`.")
        pt = df.pivot_table(index="dept", columns="month", values="cost",
                            aggfunc="sum", fill_value=0)
        pt["total"] = pt.sum(axis=1)
        expected = pt
        sol = ("result = df.pivot_table(index='dept', columns='month', "
               "values='cost', aggfunc='sum', fill_value=0)\n"
               "result['total'] = result.sum(axis=1)")
        hints = ["Pivot first, then sum across columns with axis=1.",
                 "Assign the row sums to a new 'total' column."]
        notes = "Pivot then a row-wise total column."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_apply_map(rng, diff, scenario):
    n = {"easy": 6, "moderate": 8, "hard": 8}[diff]
    df = pd.DataFrame({
        "patient": _names(rng, n),
        "dept": [rng.choice(_DEPTS) for _ in range(n)],
        "age": [rng.randint(20, 80) for _ in range(n)],
    })
    inputs = {"df": df}
    setup = f"df = {_df_repr(df)}"
    if diff == "easy":
        mapping = {d: d[:3].upper() for d in _DEPTS}
        prompt = (f"Scenario: {scenario}.\n\n"
                  f"Add a column `dept_code` by mapping `dept` through this dict: "
                  f"{mapping}. Assign the updated DataFrame to `result`.")
        expected = df.copy()
        expected["dept_code"] = df["dept"].map(mapping)
        sol = (f"mapping = {mapping}\n"
               "result = df.copy()\n"
               "result['dept_code'] = result['dept'].map(mapping)")
        hints = ["Series.map(dict) looks each value up in the dict."]
        notes = "map applies a dict lookup element-wise."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Add a column `age_band` that is 'senior' when `age` >= 65 else "
                  "'adult', using apply with a lambda. Assign to `result`.")
        expected = df.copy()
        expected["age_band"] = df["age"].apply(
            lambda a: "senior" if a >= 65 else "adult")
        sol = ("result = df.copy()\n"
               "result['age_band'] = result['age'].apply("
               "lambda a: 'senior' if a >= 65 else 'adult')")
        hints = ["Series.apply(lambda x: ...) runs the function per value."]
        notes = "apply with a conditional lambda buckets the ages."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Add a column `summary` of the form '<patient> (<dept>)' built with "
                  "a row-wise apply (axis=1). Assign to `result`.")
        expected = df.copy()
        expected["summary"] = df.apply(
            lambda r: f"{r['patient']} ({r['dept']})", axis=1)
        sol = ("result = df.copy()\n"
               "result['summary'] = result.apply("
               "lambda r: f\"{r['patient']} ({r['dept']})\", axis=1)")
        hints = ["df.apply(func, axis=1) passes each row as a Series.",
                 "Build the string from r['patient'] and r['dept']."]
        notes = "Row-wise apply combines two columns into a label."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_missing(rng, diff, scenario):
    n = {"easy": 7, "moderate": 9, "hard": 9}[diff]
    ages = [rng.randint(20, 80) for _ in range(n)]
    # punch holes
    for i in rng.sample(range(n), 2):
        ages[i] = np.nan
    cost = [round(rng.uniform(50, 300), 2) for _ in range(n)]
    for i in rng.sample(range(n), 2):
        cost[i] = np.nan
    df = pd.DataFrame({"patient": _names(rng, n), "age": ages, "cost": cost})
    inputs = {"df": df}
    setup = f"df = {_df_repr(df)}"
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Fill missing `age` values with 0. Assign the updated DataFrame to "
                  "`result`.")
        expected = df.copy()
        expected["age"] = df["age"].fillna(0)
        sol = ("result = df.copy()\n"
               "result['age'] = result['age'].fillna(0)")
        hints = ["Series.fillna(0) replaces NaN with 0."]
        notes = "fillna with a constant."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Fill missing `age` with the mean age (computed ignoring NaN). "
                  "Assign to `result`.")
        expected = df.copy()
        expected["age"] = df["age"].fillna(df["age"].mean())
        sol = ("result = df.copy()\n"
               "result['age'] = result['age'].fillna(result['age'].mean())")
        hints = ["Series.mean() skips NaN by default.",
                 "Pass that mean into fillna."]
        notes = "Mean imputation for the missing ages."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Drop every row that has a missing value in ANY column. Reset the "
                  "index with drop=True. Assign to `result`.")
        expected = df.dropna().reset_index(drop=True)
        sol = "result = df.dropna().reset_index(drop=True)"
        hints = ["dropna() removes rows with any NaN.",
                 "reset_index(drop=True) renumbers the surviving rows."]
        notes = "dropna then a clean integer index."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_newcol(rng, diff, scenario):
    n = {"easy": 6, "moderate": 8, "hard": 8}[diff]
    df = pd.DataFrame({
        "patient": _names(rng, n),
        "visits": [rng.randint(1, 9) for _ in range(n)],
        "cost": [round(rng.uniform(50, 300), 2) for _ in range(n)],
    })
    inputs = {"df": df}
    setup = f"df = {_df_repr(df)}"
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Add a column `cost_per_visit` = `cost` / `visits`. Assign the "
                  "updated DataFrame to `result`.")
        expected = df.copy()
        expected["cost_per_visit"] = df["cost"] / df["visits"]
        sol = ("result = df.copy()\n"
               "result['cost_per_visit'] = result['cost'] / result['visits']")
        hints = ["Column arithmetic is element-wise."]
        notes = "Vectorized division creates the new column."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Add a column `high_cost` that is True when `cost` is above the "
                  "mean `cost`, else False. Assign to `result`.")
        expected = df.copy()
        expected["high_cost"] = df["cost"] > df["cost"].mean()
        sol = ("result = df.copy()\n"
               "result['high_cost'] = result['cost'] > result['cost'].mean()")
        hints = ["A comparison against the column mean yields a bool Series."]
        notes = "Boolean column from a comparison to the mean."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Add a column `cost_share` = each row's `cost` divided by the total "
                  "`cost` across all rows, rounded to 3 decimals. Assign to `result`.")
        expected = df.copy()
        expected["cost_share"] = (df["cost"] / df["cost"].sum()).round(3)
        sol = ("result = df.copy()\n"
               "result['cost_share'] = (result['cost'] / "
               "result['cost'].sum()).round(3)")
        hints = ["Divide the column by its own sum for a share.",
                 "Round the resulting Series to 3 places."]
        notes = "Row share of a column total, rounded."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_rename(rng, diff, scenario):
    n = {"easy": 5, "moderate": 6, "hard": 6}[diff]
    df = pd.DataFrame({
        "pat": _names(rng, n),
        "ag": [rng.randint(20, 80) for _ in range(n)],
        "dpt": [rng.choice(_DEPTS) for _ in range(n)],
    })
    inputs = {"df": df}
    setup = f"df = {_df_repr(df)}"
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Rename the column `pat` to `patient`. Assign the renamed DataFrame "
                  "to `result`.")
        expected = df.rename(columns={"pat": "patient"})
        sol = "result = df.rename(columns={'pat': 'patient'})"
        hints = ["rename(columns={'old': 'new'})."]
        notes = "Single-column rename via a dict."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Rename `pat`->`patient`, `ag`->`age`, `dpt`->`dept`. Assign to "
                  "`result`.")
        expected = df.rename(columns={"pat": "patient", "ag": "age", "dpt": "dept"})
        sol = ("result = df.rename(columns={'pat': 'patient', "
               "'ag': 'age', 'dpt': 'dept'})")
        hints = ["One dict, several old:new pairs."]
        notes = "Multi-column rename via a dict."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Rename ALL columns to upper case using a function (not a hard-coded "
                  "dict). Assign to `result`.")
        expected = df.rename(columns=str.upper)
        sol = "result = df.rename(columns=str.upper)"
        hints = ["rename(columns=func) applies the function to each name.",
                 "str.upper is the function to pass."]
        notes = "Functional rename uppercases every column."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


def _g_pd_datetime(rng, diff, scenario):
    n = {"easy": 6, "moderate": 7, "hard": 7}[diff]
    base = [f"2026-0{rng.randint(1,9)}-{rng.randint(10,28):02d}" for _ in range(n)]
    df = pd.DataFrame({"patient": _names(rng, n), "admit": base})
    inputs = {"df": df}
    setup = f"df = {_df_repr(df)}"
    if diff == "easy":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Parse the string column `admit` into real datetimes in a new "
                  "column `admit_dt`. Assign the updated DataFrame to `result`.")
        expected = df.copy()
        expected["admit_dt"] = pd.to_datetime(df["admit"])
        sol = ("result = df.copy()\n"
               "result['admit_dt'] = pd.to_datetime(result['admit'])")
        hints = ["pd.to_datetime(series) parses the strings."]
        notes = "Parse strings into datetime64."
    elif diff == "moderate":
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Parse `admit` to datetime, then add an integer `month` column "
                  "pulled from it via the .dt accessor. Assign to `result`.")
        expected = df.copy()
        dt = pd.to_datetime(df["admit"])
        expected["month"] = dt.dt.month
        sol = ("result = df.copy()\n"
               "dt = pd.to_datetime(result['admit'])\n"
               "result['month'] = dt.dt.month")
        hints = ["After parsing, use .dt.month on the datetime Series."]
        notes = ".dt.month extracts the month integer."
    else:
        prompt = (f"Scenario: {scenario}.\n\n"
                  "Parse `admit` to datetime, then add a `weekday` column with the "
                  "weekday name (Monday, Tuesday, ...) via .dt.day_name(). Assign to "
                  "`result`.")
        expected = df.copy()
        dt = pd.to_datetime(df["admit"])
        expected["weekday"] = dt.dt.day_name()
        sol = ("result = df.copy()\n"
               "dt = pd.to_datetime(result['admit'])\n"
               "result['weekday'] = dt.dt.day_name()")
        hints = [".dt.day_name() returns the weekday label string."]
        notes = ".dt.day_name() gives the weekday name."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs,
                expected=expected, solution=sol, result_var="result",
                hints=hints, notes=notes)


# ---- numpy ----

def _g_np_create(rng, diff, scenario):
    if diff == "easy":
        stop = rng.choice([5, 6, 7, 8])
        prompt = (f"Create a 1-D array of the integers 0 up to (but not including) "
                  f"{stop} using np.arange. Assign to `result`.")
        expected = np.arange(stop)
        sol = f"result = np.arange({stop})"
        hints = ["np.arange(stop) is like range(stop) as an array."]
        notes = "arange builds an integer range array."
        setup = "import numpy as np"
    elif diff == "moderate":
        n = rng.choice([4, 5, 6])
        prompt = (f"Create an array of {n} evenly spaced values from 0 to 1 inclusive "
                  f"using np.linspace. Assign to `result`.")
        expected = np.linspace(0, 1, n)
        sol = f"result = np.linspace(0, 1, {n})"
        hints = ["np.linspace(start, stop, num) includes both endpoints."]
        notes = "linspace spreads num points across an inclusive range."
        setup = "import numpy as np"
    else:
        r, c = rng.choice([(2, 3), (3, 2), (3, 3)])
        prompt = (f"Create a {r}x{c} array filled with the value 7 (integer dtype) "
                  f"using np.full. Assign to `result`.")
        expected = np.full((r, c), 7)
        sol = f"result = np.full(({r}, {c}), 7)"
        hints = ["np.full(shape, value) fills an array of that shape."]
        notes = "full builds a constant-valued matrix."
        setup = "import numpy as np"
    return dict(prompt=prompt, setup_code=setup, inputs={}, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_np_vectorized(rng, diff, scenario):
    n = {"easy": 5, "moderate": 6, "hard": 6}[diff]
    a = np.array([rng.randint(1, 9) for _ in range(n)])
    setup = f"import numpy as np\na = np.array({a.tolist()})"
    inputs = {"a": a}
    if diff == "easy":
        prompt = ("Given array `a`, return a new array with every element doubled. "
                  "Assign to `result`.")
        expected = a * 2
        sol = "result = a * 2"
        hints = ["Scalar multiplication is element-wise."]
        notes = "Vectorized scalar multiply."
    elif diff == "moderate":
        b = np.array([rng.randint(1, 9) for _ in range(n)])
        setup += f"\nb = np.array({b.tolist()})"
        inputs["b"] = b
        prompt = ("Given arrays `a` and `b` (same length), return their element-wise "
                  "product. Assign to `result`.")
        expected = a * b
        sol = "result = a * b"
        hints = ["a * b multiplies position by position."]
        notes = "Element-wise product of two arrays."
    else:
        prompt = ("Given array `a`, return (a squared minus 1) divided by 2 as a "
                  "float array, element-wise. Assign to `result`.")
        expected = (a ** 2 - 1) / 2
        sol = "result = (a ** 2 - 1) / 2"
        hints = ["Chain element-wise ops; division promotes to float."]
        notes = "Composite vectorized expression."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_np_mask(rng, diff, scenario):
    n = {"easy": 6, "moderate": 8, "hard": 8}[diff]
    a = np.array([rng.randint(0, 20) for _ in range(n)])
    setup = f"import numpy as np\na = np.array({a.tolist()})"
    inputs = {"a": a}
    if diff == "easy":
        thr = 10
        prompt = (f"Given array `a`, return only the elements greater than {thr}. "
                  "Assign to `result`.")
        expected = a[a > thr]
        sol = f"result = a[a > {thr}]"
        hints = ["Index the array with a boolean condition: a[a > thr]."]
        notes = "Boolean mask selects matching elements."
    elif diff == "moderate":
        prompt = ("Given array `a`, return its even elements (divisible by 2). "
                  "Assign to `result`.")
        expected = a[a % 2 == 0]
        sol = "result = a[a % 2 == 0]"
        hints = ["a % 2 == 0 is the even mask."]
        notes = "Modulo mask keeps even values."
    else:
        lo, hi = 5, 15
        prompt = (f"Given array `a`, count how many elements are strictly between {lo} "
                  f"and {hi}. Return an int. Assign to `result`.")
        expected = int(((a > lo) & (a < hi)).sum())
        sol = f"result = int(((a > {lo}) & (a < {hi})).sum())"
        hints = ["Combine masks with & (parenthesize each).",
                 "Sum the boolean mask to count True values."]
        notes = "Sum of a combined boolean mask is a count."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_np_agg(rng, diff, scenario):
    if diff == "easy":
        a = np.array([rng.randint(1, 9) for _ in range(6)])
        setup = f"import numpy as np\na = np.array({a.tolist()})"
        prompt = ("Given array `a`, return the sum of all its elements as an int. "
                  "Assign to `result`.")
        expected = int(a.sum())
        sol = "result = int(a.sum())"
        hints = ["a.sum() reduces the whole array."]
        notes = "Total of a 1-D array."
        inputs = {"a": a}
    elif diff == "moderate":
        m = np.array([[rng.randint(1, 9) for _ in range(3)] for _ in range(3)])
        setup = f"import numpy as np\nm = np.array({m.tolist()})"
        prompt = ("Given 2-D array `m`, return the sum of each column as a 1-D array "
                  "(sum down the rows). Assign to `result`.")
        expected = m.sum(axis=0)
        sol = "result = m.sum(axis=0)"
        hints = ["axis=0 collapses rows, leaving one value per column."]
        notes = "Column sums use axis=0."
        inputs = {"m": m}
    else:
        m = np.array([[rng.randint(1, 9) for _ in range(3)] for _ in range(3)])
        setup = f"import numpy as np\nm = np.array({m.tolist()})"
        prompt = ("Given 2-D array `m`, return the mean of each ROW as a 1-D array. "
                  "Assign to `result`.")
        expected = m.mean(axis=1)
        sol = "result = m.mean(axis=1)"
        hints = ["axis=1 collapses columns, leaving one value per row."]
        notes = "Row means use axis=1."
        inputs = {"m": m}
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_np_reshape(rng, diff, scenario):
    if diff == "easy":
        prompt = ("Create the integers 0..11 with np.arange, then reshape them into a "
                  "3x4 array. Assign to `result`.")
        expected = np.arange(12).reshape(3, 4)
        sol = "result = np.arange(12).reshape(3, 4)"
        hints = ["arange(12) then .reshape(3, 4)."]
        notes = "Reshape a flat range into a grid."
        setup = "import numpy as np"
        return dict(prompt=prompt, setup_code=setup, inputs={}, expected=expected,
                    solution=sol, result_var="result", hints=hints, notes=notes)
    elif diff == "moderate":
        a = np.arange(12)
        setup = "import numpy as np\na = np.arange(12)"
        prompt = ("Given `a` = np.arange(12), reshape it into 6 rows and let numpy "
                  "infer the column count with -1. Assign to `result`.")
        expected = a.reshape(6, -1)
        sol = "result = a.reshape(6, -1)"
        hints = ["-1 tells reshape to compute that dimension."]
        notes = "-1 infers the remaining dimension."
        return dict(prompt=prompt, setup_code=setup, inputs={"a": a},
                    expected=expected, solution=sol, result_var="result",
                    hints=hints, notes=notes)
    else:
        m = np.arange(12).reshape(3, 4)
        setup = "import numpy as np\nm = np.arange(12).reshape(3, 4)"
        prompt = ("Given 3x4 array `m`, flatten it back to a 1-D array with .ravel(). "
                  "Assign to `result`.")
        expected = m.ravel()
        sol = "result = m.ravel()"
        hints = [".ravel() returns a flattened 1-D view."]
        notes = "ravel flattens to 1-D."
        return dict(prompt=prompt, setup_code=setup, inputs={"m": m},
                    expected=expected, solution=sol, result_var="result",
                    hints=hints, notes=notes)


def _g_np_where(rng, diff, scenario):
    n = {"easy": 6, "moderate": 7, "hard": 7}[diff]
    a = np.array([rng.randint(0, 20) for _ in range(n)])
    setup = f"import numpy as np\na = np.array({a.tolist()})"
    inputs = {"a": a}
    if diff == "easy":
        thr = 10
        prompt = (f"Given array `a`, build an array that is 1 where `a` > {thr} and 0 "
                  "otherwise, using np.where. Assign to `result`.")
        expected = np.where(a > thr, 1, 0)
        sol = f"result = np.where(a > {thr}, 1, 0)"
        hints = ["np.where(cond, if_true, if_false)."]
        notes = "where picks between two scalars on a condition."
    elif diff == "moderate":
        prompt = ("Given array `a`, build an array of labels: 'hi' where `a` >= 10 "
                  "else 'lo', using np.where. Assign to `result`.")
        expected = np.where(a >= 10, "hi", "lo")
        sol = "result = np.where(a >= 10, 'hi', 'lo')"
        hints = ["The two branches can be strings."]
        notes = "where can emit string labels."
    else:
        prompt = ("Given array `a`, return a NEW array where every element below 5 is "
                  "clamped up to 5 and everything else is unchanged, using np.where. "
                  "Assign to `result`.")
        expected = np.where(a < 5, 5, a)
        sol = "result = np.where(a < 5, 5, a)"
        hints = ["The false branch can be the array itself to keep originals."]
        notes = "where clamps a floor while passing others through."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_np_broadcast(rng, diff, scenario):
    if diff == "easy":
        a = np.array([rng.randint(1, 9) for _ in range(4)])
        k = rng.randint(2, 5)
        setup = f"import numpy as np\na = np.array({a.tolist()})"
        prompt = (f"Given array `a`, add the scalar {k} to every element (a broadcast). "
                  "Assign to `result`.")
        expected = a + k
        sol = f"result = a + {k}"
        hints = ["A scalar broadcasts against the whole array."]
        notes = "Scalar broadcasting adds k everywhere."
        inputs = {"a": a}
    elif diff == "moderate":
        m = np.array([[rng.randint(1, 9) for _ in range(3)] for _ in range(2)])
        v = np.array([rng.randint(1, 5) for _ in range(3)])
        setup = (f"import numpy as np\nm = np.array({m.tolist()})\n"
                 f"v = np.array({v.tolist()})")
        prompt = ("Given 2x3 matrix `m` and length-3 row vector `v`, add `v` to every "
                  "row of `m` by broadcasting. Assign to `result`.")
        expected = m + v
        sol = "result = m + v"
        hints = ["A (3,) vector broadcasts across each row of a (2,3) matrix."]
        notes = "Row-vector broadcast across the matrix rows."
        inputs = {"m": m, "v": v}
    else:
        col = np.array([rng.randint(1, 5) for _ in range(3)])
        row = np.array([rng.randint(1, 5) for _ in range(4)])
        setup = (f"import numpy as np\ncol = np.array({col.tolist()})\n"
                 f"row = np.array({row.tolist()})")
        prompt = ("Given length-3 `col` and length-4 `row`, build the 3x4 outer-sum "
                  "matrix where entry [i,j] = col[i] + row[j], using reshape + "
                  "broadcasting. Assign to `result`.")
        expected = col.reshape(-1, 1) + row
        sol = "result = col.reshape(-1, 1) + row"
        hints = ["Reshape col to (3,1) so it broadcasts against (4,).",
                 "A (3,1) + (4,) gives a (3,4) result."]
        notes = "Column (3,1) plus row (4,) broadcasts to (3,4)."
        inputs = {"col": col, "row": row}
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


# ---- basic python ----

def _g_py_strings(rng, diff, scenario):
    if diff == "easy":
        s = rng.choice(["patient name", "claim status", "refill due", "visit note"])
        setup = f"s = {s!r}"
        prompt = (f"Given string `s` = {s!r}, return it in upper case. Assign to "
                  "`result`.")
        expected = s.upper()
        sol = "result = s.upper()"
        hints = ["str.upper() uppercases the whole string."]
        notes = "Basic case transform."
        inputs = {"s": s}
    elif diff == "moderate":
        s = "ava,liam,noah,mia"
        setup = f"s = {s!r}"
        prompt = (f"Given string `s` = {s!r}, split it on commas into a list of names. "
                  "Assign to `result`.")
        expected = s.split(",")
        sol = "result = s.split(',')"
        hints = ["str.split(',') breaks on the comma."]
        notes = "split turns a delimited string into a list."
        inputs = {"s": s}
    else:
        s = "  Jane  Doe  "
        setup = f"s = {s!r}"
        prompt = (f"Given string `s` = {s!r} (note the extra spaces), strip the outer "
                  "whitespace, collapse the inner whitespace to a single space, and "
                  "lower-case it. Assign the cleaned string to `result`.")
        expected = " ".join(s.split()).lower()
        sol = "result = ' '.join(s.split()).lower()"
        hints = ["s.split() with no args splits on any run of whitespace.",
                 "' '.join(...) rejoins with single spaces; then .lower()."]
        notes = "split()/join() normalizes whitespace, then lower-case."
        inputs = {"s": s}
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_py_comprehension(rng, diff, scenario):
    if diff == "easy":
        nums = [rng.randint(1, 9) for _ in range(6)]
        setup = f"nums = {nums}"
        prompt = (f"Given list `nums` = {nums}, build a list of each value squared "
                  "using a list comprehension. Assign to `result`.")
        expected = [x ** 2 for x in nums]
        sol = "result = [x ** 2 for x in nums]"
        hints = ["[x ** 2 for x in nums]."]
        notes = "Comprehension maps each element."
        inputs = {"nums": nums}
    elif diff == "moderate":
        nums = [rng.randint(1, 20) for _ in range(8)]
        setup = f"nums = {nums}"
        prompt = (f"Given list `nums` = {nums}, build a list of only the even values "
                  "using a comprehension with a condition. Assign to `result`.")
        expected = [x for x in nums if x % 2 == 0]
        sol = "result = [x for x in nums if x % 2 == 0]"
        hints = ["Add an if-clause to the comprehension to filter."]
        notes = "Filtering comprehension keeps even values."
        inputs = {"nums": nums}
    else:
        words = rng.sample(_FIRST_NAMES, 5)
        setup = f"words = {words}"
        prompt = (f"Given list `words` = {words}, build a dict mapping each word to "
                  "its length using a dict comprehension. Assign to `result`.")
        expected = {w: len(w) for w in words}
        sol = "result = {w: len(w) for w in words}"
        hints = ["{w: len(w) for w in words} builds the dict."]
        notes = "Dict comprehension keys words to their lengths."
        inputs = {"words": words}
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_py_slicing(rng, diff, scenario):
    data = [rng.randint(1, 50) for _ in range(10)]
    setup = f"data = {data}"
    inputs = {"data": data}
    if diff == "easy":
        prompt = (f"Given list `data` = {data}, return the first 3 elements via "
                  "slicing. Assign to `result`.")
        expected = data[:3]
        sol = "result = data[:3]"
        hints = ["data[:3] takes index 0,1,2."]
        notes = "Head slice."
    elif diff == "moderate":
        prompt = (f"Given list `data` = {data}, return the last 3 elements via "
                  "slicing. Assign to `result`.")
        expected = data[-3:]
        sol = "result = data[-3:]"
        hints = ["data[-3:] counts from the end."]
        notes = "Tail slice."
    else:
        prompt = (f"Given list `data` = {data}, return every second element starting "
                  "from index 1 (a strided slice). Assign to `result`.")
        expected = data[1::2]
        sol = "result = data[1::2]"
        hints = ["data[start::step] with step 2 takes every other item."]
        notes = "Strided slice from index 1."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_py_sort_key(rng, diff, scenario):
    if diff == "easy":
        nums = [rng.randint(1, 50) for _ in range(7)]
        setup = f"nums = {nums}"
        prompt = (f"Given list `nums` = {nums}, return a new list sorted descending "
                  "using sorted(). Assign to `result`.")
        expected = sorted(nums, reverse=True)
        sol = "result = sorted(nums, reverse=True)"
        hints = ["sorted(nums, reverse=True)."]
        notes = "Descending sort with reverse=True."
        inputs = {"nums": nums}
    elif diff == "moderate":
        words = rng.sample(_FIRST_NAMES, 6)
        setup = f"words = {words}"
        prompt = (f"Given list `words` = {words}, sort them by length (shortest first) "
                  "using a key function. Assign to `result`.")
        expected = sorted(words, key=len)
        sol = "result = sorted(words, key=len)"
        hints = ["Pass key=len to sort by length."]
        notes = "Key function sorts by string length."
        inputs = {"words": words}
    else:
        pairs = [(rng.choice(_FIRST_NAMES), rng.randint(1, 9)) for _ in range(5)]
        setup = f"pairs = {pairs}"
        prompt = (f"Given list of (name, score) tuples `pairs` = {pairs}, sort them by "
                  "score DESCENDING using a key lambda. Assign to `result`.")
        expected = sorted(pairs, key=lambda t: t[1], reverse=True)
        sol = "result = sorted(pairs, key=lambda t: t[1], reverse=True)"
        hints = ["key=lambda t: t[1] sorts on the second tuple element.",
                 "Add reverse=True for descending."]
        notes = "Sort tuples by their second field, descending."
        inputs = {"pairs": pairs}
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


def _g_py_counting(rng, diff, scenario):
    n = {"easy": 8, "moderate": 12, "hard": 14}[diff]
    items = [rng.choice(["A", "B", "C", "D"]) for _ in range(n)]
    setup = f"items = {items}"
    inputs = {"items": items}
    if diff == "easy":
        prompt = (f"Given list `items` = {items}, count how many times 'A' appears. "
                  "Return an int. Assign to `result`.")
        expected = items.count("A")
        sol = "result = items.count('A')"
        hints = ["list.count('A') counts occurrences."]
        notes = "list.count tallies one value."
    elif diff == "moderate":
        prompt = (f"Given list `items` = {items}, build a dict mapping each distinct "
                  "value to its count, using collections.Counter. Assign a plain dict "
                  "to `result`.")
        from collections import Counter
        expected = dict(Counter(items))
        sol = ("from collections import Counter\n"
               "result = dict(Counter(items))")
        hints = ["Counter(items) tallies everything; wrap in dict()."]
        notes = "Counter tallies all distinct values."
    else:
        prompt = (f"Given list `items` = {items}, return the single most common value "
                  "(a string), using collections.Counter. Assign to `result`.")
        from collections import Counter
        expected = Counter(items).most_common(1)[0][0]
        sol = ("from collections import Counter\n"
               "result = Counter(items).most_common(1)[0][0]")
        hints = ["Counter(...).most_common(1) returns [(value, count)].",
                 "Index [0][0] pulls the value out."]
        notes = "most_common(1) gives the mode."
    return dict(prompt=prompt, setup_code=setup, inputs=inputs, expected=expected,
                solution=sol, result_var="result", hints=hints, notes=notes)


# Registry: category key -> generator function
_GENERATORS = {
    "pd_filter": _g_pd_filter,
    "pd_select": _g_pd_select,
    "pd_sort": _g_pd_sort,
    "pd_value_counts": _g_pd_value_counts,
    "pd_groupby": _g_pd_groupby,
    "pd_merge": _g_pd_merge,
    "pd_pivot": _g_pd_pivot,
    "pd_apply_map": _g_pd_apply_map,
    "pd_missing": _g_pd_missing,
    "pd_newcol": _g_pd_newcol,
    "pd_rename": _g_pd_rename,
    "pd_datetime": _g_pd_datetime,
    "np_create": _g_np_create,
    "np_vectorized": _g_np_vectorized,
    "np_mask": _g_np_mask,
    "np_agg": _g_np_agg,
    "np_reshape": _g_np_reshape,
    "np_where": _g_np_where,
    "np_broadcast": _g_np_broadcast,
    "py_strings": _g_py_strings,
    "py_comprehension": _g_py_comprehension,
    "py_slicing": _g_py_slicing,
    "py_sort_key": _g_py_sort_key,
    "py_counting": _g_py_counting,
}


# ============================================================
# Public: generate_problem
# ============================================================

def generate_problem(category: str, difficulty: str = "moderate",
                     scenario: Optional[str] = None,
                     seed: Optional[int] = None) -> Problem:
    """Build a fresh Problem for the given category and difficulty.

    category    a key in CATEGORIES
    difficulty  one of 'easy' / 'moderate' / 'hard'
    scenario    None / 'random' / an INDUSTRY_SCENARIOS key / a literal phrase
    seed        optional int for reproducible problems (None = random each call)
    """
    if category not in _GENERATORS:
        raise ValueError(f"Unknown category: {category!r}. "
                         f"Valid: {list(_GENERATORS)}")
    if difficulty not in {k for k, _ in DIFFICULTIES}:
        raise ValueError(f"Unknown difficulty: {difficulty!r}.")
    rng = random.Random(seed)
    scen = _pick_scenario(scenario, rng)
    spec = _GENERATORS[category](rng, difficulty, scen)
    return Problem(
        category=category,
        difficulty=difficulty,
        prompt=spec["prompt"],
        setup_code=spec["setup_code"],
        inputs=spec["inputs"],
        expected=spec["expected"],
        solution=spec["solution"],
        result_var=spec.get("result_var", "result"),
        scenario=scen,
        hints=spec.get("hints", []),
        notes=spec.get("notes", ""),
    )


# ============================================================
# Public: checker
# ============================================================

def _normalize_for_compare(obj: Any) -> Any:
    # Reset index on DataFrame/Series so a different index (common after
    # filtering) does not cause a false mismatch; the user is graded on the
    # values, not on incidental index labels.
    if isinstance(obj, pd.DataFrame):
        return obj.reset_index(drop=True)
    if isinstance(obj, pd.Series):
        return obj.reset_index(drop=True)
    return obj


def check_answer(problem: Problem, user_result: Any) -> Tuple[bool, str]:
    """Compare the user's result to the expected output.

    Returns (ok, message). Handles DataFrame / Series / ndarray / scalar /
    list / dict robustly. DataFrames and Series are compared on values with
    the index reset, so an incidental index difference does not fail.
    """
    expected = problem.expected
    if user_result is None:
        return False, (f"`{problem.result_var}` is None. Assign your answer to "
                       f"`{problem.result_var}`.")

    # Type family must roughly match to give a clean message.
    exp_kind = type(expected).__name__
    got_kind = type(user_result).__name__

    try:
        if isinstance(expected, pd.DataFrame):
            if not isinstance(user_result, pd.DataFrame):
                return False, f"Expected a DataFrame, got a {got_kind}."
            e = _normalize_for_compare(expected)
            u = _normalize_for_compare(user_result)
            pdt.assert_frame_equal(e, u, check_dtype=False, check_like=False)
            return True, "Correct. DataFrame matches the expected output."

        if isinstance(expected, pd.Series):
            if not isinstance(user_result, pd.Series):
                return False, f"Expected a Series, got a {got_kind}."
            e = _normalize_for_compare(expected)
            u = _normalize_for_compare(user_result)
            # Compare values and (for value_counts) name; ignore the index name.
            pdt.assert_series_equal(e, u, check_dtype=False, check_names=False)
            return True, "Correct. Series matches the expected output."

        if isinstance(expected, np.ndarray):
            ua = np.asarray(user_result)
            if ua.shape != expected.shape:
                return False, (f"Shape mismatch: expected {expected.shape}, "
                               f"got {ua.shape}.")
            if np.issubdtype(expected.dtype, np.number) and \
               np.issubdtype(ua.dtype, np.number):
                if np.allclose(ua, expected, equal_nan=True):
                    return True, "Correct. Array matches the expected output."
                return False, "Array values do not match."
            if np.array_equal(ua.astype(str), expected.astype(str)):
                return True, "Correct. Array matches the expected output."
            return False, "Array values do not match."

        if isinstance(expected, dict):
            if user_result == expected:
                return True, "Correct. Dict matches the expected output."
            return False, f"Dict mismatch.\nExpected: {expected}\nGot:      {user_result}"

        if isinstance(expected, (list, tuple)):
            if list(user_result) == list(expected):
                return True, "Correct. Sequence matches the expected output."
            return False, (f"Sequence mismatch.\nExpected: {expected}\n"
                           f"Got:      {user_result}")

        # scalars (int / float / str / numpy scalar / bool)
        if isinstance(expected, float) or isinstance(user_result, float):
            try:
                if np.isclose(float(user_result), float(expected)):
                    return True, "Correct. Value matches the expected output."
            except (TypeError, ValueError):
                pass
            return False, f"Expected {expected!r}, got {user_result!r}."
        if user_result == expected:
            return True, "Correct. Value matches the expected output."
        return False, f"Expected {expected!r} ({exp_kind}), got {user_result!r} ({got_kind})."

    except AssertionError as e:
        return False, f"Mismatch:\n{e}"
    except Exception as e:
        return False, f"Could not compare results: {e}"


# ============================================================
# Public: renderers
# ============================================================

def _obj_to_html(obj: Any) -> str:
    if isinstance(obj, pd.DataFrame):
        return obj.to_html(index=True, border=0, classes="ex-out")
    if isinstance(obj, pd.Series):
        return obj.to_frame(name=(obj.name or "value")).to_html(border=0,
                                                                classes="ex-out")
    if isinstance(obj, np.ndarray):
        return f"<pre style='margin:0;'>{np.array2string(obj)}</pre>"
    return f"<pre style='margin:0;'>{repr(obj)}</pre>"


def render_problem_html(problem: Problem) -> str:
    """Return an HTML card showing the prompt, the input objects, and the
    expected output shape."""
    parts = []
    inputs_html = ""
    for name, obj in problem.inputs.items():
        inputs_html += (f"<div style='margin:6px 0;'><code>{name}</code>"
                        f"{_obj_to_html(obj)}</div>")
    if not inputs_html:
        inputs_html = "<div style='color:#57606a;'><i>No input objects; build the value yourself.</i></div>"
    expected_html = _obj_to_html(problem.expected)
    prompt_html = problem.prompt.replace("\n\n", "<br><br>").replace("\n", "<br>")
    diff_label = dict(DIFFICULTIES).get(problem.difficulty, problem.difficulty)
    parts.append(f'''
    <div style="border:1px solid #d0d7de; border-radius:6px; padding:16px; background:#fafbfc;">
      <div style="font-size:11px; color:#57606a; margin-bottom:8px;">
        {problem.group} &middot; {problem.label} &middot; {diff_label}
      </div>
      <h4 style="margin:0 0 10px;">Prompt</h4>
      <div style="line-height:1.5;">{prompt_html}</div>
      <h4 style="margin-top:18px;">Input</h4>
      {inputs_html}
      <h4 style="margin-top:18px;">Expected output (assign to <code>{problem.result_var}</code>)</h4>
      {expected_html}
    </div>
    ''')
    return "".join(parts)


def render_solution_html(problem: Problem) -> str:
    """Return an HTML block showing the reference solution and a short note."""
    import html as _html
    sol = _html.escape(problem.solution)
    note = _html.escape(problem.notes or "")
    return (
        f'<div style="border:1px solid #d0d7de; border-radius:6px; padding:10px 14px; '
        f'background:#f6f8fa; margin-top:6px;">'
        f'<div style="font-weight:600; margin-bottom:6px; font-size:13px; color:#0969da;">'
        f'Reference solution &middot; {problem.label} ({problem.difficulty})</div>'
        f'<pre style="margin:0; background:#282a36; color:#f8f8f2; padding:10px 12px; '
        f'border-radius:4px; font: 13px/1.5 ui-monospace, Consolas, Menlo, monospace; '
        f'overflow-x:auto; white-space:pre;">{sol}</pre>'
        f'<div style="margin-top:8px; color:#57606a; font-size:13px;">{note}</div>'
        f'</div>'
    )
