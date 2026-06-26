"""
py_patterns_build.py

Builds folders/sql/python_problem_patterns.html, mirroring the layout of
folders/sql/sql_problem_patterns.html, for the pandas / numpy / basic-Python
patterns in nb02_python_practice.ipynb (engine nb02_python_drill_utils.py).

- Reuses the SQL playbook's <head> verbatim (identical CSS + site theme), only
  changing the <title> and appending a small extra <style> that extends the
  card-standardize rules to the python tab ids.
- Reuses the SQL playbook's JS engine (tab nav, collapsible cards, jumpToRecipe,
  deep-link, itreeTable + renderITree).
- Worked examples come from py_patterns_examples.json (engine-derived, exact).
- Signal words / core templates / gotchas are authored here per category.

Style rules honored: no em-dashes or en-dashes in new prose; hyphens only for
compound nouns.

Run:  python3 py_patterns_build.py
"""
import html
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SQL_HTML = os.path.join(REPO, "folders", "sql", "sql_problem_patterns.html")
OUT_HTML = os.path.join(REPO, "folders", "sql", "python_problem_patterns.html")
EXAMPLES = os.path.join(HERE, "py_patterns_examples.json")

DIFF_LABELS = [("easy", "Easy", "#2e7d32"),
               ("moderate", "Moderate", "#e65100"),
               ("hard", "Hard", "#b71c1c")]

GROUP_TABS = [
    ("tab-pandas", "pandas", "pandas Recipes"),
    ("tab-numpy", "numpy", "numpy Recipes"),
    ("tab-python", "python", "Python Recipes"),
]

GROUP_BLURB = {
    "pandas": ("The interview core. These twelve cards mirror the most common "
               "pandas interview questions: filter, sort and top-N, "
               "groupby and aggregate, merge, pivot, datetime, and string "
               "cleaning. Read the expected output, then match a template."),
    "numpy": ("Vectorized array work. Element-wise math, boolean masks, axis "
              "reductions, reshaping, np.where, and broadcasting. These come up "
              "in feature engineering and quick numeric checks."),
    "python": ("Plain-Python fundamentals an analyst still needs: string "
               "cleaning, comprehensions, slicing, sorting with a key, and "
               "counting with Counter."),
}


def esc(s):
    """HTML-escape text/code for safe placement in the body (escapes < > &)."""
    return html.escape(str(s), quote=False)


