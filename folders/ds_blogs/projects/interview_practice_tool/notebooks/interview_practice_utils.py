"""
Interview Practice Utilities for NB08 & NB09.

Provides:
- LLM client initialization (Claude, OpenAI, Gemini) with graceful fallback
- Scenario generation engine (company archetypes × product situations × constraints)
- Step-by-step scoring rubrics for the product analytics framework
- Multi-model consensus scoring
- Session data logging for the data-story analysis in NB09
"""

import os, re, json, random, time, hashlib
from datetime import datetime
from pathlib import Path
import pandas as pd

# ============================================================
# LLM Imports (optional — graceful fallback)
# ============================================================

try:
    import anthropic
    CLAUDE_AVAILABLE = True
except ImportError:
    CLAUDE_AVAILABLE = False

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    from google import genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

MODELS = {}


def init_llm_clients():
    """Initialize LLM clients from environment variables."""
    global MODELS
    MODELS = {
        'claude':  {'available': CLAUDE_AVAILABLE},
        'openai':  {'available': OPENAI_AVAILABLE},
        'gemini':  {'available': GEMINI_AVAILABLE},
    }
    if CLAUDE_AVAILABLE:
        MODELS['claude']['client'] = anthropic.Anthropic()
    if OPENAI_AVAILABLE:
        MODELS['openai']['client'] = OpenAI()
    if GEMINI_AVAILABLE:
        _key = os.environ.get('GOOGLE_API_KEY', '')
        if _key:
            MODELS['gemini']['client'] = genai.Client(api_key=_key)
        else:
            MODELS['gemini']['available'] = False

    avail = [m for m, v in MODELS.items() if v.get('available')]
    print(f"LLM models ready: {', '.join(avail) if avail else 'NONE — scoring will use placeholder feedback'}")
    return avail


def _call_model(model_name, prompt, max_tokens=800):
    """Unified LLM call. Returns (text, latency_seconds) or (None, 0)."""
    t0 = time.time()
    try:
        if model_name == 'claude' and MODELS.get('claude', {}).get('available'):
            client = MODELS['claude']['client']
            msg = client.messages.create(
                model='claude-sonnet-4-20250514',
                max_tokens=max_tokens,
                messages=[{'role': 'user', 'content': prompt}],
            )
            return msg.content[0].text, round(time.time() - t0, 2)
        elif model_name == 'openai' and MODELS.get('openai', {}).get('available'):
            client = MODELS['openai']['client']
            resp = client.chat.completions.create(
                model='gpt-4o-mini',
                max_tokens=max_tokens,
                messages=[{'role': 'user', 'content': prompt}],
            )
            return resp.choices[0].message.content, round(time.time() - t0, 2)
        elif model_name == 'gemini' and MODELS.get('gemini', {}).get('available'):
            client = MODELS['gemini']['client']
            resp = client.models.generate_content(
                model='gemini-2.5-flash',
                contents=prompt,
            )
            return resp.text, round(time.time() - t0, 2)
    except Exception as e:
        print(f"  ⚠ {model_name} error: {e}")
    return None, 0.0


# ============================================================
# Scenario Generation Engine
# ============================================================

