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
# Phase Guides (static hints to help write your response)
# ============================================================

PHASE_GUIDES = {
    "discovery": {
        "title": "Guide: What to Write for Discovery",
        "what_this_is": "Discovery is about understanding the opportunity before building anything. You are answering: Is this worth doing?",
        "key_questions": [
            "What is the problem and who has it?",
            "How big is the market? (Use both top-down and bottom-up estimates)",
            "Who are the customer segments, and which ones matter most?",
            "What competitors or workarounds exist today?",
            "Are there conversion gaps on the existing platform? (Only if this is an existing product)",
            "What would make you say no to this opportunity?",
        ],
        "remember": [
            "If this is a new product with no users yet, you cannot do internal conversion gap analysis — use external data instead",
            "Always size the market two ways: top-down (total market x your slice) and bottom-up (count real customers x realistic spend)",
            "Name specific data sources, not just 'I would look at the data'",
            "Include go/no-go signals — what would make you stop before investing",
        ],
    },
    "validation": {
        "title": "Guide: What to Write for Validation",
        "what_this_is": "Validation is about defining what success looks like in measurable terms, before you build anything. You are answering: How will we know if this works?",
        "key_questions": [
            "What is the North Star metric? (The one number that means the product is delivering value)",
            "What inputs drive the North Star? (Build a metrics tree)",
            "What are the current baselines? (The 'before' numbers you will compare against)",
            "What guardrail metrics must not get worse? (False positives, complaints, latency)",
            "At what thresholds would you kill or pivot? (Set these before you launch)",
            "Which customer segment should you test first, and why?",
        ],
        "remember": [
            "The North Star must reflect customer value, not just activity (avoid vanity metrics like page views)",
            "Set two targets: minimum viable success (floor) and aspirational success (what great looks like)",
            "Define kill criteria now, before emotional investment — this protects the team from sunk cost bias",
            "Distinguish leading indicators (move fast) from lagging indicators (confirm over time)",
        ],
    },
    "build": {
        "title": "Guide: What to Write for Build",
        "what_this_is": "Build is about putting the tracking infrastructure in place. If it is not tracked during Build, it cannot be measured during Rollout. You are answering: What do we need to measure, and how?",
        "key_questions": [
            "What user actions need to be tracked? (Map the user journey step by step)",
            "What is the event naming convention? (Use object_action format like suggestion_accepted)",
            "What properties should each event carry? (Customer tier, segment, use case)",
            "What dashboards does the team need on day one? (Operational, adoption, outcomes)",
            "How will you validate data quality before launch?",
            "Is engineering treating tracking as a launch blocker or a nice-to-have?",
        ],
        "remember": [
            "If you miss an event now, the data for early users is lost forever",
            "Build separate dashboards for different audiences: engineering, product team, leadership",
            "Test every event in a staging environment before launch",
            "Address the scenario constraint directly (limited engineering, data lag, etc.)",
        ],
    },
    "rollout": {
        "title": "Guide: What to Write for Rollout",
        "what_this_is": "Rollout is where the product goes live and you measure real-world impact. You are answering: Is it working, and should we expand?",
        "key_questions": [
            "Who is in the first cohort and how were they selected? (Watch for selection bias)",
            "What is the activation moment? (The specific action that means a user got value)",
            "What does the adoption funnel look like? (Eligible -> Exposed -> Activated -> Retained)",
            "How does impact compare to baselines and success thresholds?",
            "What guardrail alerts are in place? (What would make you pause the rollout?)",
            "What is your recommendation: expand, iterate, or pause?",
        ],
        "remember": [
            "If the first cohort was hand-picked, early numbers will look artificially high",
            "Match your experimentation method to the constraint (no randomization = use difference-in-differences, not A/B test)",
            "Monitor guardrails in real time, not just in monthly reviews",
            "Pre-agree with the PM on what data drives the expand decision",
        ],
    },
    "scale": {
        "title": "Guide: What to Write for Scale",
        "what_this_is": "Scale is about long-term health, growth, and honest assessment. You are answering: Will this keep working, where do we grow, and should we continue?",
        "key_questions": [
            "Which segments retain and expand? Which churn?",
            "Where does the next wave of growth come from? (Existing customers or new segments?)",
            "Does the product have product-market fit? (Retention curves, North Star trend, segment consistency)",
            "For AI products: Is model performance stable or drifting?",
            "Are we above or below the kill/pivot thresholds set in Validation?",
            "What is the honest recommendation: continue, narrow focus, pivot, or stop?",
        ],
        "remember": [
            "Retention improvement usually delivers more value per dollar than acquisition",
            "Product-market fit means it works across multiple segments, not just cherry-picked ones",
            "Revisit the kill/pivot thresholds the team agreed on before they were emotionally invested",
            "For AI products, model drift is inevitable — there must be a retraining plan",
        ],
    },
}


# ============================================================
# Speaking Outlines (rehearsal scripts from the playbook)
# ============================================================

