"""
UI Components for the Interview Practice Tool.

Provides:
- Custom CSS injection for polished notebook styling
- Phase widget builder with Submit, Hint, Example, and Record buttons
- Web Speech API integration for browser-based voice recording (free, no API cost)
- Progress tracker widget
"""

import re
import time
from IPython.display import display, HTML, clear_output, Javascript
import ipywidgets as widgets


def _md_to_html(text):
    """
    Convert basic markdown to HTML for display in notebook widgets.
    Handles: **bold**, *italic*, - bullet lists, numbered lists,
    ## headings, paragraphs, and inline $formulas$.
    """
    if not text:
        return ""
    # Escape any stray HTML
    text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    lines = text.split("\n")
    html_parts = []
    in_list = False
    list_type = None  # "ul" or "ol"

    for line in lines:
        stripped = line.strip()

        # Empty line ends current list / adds paragraph break
        if not stripped:
            if in_list:
                html_parts.append(f"</{list_type}>")
                in_list = False
                list_type = None
            html_parts.append("")
            continue

        # Headings: ### or ##
        heading_match = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading_match:
            if in_list:
                html_parts.append(f"</{list_type}>")
                in_list = False
                list_type = None
            level = min(len(heading_match.group(1)) + 2, 6)  # h3-h6
            html_parts.append(f"<h{level}>{_inline_md(heading_match.group(2), escape=False)}</h{level}>")
            continue

        # Unordered list: - item or * item
        ul_match = re.match(r"^[-*]\s+(.+)$", stripped)
        if ul_match:
            if not in_list or list_type != "ul":
                if in_list:
                    html_parts.append(f"</{list_type}>")
                html_parts.append("<ul>")
                in_list = True
                list_type = "ul"
            html_parts.append(f"<li>{_inline_md(ul_match.group(1), escape=False)}</li>")
            continue

        # Ordered list: 1. item
        ol_match = re.match(r"^\d+[.)]\s+(.+)$", stripped)
        if ol_match:
            if not in_list or list_type != "ol":
                if in_list:
                    html_parts.append(f"</{list_type}>")
                html_parts.append("<ol>")
                in_list = True
                list_type = "ol"
            html_parts.append(f"<li>{_inline_md(ol_match.group(1), escape=False)}</li>")
            continue

        # Regular text — close any open list, wrap in <p>
        if in_list:
            html_parts.append(f"</{list_type}>")
            in_list = False
            list_type = None
        html_parts.append(f"<p>{_inline_md(stripped, escape=False)}</p>")

    if in_list:
        html_parts.append(f"</{list_type}>")

    return "\n".join(html_parts)


def _inline_md(text, escape=True):
    """Convert inline markdown: **bold**, *italic*, `code`, $formula$."""
    if not text:
        return ""
    if escape:
        text = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    # Bold: **text** or __text__
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    # Italic: *text* or _text_ (but not inside words)
    text = re.sub(r"(?<!\w)\*(.+?)\*(?!\w)", r"<em>\1</em>", text)
    text = re.sub(r"(?<!\w)_(.+?)_(?!\w)", r"<em>\1</em>", text)
    # Inline code: `text`
    text = re.sub(r"`(.+?)`", r"<code>\1</code>", text)
    # Inline formula: $formula$ → render as code-styled
    text = re.sub(r"\$(.+?)\$", r'<code style="background:#e8e0ff; padding:1px 4px; border-radius:3px;">\1</code>', text)
    # Colon-separated label pattern: "Label:" at start of line
    text = re.sub(r"^([A-Z][A-Za-z\s]+):", r"<strong>\1:</strong>", text)
    return text


# ============================================================
# Global CSS — injected once at notebook startup
# ============================================================