COMPANY_ARCHETYPES = [
    {
        'type': 'Healthcare AI',
        'examples': ['MedAssist AI', 'ClinicalMind', 'DiagnosIQ', 'HealthLens AI', 'CareSignal'],
        'domain_context': 'Hospital systems, EHR integration, clinical workflows, regulatory compliance (HIPAA), physician adoption',
        'users': ['physicians', 'clinical coders', 'hospital administrators', 'CDI specialists', 'nurses'],
        'metrics_flavor': 'accuracy rates, chart review time saved, query response rates, denial rate reduction',
    },
    {
        'type': 'B2B SaaS',
        'examples': ['DataForge', 'SyncFlow', 'PipelineHQ', 'MetricStack', 'CloudNest'],
        'domain_context': 'Enterprise software, multi-seat contracts, onboarding complexity, integration with existing tools',
        'users': ['operations managers', 'data teams', 'IT administrators', 'executives', 'analysts'],
        'metrics_flavor': 'seat utilization, feature adoption, time-to-value, NRR, expansion revenue',
    },
    {
        'type': 'Consumer Marketplace',
        'examples': ['SwapLocal', 'SkillBridge', 'TrustLoop', 'GigNest', 'FreshFind'],
        'domain_context': 'Two-sided marketplace dynamics, supply/demand balance, trust & safety, geographic density',
        'users': ['buyers', 'sellers', 'freelancers', 'hosts', 'small business owners'],
        'metrics_flavor': 'GMV, take rate, liquidity, repeat transaction rate, time-to-first-match',
    },
    {
        'type': 'Fintech',
        'examples': ['LedgerAI', 'CashPulse', 'SpendSmart', 'VaultLine', 'PayNova'],
        'domain_context': 'Regulatory requirements, fraud detection, financial data sensitivity, trust building',
        'users': ['consumers', 'small business owners', 'accountants', 'financial advisors', 'compliance officers'],
        'metrics_flavor': 'transaction volume, fraud rate, approval rate, cost per acquisition, activation to first transaction',
    },
    {
        'type': 'Developer Tools',
        'examples': ['CodeRadar', 'DeployPilot', 'SchemaSync', 'TestForge', 'APIBridge'],
        'domain_context': 'Developer experience, API reliability, documentation quality, community adoption, open-source dynamics',
        'users': ['software engineers', 'DevOps teams', 'engineering managers', 'CTOs', 'technical architects'],
        'metrics_flavor': 'API calls per user, p99 latency, docs-to-first-call time, SDK adoption, community contributions',
    },
    {
        'type': 'EdTech',
        'examples': ['LearnLoop', 'SkillForge', 'ClassPilot', 'TutorMind', 'StudyArc'],
        'domain_context': 'Learning outcomes measurement, engagement vs. completion tension, institutional vs. consumer sales',
        'users': ['students', 'instructors', 'school administrators', 'corporate L&D managers', 'parents'],
        'metrics_flavor': 'course completion rate, assessment scores, time-to-proficiency, instructor engagement, renewal rate',
    },
]

PRODUCT_SITUATIONS = [
    {
        'id': 'new_product_launch',
        'label': 'New Product Launch',
        'scope': 'product',
        'description': 'The company is launching an entirely new product targeting a segment they haven\'t served before.',
        'emphasis_phases': ['discovery', 'validation'],
        'key_questions': 'Is there real demand? What does PMF look like? When do we kill vs. pivot?',
    },
    {
        'id': 'feature_expansion',
        'label': 'Feature Expansion to Adjacent Market',
        'scope': 'feature',
        'description': 'An existing successful product is adding a major feature to serve an adjacent user segment.',
        'emphasis_phases': ['build', 'rollout'],
        'key_questions': 'Will the new segment cannibalize existing users? How do we measure incremental value?',
    },
    {
        'id': 'retention_crisis',
        'label': 'Retention Crisis',
        'scope': 'product',
        'description': 'The product has strong acquisition but Week-4 retention has dropped 15 percentage points over two quarters.',
        'emphasis_phases': ['scale', 'rollout'],
        'key_questions': 'What cohorts are churning? Is this an onboarding or value-delivery problem? What experiments would you run?',
    },
    {
        'id': 'ai_accuracy_complaints',
        'label': 'AI Model Accuracy Complaints',
        'scope': 'feature',
        'description': 'Users report the AI suggestions are "wrong too often." NPS has dropped but usage remains stable.',
        'emphasis_phases': ['build', 'scale'],
        'key_questions': 'How do you measure "wrong"? Is this a precision or recall problem? Should you tighten confidence thresholds?',
    },
    {
        'id': 'onboarding_dropoff',
        'label': 'Onboarding Drop-off',
        'scope': 'feature',
        'description': 'Sign-ups are healthy but only 30% of new users complete onboarding to reach the "aha moment."',
        'emphasis_phases': ['rollout', 'validation'],
        'key_questions': 'Where in the funnel is the biggest drop? Is the "aha moment" correctly defined? What experiments?',
    },
    {
        'id': 'enterprise_self_serve_tension',
        'label': 'Enterprise vs. Self-Serve Tension',
        'scope': 'product',
        'description': 'The product has both enterprise and self-serve tiers. Enterprise revenue is 4× but self-serve has 20× the users.',
        'emphasis_phases': ['scale', 'discovery'],
        'key_questions': 'Where should the analytics team invest? How do you measure ROI across such different segments?',
    },
    {
        'id': 'international_expansion',
        'label': 'International Market Expansion',
        'scope': 'product',
        'description': 'The product is expanding from the US to three new markets with different regulatory and cultural contexts.',
        'emphasis_phases': ['discovery', 'rollout'],
        'key_questions': 'Can you A/B test across markets? How do you define PMF per market? What guardrails differ?',
    },
    {
        'id': 'pricing_model_change',
        'label': 'Pricing Model Redesign',
        'scope': 'feature',
        'description': 'The company wants to shift from per-seat to usage-based pricing. Current ARR is $20M.',
        'emphasis_phases': ['validation', 'rollout'],
        'key_questions': 'How do you model revenue impact before launching? What does a safe rollout look like? Guardrails?',
    },
]