# ============================================================
# Authored per-category content: signal words, core template, gotchas.
# Templates use a leading comment line then the canonical call(s).
# ============================================================
CONTENT = {
    # ---------------- pandas ----------------
    "pd_filter": {
        "signal": ["keep rows where", "only the rows", "filter", "where age >",
                   "between", "is one of", "exclude"],
        "template": "# one condition\nresult = df[df['col'] > value]\n\n"
                    "# AND / OR: wrap each condition, combine with & or |\n"
                    "result = df[(df['a'] >= x) & (df['b'] == 'Cardiology')]\n\n"
                    "# range + membership\n"
                    "result = df[df['age'].between(30, 65) & df['dept'].isin(['Oncology', 'Neurology'])]",
        "gotchas": [
            "Each condition needs its own parentheses before & or |. "
            "df['a'] > x & df['b'] == y parses as df['a'] > (x & df['b']) == y and errors.",
            "Use & and | (element-wise), not the Python keywords and / or, "
            "which try to take the truth value of a whole Series and raise.",
            "between(lo, hi) is inclusive on both ends; isin([...]) takes a list."],
    },
    "pd_select": {
        "signal": ["select columns", "just the columns", "pick rows and columns",
                   "first N rows", "last 2 columns", "by label", "by position"],
        "template": "# columns by name (a list keeps order)\n"
                    "result = df[['patient', 'visits']]\n\n"
                    "# label-based rows + columns\n"
                    "result = df.loc[df['visits'] >= 3, ['patient', 'age']]\n\n"
                    "# purely positional\n"
                    "result = df.iloc[:3, -2:]",
        "gotchas": [
            "df['col'] returns a Series; df[['col']] returns a one-column DataFrame.",
            ".loc is label-based and end-inclusive; .iloc is position-based and "
            "end-exclusive. Mixing them up shifts your rows by one.",
            "The order of names in the list controls the output column order."],
    },
    "pd_sort": {
        "signal": ["sort by", "order by", "ascending", "descending",
                   "highest first", "tie-breaker"],
        "template": "# single key, ascending by default\n"
                    "result = df.sort_values('age')\n\n"
                    "# descending\n"
                    "result = df.sort_values('visits', ascending=False)\n\n"
                    "# multi-key with per-key direction\n"
                    "result = df.sort_values(['visits', 'age'], ascending=[False, True])",
        "gotchas": [
            "sort_values returns a new frame; it does not sort in place unless "
            "you pass inplace=True.",
            "For a multi-key sort, ascending is a list aligned position by "
            "position to the by= list.",
            "Sorting keeps the old index labels. Add .reset_index(drop=True) if "
            "you want a clean 0..n-1 index."],
    },
    "pd_value_counts": {
        "signal": ["how many of each", "count per category", "tally",
                   "most frequent", "share of", "proportion", "the mode"],
        "template": "# counts, most frequent first\n"
                    "result = df['dept'].value_counts()\n\n"
                    "# shares that sum to 1\n"
                    "result = df['dept'].value_counts(normalize=True)\n\n"
                    "# the single most common label\n"
                    "result = df['dept'].value_counts().index[0]",
        "gotchas": [
            "value_counts drops NaN by default; pass dropna=False to count it.",
            "It already sorts descending, so .index[0] is the mode. idxmax() works too.",
            "normalize=True gives proportions, not percentages; multiply by 100 yourself."],
    },
    "pd_groupby": {
        "signal": ["for each", "per group", "by department", "total per",
                   "average per", "named output columns"],
        "template": "# one aggregate -> Series indexed by the key\n"
                    "result = df.groupby('dept')['cost'].mean()\n\n"
                    "# named aggregation -> tidy renamed columns\n"
                    "result = df.groupby('dept').agg(\n"
                    "    total_visits=('visits', 'sum'),\n"
                    "    avg_cost=('cost', 'mean'),\n"
                    ")\n\n"
                    "# aggregate, then filter the aggregated Series\n"
                    "totals = df.groupby('dept')['cost'].sum()\n"
                    "result = totals[totals > totals.mean()]",
        "gotchas": [
            "groupby('k')['c'].mean() returns a Series indexed by k; reset_index() "
            "if the grader wants a flat DataFrame.",
            "Named aggregation agg(new=(col, func)) is the clean way to rename in "
            "one step. Avoid the old dict-of-lists form.",
            "To filter groups by a group statistic, aggregate first, then index "
            "the result; do not try to do it all inside agg."],
    },
    "pd_merge": {
        "signal": ["join", "combine on", "look up from the other table",
                   "keep every patient", "match on id"],
        "template": "# inner join (only matching keys)\n"
                    "result = left.merge(right, on='patient_id')\n\n"
                    "# left join keeps every left row; misses become NaN\n"
                    "result = left.merge(right, on='patient_id', how='left')\n\n"
                    "# clean the unmatched rows after the join\n"
                    "result['visits'] = result['visits'].fillna(0).astype(int)",
        "gotchas": [
            "merge defaults to how='inner'. State how='left' explicitly when "
            "every left row must survive.",
            "A left join fills misses with NaN, which promotes an int column to "
            "float. fillna then astype(int) to get integers back.",
            "If both frames share a non-key column, merge adds _x / _y suffixes; "
            "rename or drop them."],
    },
    "pd_pivot": {
        "signal": ["pivot", "rows by ... columns by", "wide grid",
                   "matrix of", "fill empty cells", "row total"],
        "template": "# long -> wide, mean per cell\n"
                    "result = df.pivot_table(index='dept', columns='month',\n"
                    "                        values='cost', aggfunc='mean')\n\n"
                    "# sum with empty cells filled\n"
                    "result = df.pivot_table(index='dept', columns='month',\n"
                    "                        values='cost', aggfunc='sum', fill_value=0)\n\n"
                    "# add a row-wise total across the month columns\n"
                    "result['total'] = result.sum(axis=1)",
        "gotchas": [
            "pivot_table aggregates duplicates; plain pivot raises on duplicate "
            "index/column pairs. Prefer pivot_table when unsure.",
            "fill_value=0 fills only the empty grid cells, not pre-existing NaN "
            "in the data.",
            "axis=1 sums across columns (a per-row total); axis=0 sums down rows."],
    },
    "pd_apply_map": {
        "signal": ["map each value", "bucket into", "label rows", "derive from",
                   "build a string from two columns", "lambda"],
        "template": "# dict lookup per value\n"
                    "result['dept_code'] = df['dept'].map(mapping)\n\n"
                    "# conditional bucket per value\n"
                    "result['age_band'] = df['age'].apply(lambda a: 'senior' if a >= 65 else 'adult')\n\n"
                    "# row-wise: each row arrives as a Series\n"
                    "result['summary'] = df.apply(lambda r: f\"{r['patient']} ({r['dept']})\", axis=1)",
        "gotchas": [
            "Series.map is for a dict or a 1-to-1 function; Series.apply runs any "
            "function per element. df.apply(..., axis=1) runs per row.",
            "Row-wise apply is slow on large frames. Reach for vectorized ops or "
            "np.where first; use apply when the logic does not vectorize.",
            "map returns NaN for keys missing from the dict; check your mapping "
            "covers every value."],
    },
    "pd_missing": {
        "signal": ["missing", "NaN", "fill", "impute", "drop rows with",
                   "mean of the column"],
        "template": "# fill with a constant\n"
                    "result['age'] = df['age'].fillna(0)\n\n"
                    "# mean imputation (mean skips NaN)\n"
                    "result['age'] = df['age'].fillna(df['age'].mean())\n\n"
                    "# drop any row with a NaN, then renumber\n"
                    "result = df.dropna().reset_index(drop=True)",
        "gotchas": [
            "Series.mean(), .sum(), etc. skip NaN by default, so the imputed mean "
            "ignores the holes correctly.",
            "dropna() removes a row if ANY column is NaN; pass subset=[...] to "
            "limit which columns count.",
            "After dropna the index has gaps; reset_index(drop=True) gives a "
            "clean 0..n-1 index without keeping the old one as a column."],
    },
    "pd_newcol": {
        "signal": ["add a column", "compute", "per visit", "share of total",
                   "flag rows above the mean", "rounded"],
        "template": "# element-wise arithmetic\n"
                    "result['cost_per_visit'] = df['cost'] / df['visits']\n\n"
                    "# boolean column from a comparison to a statistic\n"
                    "result['high_cost'] = df['cost'] > df['cost'].mean()\n\n"
                    "# share of a column total, rounded\n"
                    "result['cost_share'] = (df['cost'] / df['cost'].sum()).round(3)",
        "gotchas": [
            "Column math is element-wise and aligns on the index. Assigning a "
            "misaligned Series can introduce NaN.",
            "Work on df.copy() if you must not mutate the input the grader passed in.",
            "Dividing by a column sum gives a share; multiply by 100 only if the "
            "prompt asks for a percentage."],
    },
    "pd_rename": {
        "signal": ["rename", "relabel columns", "to a target naming",
                   "upper case the headers"],
        "template": "# one or several explicit renames\n"
                    "result = df.rename(columns={'pat': 'patient', 'ag': 'age'})\n\n"
                    "# functional rename of every column\n"
                    "result = df.rename(columns=str.upper)",
        "gotchas": [
            "rename(columns={...}) leaves unlisted columns untouched, which is "
            "usually what you want.",
            "Pass a function (columns=str.upper) to transform every header at "
            "once instead of hard-coding a dict.",
            "rename returns a new frame; the original keeps its old names."],
    },
    "pd_datetime": {
        "signal": ["parse the date", "to datetime", "the month", "weekday name",
                   "extract the year", "string column of dates"],
        "template": "# parse strings to datetime64\n"
                    "result['admit_dt'] = pd.to_datetime(df['admit'])\n\n"
                    "# pull a part with the .dt accessor\n"
                    "result['month'] = pd.to_datetime(df['admit']).dt.month\n\n"
                    "# weekday name\n"
                    "result['weekday'] = pd.to_datetime(df['admit']).dt.day_name()",
        "gotchas": [
            "You must parse to datetime first; the .dt accessor fails on a plain "
            "object/string column.",
            ".dt.month is an integer (1-12); .dt.day_name() and .dt.month_name() "
            "return label strings.",
            "Pass format='...' to pd.to_datetime for non-ISO inputs to avoid slow "
            "inference and wrong day/month swaps."],
    },
    # ---------------- numpy ----------------
    "np_create": {
        "signal": ["create an array", "integers 0 up to", "evenly spaced",
                   "filled with", "arange", "linspace", "full"],
        "template": "# integer range (stop exclusive)\n"
                    "result = np.arange(8)\n\n"
                    "# N evenly spaced points, both ends included\n"
                    "result = np.linspace(0, 1, 5)\n\n"
                    "# constant-filled matrix\n"
                    "result = np.full((3, 3), 7)",
        "gotchas": [
            "np.arange(stop) excludes stop, like range. np.linspace includes both "
            "endpoints.",
            "linspace's third argument is the COUNT of points, not the step.",
            "np.full takes the shape as a tuple: np.full((r, c), value)."],
    },
    "np_vectorized": {
        "signal": ["every element", "element-wise", "double each", "product of",
                   "without a loop"],
        "template": "# scalar broadcast over the whole array\n"
                    "result = a * 2\n\n"
                    "# element-wise between two same-length arrays\n"
                    "result = a * b\n\n"
                    "# composite expression (division promotes to float)\n"
                    "result = (a ** 2 - 1) / 2",
        "gotchas": [
            "Vectorized ops apply position by position; no Python loop is needed "
            "or wanted.",
            "Integer division by a Python int with / always yields float; use // "
            "for floor division.",
            "Two arrays must be the same shape (or broadcast-compatible) or numpy "
            "raises a shape error."],
    },
    "np_mask": {
        "signal": ["elements greater than", "even elements", "select where",
                   "count how many", "boolean condition"],
        "template": "# keep elements matching a condition\n"
                    "result = a[a > 10]\n\n"
                    "# modulo mask (even values)\n"
                    "result = a[a % 2 == 0]\n\n"
                    "# count matches: sum the boolean mask\n"
                    "result = int(((a > 5) & (a < 15)).sum())",
        "gotchas": [
            "Combine masks with & and |, each side parenthesized, just like in "
            "pandas.",
            "A boolean array sums to the count of True values, so mask.sum() is "
            "a count.",
            "Indexing with a boolean array returns a copy, not a view."],
    },
    "np_agg": {
        "signal": ["sum of all", "sum of each column", "mean of each row",
                   "reduce along", "axis"],
        "template": "# reduce the whole array\n"
                    "result = int(a.sum())\n\n"
                    "# column sums (collapse rows)\n"
                    "result = m.sum(axis=0)\n\n"
                    "# row means (collapse columns)\n"
                    "result = m.mean(axis=1)",
        "gotchas": [
            "axis=0 collapses DOWN the rows, leaving one value per column. axis=1 "
            "collapses ACROSS the columns, one value per row.",
            "No axis reduces the entire array to a scalar.",
            "numpy scalars are not plain ints; wrap in int() if the grader wants "
            "a Python int."],
    },
    "np_reshape": {
        "signal": ["reshape", "into a 3x4", "infer the dimension", "flatten",
                   "ravel"],
        "template": "# flat range into a grid\n"
                    "result = np.arange(12).reshape(3, 4)\n\n"
                    "# let numpy infer one dimension with -1\n"
                    "result = a.reshape(6, -1)\n\n"
                    "# flatten back to 1-D\n"
                    "result = m.ravel()",
        "gotchas": [
            "reshape needs the total element count to match: 3x4 must hold 12 "
            "values.",
            "-1 tells numpy to compute that one dimension from the rest. Only one "
            "-1 is allowed.",
            "ravel returns a flattened view when possible; flatten always copies."],
    },
    "np_where": {
        "signal": ["1 where ... else 0", "label hi/lo", "clamp", "pick between",
                   "conditional value"],
        "template": "# pick between two scalars on a condition\n"
                    "result = np.where(a > 10, 1, 0)\n\n"
                    "# the branches can be strings\n"
                    "result = np.where(a >= 10, 'hi', 'lo')\n\n"
                    "# pass the array itself to keep originals (clamp a floor)\n"
                    "result = np.where(a < 5, 5, a)",
        "gotchas": [
            "np.where(cond, if_true, if_false) returns a new array; it does not "
            "modify in place.",
            "Both branches broadcast, so one can be the array itself to leave "
            "non-matching elements unchanged.",
            "For more than two outcomes, nest np.where or use np.select."],
    },
    "np_broadcast": {
        "signal": ["add a scalar", "add to every row", "outer sum",
                   "different shapes", "reshape to broadcast"],
        "template": "# scalar broadcasts everywhere\n"
                    "result = a + 3\n\n"
                    "# a (3,) row vector broadcasts across each row of a (2,3)\n"
                    "result = m + v\n\n"
                    "# (3,1) + (4,) -> (3,4) outer sum\n"
                    "result = col.reshape(-1, 1) + row",
        "gotchas": [
            "Broadcasting aligns shapes from the RIGHT; dimensions must be equal "
            "or one of them 1.",
            "Reshape a length-n vector to (n, 1) to make it broadcast down rows "
            "instead of across columns.",
            "A (3,1) plus a (4,) gives a (3,4) grid, the classic outer-sum trick."],
    },
    # ---------------- python ----------------
    "py_strings": {
        "signal": ["upper case", "split on", "strip whitespace", "collapse spaces",
                   "lower-case", "clean the string"],
        "template": "# case transform\n"
                    "result = s.upper()\n\n"
                    "# split a delimited string into a list\n"
                    "result = s.split(',')\n\n"
                    "# normalize whitespace, then lower-case\n"
                    "result = ' '.join(s.split()).lower()",
        "gotchas": [
            "s.split() with no argument splits on any run of whitespace and drops "
            "empty pieces; s.split(' ') keeps them.",
            "' '.join(s.split()) is the idiom to collapse runs of internal "
            "whitespace to single spaces.",
            "Strings are immutable; every method returns a new string."],
    },
    "py_comprehension": {
        "signal": ["build a list of", "each value squared", "only the even",
                   "map word to length", "one expression"],
        "template": "# map each element\n"
                    "result = [x ** 2 for x in nums]\n\n"
                    "# filter with an if-clause\n"
                    "result = [x for x in nums if x % 2 == 0]\n\n"
                    "# dict comprehension\n"
                    "result = {w: len(w) for w in words}",
        "gotchas": [
            "The if-clause for filtering goes at the END: [x for x in xs if cond]. "
            "A conditional VALUE goes at the front: [a if c else b for x in xs].",
            "{k: v for ...} builds a dict; [ ... ] builds a list; ( ... ) builds a "
            "generator, not a tuple.",
            "Comprehensions read left to right: output expression, then for, then "
            "if."],
    },
    "py_slicing": {
        "signal": ["first N", "last N", "every second", "sub-sequence",
                   "start:stop:step"],
        "template": "# head\n"
                    "result = data[:3]\n\n"
                    "# tail\n"
                    "result = data[-3:]\n\n"
                    "# strided: every second item from index 1\n"
                    "result = data[1::2]",
        "gotchas": [
            "Slicing is start:stop:step with stop exclusive. data[:3] is indices "
            "0, 1, 2.",
            "Negative indices count from the end; data[-3:] is the last three.",
            "Slicing a list returns a new list (a shallow copy)."],
    },
    "py_sort_key": {
        "signal": ["sort descending", "by length", "by the second field",
                   "key function", "reverse"],
        "template": "# descending\n"
                    "result = sorted(nums, reverse=True)\n\n"
                    "# by a key function\n"
                    "result = sorted(words, key=len)\n\n"
                    "# tuples by their second element, descending\n"
                    "result = sorted(pairs, key=lambda t: t[1], reverse=True)",
        "gotchas": [
            "sorted(...) returns a new list; list.sort() sorts in place and "
            "returns None.",
            "key takes a function applied to each item; do not call it (key=len, "
            "not key=len()).",
            "Python's sort is stable, so equal keys keep their original order."],
    },
    "py_counting": {
        "signal": ["how many times", "count occurrences", "tally", "most common",
                   "Counter"],
        "template": "# count one value\n"
                    "result = items.count('A')\n\n"
                    "# tally everything\n"
                    "from collections import Counter\n"
                    "result = dict(Counter(items))\n\n"
                    "# the single most common value\n"
                    "result = Counter(items).most_common(1)[0][0]",
        "gotchas": [
            "list.count(x) counts one value; Counter tallies them all in one pass.",
            "Counter(items).most_common(1) returns a list [(value, count)], so "
            "index [0][0] for the value.",
            "A Counter is a dict subclass; wrap in dict() if the grader compares "
            "against a plain dict."],
    },
}