PHASE_SCRIPTS = {
    "discovery": {
        "title": "Speaking Outline: Discovery Conversation",
        "sections": [
            {
                "label": "OPEN",
                "label_type": "open",
                "title": "Set the framework and introduce Discovery",
                "bullets": [
                    ("My approach", '"I like to use a five phase method for product analytics: Discovery, Validation, Build, Rollout, and Scale."'),
                    ("What it does", '"This helps define the metrics we need to track the success of a new product or feature, and also helps make critical decisions along the way, like whether to continue, pivot, or stop."'),
                    ("Each phase builds", '"Each phase feeds into the next, so the work we do early on directly shapes what we measure, how we launch, and how we know if the product is working."'),
                    ("Start with Discovery", '"I will start with Discovery, which is about understanding the opportunity before we build anything."'),
                    ("Problem scope", "What is the problem the product is intended to fix, who has it, and how big is it"),
                    ("Alternatives", "Are there already competitors or indirect alternatives that customers are using today"),
                    ("Opportunity viability", "Are there early signs the opportunity itself is not viable, like a market that is too small or a competitive landscape with no whitespace"),
                    ("Downstream inputs", "These inputs become the foundation for Validation, where we define success metrics and set thresholds, and for Build, where we decide what to instrument"),
                ],
            },
            {
                "label": "ACT",
                "label_type": "action",
                "title": "Actions",
                "bullets": [
                    ("Share screen", "Open a blank document or whiteboard"),
                    ("Context header", 'Create two columns — "Existing Platform" and "Net New Product" — ask which applies'),
                    ("Assumptions log", "Start a running list of assumptions to validate"),
                ],
            },
            {
                "label": "1",
                "label_type": "number",
                "title": "Clarify the context",
                "bullets": [
                    ("Platform type", '"Are we adding to an existing product or building from scratch?"'),
                    ("Existing", "Internal data available to validate against real user behavior"),
                    ("Net new", "Rely on external evidence — industry reports, public data, customer interviews"),
                    ("Analytics output", "Determines which data sources are available and what validation methods apply to every analysis in this phase"),
                ],
                "how_to_say_it": '"Are we adding a feature to an existing product where we have usage data, or is this a net new product with no existing users? The answer changes what I can realistically validate in Discovery and how much confidence we should put in the estimates."',
            },
            {
                "label": "2",
                "label_type": "number",
                "title": "Understand the problem",
                "bullets": [
                    ("Problem statement", '"What specific problem are we solving and for whom?"'),
                    ("Current solutions", '"How are those customers solving it today?" — competitors, workarounds, manual processes'),
                    ("Analytics output", "Defines what the North Star metric should measure and which customer outcomes to track"),
                ],
                "how_to_say_it": '"Before I start pulling data, I want to make sure I understand the problem we are solving. Can you walk me through who is experiencing this pain, how they deal with it today, and what changes for them if we build this?"',
            },
            {
                "label": "3",
                "label_type": "number",
                "title": "Size the market",
                "bullets": [
                    ("Source check", '"Where did the current market estimate come from?"'),
                    ("Bottom up check", "Count target customers x realistic spend"),
                    ("Conversion filter", "Not everyone adopts — apply realistic rates"),
                    ("Competitive subtraction", "Subtract who is already well served"),
                    ("Visual", "Write the top down and bottom up numbers side by side on screen"),
                    ("Analytics output", "Produces the Total Addressable Market and Serviceable Addressable Market numbers that set the ceiling for success thresholds in Validation"),
                ],
                "how_to_say_it": '"I see the market estimate is $X. Can you tell me where that number comes from — industry report, internal model, competitive benchmarks? That helps me figure out what data I should pull to stress test it."',
            },
            {
                "label": "4",
                "label_type": "number",
                "title": "Segment the customers",
                "bullets": [
                    ("Segmentation axes", "Group by what predicts value — pain severity, company size, workflow complexity"),
                    ("Rank", "Size and rank each segment by need x readiness x revenue"),
                    ("Visual", "Sketch a simple prioritization matrix on screen"),
                    ("Analytics output", "Produces segment definitions that determine how we set different success thresholds per group, what properties to attach to every tracked event, and which segment to launch to first"),
                ],
            },
            {
                "label": "5",
                "label_type": "number",
                "title": "Identify conversion gaps (existing platform only)",
                "bullets": [
                    ("Drop off points", '"Where do users start an action but not finish it today?"'),
                    ("High gap", "Demand exists but something blocks completion"),
                    ("Low gap", "Current experience works, less reason to build"),
                    ("Analytics output", "Establishes baseline measurements (the before numbers) that Rollout will measure the product impact against"),
                ],
            },
            {
                "label": "6",
                "label_type": "number",
                "title": "Map the competitive landscape",
                "bullets": [
                    ("Direct competitors", "Who solves this today?"),
                    ("Indirect alternatives", "Spreadsheets, manual processes, in house tools"),
                    ("Whitespace", "Where nobody serves customers well"),
                    ("Visual", "Note on screen which gaps align with our strongest segments"),
                    ("Analytics output", "Identifies whitespace opportunities and shapes what the dashboards need to prove"),
                ],
                "how_to_say_it": '"Who are the main players solving this today, and what do you think they are missing? I want to make sure my competitive analysis covers both the obvious competitors and the workarounds customers are using."',
            },
            {
                "label": "7",
                "label_type": "number",
                "title": "Assess go or no go inputs",
                "bullets": [
                    ("Kill question", '"What would make you say no to this?"'),
                    ("Confidence levels", "Document each assumption as high, medium, or low"),
                    ("Flag gaps", "Anything that needs more data before deciding"),
                    ("Analytics output", "Produces the kill/pivot criteria and a confidence scored assumption log that Validation uses to set formal thresholds"),
                ],
                "how_to_say_it": '"If Discovery shows that the addressable market is smaller than expected, or that the competitive landscape is more crowded than we thought, would that change the plan?"',
            },
            {
                "label": "BRIDGE",
                "label_type": "bridge",
                "title": "Bridge to next phase",
                "bullets": [
                    ("Validation preview", '"These segments, sizing numbers, and gap analyses become the inputs for Validation, where we define exactly what success looks like and set thresholds for when to stop."'),
                ],
            },
        ],
    },
    "validation": {
        "title": "Speaking Outline: Validation Conversation",
        "sections": [
            {
                "label": "OPEN",
                "label_type": "open",
                "title": "Transition from Discovery and frame Validation",
                "bullets": [
                    ("Recap handoff", '"Discovery gave us the market sizing, customer segments, and competitive whitespace. Now we need to define what winning looks like before we build anything."'),
                    ("Purpose of Validation", '"Validation is about turning the opportunity into measurable targets, so the team has a shared definition of success and agreed criteria for when to stop."'),
                    ("Warning signs", "Signs the product concept is not viable: the team cannot agree on a North Star metric, baselines are already high (little room to improve), or leadership refuses to define kill/pivot thresholds"),
                    ("Downstream inputs", "The metrics, baselines, and thresholds set here become the spec for what Build needs to instrument and the benchmarks Rollout measures against"),
                ],
            },
            {
                "label": "ACT",
                "label_type": "action",
                "title": "Actions",
                "bullets": [
                    ("Share screen", "Open a document or whiteboard with Discovery outputs visible"),
                    ("Metrics scaffold", "Create a section for North Star, supporting metrics, baselines, and thresholds"),
                    ("Assumptions carry forward", "Pull up the assumptions log from Discovery to validate or update"),
                ],
            },
            {
                "label": "1",
                "label_type": "number",
                "title": "Define the North Star metric",
                "bullets": [
                    ("Customer outcome", '"What changes for the customer when this product works?"'),
                    ("One number", "Translate the answer into a single measurable metric"),
                    ("Four criteria", "Reflects value (not vanity), measurable, leads revenue, moveable by the team"),
                    ("Analytics output", "Produces the North Star metric definition that drives the entire metrics tree, event taxonomy, and dashboard design in Build"),
                ],
                "how_to_say_it": '"If this product works exactly the way you hope, what changes for the customer? I am trying to identify the one number we can track that tells us whether we are delivering real value — not just whether people are using it."',
            },
            {
                "label": "2",
                "label_type": "number",
                "title": "Build the metrics tree",
                "bullets": [
                    ("Decompose", "Break the North Star into the 3 to 5 inputs that drive it"),
                    ("Leading indicators", "Which inputs move first and predict the North Star"),
                    ("Guardrails", "What must not get worse (false positive rate, user complaints, latency)"),
                    ("Analytics output", "Produces the metrics tree that becomes the spec for every event and dashboard Build needs to create"),
                ],
            },
            {
                "label": "3",
                "label_type": "number",
                "title": "Establish baselines",
                "bullets": [
                    ("Before number", '"Where are customers today on each metric?"'),
                    ("Data availability", "Do we already track the key outcome, or do we need to build that measurement before launch"),
                    ("Segment variation", "Baselines may differ by segment — measure each separately"),
                    ("Analytics output", "Produces baseline measurements (the before numbers) that Rollout uses to prove the product impact"),
                ],
                "how_to_say_it": '"Before we launch, I need to measure where customers are today so we have a comparison point. Do we already track the key outcome, or do I need to build that measurement before we go live?"',
            },
            {
                "label": "4",
                "label_type": "number",
                "title": "Set success thresholds",
                "bullets": [
                    ("Two targets", "Minimum viable success (floor the product must clear) and aspirational success (what great looks like)"),
                    ("Grounded in data", "Use baselines and industry benchmarks, not gut feel"),
                    ("Per segment", "Different segments may have different thresholds"),
                    ("Analytics output", "Produces success thresholds that become the criteria for the expand/iterate/pause decision in Rollout"),
                ],
            },
            {
                "label": "5",
                "label_type": "number",
                "title": "Define kill and pivot criteria",
                "bullets": [
                    ("Set now, use later", '"If Week 4 retention is below X%, if the North Star does not move by Y%, we trigger a formal review"'),
                    ("Why now", "Setting these before launch removes emotion and sunk cost bias from the decision"),
                    ("Get agreement", "Leadership must sign off on these thresholds in advance"),
                    ("Analytics output", "Produces kill/pivot thresholds that Scale uses in the product-market fit scorecard to make the continue/stop decision"),
                ],
                "how_to_say_it": '"I want to agree on the thresholds now, while we are being objective. Something like: if Week 4 retention is below X%, or if the North Star does not move by Y% within the first three cohorts, we trigger a formal review."',
            },
            {
                "label": "6",
                "label_type": "number",
                "title": "Select pilot segments",
                "bullets": [
                    ("Segment hypothesis", '"Which segment is most likely to succeed, and why?"'),
                    ("Pilot design", "Design measurement to test the hypothesis and catch early signals if it is wrong"),
                    ("Sample size", "Enough users per segment to draw meaningful conclusions"),
                    ("Analytics output", "Determines which segments to launch to first and how to structure the cohort analysis in Rollout"),
                ],
                "how_to_say_it": '"Discovery identified three segments. Which one do you want to validate first, and what makes you think they will get the most value?"',
            },
            {
                "label": "BRIDGE",
                "label_type": "bridge",
                "title": "Bridge to next phase",
                "bullets": [
                    ("Build preview", '"Now that we have the North Star, metrics tree, baselines, and thresholds, Build is where we turn these into actual tracking. The event taxonomy and dashboards will be designed to measure exactly what we just defined."'),
                ],
            },
        ],
    },
    "build": {
        "title": "Speaking Outline: Build Conversation",
        "sections": [
            {
                "label": "OPEN",
                "label_type": "open",
                "title": "Transition from Validation and frame Build",
                "bullets": [
                    ("Recap handoff", '"Validation gave us the North Star metric, metrics tree, baselines, and kill/pivot thresholds. Now we need to build the tracking infrastructure to measure all of it."'),
                    ("Purpose of Build", '"Build is where we put the analytics infrastructure in place. If something is not tracked during Build, it cannot be measured during Rollout. There is no going back."'),
                    ("Warning signs", "Engineering treats tracking as a nice to have instead of a launch blocker, or the team cannot agree on which user actions matter most"),
                    ("Downstream inputs", "The event taxonomy, dashboards, and data quality checks built here are what Rollout and Scale depend on entirely"),
                ],
            },
            {
                "label": "ACT",
                "label_type": "action",
                "title": "Actions",
                "bullets": [
                    ("Share screen", "Open the metrics tree from Validation as a reference"),
                    ("Event table", "Start a table with columns: Event Name, Trigger, Properties, Owner"),
                    ("Dashboard wireframe", "Sketch the day one dashboard layout"),
                ],
            },
            {
                "label": "1",
                "label_type": "number",
                "title": "Map the user journey to events",
                "bullets": [
                    ("Ideal workflow", '"Walk me through the user journey step by step"'),
                    ("Critical actions", "Every meaningful step from first login through the core value moment"),
                    ("Missed events", "If we miss a step now, we cannot measure it for users who already went through the flow"),
                    ("Analytics output", "Produces the user journey map that determines every event in the event taxonomy"),
                ],
                "how_to_say_it": '"Can you walk me through the ideal user journey step by step? I need to make sure we are tracking every meaningful action — from first login through the core value moment."',
            },
            {
                "label": "2",
                "label_type": "number",
                "title": "Design the event taxonomy",
                "bullets": [
                    ("Naming convention", "Consistent format like object_action (e.g. suggestion_displayed, suggestion_accepted)"),
                    ("Properties", "Attach segment identifiers to every event — customer tier, use case, company size"),
                    ("Granularity", 'Separate events for related but distinct actions (e.g. "suggestion displayed" is separate from "suggestion accepted")'),
                    ("Analytics output", "Produces the event taxonomy document — the foundation every Rollout and Scale metric sits on"),
                ],
            },
            {
                "label": "3",
                "label_type": "number",
                "title": "Build dashboards for launch decisions",
                "bullets": [
                    ("Decision driven", '"What decisions will the team need to make in the first two weeks after launch?"'),
                    ("Day one ready", "Dashboards must be live before launch, not built after"),
                    ("Stakeholder views", "Executive summary for leadership, detailed operational view for the product team"),
                    ("Analytics output", "Produces the dashboards the team stares at during Rollout"),
                ],
                "how_to_say_it": '"Walk me through the first two weeks after launch. What questions will you be asking, and what decisions will you need to make? I want to build the dashboards around the decisions you actually need to make."',
            },
            {
                "label": "4",
                "label_type": "number",
                "title": "Plan data quality validation",
                "bullets": [
                    ("Double fire check", "Make sure events fire exactly once per action, not twice"),
                    ("Property completeness", "Verify all required properties are populated on every event"),
                    ("QA environment", "Test tracking in staging before launch"),
                    ("Analytics output", "Produces data quality checks — the early warning system that keeps Rollout numbers trustworthy"),
                ],
            },
            {
                "label": "5",
                "label_type": "number",
                "title": "Coordinate with engineering",
                "bullets": [
                    ("Tracking as blocker", "Tracking must be treated as a launch requirement, not a nice to have"),
                    ("Cutoff date", "When is the latest to hand engineering the tracking plan"),
                    ("Model logging (AI)", "For AI products, log model confidence, input features, and user feedback on every suggestion"),
                    ("Analytics output", "Ensures every event in the taxonomy is actually implemented"),
                ],
                "how_to_say_it": '"I have the event tracking plan ready. When is the latest I can hand this to engineering and still have it in the launch build? I want to make sure the tracking is treated as a blocker, not a stretch goal."',
            },
            {
                "label": "BRIDGE",
                "label_type": "bridge",
                "title": "Bridge to next phase",
                "bullets": [
                    ("Rollout preview", '"With the event taxonomy, dashboards, and quality checks in place, we are ready for Rollout — where we start measuring real user behavior against the baselines and thresholds we set in Validation."'),
                ],
            },
        ],
    },
    "rollout": {
        "title": "Speaking Outline: Rollout Conversation",
        "sections": [
            {
                "label": "OPEN",
                "label_type": "open",
                "title": "Transition from Build and frame Rollout",
                "bullets": [
                    ("Recap handoff", '"Build gave us the event taxonomy, dashboards, and data quality checks. The product is live. Now we measure real world impact."'),
                    ("Purpose of Rollout", '"Rollout is where analytics goes from planning to real time decision making. We monitor adoption, measure impact against baselines, and decide whether to expand, iterate, or pause."'),
                    ("Warning signs", "Early cohort was cherry picked so numbers do not generalize, activation rate is low, or guardrail metrics are triggering alerts"),
                    ("Downstream inputs", "Rollout adoption data, retention curves, and impact measurements become the inputs for Scale product-market fit assessment"),
                ],
            },
            {
                "label": "ACT",
                "label_type": "action",
                "title": "Actions",
                "bullets": [
                    ("Share screen", "Open the Rollout dashboard"),
                    ("Thresholds visible", "Pull up the success thresholds and kill/pivot criteria from Validation as reference"),
                    ("Cohort tracker", "Set up a view showing each rollout cohort separately"),
                ],
            },
            {
                "label": "1",
                "label_type": "number",
                "title": "Understand the rollout sequence",
                "bullets": [
                    ("Cohort selection", '"Who is in the first cohort and how were they selected?"'),
                    ("Selection bias", "If the first users were hand picked, early numbers will look artificially high"),
                    ("Generalizability", "Factor the selection method into the analysis so we do not over extrapolate"),
                    ("Analytics output", "Determines how to interpret early adoption data and whether results can be projected to the full customer base"),
                ],
                "how_to_say_it": '"Help me understand who is in the first cohort and how they were selected. If they are our most engaged customers, the early numbers will look great but may not generalize."',
            },
            {
                "label": "2",
                "label_type": "number",
                "title": "Define the activation moment",
                "bullets": [
                    ("Value moment", '"When does a user go from trying it out to this actually helps me?"'),
                    ("Specific action", "Define activation as the specific action that signals core value, not just logging in"),
                    ("Time to activation", "Track how long it takes users to reach that moment"),
                    ("Analytics output", "Produces the activation rate metric — the most important leading indicator of retention"),
                ],
                "how_to_say_it": '"What is the moment where a user goes from trying it out to this actually helps me? I want to define activation as that specific action so we can measure time to activation."',
            },
            {
                "label": "3",
                "label_type": "number",
                "title": "Monitor the adoption funnel",
                "bullets": [
                    ("Funnel stages", "Eligible -> Exposed -> Activated -> Retained"),
                    ("Drop off analysis", "Where are users falling out and why"),
                    ("Segment splits", "Break the funnel by segment to see which groups move through and which stall"),
                    ("Analytics output", "Produces the adoption funnel analysis showing where the product is losing users"),
                ],
            },
            {
                "label": "4",
                "label_type": "number",
                "title": "Measure impact against baselines",
                "bullets": [
                    ("Before and after", "Compare each metric to the baseline from Validation"),
                    ("North Star movement", "Is the North Star moving in the right direction"),
                    ("Threshold check", "Are we above the minimum viable success threshold or below it"),
                    ("Analytics output", "Produces the impact report comparing actuals to success thresholds — the core input to the expand/iterate/pause decision"),
                ],
            },
            {
                "label": "5",
                "label_type": "number",
                "title": "Set guardrail alerts",
                "bullets": [
                    ("Pause triggers", '"What would make you say stop, let us figure this out before we expand?"'),
                    ("Automated alerts", "Set up real time notifications on those exact thresholds"),
                    ("Real time vs monthly", "Catch problems in real time instead of discovering them in a monthly review"),
                    ("Analytics output", "Produces the guardrail monitoring system that protects the product from silent failures"),
                ],
                "how_to_say_it": '"If something goes wrong after launch, what would make you say stop, let us figure this out before we expand? I want to set up automated alerts on those exact thresholds."',
            },
            {
                "label": "6",
                "label_type": "number",
                "title": "Frame the expand, iterate, or pause decision",
                "bullets": [
                    ("Decision criteria", "Activation rate, North Star movement, and guardrail health"),
                    ("Agree upfront", "Align with the PM now on what data will drive the call"),
                    ("Recommendation format", "Present the data with a clear recommendation: expand, iterate on specific issues, or pause"),
                    ("Analytics output", "Produces the expand/iterate/pause recommendation — the highest impact deliverable of the entire Rollout phase"),
                ],
                "how_to_say_it": '"After the first cohort has been live for four weeks, we will need to decide whether to expand. Can we agree now on what data will drive that decision?"',
            },
            {
                "label": "BRIDGE",
                "label_type": "bridge",
                "title": "Bridge to next phase",
                "bullets": [
                    ("Scale preview", '"Once the product proves it works in the first cohorts, Scale is where we ask the harder questions: will it keep working as we grow, which segments should we expand to next, and does it have real product-market fit."'),
                ],
            },
        ],
    },
    "scale": {
        "title": "Speaking Outline: Scale Conversation",
        "sections": [
            {
                "label": "OPEN",
                "label_type": "open",
                "title": "Transition from Rollout and frame Scale",
                "bullets": [
                    ("Recap handoff", '"Rollout showed us adoption, activation, and impact data. The product is working. Now we ask the harder questions: will it keep working as we grow, where do we expand, and does it have real product-market fit?"'),
                    ("Purpose of Scale", '"Scale is about optimizing what works, growing into new segments, monitoring long term health, and being honest about whether the product should continue at all."'),
                    ("Warning signs", "Retention flattens or declines across cohorts, the North Star stops improving, or the product only works in cherry picked segments and cannot generalize"),
                    ("Downstream inputs", "Scale is the final phase — its outputs are strategic decisions about continued investment, expansion, optimization, or sunsetting"),
                ],
            },
            {
                "label": "ACT",
                "label_type": "action",
                "title": "Actions",
                "bullets": [
                    ("Share screen", "Open the product-market fit scorecard or retention dashboard"),
                    ("Threshold reference", "Pull up the kill/pivot thresholds from Validation"),
                    ("Segment comparison", "Show a view with segment level performance side by side"),
                ],
            },
            {
                "label": "1",
                "label_type": "number",
                "title": "Review segment performance",
                "bullets": [
                    ("Segment splits", '"Which segments retain, which expand, and which churn?"'),
                    ("Alignment check", "Does the data match what PM is hearing from customers and sales"),
                    ("Surface tension", "If data says segment A is thriving and segment B is churning but the team wants to invest in B, present that tension directly"),
                    ("Analytics output", "Produces the segment performance report that determines where to invest and where to pull back"),
                ],
                "how_to_say_it": '"Here is what the data shows: segment A retains at 40% and delivers $X value, segment B retains at 12%. I want to check whether that matches what you are hearing from customers and sales."',
            },
            {
                "label": "2",
                "label_type": "number",
                "title": "Identify the growth engine",
                "bullets": [
                    ("Growth source", '"Are we growing by getting more value from existing customers or by reaching new ones?"'),
                    ("Expansion path", "If existing — feature adoption and upsell propensity analysis"),
                    ("New segments", "If new — Ideal Customer Profile scoring and adjacent market sizing"),
                    ("Analytics output", "Produces the growth analysis that determines the expansion strategy"),
                ],
                "how_to_say_it": '"Are we growing by getting more value out of existing customers, or by reaching new ones? I can build the analysis either way, but the data I pull and the models I build are different."',
            },
            {
                "label": "3",
                "label_type": "number",
                "title": "Assess product-market fit",
                "bullets": [
                    ("Retention curves", "Are retention curves flattening (good) or declining (bad) across cohorts"),
                    ("North Star trend", "Is the North Star still improving as the customer base expands"),
                    ("Segment consistency", "Does it work across multiple segments or only in cherry picked ones"),
                    ("Analytics output", "Produces the product-market fit scorecard — the highest stakes deliverable of the entire lifecycle"),
                ],
            },
            {
                "label": "4",
                "label_type": "number",
                "title": "Monitor model health (AI products)",
                "bullets": [
                    ("Drift detection", "Model performance degrades over time as the customer base changes"),
                    ("Accuracy tracking", "Track precision, recall, and acceptance rate over time"),
                    ("Retraining plan", "Who owns the decision to retrain, and how quickly can they act"),
                    ("Analytics output", "Produces the model monitoring dashboard and drift alerts"),
                ],
                "how_to_say_it": '"The model accuracy metrics are stable now, but drift is inevitable as the customer base changes. Do we have a plan for when and how to retrain?"',
            },
            {
                "label": "5",
                "label_type": "number",
                "title": "Revisit kill and pivot thresholds",
                "bullets": [
                    ("Threshold check", '"We set kill/pivot thresholds back in Validation. Are we above or below them?"'),
                    ("Honest conversation", "If below thresholds in certain segments, are we still willing to act on them"),
                    ("Sunk cost defense", "Have this conversation before the data forces it, when objectivity is easier"),
                    ("Analytics output", "Produces the continue/pivot/stop recommendation backed by thresholds the team agreed on before they were emotionally invested"),
                ],
                "how_to_say_it": '"We set kill/pivot thresholds back in Validation. I want to check in on those. If the data shows we are below those thresholds in certain segments, are we still willing to act on them?"',
            },
            {
                "label": "CLOSING",
                "label_type": "bridge",
                "title": "Closing",
                "bullets": [
                    ("Full circle", '"This brings us full circle through all five phases: we discovered the opportunity, validated what success looks like, built the tracking, measured real world impact, and now have the data to make strategic decisions about where to grow, what to optimize, and whether to continue."'),
                ],
            },
        ],
    },
}


