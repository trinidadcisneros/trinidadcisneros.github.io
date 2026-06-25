"""
Fragrance Picker library
=========================
All the logic for the fragrance picker lives here so the notebook stays minimal.

Use in a notebook:

    import fragrance_picker_lib as fp
    fp.setup()      # loads ANTHROPIC_API_KEY, inits Claude, pulls inventory live from Google Drive
    fp.launch()     # shows the interactive picker

Power-user helpers are also exposed: fp.filter_pool, fp.pick_offline,
fp.recommend_with_claude, fp.mark_used, fp.usage_counts, fp.load_usage, etc.

API key is read from the environment (same pattern as nb01_sql_practice.ipynb).
Nothing is hardcoded.
"""

import os
import json
from pathlib import Path
from datetime import datetime

import pandas as pd

# --------------------------------------------------------------------------
# Config (paths are anchored to this file so logs/fallback sit next to it)
# --------------------------------------------------------------------------
SHEET_ID = "16Q9w45SOG5MPgKZo7pSbuRCNOS0MBDJcvl-rHXMVg3M"   # Fragrances sheet (source of truth)
GID = "0"                                                    # 'Inventory' tab; copy #gid=NNN if wrong
USAGE_LOG = Path(__file__).with_name("usage_log.csv")
REC_LOG = Path(__file__).with_name("recommendations_log.csv")

MODEL = "claude-sonnet-4-5"   # claude-haiku-4-5-20251001 (cheaper) or claude-opus-4-8 (strongest)

CANON = ['Ambery/Resinous', 'Aquatic', 'Aromatic Green', 'Creamy Resinous Woods',
         'Dry Aromatic Woods', 'Floral', 'Fougere', 'Fresh Citrus', 'Fruity',
         'Gourmand', 'Leather', 'Spicy', 'Tobacco', 'Vanilla Gourmand']
_CM = {c.lower(): c for c in CANON}

SEASONS = ['Any', 'Cool', 'Warm/Cool', 'Warm']
TIMES = ['Any', 'Day', 'Day/Night', 'Night']
ACTIVITIES = ['Gym', 'Bar / social / date / dinner', 'Home / lounge', 'Work function']
USAGE_MODES = ['Any', 'New (not yet tried)', 'Previously tried']

ACTIVITY_AFFINITY = {
    'Gym':                          ['Fresh Citrus', 'Aquatic', 'Aromatic Green', 'Fruity'],
    'Bar / social / date / dinner': ['Ambery/Resinous', 'Gourmand', 'Vanilla Gourmand', 'Leather', 'Tobacco', 'Spicy', 'Creamy Resinous Woods'],
    'Home / lounge':                ['Vanilla Gourmand', 'Gourmand', 'Creamy Resinous Woods', 'Aromatic Green', 'Tobacco'],
    'Work function':                ['Dry Aromatic Woods', 'Fresh Citrus', 'Fougere', 'Creamy Resinous Woods', 'Aquatic'],
}

# --------------------------------------------------------------------------
# Module state (populated by setup())
# --------------------------------------------------------------------------
client = None
df = None
SIZES = []
CATEGORIES = []


# --------------------------------------------------------------------------
# Claude client (env-based key)
# --------------------------------------------------------------------------
def init_claude(model=None):
    """Create the Anthropic client. Reads ANTHROPIC_API_KEY from the environment."""
    global client, MODEL
    if model:
        MODEL = model
    try:
        from dotenv import load_dotenv, find_dotenv
        load_dotenv(find_dotenv(usecwd=True))
        alt = Path.home() / ("Documents/Development/Coding/bitterscientist.com/bitterscientist.com/"
                             "folders/ds_blogs/projects/data_analyst_interview_prep/.env")
        if alt.exists():
            load_dotenv(alt, override=False)
    except Exception:
        pass

    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ANTHROPIC_API_KEY not found. Set it like your other project, or run:")
        print("    os.environ['ANTHROPIC_API_KEY'] = 'sk-ant-...'   then call fp.setup() again")
        client = None
        return False
    try:
        import anthropic
        client = anthropic.Anthropic()
        print(f"Claude ready ({MODEL})")
        return True
    except Exception as e:
        print(f"Claude init failed: {e}")
        client = None
        return False