# ============================================================
# HTML helpers
# ============================================================
def code_block(text):
    return ('<pre class="code-block"><code>' + esc(text) +
            "</code></pre>")


def pre_plain(text):
    return ('<pre style="margin:0; background:#f6f8fa; border:1px solid #e1e4e8; '
            'border-radius:4px; padding:10px 12px; overflow-x:auto; '
            "font: 0.95rem/1.5 'Courier New', Consolas, monospace; "
            'color:#24292f; white-space:pre;">' + esc(text) + "</pre>")


def diff_badge(color, label):
    return ('<span style="display: inline-block; background-color: ' + color +
            '; color: white; padding: 4px 10px; border-radius: 3px; '
            'font-size: 1.328rem; font-weight: 600;">' + label + "</span>")


def helper_badge(text):
    # purple 6a1b9a triggers the cw-standardize "helper card" light styling
    return ('<span style="display: inline-block; background-color: #6a1b9a; '
            'color: white; padding: 4px 10px; border-radius: 3px; '
            'font-size: 1.2rem; font-weight: 600;">' + text + "</span>")


def signal_words_block(words):
    chips = " ".join('<code>' + esc(w) + "</code>" for w in words)
    return ('<div style="margin-bottom: 15px;">'
            "<p><strong>Signal words in the prompt:</strong> " + chips + "</p>"
            "</div>")


