"""
py_patterns_gen_examples.py

Derives worked-example content for python_problem_patterns.html DIRECTLY from the
nb02 engine (nb02_python_drill_utils), so every prompt / input / solution /
expected output in the playbook matches the notebook exactly.

For each of the 24 categories x 3 difficulties it generates one problem with a
fixed seed (reproducible), then captures:
  prompt, setup_code, input objects (as text), solution, expected output (text),
  hints, notes.

Writes a JSON blob to py_patterns_examples.json next to this script.

Run from anywhere; paths are derived from __file__ and a known repo layout.
"""
import json
import os
import sys
import io
import contextlib

HERE = os.path.dirname(os.path.abspath(__file__))
# folders/sql/build_scripts -> repo root is three up
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
NB_DIR = os.path.join(
    REPO, "folders", "ds_blogs", "projects",
    "data_analyst_interview_prep", "notebooks",
)
sys.path.insert(0, NB_DIR)

import numpy as np
import pandas as pd
import nb02_python_drill_utils as pdu

DIFFS = ["easy", "moderate", "hard"]


def obj_to_text(obj):
    """Plain-text rendering of an input/expected object for a <pre> block."""
    if isinstance(obj, pd.DataFrame):
        return obj.to_string(index=True)
    if isinstance(obj, pd.Series):
        return obj.to_string()
    if isinstance(obj, np.ndarray):
        return np.array2string(obj)
    return repr(obj)


def shape_label(obj):
    if isinstance(obj, pd.DataFrame):
        return "DataFrame %d rows x %d cols" % obj.shape
    if isinstance(obj, pd.Series):
        return "Series len %d" % obj.shape[0]
    if isinstance(obj, np.ndarray):
        return "ndarray shape %s" % (obj.shape,)
    if isinstance(obj, (list, tuple)):
        return "%s len %d" % (type(obj).__name__, len(obj))
    if isinstance(obj, dict):
        return "dict %d keys" % len(obj)
    return type(obj).__name__


def first_run_input_text(p):
    """Render the named input objects (df, a, m, ...) as labeled text blocks."""
    blocks = []
    for name, obj in p.inputs.items():
        blocks.append({"name": name, "shape": shape_label(obj),
                       "text": obj_to_text(obj)})
    return blocks


# Fixed seed per (category, difficulty) so the page is stable across rebuilds.
def seed_for(cat, diff):
    return (abs(hash(cat)) % 9000) + DIFFS.index(diff) * 13 + 7


def build():
    out = {"categories": {}, "category_order": pdu.category_keys(),
           "meta": {}}
    for cat in pdu.category_keys():
        meta = pdu.CATEGORIES[cat]
        entry = {"label": meta["label"], "group": meta["group"],
                 "blurb": meta["blurb"], "examples": {}}
        for diff in DIFFS:
            # deterministic but varied
            seed = seed_for(cat, diff)
            p = pdu.generate_problem(cat, diff, scenario="random", seed=seed)
            # strip the leading "Scenario: ...\n\n" so the playbook prompt is
            # the pure task; keep the scenario separately.
            prompt = p.prompt
            scenario = p.scenario
            if prompt.startswith("Scenario:"):
                # remove the first paragraph
                parts = prompt.split("\n\n", 1)
                prompt = parts[1] if len(parts) > 1 else prompt
            entry["examples"][diff] = {
                "prompt": prompt.strip(),
                "scenario": scenario,
                "setup_code": p.setup_code,
                "inputs": first_run_input_text(p),
                "solution": p.solution,
                "result_var": p.result_var,
                "expected_text": obj_to_text(p.expected),
                "expected_shape": shape_label(p.expected),
                "hints": p.hints,
                "notes": p.notes,
            }
        out["categories"][cat] = entry
    return out


if __name__ == "__main__":
    data = build()
    dest = os.path.join(HERE, "py_patterns_examples.json")
    with open(dest, "w") as f:
        json.dump(data, f, indent=1)
    n = sum(len(c["examples"]) for c in data["categories"].values())
    print("wrote", dest)
    print("categories:", len(data["categories"]), "examples:", n)