# --------------------------------------------------------------------------
# Inventory: LIVE Google Sheet pull every run (no local copy, by design)
# --------------------------------------------------------------------------
# Headers are matched case-insensitively and trimmed, so 'Container ID',
# 'container id', or 'Container ID ' all map correctly.
_COLMAP = {'company': 'company', 'fragrance': 'fragrance', 'strength': 'strength',
           'size ml': 'size', 'fragrantica score': 'score', 'container category': 'category',
           'container id': 'container', 'season': 'season', 'time of day': 'time',
           'top notes': 'top', 'middle notes': 'middle', 'base notes': 'base'}


def clean_inventory(raw):
    rename = {}
    for c in raw.columns:
        key = str(c).strip().lower()
        if key in _COLMAP:
            rename[c] = _COLMAP[key]
    d = raw.rename(columns=rename)
    keep = [v for v in _COLMAP.values() if v in d.columns]
    d = d[keep].fillna('')
    for need in ['company', 'fragrance', 'strength', 'size', 'score', 'category',
                 'container', 'season', 'time', 'top', 'middle', 'base']:
        if need not in d.columns:
            d[need] = ''
    for c in d.columns:
        d[c] = d[c].astype(str).str.strip()
    d['category'] = d['category'].apply(lambda c: _CM.get(c.lower(), c))
    d = d.drop_duplicates(subset=['company', 'fragrance', 'strength', 'size']).reset_index(drop=True)
    d['score_num'] = pd.to_numeric(d['score'], errors='coerce')
    return d


def load_inventory(verbose=True):
    """Pull the Google Sheet LIVE every run. No local copy is used, so the data is
    never stale. Raises a clear error (instead of silently using old data) if the
    sheet can't be reached."""
    url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={GID}"
    try:
        raw = pd.read_csv(url, dtype=str)
    except Exception as e:
        raise RuntimeError(
            "LIVE PULL FAILED - could not reach your Google Sheet (" + str(e) + ").\n"
            "This notebook reads your sheet live every run (no local copy by design), so it stops here\n"
            "rather than show stale data. To fix: in Google Sheets open Share -> General access ->\n"
            "'Anyone with the link' -> Viewer, then re-run. (Want to keep it fully private instead? "
            "Ask me to switch to the Google service-account method.)")
    cols = [str(c).strip().lower() for c in raw.columns]
    if 'container category' not in cols:
        raise RuntimeError(
            "LIVE PULL returned a page that isn't your Inventory sheet (the sheet is likely private,\n"
            "or GID points to the wrong tab). To fix: Share -> 'Anyone with the link' -> Viewer.\n"
            "If it's the wrong tab, open the Inventory tab and set fp.GID to the number after #gid= in the URL.\n"
            "(No local copy is used by design.)")
    d = clean_inventory(raw)
    if verbose:
        n_id = int((d['container'] != '').sum())
        print(f"Pulled LIVE from Google Drive: {len(d)} fragrances | "
              f"Container ID filled for {n_id} of {len(d)}")
        if n_id == 0:
            print("  Note: no Container IDs detected - confirm the column is named 'Container ID' and has values.")
    return d


def setup(model=None, verbose=True):
    """Initialize everything: Claude client + inventory. Returns the DataFrame."""
    global df, SIZES, CATEGORIES
    init_claude(model)
    df = load_inventory(verbose)

    def _sz(v):
        try:
            return float(v)
        except Exception:
            return 9e9

    SIZES = sorted([s for s in df['size'].unique() if s], key=_sz)
    CATEGORIES = [c for c in CANON if c in set(df['category'])]
    if verbose:
        print(f"{len(df)} fragrances | {len(CATEGORIES)} categories | sizes: " + ", ".join(SIZES))
    return df