def gotcha_list(items):
    lis = "".join("<li>" + esc(x) + "</li>" for x in items)
    return ('<p style="margin-top:18px;"><strong>Common gotchas</strong></p>'
            '<ul class="gotcha-list" style="margin: 6px 0 0 20px; line-height:1.7;">'
            + lis + "</ul>")


def worked_example_tile(cat, diff_key, diff_label, color, ex):
    """One Easy/Moderate/Hard worked-example tile."""
    title = ('<h3 class="problem-card-title" style="margin:0; display:flex; '
             'align-items:center; gap:12px;">' + diff_badge(color, diff_label) +
             '<span>' + esc(ex["notes"] or "Worked example") + "</span></h3>")
    inputs_html = ""
    if ex["inputs"]:
        for inp in ex["inputs"]:
            inputs_html += ('<div style="margin:6px 0;"><code>' + esc(inp["name"]) +
                            '</code> <span style="color:#57606a; font-size:0.95rem;">(' +
                            esc(inp["shape"]) + ")</span>" + pre_plain(inp["text"]) +
                            "</div>")
    else:
        inputs_html = ('<div style="color:#57606a;"><em>No input objects; build '
                       "the value yourself.</em></div>")
    hints_html = ""
    if ex["hints"]:
        lis = "".join("<li>" + esc(h) + "</li>" for h in ex["hints"])
        hints_html = ('<details style="margin-top:10px;"><summary>Hints</summary>'
                      '<div class="solution-content"><ul style="margin:0 0 0 18px; '
                      'line-height:1.7;">' + lis + "</ul></div></details>")
    body = (
        '<div class="problem-card-content">'
        '<p style="color:#57606a; font-size:1.05rem; margin:0 0 8px;"><strong>Scenario:</strong> '
        + esc(ex["scenario"]) + "</p>"
        "<p><strong>Task:</strong> " + esc(ex["prompt"]) + "</p>"
        '<p style="margin-top:12px;"><strong>Input</strong></p>' + inputs_html +
        '<p style="margin-top:12px;"><strong>Expected output</strong> '
        '<span style="color:#57606a; font-size:0.95rem;">(assign to <code>'
        + esc(ex["result_var"]) + "</code>, " + esc(ex["expected_shape"]) +
        ")</span></p>" + pre_plain(ex["expected_text"]) +
        '<details style="margin-top:12px;"><summary>Reference solution</summary>'
        '<div class="solution-content">' + code_block(ex["solution"]) +
        ('<p style="margin:8px 0 0; color:#57606a;">' + esc(ex["notes"]) + "</p>"
         if ex["notes"] else "") + "</div></details>" +
        hints_html +
        "</div>")
    excerpt = ('<div class="problem-card-excerpt"><p>' + esc(ex["prompt"][:120]) +
               ("..." if len(ex["prompt"]) > 120 else "") + "</p></div>")
    return ('<div class="problem-card collapsed" style="margin:0 0 8px 0;">'
            '<div class="problem-card-header">' + title +
            '<span class="problem-toggle">&#9660;</span></div>' +
            excerpt + body + "</div>")