CONSTRAINT_TWISTS = [
    'Engineering capacity is limited — you can only instrument 3 new events this quarter.',
    'The CEO wants results in 6 weeks, not the usual 3-month roadmap.',
    'You cannot randomize users for A/B testing due to regulatory constraints — you need quasi-experimental methods.',
    'The data warehouse has a 48-hour lag, so real-time dashboards are not feasible.',
    'Two executives disagree on the North Star metric — one wants revenue, the other wants engagement.',
    'Your user base is small (< 5,000 monthly actives), so statistical power is a real concern.',
    'The product serves both internal users (employees) and external users (customers) with very different needs.',
    'Historical data only goes back 4 months — there\'s no long-term baseline.',
    'A competitor just launched a similar feature, creating urgency to ship before the next quarter.',
    'The sales team is promising features to prospects that haven\'t been validated with analytics.',
]


def generate_scenario(scope_filter=None, seed=None):
    """
    Generate a random case-study scenario.

    Parameters
    ----------
    scope_filter : str or None
        'product' for new product scenarios, 'feature' for feature scenarios, None for any.
    seed : int or None
        For reproducibility.

    Returns
    -------
    dict with keys: company, archetype, situation, constraint, scope, full_prompt, scenario_id
    """
    rng = random.Random(seed)

    archetype = rng.choice(COMPANY_ARCHETYPES)
    situations = PRODUCT_SITUATIONS
    if scope_filter:
        situations = [s for s in situations if s['scope'] == scope_filter]
    situation = rng.choice(situations)
    constraint = rng.choice(CONSTRAINT_TWISTS)
    company_name = rng.choice(archetype['examples'])

    user_type = rng.choice(archetype['users'])

    full_prompt = (
        f"**Company:** {company_name} — a {archetype['type'].lower()} company.\n\n"
        f"**Context:** {archetype['domain_context']}.\n\n"
        f"**Situation:** {situation['description']} "
        f"The primary users affected are {user_type}.\n\n"
        f"**Constraint:** {constraint}\n\n"
        f"**Key questions to address:** {situation['key_questions']}"
    )

    scenario_id = hashlib.md5(full_prompt.encode()).hexdigest()[:8]

    return {
        'scenario_id': scenario_id,
        'company_name': company_name,
        'archetype_type': archetype['type'],
        'archetype_metrics': archetype['metrics_flavor'],
        'situation_id': situation['id'],
        'situation_label': situation['label'],
        'scope': situation['scope'],
        'emphasis_phases': situation['emphasis_phases'],
        'constraint': constraint,
        'user_type': user_type,
        'full_prompt': full_prompt,
    }


# ============================================================
# Framework Steps & Scoring Rubrics
# ============================================================