# --------------------------------------------------------------------------
# Filtering + offline ranking
# --------------------------------------------------------------------------
def filter_pool(category, size='5', season='Any', time='Any'):
    q = df
    if category and category != 'Any':
        q = q[q['category'] == category]
    if size and size != 'Any':
        q = q[q['size'] == str(size)]
    if season and season != 'Any':
        q = q[q['season'] == season]
    if time and time != 'Any':
        q = q[q['time'] == time]
    return q.copy()


def pick_offline(pool, activity=None, n=3):
    """Weighted random by Fragrantica score (+ activity affinity), so higher rated
    show more often but anything can surface. Good for testing more of the collection."""
    p = pool.copy()
    if p.empty:
        return p
    base = p['score_num'].fillna(4.0)
    w = base - base.min() + 0.1
    if activity in ACTIVITY_AFFINITY:
        w = w + p['category'].isin(set(ACTIVITY_AFFINITY[activity])).astype(float)
    return p.sample(n=min(n, len(p)), weights=w, replace=False)


# --------------------------------------------------------------------------
# Claude recommendation (activity-aware, reasons on the note pyramid)
# --------------------------------------------------------------------------
def recommend_with_claude(pool, activity, season='Any', time='Any', n=3):
    if client is None:
        return None, "Claude client not ready - using offline ranking instead."
    cols = ['company', 'fragrance', 'category', 'score', 'season', 'time', 'top', 'middle', 'base']
    cand = pool[[c for c in cols if c in pool.columns]].to_dict('records')[:50]
    if not cand:
        return None, "No candidates to send."

    def _fmt_notes(c):
        parts = []
        for lbl, k in [('Top', 'top'), ('Heart', 'middle'), ('Base', 'base')]:
            v = str(c.get(k, '') or '').strip()
            if v and v.lower() != 'x':
                parts.append(f"{lbl}: {v}")
        return "  ||  notes -> " + "; ".join(parts) if parts else ""

    listing = "\n".join(
        f"{i+1}. {c['company']} - {c['fragrance']} | {c['category']} | score {c['score']} "
        f"| {c['season']} | {c['time']}{_fmt_notes(c)}"
        for i, c in enumerate(cand)
    )
    system = (
        "You are a knowledgeable fragrance advisor. From the user's own collection, pick the best "
        "scents for a specific occasion. Weigh projection and sillage: gym = clean and light, never "
        "cloying; work function = polished, inoffensive, moderate projection; bar/social/date/dinner "
        "= attractive, more projection and warmth; home/lounge = comforting and soft. Also weigh "
        "season and time. When a note composition is given (Top/Heart/Base), use it as the main basis "
        "for fit: bright citrus, aquatic, and green notes suit the gym; ambers, vanillas, gourmands, "
        "tobacco, and spices suit evenings out; soft woods and vanillas suit lounging; clean woods and "
        "fougeres suit work. Only choose from the provided list."
    )
    user = (
        f"Occasion: {activity}\nSeason filter: {season}\nTime filter: {time}\n\n"
        f"Candidates (already filtered):\n{listing}\n\n"
        f"Choose the {n} best. Return ONLY JSON: "
        f'[{{"company": "...", "fragrance": "...", "reason": "one concise sentence"}}]'
    )
    try:
        msg = client.messages.create(model=MODEL, max_tokens=700, system=system,
                                     messages=[{"role": "user", "content": user}])
        text = msg.content[0].text.strip()
        if "```" in text:
            text = text.split("```json", 1)[-1].split("```", 1)[0] if "```json" in text else text.split("```")[1]
            text = text.strip()
        return json.loads(text), None
    except Exception as e:
        return None, f"Claude error ({e}); using offline ranking instead."