def recipe_card(cat, data, examples):
    c = CONTENT[cat]
    label = data["label"]
    group = data["group"]
    blurb = data["blurb"]
    # header
    header = ('<div class="problem-card-header">'
              '<h3 class="problem-card-title">'
              '<span style="display:inline-block; background-color:#455a64; '
              'color:white; padding:3px 9px; border-radius:3px; font-size:1.1rem; '
              'font-weight:600; margin-right:8px;">' + esc(group) + "</span>" +
              esc(label) + "</h3>"
              '<span class="count-badge">3 levels</span>'
              '<span class="problem-toggle">&#9660;</span></div>')
    excerpt = '<div class="problem-card-excerpt"><p>' + esc(blurb) + "</p></div>"

    # signal words + core call (the "div[style*=margin-bottom: 15px]" intro)
    intro = signal_words_block(c["signal"])

    # template helper card
    template_card = (
        '<div class="problem-card collapsed" style="margin: 12px 0;">'
        '<div class="problem-card-header">'
        '<h3 class="problem-card-title" style="margin:0; display:flex; '
        'align-items:center; gap:12px;">' + helper_badge("TEMPLATE") +
        "<span>Pattern template</span></h3>"
        '<span class="problem-toggle">&#9660;</span></div>'
        '<div class="problem-card-excerpt"><p>The canonical call(s) for this '
        "pattern. Copy, then swap the column and value names.</p></div>"
        '<div class="problem-card-content">' + code_block(c["template"]) +
        "</div></div>")

    # worked example tiles
    tiles = ('<div class="problem-card collapsed qtype-group" style="margin: 12px 0;">'
             '<div class="problem-card-header">'
             '<h3 class="problem-card-title" style="margin:0;">Worked examples '
             "(Easy / Moderate / Hard)</h3>"
             '<span class="count-badge">3 problems</span>'
             '<span class="problem-toggle">&#9660;</span></div>'
             '<div class="problem-card-excerpt"><p>Three engine-generated '
             "problems, one per difficulty, with input, expected output, and a "
             "reference solution.</p></div>"
             '<div class="problem-card-content">')
    for dk, dl, color in DIFF_LABELS:
        tiles += worked_example_tile(cat, dk, dl, color, examples[dk])
    tiles += "</div></div>"

    gotchas = gotcha_list(c["gotchas"])

    content = ('<div class="problem-card-content">' + intro + template_card +
               tiles + gotchas + "</div>")
    return ('<div class="problem-card collapsed" id="' + cat + '">' + header +
            excerpt + content + "</div>")


# ============================================================
# Decision tree (itree) definitions  -> COWORK_ITREES JSON
# Leaf nodes link to recipe anchors (#<cat>).
# ============================================================
def leaf(name, desc, anchor, code=None):
    d = {"leaf": name, "desc": desc, "anchor": anchor}
    if code:
        d["code"] = code
    return d


ITREES = {
    "pandas-itree": {
        "q": "What does your expected output look like?",
        "sub": "Read the shape of the answer first, then match a recipe.",
        "options": [
            {"label": "Same rows, just fewer of them",
             "cap": "You are keeping a subset of rows by a condition.",
             "next": leaf("Filtering / boolean indexing",
                          "Keep rows that satisfy one or more conditions with a boolean mask.",
                          "pd_filter", "df[(df['a'] >= x) & (df['b'].isin(vals))]")},
            {"label": "Same rows, reordered",
             "cap": "Highest or lowest first, maybe a tie-breaker.",
             "next": leaf("Sorting",
                          "Order rows by one or more columns with sort_values.",
                          "pd_sort", "df.sort_values(['a','b'], ascending=[False, True])")},
            {"label": "Same rows, a new column added",
             "cap": "A derived column, a label, or a parsed date.",
             "next": {"q": "How is the new column built?",
                      "options": [
                          {"label": "Arithmetic from existing columns",
                           "next": leaf("New computed columns",
                                        "Element-wise arithmetic into a new column.",
                                        "pd_newcol", "df['rate'] = df['a'] / df['b']")},
                          {"label": "A dict lookup or a per-value function",
                           "next": leaf("apply / map",
                                        "map for a dict, apply for a function, axis=1 for row-wise.",
                                        "pd_apply_map", "df['band'] = df['age'].apply(lambda a: 'senior' if a>=65 else 'adult')")},
                          {"label": "A date part pulled from a date column",
                           "next": leaf("Datetime parse / extract",
                                        "Parse to datetime, then use the .dt accessor.",
                                        "pd_datetime", "pd.to_datetime(df['d']).dt.month")},
                          {"label": "Just a column renamed",
                           "next": leaf("Rename columns",
                                        "Relabel headers with a dict or a function.",
                                        "pd_rename", "df.rename(columns={'pat':'patient'})")},
                      ]}},
            {"label": "One summary row per group",
             "cap": "A total or average per category.",
             "next": leaf("groupby + agg",
                          "Split by a key, aggregate each group, optionally rename.",
                          "pd_groupby", "df.groupby('k').agg(total=('c','sum'))")},
            {"label": "A tally of how often each value appears",
             "cap": "Counts or shares per category, or the mode.",
             "next": leaf("value_counts / counting",
                          "value_counts for counts, normalize=True for shares.",
                          "pd_value_counts", "df['col'].value_counts()")},
            {"label": "Columns pulled from a second table",
             "cap": "A join on a shared key.",
             "next": leaf("merge / join",
                          "Combine two frames on a key; choose the how= carefully.",
                          "pd_merge", "left.merge(right, on='id', how='left')")},
            {"label": "A wide grid (rows by one field, columns by another)",
             "cap": "Long data reshaped to a matrix.",
             "next": leaf("pivot_table / pivot",
                          "Reshape long to wide with an aggregation.",
                          "pd_pivot", "df.pivot_table(index='r', columns='c', values='v', aggfunc='sum')")},
            {"label": "The same frame with the holes handled",
             "cap": "NaN filled or rows dropped.",
             "next": leaf("Missing data (fillna / dropna)",
                          "Fill NaN with a constant or a statistic, or drop the rows.",
                          "pd_missing", "df.dropna().reset_index(drop=True)")},
            {"label": "Specific columns or positions selected",
             "cap": "A projection by label or position.",
             "next": leaf("Select rows / columns (loc / iloc)",
                          "Pull columns by name, or rows and columns with loc / iloc.",
                          "pd_select", "df.loc[mask, ['a','b']]")},
        ],
    },
    "numpy-itree": {
        "q": "What are you doing to the array?",
        "options": [
            {"label": "Building a fresh array from scratch",
             "next": leaf("Array creation",
                          "arange, linspace, full, zeros to build an array.",
                          "np_create", "np.arange(8); np.linspace(0,1,5); np.full((3,3),7)")},
            {"label": "Math on every element",
             "next": leaf("Vectorized arithmetic",
                          "Element-wise math with no loop.",
                          "np_vectorized", "(a ** 2 - 1) / 2")},
            {"label": "Selecting or counting elements by a condition",
             "next": leaf("Boolean masks",
                          "Index with a condition; sum the mask to count.",
                          "np_mask", "a[a > 10]; int((a % 2 == 0).sum())")},
            {"label": "Reducing along an axis (sum / mean)",
             "next": leaf("Aggregations (sum / mean / axis)",
                          "axis=0 down rows, axis=1 across columns.",
                          "np_agg", "m.sum(axis=0); m.mean(axis=1)")},
            {"label": "Changing the shape without changing values",
             "next": leaf("Reshape",
                          "reshape, -1 to infer, ravel to flatten.",
                          "np_reshape", "np.arange(12).reshape(3,4); m.ravel()")},
            {"label": "Picking between two values on a condition",
             "next": leaf("np.where",
                          "Vectorized if/else into a new array.",
                          "np_where", "np.where(a > 10, 1, 0)")},
            {"label": "Combining arrays of different shapes",
             "next": leaf("Broadcasting",
                          "Align shapes from the right; reshape to (n,1) to go down rows.",
                          "np_broadcast", "col.reshape(-1,1) + row")},
        ],
    },
    "python-itree": {
        "q": "What plain-Python task is it?",
        "options": [
            {"label": "Cleaning or splitting a string",
             "next": leaf("String operations",
                          "split, join, strip, case methods.",
                          "py_strings", "' '.join(s.split()).lower()")},
            {"label": "Building a list or dict in one expression",
             "next": leaf("List / dict comprehensions",
                          "Map and filter in a single comprehension.",
                          "py_comprehension", "[x for x in xs if x % 2 == 0]")},
            {"label": "Pulling a sub-sequence by position",
             "next": leaf("Slicing",
                          "start:stop:step, with negative indices from the end.",
                          "py_slicing", "data[1::2]")},
            {"label": "Ordering items, maybe by a custom key",
             "next": leaf("Sorting with keys",
                          "sorted with key= and reverse=.",
                          "py_sort_key", "sorted(pairs, key=lambda t: t[1], reverse=True)")},
            {"label": "Tallying how often items appear",
             "next": leaf("Counting",
                          "list.count for one value, Counter for all.",
                          "py_counting", "Counter(items).most_common(1)[0][0]")},
        ],
    },
}


