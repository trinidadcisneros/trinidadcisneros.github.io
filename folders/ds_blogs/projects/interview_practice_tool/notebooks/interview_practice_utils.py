"""
Interview Practice Utilities — Product Analytics Framework Coach.

Claude-powered interactive practice tool aligned to the 5-phase
Product Analytics Lifecycle: Discovery → Validation → Build → Rollout → Scale.

Each phase embeds framework-specific guardrails so Claude's coaching
stays grounded in the playbook content.
"""

import os, re, json, random, time, hashlib
from datetime import datetime
from pathlib import Path
import pandas as pd

# ============================================================
# LLM Setup (Claude only)
# ============================================================

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

_CLIENT = None
_MODEL = "claude-sonnet-4-20250514"


def init_claude():
    """Initialize the Claude client. Returns True if successful."""
    global _CLIENT
    if not CLAUDE_AVAILABLE:
        print("anthropic package not installed. Run: pip install anthropic")
        return False
    try:
        _CLIENT = anthropic.Anthropic()
        # Quick test
        _CLIENT.messages.create(
            model=_MODEL,
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
        print(f"Claude ready ({_MODEL})")
        return True
    except Exception as e:
        print(f"Claude init failed: {e}")
        _CLIENT = None
        return False


def _call_claude(system_prompt, user_prompt, max_tokens=1000):
    """Call Claude with system + user prompt. Returns (text, latency)."""
    if not _CLIENT:
        return None, 0.0
    t0 = time.time()
    try:
        msg = _CLIENT.messages.create(
            model=_MODEL,
            max_tokens=max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        return msg.content[0].text, round(time.time() - t0, 2)
    except Exception as e:
        print(f"  Claude error: {e}")
        return None, 0.0


# ============================================================
# Scenario Generation Engine
# ============================================================

COMPANY_ARCHETYPES = [
    {
        "type": "Healthcare AI",
        "examples": ["MedAssist AI", "ClinicalMind", "DiagnosIQ", "HealthLens AI", "CareSignal"],
        "domain_context": "Hospital systems, electronic health record integration, clinical workflows, regulatory compliance, physician adoption",
        "users": ["physicians", "clinical coders", "hospital administrators", "clinical documentation specialists", "nurses"],
        "metrics_flavor": "accuracy rates, chart review time saved, query response rates, denial rate reduction",
    },
    {
        "type": "B2B SaaS",
        "examples": ["DataForge", "SyncFlow", "PipelineHQ", "MetricStack", "CloudNest"],
        "domain_context": "Enterprise software, multi-seat contracts, onboarding complexity, integration with existing tools",
        "users": ["operations managers", "data teams", "IT administrators", "executives", "analysts"],
        "metrics_flavor": "seat utilization, feature adoption, time-to-value, net revenue retention, expansion revenue",
    },
    {
        "type": "Consumer Marketplace",
        "examples": ["SwapLocal", "SkillBridge", "TrustLoop", "GigNest", "FreshFind"],
        "domain_context": "Two-sided marketplace dynamics, supply and demand balance, trust and safety, geographic density",
        "users": ["buyers", "sellers", "freelancers", "hosts", "small business owners"],
        "metrics_flavor": "gross merchandise value, take rate, liquidity, repeat transaction rate, time-to-first-match",
    },
    {
        "type": "Fintech",
        "examples": ["LedgerAI", "CashPulse", "SpendSmart", "VaultLine", "PayNova"],
        "domain_context": "Regulatory requirements, fraud detection, financial data sensitivity, trust building",
        "users": ["consumers", "small business owners", "accountants", "financial advisors", "compliance officers"],
        "metrics_flavor": "transaction volume, fraud rate, approval rate, cost per acquisition, activation to first transaction",
    },
    {
        "type": "Developer Tools",
        "examples": ["CodeRadar", "DeployPilot", "SchemaSync", "TestForge", "APIBridge"],
        "domain_context": "Developer experience, API reliability, documentation quality, community adoption, open-source dynamics",
        "users": ["software engineers", "DevOps teams", "engineering managers", "technical architects"],
        "metrics_flavor": "API calls per user, p99 latency, docs-to-first-call time, SDK adoption, community contributions",
    },
    {
        "type": "EdTech",
        "examples": ["LearnLoop", "SkillForge", "ClassPilot", "TutorMind", "StudyArc"],
        "domain_context": "Learning outcomes measurement, engagement vs. completion tension, institutional vs. consumer sales",
        "users": ["students", "instructors", "school administrators", "corporate learning managers", "parents"],
        "metrics_flavor": "course completion rate, assessment scores, time-to-proficiency, instructor engagement, renewal rate",
    },
]

PRODUCT_SITUATIONS = [
    {
        "id": "new_product_launch",
        "label": "New Product Launch",
        "scope": "product",
        "description": "The company is launching an entirely new product targeting a segment it has not served before.",
        "emphasis_phases": ["discovery", "validation"],
    },
    {
        "id": "feature_expansion",
        "label": "Feature Expansion to Adjacent Market",
        "scope": "feature",
        "description": "An existing successful product is adding a major feature to serve an adjacent user segment.",
        "emphasis_phases": ["build", "rollout"],
    },
    {
        "id": "retention_crisis",
        "label": "Retention Crisis",
        "scope": "product",
        "description": "The product has strong acquisition but Week-4 retention has dropped 15 percentage points over two quarters.",
        "emphasis_phases": ["scale", "rollout"],
    },
    {
        "id": "ai_accuracy_complaints",
        "label": "AI Model Accuracy Complaints",
        "scope": "feature",
        "description": "Users report the AI suggestions are wrong too often. Net Promoter Score has dropped but usage remains stable.",
        "emphasis_phases": ["build", "scale"],
    },
    {
        "id": "onboarding_dropoff",
        "label": "Onboarding Drop-off",
        "scope": "feature",
        "description": "Sign-ups are healthy but only 30 percent of new users complete onboarding to reach the core value moment.",
        "emphasis_phases": ["rollout", "validation"],
    },
    {
        "id": "enterprise_self_serve_tension",
        "label": "Enterprise vs. Self-Serve Tension",
        "scope": "product",
        "description": "The product has both enterprise and self-serve tiers. Enterprise revenue is four times larger but self-serve has twenty times the users.",
        "emphasis_phases": ["scale", "discovery"],
    },
    {
        "id": "international_expansion",
        "label": "International Market Expansion",
        "scope": "product",
        "description": "The product is expanding from the United States to three new markets with different regulatory and cultural contexts.",
        "emphasis_phases": ["discovery", "rollout"],
    },
    {
        "id": "pricing_model_change",
        "label": "Pricing Model Redesign",
        "scope": "feature",
        "description": "The company wants to shift from per-seat to usage-based pricing. Current annual recurring revenue is twenty million dollars.",
        "emphasis_phases": ["validation", "rollout"],
    },
]

CONSTRAINT_TWISTS = [
    "Engineering capacity is limited — only three new events can be instrumented this quarter.",
    "The CEO wants results in six weeks, not the usual three-month roadmap.",
    "Users cannot be randomized for A/B testing due to regulatory constraints — quasi-experimental methods are required.",
    "The data warehouse has a 48-hour lag, so real-time dashboards are not feasible.",
    "Two executives disagree on the North Star metric — one wants revenue, the other wants engagement.",
    "The user base is small (fewer than 5,000 monthly actives), so statistical power is a real concern.",
    "The product serves both internal users (employees) and external users (customers) with very different needs.",
    "Historical data only goes back four months — there is no long-term baseline.",
    "A competitor just launched a similar feature, creating urgency to ship before the next quarter.",
    "The sales team is promising features to prospects that have not been validated with analytics.",
]


def generate_scenario(scope_filter=None, seed=None):
    """Generate a random case-study scenario."""
    rng = random.Random(seed)
    archetype = rng.choice(COMPANY_ARCHETYPES)
    situations = PRODUCT_SITUATIONS
    if scope_filter:
        situations = [s for s in situations if s["scope"] == scope_filter]
    situation = rng.choice(situations)
    constraint = rng.choice(CONSTRAINT_TWISTS)
    company_name = rng.choice(archetype["examples"])
    user_type = rng.choice(archetype["users"])

    full_prompt = (
        f"Company: {company_name} — a {archetype['type'].lower()} company.\n"
        f"Context: {archetype['domain_context']}.\n"
        f"Situation: {situation['description']} "
        f"The primary users affected are {user_type}.\n"
        f"Constraint: {constraint}"
    )

    scenario_id = hashlib.md5(full_prompt.encode()).hexdigest()[:8]

    return {
        "scenario_id": scenario_id,
        "company_name": company_name,
        "archetype_type": archetype["type"],
        "archetype_metrics": archetype["metrics_flavor"],
        "situation_id": situation["id"],
        "situation_label": situation["label"],
        "scope": situation["scope"],
        "emphasis_phases": situation["emphasis_phases"],
        "constraint": constraint,
        "user_type": user_type,
        "full_prompt": full_prompt,
    }


# ============================================================
# Phase Framework Content (embedded guardrails for Claude)
# ============================================================

PHASES = [
    {
        "phase_num": 1,
        "phase_id": "discovery",
        "phase_name": "Discovery — Size the Opportunity",
        "instruction": (
            "How would you approach discovery analytics for this scenario? "
            "Describe what data you would gather, how you would size the opportunity, "
            "and what signals would indicate this is worth pursuing."
        ),
        "framework_context": """DISCOVERY PHASE FRAMEWORK:

Deliverables an analyst produces in this phase:
1. Market Sizing and Total Addressable Opportunity — total addressable market estimate, revenue opportunity model, conversion gap analysis (if existing platform), external evidence synthesis, and confidence-level documentation.
2. Customer Segmentation — segment definitions with clear criteria, segment size distribution, prioritization matrix (need x readiness x revenue potential).
3. Competitive Landscape Mapping — competitor feature matrix, market share estimates, differentiation positioning, and internal usage pattern analysis.

Key Metrics:
- Total Addressable Market (maximum revenue opportunity if capturing 100% of target market)
- Segment Size Distribution (how many potential customers in each segment)
- Conversion Gap Analysis (difference between what users could do vs. actually do — existing platform only)
- Competitive Coverage (percentage of market already served by existing solutions)

Analysis Methods:
- Top Down Market Sizing: Total Market x Segment % x Realistic Capture % = Addressable Opportunity
- Bottom Up Market Sizing: Count actual target customers, multiply by realistic revenue per customer
- Competitive Landscape Analysis: Identify existing solutions, coverage, and whitespace
- Customer Interview Analysis: Code responses into themes, count frequency, identify segments with strongest pain
- Conversion Gap Analysis: (Eligible Users - Converted Users) / Eligible Users x 100 = Gap % (existing platform only)

Trade-offs to consider:
- Go big or go focused: Bigger market harder to serve; narrow easier to win but may lack scale
- Move fast or research first: Months of research risks competitor launch; skipping risks building what nobody wants

IMPORTANT: If this is a net-new product with no existing platform, the analyst cannot do conversion gap analysis on internal data. They must rely on external market data, competitive benchmarks, and customer interviews to estimate demand.""",
        "rubric": {
            "data_sources": "Identifies specific data sources (internal logs if applicable, surveys, market research, competitive analysis).",
            "sizing_method": "Proposes a concrete sizing method (top-down, bottom-up, or both) with actual formula or logic.",
            "go_no_go_signals": "Defines what good and bad signals look like before committing resources.",
            "feasibility": "Considers technical and organizational feasibility.",
            "context_awareness": "Correctly handles whether this is a new product (external data) or existing product (internal + external data).",
        },
        "strong_traits": "Names actual metrics. Uses both top-down and bottom-up sizing. Acknowledges uncertainty ranges. Distinguishes new-product vs. existing-product data sources.",
        "common_mistakes": "Jumping to solutions without sizing. Ignoring competitive landscape. Trying to do conversion gap analysis when there is no existing product. Not defining failure criteria early.",
    },
    {
        "phase_num": 2,
        "phase_id": "validation",
        "phase_name": "Validation — Define and Measure Success",
        "instruction": (
            "Define the analytics framework for measuring success. "
            "What is the North Star metric? What input metrics feed it? "
            "What guardrail metrics would you track? How would you set baselines "
            "and what thresholds would trigger a kill or pivot decision?"
        ),
        "framework_context": """VALIDATION PHASE FRAMEWORK:

Deliverables an analyst produces in this phase:
1. Define the North Star Metric — the single metric that best captures customer value. Must reflect customer outcomes, be measurable, lead revenue, and be moveable by the product team.
2. Build the Metrics Tree — break the North Star into mathematical components. Universal formula: North Star = Reach x Activation x Engagement x Value per Engagement. Assign baselines and targets to each leaf metric.
3. Set Baseline Measurements — measure current state before product launches so before-and-after comparison is possible.
4. Define Kill/Pivot Thresholds — explicit criteria for when to stop. Example: "If Week-4 retention is below X%, or if the North Star does not move by Y% within three cohorts, trigger formal review." Set these BEFORE the product launches, before emotional investment.

Key Metrics:
- North Star Metric (the one number reflecting customer value)
- Metrics Tree Drivers (components that compose the North Star)
- Baseline measurements (current state before launch)
- Kill/pivot thresholds (predetermined decision criteria)

Analysis Methods:
- Metrics Tree Building: Express North Star as formula, break each variable into drivers, label as leading or lagging, assign baselines and targets
- Baseline Establishment: Measure key metrics in current state before product launch
- Power Analysis: Calculate how long experiments need to run to detect meaningful differences given current user volumes
- Benchmark Analysis: Compare proposed targets to industry benchmarks

Trade-offs to consider:
- Early signals or proven results: Activation (fast) vs. revenue/retention (slow). Early signals can mislead.
- Ambitious targets or safe targets: Bar too high = product always looks like failure; bar too low = declare success without solving problem. Set two targets: "minimum viable success" and "aspirational success".""",
        "rubric": {
            "north_star_clarity": "North Star is specific, measurable, and tied to user value — not a vanity metric.",
            "metrics_tree": "Builds a logical tree where inputs clearly drive the North Star. Distinguishes leading from lagging indicators.",
            "baselines": "Plans to set baselines before launch with specific approach.",
            "kill_criteria": "Defines explicit thresholds that trigger kill or pivot conversations.",
            "guardrails": "Identifies guardrail metrics that would flag unintended negative consequences.",
        },
        "strong_traits": "Explains WHY each metric matters. Distinguishes leading from lagging indicators. Sets both minimum and aspirational targets. Defines kill criteria before emotional investment.",
        "common_mistakes": "Choosing revenue as North Star when engagement is the real lever. Forgetting guardrails. Listing metrics without hierarchy. No kill criteria.",
    },
    {
        "phase_num": 3,
        "phase_id": "build",
        "phase_name": "Build — Instrument the Product",
        "instruction": (
            "What instrumentation and data infrastructure would you put in place? "
            "Describe the event taxonomy, dashboards, and data quality validation "
            "needed before launch."
        ),
        "framework_context": """BUILD PHASE FRAMEWORK:

Deliverables an analyst produces in this phase:
1. Event Taxonomy Design — define every meaningful user action and system event to track. Use consistent naming convention (Object-Action format like "suggestion_accepted"). Include segment properties on every event. Estimate event volumes.
2. Dashboard Design — three dashboards minimum:
   - Operational (for engineering): uptime, latency, errors
   - Adoption (for product team): active users, funnel conversion
   - Outcomes (for leadership): North Star, revenue impact
3. Data Quality and Validation Plan — validation checklist, expected event volume estimates, quality monitoring queries. Pre-launch validation: fire every event manually, check for missing properties, validate volume against expectations, test dashboards with real data.

Key Metrics:
- Event Coverage (percentage of meaningful user actions being tracked)
- Data Quality Score (completeness, accuracy, timeliness of event data)
- Expected Event Volume (how many events per user per session)
- Dashboard Readiness (all required dashboards built, tested, populated)

Analysis Methods:
- Data Quality Validation: Systematically check that every tracked event fires correctly with right data
- Event Taxonomy Mapping: Structured document listing every event, what triggers it, what data it carries, what decision it supports
- Dashboard Dry Run: Build dashboards with sample data, walk stakeholders through them, verify they answer specific decisions

IMPORTANT: This phase is about preparation. No experiments, no conclusions. The analyst ensures clean data flows are in place so that Rollout and Scale analytics have trustworthy inputs.""",
        "rubric": {
            "event_taxonomy": "Proposes a coherent naming convention and identifies the key events to track for this scenario.",
            "dashboard_design": "Plans dashboards for different audiences (engineering, product, leadership) with distinct purposes.",
            "data_quality": "Describes a validation plan to ensure data is correct before relying on it.",
            "practical_constraints": "Addresses the scenario's constraint (e.g., limited engineering capacity, lag in data warehouse).",
        },
        "strong_traits": "Uses Object-Action naming. Plans validation before launch. Designs dashboards for specific decisions, not vanity displays. Addresses the constraint directly.",
        "common_mistakes": "Skipping instrumentation and jumping to analysis. Not addressing data quality. Building one dashboard for everyone. Ignoring the constraint.",
    },
    {
        "phase_num": 4,
        "phase_id": "rollout",
        "phase_name": "Rollout — Measure Real-World Impact",
        "instruction": (
            "Design the rollout and experimentation plan. How would you test this? "
            "What methodology would you use? Define the rollout stages, success criteria, "
            "guardrail monitoring, and what would make you stop or expand."
        ),
        "framework_context": """ROLLOUT PHASE FRAMEWORK:

Deliverables an analyst produces in this phase:
1. Adoption Funnel Analysis — track the journey from exposure to activation to engagement to retention. Identify drop-off points and why users do not progress.
2. Cohort Analysis and Experimentation — compare outcomes between groups using:
   - A/B Testing (gold standard) — randomly assign users, compare outcomes. Strongest evidence of causation. Requires enough users and ability to randomize.
   - Pre/Post Analysis — compare metric before and after launch. Simple but cannot separate product effect from other changes.
   - Difference in Differences — compare treated and untreated groups over time. Removes background trends. Requires parallel trends assumption.
   - Interrupted Time Series — track metric over long period, mark launch, look for visible shift. For situations with no comparison group.
   - Funnel Analysis — track conversion between steps. Identify largest drop-offs.
   - Cohort Analysis — group users by when they joined, compare outcomes. Reveals if improvements reach new users.
   - Sequential Testing — monitor experiment results as data accumulates. Allows early stopping while controlling error rates.
   - Multi Armed Bandit — dynamically allocate traffic to better-performing variants. Useful when opportunity cost of showing worse variant is high.
3. Guardrail Metrics Monitoring — monitor false positive rate, workflow disruption, user satisfaction, compliance metrics.
4. Expand/Iterate/Pause Decision — clear criteria:
   - Expand: North Star meets target, guardrails clean, >60% activation in 30 days
   - Iterate: Mixed signals (e.g., strong accuracy but low acceptance rate)
   - Pause: Guardrails breached, adoption flat despite support

Key Metrics:
- Activation Rate (% of new users reaching core value moment)
- Time-to-Activation (days from exposure to first meaningful use)
- Daily Active / Monthly Active ratio (engagement frequency)
- Precision (target >85% for AI products)
- Recall (target >70% for AI products)
- Acceptance Rate (target >50% in first 90 days)

Formulas:
- Pre/Post: (Metric_after - Metric_before) / Metric_before x 100 = % Change
- Difference in Differences: (Treatment_after - Treatment_before) - (Control_after - Control_before)
- Funnel Conversion: Users_completing_step / Users_entering_step x 100 = Step Conversion %

Trade-offs to consider:
- Wait for certainty or decide now: 95% certainty takes time; deciding early risks false positives.
- Catch everything or avoid false alarms (AI products): More flags = fewer misses but overwhelming noise.
- Launch wide or roll out gradually: Wide captures market fast; staged catches problems early.""",
        "rubric": {
            "methodology_fit": "Chosen method matches the scenario constraints (e.g., uses difference-in-differences if randomization is impossible).",
            "sample_size_awareness": "Discusses statistical power and practical sample size requirements.",
            "success_criteria": "Pre-defines what success looks like with specific thresholds.",
            "kill_criteria": "Defines what causes an early stop — guardrail violations, harm signals.",
            "rollout_phases": "Plans a phased approach (internal to beta to staged to general availability) with gate criteria.",
            "guardrails": "Monitors for unintended negative consequences alongside the primary metric.",
        },
        "strong_traits": "Acknowledges power limitations. Plans for edge cases. Mentions network effects or contamination risks. Matches methodology to the constraint.",
        "common_mistakes": "Defaulting to A/B test when randomization is not possible. No power analysis. No kill criteria. Ignoring the constraint.",
    },
    {
        "phase_num": 5,
        "phase_id": "scale",
        "phase_name": "Scale — Optimize and Expand",
        "instruction": (
            "Assuming initial rollout succeeds, how would you approach scale analytics? "
            "Describe your retention framework, product-market fit assessment, "
            "and how you would decide between continuing, pivoting, or shutting down."
        ),
        "framework_context": """SCALE PHASE FRAMEWORK:

Deliverables an analyst produces in this phase:
1. Retention and Expansion Analysis — retention cohort charts, churn prediction models, expansion revenue analysis. Define "retained" as the action best correlating with continued payment.
2. Targeting and Prioritization for Growth — Ideal Customer Profile analysis (updated with real data), lead scoring model, segment-level return on investment analysis.
3. Model Performance Monitoring (for AI products) — model performance dashboard, drift detection alerts, segment-level accuracy reports, retraining trigger criteria.
4. Product-Market Fit Assessment — product-market fit scorecard (updated monthly), segment-level retention and outcome benchmarks, pre-defined pivot/kill thresholds, formal recommendation document when triggered.

Key Metrics:
- N-Day Retention (% active at Day 1, 7, 30, 90)
- Cohort Retention Trend (improving vs. declining)
- Net Revenue Retention (revenue from existing customers including expansion and churn)
- Churn Prediction Score (which users are likely to leave)
- Net Promoter Score or user sentiment

Product-Market Fit Signals:
- Cohort retention trends: Improving = healthy; Flat = warning; Declining = critical
- North Star movement: Above target = healthy; Below but trending up = warning; No movement = critical
- Segment traction: Multiple segments healthy = healthy; Only 1-2 niche = warning; No above-average segment = critical
- User sentiment: >30 NPS = healthy; 0-30 = warning; Negative/declining = critical

Analysis Methods:
- Retention Curve Analysis: Plot % users still active over time. Flattening curve = core user base found. Continuous decline = no lasting value.
  Formula: Retention_day_n = Users_active_day_n / Users_in_cohort x 100
- Survival Analysis (Kaplan-Meier): Statistical method for time until churn. Handles censored data.
- Cohort-Based Retention: Group by signup date, first-week behavior, or segment. Time-based reveals if improvements reaching new users.
- Churn Prediction Models: Predict churn based on early signals (sessions in week 1, feature diversity, session duration trends, support tickets).
- Lifetime Value Analysis: Average Revenue per User x Gross Margin x (1 / Churn Rate) = Lifetime Value. Healthy ratio: Lifetime Value > 3x Customer Acquisition Cost.

Warning Signs and Kill Signals:
- Kill or major pivot: Retention declining across all cohorts, North Star not moving despite 3+ iterations, no segment showing above-average outcomes
- Narrow focus: Only 1-2 segments retaining well — narrow to those and re-evaluate
- Continue and expand: Multiple segments retaining, North Star above target, positive NPS

Trade-offs to consider:
- Keep existing users or find new ones: Retention improvement usually delivers more value per dollar than acquisition
- Deepen the product or broaden it: Existing customers want advanced capabilities; new segments want basic compatibility
- Keep going or shut it down: Teams stay attached even when data says stop""",
        "rubric": {
            "retention_framework": "Describes specific retention curves and benchmarks for this product type.",
            "pmf_signals": "Identifies concrete product-market fit signals beyond 'retention is good' — engagement depth, organic growth, willingness to pay.",
            "cohort_strategy": "Plans meaningful cohort segmentation (time, behavior, segment) with clear rationale.",
            "kill_pivot_criteria": "Defines thresholds that trigger a discontinue or pivot conversation with leadership.",
            "expansion_plan": "Addresses how to identify next growth opportunities using segment data.",
        },
        "strong_traits": "Connects cohort insights to product decisions. Names product-market fit benchmarks relevant to the industry. Plans for honest assessment. Addresses warning signs directly.",
        "common_mistakes": "Vague 'we would look at retention' without specifics. No product-market fit framework. Does not address what happens if metrics are bad. Ignores churn prediction.",
    },
]


# ============================================================
# System Prompt (Coach Persona)
# ============================================================

COACH_SYSTEM_PROMPT = """You are a senior product analytics coach helping a candidate prepare for a case study interview. Your role is to evaluate responses against a specific framework and provide constructive, actionable feedback.

RULES:
- Be specific. Reference the scenario details in your feedback.
- When something is missing, name exactly what is missing and why it matters.
- When something is strong, explain why it demonstrates good analytical thinking.
- Keep feedback concise — three to five sentences of substance, not filler.
- Do not invent information about the scenario. Stay within what was given.
- Score honestly. A 3 out of 5 is a solid developing response. Reserve 5 for truly exceptional answers.
- Use plain language. Spell out all terms (no acronyms).
- Frame improvement suggestions as "Next time, try..." rather than criticism.

FORMATTING RULES (very important):
- Write in plain prose paragraphs. Do NOT use markdown formatting like **bold**, *italic*, ##headings, or --- dividers.
- Use numbered lists (1. 2. 3.) or dash lists (- item) only when listing specific items.
- Never use markdown bold (**) or italic (*) markers anywhere in your response.
- Keep it clean, readable, plain text."""


def _build_phase_prompt(scenario, phase, user_response, mode="score"):
    """Build the user prompt for scoring or hinting."""
    rubric_text = "\n".join(
        f"  - {dim}: {desc}" for dim, desc in phase["rubric"].items()
    )

    if mode == "hint":
        return f"""SCENARIO:
{scenario['full_prompt']}

PHASE: Phase {phase['phase_num']} — {phase['phase_name']}
TASK: {phase['instruction']}

FRAMEWORK REFERENCE:
{phase['framework_context']}

The candidate is stuck and asking for a hint. Give them a nudge — not the answer. Suggest ONE specific thing they should think about next, drawn from the framework reference above. Keep it to 2-3 sentences. Do not give away the full answer. Write in plain prose, no markdown formatting."""

    if mode == "example":
        return f"""SCENARIO:
{scenario['full_prompt']}

PHASE: Phase {phase['phase_num']} — {phase['phase_name']}
TASK: {phase['instruction']}

FRAMEWORK REFERENCE:
{phase['framework_context']}

The candidate wants to see what a strong response looks like for this phase. Write a concise but thorough example response (200-300 words) that would score 4-5 out of 5 on the rubric. Use specific details from the scenario. This is a teaching tool — make it clear why each element is included.

Write in plain prose paragraphs. You may use numbered lists or dash lists for specific items, but do NOT use markdown formatting (no **bold**, no *italic*, no ## headings, no --- dividers). Keep it clean and readable."""

    # Default: score mode
    return f"""SCENARIO:
{scenario['full_prompt']}

PHASE: Phase {phase['phase_num']} — {phase['phase_name']}
TASK: {phase['instruction']}

FRAMEWORK REFERENCE (use this to evaluate completeness):
{phase['framework_context']}

SCORING RUBRIC (rate each dimension 1-5):
{rubric_text}

WHAT A STRONG ANSWER LOOKS LIKE:
{phase['strong_traits']}

COMMON MISTAKES TO WATCH FOR:
{phase['common_mistakes']}

CANDIDATE'S RESPONSE:
{user_response}

INSTRUCTIONS:
1. Score each rubric dimension from 1 (poor) to 5 (excellent).
2. Provide a composite score (average of dimensions, rounded to 1 decimal).
3. Write 3-5 sentences of specific, constructive feedback referencing the scenario.
4. Identify one specific strength and one specific area for improvement.
5. If the candidate missed key framework elements, name them specifically.

Respond in EXACTLY this JSON format (no markdown, no code fences):
{{
  "scores": {{"dimension_name": score, ...}},
  "composite": 3.5,
  "feedback": "Your specific feedback here.",
  "strength": "One thing done well.",
  "improvement": "One thing to work on.",
  "missed_elements": ["element 1", "element 2"]
}}"""


# ============================================================
# Scoring
# ============================================================

def _parse_json_response(text):
    """Parse JSON from Claude response, handling markdown fences."""
    if text is None:
        return None
    text = re.sub(r"^```(?:json)?\s*", "", text.strip())
    text = re.sub(r"\s*```$", "", text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def score_response(scenario, phase, user_response):
    """
    Score a candidate response for a given phase.

    Returns dict with: scores, composite, feedback, strength, improvement,
    missed_elements, latency, raw_text
    """
    prompt = _build_phase_prompt(scenario, phase, user_response, mode="score")
    text, latency = _call_claude(COACH_SYSTEM_PROMPT, prompt, max_tokens=800)

    parsed = _parse_json_response(text)
    if parsed:
        parsed["latency"] = latency
        parsed["raw_text"] = text
        return parsed

    # Fallback if parsing fails
    return {
        "scores": {},
        "composite": 0.0,
        "feedback": text or "Scoring failed. Try again.",
        "strength": "N/A",
        "improvement": "N/A",
        "missed_elements": [],
        "latency": latency,
        "raw_text": text,
    }


def get_hint(scenario, phase):
    """Get a coaching hint for the current phase."""
    prompt = _build_phase_prompt(scenario, phase, "", mode="hint")
    text, latency = _call_claude(COACH_SYSTEM_PROMPT, prompt, max_tokens=300)
    return text or "Think about what deliverables an analyst would produce in this phase. Check the playbook for the specific framework."


def get_example(scenario, phase):
    """Get an example strong response for the current phase."""
    prompt = _build_phase_prompt(scenario, phase, "", mode="example")
    text, latency = _call_claude(COACH_SYSTEM_PROMPT, prompt, max_tokens=800)
    return text or "Example generation failed. Review the playbook for this phase."


# ============================================================
# Session Logging
# ============================================================

_SESSION_LOG = []
_OUTPUTS_DIR = None


def init_session_logger(outputs_dir):
    """Set the output directory for session logs."""
    global _OUTPUTS_DIR
    _OUTPUTS_DIR = outputs_dir
    os.makedirs(outputs_dir, exist_ok=True)


def log_phase_result(session_id, scenario, phase, user_response, score_result, time_spent_sec=None):
    """Log a single phase result for later analysis."""
    record = {
        "session_id": session_id,
        "timestamp": datetime.now().isoformat(),
        "scenario_id": scenario["scenario_id"],
        "archetype": scenario["archetype_type"],
        "situation": scenario["situation_label"],
        "scope": scenario["scope"],
        "constraint": scenario["constraint"],
        "phase_num": phase["phase_num"],
        "phase_name": phase["phase_name"],
        "user_response_length": len(user_response),
        "user_response": user_response,
        "composite_score": score_result.get("composite", 0),
        "latency": score_result.get("latency", 0),
        "feedback": score_result.get("feedback", ""),
        "strength": score_result.get("strength", ""),
        "improvement": score_result.get("improvement", ""),
        "time_spent_sec": time_spent_sec,
    }

    # Per-dimension scores
    for dim, val in score_result.get("scores", {}).items():
        record[f"score_{dim}"] = val

    # Missed elements
    missed = score_result.get("missed_elements", [])
    record["missed_elements"] = "; ".join(missed) if missed else ""
    record["n_missed"] = len(missed)

    _SESSION_LOG.append(record)
    return record


def save_session_log(filename=None):
    """Save accumulated session log to CSV."""
    if not _SESSION_LOG:
        print("No session data to save.")
        return None

    if filename is None:
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"practice_session_{ts}.csv"

    filepath = os.path.join(_OUTPUTS_DIR, filename)
    df = pd.DataFrame(_SESSION_LOG)
    df.to_csv(filepath, index=False)
    print(f"Session log saved: {filepath}  ({len(df)} phase records)")
    return filepath


def load_all_sessions(outputs_dir=None):
    """Load all saved session CSVs into one DataFrame."""
    d = outputs_dir or _OUTPUTS_DIR
    files = sorted(Path(d).glob("practice_session_*.csv"))
    if not files:
        print("No session files found.")
        return pd.DataFrame()
    dfs = [pd.read_csv(f) for f in files]
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(files)} session files -> {len(combined)} phase records")
    return combined


# ============================================================
# Display Helpers
# ============================================================

def format_scenario_html(scenario):
    """Return formatted HTML for notebook display."""
    scope_label = "New Product" if scenario["scope"] == "product" else "Feature on Existing Product"
    return f"""
<div style="background:#f0f7ff; border-left:4px solid #2E86AB; padding:16px; border-radius:6px; margin:8px 0;">
  <h3 style="margin:0 0 8px 0; color:#1a1a2e;">Case Study Scenario</h3>
  <table style="border-collapse:collapse; width:100%;">
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top; white-space:nowrap;">Company</td>
        <td style="padding:4px 0;">{scenario['company_name']} — {scenario['archetype_type']}</td></tr>
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top;">Situation</td>
        <td style="padding:4px 0;">{scenario['situation_label']}</td></tr>
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top;">Scope</td>
        <td style="padding:4px 0;">{scope_label}</td></tr>
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top;">Primary Users</td>
        <td style="padding:4px 0;">{scenario['user_type']}</td></tr>
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top;">Constraint</td>
        <td style="padding:4px 0; color:#b91c1c;">{scenario['constraint']}</td></tr>
  </table>
  <div style="margin-top:10px; font-size:13px; color:#555;">
    Emphasis phases: {', '.join(p.title() for p in scenario['emphasis_phases'])} |
    Domain metrics: {scenario['archetype_metrics']}
  </div>
</div>"""


def format_phase_instruction_html(phase):
    """Return HTML for the phase instruction banner."""
    colors = {
        "discovery": ("#2E86AB", "#e8f4f8"),
        "validation": ("#F18F01", "#fff7eb"),
        "build": ("#6c63ff", "#f0eeff"),
        "rollout": ("#2CA58D", "#e8f7f3"),
        "scale": ("#E15554", "#fdeaea"),
    }
    border_color, bg_color = colors.get(phase["phase_id"], ("#333", "#f5f5f5"))

    return f"""
<div style="background:{bg_color}; border-left:4px solid {border_color}; padding:14px; border-radius:6px; margin-bottom:12px;">
  <h3 style="margin:0 0 6px 0; color:{border_color};">Phase {phase['phase_num']}: {phase['phase_name']}</h3>
  <p style="margin:0; line-height:1.6;">{phase['instruction']}</p>
</div>"""


def format_score_html(phase, score_result):
    """Return formatted HTML for score feedback."""
    composite = score_result.get("composite", 0)

    if composite >= 4.0:
        color, bg, label = "#166534", "#dcfce7", "Strong"
    elif composite >= 3.0:
        color, bg, label = "#854d0e", "#fef9c3", "Developing"
    else:
        color, bg, label = "#991b1b", "#fee2e2", "Needs Work"

    # Dimension bars
    dim_html = ""
    for dim, val in score_result.get("scores", {}).items():
        pct = val / 5 * 100
        dim_label = dim.replace("_", " ").title()
        dim_html += f"""
        <div style="display:flex; align-items:center; margin:3px 0;">
          <span style="width:200px; font-size:13px;">{dim_label}</span>
          <div style="flex:1; background:#e5e7eb; border-radius:4px; height:16px; margin:0 8px;">
            <div style="width:{pct}%; background:{color}; height:16px; border-radius:4px;"></div>
          </div>
          <span style="font-size:13px; font-weight:600;">{val}/5</span>
        </div>"""

    # Missed elements
    missed = score_result.get("missed_elements", [])
    missed_html = ""
    if missed:
        items = "".join(f"<li>{m}</li>" for m in missed)
        missed_html = f"""
        <div style="margin-top:10px; padding:10px; background:#fff7ed; border-radius:4px; border-left:3px solid #F18F01;">
          <strong style="color:#92400e;">Framework elements to revisit:</strong>
          <ul style="margin:4px 0 0 16px; padding:0; font-size:14px;">{items}</ul>
        </div>"""

    return f"""
<div style="background:{bg}; border-left:4px solid {color}; padding:16px; border-radius:6px; margin:8px 0;">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0; color:{color};">Phase {phase['phase_num']}: {phase['phase_name']}</h3>
    <span style="font-size:24px; font-weight:700; color:{color};">{composite}/5 — {label}</span>
  </div>
  <div style="margin:12px 0;">{dim_html}</div>
  <div style="margin-top:12px; padding:10px; background:white; border-radius:4px;">
    <strong>Feedback:</strong> {score_result.get('feedback', '')}
  </div>
  <div style="margin-top:8px; display:flex; gap:16px;">
    <div style="flex:1; padding:8px; background:white; border-radius:4px;">
      <strong style="color:#166534;">Strength:</strong> {score_result.get('strength', '')}
    </div>
    <div style="flex:1; padding:8px; background:white; border-radius:4px;">
      <strong style="color:#b91c1c;">Improve:</strong> {score_result.get('improvement', '')}
    </div>
  </div>
  {missed_html}
  <div style="font-size:12px; color:#6b7280; margin-top:8px;">Scored in {score_result.get('latency', 0)}s</div>
</div>"""


def format_session_summary_html(phase_scores):
    """Return HTML summary of all phases in a session."""
    if not phase_scores:
        return "<p>No scores recorded yet.</p>"

    total = sum(s["composite"] for s in phase_scores) / len(phase_scores)
    rows = ""
    phase_colors = {1: "#2E86AB", 2: "#F18F01", 3: "#6c63ff", 4: "#2CA58D", 5: "#E15554"}

    for s in phase_scores:
        comp = s["composite"]
        if comp >= 4.0:
            badge = "Strong"
            badge_bg = "#dcfce7"
            badge_color = "#166534"
        elif comp >= 3.0:
            badge = "Developing"
            badge_bg = "#fef9c3"
            badge_color = "#854d0e"
        else:
            badge = "Needs Work"
            badge_bg = "#fee2e2"
            badge_color = "#991b1b"
        pc = phase_colors.get(s["phase_num"], "#333")
        rows += f"""<tr>
            <td style="padding:6px 10px; border-left:3px solid {pc};"><strong>Phase {s['phase_num']}</strong></td>
            <td style="padding:6px 10px;">{s['phase_name']}</td>
            <td style="padding:6px 10px; font-weight:600;">{comp}/5</td>
            <td style="padding:6px 10px;"><span style="background:{badge_bg}; color:{badge_color}; padding:2px 8px; border-radius:10px; font-size:12px;">{badge}</span></td>
        </tr>"""

    return f"""
<div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:8px; margin:12px 0;">
  <h3 style="margin:0 0 12px 0;">Session Summary — Overall: {round(total, 1)}/5</h3>
  <table style="width:100%; border-collapse:collapse;">
    <thead><tr style="border-bottom:2px solid #cbd5e1;">
      <th style="padding:6px 10px; text-align:left;"></th>
      <th style="padding:6px 10px; text-align:left;">Phase</th>
      <th style="padding:6px 10px; text-align:left;">Score</th>
      <th style="padding:6px 10px; text-align:left;">Level</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""