# --------------------------------------------------------------------------
# Usage tracking
# --------------------------------------------------------------------------
USAGE_COLS = ['timestamp', 'activity', 'company', 'fragrance', 'category', 'size', 'season', 'time']


def load_usage():
    if USAGE_LOG.exists():
        return pd.read_csv(USAGE_LOG, dtype=str).fillna('')
    return pd.DataFrame(columns=USAGE_COLS)


def mark_used(activity, rec):
    u = load_usage()
    row = {'timestamp': datetime.now().isoformat(timespec='seconds'), 'activity': activity,
           'company': rec.get('company', ''), 'fragrance': rec.get('fragrance', ''),
           'category': rec.get('category', ''), 'size': rec.get('size', ''),
           'season': rec.get('season', ''), 'time': rec.get('time', '')}
    u = pd.concat([u, pd.DataFrame([row])], ignore_index=True)
    u.to_csv(USAGE_LOG, index=False)
    return len(u)


def usage_counts(activity=None):
    u = load_usage()
    if activity and not u.empty:
        u = u[u['activity'] == activity]
    if u.empty:
        return {}
    return u.groupby(['company', 'fragrance']).size().to_dict()


def used_keys(activity=None):
    return set(usage_counts(activity).keys())


def apply_usage(pool, activity, usage_mode):
    if usage_mode == 'Any' or pool.empty:
        return pool
    uk = used_keys(activity)
    mask = pool.apply(lambda r: (r['company'], r['fragrance']) in uk, axis=1)
    return pool[~mask] if usage_mode.startswith('New') else pool[mask]


def log_recommendation(activity, category, size, season, time, mode, picks):
    row = {'timestamp': datetime.now().isoformat(timespec='seconds'), 'activity': activity,
           'category': category, 'size': size, 'season': season, 'time': time, 'mode': mode,
           'suggestions': '; '.join(f"{p.get('company','')} - {p.get('fragrance','')}" for p in picks)}
    pd.DataFrame([row]).to_csv(REC_LOG, mode='a', header=not REC_LOG.exists(), index=False)


# --------------------------------------------------------------------------
# Rendering
# --------------------------------------------------------------------------
def _records_from_df(pdf):
    cols = ['company', 'fragrance', 'category', 'size', 'score', 'season', 'time', 'container']
    return pdf[[c for c in cols if c in pdf.columns]].to_dict('records')


def _enrich_picks(picks, pool):
    out = []
    for p in picks:
        co, fr = p.get('company', ''), p.get('fragrance', '')
        m = pool[(pool['company'] == co) & (pool['fragrance'] == fr)]
        if m.empty:
            m = pool[pool['fragrance'] == fr]
        rec = {'company': co, 'fragrance': fr, 'reason': p.get('reason', '')}
        if not m.empty:
            r = m.iloc[0]
            rec.update({'category': r['category'], 'size': r['size'], 'score': r['score'],
                        'season': r['season'], 'time': r['time'],
                        'container': r.get('container', '')})
        out.append(rec)
    return out


def _badge(score):
    try:
        s = float(score)
    except Exception:
        s = None
    color = '#2e7d32' if (s and s >= 4.4) else ('#f9a825' if (s and s >= 4.1) else '#9e9e9e')
    return (f"<span style='background:{color};color:#fff;padding:2px 9px;border-radius:11px;"
            f"font-size:12px;font-weight:600'>{score or '-'}</span>")