# ============================================================
# Phase Sub-Steps (decomposed practice fields per phase)
# ============================================================

PHASE_SUBSTEPS = {
    "discovery": {
        "phase_title": "Phase 1: Discovery — Size the Opportunity",
        "phase_color": "#2E86AB",
        "phase_bg": "#e8f4f8",
        "steps": [
            {
                "id": "context",
                "title": "Clarify the Context",
                "icon": "1",
                "instruction": "Is this an existing product or a net new product? What problem are we solving and for whom? How are customers solving it today?",
                "hint": "This determines everything else. Existing product = internal data available. Net new = rely on external evidence. Name the specific problem and who has it.",
                "rubric_focus": "Correctly identifies product type (new vs existing), names specific problem, identifies affected users.",
            },
            {
                "id": "market_sizing",
                "title": "Market Sizing",
                "icon": "2",
                "instruction": "How big is the opportunity? Use both top-down and bottom-up methods. What is the TAM, SAM, and SOM?",
                "hint": "Top-down: Total Market x Segment % x Capture %. Bottom-up: Count real target customers x realistic revenue per customer. Show both side by side.",
                "rubric_focus": "Uses both sizing methods, names specific numbers or estimation approach, acknowledges uncertainty ranges.",
            },
            {
                "id": "segmentation",
                "title": "Customer Segmentation",
                "icon": "3",
                "instruction": "Who are the customer segments? How would you rank them? What axes predict the most value (pain severity, company size, workflow complexity)?",
                "hint": "Group by what predicts value. Rank each segment by need x readiness x revenue. Sketch a prioritization matrix.",
                "rubric_focus": "Defines segments with clear criteria, ranks by meaningful dimensions, identifies which segment to target first.",
            },
            {
                "id": "conversion_gaps",
                "title": "Conversion Gap Analysis",
                "icon": "4",
                "instruction": "Where do users start an action but not finish it today? (Existing platform only — skip if net new product.) What do high and low gaps tell you?",
                "hint": "Formula: (Eligible Users - Users Who Completed) / Eligible Users x 100 = Gap %. High gap = demand exists but something blocks completion. Low gap = current experience works.",
                "rubric_focus": "Correctly applies conversion gap only to existing products, identifies specific drop-off points, interprets what gaps mean.",
            },
            {
                "id": "competitive",
                "title": "Competitive Landscape",
                "icon": "5",
                "instruction": "Who are the direct competitors? What indirect alternatives exist (spreadsheets, manual processes)? Where is the whitespace — where nobody serves customers well?",
                "hint": "Map both obvious competitors and workarounds. Identify which competitive gaps align with your strongest segments.",
                "rubric_focus": "Names specific competitors and alternatives, identifies whitespace, connects competitive gaps to segments.",
            },
            {
                "id": "tradeoffs",
                "title": "Trade-offs",
                "icon": "⚖",
                "instruction": "What are the key trade-offs in this phase? (Go big vs go focused? Move fast vs research first?)",
                "hint": "Bigger market = harder to serve but more upside. Narrow market = easier to win but may lack scale. Moving fast risks building wrong thing; researching too long risks competitor launch.",
                "rubric_focus": "Identifies relevant trade-offs for the scenario, explains both sides, takes a position with reasoning.",
            },
            {
                "id": "warning_signs",
                "title": "Warning Signs and Go/No-Go",
                "icon": "🚨",
                "instruction": "What signals would tell you to stop before investing engineering resources? What would a go signal look like? What would a no-go signal look like?",
                "hint": "No-go signals: TAM smaller than estimated, no underserved segment found, competitive landscape has no whitespace. Go signals: Clear segment with strong need, addressable market large enough, competitive gaps align with team strengths.",
                "rubric_focus": "Defines specific go and no-go criteria, names concrete thresholds, does not skip the possibility of stopping.",
            },
            {
                "id": "speaking",
                "title": "Speaking Practice: Full Discovery Conversation",
                "icon": "🎙",
                "instruction": "Record or type your full Discovery conversation as if you are presenting to the interviewer. Walk through all the points above in a coherent flow.",
                "hint": "Start by framing the 5-phase method, then transition to Discovery. Cover context, market sizing, segmentation, conversion gaps, competitive landscape, and go/no-go. End with a bridge to Validation.",
                "rubric_focus": "Covers all Discovery elements in a coherent flow, uses clear transitions, demonstrates structured thinking, maintains conversational tone.",
                "is_speaking": True,
            },
        ],
    },
    "validation": {
        "phase_title": "Phase 2: Validation — Define and Measure Success",
        "phase_color": "#F18F01",
        "phase_bg": "#fff7eb",
        "steps": [
            {
                "id": "north_star",
                "title": "Define the North Star Metric",
                "icon": "1",
                "instruction": "What is the single metric that best captures whether this product is delivering real value to customers? Why this metric and not another?",
                "hint": "The North Star must reflect customer value (not vanity), be measurable, lead revenue, and be moveable by the team. Test: if it doubles, does leadership care? If it drops to zero, is the product a failure?",
                "rubric_focus": "North Star is specific and measurable, tied to customer value not activity, explains why this metric was chosen over alternatives.",
            },
            {
                "id": "metrics_tree",
                "title": "Build the Metrics Tree",
                "icon": "2",
                "instruction": "What 3-5 input metrics drive the North Star? Express it as a formula or hierarchy. Which are leading indicators (move fast) and which are lagging (confirm over time)?",
                "hint": "Universal structure: North Star = Reach x Activation x Engagement x Value per Engagement. Label each driver as leading or lagging. Each branch maps to a specific event the tracking plan must support.",
                "rubric_focus": "Builds logical tree where inputs clearly drive the North Star, distinguishes leading from lagging indicators, each metric is measurable.",
            },
            {
                "id": "baselines",
                "title": "Establish Baselines",
                "icon": "3",
                "instruction": "What are the current 'before' numbers for each key metric? Do we already track them, or do we need to build that measurement before launch? How do baselines differ by segment?",
                "hint": "Every impact claim needs a before number. If no baseline exists, build the measurement before launch. Baselines may differ by segment — measure each separately.",
                "rubric_focus": "Plans to measure baselines before launch, identifies which metrics already exist vs need to be built, considers segment-level variation.",
            },
            {
                "id": "success_thresholds",
                "title": "Success Thresholds",
                "icon": "4",
                "instruction": "What are the minimum viable success targets (floor) and aspirational targets (stretch)? How did you set these — baselines, benchmarks, or both?",
                "hint": "Set two targets per metric: minimum (must clear to justify investment) and aspirational (what great looks like). Ground them in baselines and industry benchmarks, not gut feel. Different segments may need different thresholds.",
                "rubric_focus": "Sets both minimum and aspirational targets, grounds them in data not gut feel, explains reasoning behind specific thresholds.",
            },
            {
                "id": "kill_pivot",
                "title": "Kill and Pivot Criteria",
                "icon": "5",
                "instruction": "At what specific thresholds would you recommend stopping or pivoting? Why is it important to set these before launch?",
                "hint": "Example: 'If Week-4 retention is below X%, or North Star does not move by Y% within 3 cohorts, trigger formal review.' Set now while team is objective — before sunk costs cloud judgment.",
                "rubric_focus": "Defines explicit numeric thresholds, explains why setting them pre-launch matters, gets leadership sign-off.",
            },
            {
                "id": "guardrails",
                "title": "Guardrail Metrics",
                "icon": "6",
                "instruction": "What metrics must NOT get worse when the product launches? (False positive rate, user complaints, latency, compliance metrics, etc.)",
                "hint": "Guardrails protect against unintended side effects. The product might hit its North Star but break something else. Name specific guardrails relevant to this scenario.",
                "rubric_focus": "Identifies scenario-relevant guardrails, explains what each protects against, sets thresholds for alerts.",
            },
            {
                "id": "tradeoffs",
                "title": "Trade-offs",
                "icon": "⚖",
                "instruction": "What are the key trade-offs? (Early signals vs proven results? Ambitious targets vs safe targets?)",
                "hint": "Activation signals are fast but can mislead. Revenue/retention signals are slow but definitive. Setting the bar too high = always looks like failure. Too low = declares success without solving the problem.",
                "rubric_focus": "Identifies relevant trade-offs, explains both sides, takes a position appropriate to the scenario.",
            },
            {
                "id": "warning_signs",
                "title": "Warning Signs",
                "icon": "🚨",
                "instruction": "What warning signs indicate the product concept itself is not viable? What would make you recommend not proceeding to Build?",
                "hint": "Red flags: team cannot agree on a North Star (concept too vague), baselines already high (little room to improve), leadership refuses to define kill criteria (planning to succeed regardless of data).",
                "rubric_focus": "Names specific warning signs for this scenario, connects each to a concrete consequence, does not skip the possibility of stopping.",
            },
            {
                "id": "speaking",
                "title": "Speaking Practice: Full Validation Conversation",
                "icon": "🎙",
                "instruction": "Record or type your full Validation conversation. Bridge from Discovery, walk through North Star, metrics tree, baselines, thresholds, kill criteria, and bridge to Build.",
                "hint": "Open with what Discovery handed off. Define the North Star first, then decompose it. Establish baselines, set thresholds, define kill criteria. End with what Build needs from you.",
                "rubric_focus": "Covers all Validation elements coherently, bridges from Discovery, demonstrates structured metrics thinking, maintains conversational tone.",
                "is_speaking": True,
            },
        ],
    },
    "build": {
        "phase_title": "Phase 3: Build — Instrument the Product",
        "phase_color": "#6c63ff",
        "phase_bg": "#f0eeff",
        "steps": [
            {
                "id": "user_journey",
                "title": "Map the User Journey to Events",
                "icon": "1",
                "instruction": "Walk through the ideal user journey step by step. What are the critical actions from first login through the core value moment?",
                "hint": "Every meaningful step needs a tracked event. If you miss something now, the data for early users who went through that flow is lost permanently.",
                "rubric_focus": "Maps a complete user journey, identifies all critical actions, notes where gaps would create blind spots.",
            },
            {
                "id": "event_taxonomy",
                "title": "Event Taxonomy Design",
                "icon": "2",
                "instruction": "What naming convention would you use? What properties should each event carry? What is the right level of granularity?",
                "hint": "Use object_action format (suggestion_displayed, suggestion_accepted). Attach segment identifiers to every event: customer tier, use case, company size. Separate events for distinct actions.",
                "rubric_focus": "Uses consistent naming convention, includes segment properties, appropriate granularity level, estimates event volumes.",
            },
            {
                "id": "dashboards",
                "title": "Dashboard Design",
                "icon": "3",
                "instruction": "What dashboards does the team need on day one? Who is the audience for each? What decisions does each dashboard support?",
                "hint": "Three dashboards minimum: Operational (engineering: uptime, latency, errors), Adoption (product team: active users, funnel), Outcomes (leadership: North Star, revenue impact). Build for decisions, not vanity.",
                "rubric_focus": "Plans dashboards for different audiences, each serves specific decisions, ready before launch not after.",
            },
            {
                "id": "data_quality",
                "title": "Data Quality Validation Plan",
                "icon": "4",
                "instruction": "How would you validate that tracking is correct before relying on it? What checks would you run?",
                "hint": "Check: events fire exactly once per action (not twice), all required properties are populated, test in staging before launch, validate volumes against expectations.",
                "rubric_focus": "Describes systematic validation approach, catches common issues (double-firing, missing properties), tests before launch.",
            },
            {
                "id": "engineering",
                "title": "Engineering Coordination",
                "icon": "5",
                "instruction": "How would you ensure tracking is treated as a launch requirement? What is the handoff process? For AI products, what model logging is needed?",
                "hint": "Tracking must be a blocker, not a nice-to-have. Know the cutoff date for handing engineering the plan. For AI: log model confidence, input features, user feedback on every suggestion.",
                "rubric_focus": "Treats tracking as launch blocker, coordinates timing, addresses AI model logging if applicable.",
            },
            {
                "id": "tradeoffs",
                "title": "Trade-offs",
                "icon": "⚖",
                "instruction": "What trade-offs exist in instrumentation? (Track everything vs limited engineering capacity? Real-time vs batch processing?)",
                "hint": "More events = better visibility but more engineering work. Address the scenario constraint directly (e.g., only 3 new events this quarter, 48-hour data lag).",
                "rubric_focus": "Identifies instrumentation trade-offs, addresses the scenario constraint directly, proposes a practical solution.",
            },
            {
                "id": "warning_signs",
                "title": "Warning Signs",
                "icon": "🚨",
                "instruction": "What signals indicate Build is going wrong? What would make you escalate?",
                "hint": "Red flags: engineering deprioritizes tracking, team cannot agree on which user actions matter, no time to test before launch, dashboards built after launch instead of before.",
                "rubric_focus": "Names specific Build-phase warning signs, connects each to downstream consequences, proposes mitigation.",
            },
            {
                "id": "speaking",
                "title": "Speaking Practice: Full Build Conversation",
                "icon": "🎙",
                "instruction": "Record or type your full Build conversation. Bridge from Validation, walk through event taxonomy, dashboards, data quality, engineering coordination, and bridge to Rollout.",
                "hint": "Open with what Validation defined. Show the metrics tree drives the event taxonomy. Walk through dashboards by audience. Cover data quality. End with readiness for Rollout.",
                "rubric_focus": "Covers all Build elements coherently, bridges from Validation, demonstrates practical instrumentation thinking, maintains conversational tone.",
                "is_speaking": True,
            },
        ],
    },
    "rollout": {
        "phase_title": "Phase 4: Rollout — Measure Real-World Impact",
        "phase_color": "#2CA58D",
        "phase_bg": "#e8f7f3",
        "steps": [
            {
                "id": "rollout_sequence",
                "title": "Rollout Sequence and Selection Bias",
                "icon": "1",
                "instruction": "Who gets the product first? How were they selected? How does the selection method affect how you interpret early data?",
                "hint": "If the first cohort was hand-picked (most engaged, biggest accounts), early numbers will look artificially high. Factor selection into your analysis so you do not over-extrapolate.",
                "rubric_focus": "Identifies how the first cohort is selected, explains impact of selection bias, adjusts interpretation accordingly.",
            },
            {
                "id": "activation",
                "title": "Define the Activation Moment",
                "icon": "2",
                "instruction": "What specific action signals that a user has truly experienced the product's core value? How would you measure time-to-activation?",
                "hint": "Activation is not 'logged in' or 'clicked around.' It is the specific action where the user goes from trying it out to this actually helps me. Track how long it takes to get there.",
                "rubric_focus": "Defines activation as a specific action tied to core value, not just usage, plans to measure time-to-activation.",
            },
            {
                "id": "experiment_method",
                "title": "Experimentation Method",
                "icon": "3",
                "instruction": "What methodology would you use to measure impact? (A/B test, pre/post, difference-in-differences, interrupted time series?) Why this method given the constraints?",
                "hint": "Match method to constraint. Cannot randomize? Use difference-in-differences or interrupted time series. Small user base? Consider sequential testing. The method must fit the scenario.",
                "rubric_focus": "Chooses method that fits the scenario constraint, explains why, acknowledges limitations of chosen method.",
            },
            {
                "id": "adoption_funnel",
                "title": "Adoption Funnel",
                "icon": "4",
                "instruction": "What does the adoption funnel look like? (Eligible → Exposed → Activated → Retained) Where do you expect the biggest drop-offs? How would you break it by segment?",
                "hint": "Track each stage. Identify where users fall out and why. Break by segment to see which groups move through and which stall.",
                "rubric_focus": "Maps complete funnel stages, identifies likely drop-off points, plans segment-level analysis.",
            },
            {
                "id": "impact_baselines",
                "title": "Impact vs Baselines and Thresholds",
                "icon": "5",
                "instruction": "How would you compare actual results to the baselines and success thresholds set in Validation? What does the comparison tell you?",
                "hint": "Compare each metric to its baseline (before number) and its threshold (target). Above minimum = continue. Below minimum = investigate. Above aspirational = celebrate and expand.",
                "rubric_focus": "Connects back to Validation baselines and thresholds, interprets results against pre-set criteria, draws clear conclusions.",
            },
            {
                "id": "guardrails",
                "title": "Guardrail Alerts",
                "icon": "6",
                "instruction": "What guardrail metrics are you monitoring? What thresholds trigger a pause? How would you set up real-time alerts?",
                "hint": "Ask: 'What would make you say stop before expanding?' Set automated alerts on those thresholds. Catch problems in real time, not monthly reviews.",
                "rubric_focus": "Sets up specific guardrail thresholds, plans real-time monitoring, defines what triggers a pause.",
            },
            {
                "id": "decision",
                "title": "Expand, Iterate, or Pause Decision",
                "icon": "7",
                "instruction": "Based on the data, what is your recommendation framework? What criteria drive expand vs iterate vs pause? How would you present this to the PM?",
                "hint": "Expand: North Star meets target, guardrails clean, >60% activation in 30 days. Iterate: Mixed signals. Pause: Guardrails breached, adoption flat. Pre-agree on criteria with PM.",
                "rubric_focus": "Defines clear criteria for each decision, presents recommendation format, pre-aligns with PM on decision drivers.",
            },
            {
                "id": "tradeoffs",
                "title": "Trade-offs",
                "icon": "⚖",
                "instruction": "What are the key trade-offs? (Wait for certainty vs decide now? Launch wide vs staged rollout? For AI: catch everything vs avoid false alarms?)",
                "hint": "95% certainty takes time; deciding early risks false positives. Wide launch captures market fast; staged catches problems early.",
                "rubric_focus": "Identifies relevant trade-offs, explains both sides, takes a position appropriate to the scenario and constraint.",
            },
            {
                "id": "warning_signs",
                "title": "Warning Signs",
                "icon": "🚨",
                "instruction": "What signals indicate Rollout is not going well? What would make you recommend pausing or rolling back?",
                "hint": "Red flags: activation rate below threshold, guardrail metrics breaching, early cohort not generalizing to later cohorts, North Star flat despite high usage.",
                "rubric_focus": "Names specific Rollout warning signs, connects each to a concrete action, does not skip the possibility of pausing.",
            },
            {
                "id": "speaking",
                "title": "Speaking Practice: Full Rollout Conversation",
                "icon": "🎙",
                "instruction": "Record or type your full Rollout conversation. Bridge from Build, walk through rollout sequence, activation, experimentation, funnel, impact, guardrails, and the expand/iterate/pause decision. Bridge to Scale.",
                "hint": "Open with what Build delivered. Cover the rollout sequence and selection bias. Define activation. Explain your method. Walk through the funnel and impact. Set guardrails. End with your recommendation framework.",
                "rubric_focus": "Covers all Rollout elements coherently, bridges from Build, demonstrates real-world measurement thinking, maintains conversational tone.",
                "is_speaking": True,
            },
        ],
    },
    "scale": {
        "phase_title": "Phase 5: Scale — Optimize and Expand",
        "phase_color": "#E15554",
        "phase_bg": "#fdeaea",
        "steps": [
            {
                "id": "segment_performance",
                "title": "Segment Performance Review",
                "icon": "1",
                "instruction": "Which segments retain and expand? Which churn? Does the data match what the PM is hearing from customers and sales?",
                "hint": "Present segment data directly. If data says segment A thrives and segment B churns but the team wants to invest in B, surface that tension. Do not bury bad news.",
                "rubric_focus": "Analyzes segments with specific metrics, surfaces misalignment between data and team assumptions, presents tension constructively.",
            },
            {
                "id": "growth_engine",
                "title": "Growth Engine Analysis",
                "icon": "2",
                "instruction": "Where does the next wave of growth come from? Expanding value in existing customers, or reaching new segments? What analysis supports each path?",
                "hint": "Expansion = feature adoption, upsell propensity. New segments = Ideal Customer Profile scoring, adjacent market sizing. The data you pull and models you build differ by path.",
                "rubric_focus": "Identifies growth path with reasoning, names specific analysis for that path, connects to the scenario.",
            },
            {
                "id": "pmf",
                "title": "Product-Market Fit Assessment",
                "icon": "3",
                "instruction": "Does this product have product-market fit? What signals tell you? (Retention curves, North Star trend, segment consistency, user sentiment)",
                "hint": "PMF signals: retention curves flattening (good) vs declining (bad), North Star still improving as customer base expands, works across multiple segments not just cherry-picked ones, positive NPS.",
                "rubric_focus": "Uses multiple PMF signals not just one, analyzes across segments, distinguishes real PMF from niche success.",
            },
            {
                "id": "model_health",
                "title": "Model Health Monitoring (AI Products)",
                "icon": "4",
                "instruction": "For AI products: Is model performance stable or drifting? What metrics track drift? Who owns the retraining decision and how quickly can they act?",
                "hint": "Track precision, recall, acceptance rate over time. Drift is inevitable as the customer base changes. There must be a retraining plan with clear ownership and response time.",
                "rubric_focus": "Tracks relevant model metrics, plans for drift detection, establishes retraining ownership and process.",
            },
            {
                "id": "kill_pivot_review",
                "title": "Kill/Pivot Threshold Review",
                "icon": "5",
                "instruction": "Revisit the thresholds set in Validation. Are we above or below them? Are we willing to act on them? What is the honest recommendation?",
                "hint": "This is the hardest conversation. If below thresholds, have the conversation before the data forces it. Sunk cost pressure makes it harder to be objective later.",
                "rubric_focus": "References Validation thresholds specifically, gives honest assessment, does not avoid the hard recommendation.",
            },
            {
                "id": "tradeoffs",
                "title": "Trade-offs",
                "icon": "⚖",
                "instruction": "What are the key trade-offs? (Retain existing vs acquire new? Deepen product vs broaden? Keep going vs shut down?)",
                "hint": "Retention improvement usually delivers more value per dollar than acquisition. Existing customers want advanced features; new segments want basic compatibility. Teams stay attached even when data says stop.",
                "rubric_focus": "Identifies relevant trade-offs, explains both sides, takes a position backed by the scenario data.",
            },
            {
                "id": "warning_signs",
                "title": "Warning Signs and Kill Signals",
                "icon": "🚨",
                "instruction": "What signals indicate the product should be narrowed, pivoted, or stopped entirely? What does 'continue and expand' look like vs 'narrow focus' vs 'kill'?",
                "hint": "Kill: retention declining all cohorts, North Star not moving after 3+ iterations, no segment shows above-average outcomes. Narrow: only 1-2 segments retaining. Continue: multiple segments retaining, North Star above target, positive NPS.",
                "rubric_focus": "Defines specific criteria for continue/narrow/kill, uses data thresholds not feelings, does not skip the kill option.",
            },
            {
                "id": "speaking",
                "title": "Speaking Practice: Full Scale Conversation",
                "icon": "🎙",
                "instruction": "Record or type your full Scale conversation. Bridge from Rollout, walk through segment performance, growth engine, PMF assessment, model health, and kill/pivot review. Close with the full-circle summary.",
                "hint": "Open with what Rollout showed. Review segments. Identify growth path. Assess PMF honestly. Check model health for AI. Revisit kill/pivot thresholds. Close by bringing the 5-phase lifecycle full circle.",
                "rubric_focus": "Covers all Scale elements coherently, bridges from Rollout, demonstrates honest assessment thinking, closes the lifecycle loop.",
                "is_speaking": True,
            },
        ],
    },
}