# ============================================================
# Diagnostic tab (a five-step process to route a Python prompt)
# ============================================================
def diagnostic_tab():
    steps = [
        ("Step 1: Name the inputs and the output",
         "List what you are handed (a DataFrame df, an array a, a list) and what "
         "the answer should be (a DataFrame, a Series, an array, a scalar, a list, "
         "a dict). The shape of the output is the strongest signal for which "
         "recipe you need.",
         "Input: df with columns patient, age, dept, visits\n"
         "Output: a Series of mean cost indexed by dept\n"
         "=> output is one value per group => groupby + agg"),
        ("Step 2: Pick the family",
         "Decide pandas, numpy, or plain Python. Tabular data with named columns "
         "is pandas. A numeric grid or vector is numpy. A bare list, string, or "
         "dict is plain Python.",
         "[x] pandas   [ ] numpy   [ ] python\n"
         "The data is a labeled table, so this is pandas."),
        ("Step 3: Match the output shape to a recipe",
         "Use the Decision Tree tab. In pandas: fewer rows is filter; reordered is "
         "sort; a new column is newcol / apply / datetime / rename; one row per "
         "group is groupby; a tally is value_counts; columns from another table is "
         "merge; a wide grid is pivot. State it in one sentence: this is a "
         "__________ because __________.",
         "This is a group-aggregate because I need one summary row per dept."),
        ("Step 4: Write the assignment",
         "Copy the template from the recipe card and swap in the real column and "
         "value names. Assign the answer to the variable the prompt names, usually "
         "result. Build on df.copy() if you must not mutate the input.",
         "result = df.groupby('dept')['cost'].mean()"),
        ("Step 5: Check the dtype and the index",
         "Most false fails are dtype and index noise: an int column promoted to "
         "float by a NaN, a leftover non-default index after filtering, a Series "
         "where a DataFrame was expected. reset_index(drop=True) and astype fix "
         "most of these.",
         "result = result.reset_index()   # if a flat DataFrame is wanted\n"
         "df['visits'] = df['visits'].fillna(0).astype(int)"),
    ]
    cards = ""
    for title, what, worked in steps:
        cards += (
            '<div class="problem-card collapsed" style="margin: 0 0 12px 0;">'
            '<div class="problem-card-header" style="padding: 10px 14px;">'
            '<h3 class="problem-card-title" style="margin:0; font-size:1.4rem;">'
            + esc(title) + "</h3>"
            '<span class="problem-toggle">&#9660;</span></div>'
            '<div class="problem-card-content" style="padding:12px 14px;">'
            "<p><strong>What to do:</strong> " + esc(what) + "</p>"
            '<div style="background:#f5f5f5; border-left:3px solid #2e7d32; '
            'padding:10px 14px; margin-top:10px; border-radius:3px;">'
            '<p style="margin:0 0 4px; font-weight:600; color:#2e7d32; '
            'font-size:1.2rem;">Worked example (mean cost per dept):</p>'
            '<pre style="margin:0; font-size:1.15rem; white-space:pre-wrap; '
            "font-family:'Courier New', Consolas, monospace; color:#333;\">"
            + esc(worked) + "</pre></div></div></div>")
    return (
        '<div id="tab-diagnostic" class="tab-pane active">'
        '<div class="section-heading" style="display:flex; align-items:center; '
        'justify-content:center; position:relative; border-left:none; '
        'padding-left:0;"><span>Five-Step Diagnostic Process</span>'
        '<button type="button" onclick="collapseAllInTab(this)" style="position:'
        'absolute; right:0; font-size:1rem; font-weight:600; padding:6px 14px; '
        'border:1px solid #cbd5e1; border-radius:6px; background:#f1f5f9; '
        'color:#334155; cursor:pointer;">Collapse all</button></div>'
        '<p style="margin-bottom:20px; line-height:1.8;">A short routine for '
        "turning a pandas, numpy, or Python prompt into the right one-line "
        "answer. Work the five steps, then copy the template from the matching "
        "recipe card.</p>" + cards + "</div>")


