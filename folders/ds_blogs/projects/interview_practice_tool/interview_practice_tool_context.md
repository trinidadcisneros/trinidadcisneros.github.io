# Interview Practice Tool — Project Context

## Purpose
Claude-powered interactive interview practice tool aligned to the 5-phase Product Analytics Lifecycle (Discovery, Validation, Build, Rollout, Scale). Each phase embeds framework-specific guardrails so coaching feedback stays grounded in the playbook content.

## Interview Date
April 9, 2026, 11:00am-12:00pm PDT (SmarterDx Senior Product Analyst case study)

## Project Structure

```
interview_practice_tool/
├── interview_practice_tool_context.md   <- this file
├── data/
│   └── outputs/
│       ├── nb01/               <- Interview practice session logs (CSV)
│       └── nb09/               <- LLM coaching data story outputs
└── notebooks/
    ├── interview_practice_utils.py  <- Core logic: Claude API, scenarios, phases, scoring
    ├── ui_components.py             <- All UI: CSS, widgets, speech API, HTML formatters
    ├── nb01_interview_practice.ipynb <- Interactive practice tool (8 cells)
    └── nb09_llm_coaching_analysis.ipynb <- Data story: scoring analysis (unchanged)
```

## Notebook Pipeline

| Notebook | Purpose |
|----------|---------|
| NB01 | Interactive 5-phase interview practice with Claude-scored feedback, hints, example responses, and voice recording |
| NB09 | Data story: scoring analysis from practice sessions |

## How It Works

1. Generate a random case study scenario (6 archetypes x 8 situations x 10 constraints = 480 combinations)
2. Walk through 5 phases aligned to the Product Analytics Framework Playbook
3. Each phase provides:
   - Phase instruction with color-coded banner
   - Text input for your response
   - Record Response: browser-based voice-to-text via Web Speech API (free, no API cost)
   - Submit and Score: rubric-based scoring with per-dimension bars, feedback, strength, improvement, missed elements
   - Get a Hint: coaching nudge without giving the answer
   - Show Example: full example strong response for the current scenario
4. Session data logged to CSV for progress tracking

## Key Files

### interview_practice_utils.py
Core logic file. Claude-only, 5-phase design.

Key components:
- `init_claude()` — initialize Anthropic client
- `_call_claude(system_prompt, user_prompt, max_tokens)` — single Claude API wrapper (claude-sonnet-4-20250514)
- `generate_scenario()` — random scenario from 480 combinations; SmarterDx mode biases toward Healthcare AI
- `PHASES` — list of 5 phase definitions, each containing:
  - phase_num, phase_id, phase_name, instruction
  - framework_context (2000-3000 characters of playbook content as guardrails)
  - rubric (dictionary of dimension: description for scoring)
  - strong_traits, common_mistakes
- `COACH_SYSTEM_PROMPT` — master system prompt with formatting rules
- `_build_phase_prompt()` — builds prompts for 3 modes: score, hint, example
- `score_response()`, `get_hint()`, `get_example()` — user-facing functions
- `log_phase_result()`, `save_session_log()` — CSV session logging
- `format_scenario_html()`, `format_phase_instruction_html()`, `format_score_html()`, `format_session_summary_html()` — HTML formatters

Phase rubric dimensions:
- Discovery: data_sources, sizing_method, go_no_go_signals, feasibility, context_awareness
- Validation: north_star_clarity, metrics_tree, baselines, kill_criteria, guardrails
- Build: event_taxonomy, dashboard_design, data_quality, practical_constraints
- Rollout: methodology_fit, sample_size_awareness, success_criteria, kill_criteria, rollout_phases, guardrails
- Scale: retention_framework, pmf_signals, cohort_strategy, kill_pivot_criteria, expansion_plan

### ui_components.py
All UI code, separated from the main notebook for cleanliness.

Key components:
- `_md_to_html()` — full markdown-to-HTML converter (bold, italic, bullets, numbered lists, headings, paragraphs, HTML escaping)
- `_inline_md()` — single-line markdown converter
- `NOTEBOOK_CSS` — custom CSS (~8100 characters) with `.ipu-*` class prefix
- `_speech_js(phase_num)` — generates Web Speech API JavaScript per phase (continuous recognition, interim results, pushes transcript into ipywidgets Textarea)
- `inject_styles()` — injects CSS into notebook
- `render_header()` — renders the app header
- `make_phase_widget()` — builds complete phase UI: header, textarea, record button, submit/hint/example buttons, feedback/hint/example output panels

CSS class naming: `.ipu-*` prefix (ipu-app, ipu-header, ipu-section, ipu-scenario, ipu-phase, ipu-phase-discovery/validation/build/rollout/scale, ipu-score, ipu-hint, ipu-example, ipu-record-btn, ipu-summary, ipu-badge)

Phase colors: Discovery=#2E86AB (blue), Validation=#F18F01 (orange), Build=#6c63ff (purple), Rollout=#2CA58D (green), Scale=#E15554 (red)

### nb01_interview_practice.ipynb
Streamlined 8-cell notebook:
1. Markdown title
2. Imports + CSS injection + header render
3. Claude init + session ID display
4. Scenario generator (scope + mode radio buttons)
5. Five-phase walkthrough loop
6. Session summary + radar chart
7. Save session to CSV
8. Markdown reference table

## Key Design Decisions

- **Claude-only** (simplified from multi-model): single model for reliable, consistent coaching
- **5 phases not 7 steps**: aligned directly to playbook tabs (Discovery, Validation, Build, Rollout, Scale)
- **Embedded framework context**: each phase includes 2000-3000 characters of playbook content as guardrails in the system prompt, so Claude's feedback references specific deliverables, metrics, and methods from the framework
- **Three interaction modes**: score (primary), hint (stuck), example (learning)
- **Voice recording via Web Speech API**: free, browser-built-in (Chrome/Edge only), no Claude API cost
- **Markdown rendering**: belt-and-suspenders approach — system prompt instructs Claude to respond in plain prose (no markdown), plus `_md_to_html()` converter handles any markdown that comes back anyway
- **SmarterDx mode**: biases scenario generation toward Healthcare AI archetypes
- **UI separation**: all widget/CSS/JS code in ui_components.py keeps nb01 clean and focused

## Editorial Rules

- No "we/our" — use third person or second person sparingly
- No hyphens unless grammatically required compound nouns
- No acronyms — spell out everything
- LLM prompts instruct Claude to respond in plain prose, no markdown formatting
- Framework sections should be domain-agnostic

## Dependencies
pandas, numpy, matplotlib, ipywidgets, anthropic

## Related Project
The playbook content is sourced from `playbooks/playbook_product_analytics_framework.html`. The case study HTML is at `ds_blogs/projects/product_analytics_interview_prep/product_analytics_case_study.html`.