NOTEBOOK_CSS = """
<style>
/* ── Reset & Base ───────────────────────────────────── */
.ipu-app {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    max-width: 900px;
    margin: 0 auto;
}

/* ── Header Banner ──────────────────────────────────── */
.ipu-header {
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    color: white;
    padding: 28px 32px;
    border-radius: 12px;
    margin-bottom: 24px;
}
.ipu-header h1 {
    margin: 0 0 6px 0;
    font-size: 24px;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.ipu-header p {
    margin: 0;
    font-size: 14px;
    color: #94a3b8;
    line-height: 1.5;
}

/* ── Section Headers ────────────────────────────────── */
.ipu-section {
    margin: 28px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid #e2e8f0;
}
.ipu-section h2 {
    margin: 0;
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
}
.ipu-section p {
    margin: 4px 0 0 0;
    font-size: 13px;
    color: #64748b;
}

/* ── Scenario Card ──────────────────────────────────── */
.ipu-scenario {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #2E86AB;
    border-radius: 8px;
    padding: 20px 24px;
    margin: 12px 0;
}
.ipu-scenario h3 {
    margin: 0 0 12px 0;
    font-size: 16px;
    font-weight: 700;
    color: #1a1a2e;
}
.ipu-scenario-row {
    display: flex;
    padding: 5px 0;
    font-size: 14px;
    line-height: 1.5;
}
.ipu-scenario-label {
    width: 120px;
    font-weight: 600;
    color: #475569;
    flex-shrink: 0;
}
.ipu-scenario-value {
    color: #1e293b;
}
.ipu-scenario-constraint {
    color: #dc2626;
    font-weight: 500;
}
.ipu-scenario-meta {
    margin-top: 10px;
    font-size: 12px;
    color: #94a3b8;
}

/* ── Phase Card ─────────────────────────────────────── */
.ipu-phase {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 0;
    margin: 16px 0;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.ipu-phase-header {
    padding: 16px 24px;
    display: flex;
    align-items: center;
    gap: 12px;
}
.ipu-phase-num {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: 700;
    font-size: 16px;
    color: white;
    flex-shrink: 0;
}
.ipu-phase-title {
    font-size: 16px;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0;
}
.ipu-phase-instruction {
    padding: 0 24px 16px 24px;
    font-size: 14px;
    color: #475569;
    line-height: 1.6;
}
.ipu-phase-body {
    padding: 0 24px 20px 24px;
}

/* Phase colors */
.ipu-phase-discovery .ipu-phase-header { background: #e8f4f8; }
.ipu-phase-discovery .ipu-phase-num { background: #2E86AB; }
.ipu-phase-validation .ipu-phase-header { background: #fff7eb; }
.ipu-phase-validation .ipu-phase-num { background: #F18F01; }
.ipu-phase-build .ipu-phase-header { background: #f0eeff; }
.ipu-phase-build .ipu-phase-num { background: #6c63ff; }
.ipu-phase-rollout .ipu-phase-header { background: #e8f7f3; }
.ipu-phase-rollout .ipu-phase-num { background: #2CA58D; }
.ipu-phase-scale .ipu-phase-header { background: #fdeaea; }
.ipu-phase-scale .ipu-phase-num { background: #E15554; }

/* ── Button Row ─────────────────────────────────────── */
.ipu-btn-row {
    display: flex;
    gap: 8px;
    flex-wrap: wrap;
    margin-top: 10px;
}

/* ── Score Card ─────────────────────────────────────── */
.ipu-score {
    border-radius: 8px;
    padding: 18px 20px;
    margin-top: 12px;
}
.ipu-score-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}
.ipu-score-composite {
    font-size: 28px;
    font-weight: 800;
}
.ipu-score-label {
    font-size: 13px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.ipu-score-bar-row {
    display: flex;
    align-items: center;
    margin: 4px 0;
}
.ipu-score-bar-label {
    width: 180px;
    font-size: 13px;
    color: #475569;
}
.ipu-score-bar-track {
    flex: 1;
    background: #e5e7eb;
    border-radius: 4px;
    height: 14px;
    margin: 0 10px;
    overflow: hidden;
}
.ipu-score-bar-fill {
    height: 14px;
    border-radius: 4px;
    transition: width 0.4s ease;
}
.ipu-score-bar-value {
    font-size: 13px;
    font-weight: 600;
    width: 35px;
    text-align: right;
}
.ipu-score-feedback {
    background: white;
    border-radius: 6px;
    padding: 12px 14px;
    margin-top: 12px;
    font-size: 14px;
    line-height: 1.6;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.ipu-score-feedback strong {
    display: block;
    margin-bottom: 4px;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.ipu-score-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
}
.ipu-score-missed {
    background: #fff7ed;
    border-left: 3px solid #F18F01;
    border-radius: 6px;
    padding: 10px 14px;
    margin-top: 10px;
    font-size: 13px;
}
.ipu-score-missed strong {
    color: #92400e;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
}
.ipu-score-missed ul {
    margin: 4px 0 0 16px;
    padding: 0;
}
.ipu-score-latency {
    font-size: 11px;
    color: #94a3b8;
    margin-top: 8px;
}

/* ── Hint / Example Cards ───────────────────────────── */
.ipu-hint {
    background: #fffbeb;
    border-left: 3px solid #F18F01;
    border-radius: 6px;
    padding: 12px 16px;
    margin-top: 10px;
    font-size: 14px;
    line-height: 1.6;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.ipu-hint strong { color: #92400e; }
.ipu-hint .ipu-text-body { margin-top: 6px; }
.ipu-hint .ipu-text-body p { margin: 6px 0; }
.ipu-example {
    background: #f0eeff;
    border-left: 3px solid #6c63ff;
    border-radius: 6px;
    padding: 14px 16px;
    margin-top: 10px;
    font-size: 14px;
    line-height: 1.7;
    word-wrap: break-word;
    overflow-wrap: break-word;
}
.ipu-example strong { color: #4338ca; }
.ipu-example .ipu-text-body { margin-top: 10px; }
.ipu-example .ipu-text-body p { margin: 8px 0; }
.ipu-example .ipu-text-body ul,
.ipu-example .ipu-text-body ol { margin: 6px 0 6px 20px; padding: 0; }
.ipu-example .ipu-text-body li { margin: 3px 0; }
.ipu-example .ipu-text-body h3,
.ipu-example .ipu-text-body h4 {
    margin: 12px 0 4px 0;
    font-size: 14px;
    font-weight: 700;
    color: #4338ca;
}

/* ── Record Button ──────────────────────────────────── */
.ipu-record-btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border: 1px solid #dc2626;
    background: white;
    color: #dc2626;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
}
.ipu-record-btn:hover {
    background: #fef2f2;
}
.ipu-record-btn.recording {
    background: #dc2626;
    color: white;
    animation: ipu-pulse 1.5s ease-in-out infinite;
}
@keyframes ipu-pulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
    50% { box-shadow: 0 0 0 8px rgba(220, 38, 38, 0); }
}
.ipu-record-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: currentColor;
}
.ipu-record-status {
    font-size: 12px;
    color: #94a3b8;
    margin-top: 4px;
}

/* ── Progress Tracker ───────────────────────────────── */
.ipu-progress {
    display: flex;
    gap: 4px;
    margin: 20px 0;
}
.ipu-progress-step {
    flex: 1;
    height: 6px;
    border-radius: 3px;
    background: #e2e8f0;
    transition: background 0.3s;
}
.ipu-progress-step.done { background: #22c55e; }
.ipu-progress-step.active { background: #2E86AB; }

/* ── Summary Table ──────────────────────────────────── */
.ipu-summary {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 20px 24px;
    margin: 16px 0;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}
.ipu-summary h3 {
    margin: 0 0 16px 0;
    font-size: 18px;
    font-weight: 700;
    color: #1a1a2e;
}
.ipu-summary table {
    width: 100%;
    border-collapse: collapse;
}
.ipu-summary th {
    text-align: left;
    padding: 8px 10px;
    border-bottom: 2px solid #e2e8f0;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #64748b;
}
.ipu-summary td {
    padding: 8px 10px;
    border-bottom: 1px solid #f1f5f9;
    font-size: 14px;
}
.ipu-badge {
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
}
.ipu-badge-strong { background: #dcfce7; color: #166534; }
.ipu-badge-developing { background: #fef9c3; color: #854d0e; }
.ipu-badge-needs-work { background: #fee2e2; color: #991b1b; }

/* ── Phase Guide (collapsible) ─────────────────────── */
.ipu-guide {
    background: #f0f7ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    margin: 8px 0;
    overflow: hidden;
}
.ipu-guide-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    color: #1e40af;
    background: none;
    border: none;
    width: 100%;
    text-align: left;
}
.ipu-guide-toggle:hover { background: #dbeafe; }
.ipu-guide-arrow { transition: transform 0.2s; font-size: 10px; }
.ipu-guide.open .ipu-guide-arrow { transform: rotate(90deg); }
.ipu-guide-body {
    display: none;
    padding: 0 14px 14px 14px;
    font-size: 13px;
    line-height: 1.6;
    color: #334155;
}
.ipu-guide.open .ipu-guide-body { display: block; }
.ipu-guide-body h4 {
    margin: 10px 0 4px 0;
    font-size: 12px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #1e40af;
}
.ipu-guide-body ul {
    margin: 2px 0 8px 16px;
    padding: 0;
}
.ipu-guide-body li {
    margin: 3px 0;
}

/* ── Speaking Script (collapsible) ─────────────────── */
.ipu-script {
    background: #faf5ff;
    border: 1px solid #d8b4fe;
    border-radius: 8px;
    margin: 8px 0;
    overflow: hidden;
}
.ipu-script-toggle {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 10px 14px;
    cursor: pointer;
    font-size: 13px;
    font-weight: 600;
    color: #7c3aed;
    background: none;
    border: none;
    width: 100%;
    text-align: left;
}
.ipu-script-toggle:hover { background: #f3e8ff; }
.ipu-script-arrow { transition: transform 0.2s; font-size: 10px; }
.ipu-script.open .ipu-script-arrow { transform: rotate(90deg); }
.ipu-script-body {
    display: none;
    padding: 0 14px 14px 14px;
    font-size: 13px;
    line-height: 1.6;
    color: #334155;
}
.ipu-script.open .ipu-script-body { display: block; }

.ipu-script-section {
    margin: 8px 0;
    border: 1px solid #e9d5ff;
    border-radius: 6px;
    overflow: hidden;
}
.ipu-script-section-header {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px 12px;
    cursor: pointer;
    font-size: 13px;
    background: #faf5ff;
}
.ipu-script-section-header:hover { background: #f3e8ff; }
.ipu-script-label {
    display: inline-block;
    padding: 1px 8px;
    border-radius: 4px;
    font-size: 11px;
    font-weight: 700;
    min-width: 36px;
    text-align: center;
}
.ipu-script-label-open { background: #2E86AB; color: white; }
.ipu-script-label-action { background: #F18F01; color: white; }
.ipu-script-label-number { background: #6c63ff; color: white; }
.ipu-script-label-bridge { background: #2CA58D; color: white; }
.ipu-script-section-title { font-weight: 600; color: #1a1a2e; }
.ipu-script-section-arrow { margin-left: auto; font-size: 10px; transition: transform 0.2s; }
.ipu-script-section.open .ipu-script-section-arrow { transform: rotate(90deg); }

.ipu-script-section-body {
    display: none;
    padding: 8px 12px 12px 12px;
    border-top: 1px solid #e9d5ff;
}
.ipu-script-section.open .ipu-script-section-body { display: block; }

.ipu-script-bullet {
    display: flex;
    gap: 8px;
    margin: 4px 0;
    font-size: 13px;
}
.ipu-script-bullet-arrow { color: #7c3aed; flex-shrink: 0; }
.ipu-script-bullet-kw { font-weight: 700; color: #1a1a2e; }
.ipu-script-quote {
    margin: 6px 0 6px 20px;
    padding: 8px 12px;
    background: #f8fafc;
    border-left: 3px solid #7c3aed;
    border-radius: 0 4px 4px 0;
    font-size: 12px;
    font-style: italic;
    color: #555;
}
.ipu-script-quote-label {
    font-size: 11px;
    font-weight: 700;
    color: #7c3aed;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 2px;
}

/* ── Phase Separator ───────────────────────────────── */
.ipu-phase-separator {
    margin: 40px 0 24px 0;
    padding: 20px 24px;
    border-radius: 12px;
    border-left: 5px solid;
}
.ipu-phase-separator h2 {
    margin: 0 0 4px 0;
    font-size: 20px;
    font-weight: 700;
}
.ipu-phase-separator p {
    margin: 0;
    font-size: 13px;
    color: #64748b;
}

/* ── Sub-step Cards ────────────────────────────────── */
.ipu-substep {
    background: white;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    margin: 12px 0;
    overflow: hidden;
}
.ipu-substep-header {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 12px 16px;
    border-bottom: 1px solid #f1f5f9;
}
.ipu-substep-icon {
    display: flex;
    align-items: center;
    justify-content: center;
    width: 28px;
    height: 28px;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 700;
    color: white;
    flex-shrink: 0;
}
.ipu-substep-title {
    font-size: 14px;
    font-weight: 600;
    color: #1a1a2e;
}
.ipu-substep-body {
    padding: 12px 16px;
}
.ipu-substep-instruction {
    font-size: 13px;
    color: #475569;
    margin: 0 0 8px 0;
    line-height: 1.5;
}
.ipu-substep-hint {
    font-size: 12px;
    color: #7c8db0;
    background: #f8fafc;
    padding: 8px 12px;
    border-radius: 6px;
    margin: 0 0 10px 0;
    border-left: 3px solid #cbd5e1;
    line-height: 1.5;
}
.ipu-substep-feedback {
    margin-top: 8px;
}
.ipu-substep-score-badge {
    display: inline-block;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 12px;
    font-weight: 600;
    margin-bottom: 6px;
}
.ipu-substep-feedback-text {
    font-size: 13px;
    line-height: 1.5;
    color: #334155;
}
.ipu-substep-missing {
    font-size: 12px;
    color: #92400e;
    margin-top: 4px;
}

/* ── Speaking Sub-step ─────────────────────────────── */
.ipu-substep-speaking {
    border: 2px solid;
    background: #faf5ff;
}
.ipu-substep-speaking .ipu-substep-header {
    border-bottom-color: #e9d5ff;
}

/* ── Score All Button ──────────────────────────────── */
.ipu-score-all-btn {
    display: block;
    width: 100%;
    padding: 12px;
    font-size: 15px;
    font-weight: 600;
    border: none;
    border-radius: 8px;
    color: white;
    cursor: pointer;
    margin: 16px 0;
    transition: opacity 0.2s;
}
.ipu-score-all-btn:hover { opacity: 0.9; }
.ipu-score-all-btn:disabled { opacity: 0.5; cursor: not-allowed; }
</style>
"""