def decision_tree_tab():
    blocks = ""
    for tab_id, key, _ in GROUP_TABS:
        family = {"pandas": "pandas-itree", "numpy": "numpy-itree",
                  "python": "python-itree"}[key]
        blocks += (
            '<div class="problem-card collapsed" style="margin:0 0 16px 0;">'
            '<div class="problem-card-header">'
            '<h3 class="problem-card-title">' + esc(key) +
            " decision tree</h3>"
            '<span class="problem-toggle">&#9660;</span></div>'
            '<div class="problem-card-excerpt"><p>Click through the questions; '
            "each leaf links to the full recipe.</p></div>"
            '<div class="problem-card-content">'
            '<div id="' + family + '" class="itree"></div>'
            "</div></div>")
    return (
        '<div id="tab-decision-tree" class="tab-pane">'
        '<div class="section-heading">Decision Tree</div>'
        '<p style="margin-bottom:20px; line-height:1.8;">Three interactive '
        "trees, one per family. Pick the description that matches your expected "
        "output and the tree routes you to the recipe.</p>" + blocks + "</div>")


def recipes_tab(tab_id, group, title, data, examples_by_cat):
    cats = [c for c in data["category_order"]
            if data["categories"][c]["group"] == group]
    cards = ""
    for cat in cats:
        cards += recipe_card(cat, data["categories"][cat], examples_by_cat[cat])
    return ('<div id="' + tab_id + '" class="tab-pane">'
            '<div class="section-heading">' + esc(title) + "</div>"
            '<p style="margin-bottom:20px; line-height:1.8;">' +
            esc(GROUP_BLURB[group]) + "</p>" + cards + "</div>")


# ============================================================
# Assemble
# ============================================================
def extra_style():
    # Extend the cw-standardize "bold dark border + blue chip" top-level card look
    # and the difficulty-colored tile left borders to the python tab ids.
    sel_top = ",\n".join("#%s > .problem-card" % t for t, _, _ in GROUP_TABS)
    sel_hdr = ",\n".join("#%s > .problem-card > .problem-card-header" % t for t, _, _ in GROUP_TABS)
    sel_badge = ",\n".join("#%s > .problem-card > .problem-card-header .count-badge" % t for t, _, _ in GROUP_TABS)
    css = """
<style id="py-extend">
/* Top-level recipe cards in the python tabs: match the SQL standardize look */
%s {
  border: 2px solid #334155 !important;
  border-radius: 8px !important;
  margin: 0 0 16px 0 !important;
  overflow: hidden;
  box-shadow: none !important;
}
%s {
  background-color: #ffffff !important;
  display: flex !important;
  align-items: center !important;
  gap: 12px !important;
}
%s {
  margin-left: auto !important;
  background-color: #1565c0 !important;
  color: #ffffff !important;
  border: none !important;
  border-radius: 16px !important;
  padding: 5px 13px !important;
  font-weight: 500 !important;
}
/* Difficulty-colored left border on worked-example tiles */
.tab-pane .problem-card.collapsed:has(> .problem-card-header .problem-card-title > span[style*="background-color: #2e7d32"]) > .problem-card-header { border-left: 4px solid #2e7d32; }
.tab-pane .problem-card.collapsed:has(> .problem-card-header .problem-card-title > span[style*="background-color: #e65100"]) > .problem-card-header { border-left: 4px solid #e65100; }
.tab-pane .problem-card.collapsed:has(> .problem-card-header .problem-card-title > span[style*="background-color: #b71c1c"]) > .problem-card-header { border-left: 4px solid #b71c1c; }
/* gotcha list bullets */
.gotcha-list li { margin-bottom: 6px; }
</style>
""" % (sel_top, sel_hdr, sel_badge)
    return css


def build():
    with open(EXAMPLES) as f:
        data = json.load(f)
    examples_by_cat = {c: data["categories"][c]["examples"]
                       for c in data["categories"]}

    # Reuse the SQL head verbatim, swap the title, append extra style.
    with open(SQL_HTML) as f:
        sql = f.read()
    head = sql.split("</head>", 1)[0]
    head = head.replace(
        "<title>SQL Problem Patterns: A Practice Guide</title>",
        "<title>Python Problem Patterns: pandas, numpy, and Python</title>")
    head = head + extra_style() + "</head>"

    n_cats = len(data["categories"])
    subtitle = (str(n_cats) + " pandas, numpy, and basic-Python patterns grouped "
                "into three families, each with signal words, a pattern template, "
                "three worked examples (Easy, Moderate, Hard), and common gotchas, "
                "plus a five-step diagnostic and interactive decision trees.")

    body = []
    body.append("<body>")
    body.append('<div id="page-container">')
    body.append('<div id="content-wrap">')
    body.append('<div w3-include-html="/folders/navbar_footer/navbar_pages.html"></div>')
    body.append('<div class="blog-container">')
    body.append('<div class="blog-header"><h1>Python Problem Patterns</h1>'
                '<p class="subtitle">' + esc(subtitle) + "</p>"
                '<p class="meta">Last updated: June 2026</p></div>')
    # tab nav
    nav = ['<div class="tab-navigation" id="tab-nav">',
           '<button class="tab-nav-item active" data-tab="tab-diagnostic">Diagnostic Process</button>',
           '<button class="tab-nav-item" data-tab="tab-decision-tree">Decision Tree</button>']
    for tab_id, _, title in GROUP_TABS:
        nav.append('<button class="tab-nav-item" data-tab="' + tab_id + '">' +
                   esc(title) + "</button>")
    nav.append("</div>")
    body.append("\n".join(nav))
    # tab content
    body.append('<div class="tab-content">')
    body.append(diagnostic_tab())
    body.append(decision_tree_tab())
    for tab_id, group, title in GROUP_TABS:
        body.append(recipes_tab(tab_id, group, title, data, examples_by_cat))
    body.append("</div>")  # tab-content
    body.append("</div>")  # blog-container
    body.append("</div><!-- end content-wrap -->")
    body.append('<div w3-include-html="/folders/navbar_footer/footer.html"></div>')
    body.append("</div><!-- end page-container -->")

    # scripts: nav + cards + jumpToRecipe + deep-link, then itree engine
    body.append(SCRIPTS)
    body.append("<script>\n" + ITREE_ENGINE + "\nvar COWORK_ITREES=" +
                json.dumps(ITREES) +
                ";\ndocument.addEventListener('DOMContentLoaded',function(){"
                "for(var k in COWORK_ITREES){renderITree(k,COWORK_ITREES[k]);}});\n"
                "</script>")
    body.append("</body>\n</html>")

    out = head + "\n" + "\n".join(body)
    with open(OUT_HTML, "w") as f:
        f.write(out)
    print("wrote", OUT_HTML)
    print("bytes:", len(out))


