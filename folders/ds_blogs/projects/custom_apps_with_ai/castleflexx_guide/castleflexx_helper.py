"""
CastleFlexx Stretch Guide - supporting code
============================================
All the machinery that powers the notebook lives here so the notebook
itself stays clean. The notebook only needs:

    from castleflexx_helper import launch
    launch()

Files used (all in the same folder as this file):
    castleflexx_exercises.json  - the exercise library (edit freely)
    progress_log.csv            - created automatically, your history
"""

import json
from datetime import datetime
from pathlib import Path

import pandas as pd
import ipywidgets as widgets
from IPython.display import display

HERE = Path(__file__).resolve().parent
LIBRARY_FILE = HERE / "castleflexx_exercises.json"
LOG_FILE = HERE / "progress_log.csv"

LOG_COLUMNS = ["timestamp", "date", "muscle_group", "exercise", "status"]

VIDEO_WIDTH = 560
VIDEO_HEIGHT = 315


# ----------------------------------------------------------------------
# Data loading
# ----------------------------------------------------------------------

def load_library():
    """Read the exercise library JSON."""
    with open(LIBRARY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def exercises_for_group(library, group):
    """All exercises that belong to a muscle group, in library order."""
    return [ex for ex in library["exercises"] if group in ex["groups"]]


# ----------------------------------------------------------------------
# HTML builders (video embed, photos, steps)
# ----------------------------------------------------------------------

def _video_slide(video_id):
    url = f"https://www.youtube.com/embed/{video_id}"
    watch = f"https://www.youtube.com/watch?v={video_id}"
    return (
        f'<iframe width="{VIDEO_WIDTH}" height="{VIDEO_HEIGHT}" '
        f'src="{url}" frameborder="0" '
        f'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
        f'gyroscope; picture-in-picture" allowfullscreen></iframe>'
        f'<div style="font-size:12px;margin-top:4px;">'
        f'Video not loading? <a href="{watch}" target="_blank">Open it on YouTube</a>. '
        f'&nbsp;No sound? Right click this browser tab and choose <b>Unmute site</b>.</div>'
    )


def _photo_slide(video_id, which):
    """which: 'hqdefault', 'hq1', 'hq2', 'hq3' (YouTube preview stills)."""
    src = f"https://img.youtube.com/vi/{video_id}/{which}.jpg"
    return (
        f'<img src="{src}" width="{VIDEO_WIDTH}" '
        f'style="border-radius:8px;" alt="exercise photo"/>'
        f'<div style="font-size:12px;margin-top:4px;color:#666;">'
        f'Preview still from the video</div>'
    )


def _slides_for(video_id):
    """Slide list for the carousel: the video first, then three photos."""
    return [
        ("Video", _video_slide(video_id)),
        ("Photo 1 of 3", _photo_slide(video_id, "hq1")),
        ("Photo 2 of 3", _photo_slide(video_id, "hq2")),
        ("Photo 3 of 3", _photo_slide(video_id, "hq3")),
    ]


def _steps_html(ex):
    items = "".join(f"<li style='margin-bottom:6px;'>{s}</li>" for s in ex["steps"])
    tip = ex.get("tips", "")
    tip_html = (
        f"<div style='background:#f6f3ee;border-left:4px solid #c9a227;"
        f"padding:8px 12px;margin-top:10px;border-radius:4px;'>"
        f"<b>Tip:</b> {tip}</div>" if tip else ""
    )
    return (
        f"<div style='max-width:640px;font-size:14px;line-height:1.5;'>"
        f"<p style='color:#555;'><i>{ex['summary']}</i> "
        f"<span style='color:#999;'>(video length {ex['duration']})</span></p>"
        f"<b>Step by step</b><ol>{items}</ol>{tip_html}</div>"
    )


# ----------------------------------------------------------------------
# Progress log
# ----------------------------------------------------------------------

def read_log():
    if LOG_FILE.exists():
        return pd.read_csv(LOG_FILE)
    return pd.DataFrame(columns=LOG_COLUMNS)


def save_session(library, done_ids):
    """
    Write today's session to the log. Every exercise in the library gets a
    row: 'done' if it was checked, 'skipped' otherwise, so the log always
    shows what was and wasn't covered each day. Saving again on the same
    day replaces that day's rows (so you can update as the day goes on).
    """
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    stamp = now.strftime("%Y-%m-%d %H:%M:%S")

    rows = []
    for ex in library["exercises"]:
        status = "done" if ex["id"] in done_ids else "skipped"
        for group in ex["groups"]:
            rows.append(
                {"timestamp": stamp, "date": today, "muscle_group": group,
                 "exercise": ex["name"], "status": status}
            )

    log = read_log()
    log = log[log["date"] != today]          # replace today's entries
    log = pd.concat([log, pd.DataFrame(rows)], ignore_index=True)
    log.to_csv(LOG_FILE, index=False)
    return today


def history_summary(days=14):
    """One line per day: what was done and which groups were missed."""
    log = read_log()
    if log.empty:
        return None
    out = []
    for date, day in sorted(log.groupby("date"), reverse=True)[:days]:
        done = day[day["status"] == "done"]
        done_groups = sorted(done["muscle_group"].unique())
        all_groups = sorted(day["muscle_group"].unique())
        missed = [g for g in all_groups if g not in done_groups]
        out.append({
            "date": date,
            "stretches done": done["exercise"].nunique(),
            "groups worked": ", ".join(done_groups) if done_groups else "none",
            "groups missed": ", ".join(missed) if missed else "none",
        })
    return pd.DataFrame(out)


# ----------------------------------------------------------------------
# The GUI
# ----------------------------------------------------------------------

class CastleFlexxGuide:
    def __init__(self):
        self.library = load_library()
        self.done_today = set()        # exercise ids checked as done
        self._build()

    # -- widgets -------------------------------------------------------

    def _build(self):
        self.header = widgets.HTML(
            "<h2 style='margin-bottom:0;'>CastleFlexx Stretch Guide</h2>"
            "<p style='color:#666;margin-top:4px;'>Pick a muscle group, choose "
            "your stretches, watch and follow, then save your session.</p>"
            "<div style='background:#fff3cd;border-left:4px solid #e6a700;"
            "padding:8px 12px;border-radius:4px;max-width:640px;font-size:13px;'>"
            "&#128266; <b>No sound on videos?</b> Chrome sometimes mutes the "
            "whole Jupyter tab. Right click this browser tab and choose "
            "<b>Unmute site</b>.</div>"
        )

        self.group_dd = widgets.Dropdown(
            options=self.library["muscle_groups"],
            description="Muscle group:",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="360px"),
        )
        self.show_btn = widgets.Button(
            description="Show stretches", button_style="primary", icon="search"
        )
        self.show_btn.on_click(self._on_show_group)

        self.checkbox_area = widgets.VBox([])
        self.open_btn = widgets.Button(
            description="Open selected", button_style="success", icon="play"
        )
        self.open_btn.on_click(self._on_open_selected)
        self.open_row = widgets.HBox([])   # hidden until a group is shown

        self.accordion_area = widgets.VBox([])

        # -- full body routine builder --
        self.routine_time = widgets.RadioButtons(
            options=[r["label"] for r in self.library.get("routines", [])],
            description="Time I have:",
            style={"description_width": "initial"},
        )
        self.routine_btn = widgets.Button(
            description="Build my routine", button_style="info", icon="list"
        )
        self.routine_btn.on_click(self._on_build_routine)
        self.routine_box = widgets.VBox([
            widgets.HTML(
                "<hr><h3 style='margin-bottom:0;'>Full body routine</h3>"
                "<p style='color:#666;margin-top:4px;'>Short on decisions? Pick "
                "how much time you have and get a ready made set of drills to "
                "go through in order.</p>"
            ),
            widgets.HBox([self.routine_time, self.routine_btn]),
        ]) if self.library.get("routines") else widgets.VBox([])

        self.save_btn = widgets.Button(
            description="Save today's session", button_style="warning", icon="save"
        )
        self.save_btn.on_click(self._on_save)
        self.history_btn = widgets.Button(
            description="Show my history", icon="calendar"
        )
        self.history_btn.on_click(self._on_history)

        self.status_out = widgets.Output()

        self.ui = widgets.VBox([
            self.header,
            widgets.HBox([self.group_dd, self.show_btn]),
            self.checkbox_area,
            self.open_row,
            self.routine_box,
            self.accordion_area,
            widgets.HTML("<hr>"),
            widgets.HBox([self.save_btn, self.history_btn]),
            self.status_out,
        ])

    # -- events --------------------------------------------------------

    def _on_show_group(self, _):
        group = self.group_dd.value
        self._current = exercises_for_group(self.library, group)
        self._checks = []
        boxes = [widgets.HTML(f"<b>{group}</b> &mdash; tick the stretches "
                              f"you want to open:")]
        for ex in self._current:
            cb = widgets.Checkbox(
                value=False, indent=False,
                description=f"{ex['name']}  ({ex['duration']})",
                layout=widgets.Layout(width="520px"),
            )
            self._checks.append((cb, ex))
            boxes.append(cb)
        self.checkbox_area.children = boxes
        self.open_row.children = [self.open_btn]
        self.accordion_area.children = []
        self._flash(f"{len(self._current)} stretches available for {group}.")

    def _on_open_selected(self, _):
        chosen = [ex for cb, ex in self._checks if cb.value]
        if not chosen:
            self._flash("Tick at least one stretch first.", error=True)
            return
        acc = widgets.Accordion(children=[self._panel(ex) for ex in chosen])
        for i, ex in enumerate(chosen):
            acc.set_title(i, ex["name"])
        acc.selected_index = 0
        self.accordion_area.children = [acc]
        self._flash(f"Opened {len(chosen)} stretch(es). "
                    "Use the arrows to flip between video and photos.")

    def _panel(self, ex):
        """One accordion section: carousel + steps + a done checkbox."""
        slides = _slides_for(ex["video_id"])
        idx = {"i": 0}

        stage = widgets.HTML(slides[0][1])
        label = widgets.Label(slides[0][0])
        prev_b = widgets.Button(description="◀", layout=widgets.Layout(width="45px"))
        next_b = widgets.Button(description="▶", layout=widgets.Layout(width="45px"))

        def go(step):
            idx["i"] = (idx["i"] + step) % len(slides)
            label.value, stage.value = slides[idx["i"]][0], slides[idx["i"]][1]

        prev_b.on_click(lambda _b: go(-1))
        next_b.on_click(lambda _b: go(+1))

        done_cb = widgets.Checkbox(
            value=ex["id"] in self.done_today, indent=False,
            description="I did this today",
        )

        def on_done(change, ex_id=ex["id"]):
            if change["new"]:
                self.done_today.add(ex_id)
            else:
                self.done_today.discard(ex_id)

        done_cb.observe(on_done, names="value")

        return widgets.VBox([
            widgets.HBox([prev_b, next_b, label]),
            stage,
            widgets.HTML(_steps_html(ex)),
            done_cb,
        ])

    def _on_build_routine(self, _):
        label = self.routine_time.value
        routine = next(r for r in self.library["routines"] if r["label"] == label)
        by_id = {ex["id"]: ex for ex in self.library["exercises"]}
        chosen = [by_id[i] for i in routine["exercise_ids"]]

        total = sum(ex.get("est_minutes", 2) for ex in chosen)
        items = "".join(
            f"<li style='margin-bottom:4px;'>{ex['name']} "
            f"<span style='color:#999;'>(~{ex.get('est_minutes', 2)} min)</span></li>"
            for ex in chosen
        )
        plan = widgets.HTML(
            f"<div style='background:#eef4fb;border-left:4px solid #1a73e8;"
            f"padding:10px 14px;border-radius:4px;max-width:640px;'>"
            f"<b>Your {label} full body routine</b> "
            f"<span style='color:#666;'>(about {total} minutes total)</span>"
            f"<p style='margin:6px 0;color:#555;'>{routine['description']}</p>"
            f"<ol style='margin:6px 0;'>{items}</ol>"
            f"<span style='font-size:12px;color:#666;'>Work top to bottom. Each "
            f"drill is opened below with its video, photos, and steps. Tick "
            f"'I did this today' as you go, then save your session.</span></div>"
        )

        acc = widgets.Accordion(children=[self._panel(ex) for ex in chosen])
        for i, ex in enumerate(chosen):
            acc.set_title(i, f"{i + 1}. {ex['name']}")
        acc.selected_index = 0
        self.accordion_area.children = [plan, acc]
        self._flash(f"Routine ready: {len(chosen)} drills, about {total} minutes.")

    def _on_save(self, _):
        today = save_session(self.library, self.done_today)
        n = len(self.done_today)
        self._flash(
            f"Saved. {n} stretch(es) marked done for {today}; everything "
            f"else was logged as skipped so your history stays complete."
        )

    def _on_history(self, _):
        with self.status_out:
            self.status_out.clear_output()
            summary = history_summary()
            if summary is None:
                print("No sessions saved yet. Save your first one!")
            else:
                display(summary)

    # -- helpers -------------------------------------------------------

    def _flash(self, msg, error=False):
        with self.status_out:
            self.status_out.clear_output()
            color = "#b00020" if error else "#2e7d32"
            display(widgets.HTML(f"<span style='color:{color};'>{msg}</span>"))

    def show(self):
        display(self.ui)


def launch():
    """Create and display the guide. The one call the notebook makes."""
    guide = CastleFlexxGuide()
    guide.show()
    return guide