FRAMEWORK_STEPS = [
    {
        'step_num': 1,
        'step_name': 'Clarifying Questions',
        'instruction': (
            'Before diving into analytics, what questions would you ask the PM or stakeholder '
            'to scope this problem? List 3-5 questions and explain why each matters.'
        ),
        'rubric': {
            'specificity': 'Questions are specific to this scenario, not generic.',
            'coverage': 'Questions span user needs, data availability, success criteria, and constraints.',
            'prioritization': 'Most important questions are listed first with reasoning.',
            'domain_awareness': 'Questions reflect understanding of the industry context.',
        },
        'strong_answer_traits': 'Asks about existing data infrastructure, current baselines, stakeholder alignment on success definition, user research available.',
        'common_mistakes': 'Asking generic questions that could apply to any product. Forgetting to ask about data availability. Not prioritizing.',
    },
    {
        'step_num': 2,
        'step_name': 'Discovery & Opportunity Sizing',
        'instruction': (
            'How would you approach discovery analytics for this scenario? Describe what data '
            'you would gather, how you would size the opportunity, and what signals would indicate '
            'this is worth pursuing.'
        ),
        'rubric': {
            'data_sources': 'Identifies specific data sources (internal logs, surveys, market research, competitive analysis).',
            'sizing_method': 'Proposes a concrete method for opportunity sizing (TAM/SAM/SOM, usage proxy, revenue model).',
            'go_no_go_signals': 'Defines what "good" and "bad" signals would look like before committing resources.',
            'feasibility': 'Considers technical and organizational feasibility.',
        },
        'strong_answer_traits': 'Names actual metrics. Connects sizing to revenue or usage impact. Acknowledges uncertainty ranges.',
        'common_mistakes': 'Jumping to solutions without sizing. Ignoring competitive landscape. Not defining failure criteria early.',
    },
    {
        'step_num': 3,
        'step_name': 'Metrics Definition',
        'instruction': (
            'Define the analytics framework for this scenario. What is the North Star metric? '
            'What input metrics feed it? What guardrail metrics would you track? '
            'Organize this as a metrics tree.'
        ),
        'rubric': {
            'north_star_clarity': 'North Star is specific, measurable, and tied to user value — not a vanity metric.',
            'input_metrics': 'Identifies 3-5 input metrics that are leading indicators of the North Star.',
            'guardrails': 'Defines guardrail metrics that would flag unintended negative consequences.',
            'measurability': 'All metrics could actually be instrumented with reasonable engineering effort.',
            'hierarchy': 'Metrics form a logical tree where inputs clearly drive the North Star.',
        },
        'strong_answer_traits': 'Explains WHY each metric matters. Distinguishes leading from lagging indicators. Addresses trade-offs between metrics.',
        'common_mistakes': 'Choosing revenue as North Star when engagement is the real lever. Forgetting guardrails. Listing metrics without hierarchy.',
    },
    {
        'step_num': 4,
        'step_name': 'Experiment & Rollout Design',
        'instruction': (
            'Design the rollout and experimentation plan. How would you test this? What methodology '
            '(A/B test, quasi-experiment, phased rollout)? Define success criteria, sample size '
            'considerations, and what would make you stop the experiment.'
        ),
        'rubric': {
            'methodology_fit': 'Chosen method matches the scenario constraints (e.g., uses DiD if randomization impossible).',
            'sample_size_awareness': 'Discusses statistical power and practical sample size requirements.',
            'success_criteria': 'Pre-defines what "success" looks like with specific thresholds.',
            'kill_criteria': 'Defines what would cause an early stop — guardrail violations, harm signals.',
            'rollout_phases': 'Plans a phased approach (internal → beta → staged → GA) with gate criteria.',
        },
        'strong_answer_traits': 'Acknowledges power limitations. Plans for edge cases. Mentions network effects or contamination risks.',
        'common_mistakes': 'Defaulting to A/B test when randomization isn\'t possible. No power analysis. No kill criteria.',
    },
    {
        'step_num': 5,
        'step_name': 'Scale & Retention Analytics',
        'instruction': (
            'Assuming initial rollout succeeds, how would you approach scale analytics? '
            'Describe your cohort analysis strategy, retention framework, and how you would '
            'identify product-market fit signals. What would make you recommend continuing, '
            'pivoting, or discontinuing?'
        ),
        'rubric': {
            'cohort_strategy': 'Plans meaningful cohort segmentation (time, behavior, segment) with clear rationale.',
            'retention_framework': 'Describes specific retention curves and benchmarks for this product type.',
            'pmf_signals': 'Identifies concrete PMF signals beyond "retention is good" — engagement depth, organic growth, willingness to pay.',
            'kill_pivot_criteria': 'Defines thresholds that trigger a discontinue/pivot conversation with leadership.',
        },
        'strong_answer_traits': 'Connects cohort insights to product decisions. Names PMF benchmarks relevant to the industry. Plans for honest PMF assessment.',
        'common_mistakes': 'Vague "we\'d look at retention." No PMF framework. Doesn\'t address what happens if metrics are bad.',
    },
    {
        'step_num': 6,
        'step_name': 'Trade-off Analysis',
        'instruction': (
            'Identify the 2-3 most important trade-offs in this scenario. For each, explain '
            'the tension, what data you\'d use to navigate it, and how you would frame the '
            'decision for leadership.'
        ),
        'rubric': {
            'identification': 'Correctly identifies real trade-offs inherent in this scenario — not invented ones.',
            'data_framing': 'Proposes specific data/analysis to quantify each side of the trade-off.',
            'stakeholder_communication': 'Frames trade-offs in terms leadership can act on — not just analytics jargon.',
            'recommendation_stance': 'Takes a defensible position rather than just presenting both sides passively.',
        },
        'strong_answer_traits': 'Uses "if X then Y, but at the cost of Z" framing. Proposes how to measure the trade-off. Acknowledges reversibility.',
        'common_mistakes': 'Presenting trade-offs without data. Being passive ("it depends"). Missing the biggest trade-off for the scenario.',
    },
    {
        'step_num': 7,
        'step_name': 'Executive Summary & Recommendation',
        'instruction': (
            'Synthesize your analysis into a 3-5 sentence executive recommendation. '
            'What should the company do, what would you measure to know it\'s working, '
            'and what\'s the biggest risk?'
        ),
        'rubric': {
            'clarity': 'Recommendation is specific and actionable — a PM could execute on it.',
            'evidence_grounding': 'Connects back to the metrics and analysis described in previous steps.',
            'risk_awareness': 'Names the single biggest risk and how to mitigate it.',
            'conciseness': 'Delivers the full recommendation in 3-5 sentences — not a wall of text.',
        },
        'strong_answer_traits': 'Starts with the recommendation, not the analysis. Quantifies expected impact. Names the next decision point.',
        'common_mistakes': 'Summarizing the process instead of making a recommendation. Being vague. Forgetting risk.',
    },
]