# ============================================================
# Web Speech API JavaScript (injected per phase)
# ============================================================

def _speech_js(phase_num):
    """Return JS for Web Speech API recording tied to a specific phase."""
    return f"""
<script>
(function() {{
    var phaseNum = {phase_num};
    var btnId = 'ipu-rec-btn-' + phaseNum;
    var statusId = 'ipu-rec-status-' + phaseNum;
    var recognition = null;
    var isRecording = false;
    var finalTranscript = '';

    var btn = document.getElementById(btnId);
    var status = document.getElementById(statusId);
    if (!btn) return;

    // Check browser support
    var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {{
        btn.textContent = 'Speech not supported in this browser';
        btn.disabled = true;
        btn.style.opacity = '0.5';
        return;
    }}

    btn.addEventListener('click', function() {{
        if (isRecording) {{
            // Stop
            recognition.stop();
            return;
        }}

        // Start
        recognition = new SpeechRecognition();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = 'en-US';
        finalTranscript = '';

        recognition.onstart = function() {{
            isRecording = true;
            btn.classList.add('recording');
            btn.innerHTML = '<span class="ipu-record-dot"></span> Stop Recording';
            status.textContent = 'Listening... speak your response';
        }};

        recognition.onresult = function(event) {{
            var interim = '';
            for (var i = event.resultIndex; i < event.results.length; i++) {{
                if (event.results[i].isFinal) {{
                    finalTranscript += event.results[i][0].transcript + ' ';
                }} else {{
                    interim += event.results[i][0].transcript;
                }}
            }}
            status.textContent = finalTranscript + interim;

            // Push transcript into the ipywidgets Textarea
            // Find the textarea in the phase widget
            var phaseContainer = btn.closest('.ipu-phase') || btn.parentElement.parentElement.parentElement;
            var textareas = phaseContainer.querySelectorAll('textarea');
            if (textareas.length > 0) {{
                var ta = textareas[0];
                ta.value = finalTranscript + interim;
                // Trigger input event so ipywidgets picks up the change
                ta.dispatchEvent(new Event('input', {{ bubbles: true }}));
            }}
        }};

        recognition.onerror = function(event) {{
            status.textContent = 'Error: ' + event.error + '. Try again.';
            isRecording = false;
            btn.classList.remove('recording');
            btn.innerHTML = '<span class="ipu-record-dot"></span> Record Response';
        }};

        recognition.onend = function() {{
            isRecording = false;
            btn.classList.remove('recording');
            btn.innerHTML = '<span class="ipu-record-dot"></span> Record Response';
            if (finalTranscript.trim()) {{
                status.textContent = 'Recording complete — ' + finalTranscript.trim().split(' ').length + ' words captured';
            }} else {{
                status.textContent = 'No speech detected. Try again.';
            }}
        }};

        recognition.start();
    }});
}})();
</script>
"""