def show_results(records, occasion, mode_label, activity=None):
    """Static HTML table (used for programmatic / non-widget output)."""
    from IPython.display import HTML, display
    counts = usage_counts(activity)
    th = ("text-align:left;padding:9px 12px;font-size:11px;text-transform:uppercase;"
          "letter-spacing:.04em;color:#8a8f98;border-bottom:2px solid #e6e8eb;")
    td = "padding:11px 12px;border-bottom:1px solid #eef0f2;color:#3c4149;font-size:13px;vertical-align:top;"
    rows = ''
    for r in records:
        used = counts.get((r.get('company', ''), r.get('fragrance', '')), 0)
        reason = r.get('reason')
        reason_html = (f"<div style='color:#6b7280;font-size:12px;margin-top:4px;line-height:1.4'>{reason}</div>"
                       if reason else '')
        box = r.get('container', '')
        box_html = (f"<span style='background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe;"
                    f"padding:2px 8px;border-radius:6px;font-family:ui-monospace,Menlo,monospace;"
                    f"font-size:12px;font-weight:600'>{box}</span>") if box else "<span style='color:#c0c4c9'>-</span>"
        rows += (f"<tr><td style='{td}'><div style='font-weight:600;color:#111827'>{r.get('fragrance','')}</div>{reason_html}</td>"
                 f"<td style='{td};color:#6b7280'>{r.get('company','')}</td>"
                 f"<td style='{td}'>{box_html}</td>"
                 f"<td style='{td}'>{r.get('category','')}</td>"
                 f"<td style='{td}'>{r.get('size','')} ml</td>"
                 f"<td style='{td}'>{_badge(r.get('score',''))}</td>"
                 f"<td style='{td}'>{r.get('season','')}</td>"
                 f"<td style='{td}'>{r.get('time','')}</td>"
                 f"<td style='{td};color:#6b7280'>{str(used)+'x' if used else '-'}</td></tr>")
    head = ''.join(f"<th style='{th}'>{h}</th>" for h in
                   ['Fragrance', 'Company', 'Box', 'Category', 'Size', 'Score', 'Season', 'Time', 'Used'])
    html = (f"<div style='font-family:-apple-system,Segoe UI,Roboto,sans-serif;max-width:920px'>"
            f"<div style='font-size:13px;color:#6b7280;margin:4px 0 10px'>{mode_label} for "
            f"<b style='color:#c0392b'>{occasion}</b></div>"
            f"<table style='border-collapse:collapse;width:100%;background:#fff;"
            f"box-shadow:0 1px 4px rgba(0,0,0,.08);border-radius:10px;overflow:hidden'>"
            f"<thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table></div>")
    display(HTML(html))


# --------------------------------------------------------------------------
# Interactive GUI
# --------------------------------------------------------------------------
_W = {'name': '240px', 'co': '130px', 'con': '80px', 'cat': '120px', 'sz': '50px', 'sc': '58px', 'us': '45px'}