# ============================================================
# Scoring Engine
# ============================================================

def _build_scoring_prompt(scenario, step, user_response):
    """Build the LLM scoring prompt for a given step."""
    rubric_text = '\n'.join(
        f"  - {dim}: {desc}" for dim, desc in step['rubric'].items()
    )

    prompt = f"""You are an expert product analytics interviewer evaluating a candidate's response.

SCENARIO:
{scenario['full_prompt']}

FRAMEWORK STEP: Step {step['step_num']} — {step['step_name']}
TASK: {step['instruction']}

SCORING RUBRIC (rate each dimension 1-5):
{rubric_text}

WHAT A STRONG ANSWER LOOKS LIKE:
{step['strong_answer_traits']}

COMMON MISTAKES TO WATCH FOR:
{step['common_mistakes']}

CANDIDATE'S RESPONSE:
{user_response}

INSTRUCTIONS:
1. Score each rubric dimension from 1 (poor) to 5 (excellent).
2. Provide a composite score (average of dimensions, rounded to 1 decimal).
3. Write 2-3 sentences of specific, constructive feedback referencing the scenario.
4. Identify one specific strength and one specific area for improvement.

Respond in EXACTLY this JSON format (no markdown, no code fences):
{{
  "scores": {{"dimension_name": score, ...}},
  "composite": 3.5,
  "feedback": "Your specific feedback here.",
  "strength": "One thing done well.",
  "improvement": "One thing to work on."
}}"""
    return prompt


