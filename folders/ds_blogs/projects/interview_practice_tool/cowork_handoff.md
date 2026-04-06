# Cowork Handoff — Interview Preparation

**Context:** I'm preparing for a Senior Product Analyst case study interview at SmarterDx on April 9, 2026 (11:00am-12:00pm PDT). I've built an interview preparation ecosystem and need continued help with product analytics across a product's lifecycle. Here's everything you need to know:

**Interview Date:** April 9, 2026, 11:00am-12:00pm PDT, SmarterDx, Senior Product Analyst

**Project Location:** My selected folder is `bitterscientist.com` — all project files are under `/folders/` within it.

## What Exists

1. **Product Analytics Framework Playbook** at `/folders/playbooks/playbook_product_analytics_framework.html`
   - Tabbed HTML page covering the 5-phase product analytics lifecycle: Discovery, Validation, Build, Rollout, Scale
   - Additional tabs: Interview Playbook, Interactive Walkthrough, Flashcards and Quiz, Citations and Resources
   - Uses Bootstrap 3.4.0 with jQuery, custom interactive card patterns (click-to-expand/collapse)
   - CSS card classes: `.deliv-card` (deliverables), `.km-card` (key metrics), `.am-card` (analysis methods), `.to-card` (trade-offs), `.covers-card` (overview)
   - 25 analysis method cards with formulas where math is simple
   - Color scheme: #2E86AB (blue), #F18F01 (orange), #2CA58D (green), #E15554 (red), #6c63ff (purple), #1a1a2e (dark)

2. **Interview Practice Tool** at `/folders/ds_blogs/projects/interview_practice_tool/notebooks/`
   - `nb01_interview_practice.ipynb` — streamlined 8-cell Jupyter notebook for practicing the 5 phases with Claude-powered coaching
   - `interview_practice_utils.py` — core logic: Claude API calls (claude-sonnet-4-20250514), scenario generation (480 combinations from 6 archetypes x 8 situations x 10 constraints), phase definitions with embedded framework guardrails, scoring rubrics, session logging
   - `ui_components.py` — all UI: custom CSS injection, Web Speech API for microphone recording (free, browser-built-in), markdown-to-HTML converter, widget builders, styled HTML formatters
   - Each phase has 4 interaction modes: Submit and Score, Get a Hint, Show Example, Record Response
   - Phase colors match the playbook: Discovery=blue, Validation=orange, Build=purple, Rollout=green, Scale=red
   - `interview_practice_tool_context.md` — full project documentation

3. **E-Commerce Case Study** at `/folders/ds_blogs/projects/product_analytics_interview_prep/product_analytics_case_study.html`
   - Applied case study demonstrating the framework with e-commerce data

4. **Blog Landing Page** at `/folders/ds_blogs/ds_blog_landing.html` — 51 posts, includes cards for the playbook and case study

## Editorial Rules (follow these strictly)

- No "we/our" — use third person or second person sparingly
- No hyphens unless grammatically required compound nouns
- No acronyms — spell out everything (PM becomes Product Manager, TAM becomes Total Addressable Market, NPS becomes Net Promoter Score, and so on)
- Framework sections should be domain-agnostic
- All collapsible sections start collapsed by default
- LLM prompts instruct Claude to respond in plain prose, no markdown formatting

## Key Framework Phases

- **Discovery:** Market sizing (top-down and bottom-up), customer segmentation, competitive landscape mapping. Trade-offs: go big versus go focused, move fast versus research first.
- **Validation:** North Star metric definition, metrics tree building, baseline measurements, kill/pivot thresholds. Trade-offs: early signals versus proven results, ambitious versus safe targets.
- **Build:** Event taxonomy design (Object-Action naming), dashboard design (operational/adoption/outcomes), data quality validation. Implementation-focused phase.
- **Rollout:** A/B testing, pre/post analysis, difference-in-differences, interrupted time series, funnel analysis, cohort analysis, sequential testing, multi-armed bandit. Adoption funnels, guardrail monitoring, expand/iterate/pause decisions. Trade-offs: certainty versus speed, catch-everything versus precision, wide versus gradual launch.
- **Scale:** Retention curve analysis, survival analysis, churn prediction, lifetime value (lifetime value greater than 3 times Customer Acquisition Cost), product-market fit assessment with scorecard, warning signs and kill signals. Trade-offs: retention versus acquisition, deepen versus broaden, continue versus shut down.

## What I Need Help With Going Forward

- Continued interview preparation for the SmarterDx case study
- Questions and requests about product analytics across a product's lifecycle
- Possible improvements to the playbook, practice tool, or case study
- Practice walking through scenarios and getting feedback
- Any additional preparation for the April 9 interview

Please read the `interview_practice_tool_context.md` file and the playbook HTML as needed to get full context on the framework content.