# ============================================================
# Inject CSS
# ============================================================

def inject_styles():
    """Inject the global CSS into the notebook. Call once at startup."""
    display(HTML(NOTEBOOK_CSS))


# ============================================================
# Header
# ============================================================

def render_header():
    """Render the app header banner."""
    display(HTML("""
    <div class="ipu-app">
      <div class="ipu-header">
        <h1>Product Analytics Interview Practice</h1>
        <p>Walk through the 5-phase lifecycle — Discovery, Validation, Build, Rollout, Scale —
        with Claude-powered coaching. Write or speak your response at each phase, then get
        rubric-based feedback grounded in the framework playbook.</p>
      </div>
    </div>
    """))


# ============================================================
# Scenario Display
# ============================================================

def format_scenario_html(scenario):
    """Return styled HTML for the scenario card."""
    scope_label = "New Product" if scenario["scope"] == "product" else "Feature on Existing Product"
    product_desc = scenario.get('product_description', '')
    problem = scenario.get('problem', '')
    customer_profile = scenario.get('customer_profile', '')

    # Capitalize first letter of product description (comes after "is")
    if product_desc:
        product_desc = product_desc[0].upper() + product_desc[1:]

    return f"""
    <div class="ipu-scenario">
      <h3>Case Study Scenario</h3>
      <div class="ipu-scenario-row">
        <span class="ipu-scenario-label">Company</span>
        <span class="ipu-scenario-value"><strong>{scenario['company_name']}</strong> — {scenario['archetype_type']}</span>
      </div>
      <div class="ipu-scenario-row">
        <span class="ipu-scenario-label">The Product</span>
        <span class="ipu-scenario-value">{product_desc}</span>
      </div>
      <div class="ipu-scenario-row">
        <span class="ipu-scenario-label">The Problem</span>
        <span class="ipu-scenario-value">{problem}</span>
      </div>
      <div class="ipu-scenario-row">
        <span class="ipu-scenario-label">Target Customers</span>
        <span class="ipu-scenario-value">{customer_profile}</span>
      </div>
      <div class="ipu-scenario-row">
        <span class="ipu-scenario-label">Situation</span>
        <span class="ipu-scenario-value">{scenario['situation_label']}: {scenario.get('situation_description', '') or ''}</span>
      </div>
      <div class="ipu-scenario-row">
        <span class="ipu-scenario-label">Primary Users</span>
        <span class="ipu-scenario-value">{scenario['user_type'].title()}</span>
      </div>
      <div class="ipu-scenario-row">
        <span class="ipu-scenario-label">Constraint</span>
        <span class="ipu-scenario-constraint">{scenario['constraint']}</span>
      </div>
      <div class="ipu-scenario-meta">
        Scope: {scope_label} |
        Emphasis phases: {', '.join(p.title() for p in scenario['emphasis_phases'])} |
        Domain metrics: {scenario['archetype_metrics']}
      </div>
    </div>"""