def _parse_score_response(text):
    """Parse JSON from LLM response, handling markdown fences."""
    if text is None:
        return None
    # Strip markdown code fences if present
    text = re.sub(r'^```(?:json)?\s*', '', text.strip())
    text = re.sub(r'\s*```$', '', text.strip())
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None


def score_response(scenario, step, user_response):
    """
    Score a user's response using all available LLMs.

    Returns
    -------
    dict with keys:
        model_results : dict  — per-model parsed scores
        consensus : dict — averaged composite + merged feedback
        raw_responses : dict — raw text from each model
        latencies : dict — response time per model
    """
    prompt = _build_scoring_prompt(scenario, step, user_response)

    model_results = {}
    raw_responses = {}
    latencies = {}

    avail = [m for m, v in MODELS.items() if v.get('available')]
    if not avail:
        # Placeholder when no LLMs available
        return {
            'model_results': {},
            'consensus': {
                'composite': 0.0,
                'feedback': '⚠ No LLM models available. Configure API keys to enable scoring.',
                'strength': 'N/A',
                'improvement': 'N/A',
                'scores': {},
            },
            'raw_responses': {},
            'latencies': {},
        }

    for model_name in avail:
        text, latency = _call_model(model_name, prompt, max_tokens=600)
        raw_responses[model_name] = text
        latencies[model_name] = latency
        parsed = _parse_score_response(text)
        if parsed:
            model_results[model_name] = parsed

    # Build consensus
    consensus = _build_consensus(model_results)

    return {
        'model_results': model_results,
        'consensus': consensus,
        'raw_responses': raw_responses,
        'latencies': latencies,
    }


def _build_consensus(model_results):
    """Average scores across models, pick best feedback."""
    if not model_results:
        return {
            'composite': 0.0,
            'feedback': 'No models returned valid scores.',
            'strength': 'N/A', 'improvement': 'N/A', 'scores': {},
        }

    # Average composite
    composites = [r.get('composite', 0) for r in model_results.values() if r.get('composite')]
    avg_composite = round(sum(composites) / len(composites), 1) if composites else 0.0

    # Average per-dimension scores
    all_dims = set()
    for r in model_results.values():
        if r.get('scores'):
            all_dims.update(r['scores'].keys())

    avg_scores = {}
    for dim in all_dims:
        vals = [r['scores'][dim] for r in model_results.values()
                if r.get('scores') and dim in r['scores']]
        avg_scores[dim] = round(sum(vals) / len(vals), 1) if vals else 0

    # Take the longest (most detailed) feedback
    feedbacks = [(r.get('feedback', ''), m) for m, r in model_results.items()]
    best_feedback = max(feedbacks, key=lambda x: len(x[0]))[0] if feedbacks else ''

    strengths = [r.get('strength', '') for r in model_results.values() if r.get('strength')]
    improvements = [r.get('improvement', '') for r in model_results.values() if r.get('improvement')]

    return {
        'composite': avg_composite,
        'scores': avg_scores,
        'feedback': best_feedback,
        'strength': max(strengths, key=len) if strengths else 'N/A',
        'improvement': max(improvements, key=len) if improvements else 'N/A',
        'model_agreement': _calc_agreement(model_results),
    }


def _calc_agreement(model_results):
    """Calculate inter-model agreement (std dev of composites)."""
    composites = [r.get('composite', 0) for r in model_results.values() if r.get('composite')]
    if len(composites) < 2:
        return {'std_dev': 0.0, 'n_models': len(composites)}
    mean = sum(composites) / len(composites)
    variance = sum((c - mean) ** 2 for c in composites) / len(composites)
    return {
        'std_dev': round(variance ** 0.5, 2),
        'n_models': len(composites),
        'range': round(max(composites) - min(composites), 1),
    }


# ============================================================
# Session Logging (for NB09 data story)
# ============================================================

_SESSION_LOG = []   # in-memory buffer
_OUTPUTS_DIR = None