SCRIPTS = r"""
<script type="text/javascript" src="../../static/js/include.js"></script>
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const tabNav = document.getElementById('tab-nav');
    const tabButtons = document.querySelectorAll('.tab-nav-item');
    const tabPanes = document.querySelectorAll('.tab-pane');
    window.addEventListener('scroll', function() {
      if (window.scrollY > 200) { tabNav.classList.add('sticky'); }
      else { tabNav.classList.remove('sticky'); }
    });
    tabButtons.forEach(button => {
      button.addEventListener('click', function() {
        const tabId = this.getAttribute('data-tab');
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabPanes.forEach(pane => pane.classList.remove('active'));
        this.classList.add('active');
        const targetPane = document.getElementById(tabId);
        if (targetPane) targetPane.classList.add('active');
        setTimeout(() => {
          const contentOffset = tabNav.offsetTop - 20;
          window.scrollTo({ top: contentOffset, behavior: 'smooth' });
        }, 0);
      });
    });
    function initializeProblemCards() {
      const problemCards = document.querySelectorAll('.problem-card-header');
      problemCards.forEach(header => {
        if (!header.hasListener) {
          header.addEventListener('click', function() {
            const card = this.closest('.problem-card');
            card.classList.toggle('collapsed');
          });
          header.hasListener = true;
        }
      });
    }
    document.querySelectorAll('.problem-card').forEach(card => { card.classList.add('collapsed'); });
    initializeProblemCards();
    tabButtons.forEach(button => { button.addEventListener('click', function() { setTimeout(initializeProblemCards, 100); }); });
  });

  function collapseAllInTab(btn){
    var pane = btn.closest('.tab-pane'); if(!pane) return;
    var cards = pane.querySelectorAll('.problem-card');
    var anyOpen = Array.prototype.some.call(cards, function(c){ return !c.classList.contains('collapsed'); });
    cards.forEach(function(c){ if(anyOpen){ c.classList.add('collapsed'); } else { c.classList.remove('collapsed'); } });
    btn.textContent = anyOpen ? 'Expand all' : 'Collapse all';
  }

  function jumpToRecipe(recipeId) {
    var card = document.getElementById(recipeId); if (!card) return;
    var tabPane = card.closest('.tab-pane');
    if (tabPane) {
      document.querySelectorAll('.tab-nav-item').forEach(function(b) { b.classList.remove('active'); });
      document.querySelectorAll('.tab-pane').forEach(function(p) { p.classList.remove('active'); });
      var tabBtn = document.querySelector('[data-tab="' + tabPane.id + '"]');
      if (tabBtn) tabBtn.classList.add('active');
      tabPane.classList.add('active');
    }
    var anc = card;
    while (anc) { if (anc.classList && anc.classList.contains('collapsed')) anc.classList.remove('collapsed'); anc = anc.parentElement; }
    setTimeout(function() { card.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 100);
  }

  window.addEventListener('DOMContentLoaded', function() {
    var id = location.hash ? location.hash.slice(1) : ''; if (!id) return;
    var el = document.getElementById(id); if (!el) return;
    var pane = el.closest('.tab-pane');
    if (pane) {
      document.querySelectorAll('.tab-nav-item').forEach(function(b){ b.classList.remove('active'); });
      document.querySelectorAll('.tab-pane').forEach(function(p){ p.classList.remove('active'); });
      var btn = document.querySelector('[data-tab="' + pane.id + '"]');
      if (btn) btn.classList.add('active');
      pane.classList.add('active');
    }
    var node = el;
    while (node) { if (node.classList && node.classList.contains('collapsed')) node.classList.remove('collapsed'); node = node.parentElement; }
    setTimeout(function(){ el.scrollIntoView({ behavior: 'smooth', block: 'start' }); }, 120);
  });
</script>
"""

ITREE_ENGINE = r"""
function itreeTable(cols, rows){
  function cell(c){
    if(c && typeof c==='object'){ return '<td>'+c.v+'</td>'; }
    return '<td>'+c+'</td>';
  }
  var h='<table class="ix"><tr>'+cols.map(function(c){return '<th>'+c+'</th>';}).join('')+'</tr>';
  rows.forEach(function(r){ h+='<tr>'+r.map(cell).join('')+'</tr>'; });
  return h+'</table>';
}
function renderITree(id, tree){
  var root=document.getElementById(id); if(!root) return; var path=[];
  function node(){ return path.length? path[path.length-1].node : tree; }
  function draw(){
    root.innerHTML='';
    path.forEach(function(p){ var c=document.createElement('div'); c.className='itree-crumb'; c.innerHTML='<b>'+p.q+'</b> &rarr; '+p.choice; root.appendChild(c); });
    var n=node();
    if(n.leaf){
      var d=document.createElement('div'); d.className='itree-leaf';
      var html='<div class="itree-leaf-title">&#10003; Use: '+n.leaf+'</div><div class="itree-leaf-desc">'+n.desc+'</div>';
      if(n.code){ html+='<div class="itree-lbl">Core call</div><pre class="itree-code"><code>'+n.code.replace(/&/g,'&amp;').replace(/</g,'&lt;')+'</code></pre>'; }
      if(n.anchor){ html+='<a class="itree-recipe" href="#'+n.anchor+'" onclick="jumpToRecipe(\''+n.anchor+'\');return false;">Open the full recipe &rarr;</a>'; }
      d.innerHTML=html; root.appendChild(d);
    } else {
      var q=document.createElement('div'); q.className='itree-q'; q.textContent=n.q; root.appendChild(q);
      if(n.sub){ var sb=document.createElement('div'); sb.className='itree-subq'; sb.textContent=n.sub; root.appendChild(sb); }
      var opts=document.createElement('div'); opts.className='itree-opts';
      n.options.forEach(function(o){
        var b=document.createElement('div'); b.className='itree-opt';
        var inner='<div class="itree-opt-label">'+o.label+'</div>';
        if(o.cap) inner+='<div class="itree-opt-cap">'+o.cap+'</div>';
        b.innerHTML=inner;
        b.onclick=function(){ path.push({q:n.q, choice:o.label, node:o.next}); draw(); };
        opts.appendChild(b);
      });
      root.appendChild(opts);
    }
    if(path.length){ var bk=document.createElement('button'); bk.type='button'; bk.className='itree-reset'; bk.textContent='← Back one step'; bk.onclick=function(){ path.pop(); draw(); }; root.appendChild(bk); }
  }
  draw();
}
"""


if __name__ == "__main__":
    build()
