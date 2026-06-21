"""
Muay Thai Workout Generator library
===================================
All the logic for the workout generator lives here so the notebook stays minimal.

Use in a notebook:

    import muay_thai_lib as mt
    mt.launch()        # interactive generator with copy-ready output + tracking

Power-user helpers: mt.build_workout('basic'), mt.workout_text(...),
mt.mark_used(...), mt.usage_counts(), mt.load_usage().

Each generated workout: fixed warmup + 3 random burnouts + 7 drills that satisfy
both a difficulty mix (by level) and a category mix (2 strikes, 2 lower body,
3 combinations). Output is paste-ready for Google Keep with XXX pm placeholders.
"""
import html as _html
import json as _json
import random
from pathlib import Path
from datetime import datetime

import pandas as pd

USAGE_LOG = Path(__file__).with_name("muay_thai_usage_log.csv")
WORKOUT_LOG = Path(__file__).with_name("muay_thai_workout_log.csv")

WARMUP = ["dynamic stretches", "standing hamstring stretch with step",
          "shadow boxing", "shadow alternating kicks", "plank"]
LEVEL_REQ = {"basic": {1: 5, 2: 1, 3: 1},
             "intermediate": {1: 1, 2: 5, 3: 1},
             "advance": {1: 1, 2: 1, 3: 5}}
CAT_REQ = {"S": 2, "L": 2, "C": 3}
DIFFICULTIES = ["basic", "intermediate", "advance"]
N_BURNOUTS = 3
N_DRILLS = 7