def init_session_logger(outputs_dir):
    """Set the output directory for session logs."""
    global _OUTPUTS_DIR
    _OUTPUTS_DIR = outputs_dir
    os.makedirs(outputs_dir, exist_ok=True)


def log_step_result(session_id, scenario, step, user_response, score_result, time_spent_sec=None):
    """Log a single step result for later analysis."""
    record = {
        'session_id': session_id,
        'timestamp': datetime.now().isoformat(),
        'scenario_id': scenario['scenario_id'],
        'archetype': scenario['archetype_type'],
        'situation': scenario['situation_label'],
        'scope': scenario['scope'],
        'constraint': scenario['constraint'],
        'step_num': step['step_num'],
        'step_name': step['step_name'],
        'user_response_length': len(user_response),
        'user_response': user_response,
        'composite_score': score_result['consensus']['composite'],
        'time_spent_sec': time_spent_sec,
    }

    # Per-model details
    for model_name, result in score_result.get('model_results', {}).items():
        record[f'{model_name}_composite'] = result.get('composite', None)
        record[f'{model_name}_latency'] = score_result.get('latencies', {}).get(model_name, None)
        record[f'{model_name}_feedback'] = result.get('feedback', '')
        # Per-dimension scores
        for dim, val in result.get('scores', {}).items():
            record[f'{model_name}_{dim}'] = val

    # Consensus dimension scores
    for dim, val in score_result['consensus'].get('scores', {}).items():
        record[f'consensus_{dim}'] = val

    # Agreement stats
    agreement = score_result['consensus'].get('model_agreement', {})
    record['agreement_std_dev'] = agreement.get('std_dev', None)
    record['agreement_range'] = agreement.get('range', None)
    record['n_models_scored'] = agreement.get('n_models', 0)

    _SESSION_LOG.append(record)
    return record


def save_session_log(filename=None):
    """Save accumulated session log to CSV."""
    if not _SESSION_LOG:
        print("No session data to save.")
        return None

    if filename is None:
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'practice_session_{ts}.csv'

    filepath = os.path.join(_OUTPUTS_DIR, filename)
    df = pd.DataFrame(_SESSION_LOG)
    df.to_csv(filepath, index=False)
    print(f"Session log saved: {filepath}  ({len(df)} step records)")
    return filepath


def load_all_sessions(outputs_dir=None):
    """Load all saved session CSVs into one DataFrame for NB09 analysis."""
    d = outputs_dir or _OUTPUTS_DIR
    files = sorted(Path(d).glob('practice_session_*.csv'))
    if not files:
        print("No session files found.")
        return pd.DataFrame()
    dfs = [pd.read_csv(f) for f in files]
    combined = pd.concat(dfs, ignore_index=True)
    print(f"Loaded {len(files)} session files → {len(combined)} step records")
    return combined


# ============================================================
# Display Helpers
# ============================================================

def format_scenario_display(scenario):
    """Return formatted HTML string for notebook display."""
    return f"""
<div style="background:#f0f7ff; border-left:4px solid #2563eb; padding:16px; border-radius:6px; margin:8px 0;">
  <h3 style="margin:0 0 8px 0; color:#1e40af;">🎯 Case Study Scenario</h3>
  <table style="border-collapse:collapse; width:100%;">
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top; white-space:nowrap;">Company</td>
        <td style="padding:4px 0;">{scenario['company_name']} — {scenario['archetype_type']}</td></tr>
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top;">Situation</td>
        <td style="padding:4px 0;">{scenario['situation_label']}</td></tr>
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top;">Scope</td>
        <td style="padding:4px 0;">{'🆕 New Product' if scenario['scope'] == 'product' else '🔧 Feature on Existing Product'}</td></tr>
    <tr><td style="padding:4px 12px 4px 0; font-weight:600; vertical-align:top;">Constraint</td>
        <td style="padding:4px 0; color:#b91c1c;">{scenario['constraint']}</td></tr>
  </table>
  <div style="margin-top:12px; padding:10px; background:#e0e7ff; border-radius:4px;">
    <strong>Key questions to address:</strong><br/>
    {scenario['full_prompt'].split('Key questions to address:**')[-1].strip()}
  </div>
</div>"""


