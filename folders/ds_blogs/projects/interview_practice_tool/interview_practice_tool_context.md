# Interview Practice Tool — Project Context

## Purpose
Interactive LLM-scored interview practice tool and accompanying data story analyzing whether frontier LLMs can serve as reliable coaching evaluators. Originally developed alongside the product analytics interview prep project for the SmarterDx case study interview.

## Interview Date
April 9, 2026, 11:00am–12:00pm PDT (SmarterDx Senior Product Analyst case study)

## Project Structure

```
interview_practice_tool/
├── interview_practice_tool_context.md   ← this file
├── data/
│   └── outputs/
│       ├── nb08/               ← Interview practice session logs (CSV)
│       └── nb09/               ← LLM coaching data story outputs
└── notebooks/
    ├── interview_practice_utils.py          ← Shared utilities for NB08 & NB09
    ├── nb08_interview_practice.ipynb        ← Interactive LLM-scored practice tool
    └── nb09_llm_coaching_analysis.ipynb     ← Data story: "Can LLMs Be Reliable Coaches?"
```

## Notebook Pipeline

| Notebook | Purpose | Methods Covered |
|----------|---------|-----------------|
| NB08 | Interactive interview practice | LLM-scored case study walkthrough, multi-model scoring, session logging |
| NB09 | LLM coaching data story | Inter-rater reliability (Krippendorff's alpha, ICC), scoring bias analysis, learning curves |

## Dual-Purpose Design

**Outcome 1 — Interview Prep (NB08):** Interactive notebook generates random case-study scenarios (6 company archetypes x 8 product situations x 10 constraints = 480 combinations), walks through 7 framework steps with text input, and scores each response via Claude/GPT/Gemini with step-specific rubrics. Supports "General Tech" and "SmarterDx Prep" modes.

**Outcome 2 — Data Story (NB09):** "Can LLMs Be Reliable Coaches?" — Analyzes the scoring data from NB08 sessions to measure inter-model agreement (Krippendorff's alpha, ICC), detect systematic biases (verbosity reward, model severity), compare latency, and track learning curves. Blog narrative: Are frontier LLMs consistent enough to evaluate unstructured analytical reasoning?

## Shared Utilities (interview_practice_utils.py)
~500 lines containing: LLM client init (Claude/OpenAI/Gemini with graceful fallback), `_call_model()` returning (text, latency), scenario generation engine, 7 framework steps with per-dimension scoring rubrics, `score_response()` with multi-model consensus, session logging to CSV, HTML display formatters.

## Dependencies
pandas, numpy, scipy, matplotlib, seaborn, ipywidgets, anthropic, openai, google-genai

## Related Project
The product analytics methods notebooks (NB01-NB07) remain in `product_analytics_interview_prep/`. NB08 generates practice session data; NB09 analyzes it as a data story.

## Future Blog Post (TODO)
**"Can LLMs Be Reliable Coaches?"** — Data story analyzing inter-model agreement, scoring bias, and learning curves from NB08 practice sessions. Uses NB09 as the worked example.