# ============================================================
# Score Display
# ============================================================

def format_score_html(phase, score_result):
    """Return styled HTML for score feedback."""
    composite = score_result.get("composite", 0)

    if composite >= 4.0:
        color, bg, label, badge_cls = "#166534", "#dcfce7", "Strong", "ipu-badge-strong"
    elif composite >= 3.0:
        color, bg, label, badge_cls = "#854d0e", "#fef9c3", "Developing", "ipu-badge-developing"
    else:
        color, bg, label, badge_cls = "#991b1b", "#fee2e2", "Needs Work", "ipu-badge-needs-work"

    # Dimension bars
    bars_html = ""
    for dim, val in score_result.get("scores", {}).items():
        pct = val / 5 * 100
        dim_label = dim.replace("_", " ").title()
        bars_html += f"""
        <div class="ipu-score-bar-row">
          <span class="ipu-score-bar-label">{dim_label}</span>
          <div class="ipu-score-bar-track">
            <div class="ipu-score-bar-fill" style="width:{pct}%; background:{color};"></div>
          </div>
          <span class="ipu-score-bar-value">{val}/5</span>
        </div>"""

    # Missed elements
    missed = score_result.get("missed_elements", [])
    missed_html = ""
    if missed:
        items = "".join(f"<li>{m}</li>" for m in missed)
        missed_html = f"""
        <div class="ipu-score-missed">
          <strong>Framework elements to revisit</strong>
          <ul>{items}</ul>
        </div>"""

    return f"""
    <div class="ipu-score" style="background:{bg}; border-left: 4px solid {color};">
      <div class="ipu-score-header">
        <div>
          <div class="ipu-score-label" style="color:{color};">Phase {phase['phase_num']}: {phase['phase_name']}</div>
        </div>
        <div style="text-align:right;">
          <div class="ipu-score-composite" style="color:{color};">{composite}/5</div>
          <span class="ipu-badge {badge_cls}">{label}</span>
        </div>
      </div>
      {bars_html}
      <div class="ipu-score-feedback">
        <strong style="color:{color};">Feedback</strong>
        {_inline_md(score_result.get('feedback', ''))}
      </div>
      <div class="ipu-score-grid">
        <div class="ipu-score-feedback">
          <strong style="color:#166534;">Strength</strong>
          {_inline_md(score_result.get('strength', ''))}
        </div>
        <div class="ipu-score-feedback">
          <strong style="color:#991b1b;">Improve</strong>
          {_inline_md(score_result.get('improvement', ''))}
        </div>
      </div>
      {missed_html}
      <div class="ipu-score-latency">Scored in {score_result.get('latency', 0)}s</div>
    </div>"""


# ============================================================
# Session Summary
# ============================================================