def format_score_display(step, score_result):
    """Return formatted HTML for score feedback."""
    c = score_result['consensus']
    composite = c.get('composite', 0)

    # Color code
    if composite >= 4.0:
        color, bg, label = '#166534', '#dcfce7', 'Strong'
    elif composite >= 3.0:
        color, bg, label = '#854d0e', '#fef9c3', 'Developing'
    else:
        color, bg, label = '#991b1b', '#fee2e2', 'Needs Work'

    # Dimension bars
    dim_html = ''
    for dim, val in c.get('scores', {}).items():
        pct = val / 5 * 100
        dim_label = dim.replace('_', ' ').title()
        dim_html += f"""
        <div style="display:flex; align-items:center; margin:3px 0;">
          <span style="width:180px; font-size:13px;">{dim_label}</span>
          <div style="flex:1; background:#e5e7eb; border-radius:4px; height:16px; margin:0 8px;">
            <div style="width:{pct}%; background:{color}; height:16px; border-radius:4px;"></div>
          </div>
          <span style="font-size:13px; font-weight:600;">{val}/5</span>
        </div>"""

    # Model agreement
    agreement = c.get('model_agreement', {})
    n_models = agreement.get('n_models', 0)
    std_dev = agreement.get('std_dev', 0)
    agreement_note = ''
    if n_models >= 2:
        agreement_note = f'<div style="font-size:12px; color:#6b7280; margin-top:8px;">Models: {n_models} | Score spread: ±{std_dev}</div>'

    return f"""
<div style="background:{bg}; border-left:4px solid {color}; padding:16px; border-radius:6px; margin:8px 0;">
  <div style="display:flex; justify-content:space-between; align-items:center;">
    <h3 style="margin:0; color:{color};">Step {step['step_num']}: {step['step_name']}</h3>
    <span style="font-size:24px; font-weight:700; color:{color};">{composite}/5 — {label}</span>
  </div>
  <div style="margin:12px 0;">{dim_html}</div>
  <div style="margin-top:12px; padding:10px; background:white; border-radius:4px;">
    <strong>Feedback:</strong> {c.get('feedback', '')}
  </div>
  <div style="margin-top:8px; display:flex; gap:16px;">
    <div style="flex:1; padding:8px; background:white; border-radius:4px;">
      <strong style="color:#166534;">✓ Strength:</strong> {c.get('strength', '')}
    </div>
    <div style="flex:1; padding:8px; background:white; border-radius:4px;">
      <strong style="color:#b91c1c;">↗ Improve:</strong> {c.get('improvement', '')}
    </div>
  </div>
  {agreement_note}
</div>"""


def format_session_summary(session_scores):
    """Return HTML summary of all steps in a session."""
    if not session_scores:
        return '<p>No scores recorded yet.</p>'

    total = sum(s['composite'] for s in session_scores) / len(session_scores)
    rows = ''
    for s in session_scores:
        comp = s['composite']
        if comp >= 4.0:
            badge = '🟢'
        elif comp >= 3.0:
            badge = '🟡'
        else:
            badge = '🔴'
        rows += f'<tr><td style="padding:4px 8px;">{badge} Step {s["step_num"]}</td><td style="padding:4px 8px;">{s["step_name"]}</td><td style="padding:4px 8px; font-weight:600;">{comp}/5</td></tr>'

    return f"""
<div style="background:#f8fafc; border:1px solid #e2e8f0; padding:16px; border-radius:8px; margin:12px 0;">
  <h3 style="margin:0 0 12px 0;">Session Summary — Overall: {round(total, 1)}/5</h3>
  <table style="width:100%; border-collapse:collapse;">
    <thead><tr style="border-bottom:2px solid #cbd5e1;">
      <th style="padding:4px 8px; text-align:left;"></th>
      <th style="padding:4px 8px; text-align:left;">Step</th>
      <th style="padding:4px 8px; text-align:left;">Score</th>
    </tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""