def _render_interactive(records, activity, occasion, mode_label):
    import ipywidgets as widgets
    from ipywidgets import Layout
    counts = usage_counts(activity)
    thx = 'font-size:11px;text-transform:uppercase;letter-spacing:.04em;color:#8a8f98;'
    header = widgets.HTML(
        "<div style='display:flex;padding:0 0 6px 34px;border-bottom:2px solid #e6e8eb;"
        "font-family:-apple-system,Segoe UI,Roboto'>"
        + ''.join(f"<div style='width:{_W[k]};{thx}'>{lbl}</div>" for k, lbl in
                  [('name', 'Fragrance'), ('co', 'Company'), ('con', 'Box'), ('cat', 'Category'),
                   ('sz', 'Size'), ('sc', 'Score'), ('us', 'Used')]) + "</div>")
    rows, checks = [], []
    for r in records:
        used = counts.get((r.get('company', ''), r.get('fragrance', '')), 0)
        reason = r.get('reason')
        reason_html = (f"<div style='color:#6b7280;font-size:12px;margin-top:3px;line-height:1.35;"
                       f"width:240px'>{reason}</div>" if reason else '')
        info = widgets.HTML(
            "<div style='display:flex;align-items:flex-start;font-family:-apple-system,Segoe UI,Roboto;"
            "font-size:13px;color:#3c4149'>"
            f"<div style='width:{_W['name']}'><b style='color:#111827'>{r.get('fragrance','')}</b>{reason_html}</div>"
            f"<div style='width:{_W['co']};color:#6b7280'>{r.get('company','')}</div>"
            f"<div style='width:{_W['con']}'>" + (f"<span style='background:#eef2ff;color:#3730a3;border:1px solid #c7d2fe;padding:1px 7px;border-radius:6px;font-family:ui-monospace,Menlo,monospace;font-size:12px;font-weight:600'>{r.get('container','')}</span>" if r.get('container','') else "<span style='color:#c0c4c9'>-</span>") + "</div>"
            f"<div style='width:{_W['cat']}'>{r.get('category','')}</div>"
            f"<div style='width:{_W['sz']}'>{r.get('size','')}ml</div>"
            f"<div style='width:{_W['sc']}'>{_badge(r.get('score',''))}</div>"
            f"<div style='width:{_W['us']};color:#6b7280'>{str(used)+'x' if used else '-'}</div></div>")
        cb = widgets.Checkbox(value=False, indent=False, layout=Layout(width='30px'))
        rows.append(widgets.HBox([cb, info], layout=Layout(align_items='flex-start',
                    padding='8px 0', border_bottom='1px solid #eef0f2')))
        checks.append((cb, r))
    title = widgets.HTML(f"<div style='font-family:-apple-system,Segoe UI,Roboto;font-size:13px;"
                         f"color:#6b7280;margin:2px 0 8px'>{mode_label} for "
                         f"<b style='color:#c0392b'>{occasion}</b></div>")
    mark = widgets.Button(description='Mark selected as used', icon='check', layout=Layout(width='210px'))
    mark.style.button_color = '#2e7d32'
    mark.style.font_weight = '600'
    status = widgets.HTML()

    def _do(_):
        m = 0
        for cb, r in checks:
            if cb.value:
                mark_used(activity, r)
                m += 1
                cb.value = False
        status.value = (f"<span style='color:#2e7d32;font-size:13px'>Logged {m} as used for {activity}. "
                        f"Re-run Recommend to see updated counts.</span>"
                        if m else "<span style='color:#b91c1c;font-size:13px'>Tick a box first.</span>")
    mark.on_click(_do)
    return widgets.VBox([title, header] + rows +
                        [widgets.HBox([mark], layout=Layout(padding='10px 0 0 0')), status])