DRILLS = [
    {"id": "1.1", "name": "Body Hook, Body Hook, Hook", "level": 1, "cat": "S"},
    {"id": "1.2", "name": "Cross, Hook, Check, Rear Roundhouse", "level": 1, "cat": "C"},
    {"id": "1.3", "name": "Cross, Hook, Cross, Switch Kick", "level": 1, "cat": "C"},
    {"id": "1.4", "name": "Double Jab, Overhand, Liver Shot", "level": 1, "cat": "S"},
    {"id": "1.5", "name": "Hook, Roundhouse", "level": 1, "cat": "C"},
    {"id": "1.6", "name": "Jab, Body Cross", "level": 1, "cat": "S"},
    {"id": "1.7", "name": "Jab, Body Hook, Body Hook, Cross", "level": 1, "cat": "S"},
    {"id": "1.8", "name": "Jab, Cross", "level": 1, "cat": "S"},
    {"id": "1.9", "name": "Jab, Cross, Check, Switch Kick", "level": 1, "cat": "C"},
    {"id": "1.10", "name": "Jab, Cross, Hook", "level": 1, "cat": "S"},
    {"id": "1.11", "name": "Jab, Cross, Hook, Cross", "level": 1, "cat": "S"},
    {"id": "1.12", "name": "Jab, Cross, Hook, Roundhouse", "level": 1, "cat": "C"},
    {"id": "1.13", "name": "Jab, Cross, Pendulum Kick", "level": 1, "cat": "C"},
    {"id": "1.14", "name": "Jab, Cross, Rear Knee, Rear Roundhouse", "level": 1, "cat": "C"},
    {"id": "1.15", "name": "Jab, Cross, Rear Roundhouse", "level": 1, "cat": "C"},
    {"id": "1.16", "name": "Jab, Cross, Switch Kick", "level": 1, "cat": "C"},
    {"id": "1.17", "name": "Jab, Hook, Cross, Rear Elbow", "level": 1, "cat": "S"},
    {"id": "1.18", "name": "Jab, Hook, Rear Elbow", "level": 1, "cat": "S"},
    {"id": "1.19", "name": "Jab, Hook, Roundhouse", "level": 1, "cat": "C"},
    {"id": "1.20", "name": "Jab, Jab Body, Overhand", "level": 1, "cat": "S"},
    {"id": "1.21", "name": "Jab, Switch Kick", "level": 1, "cat": "C"},
    {"id": "1.22", "name": "Jab, Liver Shot, Hook, Cross", "level": 1, "cat": "S"},
    {"id": "1.23", "name": "Jab, Roundhouse", "level": 1, "cat": "C"},
    {"id": "1.24", "name": "Jab, Lead Spear Elbow", "level": 1, "cat": "S"},
    {"id": "1.25", "name": "Jab, Teep", "level": 1, "cat": "C"},
    {"id": "1.26", "name": "Long Guard, Rear Knee, Long Guard, Lead Elbow", "level": 1, "cat": "C"},
    {"id": "1.27", "name": "Rear Roundhouse, Teep", "level": 1, "cat": "L"},
    {"id": "1.28", "name": "Rear Roundhouse, Rear Knee", "level": 1, "cat": "L"},
    {"id": "1.29", "name": "Rear Roundhouse, Push Kick", "level": 1, "cat": "L"},
    {"id": "1.30", "name": "Push Kick, Rear Roundhouse", "level": 1, "cat": "L"},
    {"id": "1.31", "name": "Switch Kick, Teep", "level": 1, "cat": "L"},
    {"id": "1.32", "name": "Switch Kick, Cross", "level": 1, "cat": "C"},
    {"id": "1.33", "name": "Switch Kick, Rear Round Knee", "level": 1, "cat": "L"},
    {"id": "1.34", "name": "Switch Knee, Rear Elbow", "level": 1, "cat": "C"},
    {"id": "1.35", "name": "Teep, Fake Teep, Rear Knee", "level": 1, "cat": "L"},
    {"id": "1.36", "name": "Teep, Rear Roundhouse", "level": 1, "cat": "L"},
    {"id": "1.37", "name": "Teep, Switch Kick", "level": 1, "cat": "L"},
    {"id": "2.1", "name": "Cross, Liver Shot, High Kick", "level": 2, "cat": "C"},
    {"id": "2.2", "name": "Cross, Rear Head Kick", "level": 2, "cat": "C"},
    {"id": "2.3", "name": "Double Roundhouse", "level": 2, "cat": "L"},
    {"id": "2.4", "name": "Double Teep, Rear Roundhouse", "level": 2, "cat": "L"},
    {"id": "2.5", "name": "Hook, Cross, Rear Roundhouse, Cross", "level": 2, "cat": "C"},
    {"id": "2.6", "name": "Hook, Liver Shot, Low Kick", "level": 2, "cat": "C"},
    {"id": "2.7", "name": "Hook, Reverse Elbow, Rear Elbow", "level": 2, "cat": "S"},
    {"id": "2.8", "name": "Hook, Rear Roundhouse, Cross, Switch Kick", "level": 2, "cat": "C"},
    {"id": "2.9", "name": "Jab, Body Cross, Lead High Kick", "level": 2, "cat": "C"},
    {"id": "2.10", "name": "Jab, Body Cross, Post, Rear Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.11", "name": "Jab, Cross, Hook, Rear Kick, Check, Rear Kick", "level": 2, "cat": "C"},
    {"id": "2.12", "name": "Jab, Cross, Hook, Rear Roundhouse, Lead Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.13", "name": "Jab Cross - Cross, Hook - Hook, Cross", "level": 2, "cat": "S"},
    {"id": "2.14", "name": "Jab, Cross, Hook, Rear Roundhouse, Lead Round Knee", "level": 2, "cat": "C"},
    {"id": "2.15", "name": "Jab, Cross, Lean Back, High Kick", "level": 2, "cat": "C"},
    {"id": "2.16", "name": "Jab, Cross, Switch Kick, Check, Switch Kick", "level": 2, "cat": "C"},
    {"id": "2.17", "name": "Jab, Cross, Switch Kick, Rear Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.18", "name": "Jab, Cross, Switch Kick, Rear Round Knee", "level": 2, "cat": "C"},
    {"id": "2.19", "name": "Jab, Hook, Rear Elbow, Rear Knee", "level": 2, "cat": "C"},
    {"id": "2.20", "name": "Jab, Rear Spear Elbow, Lead Elbow", "level": 2, "cat": "S"},
    {"id": "2.21", "name": "Jab, Spear Rear Elbow", "level": 2, "cat": "S"},
    {"id": "2.22", "name": "Jab, Teep, Cross, Rear Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.23", "name": "Lead Elbow, Rear Elbow, Reverse Elbow, Rear Elbow", "level": 2, "cat": "S"},
    {"id": "2.24", "name": "Lead Roundhouse, Rear Roundhouse (Alternating Kicks)", "level": 2, "cat": "L"},
    {"id": "2.25", "name": "Long Guard, Rear Knee, Long Guard, Rear Elbow", "level": 2, "cat": "C"},
    {"id": "2.26", "name": "Long Guard, Spear Elbow, Rear Knee, LG, Rear Elbow, Switch Knee", "level": 2, "cat": "C"},
    {"id": "2.27", "name": "Push Kick, Fake Push Kick, Step Knee", "level": 2, "cat": "L"},
    {"id": "2.28", "name": "Push Kick, Rear Knee, Rear Elbow", "level": 2, "cat": "C"},
    {"id": "2.29", "name": "Cross, Lead Knee, Lead Elbow", "level": 2, "cat": "C"},
    {"id": "2.30", "name": "Rear Roundhouse, Hook, Cross, Lead Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.31", "name": "Rear Roundhouse, Cross, Lead Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.32", "name": "Rear Knee, Hook, Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.33", "name": "Switch Hook, Rear Roundhouse", "level": 2, "cat": "C"},
    {"id": "2.34", "name": "Teep, Check, Knee", "level": 2, "cat": "L"},
    {"id": "2.35", "name": "Teep, Rear Knee, Lead Elbow", "level": 2, "cat": "C"},
    {"id": "2.36", "name": "Teep, Rear Roundhouse, Rear Knee", "level": 2, "cat": "L"},
    {"id": "2.37", "name": "Rear Push Kick, Teep, Lead Knee, Rear Knee", "level": 2, "cat": "L"},
    {"id": "2.38", "name": "Teep, Switch Kick, Switch Knee", "level": 2, "cat": "L"},
    {"id": "2.39", "name": "Teep, Fake Teep, Lead Spear Elbow, Rear Elbow", "level": 2, "cat": "C"},
    {"id": "3.1", "name": "Cross, Hook, Roundhouse, Hook, Cross, Switch Kick", "level": 3, "cat": "C"},
    {"id": "3.2", "name": "Hook, Spinning Elbow", "level": 3, "cat": "S"},
    {"id": "3.3", "name": "Jab, Rear Roundhouse, Superman", "level": 3, "cat": "C"},
    {"id": "3.4", "name": "Push Kick, Jumping Scissor Knee", "level": 3, "cat": "L"},
    {"id": "3.5", "name": "Push Kick, Fake Push Kick, Spinning Elbow", "level": 3, "cat": "C"},
    {"id": "3.6", "name": "Question Mark Kick", "level": 3, "cat": "L"},
    {"id": "3.7", "name": "Rear Elbow, Lead Elbow, Spinning Elbow, Rear Elbow", "level": 3, "cat": "S"},
    {"id": "3.8", "name": "Rear Roundhouse, Cobra Punch", "level": 3, "cat": "C"},
    {"id": "3.9", "name": "Rear Roundhouse, Knee Guard, Round Knee", "level": 3, "cat": "L"},
    {"id": "3.10", "name": "Rear Roundhouse, Lead Roundhouse, Cross, Hook, Roundhouse", "level": 3, "cat": "C"},
    {"id": "3.11", "name": "Scissor Kick", "level": 3, "cat": "L"},
    {"id": "3.12", "name": "Switch Cross, Double Jab, Roundhouse", "level": 3, "cat": "C"},
    {"id": "3.13", "name": "Switch Cross, Hook, Rear Roundhouse", "level": 3, "cat": "C"},
    {"id": "3.14", "name": "Switch Hook, Rear Knee, Rear Elbow", "level": 3, "cat": "C"},
    {"id": "3.15", "name": "Switch Kick, Knee Guard, Round Knee", "level": 3, "cat": "L"},
    {"id": "3.16", "name": "Switch Kick, Switch Stance Cross, Roundhouse", "level": 3, "cat": "C"},
    {"id": "3.17", "name": "Switch Kick, Switch Hook, Roundhouse", "level": 3, "cat": "C"},
    {"id": "3.18", "name": "Teep, Fake Teep, Jumping Roundhouse", "level": 3, "cat": "L"},
    {"id": "3.19", "name": "Teep, Jumping Knee", "level": 3, "cat": "L"},
    {"id": "3.20", "name": "Teep, Jumping Switch Teep", "level": 3, "cat": "L"},
    {"id": "3.21", "name": "Teep, Superman Jab, Roundhouse, Superman", "level": 3, "cat": "C"},
    {"id": "3.22", "name": "Teep, Superman Jab, Roundhouse", "level": 3, "cat": "C"},
    {"id": "3.23", "name": "Teep, Fake Teep, Hook, Roundhouse", "level": 3, "cat": "C"},
]