def format_session_summary_html(phase_scores):
    """Return styled HTML for the session summary table."""
    if not phase_scores:
        return "<p>No scores recorded yet.</p>"

    total = sum(s["composite"] for s in phase_scores) / len(phase_scores)
    phase_colors = {1: "#2E86AB", 2: "#F18F01", 3: "#6c63ff", 4: "#2CA58D", 5: "#E15554"}

    rows = ""
    for s in phase_scores:
        comp = s["composite"]
        if comp >= 4.0:
            badge_cls, badge_text = "ipu-badge-strong", "Strong"
        elif comp >= 3.0:
            badge_cls, badge_text = "ipu-badge-developing", "Developing"
        else:
            badge_cls, badge_text = "ipu-badge-needs-work", "Needs Work"
        pc = phase_colors.get(s["phase_num"], "#333")
        rows += f"""<tr>
            <td style="border-left:3px solid {pc}; padding-left:12px;"><strong>Phase {s['phase_num']}</strong></td>
            <td>{s['phase_name']}</td>
            <td style="font-weight:600;">{comp}/5</td>
            <td><span class="ipu-badge {badge_cls}">{badge_text}</span></td>
        </tr>"""

    return f"""
    <div class="ipu-summary">
      <h3>Session Summary — Overall: {round(total, 1)}/5</h3>
      <table>
        <thead><tr><th></th><th>Phase</th><th>Score</th><th>Level</th></tr></thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


# ============================================================
# Phase Widget Builder
# ============================================================

def _build_guide_html(phase_id, ipu_module):
    """Build collapsible guide HTML for a phase."""
    guide = getattr(ipu_module, 'PHASE_GUIDES', {}).get(phase_id)
    if not guide:
        return ""

    questions_li = "".join(f"<li>{q}</li>" for q in guide["key_questions"])
    remember_li = "".join(f"<li>{r}</li>" for r in guide["remember"])

    return f"""
    <div class="ipu-guide" id="ipu-guide-{phase_id}">
        <button class="ipu-guide-toggle" onclick="this.parentElement.classList.toggle('open')">
            <span class="ipu-guide-arrow">&#9654;</span> {guide['title']}
        </button>
        <div class="ipu-guide-body">
            <p style="margin:0 0 8px 0; color:#475569;">{guide['what_this_is']}</p>
            <h4>Key questions to answer</h4>
            <ul>{questions_li}</ul>
            <h4>Things to remember</h4>
            <ul>{remember_li}</ul>
        </div>
    </div>"""


def _build_script_html(phase_id, ipu_module):
    """Build collapsible speaking outline HTML for a phase."""
    script = getattr(ipu_module, 'PHASE_SCRIPTS', {}).get(phase_id)
    if not script:
        return ""

    sections_html = ""
    for sec in script["sections"]:
        label_class = f"ipu-script-label-{sec['label_type']}"

        bullets_html = ""
        for kw, text in sec["bullets"]:
            bullets_html += f"""<div class="ipu-script-bullet">
                <span class="ipu-script-bullet-arrow">&rarr;</span>
                <span><span class="ipu-script-bullet-kw">{kw}:</span> {text}</span>
            </div>"""

        quote_html = ""
        if sec.get("how_to_say_it"):
            quote_html = f"""<div class="ipu-script-quote">
                <div class="ipu-script-quote-label">How to say it</div>
                {sec['how_to_say_it']}
            </div>"""

        sections_html += f"""
        <div class="ipu-script-section" id="ipu-ss-{phase_id}-{sec['label'].lower().replace(' ', '')}">
            <div class="ipu-script-section-header" onclick="this.parentElement.classList.toggle('open')">
                <span class="ipu-script-label {label_class}">{sec['label']}</span>
                <span class="ipu-script-section-title">{sec['title']}</span>
                <span class="ipu-script-section-arrow">&#9654;</span>
            </div>
            <div class="ipu-script-section-body">
                {bullets_html}
                {quote_html}
            </div>
        </div>"""

    return f"""
    <div class="ipu-script" id="ipu-script-{phase_id}">
        <button class="ipu-script-toggle" onclick="this.parentElement.classList.toggle('open')">
            <span class="ipu-script-arrow">&#9654;</span> {script['title']}
        </button>
        <div class="ipu-script-body">
            <p style="margin:0 0 8px 0; color:#6b21a8; font-size:12px;">Click any section to expand the talking points and suggested phrasing. Use these to practice speaking out loud.</p>
            {sections_html}
        </div>
    </div>"""


def make_phase_widget(phase, state, session_id, ipu_module):
    """
    Build the full interactive widget for a single phase.

    Parameters
    ----------
    phase : dict — phase definition from ipu.PHASES
    state : dict — shared state with 'scenario' and 'phase_results' keys
    session_id : str — current session ID
    ipu_module : module — the interview_practice_utils module (for scoring functions)
    """
    import time as _time

    phase_num = phase["phase_num"]
    phase_id = phase["phase_id"]

    # ── Guide + Script static HTML ──
    guide_html_widget = widgets.HTML(_build_guide_html(phase_id, ipu_module))
    script_html_widget = widgets.HTML(_build_script_html(phase_id, ipu_module))

    # ── Text input ──
    text_input = widgets.Textarea(
        placeholder="Type your response here — or click Record to speak it. Be specific: name metrics, methods, data sources.",
        layout=widgets.Layout(width="100%", height="200px"),
    )

    # ── Buttons ──
    submit_btn = widgets.Button(
        description="Submit and Score",
        button_style="success",
        layout=widgets.Layout(width="160px", height="34px"),
    )
    hint_btn = widgets.Button(
        description="Get a Hint",
        button_style="warning",
        layout=widgets.Layout(width="130px", height="34px"),
    )
    example_btn = widgets.Button(
        description="Show Example",
        button_style="",
        layout=widgets.Layout(width="140px", height="34px"),
    )

    feedback_output = widgets.Output()
    hint_output = widgets.Output()

    # ── Record button (HTML + JS) ──
    record_html = widgets.HTML(f"""
    <div style="margin-top:8px;">
        <button class="ipu-record-btn" id="ipu-rec-btn-{phase_num}">
            <span class="ipu-record-dot"></span> Record Response
        </button>
        <div class="ipu-record-status" id="ipu-rec-status-{phase_num}">
            Click to start recording with your microphone (Chrome/Edge)
        </div>
    </div>
    """)
    # JS will be injected after the widget renders
    speech_js_html = widgets.HTML(_speech_js(phase_num))

    # ── Handlers ──
    def on_submit(b):
        response = text_input.value.strip()
        if not response:
            with feedback_output:
                clear_output(wait=True)
                display(HTML('<div style="color:#dc2626; padding:8px;">Write or record a response first.</div>'))
            return

        scenario = state.get("scenario")
        if not scenario:
            with feedback_output:
                clear_output(wait=True)
                display(HTML('<div style="color:#dc2626; padding:8px;">Generate a scenario first.</div>'))
            return

        submit_btn.disabled = True
        submit_btn.description = "Scoring..."

        t0 = _time.time()
        result = ipu_module.score_response(scenario, phase, response)
        elapsed = round(_time.time() - t0, 1)

        ipu_module.log_phase_result(session_id, scenario, phase, response, result, time_spent_sec=elapsed)

        state["phase_results"][phase_num] = {
            "phase_num": phase_num,
            "phase_name": phase["phase_name"],
            "composite": result.get("composite", 0),
            "scores": result.get("scores", {}),
        }

        with feedback_output:
            clear_output(wait=True)
            display(HTML(format_score_html(phase, result)))

        submit_btn.disabled = False
        submit_btn.description = "Re-Submit and Score"

    def on_hint(b):
        scenario = state.get("scenario")
        if not scenario:
            with hint_output:
                clear_output(wait=True)
                display(HTML('<div style="color:#dc2626; padding:8px;">Generate a scenario first.</div>'))
            return

        hint_btn.disabled = True
        hint_btn.description = "Thinking..."

        hint_text = ipu_module.get_hint(scenario, phase)

        with hint_output:
            clear_output(wait=True)
            hint_html = _md_to_html(hint_text)
            display(HTML(f'<div class="ipu-hint"><strong>Hint</strong><div class="ipu-text-body">{hint_html}</div></div>'))

        hint_btn.disabled = False
        hint_btn.description = "Get a Hint"

    def on_example(b):
        scenario = state.get("scenario")
        if not scenario:
            with hint_output:
                clear_output(wait=True)
                display(HTML('<div style="color:#dc2626; padding:8px;">Generate a scenario first.</div>'))
            return

        example_btn.disabled = True
        example_btn.description = "Generating..."

        example_text = ipu_module.get_example(scenario, phase)

        with hint_output:
            clear_output(wait=True)
            example_html = _md_to_html(example_text)
            display(HTML(f'<div class="ipu-example"><strong>Example Strong Response</strong><div class="ipu-text-body">{example_html}</div></div>'))

        example_btn.disabled = False
        example_btn.description = "Show Example"

    submit_btn.on_click(on_submit)
    hint_btn.on_click(on_hint)
    example_btn.on_click(on_example)

    # ── Phase header HTML ──
    phase_header_html = f"""
    <div class="ipu-phase ipu-phase-{phase_id}">
      <div class="ipu-phase-header">
        <div class="ipu-phase-num">{phase_num}</div>
        <div class="ipu-phase-title">{phase['phase_name']}</div>
      </div>
      <div class="ipu-phase-instruction">{phase['instruction']}</div>
    </div>
    """

    header_widget = widgets.HTML(phase_header_html)
    button_row = widgets.HBox([submit_btn, hint_btn, example_btn], layout=widgets.Layout(gap="8px"))

    return widgets.VBox([
        header_widget,
        guide_html_widget,
        script_html_widget,
        text_input,
        record_html,
        speech_js_html,
        button_row,
        feedback_output,
        hint_output,
    ], layout=widgets.Layout(margin="0 0 20px 0"))


def make_decomposed_phase_widget(phase_id, state, session_id, ipu_module):
    """
    Build a decomposed phase widget with individual sub-step input fields,
    per-step Check buttons, and a Score All button.
    """
    import time as _time

    substeps_data = getattr(ipu_module, 'PHASE_SUBSTEPS', {}).get(phase_id)
    if not substeps_data:
        return widgets.HTML(f'<p>No sub-steps defined for {phase_id}</p>')

    phase_color = substeps_data["phase_color"]
    phase_bg = substeps_data["phase_bg"]
    phase_title = substeps_data["phase_title"]

    # ── Phase separator header ──
    separator_html = widgets.HTML(f"""
    <div class="ipu-phase-separator" style="background:{phase_bg}; border-left-color:{phase_color};">
        <h2 style="color:{phase_color};">{phase_title}</h2>
        <p>Complete each section below. Use Check to get feedback on individual sections, or Score All to evaluate the full phase.</p>
    </div>
    """)

    # ── Build sub-step widgets ──
    substep_widgets = []
    text_inputs = {}  # id -> textarea widget
    feedback_outputs = {}  # id -> output widget

    for step in substeps_data["steps"]:
        step_id = step["id"]
        is_speaking = step.get("is_speaking", False)

        # Textarea
        height = "250px" if is_speaking else "120px"
        placeholder = "Record or type your full conversation here..." if is_speaking else "Type your response..."
        ta = widgets.Textarea(
            placeholder=placeholder,
            layout=widgets.Layout(width="100%", height=height),
        )
        text_inputs[step_id] = ta

        # Feedback output
        fb_out = widgets.Output()
        feedback_outputs[step_id] = fb_out

        # Check button
        check_btn = widgets.Button(
            description="Check",
            button_style="info",
            layout=widgets.Layout(width="80px", height="30px"),
        )

        def make_check_handler(sid, step_def, textarea, fb_output, btn):
            def on_check(b):
                response = textarea.value.strip()
                if not response:
                    with fb_output:
                        clear_output(wait=True)
                        display(HTML('<div style="color:#dc2626; font-size:13px; padding:4px;">Write something first.</div>'))
                    return
                scenario = state.get("scenario")
                if not scenario:
                    with fb_output:
                        clear_output(wait=True)
                        display(HTML('<div style="color:#dc2626; font-size:13px; padding:4px;">Generate a scenario first.</div>'))
                    return

                btn.disabled = True
                btn.description = "..."
                result = ipu_module.score_substep(scenario, phase_id, step_def, response)
                btn.disabled = False
                btn.description = "Check"

                if result:
                    score = result.get("score", 0)
                    if score >= 4:
                        sc_color, sc_bg = "#166534", "#dcfce7"
                    elif score >= 3:
                        sc_color, sc_bg = "#854d0e", "#fef9c3"
                    else:
                        sc_color, sc_bg = "#991b1b", "#fee2e2"

                    missing_html = ""
                    missing = result.get("missing", [])
                    if missing:
                        items = ", ".join(missing)
                        missing_html = f'<div class="ipu-substep-missing">Missing: {items}</div>'

                    with fb_output:
                        clear_output(wait=True)
                        display(HTML(f"""<div class="ipu-substep-feedback">
                            <span class="ipu-substep-score-badge" style="background:{sc_bg}; color:{sc_color};">{score}/5</span>
                            <div class="ipu-substep-feedback-text">{result.get('feedback', '')}</div>
                            {missing_html}
                        </div>"""))
            return on_check

        check_btn.on_click(make_check_handler(step_id, step, ta, fb_out, check_btn))

        # Speaking section gets record button too
        extra_widgets = []
        if is_speaking:
            # Find the phase_num for speech JS
            phase_nums = {"discovery": 1, "validation": 2, "build": 3, "rollout": 4, "scale": 5}
            pnum = phase_nums.get(phase_id, 0)
            rec_html = widgets.HTML(f"""
            <div style="margin-top:4px;">
                <button class="ipu-record-btn" id="ipu-rec-btn-{pnum}0">
                    <span class="ipu-record-dot"></span> Record
                </button>
                <span class="ipu-record-status" id="ipu-rec-status-{pnum}0" style="font-size:11px; color:#888;"></span>
            </div>
            """)
            speech_js = widgets.HTML(_speech_js(f"{pnum}0"))
            extra_widgets = [rec_html, speech_js]

        # Build the card HTML with collapsible hint
        speaking_class = " ipu-substep-speaking" if is_speaking else ""
        hint_id = f"hint-{phase_id}-{step['id']}"
        card_header = widgets.HTML(f"""
        <div class="ipu-substep{speaking_class}">
            <div class="ipu-substep-header">
                <div class="ipu-substep-icon" style="background:{phase_color};">{step['icon']}</div>
                <div class="ipu-substep-title">{step['title']}</div>
            </div>
            <div class="ipu-substep-body">
                <div class="ipu-substep-instruction">{step['instruction']}</div>
                <div class="ipu-substep-hint-toggle" onclick="var b=document.getElementById('{hint_id}'); var a=this.querySelector('.hint-arrow'); if(b.style.display==='none'){{b.style.display='block'; a.textContent='▼';}} else {{b.style.display='none'; a.textContent='▶';}}" style="cursor:pointer; color:#6c63ff; font-size:12px; font-weight:600; padding:4px 0; user-select:none;">
                    <span class="hint-arrow" style="font-size:10px; margin-right:4px;">▶</span> Show Hint
                </div>
                <div id="{hint_id}" class="ipu-substep-hint" style="display:none;">{step['hint']}</div>
            </div>
        </div>
        """)

        # We need to nest the textarea inside the card visually.
        # Since ipywidgets can't inject inside HTML, we'll use a VBox approach
        # with the card header, then the textarea below it with matching styling
        btn_row = widgets.HBox([check_btn], layout=widgets.Layout(justify_content="flex-end", margin="4px 0 0 0"))

        step_container = widgets.VBox(
            [card_header] + extra_widgets + [ta, btn_row, fb_out],
            layout=widgets.Layout(
                margin="12px 0",
                padding="0",
            )
        )
        substep_widgets.append(step_container)

    # ── Score All button ──
    score_all_output = widgets.Output()
    score_all_btn = widgets.Button(
        description=f"Score All {phase_title.split(':')[0].strip()}",
        button_style="success",
        layout=widgets.Layout(width="100%", height="44px"),
    )

    def on_score_all(b):
        scenario = state.get("scenario")
        if not scenario:
            with score_all_output:
                clear_output(wait=True)
                display(HTML('<div style="color:#dc2626; padding:8px;">Generate a scenario first.</div>'))
            return

        # Collect all non-empty responses
        all_responses = []
        for step in substeps_data["steps"]:
            val = text_inputs[step["id"]].value.strip()
            if val:
                all_responses.append(f"[{step['title']}]\n{val}")

        if not all_responses:
            with score_all_output:
                clear_output(wait=True)
                display(HTML('<div style="color:#dc2626; padding:8px;">Fill in at least one section first.</div>'))
            return

        combined = "\n\n".join(all_responses)

        # Find the matching PHASES entry for full scoring
        phase_def = None
        for p in ipu_module.PHASES:
            if p["phase_id"] == phase_id:
                phase_def = p
                break

        if not phase_def:
            return

        score_all_btn.disabled = True
        score_all_btn.description = "Scoring..."

        t0 = _time.time()
        result = ipu_module.score_response(scenario, phase_def, combined)
        elapsed = round(_time.time() - t0, 1)

        ipu_module.log_phase_result(session_id, scenario, phase_def, combined, result, time_spent_sec=elapsed)

        state["phase_results"][phase_def["phase_num"]] = {
            "phase_num": phase_def["phase_num"],
            "phase_name": phase_def["phase_name"],
            "composite": result.get("composite", 0),
            "scores": result.get("scores", {}),
        }

        with score_all_output:
            clear_output(wait=True)
            display(HTML(format_score_html(phase_def, result)))

        score_all_btn.disabled = False
        score_all_btn.description = f"Re-Score All {phase_title.split(':')[0].strip()}"

    score_all_btn.on_click(on_score_all)

    # ── Guide + Script (reuse existing) ──
    guide_widget = widgets.HTML(_build_guide_html(phase_id, ipu_module))
    script_widget = widgets.HTML(_build_script_html(phase_id, ipu_module))

    return widgets.VBox(
        [separator_html, guide_widget, script_widget] + substep_widgets + [score_all_btn, score_all_output],
        layout=widgets.Layout(margin="0 0 40px 0"),
    )