def launch():
    """Build and display the interactive picker. Call after setup()."""
    import ipywidgets as widgets
    from ipywidgets import Layout
    from IPython.display import display, HTML, clear_output

    if df is None:
        print("Inventory not loaded. Run fp.setup() first.")
        return

    dd = dict(style={'description_width': '70px'}, layout=Layout(width='240px'))
    w_act = widgets.Dropdown(options=ACTIVITIES, description='Activity', **dd)
    w_cat = widgets.Dropdown(options=['Any'] + CATEGORIES, description='Category', **dd)
    w_size = widgets.Dropdown(options=SIZES, value=('5' if '5' in SIZES else SIZES[0]), description='Size ml', **dd)
    w_sea = widgets.Dropdown(options=SEASONS, description='Season', **dd)
    w_time = widgets.Dropdown(options=TIMES, description='Time', **dd)
    w_use = widgets.Dropdown(options=USAGE_MODES, description='Usage', **dd)
    w_ai = widgets.Checkbox(value=bool(client), description='Use Claude (activity-aware)', indent=False)
    w_btn = widgets.Button(description='Recommend 3', icon='magic', layout=Layout(width='160px', height='38px'))
    w_btn.style.button_color = '#c0392b'
    w_btn.style.font_weight = '600'
    w_fav = widgets.Button(description='My most used', icon='star', layout=Layout(width='150px', height='38px'))
    out, fav_out = widgets.Output(), widgets.Output()

    banner = widgets.HTML("<div style='font-family:-apple-system,Segoe UI,Roboto;padding:14px 16px;"
                          "background:linear-gradient(135deg,#c0392b,#7b241c);color:#fff;border-radius:10px 10px 0 0'>"
                          "<div style='font-size:17px;font-weight:700'>Fragrance Picker</div>"
                          "<div style='font-size:12px;opacity:.9'>Live from Google Drive - choose occasion, filters, and usage</div></div>")

    def on_click(_):
        pool = filter_pool(w_cat.value, w_size.value, w_sea.value, w_time.value)
        pool = apply_usage(pool, w_act.value, w_use.value)
        with out:
            clear_output()
            display(HTML(f"<div style='font-family:-apple-system,Segoe UI,Roboto;color:#6b7280;"
                         f"font-size:13px'>{len(pool)} match your filters ({w_use.value}). Picking 3 ...</div>"))
            if pool.empty:
                display(HTML("<div style='color:#b91c1c;font-size:13px'>No matches. Loosen filters, "
                             "or switch Usage to Any.</div>"))
                return
            if w_ai.value:
                ai, note = recommend_with_claude(pool, w_act.value, w_sea.value, w_time.value)
                if ai:
                    recs = _enrich_picks(ai, pool)
                    log_recommendation(w_act.value, w_cat.value, w_size.value, w_sea.value, w_time.value, 'claude', recs)
                    clear_output()
                    display(_render_interactive(recs, w_act.value, w_act.value, 'Claude picks'))
                    return
                if note:
                    print(note)
            recs = _records_from_df(pick_offline(pool, w_act.value))
            log_recommendation(w_act.value, w_cat.value, w_size.value, w_sea.value, w_time.value, 'offline', recs)
            clear_output()
            display(_render_interactive(recs, w_act.value, w_act.value, 'Offline picks'))

    def on_fav(_):
        with fav_out:
            clear_output()
            c = usage_counts(w_act.value)
            if not c:
                display(HTML("<i style='font-family:-apple-system,Segoe UI,Roboto;color:#6b7280;"
                             "font-size:13px'>No usage logged yet for this activity.</i>"))
                return
            items = sorted(c.items(), key=lambda x: -x[1])
            tr = ''.join(f"<tr><td style='padding:6px 12px;border-bottom:1px solid #eee'>{fr}</td>"
                         f"<td style='padding:6px 12px;border-bottom:1px solid #eee;color:#6b7280'>{co}</td>"
                         f"<td style='padding:6px 12px;border-bottom:1px solid #eee'><b>{n}x</b></td></tr>"
                         for (co, fr), n in items)
            display(HTML("<div style='font-family:-apple-system,Segoe UI,Roboto;font-size:13px;margin-top:8px'>"
                         f"<b>Most used for {w_act.value}</b>"
                         "<table style='border-collapse:collapse;margin-top:6px'>"
                         "<thead><tr>"
                         "<th style='text-align:left;padding:6px 12px;color:#8a8f98;font-size:11px;text-transform:uppercase'>Fragrance</th>"
                         "<th style='text-align:left;padding:6px 12px;color:#8a8f98;font-size:11px;text-transform:uppercase'>Company</th>"
                         "<th style='text-align:left;padding:6px 12px;color:#8a8f98;font-size:11px;text-transform:uppercase'>Used</th>"
                         f"</tr></thead><tbody>{tr}</tbody></table></div>"))

    w_btn.on_click(on_click)
    w_fav.on_click(on_fav)
    panel = widgets.VBox([widgets.HBox([w_act, w_cat]),
                          widgets.HBox([w_size, w_sea, w_time]),
                          widgets.HBox([w_use, w_ai]),
                          widgets.HBox([w_btn, w_fav])],
                         layout=Layout(border='1px solid #e6e8eb', border_top='none',
                                       padding='14px', border_radius='0 0 10px 10px'))
    display(widgets.VBox([banner, panel, out, fav_out], layout=Layout(max_width='820px')))