BURNOUTS = [
    {"id": "4.1", "name": "Alternating Kicks"},
    {"id": "4.2", "name": "Balancing Teeps"},
    {"id": "4.3", "name": "Speed Kicks"},
    {"id": "4.4", "name": "Burnout Punches"},
    {"id": "4.5", "name": "Burnout Alternating Teeps"},
    {"id": "4.6", "name": "20/20/20 Intense Burnout"},
    {"id": "4.7", "name": "Jab Pyramid"},
    {"id": "4.8", "name": "Kick Pyramid"},
    {"id": "4.9", "name": "Teep, Switch Kick Burnout"},
    {"id": "4.10", "name": "Switch Kick, Switch Knee Burnout"},
    {"id": "4.11", "name": "Skip Knees"},
    {"id": "4.12", "name": "Clinching The Bag"},
    {"id": "4.13", "name": "Kick, Check Drill"},
    {"id": "4.14", "name": "Jabbing Out"},
    {"id": "4.15", "name": "Teeping Out"},
    {"id": "4.16", "name": "Long Guarding Out"},
    {"id": "4.17", "name": "Chin Tucked Drill"},
    {"id": "4.18", "name": "Improvising Combos"},
    {"id": "4.19", "name": "Basic Combo Pyramid"},
    {"id": "4.20", "name": "Long Range Kicks"},
    {"id": "4.21", "name": "Power Low Kicks"},
    {"id": "4.22", "name": "Swinging Heavy Bag Footwork Drill"},
    {"id": "4.23", "name": "Swinging Heavy Bag Distance Control"},
    {"id": "4.24", "name": "Power Boxing"},
    {"id": "4.25", "name": "Low, Middle, High Kicks"},
    {"id": "4.26", "name": "Body, Body, Head"},
    {"id": "4.27", "name": "Left Side Strikes Only"},
    {"id": "4.28", "name": "Right Side Strikes Only"},
    {"id": "4.29", "name": "Lower Body Strikes Only"},
    {"id": "4.30", "name": "Punch, Elbow, Kick, Knee"},
    {"id": "4.31", "name": "Inside Fighting"},
    {"id": "4.32", "name": "Precision Striking"},
    {"id": "4.33", "name": "Teep Chair Technique"},
]