def score_substep(scenario, phase_id, substep, user_response):
    """Score a single sub-step response with targeted feedback."""
    if not _CLIENT:
        return None

    prompt = f"""SCENARIO:
{scenario['full_prompt']}

PHASE: {substep['title']} (part of {phase_id.title()} phase)
TASK: {substep['instruction']}
EVALUATION FOCUS: {substep['rubric_focus']}

CANDIDATE'S RESPONSE:
{user_response}

Give targeted feedback on this specific section in 2-3 sentences. Be specific about what was done well and what is missing. Use plain language. Do not use markdown formatting.

Then rate it 1-5 where:
- 1-2 = Missing key elements
- 3 = Covers basics but lacks specifics
- 4 = Strong with specific details
- 5 = Exceptional, nothing missing

Respond in this JSON format (no markdown, no code fences):
{{"score": 4, "feedback": "Your feedback here.", "missing": ["element 1"]}}"""

    text, latency = _call_claude(COACH_SYSTEM_PROMPT, prompt, max_tokens=400)
    parsed = _parse_json_response(text)
    if parsed:
        parsed["latency"] = latency
        return parsed
    return {"score": 0, "feedback": text or "Scoring failed.", "missing": [], "latency": latency}


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

FORMATTING RULES (very important):
- Use bullet points for every major idea. Do not write long paragraphs.
- Use plain, everyday language a 9th grader could understand. Spell out every term the first time you use it.
- When you mention a metric or method, add a short plain-English explanation in parentheses right after it.
- Organize bullets under short, clear labels like "Data I would gather:", "How I would size this:", "What good and bad signals look like:" etc.
- Do NOT use markdown formatting (no **bold**, no *italic*, no ## headings, no --- dividers).
- Keep it clean, scannable, and easy to read out loud."""

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