# --------------------------------------------------------------------------
# Selection: constraint solver for level mix + category mix
# --------------------------------------------------------------------------
def _avail(drills):
    m = {1: {"S": [], "L": [], "C": []}, 2: {"S": [], "L": [], "C": []}, 3: {"S": [], "L": [], "C": []}}
    for d in drills:
        m[d["level"]][d["cat"]].append(d)
    return m


def _find_matrix(level_req, avail):
    """Find counts n[level][cat] with row sums = level_req and col sums = CAT_REQ.
    Randomized backtracking so results vary each run."""
    levels = [1, 2, 3]
    cats = ["S", "L", "C"]
    row_left = {1: level_req[1], 2: level_req[2], 3: level_req[3]}
    col_left = {"S": CAT_REQ["S"], "L": CAT_REQ["L"], "C": CAT_REQ["C"]}
    n = {1: {}, 2: {}, 3: {}}

    def solve(idx):
        if idx == 9:
            return all(row_left[l] == 0 for l in levels) and all(col_left[c] == 0 for c in cats)
        l = levels[idx // 3]
        c = cats[idx % 3]
        cap = min(row_left[l], col_left[c], len(avail[l][c]))
        vals = list(range(cap + 1))
        random.shuffle(vals)
        for v in vals:
            n[l][c] = v
            row_left[l] -= v
            col_left[c] -= v
            if solve(idx + 1):
                return True
            row_left[l] += v
            col_left[c] += v
        return False

    return n if solve(0) else None


def pick_drills(level, prefer_new=False):
    """Pick 7 drills meeting both the level mix and the 2S/2L/3C category mix.
    With prefer_new, try drills not yet marked done first, then fall back."""
    full = list(DRILLS)
    candidate_sets = []
    if prefer_new:
        uid = used_ids("drill")
        candidate_sets.append([d for d in full if d["id"] not in uid])
    candidate_sets.append(full)
    for candidates in candidate_sets:
        avail = _avail(candidates)
        matrix = _find_matrix(LEVEL_REQ[level], avail)
        if matrix:
            chosen = []
            for l in (1, 2, 3):
                for c in ("S", "L", "C"):
                    bucket = list(avail[l][c])
                    random.shuffle(bucket)
                    chosen += bucket[:matrix[l][c]]
            order = {"S": 0, "L": 1, "C": 2}
            chosen.sort(key=lambda d: order[d["cat"]])
            return chosen
    # fallback: satisfy level counts only
    chosen = []
    for l, need in LEVEL_REQ[level].items():
        bucket = [d for d in DRILLS if d["level"] == l]
        random.shuffle(bucket)
        chosen += bucket[:need]
    return chosen


def pick_burnouts(n=N_BURNOUTS, prefer_new=False):
    pool = list(BURNOUTS)
    if prefer_new:
        uid = used_ids("burnout")
        fresh = [b for b in pool if b["id"] not in uid]
        if len(fresh) >= n:
            pool = fresh
    random.shuffle(pool)
    return pool[:n]


def workout_text(level, burns, drills):
    """Paste-ready text for Google Keep, with XXX pm placeholders."""
    L = ["XXX pm", "Room 2 (7:00-8:00) - Muay Thai (" + level + ")", "", "WARMUP", ""]
    for w in WARMUP:
        L += ["XXX pm", w, ""]
    L += ["A) Burnout drills [OPTIONS 3]", ""]
    for b in burns:
        L += ["XXX pm", b["id"] + " " + b["name"], ""]
    L += ["B) Muay Thai Drills [OPTIONS 7]",
          "[2 all strikes: jabs, cross, hooks, body hits, elbows, defense]",
          "[2 all lower body: teeps, knees, kicks, defense]",
          "[3 Combinations of strikes and lower body]", ""]
    for d in drills:
        L += ["XXX pm", d["id"] + " " + d["name"], ""]
    return "\n".join(L).rstrip() + "\n"


def build_workout(level, prefer_new=False):
    drills = pick_drills(level, prefer_new)
    burns = pick_burnouts(N_BURNOUTS, prefer_new)
    return {"level": level, "burnouts": burns, "drills": drills,
            "text": workout_text(level, burns, drills)}


# --------------------------------------------------------------------------
# Tracking
# --------------------------------------------------------------------------
USAGE_COLS = ["timestamp", "difficulty", "kind", "id", "name"]


def load_usage():
    if USAGE_LOG.exists():
        return pd.read_csv(USAGE_LOG, dtype=str).fillna("")
    return pd.DataFrame(columns=USAGE_COLS)


def mark_used(difficulty, items):
    u = load_usage()
    ts = datetime.now().isoformat(timespec="seconds")
    rows = [{"timestamp": ts, "difficulty": difficulty, "kind": it.get("kind", ""),
             "id": it.get("id", ""), "name": it.get("name", "")} for it in items]
    if rows:
        u = pd.concat([u, pd.DataFrame(rows)], ignore_index=True)
        u.to_csv(USAGE_LOG, index=False)
    return len(u)


def usage_counts(kind=None):
    u = load_usage()
    if kind and not u.empty:
        u = u[u["kind"] == kind]
    if u.empty:
        return {}
    return u.groupby(["kind", "id", "name"]).size().to_dict()


def used_ids(kind=None):
    u = load_usage()
    if kind and not u.empty:
        u = u[u["kind"] == kind]
    return set(u["id"]) if not u.empty else set()


def log_workout(level, burns, drills, mode):
    row = {"timestamp": datetime.now().isoformat(timespec="seconds"), "difficulty": level, "mode": mode,
           "burnouts": "; ".join(b["id"] + " " + b["name"] for b in burns),
           "drills": "; ".join(d["id"] + " " + d["name"] for d in drills)}
    pd.DataFrame([row]).to_csv(WORKOUT_LOG, mode="a", header=not WORKOUT_LOG.exists(), index=False)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def _copy_box(text):
    safe = _html.escape(text)
    js = _json.dumps(text)
    uid = "cp" + str(random.randint(1000, 9999))
    btn_style = ("background:#3da9fc;color:#fff;border:none;border-radius:8px;padding:9px 16px;"
                 "font-size:13px;font-weight:600;cursor:pointer;margin-bottom:8px;"
                 "font-family:-apple-system,Segoe UI,Roboto")
    pre_style = ("white-space:pre-wrap;font-family:ui-monospace,Menlo,monospace;font-size:12.5px;"
                 "background:#0b0d11;color:#e8eaed;border-radius:10px;padding:14px;max-height:430px;"
                 "overflow:auto;margin:0")
    script = ("<script>(function(){var t=" + js + ";var b=document.getElementById('" + uid + "_btn');"
              "if(b){b.addEventListener('click',function(){navigator.clipboard.writeText(t).then("
              "function(){b.textContent='Copied ✓';setTimeout(function(){"
              "b.textContent='Copy for Google Keep';},1200);});});}})();</script>")
    return ("<div style='max-width:820px'>"
            "<button id='" + uid + "_btn' style='" + btn_style + "'>Copy for Google Keep</button>"
            "<pre id='" + uid + "_pre' style='" + pre_style + "'>" + safe + "</pre>" + script + "</div>")


def show_workout(wk):
    """Static (non-widget) display: copy box only."""
    from IPython.display import HTML, display
    display(HTML(_copy_box(wk["text"])))


def _practiced_table():
    c = usage_counts()
    if not c:
        return ("<i style='font-family:-apple-system,Segoe UI,Roboto;color:#6b7280;font-size:13px'>"
                "No workouts logged yet.</i>")
    items = sorted(c.items(), key=lambda x: -x[1])
    th = ("text-align:left;padding:6px 12px;color:#8a8f98;font-size:11px;text-transform:uppercase")
    td = "padding:6px 12px;border-bottom:1px solid #eee;font-size:13px"
    tr = "".join("<tr><td style='" + td + "'>" + idv + "</td><td style='" + td + "'>" + name +
                 "</td><td style='" + td + ";color:#6b7280'>" + kind + "</td><td style='" + td +
                 "'><b>" + str(n) + "x</b></td></tr>" for (kind, idv, name), n in items)
    return ("<div style='font-family:-apple-system,Segoe UI,Roboto;font-size:13px;margin-top:8px'>"
            "<b>Most practiced</b><table style='border-collapse:collapse;margin-top:6px'><thead><tr>"
            "<th style='" + th + "'>ID</th><th style='" + th + "'>Drill</th>"
            "<th style='" + th + "'>Kind</th><th style='" + th + "'>Done</th></tr></thead><tbody>" +
            tr + "</tbody></table></div>")


# --------------------------------------------------------------------------
# Interactive GUI
# --------------------------------------------------------------------------
def _checklist(wk):
    import ipywidgets as widgets
    from ipywidgets import Layout
    raw = usage_counts()
    counts = {}
    for (kind, idv, name), n in raw.items():
        counts[(kind, idv)] = counts.get((kind, idv), 0) + n
    items = [dict(b, kind="burnout") for b in wk["burnouts"]] + [dict(d, kind="drill") for d in wk["drills"]]
    rows, checks = [], []
    for it in items:
        done = counts.get((it["kind"], it["id"]), 0)
        tag = "Burnout" if it["kind"] == "burnout" else {"S": "strikes", "L": "lower body", "C": "combo"}.get(it.get("cat", ""), "")
        done_html = (" <span style='color:#2e7d32;font-size:11px'>done " + str(done) + "x</span>") if done else ""
        lab = widgets.HTML("<div style='font-family:-apple-system,Segoe UI,Roboto;font-size:13px;color:#3c4149'>"
                           "<b style='color:#111827'>" + it["id"] + "</b> " + it["name"] +
                           " <span style='color:#9aa0a6;font-size:11px'>(" + tag + ")</span>" + done_html + "</div>")
        cb = widgets.Checkbox(value=True, indent=False, layout=Layout(width="28px"))
        rows.append(widgets.HBox([cb, lab], layout=Layout(align_items="center", padding="3px 0")))
        checks.append((cb, it))
    title = widgets.HTML("<div style='font-family:-apple-system,Segoe UI,Roboto;font-size:13px;color:#6b7280;"
                         "margin:6px 0 4px'>Mark what you actually did (unticked ones are skipped):</div>")
    mark = widgets.Button(description="Mark checked as done", icon="check", layout=Layout(width="200px"))
    mark.style.button_color = "#2e7d32"
    mark.style.font_weight = "600"
    status = widgets.HTML()

    def _do(_):
        sel = [it for cb, it in checks if cb.value]
        if not sel:
            status.value = "<span style='color:#b91c1c;font-size:13px'>Tick at least one.</span>"
            return
        mark_used(wk["level"], sel)
        status.value = ("<span style='color:#2e7d32;font-size:13px'>Logged " + str(len(sel)) +
                        " as done. Generate again to favor new drills.</span>")
    mark.on_click(_do)
    return widgets.VBox([title] + rows + [widgets.HBox([mark], layout=Layout(padding="8px 0 0 0")), status],
                        layout=Layout(margin="14px 0 0 0", border_top="1px solid #eef0f2", padding="10px 0 0 0"))


def launch():
    import ipywidgets as widgets
    from ipywidgets import Layout
    from IPython.display import display, HTML, clear_output

    w_diff = widgets.Dropdown(options=DIFFICULTIES, description="Difficulty",
                              style={"description_width": "80px"}, layout=Layout(width="250px"))
    w_new = widgets.Checkbox(value=False, description="Prefer drills I haven't done yet", indent=False)
    w_btn = widgets.Button(description="Generate workout", icon="bolt", layout=Layout(width="190px", height="38px"))
    w_btn.style.button_color = "#c0392b"
    w_btn.style.font_weight = "600"
    w_fav = widgets.Button(description="My most practiced", icon="bar-chart", layout=Layout(width="180px", height="38px"))
    out, fav_out = widgets.Output(), widgets.Output()

    banner = widgets.HTML("<div style='font-family:-apple-system,Segoe UI,Roboto;padding:14px 16px;"
                          "background:linear-gradient(135deg,#c0392b,#7b241c);color:#fff;border-radius:10px 10px 0 0'>"
                          "<div style='font-size:17px;font-weight:700'>Muay Thai Workout Generator</div>"
                          "<div style='font-size:12px;opacity:.9'>~40 min - warmup + 3 burnouts + 7 drills - copy to Google Keep</div></div>")

    def on_gen(_):
        wk = build_workout(w_diff.value, w_new.value)
        log_workout(wk["level"], wk["burnouts"], wk["drills"], "new" if w_new.value else "any")
        with out:
            clear_output()
            display(HTML(_copy_box(wk["text"])))
            display(_checklist(wk))

    def on_fav(_):
        with fav_out:
            clear_output()
            display(HTML(_practiced_table()))

    w_btn.on_click(on_gen)
    w_fav.on_click(on_fav)
    panel = widgets.VBox([widgets.HBox([w_diff]), widgets.HBox([w_new]), widgets.HBox([w_btn, w_fav])],
                         layout=Layout(border="1px solid #e6e8eb", border_top="none", padding="14px",
                                       border_radius="0 0 10px 10px"))
    display(widgets.VBox([banner, panel, out, fav_out], layout=Layout(max_width="820px")))
