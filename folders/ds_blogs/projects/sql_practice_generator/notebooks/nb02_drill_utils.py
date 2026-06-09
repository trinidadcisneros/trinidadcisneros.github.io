"""
nb02 Pharmacy Interview Drill Utilities
========================================

Claude powered drill generator for Staff Product Analyst interview prep in the
pharmacy / digital health space. Built on top of nb01 SQL practice infrastructure.

Three categories with nested subtopics (pharmacy_sql moved to nb01):

  1. Data Transformation Modeling    (executable in Postgres sandbox)
  2. Critical Reasoning SQL          (executable in Postgres sandbox)
  3. Understanding Product Metrics & KPIs  (markdown graded, no SQL exec)

Reuses sql_practice_utils (sandbox connection, validation harness, save/load)
and adds pharmacy/care domain bias to every generated problem.
"""

import os
import json
import uuid
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

import pandas as pd

# Reuse the nb01 infrastructure rather than duplicating it
import sql_practice_utils as spu
import sandbox as sbx


# ============================================================
# Claude client (shares the singleton from sql_practice_utils)
# ============================================================

def init_claude(model: str = None) -> bool:
    """Initialize the Claude client via sql_practice_utils."""
    return spu.init_claude(model)


def _call_claude(system_prompt: str, user_prompt: str, max_tokens: int = 4000) -> Optional[str]:
    return spu._call_claude(system_prompt, user_prompt, max_tokens=max_tokens)


def _extract_json(text: str) -> Optional[Dict[str, Any]]:
    return spu._extract_json(text)


# ============================================================
# Category and subtopic catalog
# ============================================================

# Categories that execute against the Postgres sandbox use base_qtype to pick
# the validation harness shape. KPI category is markdown only (no SQL exec).

CATEGORIES = {
    "transformation_modeling": {
        "label": "1. Data Transformation Modeling",
        "description": "Schema design, dimensional modeling, SCD Type 2, dbt tests + macros.",
        "kind": "sql",
        "subtopics": {
            "schema_design": {
                "label": "Schema design (propose tables and grain)",
                "kind": "kpi",  # design doc, KPI form-graded
            },
            "dimensional_modeling": {
                "label": "Dimensional modeling (build fact + dim tables)",
                "base_qtype": "select_analytical",
            },
            "scd_type_2": {
                "label": "SCD Type 2 (formulary changes over time)",
                "base_qtype": "select_analytical",
            },
            "multiple_choice": {
                "label": "Multiple choice drills (terminology + concepts)",
                "kind": "multiple_choice",  # MCQ + True/False + order questions, graded against an answer key
            },
        },
    },
    "critical_reasoning": {
        "label": "2. Critical Reasoning SQL",
        "description": "Ambiguous metric definitions, missing data, clarify-then-query, broken-query critique.",
        "kind": "sql",
        "subtopics": {
            "ambiguous_metric": {
                "label": "Ambiguous metric definition (state assumptions, then SQL)",
                "base_qtype": "select_analytical",
            },
            "missing_data": {
                "label": "Missing data assumptions (nulls, late events, partial rows)",
                "base_qtype": "select_analytical",
            },
            "edge_cases": {
                "label": "Edge case handling (boundary days, partial events)",
                "base_qtype": "select_analytical",
            },
            "clarify_then_query": {
                "label": "Clarify then query (list questions, then SQL)",
                "base_qtype": "select_analytical",
            },
            "outlier_handling": {
                "label": "Outlier handling (median vs mean, capping)",
                "base_qtype": "select_analytical",
            },
            "broken_query_critique": {
                "label": "Critique a broken SQL query (spot the bug, propose the fix)",
                "base_qtype": "select_analytical",
                "subkind": "critique",  # special-cased generator below
            },
        },
    },
    "product_kpis": {
        "label": "3. Understanding Product Metrics & KPIs",
        "description": "Markdown answers graded against a rubric. Mirrors Product Analytics Academy exercise types.",
        "kind": "kpi",
        "subtopics": {
            "metric_critique": {
                "label": "Metric critique (what is wrong with this metric?)",
                "academy_section": "Section 1 Metrics",
            },
            "metric_design": {
                "label": "Metric design (propose 2+ metrics for this feature)",
                "academy_section": "Section 1 Metrics",
            },
            "metric_diagnosis": {
                "label": "Metric diagnosis (explain why metric behaved this way)",
                "academy_section": "Section 1 Metrics",
            },
            "counter_metric_design": {
                "label": "Counter metric design (negative impact + counter metric)",
                "academy_section": "Section 2 Experiment Design",
            },
            "experiment_critique": {
                "label": "Experiment critique (find flaws in proposed metrics)",
                "academy_section": "Section 2 Experiment Design",
            },
            "event_vs_user_property": {
                "label": "Event vs user property (which to use? why?)",
                "academy_section": "Section 4 Tracking Plans",
            },
            "event_properties_design": {
                "label": "Event properties design (what properties to capture?)",
                "academy_section": "Section 4 Tracking Plans",
            },
            "user_properties_design": {
                "label": "User properties design (segmentation properties)",
                "academy_section": "Section 4 Tracking Plans",
            },
            "tracking_plan_design": {
                "label": "Tracking plan design (3 events + properties for a feature)",
                "academy_section": "Section 4 Tracking Plans",
            },
            "prd_impact_measurement": {
                "label": "PRD impact measurement section (full write up)",
                "academy_section": "Section 4 Tracking Plans",
            },
            "multiple_choice": {
                "label": "Multiple choice drills (terminology + concepts)",
                "kind": "multiple_choice",
            },
        },
    },
    "version_control": {
        "label": "4. Version Control (Git workflows for analytics)",
        "description": "Branching strategy, merge conflict resolution, rebase vs merge, PR critique, commit hygiene, revert strategy.",
        "kind": "kpi",
        "subtopics": {
            "branching_strategy": {
                "label": "Branching strategy (design the team's PR workflow)",
            },
            "merge_conflict_resolution": {
                "label": "Merge conflict resolution (resolve a SQL/dbt model conflict)",
            },
            "rebase_vs_merge": {
                "label": "Rebase vs merge (when to use each, why)",
            },
            "pr_review_critique": {
                "label": "PR review critique (flag what's wrong in a mock diff)",
            },
            "commit_message_critique": {
                "label": "Commit message critique (rewrite a vague commit message)",
            },
            "revert_strategy": {
                "label": "Revert a bad commit safely (revert vs reset, force-push risk)",
            },
            "git_state_diagnose": {
                "label": "Diagnose a stuck Git state (what command gets you out?)",
            },
            "multiple_choice": {
                "label": "Multiple choice drills (terminology + concepts)",
                "kind": "multiple_choice",
            },
        },
    },
}


def category_keys() -> List[str]:
    return list(CATEGORIES.keys())


def subtopic_keys(category: str) -> List[str]:
    return list(CATEGORIES[category]["subtopics"].keys())


def category_kind(category: str) -> str:
    return CATEGORIES[category]["kind"]


def subtopic_kind(category: str, subtopic: str) -> str:
    """Returns the subtopic's kind, honoring a per-subtopic override if present.
    Falls back to the category's kind when the subtopic doesn't override."""
    sub = CATEGORIES[category]["subtopics"][subtopic]
    return sub.get("kind", category_kind(category))


def subtopic_label(category: str, subtopic: str) -> str:
    return CATEGORIES[category]["subtopics"][subtopic]["label"]


def base_qtype(category: str, subtopic: str) -> Optional[str]:
    return CATEGORIES[category]["subtopics"][subtopic].get("base_qtype")


# ============================================================
# Pharmacy / care domain scenarios (no company names — generic anchors)
# All generated problems anchor on one of these
# ============================================================

# Industry scenarios — replaces the old PHARMACY_SCENARIOS list with a dict
# keyed by industry slug. _pick_scenario(industry) picks from one slug, or
# flattens across all slugs when called with no arg / "random".
INDUSTRY_SCENARIOS = {
    "consumer_social": [
        "a dating app tracking mutual matches and messaging engagement",
        "a photo sharing app tracking story creation and view rates",
        "a short video platform tracking watch time and completion rates",
        "a community forum tracking thread participation and member retention",
        "a podcast app tracking listening sessions and episode completion",
    ],
    "marketplace": [
        "a ride share app tracking match rate from request to driver acceptance",
        "a food delivery service tracking order completion and delivery time",
        "a gig labor marketplace tracking job acceptance and completion rates",
        "a P2P resale marketplace tracking listing-to-sale conversion",
        "a real estate listing platform tracking saved searches and inquiry rates",
    ],
    "ecommerce": [
        "a D2C subscription box service tracking renewal and churn",
        "a fashion ecommerce site tracking add-to-cart and conversion",
        "an online grocery service tracking basket size and reorder rates",
        "a beauty retailer tracking loyalty program redemption rates",
    ],
    "fintech": [
        "a neobank tracking debit card swipes and deposit funnel",
        "a buy-now-pay-later service tracking installment payment compliance",
        "a robo advisor tracking portfolio rebalancing and AUM growth",
        "a crypto exchange tracking trading volume and on-ramp deposits",
        "an expense management app tracking receipt capture and policy compliance",
    ],
    "b2b_saas": [
        "a CRM tracking pipeline coverage and won opportunity rates",
        "a project management tool tracking sprint completion and task throughput",
        "an HR platform tracking onboarding completion and benefits enrollment",
        "an observability platform tracking alert acknowledge time and MTTR",
        "a developer tools company tracking trial-to-paid conversion and seat expansion",
    ],
    "productivity_media": [
        "a note-taking app tracking notebook creation and daily writing streaks",
        "a streaming video service tracking watch time and binge depth",
        "a music streaming service tracking saved tracks and playlist creation",
        "a news app tracking article completion and subscription conversion",
    ],
    "health_wellness": [
        "a telehealth platform tracking visit completion and follow-up scheduling",
        "a mental health app tracking session completion and journal entries",
        "a fitness app tracking workout completion and active days per week",
        "a sleep tracking app tracking sleep score and goal achievement",
    ],
    "gaming": [
        "a free-to-play mobile game tracking session length and ad impressions",
        "a console online service tracking multiplayer match acceptance",
        "a battle royale mobile game tracking match completion and squad invites",
    ],
    "education": [
        "an online course platform tracking course completion and certification",
        "a language learning app tracking daily streaks and lesson completion",
        "a tutoring marketplace tracking session booking and tutor ratings",
        "a K-12 homework app tracking assignment turn-in and grade improvement",
    ],
    "pharmacy_care": [
        "a digital pharmacy tracking prescription submissions through PBM adjudication",
        "a same day medication delivery service tracking on-time delivery performance",
        "a prescription refill adherence program tracking 30/60/90 day refill rates",
        "a prior authorization cycle time tracking system across payers",
        "a telehealth visit completion funnel from booking to provider sign-off",
        "an at-home diagnostic test kit platform tracking kit shipped and results released",
        "a clinical engagement program tracking patient outreach response rates by channel",
    ],
}

# Backward compat: PHARMACY_SCENARIOS still exists for code paths that
# imported it directly, but it now aliases the pharmacy_care slice.
PHARMACY_SCENARIOS = INDUSTRY_SCENARIOS["pharmacy_care"]


def _pick_scenario(industry: Optional[str] = None) -> str:
    """Pick a generic industry-scoped scenario anchor for problem generation.

    industry can be:
      - None or "random" / "" — pick across all industries
      - "booedup" — returns the BooedUp anchor (the rich app context is
        injected separately via apply_scenario_anchor)
      - an INDUSTRY_SCENARIOS key — pick within that vertical only
    """
    if industry == "booedup":
        return "the BooedUp dating app"
    if industry and industry in INDUSTRY_SCENARIOS:
        return random.choice(INDUSTRY_SCENARIOS[industry])
    # random / unknown / none — flatten all non-booedup industries
    pool = []
    for k, v in INDUSTRY_SCENARIOS.items():
        pool.extend(v)
    return random.choice(pool) if pool else "a consumer mobile product"


# ============================================================
# Subtopic guidance — extends nb01's _topic_specific_guidance with
# Pharmacy domain context and subtopic-specific framing
# ============================================================

SUBTOPIC_GUIDANCE = {
    # ---- Data Transformation Modeling ----
    # NOTE: cte_chain, staging_vs_marts, and materialization_choice were dropped
    # (they were redundant with nb01 SQL practice OR with schema_design's
    # structured form). Tab 2 now contains 4 modeling-essential subtopics:
    # schema_design (KPI form), dimensional_modeling (SQL), scd_type_2 (SQL),
    "dimensional_modeling": (
        "Build a problem that requires designing a small star schema for a pharmacy analytics "
        "question. Schema includes 1 fact table (e.g., fact_claims) and 2 to 3 dim tables "
        "(dim_drug, dim_payer, dim_patient). The prompt asks the user to write a query that joins "
        "the fact to the dims and aggregates by a dim attribute. The answer key uses INNER JOIN "
        "or LEFT JOIN with explicit ON clauses naming the surrogate keys. Include a dim with a "
        "many-to-one collapse (e.g., dim_drug.drug_class) so the GROUP BY happens at the dim level, "
        "not the fact grain."
    ),
    "scd_type_2": (
        "Build a Slowly Changing Dimension Type 2 problem. Schema includes a dim with valid_from / "
        "valid_to / is_current columns (e.g., dim_formulary tracking which drugs are covered by a "
        "payer over time). Fact table has a transaction date. The prompt asks the user to join the "
        "fact to the version of the dim that was active on the transaction date (using BETWEEN "
        "valid_from AND valid_to, or valid_from <= tx_date AND (valid_to IS NULL OR valid_to > tx_date)). "
        "Include at least one fact row that lands on a boundary date so the join inclusivity matters."
    ),
    # NOTE: schema_design was previously a SQL drill but is now KPI-style
    # (markdown-graded design doc). Its generator prompt lives in
    # KPI_SUBTOPIC_GUIDANCE further down. The kind override on the catalog entry
    # routes generation to generate_kpi_problem.
    # ---- Critical Reasoning SQL ----
    "ambiguous_metric": (
        "Build a problem where the metric definition is intentionally ambiguous. The prompt asks "
        "for something like 'patient adherence rate' or 'pharmacy fulfillment rate' WITHOUT "
        "specifying the exact numerator and denominator. The prompt MUST instruct the user: "
        "'In a SQL comment at the top, state which definition you chose and why. Then write the "
        "SQL.' The answer key opens with `-- Definition chosen: ...` then the SQL. The validation "
        "harness only checks that the SQL runs and produces a sensible result; multiple definitions "
        "are acceptable, but the answer must declare its choice."
    ),
    "missing_data": (
        "Build a problem where the data has realistic missingness: NULL fields, late-arriving rows "
        "(event_ts after the cutoff), partial event sequences (a claim with a 'submitted' event "
        "but no 'paid' event yet). The prompt asks for a metric and forces the user to handle the "
        "gaps. The answer key MUST include explicit handling: COALESCE, IS NOT NULL filters, "
        "LEFT JOIN with NULL handling, or a COMMENT explaining the assumption. Include at least "
        "two flavors of missingness in the test data."
    ),
    "edge_cases": (
        "Build a problem with at least three intentional edge cases: (1) a refill on the boundary "
        "day (day 30 exactly) so the user must decide < vs <=, (2) a rejected-then-never-recycled "
        "claim so the user must decide whether to count as abandoned, (3) a claim with a reversal "
        "after pay so the user must decide net vs gross. The prompt MUST tell the user to handle "
        "each edge case explicitly. The answer key includes SQL comments noting how each edge case "
        "is handled."
    ),
    "clarify_then_query": (
        "Build a problem where the prompt is intentionally short and underspecified (2 to 3 "
        "sentences). The prompt MUST instruct the user: 'Before writing SQL, list 3 to 5 clarifying "
        "questions you would ask the requesting stakeholder in a SQL comment block. Then make "
        "reasonable assumptions and write the SQL.' The answer key opens with `-- Clarifying "
        "questions: 1. ... 2. ... 3. ...` then `-- Assumptions: ...` then the SQL."
    ),
    "outlier_handling": (
        "Build a problem on time-to-fill or revenue-per-claim where the data is heavily skewed "
        "(a few outliers 10x to 100x larger than the median). The prompt MUST ask the user to "
        "produce both AVG and MEDIAN AND comment on which is more appropriate. Alternative: ask "
        "the user to write SQL that caps outliers at the 99th percentile before averaging. The "
        "answer key uses PERCENTILE_CONT and includes a SQL comment explaining the choice."
    ),
    "broken_query_critique": (
        "Build a 'critique a broken SQL query' problem in the style of Product Analytics Academy "
        "SQL Exercises 2 and 4. Pick ONE common bug class:\n"
        "  - Missing GROUP BY on aggregation with non-aggregated select column\n"
        "  - Missing ON clause on a JOIN (cross product instead of intended inner join)\n"
        "  - Aggregation in WHERE instead of HAVING\n"
        "  - COUNT(*) vs COUNT(DISTINCT) confusion\n"
        "  - LEFT JOIN with WHERE on the right table column (silently becomes inner join)\n"
        "  - Window function partition on the wrong column (e.g., partitioning by event_id when "
        "you meant claim_id)\n"
        "  - Date arithmetic boundary error (BETWEEN inclusive of upper, double-counting the cutoff)\n"
        "The prompt structure MUST be:\n"
        "  1. A 1-paragraph pharmacy/care scenario describing what the analyst is trying to compute.\n"
        "  2. A code block showing the COLLEAGUE'S BROKEN QUERY verbatim.\n"
        "  3. A directive: 'Identify the bug in a single SQL line comment at the top of your "
        "answer (-- Bug: ...), then write the corrected query.'\n"
        "The answer_key MUST open with `-- Bug: <one-line description>` then the corrected query "
        "(followed by a confirming SELECT if mutation, or just be the fixed SELECT). The example "
        "input data should be small enough that the bug's wrong output is visibly different from "
        "the right output (e.g., GROUP BY missing produces a single aggregated row instead of one "
        "per category; missing ON produces N*M cross-product rows). Hints should progressively "
        "give: (1) 'something is missing that lets the engine know how to group/join', (2) name "
        "the clause, (3) show the corrected line."
    ),
}


# ============================================================
# SQL category problem generation
# Wraps spu generation but injects pharmacy scenario + subtopic guidance
# ============================================================

SQL_GENERATOR_SYSTEM = spu.GENERATOR_SYSTEM + """

ADDITIONAL CONTEXT FOR THIS DRILL:
- The learner is preparing for a Staff Product Analyst interview in the pharmacy /
  digital health space (digital pharmacy operations, at-home diagnostics, telehealth,
  care coordination).
- DO NOT use any specific company names in prompts, scenarios, glossaries, or examples.
  Use generic descriptors like "a digital pharmacy", "a B2B pharmacy API platform",
  "an at-home diagnostic service", "a telehealth platform", etc. NEVER mention real
  pharmacy or healthcare company names (no Fuze Health, FuzeRx, Truepill, Alto,
  LetsGetChecked, CVS, Walgreens, Express Scripts, OptumRx, etc).
- Use realistic pharmacy / care / diagnostics / telehealth domain terminology in the
  table names, column names, and prompt wording.
- Realistic fact table names: claims, claim_events, prescriptions, fills,
  test_kit_orders, telehealth_visits, patient_outreach, deliveries.
- Realistic dim names: dim_drug, dim_payer, dim_patient, dim_pharmacy, dim_prescriber,
  dim_test_kit_type, dim_geography.
- Use real NCPDP-style reject category language WITHOUT claiming exact NCPDP fidelity:
  'PA required', 'formulary not covered', 'refill too soon', 'days supply exceeded',
  'DUR reject', 'COB stale', 'NDC not covered', 'plan limitations exceeded'.
- Drug class examples: GLP-1 agonists, oral contraceptives, statins, fertility meds
  (gonadotropins, progesterone), HIV PrEP, mental health (SSRI), oncology infusion.
- Patient outcome columns: time_to_fill, days_supply, abandoned_flag, refill_at_30d.
- Do NOT use generic e-commerce, ride-share, or social media scenarios.

INSERT FORMAT REQUIREMENT (HARD RULE):
- Every INSERT statement in example_input_data and test_data MUST include the explicit
  column list:  INSERT INTO <table> (col1, col2, col3) VALUES (...);
- Do NOT emit `INSERT INTO <table> VALUES (...)` without the column list. The notebook
  renderer requires the column list to display the data as an HTML table.

INSERT TUPLE LENGTH CONSISTENCY (HARD RULE):
- Every row tuple in a multi-row VALUES clause MUST have EXACTLY the same number of
  values as the column list and as every other row tuple. Postgres rejects with
  "VALUES lists must all be the same length" if any row tuple length differs.
- Before emitting the INSERT, count the columns in the column list and confirm every
  parenthesized row tuple has that exact count.
- Example of the failure mode to AVOID:
    INSERT INTO claims (claim_id, rx_number, patient_id, drug_class)
    VALUES ('C001', 'RX1', 'P1', 'GLP-1'),
           ('C002', 'RX2', 'P2'),                           -- WRONG: only 3 values
           ('C003', 'RX3', 'P3', 'statins', 'extra');       -- WRONG: 5 values

SCHEMA-DATA CONSISTENCY (HARD RULE):
- If a column is declared NOT NULL in CREATE TABLE, NEVER INSERT NULL into that column
  in example_input_data or test_data. The script will fail to load and the problem is
  unsolvable.
- If a column is declared as PRIMARY KEY, all values for that column across all INSERT
  statements MUST be unique and non-NULL.
- If a foreign key is declared, every value inserted into the child column MUST exist
  in the parent table FIRST (load parent rows before child rows in the script).
- If a CHECK constraint is declared, every inserted value must satisfy it.
- If the problem requires NULLs in the data (NULL handling drills, missing data drills),
  the relevant column MUST be declared as nullable in the schema (omit NOT NULL).
  Do not declare NOT NULL and then "demonstrate" NULL handling — that crashes the loader.
- Always load tables in dependency order: parent dims first, then facts that reference them.

ADDITIONAL JSON FIELDS REQUIRED FOR THIS NOTEBOOK:
The standard schema from the parent system prompt still applies, but you MUST also include
these two additional top-level keys in the JSON object:

  "glossary": [
    {"term": "adjudication", "definition": "the real-time decision the PBM makes on whether to pay a submitted prescription claim and how much"},
    {"term": "recycle", "definition": "resubmitting a previously rejected claim after fixing the issue (e.g., adding a prior authorization)"},
    {"term": "submitted (event)", "definition": "the moment the pharmacy first transmits the claim to the PBM"},
    {"term": "<other domain or method term used in the prompt>", "definition": "<one-sentence lay explanation>"}
  ],

  "calculation_explanation": "A 3-6 step plain-language walkthrough of HOW to compute the answer. FORMAT REQUIREMENT: each step MUST be on its own line, prefixed with a number followed by a period and a space ('1. ', '2. ', etc), with a literal newline between steps. Do NOT put all steps on one line — that breaks the renderer. Avoid SQL syntax. Do NOT give away the exact code, but DO explain the conceptual approach. Correct format example (newlines shown literally):\n  1. For each claim, find the first time each event type happened.\n  2. Count how many distinct claims have at least one event of each type.\n  3. For each stage after the first, divide its count by the prior stage's count to get the conversion rate.\n  4. Order the output by funnel stage sequence.",

  "interpretation_example": "A model interpretation of the example_output_rows for THIS specific problem. 3-5 bullets. SAME FORMAT REQUIREMENT as calculation_explanation: one bullet per line, each prefixed with '- ' and a literal newline between bullets. Each bullet should: (a) read the actual numbers literally first, (b) interpret what the numbers suggest about underlying business behavior, (c) where relevant, compare to industry benchmarks (FPAR 75-85% retail, refill rate 30d 60-80% chronic, abandonment 8-15%, etc), (d) flag ambiguities or concerns. Do NOT use vague phrases like 'this suggests opportunity'. Be specific. Example for an adjudication funnel where output shows submitted=10, paid=6:\n  - 60% of claims paid (6 of 10) — below the 75-85% retail FPAR benchmark, suggesting a process gap.\n  - 30% of claims rejected (3 of 10) and only 67% recycled, leaving 1 unrecovered rejection.\n  - The recycle success rate of 67% is plausible if PA-required is the dominant reject reason; lower if it's refill-too-soon.\n  - The drop from rejected (3) to paid-after-recycle (2) is the operational opportunity to size next.",

  "recommendation_example": "A model recommendation grounded in pharmacy industry standard practice. 3-5 bullets. SAME FORMAT REQUIREMENT: one bullet per line, each prefixed with '- ' and a literal newline between bullets. Each bullet should: (a) start with an action verb (Trigger, Investigate, Implement, Add, Review), (b) name the OWNING stakeholder (Pharmacy Ops, Care Coordination, Finance, Quality team, Product, Engineering), (c) reference an industry-standard practice or framework (PA team triage, medication synchronization, 90-day supply transfer, adherence outreach trigger, Star Ratings, PDC threshold, refill cliff intervention), (d) include at least one 'what to monitor next' item with a concrete metric and direction. Do NOT recommend generic things like 'investigate further' or 'iterate'. Example:\n  - Trigger PA-team triage (Pharmacy Ops): the 1 unrecovered rejection per 10 submits implies meaningful daily volume — route PA-required rejects to a dedicated team within 1 hour of reject.\n  - Implement automated formulary substitution (Engineering + Care): for formulary-not-covered rejects, propose covered alternatives at point of fill; benchmark for retail is 50-70% acceptance.\n  - Re-baseline FPAR for this product line (Finance + Product): the 60% rate may be acceptable for specialty but is a red flag for retail; segment the dashboard accordingly.\n  - Monitor weekly: track FPAR trend by reject reason and watch for the 30-day rolling average crossing 75% (the lower retail benchmark)."

Glossary rules:
- Include 4 to 8 glossary entries.
- Cover: any industry term (e.g., adjudication, formulary, prior auth, NADAC, PBM,
  refill too soon, time to fill, abandonment), each distinct event_type value used in
  the data (submitted, rejected, recycled, paid, dispensed, reversed, delivered),
  any analytical method term (e.g., funnel conversion, cohort retention, window
  function, Kaplan-Meier, percentile_cont, SCD Type 2), and any segmentation
  dimension worth knowing (e.g., drug class, payer, channel).
- Definitions must be ONE sentence each, in plain English a non-pharmacy reader can follow.
- Do NOT define generic SQL keywords (SELECT, JOIN, GROUP BY).

Calculation explanation rules:
- 3 to 6 numbered steps.
- Conceptual, not syntactic.
- Should help a learner who knows SQL but does not yet know the domain decide on the right
  shape (CTE, window, GROUP BY, etc.).
- Do NOT include the literal SQL — that is what answer_key is for.

============================================================
TERMINOLOGY ACCURACY MANDATE — HARD RULE FOR ALL CATEGORIES
============================================================

All metric names, technical terms, schema names, reject codes, drug names, and benchmark
numbers used anywhere in the problem MUST reflect ACTUAL industry practice. DO NOT invent
or paraphrase standard terminology. DO NOT hallucinate concepts, frameworks, or numbers.

If you are unsure whether a term, code, or benchmark is real, DO NOT use it. Substitute
something from the approved lists below or omit the detail entirely.

----- PHARMACY ADJUDICATION METRIC NAMES -----
Use these names verbatim in prompts when the problem computes them. Do NOT invent
synonyms like "claim acceptance percentage" or "successful adjudication ratio".
- First Pass Acceptance Rate (FPAR) = paid_on_first_submit / total_submitted
- Net Acceptance Rate = (total_paid - total_reversed) / total_submitted
- Recycle Success Rate = paid_after_recycle / total_recycled
- Abandonment Rate = scripts_never_dispensed_within_N_days / total_submitted
- Manual Touch Rate = manual_interventions per 1000 scripts
- Time to Fill = minutes from submit to dispense (use MEDIAN, not AVG, for skewed data)
- Time to PA Approval = minutes/hours from PA-required reject to next paid event
- Days Supply on Hand = patient adherence proxy (PDC > 80% is the standard adherence cutoff)

----- NCPDP TRANSACTION CODES (the source-of-truth field shape) -----
Colloquial event_type names are fine in the data, but the GLOSSARY field MUST mention the
NCPDP code mapping so the learner sees the source-of-truth. Do NOT invent codes.
- B1 = billing / first submit
- B2 = reversal of paid claim
- B3 = rebill / recycle of rejected claim

----- NCPDP REJECT CODES (only these, with these names) -----
Use the format `'<code> - <official name>'` when populating reject_code values:
- 70 - Product/Service Not Covered
- 75 - Prior Authorization Required
- 76 - Plan Limitations Exceeded
- 79 - Refill Too Soon
- 88 - DUR Reject (Drug Utilization Review — interaction, duplicate therapy, dose limits)
- M/I family - Missing/Invalid data field (e.g., M/I Days Supply, M/I Quantity Dispensed)
- 65 - Patient Not Covered
- 41 - Submit Bill To Other Processor (COB / coordination of benefits)
DO NOT invent reject codes outside this list.

----- REALISTIC BENCHMARKS (when prompts mention current or target metric values) -----
Use ranges in this list. Do NOT invent benchmarks like "lift FPAR from 30% to 50%".
- Retail/digital pharmacy FPAR: 75 to 85%
- Specialty pharmacy FPAR: 60 to 75% (more PA)
- Net Acceptance Rate retail: 90 to 95%
- Recycle Success Rate by category: PA-required 60-80% (with PA team), formulary
  substitution 50-70%, refill-too-soon ~5% (most can't be recycled, they wait)
- Abandonment rate retail: 8 to 15%; specialty 15 to 30%
- Adjudication response time: under 2 seconds end-to-end
- Time to fill at-counter retail: 15 to 60 min; same-day delivery: 1 to 24 hours
- Manual touch rate: typical 30 to 100 per 1000 scripts depending on PA volume

----- DRUG CLASSES (real names only) -----
GLP-1 agonists, oral contraceptives, statins, fertility medications (gonadotropins,
progesterone, leuprolide), HIV PrEP, SSRIs, SNRIs, oncology infusion, biologics,
ADHD stimulants, anticoagulants (DOACs, warfarin), insulin, diabetes orals (metformin,
SGLT2 inhibitors), respiratory inhalers (ICS, LABA, SABA), opioids, ADHD non-stimulants.
DO NOT invent drug class names.

----- DBT AND MODELING VOCABULARY (only these, only with these meanings) -----
- sources, staging (stg_), intermediate (int_), marts
- materializations: table, view, incremental, ephemeral
- SCD Type 2 fields: valid_from, valid_to, is_current
- star schema terminology: fact tables (one row per business event), dimension tables,
  surrogate keys, natural keys, conformed dimensions, junk dimensions
- dbt features: ref(), source(), tests (unique, not_null, accepted_values, relationships),
  exposures, snapshots, seeds
DO NOT invent dbt project structure, materialization options, or test types.

----- TABLE AND COLUMN NAMING CONVENTIONS -----
Use snake_case for all table and column names. Use these realistic shapes:
- Fact tables: claims, claim_events, prescriptions, fills, dispenses, deliveries,
  test_kit_orders, telehealth_visits, patient_outreach
- Dim tables: dim_drug, dim_payer, dim_pharmacy, dim_prescriber, dim_patient,
  dim_geography, dim_test_kit_type, dim_diagnosis
- Standard column names: claim_id, rx_number, patient_id, prescriber_id, payer_id,
  ndc (National Drug Code, 11-digit), drug_class, days_supply, quantity_dispensed,
  fill_date, submit_ts, dispense_ts, reject_code, paid_amount, ingredient_cost,
  dispensing_fee, copay, valid_from, valid_to, is_current

============================================================
EDGE CASE REQUIREMENT FOR test_data — HARD RULE
============================================================

Every test_data MUST include AT LEAST ONE realistic edge case. Pick the one that fits
the problem; if none fits, the problem may not be a good drill. Rotate across problems
so the learner sees all of them eventually:
- A REVERSAL: an event_type='reversed' (B2) record after a 'paid' event for the same claim
- A PARTIAL APPROVAL: a claim with both 'paid' and 'rejected' events on the same submit_ts
  (paid for some days_supply, rejected for the rest)
- A MULTI-CLAIM PRESCRIPTION: two claim_ids that share the same rx_number (rebill with
  new claim_id, OR a partial-fill split)
- A LATE-ARRIVING EVENT: an event_ts after the analytical cutoff date in the prompt
- A NULL-BEARING FIELD: a NULL in a column the answer_key must explicitly handle
- A DUPLICATE FIRST EVENT: same claim_id with two 'submitted' events at different ts
  (so first-occurrence logic must be exercised)

The answer_key MUST produce correct test_expected_rows DESPITE this edge case. If the
answer_key produces wrong output on the edge case, the answer_key is buggy and the
problem fails validation — fix the answer_key, do not weaken the test_data.

============================================================
ANTI-HALLUCINATION RULE FOR ALL DOMAIN CONTENT
============================================================

If you find yourself generating any of these, STOP and substitute from the approved lists:
- A metric name not on the metric list above
- A reject code number or name not on the reject code list above
- A drug class not on the drug class list above
- A benchmark number outside the benchmark ranges above
- A dbt vocabulary term not on the dbt list above
- An NCPDP transaction code not in (B1, B2, B3) — there are others (S1, P1, etc.) but
  use only the three above unless you can name the real code's purpose
- A "framework" or "methodology" name (e.g., "the McKinsey adjudication framework",
  "the AHA pharmacy operations standard") — these are usually not real

When in doubt, use plainer descriptive language instead of inventing branded terminology.
"""


def _build_sql_user_prompt(category: str, subtopic: str, dialect: str, scenario: str,
                           last_error: Optional[str] = None) -> str:
    """Compose the per-attempt user prompt for SQL category generation."""
    base_qt = base_qtype(category, subtopic)
    # Start with the nb01 topic guidance for the underlying question type
    guidance = spu._topic_specific_guidance(base_qt, dialect, scenario=scenario)
    # Layer the subtopic specific framing on top
    guidance += "\n\n--- SUBTOPIC FRAMING (this is the most important guidance) ---\n"
    guidance += SUBTOPIC_GUIDANCE.get(subtopic, "")
    guidance += f"\n\nLearner is drilling: {CATEGORIES[category]['label']} -> {subtopic_label(category, subtopic)}\n"
    if last_error:
        guidance += (
            "\n\n!!! PREVIOUS ATTEMPT FAILED VALIDATION !!!\n"
            f"{last_error}\n\n"
            "MANDATORY FIX PROTOCOL — read carefully:\n\n"
            "If the failure is 'Could not parse JSON from response.':\n"
            "  - Your prior response was either truncated mid-JSON or had prose around the "
            "JSON object that broke the parser. Both are output-budget problems.\n"
            "  - Emit ONE single ```json fenced block. NO prose before, NO prose after, NO "
            "second code block. The very first non-whitespace character of the fenced block "
            "must be `{` and the very last must be `}`.\n"
            "  - Tighten the response to fit within 4000 tokens. Concretely: cap CREATE TABLE "
            "at 2 tables, cap example_input_data at 8 rows, cap test_data at 18 rows, keep "
            "schema_ddl/prompt/answer_key terse, keep glossary at 4 entries (the floor), and "
            "keep calculation_explanation at 3 to 4 steps.\n"
            "  - Do NOT include a SQL code block separately — answer_key is a JSON STRING "
            "field inside the JSON object, not its own fenced block.\n"
            "  - Inside JSON string values, escape internal double quotes as \\\" and use "
            "literal \\n for newlines; do not embed unescaped newlines in JSON strings.\n\n"
            "If the failure is a SCHEMA CONSTRAINT VIOLATION (NOT NULL, PRIMARY KEY, "
            "FOREIGN KEY, CHECK):\n"
            "  - Either remove the constraint from CREATE TABLE, OR fix the data so "
            "every inserted row satisfies the constraint.\n"
            "  - For NOT NULL violations: change the column to nullable, OR replace the "
            "NULL with a real value, OR drop the offending row entirely.\n"
            "  - Load parent dim tables BEFORE child fact tables in the script.\n\n"
            "If the failure is 'LLM-claimed example_output_rows differ from actual':\n"
            "  - This means your answer_key SQL produces one result and your claimed "
            "example_output_rows shows another. They MUST agree. Pick ONE side:\n"
            "    OPTION A — TRUST THE SQL: copy the validator's 'actual' values into "
            "example_output_rows. Use this when the SQL is correct and your hand-traced "
            "claim was wrong.\n"
            "    OPTION B — TRUST THE CLAIM: rewrite the answer_key SQL until it produces "
            "the values you claimed. Use this when you're confident the claim reflects the "
            "right business logic and the SQL has a bug.\n"
            "  - DO NOT change both sides. DO NOT change the prompt or the input data unless "
            "the data itself is the bug (e.g., the data contradicts the prompt).\n"
            "  - Most often, OPTION A is right — the SQL ran in Postgres, so it computed "
            "what it computed. Your hand-trace was probably off by one in the date math, "
            "the cohort denominator, or the deduplication step.\n\n"
            "BEFORE EMITTING THE NEW JSON:\n"
            "  - Walk through example_input_data row by row in your head, applying the "
            "answer_key's logic step by step.\n"
            "  - Confirm your trace produces example_output_rows EXACTLY (right cells, "
            "right decimal precision, right NULL handling).\n"
            "  - If the trace doesn't match, fix one side per the protocol above.\n"
        )
    guidance += "\n\nReturn the JSON object now."
    return guidance


def _canonical_value(v) -> str:
    """Normalize a cell value for tolerant comparison between LLM claim and DB output.
    Treats None / 'None' / 'NULL' as equivalent. Numericizes BOTH numeric strings AND
    Decimal/float so '0.5000' and Decimal('0.5000') both canonicalize to '0.5'."""
    import decimal
    if v is None:
        return "NULL"

    # Numeric coercion path — apply to both numeric types AND numeric-looking strings
    if isinstance(v, str):
        s = v.strip()
        if s in ("", "None", "NULL", "null", "<NA>", "nan", "NaN"):
            return "NULL"
        # Try to parse as a number (this handles '0.5000', '0.6667', '5', '5.0', '-3.14')
        try:
            f = float(s)
            if f.is_integer():
                return str(int(f))
            return f"{f:.6g}"  # 6 significant figures, drops trailing zeros
        except (ValueError, TypeError):
            return s  # genuine string, return as-is

    if isinstance(v, (int, float, decimal.Decimal)):
        try:
            f = float(v)
            if f.is_integer():
                return str(int(f))
            return f"{f:.6g}"
        except Exception:
            return str(v)
    return str(v)


def _validate_sql_problem_strict(parsed: Dict[str, Any]) -> Tuple[bool, str]:
    """Strict validator. Runs the standard sql_practice_utils validation, then ALSO
    verifies the LLM's CLAIMED example_output matches what the answer_key actually
    produces. If they differ, the LLM didn't trace its own answer carefully and the
    user would otherwise be graded against silently-wrong expected output."""
    # Snapshot the LLM's claimed output BEFORE the standard validator overwrites it
    claimed_cols = list(parsed.get("example_output_columns") or [])
    claimed_rows = [list(r) if isinstance(r, list) else [r] for r in (parsed.get("example_output_rows") or [])]

    # Run the standard validator — runs the answer_key against example_input_data
    # and overwrites example_output_columns/rows with the actual DB result
    ok, err = spu._validate_problem(parsed)
    if not ok:
        return False, err

    actual_cols = list(parsed.get("example_output_columns") or [])
    actual_rows = parsed.get("example_output_rows") or []

    # If the LLM didn't claim anything, accept (no claim to compare against)
    if not claimed_cols and not claimed_rows:
        return True, "Valid (no LLM claim to verify; accepted DB-derived output)."

    # Column shape
    if claimed_cols and claimed_cols != actual_cols:
        return False, (
            f"LLM-claimed example_output_columns disagree with answer_key actual output.\n"
            f"  Claimed: {claimed_cols}\n"
            f"  Actual:  {actual_cols}\n"
            f"Re-trace the answer_key against example_input_data and align the claimed columns."
        )

    # Row count
    if len(claimed_rows) != len(actual_rows):
        return False, (
            f"LLM claimed {len(claimed_rows)} example output rows but the answer_key "
            f"actually produces {len(actual_rows)}. Re-trace the answer_key row by row "
            f"against the example_input_data."
        )

    # Cell-by-cell tolerant comparison
    mismatches = []
    for i, (cr, ar) in enumerate(zip(claimed_rows, actual_rows)):
        if len(cr) != len(ar):
            mismatches.append(f"row {i}: claimed {len(cr)} cells, actual {len(ar)} cells")
            continue
        for j, (cv, av) in enumerate(zip(cr, ar)):
            if _canonical_value(cv) != _canonical_value(av):
                col_label = actual_cols[j] if j < len(actual_cols) else f"col{j}"
                mismatches.append(f"row {i} col '{col_label}': claimed {cv!r}, actual {av!r}")
    if mismatches:
        head = mismatches[:6]
        more = len(mismatches) - len(head)
        msg = (
            "LLM-claimed example_output_rows differ from what the answer_key actually "
            "produces. The user would otherwise be graded against silently-wrong expected "
            "output. Specific mismatches:\n"
        )
        msg += "\n".join(f"  - {m}" for m in head)
        if more > 0:
            msg += f"\n  ... and {more} more cell mismatches"
        msg += (
            "\nThis is a self-consistency failure. Re-trace the answer_key against "
            "example_input_data row by row. Either fix the answer_key or fix the claimed "
            "example_output_rows so they agree."
        )
        return False, msg

    return True, "Valid (claimed and actual outputs match)."


def generate_sql_problem(category: str, subtopic: str, dialect: str = "postgresql",
                         max_retries: int = 6, on_attempt=None,
                         scenario_mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Generate a SQL drill problem and validate it via the sandbox harness.
    scenario_mode: None or 'random' for generic scenarios; 'booedup' to anchor
    the problem in the user's BooedUp dating app context."""
    scenario = _pick_scenario(scenario_mode)
    base_qt = base_qtype(category, subtopic)
    last_error = None
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass
        user_prompt = _build_sql_user_prompt(category, subtopic, dialect, scenario, last_error)
        user_prompt = apply_scenario_anchor(user_prompt, scenario_mode)
        text = _call_claude(SQL_GENERATOR_SYSTEM, user_prompt, max_tokens=4000)
        parsed = _extract_json(text)
        if not parsed:
            last_error = "Could not parse JSON from response."
            continue
        parsed["_meta"] = {
            "category": category,
            "subtopic": subtopic,
            "kind": "sql",
            "question_type": base_qt,
            "dialect": dialect,
            "scenario": scenario,
            "scenario_mode": scenario_mode or "random",
            "generated_at": datetime.now().isoformat(),
            "problem_id": uuid.uuid4().hex[:12],
            "validation_attempts": attempt,
            "notebook": "nb02_analyst_interview_drills",
        }
        ok, err = _validate_sql_problem_strict(parsed)
        if ok:
            return parsed
        last_error = err
    print(f"Generation failed validation after {max_retries} attempts. Last error: {last_error}")
    return None


# ============================================================
# Product Metrics & KPIs problem generation (markdown only)
# ============================================================

KPI_GENERATOR_SYSTEM = """\
You generate Product Analytics drill problems for a learner preparing for a Staff Product
Analyst interview in the pharmacy / digital health space (digital pharmacy operations,
at-home diagnostics, telehealth, care coordination).

NO COMPANY NAMES: do not name specific companies in scenarios, prompts, examples, or
recommendations. Use generic descriptors only ("the pharmacy", "the platform",
"the care coordination team", "an at-home diagnostic service", etc). NEVER use Fuze
Health, FuzeRx, Truepill, Alto, LetsGetChecked, CVS, Walgreens, Express Scripts,
OptumRx, or any other real company name.

The drill style mirrors Ali Baghshomali's Product Analytics Academy course exactly. Reference
answers in that course are TERSE. Examples of what counts as a complete answer there:
  - Metric critique: 'Should be normalized. Ride Cancellation Rate is better.' (one sentence)
  - Metric design: just a bullet list of metric names with NO formulas and NO rationale
        - Number of searches per purchase
        - Conversion rate from search to purchase
  - Metric diagnosis: 'The thumbnails are misleading (aka: "clickbait")' (one sentence)
  - Tracking plan: 3 events, each with a 1-line property bullet underneath, no schemas
  - PRD impact measurement: 3 short sections (Product Performance Metrics / Questions We Want
        To Answer / Tracking Plan link), total under 100 words
Generate problems and reference answers that match this terseness. A correct one-line answer
that names the right concept IS a strong answer in this course style. Do not pad.

Output MUST be a single JSON object inside a ```json fenced block. No prose outside.

OPTIONAL TOP LEVEL FIELDS THE FORMS READ:
  - stakeholder_rationale (string, one sentence): why the stakeholder proposed the metric. For metric_critique, write this as the stakeholder would defend it — that is the flawed reasoning the learner is supposed to spot. For metric_design and other subtopics, write what the team is trying to learn from the feature so the learner has a concrete goal to anchor on.
  - metric_critique_picks (dict, only for metric_critique subtopic): see the metric_critique user prompt for the required shape. Drives the learner's Q6/Q7/Q8 dropdowns.


JSON schema:
{
  "title": "short title, 4-8 words",
  "scenario": "1 to 2 sentence pharmacy/care scenario setup (no company names)",
  "prompt": "the actual exercise question, 2 to 5 sentences",
  "instructions": "what the user should write in their answer. BE EXPLICIT about the expected length and format. Default: 'Bullet list is fine. No formulas required unless asked. Aim for under 100 words total.'",
  "expected_themes": [
    "theme 1 the answer should hit (3 to 8 words each)",
    "theme 2 the answer should hit",
    "..."
  ],
  "reference_answer": "a strong sample answer in markdown, 50 to 150 words. Bullet lists welcome. Match the PAA terseness shown above. For metric design and property design exercises, the reference answer can be JUST a bullet list of names with no rationale.",
  "grading_rubric": [
    {"criterion": "criterion name", "description": "what to look for", "weight": 25},
    {"criterion": "...", "description": "...", "weight": 25},
    {"criterion": "...", "description": "...", "weight": 25},
    {"criterion": "...", "description": "...", "weight": 25}
  ],
  "hints": ["vague hint", "more specific hint", "near-answer hint"],
  "common_mistakes": ["mistake learners often make", "another mistake"]
}

Hard rules:
- The scenario MUST be about generic pharmacy / digital health product surfaces:
  digital pharmacy operations (auto-recycling, refill adherence, PA workflow, formulary
  substitution, same-day delivery), at-home diagnostic test kits, telehealth visits,
  care coordination, patient app onboarding, fertility medication delivery, prescription
  transfer flow.
- Do NOT use generic e-commerce, ride-share, or social media scenarios. NO eBay, Spotify,
  Lyft, Instagram, Netflix, YouTube examples.
- Do NOT use specific pharmacy or healthcare company names. Use generic descriptors only.
- The grading_rubric weights MUST sum to 100.
- The grading_rubric MUST NOT have a 'length' or 'thoroughness' criterion. Reward correctness
  and concept identification, not word count.
- For metric_critique, metric_design, metric_diagnosis, event_vs_user_property: the rubric
  should reward identifying the right concept (normalization, outliers, mechanism, latest-
  value-only) over producing a long explanation.
- Each criterion must be specific enough that a grader can decide pass/partial/fail.
- expected_themes are short (3 to 8 words each), they are the keyword anchors a strong
  answer should reference.
- reference_answer should model strong analytical thinking AT PAA TERSENESS. The user's
  answer can take a different valid angle.
- Use the Product Analytics Academy framework vocabulary where relevant: critical metric,
  evaluation metric, key metric, counter-metric, sanity check metric, guardrail metric,
  normalize per subject, expected direction of change, p-hacking, event vs property,
  user property vs event property, tracking plan, PRD impact measurement.

============================================================
TERMINOLOGY ACCURACY MANDATE — HARD RULE
============================================================

All product analytics framework terms, metric names, and benchmark numbers used MUST
reflect actual industry usage. Do NOT invent framework concepts, metric names, or
healthcare/pharmacy benchmarks.

----- APPROVED METRIC FRAMEWORK VOCABULARY -----
Critical metric / Evaluation metric / Key metric — primary metric the experiment moves
Counter-metric — could plausibly worsen if you naively chase the critical metric
Sanity check metric — confirms the experiment is wired correctly (e.g., cohort sizes match)
Guardrail metric — disqualifies a winner if breached (e.g., patient safety thresholds)
Normalize per subject — for cohort comparisons with uneven sizes
Expected direction of change — pre-registered for each metric
P-hacking — false positives from too many metrics or post-hoc subgroup splits
PDC (Proportion of Days Covered) — standard pharmacy adherence measure; >80% = adherent

----- APPROVED EVENT/PROPERTY VOCABULARY (Mixpanel/Amplitude standard) -----
Event — a user action with a timestamp
Event property — context captured at the moment of the event (only at-event value retained)
User property — context for a user, latest-value-only access
Tracking plan — documented set of events and properties to instrument
PRD impact measurement — section listing metrics, counter-metrics, questions, tracking plan

----- APPROVED HEALTHCARE/PHARMACY PRODUCT METRIC RANGES -----
When a scenario references a current or target metric value, use these ranges. DO NOT
invent values like "lift FPAR from 30% to 50%" — those are not industry-realistic.
- First Pass Acceptance Rate (FPAR) retail: 75 to 85%
- FPAR specialty pharmacy: 60 to 75%
- Net Acceptance Rate retail: 90 to 95%
- Recycle Success Rate: PA-required 60-80%, formulary substitution 50-70%, refill-too-soon ~5%
- Abandonment rate retail: 8 to 15%; specialty 15 to 30%
- Refill adherence at 30 days, chronic conditions: 70 to 85% (PDC > 80% = adherent)
- Test kit completion (at-home diagnostics): 60 to 85%
- Telehealth visit completion (booking → provider sign-off): 70 to 90%
- Patient app onboarding (signup → first Rx transferred): 20 to 40%
- Manual touch rate: 30 to 100 per 1000 scripts depending on PA volume
- Time to fill at-counter retail: 15 to 60 min; same-day delivery: 1 to 24 hours

----- APPROVED PRODUCT SURFACES (generic, no company names) -----
Use these scenario anchors only. Refer to them generically — e.g., "the pharmacy",
"the platform", "the care team" — never with a real company name:
- Auto-recycling workflow for refill-too-soon or PA rejections
- Same-day medication delivery
- Prior authorization (PA) approval workflow
- Formulary substitution at point of fill
- Prescription transfer flow (patient onboarding to a digital pharmacy)
- Refill adherence outreach (SMS, email, app push)
- Fertility medication delivery (gonadotropins, progesterone, leuprolide)
- At-home diagnostic test kit ordering
- Telehealth visit booking, completion, and follow-up
- Care team manual outreach for rejected claims
- Patient adherence intervention experiments

ANTI-HALLUCINATION RULE: do NOT invent metric names, framework concepts, benchmark
ranges, NCPDP codes, dbt patterns, drug classes, or company-specific product features.
If a concept is not in the approved lists above and is not a standard data analytics
primitive, do not use it. NEVER name specific real companies (Fuze Health, FuzeRx,
Truepill, Alto, LetsGetChecked, CVS, Walgreens, Express Scripts, OptumRx, etc).

============================================================
RUBRIC QUALITY FLOOR — HARD RULE
============================================================

Each grading_rubric criterion MUST:
1. Reference a SPECIFIC concept from the problem (e.g., "identifies that the metric is
   not normalized per script" — NOT "demonstrates good thinking")
2. Be testable: a grader should be able to clearly say "yes the answer addresses this"
   or "no it doesn't"
3. Cite either an expected_themes element OR the central business concept being tested

BANNED rubric language (these are feelings, not graders):
- "thoroughness", "depth of analysis", "completeness"
- "thoughtful", "well-reasoned", "demonstrates strong thinking"
- "shows understanding", "comprehensive coverage", "appropriate framing"
- "professional tone", "polished writing"

ACCEPTABLE rubric language examples:
- "Identifies the lack of normalization (per-script or per-patient) as the flaw"
- "Names a counter-metric with explicit numerator and denominator"
- "Selects event property and explains historical-vs-latest tradeoff"
- "Includes at least one rate metric (not just count metrics)"
- "Names PDC or refill adherence as the right adherence proxy"

If you can't write a rubric criterion that passes the testable bar, the problem itself
may be too vague. Re-frame the prompt to make the expected concept concrete.
"""


KPI_SUBTOPIC_GUIDANCE = {
    "metric_critique": (
        "Generate a 'what is wrong with this metric?' problem. Provide a generic pharmacy/care scenario (no company names) with a "
        "stakeholder-proposed metric that has ONE significant flaw (not normalized, count instead "
        "of rate, mean when median is better due to outliers, vanity count, mismeasures the goal). "
        "User answer style: ONE SENTENCE naming the flaw and proposing a corrected metric. Match "
        "PAA Metrics Exercise 1: 'Should be normalized. Ride Cancellation Rate is better.' The "
        "instructions field should say: 'One short sentence: name the flaw, propose a fix.' "
        "The reference_answer should be 1 to 2 sentences total. Common flaws to draw from: "
        "'total scripts dispensed' (not normalized), 'avg time to fill' (skewed, median better), "
        "'manual touch volume' (should be per 1000 scripts), 'number of rejected claims' (rate not count)."
    ),
    "metric_design": (
        "Generate a 'propose metrics for this feature' problem. Provide a generic pharmacy/care feature change (no company names). "
        "User answer style: BULLET LIST of 2 to 4 metric names. NO formulas required. NO rationale "
        "required. Match PAA Metrics Exercise format exactly: just named metrics like 'Conversion "
        "rate from search to purchase' / 'Number of items viewed per purchase'. The instructions "
        "field should say: 'Bullet list of 2 to 4 metric names. No formulas required. Aim for "
        "under 50 words total.' The reference_answer should be a bullet list of 3 to 5 metric "
        "names, nothing else. The rubric should reward (1) at least one metric tied to the stated "
        "goal, (2) normalization where appropriate, (3) variety across user behavior dimensions "
        "(time, money, actions, people)."
    ),
    "metric_diagnosis": (
        "Generate a 'metric behaved unexpectedly, explain why' problem. Provide a generic pharmacy/care scenario (no company names) "
        "with 2 metrics moving in a confusing way. User answer style: ONE SENTENCE naming the "
        "mechanism. Match PAA Metrics: 'The thumbnails are misleading (clickbait)'. The "
        "instructions field should say: 'One or two sentences: name the most likely mechanism.' "
        "The reference_answer should be 1 to 3 sentences. The rubric rewards correctly identifying "
        "the mechanism, not exhaustive enumeration of alternatives."
    ),
    "counter_metric_design": (
        "Generate a 'negative impact + counter-metric' problem. Provide a generic pharmacy/care feature change (no company names) "
        "with stated goal. User answer style: ONE PARAGRAPH (3 to 5 sentences) describing the "
        "negative consequence AND naming the counter-metric formula. Match PAA Experiment Design "
        "Exercises (eBay share button -> purchase completion rate). The instructions field should "
        "say: 'A few sentences: name the negative consequence, then name the counter-metric (with "
        "numerator/denominator) that catches it.' Reference answer 60 to 120 words."
    ),
    "experiment_critique": (
        "Generate a 'critique these proposed experiment metrics' problem. Provide a the pharmacy "
        "experiment with 4 to 6 proposed metrics where at least 2 are flawed (not normalized for "
        "cohort size, p-hacking risk from too many metrics or post-hoc subgroups, no counter-"
        "metric, vanity count instead of rate). User answer style: bulleted critique, one short "
        "line per metric (good or bad + why). Match PAA Section 2 lessons. The instructions field "
        "should say: 'Bullet list with one short critique per metric. Then suggest fixes.' "
        "Reference answer: 80 to 150 words as bullet list."
    ),
    "event_vs_user_property": (
        "Generate a 'should X be event property or user property?' problem. Provide a the pharmacy "
        "context. User answer style: ONE SENTENCE matching PAA Tracking Plans Exercise 1: "
        "'Event property, because user properties only hold the latest value.' The instructions "
        "field should say: 'One sentence: event or user property, plus the why.' Reference answer "
        "1 to 2 sentences. Rubric heavily rewards naming the historical-vs-latest tradeoff."
    ),
    "event_properties_design": (
        "Generate a 'what properties should we capture for this event?' problem. Provide a the pharmacy "
        "event name. User answer style: BULLET LIST of 3 to 6 property names. NO rationale "
        "required (one short rationale phrase optional). Match PAA Tracking Plans Exercise 2 "
        "(Uber Ride Completed -> ride_duration, ride_cost, ride_distance, ride_type). The "
        "instructions field should say: 'Bullet list of 3 to 6 property names.' Reference answer: "
        "just a bullet list. Rubric rewards (1) coverage of the obvious dimensions (time, money, "
        "category), (2) properties that unlock interesting segmentation."
    ),
    "user_properties_design": (
        "Generate a 'what user properties should we track for segmentation?' problem. Provide a "
        "the pharmacy product surface. User answer style: BULLET LIST of 4 to 6 user property names. "
        "Match PAA Tracking Plans Exercise 3 (dating app -> Gender, Sexual orientation, Age, "
        "Location, Interests). The instructions field should say: 'Bullet list of 4 to 6 user "
        "property names.' Reference answer: bullet list only. Rubric rewards properties that "
        "actually segment behavior, not vanity demographics."
    ),
    "tracking_plan_design": (
        "Generate a 'build a 3-event tracking plan for this feature' problem. Provide a the pharmacy "
        "feature. User answer style: 3 event names, with 0 to 3 properties bulleted under each. "
        "Match PAA Tracking Plans Exercise 4 (YouTube sharing: Share Button Clicked / Sharing "
        "Method Selected [share_method] / Content Successfully Shared [share_method]). The "
        "instructions field should say: '3 events with property names. No more than 3 events. "
        "No schemas, no descriptions.' Reference answer: under 80 words."
    ),
    "schema_design": (
        "Generate a SCHEMA DESIGN / DATA MODELING drill problem. This is FORM-graded "
        "(structured response, not free-form markdown) — the deliverable is a structured "
        "DESIGN PROPOSAL, not a query. "
        "The user practices reasoning about grain, fact/dim split, SCD types, dbt layer "
        "placement, idempotency under reversals, and test coverage. These are the modeling "
        "skills tested in a Staff Product Analyst interview, not GROUP BY mechanics.\n\n"
        "PAA TERSENESS RULE OVERRIDE: schema design answers are STRUCTURED, not terse. The "
        "PAA 'one sentence answer is full credit' calibration does NOT apply to this subtopic. "
        "Reference answers run 200 to 400 words across 4 to 6 headed sections. State this "
        "explicitly in the problem's `instructions` field so the grader sees it.\n\n"
        "ROTATE ACROSS THESE PROBLEM SHAPES (pick ONE per generation):\n"
        "  1. 'Build a claim-level fact from the raw event log' — given submitted/paid/"
        "rejected/reversed events at the event grain (multiple rows per claim_id), propose a "
        "fact_claim model at one-row-per-claim grain. The user states the fact columns "
        "(first_submit_ts, paid_ts, paid_amount, reversed_ts, net_paid_amount, final_status), "
        "which dim tables to join (dim_patient, dim_drug, dim_payer, dim_prescriber), how to "
        "handle the paid-then-reversed edge case (gross vs net columns), and how to handle "
        "late-arriving reversal events (re-stating closed periods or not).\n"
        "  2. 'Design the dbt model layer for X' — given a business question (e.g., 'daily "
        "FPAR by drug class for the ops dashboard'), the user proposes: (a) sources, (b) "
        "staging models, (c) intermediate models, (d) one mart model with grain stated, "
        "(e) what work each layer does and why business rules don't belong in stg_.\n"
        "  3. 'SCD type for these dims' — present 4 to 6 candidate dim tables (dim_patient, "
        "dim_drug, dim_payer, dim_prescriber, dim_pharmacy, dim_formulary). The user "
        "classifies each as SCD Type 1 / Type 2 / Type 0 with one-sentence rationale. "
        "Include at least one non-obvious case: dim_drug NDC reassignments, dim_payer "
        "plan-year boundaries, or dim_formulary quarterly tier changes.\n"
        "  4. 'Fact vs dim split' — given a wide raw event row with 12 to 15 columns "
        "(claim_id, patient_id, prescriber_id, payer_id, ndc, drug_class, days_supply, "
        "quantity_dispensed, paid_amount, copay, ingredient_cost, dispensing_fee, channel, "
        "fill_date, reject_reason), the user assigns each column to fact, a specific dim, or "
        "a junk dim, and names the surrogate-key strategy.\n"
        "  5. 'Grain decision under three reporting needs' — same raw events, three reporting "
        "needs at different grains (claim level for ops, patient-month for adherence, drug-"
        "class daily for finance). The user proposes whether to build one fact at the lowest "
        "grain and aggregate up via marts, or build three separate facts, with explicit "
        "trade-offs (storage, freshness, consistency, query complexity).\n\n"
        "PHARMACY DOMAIN ANCHORS (use these — never company names):\n"
        "  - Raw events: claim_events (event_type values: submitted, paid, rejected, "
        "recycled, reversed)\n"
        "  - Candidate dims with realistic SCD behavior:\n"
        "      dim_patient — Type 2 for address/plan, Type 1 for name/dob (rarely changes)\n"
        "      dim_drug — Type 1 for label, Type 2 if NDC reassignment matters for the metric\n"
        "      dim_payer — Type 2 for plan-year (formulary changes Jan 1)\n"
        "      dim_prescriber — Type 1 (NPI is stable)\n"
        "      dim_pharmacy — Type 1 (location id is stable)\n"
        "      dim_formulary — Type 2 (quarterly tier changes)\n"
        "  - Edge cases worth forcing in problem shapes 1 and 5: paid-then-reversed claims "
        "(idempotency), late-arriving reversal events (re-stating closed periods), multi-fill "
        "prescriptions (parent-child grain), drug NDC reassignment, partial fills.\n\n"
        "REQUIRED ADDITIONAL JSON FIELDS:\n"
        "  schema_ddl: CREATE TABLE statement(s) for the raw input table(s). Renderer\n"
        "    displays this as a schema TABLE. CRITICAL: do NOT put SQL line comments\n"
        "    (-- ...) INSIDE the column body — they leak into the rendered table as a\n"
        "    garbage row called `--`. Put any column-value notes (enum values, NULL\n"
        "    rules) in the `prompt` field as bullets, NOT as inline DDL comments.\n"
        "    Example of WRONG (don't do this):\n"
        "      CREATE TABLE claim_events (\n"
        "        event_type VARCHAR NOT NULL,\n"
        "        -- 'submitted' | 'paid' | 'rejected' | 'reversed'\n"
        "        event_ts TIMESTAMP NOT NULL\n"
        "      );\n"
        "    Example of RIGHT:\n"
        "      CREATE TABLE claim_events (\n"
        "        event_type VARCHAR NOT NULL,\n"
        "        event_ts TIMESTAMP NOT NULL\n"
        "      );\n"
        "    Then in `prompt`: 'event_type values: submitted, paid, rejected, reversed.'\n"
        "  candidate_dimensions: a list of dim tables the user can join to. Each entry:\n"
        "    {\"name\": \"dim_patient\", \"key\": \"patient_id\",\n"
        "     \"description\": \"patient demographics, address, plan info\"}.\n"
        "    Pick 4 to 7 dims relevant to this problem from the standard pharmacy\n"
        "    dim roster: dim_patient, dim_drug, dim_payer, dim_prescriber, dim_pharmacy,\n"
        "    dim_formulary, dim_geography, dim_time. The form's dim_joins multi-select\n"
        "    is built from this list, so the user picks from a fixed roster, not a\n"
        "    free-text guess.\n\n"
        "  stakeholder_asks: a list of 3 to 6 strings, each one a distinct stakeholder\n"
        "    request that the fact table must support. Phrase as the stakeholder would say\n"
        "    it: 'response rate by channel', 'median time-to-fill per drug class', 'count\n"
        "    of unanswered messages by care team member, weekly', etc. The form's pre-form\n"
        "    'translate the asks' exercise reads this list and asks the user to map each\n"
        "    ask to a fact column / dim FK / drill-down attribute. Each ask should map\n"
        "    cleanly to ONE deliverable (avoid compound asks like 'A and B').\n"
        "  field_hints: a dict mapping each form field id to a 1 to 2 sentence hint\n"
        "    SPECIFIC TO THIS PROBLEM. Field ids (12 total): business_process, grain,\n"
        "    fact_columns, key_strategy, dim_joins, scd_per_dim, conformed_dims,\n"
        "    models, tests, idempotency, late_arriving, edge_cases. Each hint anchors\n"
        "    the user's answer to the stakeholder asks. Example for business_process:\n"
        "      'For this problem, the business process is a patient outreach message\n"
        "       being sent and (sometimes) responded to. Every fact column should\n"
        "       describe the lifecycle of ONE message.'\n"
        "    Example for fact_columns:\n"
        "      'For this problem, you need three count columns (messages_sent,\n"
        "       responses_received, unanswered_count) plus first_response_ts. Each\n"
        "       count is a SUM at the patient-day-channel grain over the events.'\n"
        "    Example for dim_joins:\n"
        "      'The asks include filter-by-cohort and filter-by-channel and filter-by-\n"
        "       care-team-user, so you need dim_patient (for cohort), dim_channel, and\n"
        "       dim_care_team_user. dim_date adds calendar context for weekly rollups.'\n"
        "  worked_example_per_field: a dict mapping field id to a model answer for\n"
        "    THIS specific problem. STRUCTURED FORMAT REQUIRED — each value MUST be\n"
        "    a single string with two clearly labeled sections:\n\n"
        "      Answer: <the concise correct answer for this field on this problem>\n\n"
        "      Why: <2 to 4 sentence rationale in LAY LANGUAGE — no jargon. Explain\n"
        "      WHY this answer fits THIS problem. Reference the specific stakeholder\n"
        "      asks or volume hints from the prompt. Avoid copy-pasting the prompt\n"
        "      back; explain like you would to a junior analyst.>\n\n"
        "    Use plain English. Define jargon in parentheses on first use. The form's\n"
        "    walkthrough mode REPLACES the hint area with this content so the user\n"
        "    sees both the answer and the reasoning.\n\n"
        "    Example for grain field on a claim-level fact problem:\n"
        "      'Answer: one row per claim_id (~15M rows after 1 year).\\n\\nWhy:\n"
        "      The prompt explicitly says \"~15M claim rows after 1 year (one row\n"
        "      per unique claim_id)\" — that single sentence locks the grain. The\n"
        "      dashboard aggregates UP from claim-level (counts by partner, drug\n"
        "      class, etc), so storing pre-aggregated rows would freeze the slicing\n"
        "      and waste flexibility. Lower grain (event-level) would have multiple\n"
        "      rows per claim and break unique counts.'\n\n"
        "    Example for fact_columns on the same problem:\n"
        "      'Answer: claim_id (PK), patient_id, partner_id, drug_id, payer_id\n"
        "      (FKs), first_submit_ts, paid_ts, reversed_ts (timestamps),\n"
        "      gross_paid_amount, net_paid_amount (measures), final_status\n"
        "      (derived).\\n\\nWhy: Every metric the dashboard asked for can be\n"
        "      computed from these raw ingredients. FPAR = SUM(was_paid_first) /\n"
        "      SUM(was_submitted). Reversal Rate = SUM(reversed_ts is not null) /\n"
        "      SUM(paid_ts is not null). Median time-to-payment = MEDIAN(paid_ts -\n"
        "      first_submit_ts). Storing the rates as columns would lock the\n"
        "      slicing dimensions; storing raw counts and timestamps lets any BI\n"
        "      query slice by partner, drug, payer at query time.'\n\n"
        "PROMPT FORMAT (HARD RULES — schema_design only):\n"
        "The `prompt` field MUST be structured as FOUR labeled sections in this exact\n"
        "order. Section header on its own line. Bullets on their own lines starting\n"
        "with '\\n- ' (newline + dash + space). NEVER use ' - ' as an inline separator\n"
        "inside a single line — the renderer treats that as one sentence and the\n"
        "bullets visually collapse together.\n\n"
        "FOCUS: schema_design exercises are about FACT TABLE DESIGN. Dims are pre-built\n"
        "(per candidate_dimensions). The user designs the fact table that a dashboard\n"
        "reads from. The prompt MUST make this explicit (see YOUR TASK below).\n\n"
        "Section 1 — STAKEHOLDER CONTEXT:\n"
        "  STAKEHOLDER CONTEXT\n"
        "  \\n\n"
        "  You met with [team]. The fact table you're designing will populate a daily\n"
        "  dashboard. The dashboard needs:\n"
        "  \\n\n"
        "  - <metric 1>: <formula in plain language> by <ONE filter dim>\n"
        "  - <metric 2>: <formula> by <ONE filter dim>\n"
        "  - <metric 3>: <formula> by <ONE filter dim>\n\n"
        "  RULES for asks:\n"
        "    1. 3 to 5 asks. Each ask = ONE metric + ONE filter dim. NEVER combine\n"
        "       'by X and by Y' into a single ask — split into two asks.\n"
        "    2. Each ask MUST include a formula in plain language ('count of orders\n"
        "       with results_released event divided by count of shipped orders').\n"
        "       This tells the user EXACTLY what measure column they need to design.\n"
        "    3. Each filter dim must be ONE of the candidate_dimensions. Don't\n"
        "       reference a dim that isn't in the available list.\n\n"
        "Section 2 — VOLUME AND UPDATE FREQUENCY (REQUIRED):\n"
        "  VOLUME AND UPDATE FREQUENCY\n"
        "  \\n\n"
        "  - Daily source volume: ~<N> events per day\n"
        "  - Dashboard freshness need: <real-time / every 15 minutes / hourly / daily>\n"
        "  - Total fact rows after 1 year: ~<N> rows\n\n"
        "  These three numbers drive the materialization decision. Required so the\n"
        "  user can pick between table / incremental / view appropriately. Use realistic\n"
        "  numbers for the scenario (small daily-batch use cases: 1K-10K events/day;\n"
        "  high-volume claims: 100K-1M events/day).\n\n"
        "Section 3 — WHAT YOU HAVE IN SOURCE:\n"
        "  WHAT YOU HAVE IN SOURCE\n"
        "  \\n\n"
        "  - Source event table: `<table_name>` at event grain (one row per state change).\n"
        "  - dim_X: <attribute1>, <attribute2>, <attribute3>\n"
        "  - dim_Y: <attribute1>, <attribute2>\n"
        "  - dim_Z: <attribute1>\n\n"
        "  Just list dims and their attributes. NO 'yes' affirmations. NO redundant\n"
        "  phrasing like 'is already populated.' Every dim from candidate_dimensions\n"
        "  must appear here with its useful attributes.\n\n"
        "Section 4 — YOUR TASK:\n"
        "  YOUR TASK\n"
        "  \\n\n"
        "  Design the FACT TABLE that the dashboard reads from. Dims are already\n"
        "  built — you specify how to JOIN them and what SCD type each is. Use the\n"
        "  response form in section 2 to record your design choices.\n\n"
        "Do NOT inline column lists in the prompt — the schema_ddl block is the\n"
        "canonical source for source columns and types. The prompt's job is to\n"
        "convey stakeholder intent and constraints (volume, frequency), not duplicate\n"
        "the schema.\n\n"
        "INSTRUCTIONS field for the user's answer (set this in the JSON):\n"
        "  'Fill out each form field in section 2 (the schema design response form). "
        "Dropdowns are used where the answer set is finite (SCD types, idempotency strategies, "
        "late-arriving handling); text fields for grain, fact columns, and rationale. Click "
        "Get Schema Design Feedback to grade.'\n\n"
        "RUBRIC AXES (5 criteria, 20 pts each, summing to 100 — pick the 4 to 5 most "
        "applicable to the problem shape and adjust weights to sum to 100):\n"
        "  - Grain: states OUTPUT grain explicitly ('one row per ___'); states INPUT grain "
        "if the problem requires a grain shift; rationale ties grain to the business question\n"
        "  - Fact/dim split: correct columns assigned to fact vs each dim; surrogate key "
        "strategy named where applicable; conformed dims identified across multiple facts\n"
        "  - SCD type reasoning: Type 1/Type 2 choice fits the column's update behavior; "
        "rationale references whether history is needed for the metric or not\n"
        "  - dbt layer placement: source/stg_/int_/mart_ assignments correctly map to the work "
        "each layer does (cleanup vs reusable joins vs business-rule aggregations)\n"
        "  - Edge cases + tests: at least one realistic edge case named (reversals, late "
        "arrivals, NDC reassignment, multi-fill); at least 2 dbt tests proposed with the "
        "specific column they apply to\n\n"
        "REFERENCE ANSWER LENGTH: 200 to 400 words across 4 to 6 headed sections. The voice "
        "is structured-design-doc, not prose narrative. Markdown tables and ASCII sketches "
        "are welcome where they communicate faster than prose. The PAA terseness rule does "
        "NOT apply.\n\n"
        "EXPECTED_THEMES (8 to 12 short anchors): grain (one row per __), fact-dim split, "
        "SCD Type 2, surrogate key, dbt staging vs marts, conformed dim, idempotency under "
        "reversals, late-arriving facts, dbt tests (unique/not_null/relationships), incremental "
        "materialization, junk dim — pick 8 to 12 that match the chosen problem shape.\n\n"
        "COMMON_MISTAKES should mention: declaring grain without justifying it, ignoring "
        "reversals (paid-then-reversed nets to $0, not $X), conflating Type 1 and Type 2 dims, "
        "putting business rules in staging models, omitting tests, not naming surrogate keys, "
        "treating all dims as Type 1 to avoid SCD complexity."
    ),
    # ---- Version Control (Git for analytics) ----
    "branching_strategy": (
        "Generate a Git BRANCHING STRATEGY drill problem for an analytics team working on a "
        "shared dbt repo. Markdown-graded design-doc style.\n\n"
        "PAA TERSENESS RULE OVERRIDE: branching strategy answers are STRUCTURED, not terse. "
        "State this in the `instructions` field so the grader sees it.\n\n"
        "PROBLEM SHAPES (rotate, pick ONE per generation):\n"
        "  1. 'Design the branching strategy for an analytics team of N (3 to 8) analysts "
        "working on a shared dbt repo with daily prod runs.' User proposes: branch naming, "
        "what merges to main, dev/staging/prod environments, who reviews PRs, how dbt CI "
        "fits in.\n"
        "  2. 'Critique this team's existing strategy.' Provide a flawed setup (e.g., "
        "everyone commits to main, long-lived shared feature branches, no PR review on "
        "analytics work, dev branch that's months out of date with main). User flags the "
        "problems and proposes the fix.\n"
        "  3. 'Adapt strategy for a hotfix scenario.' Team has a long feature branch "
        "in progress, a prod model just broke and needs an emergency fix. User describes "
        "the branch flow (cherry-pick from feature branch? hotfix branch off main? what "
        "merges where?).\n\n"
        "DOMAIN ANCHOR: pharmacy / digital health analytics team using dbt + Snowflake or "
        "Postgres + GitHub. References to GitHub Actions, dbt Cloud, or dbt-core CLI are "
        "fine. Generic descriptors only — no real company names.\n\n"
        "INSTRUCTIONS for user's answer: 'Markdown answer with headed sections (## Branch "
        "naming, ## What merges where, ## Environments, ## PR review process, ## CI). "
        "Aim for 200 to 400 words. Branching strategy answers are STRUCTURED — multiple "
        "short sections beat one long paragraph.'\n\n"
        "RUBRIC AXES (4 criteria, 25 pts each):\n"
        "  - Names a recognizable workflow pattern (trunk-based, GitHub flow, GitLab flow, "
        "git-flow) and matches the team size to it correctly\n"
        "  - Specifies which branch is the deployment source for each environment "
        "(dev / staging / prod), and what triggers each environment build\n"
        "  - Defines PR review process (who reviews, what they check, when CI runs)\n"
        "  - Handles environment isolation in dbt context (per-developer schemas, dbt "
        "target switching, no cross-developer schema collisions)\n\n"
        "EXPECTED_THEMES: trunk-based development, GitHub flow, feature branch, PR review, "
        "dbt schema isolation, CI on PR, protected main branch, squash merge, environment "
        "promotion. Pick 6 to 10.\n\n"
        "COMMON_MISTAKES: long-lived shared feature branches, no PR review on analytics "
        "work, single shared dev schema causing collisions, manually deploying to prod "
        "without CI, no protected branches."
    ),
    "merge_conflict_resolution": (
        "Generate a MERGE CONFLICT RESOLUTION drill where the user reads a Git conflict "
        "block in a SQL or dbt model file and decides how to resolve it. Markdown-graded.\n\n"
        "PROBLEM SHAPE: provide a conflict block in the `prompt` field, like:\n"
        "  ```\n"
        "  <<<<<<< HEAD (main)\n"
        "  WITH paid_claims AS (\n"
        "      SELECT claim_id, paid_amount FROM stg_claim_events\n"
        "      WHERE event_type = 'paid' AND paid_amount > 0\n"
        "  )\n"
        "  =======\n"
        "  WITH paid_claims AS (\n"
        "      SELECT claim_id, paid_amount, payer_id FROM stg_claim_events\n"
        "      WHERE event_type = 'paid'\n"
        "  )\n"
        "  >>>>>>> feature/add-payer-segmentation\n"
        "  ```\n"
        "User explains: (a) what each side is doing differently, (b) which side to keep "
        "OR how to merge both intents, (c) what tests they'd add to confirm the resolution, "
        "(d) the git commands to finish the resolution.\n\n"
        "ROTATE THE TYPE OF CONFLICT (pick ONE per generation): a column added on one side, "
        "a filter loosened on one side, a CTE renamed on one side, a join changed from LEFT "
        "to INNER on one side, a window function partition changed on one side.\n\n"
        "DOMAIN ANCHOR: pharmacy claim_events, prescriptions, dim_patient — realistic dbt "
        "model code.\n\n"
        "INSTRUCTIONS: 'Markdown answer with sections: ## What each side is doing, "
        "## My resolution and why, ## Tests to add, ## Git commands to finish. Include the "
        "resolved SQL in a fenced code block. 150 to 300 words.'\n\n"
        "RUBRIC AXES (4 criteria, 25 pts each):\n"
        "  - Correctly diagnoses what each side of the conflict was trying to do\n"
        "  - Resolution preserves both intents OR justifies dropping one with clear reason "
        "(not just 'keep mine')\n"
        "  - Names a specific test to add (unique, not_null, accepted_values, "
        "expression_is_true) on the column or row count that's now at risk\n"
        "  - Names the right git commands to finish (git add, git commit, NO --force on "
        "shared branches)\n\n"
        "EXPECTED_THEMES: conflict markers, both intents preserved, dbt test, git add, "
        "git commit, no force push, regression risk. Pick 5 to 8.\n\n"
        "COMMON_MISTAKES: blindly keeping one side, force-pushing to a shared branch, "
        "skipping the test add, marking conflict resolved without actually editing the file."
    ),
    "rebase_vs_merge": (
        "Generate a REBASE vs MERGE decision drill. Provide a scenario; user states "
        "rebase or merge, and why. Markdown-graded.\n\n"
        "PAA TERSENESS APPLIES HERE: a correct 2 to 4 sentence answer naming the right "
        "choice and citing the right reason is FULL CREDIT. Do not require a long essay.\n\n"
        "PROBLEM SHAPES (rotate):\n"
        "  1. 'Long-running feature branch behind main by 30 commits — bring it up to date.' "
        "(Answer: rebase, to keep history linear and replay your changes on top of latest.)\n"
        "  2. 'Public shared feature branch with 2 collaborators — bring it up to date.' "
        "(Answer: merge, because rebasing rewrites history that others have based work on.)\n"
        "  3. 'About to merge a PR with 12 messy WIP commits — finalize before merge.' "
        "(Answer: interactive rebase to squash, or use squash-merge.)\n"
        "  4. 'Pull just downloaded 5 commits from main while you have 3 unpushed — finish.' "
        "(Answer: rebase your 3 commits on top of the 5, OR merge depending on team norm.)\n"
        "  5. 'You and a teammate both pushed to feature/x; now you can't push.' (Answer: "
        "pull --rebase or merge from origin/feature/x first; do NOT force-push.)\n\n"
        "INSTRUCTIONS: '2 to 4 sentences naming the choice (rebase, merge, or squash-merge) "
        "and the specific reason. Code commands welcome but optional.'\n\n"
        "RUBRIC AXES (3 criteria summing to 100):\n"
        "  - Names the correct choice for the scenario (40 pts)\n"
        "  - Cites the right reason: shared-history rule, history readability, conflict "
        "frequency, or merge-commit noise (35 pts)\n"
        "  - Avoids the dangerous option for the scenario (e.g., does NOT recommend "
        "force-push or rebase on a public branch with collaborators) (25 pts)\n\n"
        "EXPECTED_THEMES: rebase, merge, squash, never rebase shared history, linear "
        "history, force-push risk, --rebase pull. Pick 4 to 6.\n\n"
        "COMMON_MISTAKES: rebasing a public branch others have based work on, force-pushing "
        "to a shared branch, recommending merge when squash would be cleaner, ignoring the "
        "team-norm question."
    ),
    "pr_review_critique": (
        "Generate a PR REVIEW CRITIQUE drill where the user reads a small mock PR diff "
        "(SQL or dbt model) and flags issues. Markdown-graded.\n\n"
        "PROBLEM SHAPE: include a 15 to 40 line mock diff in the `prompt` field showing "
        "EITHER a new dbt model OR a modification to an existing one. The diff MUST contain "
        "2 to 4 review-worthy issues. Rotate across these issue types so the user sees them "
        "all eventually:\n"
        "  - Hardcoded raw table reference instead of `{{ ref('stg_x') }}` or `{{ source(..) }}`\n"
        "  - Missing schema.yml test on a key column (unique, not_null, relationships)\n"
        "  - Layering violation: business logic in stg_, or raw cleanup in mart_\n"
        "  - SELECT * in a staging model (no rename, no cast)\n"
        "  - Window function with a missing PARTITION BY that produces wrong results\n"
        "  - LEFT JOIN where INNER would have been correct (or vice versa)\n"
        "  - Column added to fact without updating downstream marts\n"
        "  - Hardcoded date filter (`WHERE event_date >= '2024-01-01'`) instead of a dynamic one\n"
        "  - No commit message context, force-push to feature branch with collaborators\n"
        "  - Missing exposures.yml entry for a model used by a dashboard\n\n"
        "INSTRUCTIONS: 'List 2 to 4 issues. For each: (a) what's wrong (1 line), (b) the "
        "fix (1 line), (c) optional severity (blocker / major / nit). Bullets fine.'\n\n"
        "RUBRIC AXES (4 criteria, 25 pts each, summing to 100):\n"
        "  - Identifies the highest-severity issue in the diff (the blocker)\n"
        "  - Names a specific fix for each issue (not 'fix it' — actual code or command)\n"
        "  - Distinguishes blockers from nits — does NOT bury a real bug under style nits\n"
        "  - Uses dbt vocabulary correctly (ref, source, materialization, schema.yml, "
        "exposure) where the issue calls for it\n\n"
        "EXPECTED_THEMES: ref(), source(), schema.yml test, layering violation, blocker vs "
        "nit, specific fix, materialization. Pick 5 to 8.\n\n"
        "COMMON_MISTAKES: only catching style issues and missing the bug, vague fixes "
        "('add a test'), confusing dbt staging vs mart concerns, demanding rewrites for "
        "stylistic preferences."
    ),
    "commit_message_critique": (
        "Generate a COMMIT MESSAGE CRITIQUE / REWRITE drill. Provide a vague or bad commit "
        "message (and optionally the diff it accompanies). User critiques it and rewrites "
        "a better one. Markdown-graded.\n\n"
        "PAA TERSENESS APPLIES: a good answer is 3 to 6 lines total (critique + rewritten "
        "message). Do not require an essay.\n\n"
        "PROBLEM SHAPES (rotate):\n"
        "  1. Vague message: 'fix' or 'updates' or 'changes' — user notes the message tells "
        "you nothing and rewrites with subject + why-not-what body.\n"
        "  2. WIP message that survived: 'wip' or 'temp' — user explains why this is "
        "unacceptable on main and rewrites.\n"
        "  3. Subject too long: 90+ char subject. User explains the 50/72 convention and "
        "rewrites with proper subject + body.\n"
        "  4. Lies about scope: 'Fix typo' on a 200-line refactor. User notes the "
        "mismatch and rewrites accurately.\n"
        "  5. Missing context: 'Add not_null test' with no reason. User adds the WHY "
        "(prod broke because patient_id was NULL on 0.3% of rows).\n\n"
        "INSTRUCTIONS: '2 to 3 sentence critique + a rewritten commit message in the "
        "conventional format (subject line under 50 chars, blank line, body wrapped at 72 "
        "chars explaining the why).'\n\n"
        "RUBRIC AXES (3 criteria summing to 100):\n"
        "  - Critique correctly identifies the specific failure (vague, WIP, mismatched "
        "scope, no context, etc) (35 pts)\n"
        "  - Rewritten subject is under 50 chars and tells you what changed at a glance "
        "(35 pts)\n"
        "  - Rewritten body explains WHY (the bug it fixes, the question it answers), not "
        "WHAT (which is in the diff) (30 pts)\n\n"
        "EXPECTED_THEMES: 50/72 convention, subject describes change, body explains why, "
        "no WIP on main, scope matches diff. Pick 4 to 6.\n\n"
        "COMMON_MISTAKES: rewriting subject to a longer rambling line, putting the WHAT in "
        "the body (it's in the diff), no body at all on a non-trivial commit, present "
        "tense vs imperative mood inconsistency."
    ),
    "revert_strategy": (
        "Generate a REVERT STRATEGY drill. Scenario: a bad commit was pushed to a shared "
        "branch (often main) and is now causing problems. User picks the right command and "
        "explains the trade-offs. Markdown-graded.\n\n"
        "PROBLEM SHAPES (rotate):\n"
        "  1. 'Bad commit pushed to main 10 minutes ago, no one else has pulled yet.' "
        "(Both git revert and git reset --hard then force-push are technically possible; "
        "git revert is safer because pulls are unpredictable.)\n"
        "  2. 'Bad commit pushed to main yesterday, downstream teams have already pulled.' "
        "(git revert ONLY — reset would rewrite history others depend on.)\n"
        "  3. 'Bad commit on a feature branch you alone work on.' (git reset --hard + "
        "force-push is fine; git revert also fine.)\n"
        "  4. 'Bad commit broke prod dbt run; need to fix forward AND ensure history is "
        "clean.' (Revert + add a test + commit message naming the failed run.)\n"
        "  5. 'Accidentally committed a secret to a public branch.' (Revert is NOT enough — "
        "the secret is in history; rotate the secret, then BFG/filter-repo to scrub.)\n\n"
        "INSTRUCTIONS: '3 to 5 sentences naming the right command (git revert vs git reset "
        "vs filter-repo vs rotate the secret), the reason, and any follow-up steps. Code "
        "commands welcome.'\n\n"
        "RUBRIC AXES (3 criteria summing to 100):\n"
        "  - Names the correct command for the scenario (40 pts)\n"
        "  - Identifies the shared-history risk: does NOT recommend force-push or reset on "
        "a branch others have pulled (35 pts)\n"
        "  - Names a sensible follow-up: a test that would have caught it, a notification "
        "to downstream teams, secret rotation if applicable (25 pts)\n\n"
        "EXPECTED_THEMES: git revert, git reset --hard, never force-push shared, secrets "
        "stay in history, BFG / filter-repo, regression test, downstream notification. "
        "Pick 4 to 7.\n\n"
        "COMMON_MISTAKES: recommending git reset on a shared branch, thinking git revert "
        "removes the bad commit from history (it doesn't — it adds an inverse commit), "
        "missing the secret-rotation step on the secret-leak scenario."
    ),
    "git_state_diagnose": (
        "Generate a 'YOU'RE STUCK IN THIS GIT STATE' troubleshooting drill. Provide a "
        "terminal output snippet or a state description; user identifies what's happening "
        "and the command to get unstuck. Markdown-graded.\n\n"
        "PAA TERSENESS APPLIES: a correct 2 to 4 sentence answer naming the state and the "
        "fix command IS full credit.\n\n"
        "PROBLEM SHAPES (rotate):\n"
        "  1. Detached HEAD after `git checkout <commit_sha>` — user names the state and "
        "explains how to get back to a branch (`git switch -c <branch>` to save work, or "
        "`git switch main` to discard).\n"
        "  2. Mid-rebase with a conflict — user explains the options: continue (after "
        "resolving), skip (drop this commit), abort (back to pre-rebase state).\n"
        "  3. 'Your branch and origin/main have diverged. Pull cannot fast-forward.' — "
        "user names the cause (commits on both sides) and the resolution (rebase pull, "
        "merge pull, or reset to origin if local commits aren't worth keeping).\n"
        "  4. Local changes block a checkout/pull — user names stash, commit, or discard "
        "as the three options with trade-offs.\n"
        "  5. 'I committed to the wrong branch.' — user names the recovery: cherry-pick "
        "the commit to the right branch, then reset the wrong branch.\n"
        "  6. 'I deleted a branch that had unmerged work.' — user names `git reflog` as "
        "the recovery tool and the steps to restore.\n\n"
        "INSTRUCTIONS: '2 to 4 sentences naming (a) what state Git is in, (b) the command "
        "to fix it, (c) what the command does. Code commands required.'\n\n"
        "RUBRIC AXES (3 criteria summing to 100):\n"
        "  - Correctly names the Git state (detached HEAD, mid-rebase, diverged, etc) "
        "(35 pts)\n"
        "  - Provides the correct command (40 pts)\n"
        "  - Explains briefly what the command does so the candidate isn't just memorizing "
        "(25 pts)\n\n"
        "EXPECTED_THEMES: detached HEAD, git reflog, git stash, rebase --continue, "
        "rebase --abort, cherry-pick, fast-forward not possible. Pick 4 to 6.\n\n"
        "COMMON_MISTAKES: panicking and force-pushing, deleting and recloning when reflog "
        "would have recovered the work, blindly running `git reset --hard` and losing "
        "uncommitted changes."
    ),
    "prd_impact_measurement": (
        "Generate a 'write the impact measurement section of a PRD' problem. Provide a the pharmacy "
        "feature with a stated goal. User answer style: 3 short sections matching PAA Tracking "
        "Plans Exercise 5 EXACTLY:\n"
        "  Product Performance Metrics\n"
        "  - <metric 1>\n"
        "  - <metric 2>\n"
        "  - <metric 3>\n"
        "  Questions We Want To Answer\n"
        "  - <question 1>\n"
        "  - <question 2>\n"
        "  - <question 3>\n"
        "  Tracking Plan\n"
        "  [Link to tracking plan]\n"
        "Total under 100 words. The instructions field should say: 'Three sections in markdown: "
        "Product Performance Metrics (3-5 bullets), Questions We Want To Answer (3-5 bullets), "
        "Tracking Plan (link placeholder is fine). Total under 100 words.'"
    ),
}


def _build_kpi_user_prompt(category: str, subtopic: str, scenario: str,
                           last_error: Optional[str] = None) -> str:
    label = subtopic_label(category, subtopic)
    g = (
        f"Generate a Product Metrics & KPIs drill problem.\n"
        f"Subtopic: {label}\n"
        f"Industry scenario anchor (use this domain, no company names): {scenario}\n\n"
        f"Subtopic instruction:\n{KPI_SUBTOPIC_GUIDANCE.get(subtopic, '')}\n"
    )
    # Per subtopic extra guidance for the new fields the form expects.
    if subtopic == "metric_critique":
        g += (
            "\n\nADDITIONAL FIELDS REQUIRED FOR metric_critique:\n"
            "  - proposed_metric: the EXACT name of the metric the stakeholder "
            "is proposing, written as a noun phrase the form can display "
            "directly (e.g., 'Total Refills Picked Up After Nudge Sent', "
            "'Match Acceptance Rate'). This must match the metric named in the "
            "prompt text. Do NOT use the problem title here — that is a different "
            "string.\n"
            "  - stakeholder_rationale: ONE sentence (max 25 words) explaining "
            "what the stakeholder THINKS this metric tells them about the "
            "scenario's purpose. Write it as the stakeholder would defend it. "
            "The metric you propose for them to critique MUST plausibly attempt "
            "to address the scenario's purpose, even though it has a flaw the "
            "learner is supposed to find. Do NOT propose a metric that has no "
            "connection to the scenario.\n"
            "  - metric_critique_picks: a dict with three keys 'numerator', "
            "'denominator', 'guardrail'. Each value is a list of 3 to 5 "
            "objects of shape {'label': '...', 'value': '...'}. The "
            "labels are options the learner will pick from in dropdowns when "
            "they propose a fix. Include at least one option that maps to the "
            "correct answer per the rubric, plus 2 to 4 plausible-but-wrong "
            "options to make the choice non trivial. value is a short snake "
            "case identifier (e.g., 'messages_per_match').\n"
            "Example metric_critique_picks for a messaging engagement problem:\n"
            "  'metric_critique_picks': {\n"
            "    'numerator': [\n"
            "      {'label': 'First messages sent after a Match connection', 'value': 'first_messages'},\n"
            "      {'label': 'Total messages sent in the period', 'value': 'total_messages'},\n"
            "      {'label': 'Reply messages', 'value': 'reply_messages'}\n"
            "    ],\n"
            "    'denominator': [\n"
            "      {'label': 'Match connections in the period', 'value': 'match_connections'},\n"
            "      {'label': 'Active users in the period', 'value': 'active_users'}\n"
            "    ],\n"
            "    'guardrail': [\n"
            "      {'label': 'Message response rate after first message', 'value': 'response_rate'},\n"
            "      {'label': 'Conversation depth', 'value': 'conversation_depth'}\n"
            "    ]\n"
            "  }\n"
            "NOTE: Use single quotes in the example above as illustration only. "
            "Emit valid JSON with double quotes in the actual output object.\n"
            "\n"
            "  - metric_movers: a list of 6 to 8 candidate reasons this metric "
            "could move (up or down) in the next reporting period. Each row "
            "is an object with these keys:\n"
            "      reason: the candidate reason. MUST follow this template: "
            "'[General pattern phrased generically that could transfer to other "
            "problems] (e.g., [specific anchor tied to THIS problem])'. The "
            "general pattern is the transferable lesson; the parenthetical "
            "anchor makes it concrete. Good: 'A delivery channel reach shrank "
            "(e.g., SMS opt-in fell after carrier filtering)'. Bad: 'SMS opt-in "
            "rate dropped due to carrier filtering changes' — too specific, no "
            "transferable pattern. Bad: 'Population' — too vague, no anchor.\n"
            "      tag: one of the 5 pattern tags ('Population', 'Quality', "
            "'Mix', 'Measurement', 'External') or the em dash '—' for "
            "distractors that do not actually apply\n"
            "      applies: boolean. True if this reason actually could move "
            "the metric in this scenario; False if it is a distractor.\n"
            "      explanation: ONE sentence explaining why it applies or why "
            "it does not.\n"
            "Include 4 to 6 rows where applies=True (covering different tags "
            "from the 5 category list) and 2 to 3 distractors where applies=False. "
            "Distractors should sound plausible but actually not move the metric "
            "(e.g., a cosmetic change in an unrelated flow, a feature launched for "
            "a different user segment, an event that would move a different "
            "metric).\n"
            "Example metric_movers row: {'reason': 'Per pair quality of the "
            "match algorithm changed (e.g., Match Score regressed, lowering "
            "messages per pair)', 'tag': 'Quality', 'applies': true, "
            "'explanation': 'Worse matches send fewer messages per pair, "
            "dropping the per user rate even with the same user base.'}\n"
        )
    elif subtopic == "metric_design":
        g += (
            "\n\nADDITIONAL FRAMING FOR metric_design:\n"
            "Frame the prompt so the learner walks the full Product Analytics "
            "Academy framework: Goal (Step 1, one sentence user goal), Signal "
            "(Step 2, success + failure observable behaviors), Metric (Step 3, "
            "numerator + denominator + statistic + time window), Layer three "
            "types (Step 4, primary + guardrail + counter), Pressure Test "
            "(Step 5, the 5 checks). Include a stakeholder_rationale field "
            "explaining what the team is trying to learn from this feature, "
            "so the learner has a concrete user goal to anchor Step 1.\n"
        )
    if last_error:
        g += f"\n\nPREVIOUS ATTEMPT FAILED:\n{last_error}\nFix and return the JSON object."
        if "Could not parse JSON" in last_error:
            g += (
                "\n\nThe JSON parse failure usually means your prior response was "
                "truncated mid-JSON or had prose around the JSON object.\n"
                "  - Emit ONE single ```json fenced block. NO prose before, NO prose "
                "after, NO second code block.\n"
                "  - Tighten the response: keep field_hints to ONE sentence each, "
                "keep worked_example_per_field to 1 to 3 lines each, keep "
                "candidate_dimensions descriptions to 1 short sentence each, keep "
                "the prompt's STAKEHOLDER CONTEXT bullets to ~10 words each.\n"
                "  - Inside JSON string values, escape internal double quotes as \\\" "
                "and use literal \\n for newlines; do not embed unescaped newlines "
                "in JSON strings.\n"
            )
    else:
        g += "\nReturn the JSON object now."
    return g


_BANNED_RUBRIC_PHRASES = (
    "thoroughness", "depth of analysis", "completeness", "thoughtful",
    "well-reasoned", "demonstrates strong thinking", "shows understanding",
    "comprehensive coverage", "appropriate framing", "professional tone",
    "polished writing", "good thinking", "quality of analysis",
)


def _validate_kpi_problem(problem: Dict[str, Any]) -> Tuple[bool, str]:
    required = ["title", "scenario", "prompt", "instructions", "expected_themes",
                "reference_answer", "grading_rubric", "hints"]
    for key in required:
        if key not in problem:
            return False, f"Missing required field: {key}"

    # schema_design has additional required fields for the form-based UX:
    # candidate_dimensions (drives the dim_joins checkboxes),
    # stakeholder_asks (drives the translate-the-asks pre-form exercise),
    # field_hints (problem-specific hint per field), and
    # worked_example_per_field (powers walkthrough mode).
    sub = problem.get("_meta", {}).get("subtopic")
    if sub == "schema_design":
        # Note: _meta is set AFTER validation, so we can't use it here. We detect
        # schema_design by the presence of candidate_dimensions or schema_ddl —
        # both are required for schema_design but absent for other KPI subtopics.
        pass
    sd_indicators = (
        problem.get("candidate_dimensions") is not None
        or "fact" in (problem.get("title", "") or "").lower()
        or "schema" in (problem.get("title", "") or "").lower()
    )
    # Heuristic: enforce these fields when the problem looks like schema_design.
    # The generator dispatch is the actual source of truth, but at validation
    # time we may not know the subtopic yet (added to _meta after validation).
    REQUIRED_SD_FIELDS = ("candidate_dimensions", "stakeholder_asks",
                          "field_hints", "worked_example_per_field", "schema_ddl")
    has_sd_field = any(k in problem for k in REQUIRED_SD_FIELDS)
    if has_sd_field or sd_indicators:
        # Looks like schema_design — enforce all 5 fields
        for key in REQUIRED_SD_FIELDS:
            if key not in problem:
                return False, (
                    f"Missing required schema_design field: '{key}'. The form needs "
                    f"candidate_dimensions (for dim checkboxes), stakeholder_asks "
                    f"(for translate exercise), field_hints (per-field hints), "
                    f"worked_example_per_field (for walkthrough mode), and "
                    f"schema_ddl (the source table)."
                )
        # Validate that field_hints and worked_example_per_field have all 11 field keys
        REQUIRED_FIELD_IDS = (
            "business_process", "grain", "fact_columns", "key_strategy",
            "dim_joins", "scd_per_dim", "conformed_dims", "models", "tests",
            "idempotency", "late_arriving", "edge_cases",
        )
        # candidate_edge_cases: list of problem-specific tricky scenarios that
        # the form's category-card edge-case step will pre-populate. Optional
        # for now — if absent, the user types their own from the 7 categories.
        fh = problem.get("field_hints", {}) or {}
        we = problem.get("worked_example_per_field", {}) or {}
        if not isinstance(fh, dict):
            return False, "field_hints must be a dict mapping field id to hint text."
        if not isinstance(we, dict):
            return False, "worked_example_per_field must be a dict mapping field id to worked example text."
        missing_hints = [k for k in REQUIRED_FIELD_IDS if not (fh.get(k) or "").strip()]
        missing_examples = [k for k in REQUIRED_FIELD_IDS if not (we.get(k) or "").strip()]
        if missing_hints:
            return False, (
                f"field_hints is missing entries for these field ids: {missing_hints}. "
                f"Every one of the 11 fields needs a problem-specific hint (1 to 2 "
                f"sentences) so the form's hint area is populated. Use these exact "
                f"keys: {list(REQUIRED_FIELD_IDS)}."
            )
        if missing_examples:
            return False, (
                f"worked_example_per_field is missing entries for these field ids: "
                f"{missing_examples}. Every one of the 11 fields needs a worked "
                f"example formatted as 'Answer: ...\\n\\nWhy: ...' so walkthrough "
                f"mode can show the answer + lay-language rationale. Use these "
                f"exact keys: {list(REQUIRED_FIELD_IDS)}."
            )
        # Validate stakeholder_asks
        asks = problem.get("stakeholder_asks", [])
        if not isinstance(asks, list) or len(asks) < 3:
            return False, "stakeholder_asks must be a list of 3 to 6 distinct asks."
        # Validate candidate_dimensions
        dims = problem.get("candidate_dimensions", [])
        if not isinstance(dims, list) or len(dims) < 3:
            return False, "candidate_dimensions must be a list of at least 3 dim entries."
        for d in dims:
            if not isinstance(d, dict) or not d.get("name") or not d.get("key"):
                return False, "Each candidate_dimensions entry must be a dict with 'name', 'key', and 'description'."
    rubric = problem.get("grading_rubric", [])
    if not isinstance(rubric, list) or len(rubric) < 2:
        return False, "grading_rubric must be a list of at least 2 criteria."
    total = sum(c.get("weight", 0) for c in rubric)
    if total != 100:
        return False, f"grading_rubric weights must sum to 100 (got {total})."
    themes = problem.get("expected_themes", [])
    if not isinstance(themes, list) or len(themes) < 2:
        return False, "expected_themes must be a list of at least 2 items."
    # Rubric quality floor: reject vague criteria
    vague_hits = []
    for c in rubric:
        crit_text = (c.get("criterion", "") + " " + c.get("description", "")).lower()
        for phrase in _BANNED_RUBRIC_PHRASES:
            if phrase in crit_text:
                vague_hits.append(f"criterion '{c.get('criterion','')}' uses banned phrase '{phrase}'")
                break
    if vague_hits:
        return False, (
            "grading_rubric criteria are too vague (would not let a grader decide "
            "pass/partial/fail consistently):\n  - "
            + "\n  - ".join(vague_hits)
            + "\nRewrite each criterion to reference a SPECIFIC concept from the problem "
            "(e.g., 'identifies the lack of normalization', 'names a counter-metric with "
            "numerator and denominator')."
        )
    return True, "Valid."


def generate_kpi_problem(category: str, subtopic: str, max_retries: int = 3,
                         on_attempt=None,
                         scenario_mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Generate a Product Metrics & KPIs problem (markdown answered).
    scenario_mode: None or 'random' for generic scenarios; 'booedup' to anchor
    the problem in the user's BooedUp dating app context."""
    scenario = _pick_scenario(scenario_mode)
    last_error = None
    # schema_design needs more tokens because the JSON spec demands multiple
    # extra fields (stakeholder_asks, candidate_dimensions, field_hints with 11
    # entries, worked_example_per_field with 11 entries, plus a multi-section
    # prompt). Default 3000 truncates mid-JSON.
    if subtopic == "schema_design":
        kpi_max_tokens = 6000
    else:
        kpi_max_tokens = 3000
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass
        user_prompt = _build_kpi_user_prompt(category, subtopic, scenario, last_error)
        user_prompt = apply_scenario_anchor(user_prompt, scenario_mode)
        text = _call_claude(KPI_GENERATOR_SYSTEM, user_prompt, max_tokens=kpi_max_tokens)
        parsed = _extract_json(text)
        if not parsed:
            last_error = "Could not parse JSON from response."
            continue
        parsed["_meta"] = {
            "category": category,
            "subtopic": subtopic,
            "kind": "kpi",
            "scenario": scenario,
            "scenario_mode": scenario_mode or "random",
            "generated_at": datetime.now().isoformat(),
            "problem_id": uuid.uuid4().hex[:12],
            "validation_attempts": attempt,
            "notebook": "nb02_analyst_interview_drills",
        }
        ok, err = _validate_kpi_problem(parsed)
        if ok:
            return parsed
        last_error = err
    print(f"KPI generation failed after {max_retries} attempts. Last error: {last_error}")
    return None


# ============================================================
# Top-level generator dispatch
# ============================================================

def generate_problem(category: str, subtopic: str, dialect: str = "postgresql",
                     max_retries: int = 4, on_attempt=None,
                     scenario_mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Dispatch to SQL, KPI, or multiple_choice generator based on the subtopic's
    effective kind (per-subtopic kind override takes precedence over category kind).
    scenario_mode is passed through so generators can anchor on a specific product
    (e.g., 'booedup' for the BooedUp dating app)."""
    kind = subtopic_kind(category, subtopic)
    if kind == "sql":
        return generate_sql_problem(category, subtopic, dialect=dialect,
                                    max_retries=max_retries, on_attempt=on_attempt,
                                    scenario_mode=scenario_mode)
    elif kind == "kpi":
        return generate_kpi_problem(category, subtopic, max_retries=max_retries,
                                    on_attempt=on_attempt, scenario_mode=scenario_mode)
    elif kind == "multiple_choice":
        return generate_multiple_choice_problem(category, max_retries=max_retries,
                                                on_attempt=on_attempt,
                                                scenario_mode=scenario_mode)
    else:
        raise ValueError(f"Unknown subtopic kind: {kind}")


# ============================================================
# KPI markdown grading
# ============================================================

KPI_GRADER_SYSTEM = """\
You are grading a learner's markdown answer to a Product Analytics drill problem.
The learner is preparing for a Staff Product Analyst interview in the pharmacy / digital health space.

CRITICAL CALIBRATION: this drill style mirrors Ali Baghshomali's Product Analytics Academy.
In that course, a CORRECT ONE SENTENCE ANSWER IS A FULL ANSWER. Examples of full credit:
  - 'Should be normalized. Ride Cancellation Rate is better.'
  - 'Event property, because user properties only hold the latest value.'
  - 'The thumbnails are misleading (clickbait).'
  - A bullet list of 3 metric names with no rationale.

Grade based on whether the learner identified the right concept, NOT whether they wrote a
lot. Length, prose vs bullets, and presence of formulas are NOT criteria. The reference_answer
in each problem is itself terse — use it to calibrate what 'full credit' looks like.

Output MUST be a single JSON object inside a ```json fenced block:
{
  "scores": [
    {"criterion": "<criterion name from rubric>", "weight": <weight>, "earned": <0..weight>, "feedback": "1-2 sentence rationale"},
    ...
  ],
  "total_score": <0..100>,
  "themes_hit": ["theme 1", ...],
  "themes_missed": ["theme N", ...],
  "what_was_strong": "1-2 sentences",
  "what_to_improve": "1-2 sentences with specifics. Cannot say 'add more detail' or 'be more thorough' as the only feedback — terseness is correct in this style.",
  "next_problem_focus": "what subtopic or skill the learner should drill next, 1 sentence"
}

Hard rules:
- For each rubric criterion, the earned points must be between 0 and the weight.
- total_score is the sum of earned across all criteria.
- themes_hit and themes_missed pull from the problem's expected_themes list.
- A correct, terse answer that hits the key concept should earn 80 to 100 percent. Reserve
  scores below 60 for answers that are wrong, off-topic, or miss the central concept.
- DO NOT penalize: bullet format, lack of formulas, lack of rationale paragraphs, brevity.
- DO penalize: missing the central concept (e.g., not naming normalization for a 'should
  be normalized' critique), naming a wrong mechanism, proposing metrics that don't tie to
  the stated goal, vanity counts where rates are required, ignoring stated outlier risk.
- Be specific in feedback. Cite the learner's words when calling out strengths or gaps.
- Do not invent themes that are not in expected_themes.
- If the learner's answer is empty or off-topic, score 0 and say so.
"""


SCHEMA_DESIGN_FORM_GRADER_SYSTEM = """\
You are grading a candidate's STRUCTURED FORM RESPONSE to a schema design / data
modeling drill problem. The candidate's response includes a `mode` field with
value either 'solve' or 'walkthrough'.

GRADING CALIBRATION BY MODE:

In SOLVE MODE the candidate attempted the problem blind without seeing the
worked answer. Grade strictly against the rubric: did they pick the right grain,
the right fact columns, the right SCD types, etc. Standard scoring.

In WALKTHROUGH MODE the candidate has been shown the worked answer (Answer +
Why in lay language) for each field and is paraphrasing it back to demonstrate
UNDERSTANDING, not problem-solving from scratch. Grade leniently against the
following different rubric:

  - Did the candidate's text demonstrate they READ and UNDERSTOOD the worked
    answer? Look for evidence of: correct concept names, the same grain choice,
    the same fact column structure (even if reworded), the same SCD pick, the
    same idempotency strategy.
  - Did they paraphrase in their own words (not pure copy-paste)? Detect
    copy-paste by checking if the response is a verbatim substring of the
    worked example. Pure copy-paste gets 50% credit (read but didn't process);
    a clear paraphrase gets full credit.
  - Are dropdown picks consistent with the worked answer? If the worked answer
    says 'natural key' and the candidate picked 'surrogate key' in the dropdown,
    they didn't read carefully — penalize that field.
  - Empty fields in walkthrough mode are NOT acceptable (they had the answer
    handed to them). Score 0 for empty fields.
  - In walkthrough mode, total scores 75-95 are typical when the candidate
    paraphrased competently. Reserve 95-100 for paraphrases that go BEYOND
    the worked example with additional correct insight.

Always note in `what_was_strong` and `what_to_improve` which mode the candidate
used so they can see how the calibration affected their score. The candidate filled out 11 fields covering grain, fact
columns, surrogate keys, dim joins, SCD type per dim, conformed dims, dbt models
(layer + materialization), per-model dbt tests, idempotency, late-arriving event
handling, and edge cases. Some answers are dropdowns (constrained values), some
are dicts (per-dim SCD picks, per-model tests), some are free text.

The form is universal across schema_design problem shapes, so the candidate may
have legitimately marked some fields as N/A or left them blank if they don't
apply to THIS particular problem. Read the problem prompt to decide which axes
are most relevant; weight rankings should reflect that.

Output MUST be a single JSON object inside a ```json fenced block:
{
  "scores": [
    {"criterion": "Business process", "weight": 8, "earned": 0..8, "feedback": "..."},
    {"criterion": "Grain", "weight": 12, "earned": 0..12, "feedback": "..."},
    {"criterion": "Fact columns", "weight": 12, "earned": 0..12, "feedback": "..."},
    {"criterion": "Surrogate vs natural key", "weight": 6, "earned": 0..6, "feedback": "..."},
    {"criterion": "Dim joins", "weight": 8, "earned": 0..8, "feedback": "..."},
    {"criterion": "SCD type per dim", "weight": 8, "earned": 0..8, "feedback": "..."},
    {"criterion": "Conformed dims", "weight": 4, "earned": 0..4, "feedback": "..."},
    {"criterion": "Models (layer + materialization)", "weight": 11, "earned": 0..11, "feedback": "..."},
    {"criterion": "dbt tests per model", "weight": 7, "earned": 0..7, "feedback": "..."},
    {"criterion": "Idempotency / re-run safety", "weight": 9, "earned": 0..9, "feedback": "..."},
    {"criterion": "Late-arriving / out-of-order events", "weight": 7, "earned": 0..7, "feedback": "..."},
    {"criterion": "Edge cases acknowledged", "weight": 8, "earned": 0..8, "feedback": "..."}
  ],
  "total_score": 0..100,
  "what_was_strong": "1-2 sentences citing the strongest field",
  "what_to_improve": "1-2 sentences naming the weakest field and concrete fix",
  "next_drill_focus": "1 sentence — what modeling skill to drill next"
}

Calibration per field:

GRAIN (20 pts):
- Full credit if the candidate names the OUTPUT grain explicitly ('one row per claim_id'
  or equivalent) AND acknowledges the INPUT grain shift (events collapse to claim).
- 12-16 pts if only output grain is stated.
- 0 pts if grain is empty, vague, or wrong (e.g., 'one row per event').

FACT COLUMNS (25 pts):
- Full credit if the candidate's response covers first_submit_ts, paid_ts, reversed_ts,
  gross_paid_amount, net_paid_amount, final_status (or near equivalents) AND distinguishes
  gross vs net (preserving audit trail vs throughput-ready).
- 15-20 pts if 4 of 6 columns named with reasonable types/sources.
- 0-10 pts if columns are missing or fundamentally wrong (e.g., storing event-level data).

DIMS AND SCD TYPE (20 pts):
- The form sends a structured dict mapping each candidate dim (dim_patient, dim_drug,
  dim_payer, dim_prescriber, dim_pharmacy, dim_formulary) to one of: skip / type0 / type1 /
  type2. Score the assignments against the realistic SCD behavior:
    dim_patient: Type 2 (address/plan changes) is best; Type 1 acceptable for thin patient dim
    dim_drug: Type 1 typical; Type 2 if NDC reassignment matters
    dim_payer: Type 2 (plan-year boundaries); Type 1 wrong
    dim_prescriber: Type 1 (NPI stable)
    dim_pharmacy: Type 1
    dim_formulary: Type 2 (quarterly tier changes)
- Skipping a dim is fine — not every problem needs every dim.
- Award full credit when the candidate joins at least 3 dims AND assigns at least one
  Type 2 correctly (dim_payer or dim_patient or dim_formulary).
- Rationale field adds clarity: a one-sentence rationale per joined dim is full credit;
  empty rationale caps at 12/20.

IDEMPOTENCY (20 pts):
- Full credit if the strategy choice (MERGE/UPSERT, window function, append+view, snapshot)
  fits the problem AND the rationale explains how it preserves gross_paid_amount while
  zeroing net_paid_amount on reversal.
- 10-15 pts if strategy is reasonable but rationale is missing or weak.
- 0-5 pts if strategy is wrong (e.g., 'just delete the reversed row' loses the audit trail).

LATE-ARRIVING (10 pts):
- Full credit if the strategy choice (re-state / correction row / snapshot lock / merge
  predicate) is reasonable AND rationale names a trade-off (consistency vs reproducibility
  vs storage cost).
- Half credit if strategy chosen but rationale weak.
- 0 if empty or strategy clearly wrong.

TESTS (5 pts):
- The form sends a list of selected tests. Full credit if the candidate selected AT LEAST
  2 tests AND at least one of them is a primary-key test (unique on claim_id, not_null
  on claim_id) AND at least one references a constraint relevant to the design (gross >=
  net, chronology of timestamps, accepted_values on final_status, or relationships).
- 2-3 pts if 2 tests selected but they're both trivial (e.g., not_null on claim_id and
  unique on claim_id — same idea, missing the design-specific check).
- 0 pts if fewer than 2 selected or none relevant.

Hard rules:
- Earned points must be between 0 and the criterion weight.
- total_score = sum of earned across all criteria.
- Be specific in feedback. Cite the candidate's actual words or dropdown picks.
- A correct concise answer beats a long vague one — reward clarity.
- If a field is empty, score 0 for that criterion and say 'left blank'.
"""


def grade_schema_design_form(
    problem: Dict[str, Any],
    form_responses: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Grade the schema_design 11-field structured form response against the rubric."""
    # Format SCD per dim as readable lines
    scd = form_responses.get("scd_per_dim", {}) or {}
    scd_block = "\n".join(f"  {dim}: {val or '(not picked)'}" for dim, val in scd.items()) or "(no dims picked)"

    # Format models as a small table
    models = form_responses.get("models", []) or []
    if models:
        model_lines = ["  | model_name | layer | materialization |"]
        for m in models:
            n = m.get("name", "(unnamed)")
            l = m.get("layer", "")
            mat = m.get("mat", "")
            model_lines.append(f"  | {n} | {l or '(no layer)'} | {mat or '(no mat)'} |")
        models_block = "\n".join(model_lines)
    else:
        models_block = "(no models defined)"

    # Format tests per model
    tests_per_model = form_responses.get("tests_per_model", {}) or {}
    tests_custom = form_responses.get("tests_custom_per_model", {}) or {}
    if tests_per_model or tests_custom:
        test_lines = []
        all_models = set(list(tests_per_model.keys()) + list(tests_custom.keys()))
        for mname in all_models:
            sels = tests_per_model.get(mname, []) or []
            custom = tests_custom.get(mname, "") or ""
            test_lines.append(f"  Tests for {mname}:")
            for s in sels:
                test_lines.append(f"    - {s}")
            if custom.strip():
                test_lines.append(f"    Custom: {custom.strip()}")
        tests_block = "\n".join(test_lines) if test_lines else "(no tests selected)"
    else:
        tests_block = "(no tests selected)"

    dim_picks = form_responses.get("dim_joins", []) or []
    dims_block = ", ".join(dim_picks) if dim_picks else "(none picked)"
    conformed = form_responses.get("conformed_dims", []) or []
    conformed_block = ", ".join(conformed) if conformed else "(none / N/A — single-fact drill)"

    candidate_dims = problem.get("candidate_dimensions", []) or []
    candidate_dims_block = ", ".join(d.get("name", "?") for d in candidate_dims if isinstance(d, dict)) or "(none provided)"

    # Format translate-the-asks pre-form exercise (if filled).
    # Two formats are supported: legacy single-dropdown (translate_picks) and the new
    # granular sub-field decomposition (translate_decomp).
    translate_picks = form_responses.get("translate_picks", {}) or {}
    translate_decomp = form_responses.get("translate_decomp", {}) or {}
    asks = problem.get("stakeholder_asks", []) or []
    translate_lines = []
    if asks and translate_decomp:
        for idx, ask in enumerate(asks):
            sub = translate_decomp.get(idx) or translate_decomp.get(str(idx)) or {}
            if isinstance(sub, dict) and any((v or "").strip() for v in sub.values()):
                parts = []
                for fk, label in (
                    ("numerator", "numerator"),
                    ("denominator", "denominator"),
                    ("filter_dim", "filter dim"),
                    ("drilldown", "drill-down attr"),
                    ("timestamp", "supporting ts"),
                ):
                    val = (sub.get(fk) or "").strip()
                    if val:
                        parts.append(f"{label}={val}")
                joined = "; ".join(parts) if parts else "(no sub-fields filled)"
                translate_lines.append(f"  Ask {idx + 1} ({ask}): {joined}")
            else:
                translate_lines.append(f"  Ask {idx + 1} ({ask}): (decomposition skipped)")
    elif asks and translate_picks:
        for idx, ask in enumerate(asks):
            pick = translate_picks.get(idx) or translate_picks.get(str(idx)) or "(not picked)"
            translate_lines.append(f"  Ask {idx + 1} ({ask}): {pick}")
    translate_block = "\n".join(translate_lines) if translate_lines else "(translate-the-asks exercise was skipped)"

    mode = (form_responses.get("mode") or "solve").strip()
    worked_examples = problem.get("worked_example_per_field", {}) or {}
    worked_block = ""
    if mode == "walkthrough" and worked_examples:
        # Include the worked examples so the grader can compare against the paraphrase
        worked_lines = []
        for fid, ex in worked_examples.items():
            if (ex or "").strip():
                worked_lines.append(f"  [{fid}]: {ex.strip()}")
        worked_block = (
            "---\nWORKED EXAMPLES SHOWN TO CANDIDATE (walkthrough mode — they read these "
            "and paraphrased below):\n" + "\n".join(worked_lines) + "\n\n"
        )

    # Format edge cases per category. New format = list of canned scenario picks
    # per category (no free text). Old format = dict of cat_id -> string.
    edge_cases_per_cat = form_responses.get("edge_cases_per_category", {}) or {}
    edge_cases_applies = form_responses.get("edge_cases_applies", {}) or {}
    edge_cat_lines = []
    if edge_cases_per_cat:
        for cat, val in edge_cases_per_cat.items():
            applies_flag = " (✓ applies)" if edge_cases_applies.get(cat) else ""
            if isinstance(val, list):
                if val:
                    picks = "; ".join(val)
                    edge_cat_lines.append(f"  [{cat}]{applies_flag}: {picks}")
            elif isinstance(val, str):
                if val.strip():
                    edge_cat_lines.append(f"  [{cat}]{applies_flag}: {val.strip()}")
    edge_cat_block = "\n".join(edge_cat_lines) if edge_cat_lines else "(no per-category edge cases provided)"

    user_prompt = (
        f"GRADING MODE: {mode}\n\n"
        f"Problem prompt:\n{problem.get('prompt','')}\n\n"
        f"Schema:\n{problem.get('schema_ddl','')[:1500]}\n\n"
        f"Candidate dimensions available for this problem: {candidate_dims_block}\n\n"
        f"Stakeholder asks (per problem.stakeholder_asks): {asks}\n\n"
        f"{worked_block}"
        f"---\nCandidate's pre-form translate-the-asks exercise:\n{translate_block}\n\n"
        f"---\nCandidate's 12-field form response:\n\n"
        f"(0) Business process:\n{form_responses.get('business_process','(empty)')}\n\n"
        f"(1) Grain — INPUT (source) grain:\n{form_responses.get('input_grain','(empty)')}\n"
        f"    OUTPUT (fact) grain:\n{form_responses.get('grain','(empty)')}\n\n"
        f"    Metrics classifier picks (per ask): {form_responses.get('metrics_classifier', {}) or '(none)'}\n\n"
        f"(2) Fact columns — supplemental text:\n{form_responses.get('fact_columns','(empty)')}\n"
        f"    SOURCE COLUMN CLASSIFIER PICKS (the candidate's PRIMARY fact column proposal):\n"
        f"    {form_responses.get('fact_columns_classifier', {}) or '(none — candidate did not classify source columns)'}\n\n"
        f"    GRADING NOTE: when the source column classifier has picks, treat them as the candidate's\n"
        f"    answer for fact_columns. Each source column with role=measure/timestamp/pivoted/pk/fk and\n"
        f"    include=yes is a proposed fact column. Score fact_columns based on classifier picks first;\n"
        f"    only fall back to the supplemental text if the classifier is empty.\n"
        f"    Each pivoted source column lists its 'pivoted_into' resulting columns (e.g.\n"
        f"    event_ts pivoted_into [order_placed_ts, shipped_ts, first_dose_ts, bundle_completed_ts]).\n"
        f"    Score the pivot completeness against the dashboard asks: each ask's required timestamps\n"
        f"    must appear in pivoted_into. Each measure column lists its 'measure_purpose' (numerator,\n"
        f"    denominator, compare_against, etc.) — use this to verify the candidate understands how\n"
        f"    each fact column powers a specific dashboard metric.\n\n"
        f"(3) Surrogate vs natural key strategy: {form_responses.get('key_strategy','(not picked)')}\n"
        f"    Rationale: {form_responses.get('key_rationale','(empty)')}\n\n"
        f"(4) Dim joins picked: {dims_block}\n"
        f"    Per-dim attribute usage selections (which attributes from each picked dim, and how):\n"
        f"    {form_responses.get('dim_attribute_usage', {}) or '(none — candidate did not specify attributes)'}\n\n"
        f"(5) SCD type per dim:\n{scd_block}\n"
        f"    Rationale: {form_responses.get('scd_rationale','(empty)')}\n\n"
        f"(6) Conformed dims: {conformed_block}\n"
        f"    Rationale: {form_responses.get('conformed_rationale','(empty)')}\n\n"
        f"(7) Models proposed:\n{models_block}\n\n"
        f"(8) dbt tests per model:\n{tests_block}\n\n"
        f"(9) Idempotency strategy: {form_responses.get('idempotency_strategy','(not picked)')}\n"
        f"    Rationale: {form_responses.get('idempotency_rationale','(empty)')}\n\n"
        f"(10) Late-arriving strategy: {form_responses.get('late_arriving_strategy','(not picked)')}\n"
        f"    Rationale: {form_responses.get('late_arriving_rationale','(empty)')}\n\n"
        f"(11) Edge cases — overall textarea:\n{form_responses.get('edge_cases','(empty)')}\n"
        f"     Per-category responses:\n{edge_cat_block}\n\n"
        f"---\nGRADING MODE for this submission: {mode}\n"
        f"Grade the candidate using the 11-axis rubric in the system prompt, applying "
        f"the calibration appropriate to the mode (strict for solve, paraphrase-focused "
        f"for walkthrough). Honor N/A picks as full credit when the axis is genuinely "
        f"not relevant to the problem (e.g., conformed dims is N/A for single-fact drills, "
        f"late-arriving is N/A for static-data drills). If the translate-the-asks exercise "
        f"was filled, weight the per-field grades slightly more positively when the "
        f"candidate's translate picks align with their later form responses (showing they "
        f"understood the mapping)."
    )
    text = _call_claude(SCHEMA_DESIGN_FORM_GRADER_SYSTEM, user_prompt, max_tokens=3000)
    return _extract_json(text)


def schema_design_form_grade_to_html(grade: Dict[str, Any]) -> str:
    """Render the schema_design form grade as HTML."""
    if not grade:
        return '<div style="color:#cf222e;">Grading failed.</div>'

    def _color(s, weight):
        pct = (s / weight) * 100 if weight else 0
        return "#1a7f37" if pct >= 80 else ("#9a6700" if pct >= 60 else "#cf222e")

    total = grade.get("total_score", 0)
    total_color = "#1a7f37" if total >= 80 else ("#9a6700" if total >= 60 else "#cf222e")
    parts = [
        '<div style="border:1px solid #d0d7de; border-radius:6px; padding:14px; background:#f6f8fa;">',
        f'<h4 style="margin:0 0 10px;">Schema Design Form Grade · '
        f'<span style="color:{total_color}; font-size:18px;">{total}/100</span></h4>',
    ]
    for s in grade.get("scores", []):
        crit = s.get("criterion", "?")
        weight = s.get("weight", 0)
        earned = s.get("earned", 0)
        feedback = s.get("feedback", "")
        c = _color(earned, weight)
        parts.append(
            f'<div style="border:1px solid #d0d7de; border-radius:6px; padding:10px 14px; '
            f'background:#fff; margin-bottom:8px; border-left:4px solid {c};">'
            f'<div style="font-weight:600; font-size:13px; margin-bottom:6px;">{crit}: '
            f'<span style="color:{c}; font-size:15px;">{earned}/{weight}</span></div>'
            f'<div style="font-size:12.5px; line-height:1.5;">{feedback}</div></div>'
        )
    strong = grade.get("what_was_strong", "")
    improve = grade.get("what_to_improve", "")
    nxt = grade.get("next_drill_focus", "")
    if strong:
        parts.append(f'<p style="margin:8px 0 4px;"><strong>Strong:</strong> {strong}</p>')
    if improve:
        parts.append(f'<p style="margin:4px 0;"><strong>Improve:</strong> {improve}</p>')
    if nxt:
        parts.append(f'<p style="margin:4px 0 0; font-style:italic; color:#57606a;"><strong>Next:</strong> {nxt}</p>')
    parts.append('</div>')
    return "".join(parts)


def grade_kpi_answer(problem: Dict[str, Any], user_answer: str) -> Optional[Dict[str, Any]]:
    """Grade the user's markdown answer against the problem's rubric and themes."""
    user_prompt = (
        f"Problem prompt:\n{problem.get('prompt','')}\n\n"
        f"Instructions:\n{problem.get('instructions','')}\n\n"
        f"Expected themes the answer should reference:\n"
        + "\n".join(f"- {t}" for t in problem.get('expected_themes', []))
        + "\n\nGrading rubric:\n"
        + json.dumps(problem.get("grading_rubric", []), indent=2)
        + f"\n\nReference answer (a strong sample, not the only valid one):\n{problem.get('reference_answer','')}\n\n"
        + f"Learner's answer:\n---\n{user_answer}\n---\n\nGrade the learner."
    )
    text = _call_claude(KPI_GRADER_SYSTEM, user_prompt, max_tokens=2000)
    return _extract_json(text)


# ============================================================
# Diagnostic feedback (SQL categories only) — reuse nb01
# ============================================================

def grade_diagnostic(problem: Dict[str, Any], answers: Dict[str, str]) -> Optional[Dict[str, Any]]:
    return spu.grade_diagnostic(problem, answers)


# ============================================================
# Modeling diagnostic grading (materialization, grain, joins, dbt layer, tests)
# ============================================================

MODELING_GRADER_SYSTEM = """\
You are coaching a Staff Product Analyst candidate on data modeling decisions for a SQL
problem in pharmacy/digital health analytics. The candidate has analyzed the problem and
made specific modeling choices: materialization strategy + rationale, grain, join strategy,
dbt layer, and test coverage. Grade each choice against the problem context.

Output MUST be a single JSON object inside a ```json fenced block:
{
  "materialization_score": <0..100>,
  "materialization_feedback": "1-2 sentences citing specifics; cover both the choice AND the rationale",
  "grain_score": <0..100>,
  "grain_feedback": "1-2 sentences",
  "join_strategy_score": <0..100>,
  "join_strategy_feedback": "1-2 sentences citing left/right reasoning, key columns, and join order",
  "dbt_layer_score": <0..100>,
  "dbt_layer_feedback": "1-2 sentences",
  "test_coverage_score": <0..100>,
  "test_coverage_feedback": "1-2 sentences naming which standard dbt tests fit (unique/not_null/accepted_values/relationships) or any custom tests",
  "design_notes_score": <null OR 0..100>,
  "design_notes_feedback": "if the design_notes field was empty, return null for the score and 'N/A — left blank' for feedback. Otherwise score the free-form modeling reasoning and write 1-2 sentences citing what was strong or missing.",
  "overall_feedback": "one short sentence on the strongest and weakest choice",
  "next_drill_focus": "what modeling skill to drill next, 1 sentence"
}

Rubric per axis (each scored 0-100 independently):

MATERIALIZATION (table / view / incremental / ephemeral / snapshot / N/A)
- Correct choice given query frequency, data volume, freshness needs
- Rationale references the right trade-offs (query cost vs build cost vs freshness)
- "View" appropriate for: low query volume, freshness > performance
- "Table" appropriate for: frequent reads on a moderate-size aggregation
- "Incremental" appropriate for: large append-only event logs queried frequently
- "Ephemeral" appropriate for: thin reusable logic with no need to persist
- "Snapshot" appropriate for: SCD Type 2 history maintenance
- "N/A" appropriate when the problem has no clear materialization decision

GRAIN ("one row per ___" — BOTH input and output)
- States the INPUT grain (the source table — what one row of the source represents)
- States the OUTPUT grain (what one row of the final SELECT represents)
- The two grains can differ (e.g., input is one row per event, output is one row per event_date after aggregation) — that's the whole point of stating both
- Both grains expressed in plain English
- Output grain matches what the prompt asks for
- Score 100 only when BOTH input and output grain are explicitly stated. If only one is stated, cap at 60.

JOIN STRATEGY
- For MULTI-TABLE problems: correctly identifies LEFT (fact / preserved table) and RIGHT (enrichment / dim), names key columns at each join step, mentions LEFT vs INNER and why.
- For SINGLE-TABLE aggregation problems with no joins: a brief acknowledgement like "N/A — single-table aggregation" or "no joins needed — single-table PIVOT/aggregate" is FULL credit (100/100). Do NOT downgrade for terse single-table answers; the candidate correctly recognized that joins aren't relevant. Only downgrade if the candidate ignored a multi-table problem or got the LEFT/RIGHT wrong.

DBT LAYER (source / stg_ / int_ / mart_ / snapshot / N/A)
- Correctly classifies the model into the right dbt layer
- Stage-only operations (rename, cast, filter test rows) belong in stg_
- Reusable enrichment (joins, window functions) belong in int_
- Business rules + final aggregations belong in mart_
- Time-bound dim history belongs in snapshot

DESIGN NOTES (free-form modeling reasoning beyond grain/joins/tests)
- This is an optional scratch space for schema-design-style problems where Grain/Joins/Tests
  don't capture everything. Typical content: fact column splits, SCD type per dim with
  rationale, idempotency logic for edge cases, ASCII star schema sketches, late-arriving
  event handling.
- If the field is EMPTY (whitespace, "(empty)", or absent), return `null` for design_notes_score
  and "N/A — left blank" for design_notes_feedback. Do not penalize.
- If the field is non-empty, score 0-100 based on whether it covers the schema-design axes
  appropriate to the problem (fact/dim split, SCD assignments with rationale, idempotency,
  edge cases). Markdown tables and ASCII diagrams count as full credit if the content is
  substantively correct — do not penalize format.
- For non-modeling problems (Tab 1 analytical SQL, critical reasoning), this field is
  expected to be empty. Returning null is correct.

TEST COVERAGE
- The candidate may submit this as "Selected tests: <list>" + "Details: <which columns/rules>"
- Names at least 2 standard dbt tests appropriate for this model
- dbt-core (built-in): unique, not_null, accepted_values, relationships
- dbt_utils package: expression_is_true, unique_combination_of_columns, not_null_proportion, recency, accepted_range, mutually_exclusive_ranges
- dbt_expectations package (Great Expectations port): expect_column_values_to_be_between, expect_column_values_to_match_regex, expect_table_row_count_to_be_between, expect_compound_columns_to_be_unique
- dbt_project_evaluator: project-level audit (root_models, undocumented_models, etc) — not per-model tests; mention only if the prompt asks about project hygiene
- Custom singular test: .sql in tests/ that returns rows on FAIL — for business rules too specific for generic tests
- Custom generic test: reusable macro returning rows on FAIL — for the same business rule across multiple columns
- Standard expectations: unique on PRIMARY KEYs and surrogate keys; not_null on required FKs and grain columns; accepted_values on enums; relationships on FKs to dim tables
- Bonus for picking the right package — e.g., dbt_utils for range checks, dbt_expectations for regex / row-count bounds, custom for one-off business rules
- Score 100 only when the candidate maps tests to specific COLUMNS (not just names the test type). E.g., "unique on event_date" beats just "unique".
- If the candidate selected appropriate tests but didn't add column-level details, cap at 70.
- If the candidate listed a project_evaluator audit on a per-model question, gently note that those are project-level audits, not per-model column tests — don't penalize but redirect.

Hard rules:
- If a field is empty or off-topic, score 0 and say so explicitly.
- Be specific in feedback. Cite the candidate's actual words when possible.
- A well-justified non-textbook choice can still score high — reward sound reasoning over rote answers.
- For SQL execution drills (analytical queries), the dbt_layer and test_coverage may be N/A or speculative — don't penalize a candidate who scopes them out with "N/A — this is an ad-hoc analytical query".
"""


def grade_modeling_diagnostic(
    problem: Dict[str, Any],
    answers: Dict[str, str],
) -> Optional[Dict[str, Any]]:
    """Grade the candidate's modeling choices against the problem context."""
    design_notes = (answers.get("design_notes") or "").strip()
    user_prompt = (
        f"Problem prompt:\n{problem.get('prompt','')}\n\n"
        f"Schema (excerpt):\n{problem.get('schema_ddl','')[:1500]}\n\n"
        f"---\nCandidate's modeling choices:\n"
        f"Materialization: {answers.get('materialization','(empty)')}\n"
        f"Materialization rationale: {answers.get('materialization_rationale','(empty)')}\n"
        f"Grain (one row per ___): {answers.get('grain','(empty)')}\n"
        f"Join strategy: {answers.get('join_strategy','(empty)')}\n"
        f"dbt layer: {answers.get('dbt_layer','(empty)')}\n"
        f"Test coverage: {answers.get('test_coverage','(empty)')}\n"
        f"Design notes (free-form modeling reasoning): "
        f"{design_notes if design_notes else '(empty — return null for design_notes_score)'}\n"
        f"---\nGrade the candidate."
    )
    text = _call_claude(MODELING_GRADER_SYSTEM, user_prompt, max_tokens=2500)
    return _extract_json(text)


def modeling_grade_to_html(grade: Dict[str, Any]) -> str:
    """Render the modeling diagnostic grade as nicely formatted HTML."""
    if not grade:
        return '<div style="color:#cf222e;">Grading failed.</div>'

    def _color(s):
        return "#1a7f37" if s >= 80 else ("#9a6700" if s >= 60 else "#cf222e")

    def _block(label, score, feedback, accent):
        c = _color(score)
        return (
            f'<div style="border:1px solid #d0d7de; border-radius:6px; padding:10px 14px; '
            f'background:#fff; margin-bottom:8px; border-left:4px solid {accent};">'
            f'<div style="font-weight:600; font-size:13px; margin-bottom:6px;">{label}: '
            f'<span style="color:{c}; font-size:15px;">{score}/100</span></div>'
            f'<div style="font-size:12.5px; line-height:1.5;">{feedback}</div></div>'
        )

    axes = [
        ("Materialization",   grade.get("materialization_score", 0),
            grade.get("materialization_feedback", ""), "#2563a8"),
        ("Grain",             grade.get("grain_score", 0),
            grade.get("grain_feedback", ""), "#057a55"),
        ("Join strategy",     grade.get("join_strategy_score", 0),
            grade.get("join_strategy_feedback", ""), "#c05621"),
        ("dbt layer",         grade.get("dbt_layer_score", 0),
            grade.get("dbt_layer_feedback", ""), "#6f42c1"),
        ("Test coverage",     grade.get("test_coverage_score", 0),
            grade.get("test_coverage_feedback", ""), "#d4a72c"),
    ]
    # Design notes is the 6th axis but only shown when the candidate filled it in.
    # Grader returns null for design_notes_score when the field was empty.
    dn_score = grade.get("design_notes_score")
    if dn_score is not None:
        axes.append((
            "Design notes", dn_score,
            grade.get("design_notes_feedback", ""), "#8b3a0e",
        ))
    avg = sum(s for _, s, _, _ in axes) / len(axes) if axes else 0
    parts = [
        '<div style="border:1px solid #d0d7de; border-radius:6px; padding:14px; background:#f6f8fa;">',
        f'<h4 style="margin:0 0 10px;">Modeling diagnostic grade · '
        f'<span style="color:{_color(avg)}; font-size:18px;">{int(avg)}/100 avg</span></h4>',
    ]
    for label, score, feedback, accent in axes:
        parts.append(_block(label, score, feedback, accent))
    overall = grade.get("overall_feedback", "")
    nxt = grade.get("next_drill_focus", "")
    if overall:
        parts.append(f'<p style="margin:8px 0 4px;"><strong>Overall:</strong> {overall}</p>')
    if nxt:
        parts.append(f'<p style="margin:4px 0 0; font-style:italic; color:#57606a;"><strong>Next:</strong> {nxt}</p>')
    parts.append('</div>')
    return "".join(parts)


# ============================================================
# Interpretation + Recommendation grading
# ============================================================

INTERP_REC_GRADER_SYSTEM = """\
You are coaching a Staff Product Analyst candidate on how to read SQL output and
translate findings into business recommendations. The candidate has been shown the
problem prompt, the example_input_data, the expected example output, and a model
interpretation + recommendation. Now they have written their own interpretation and
recommendation. Grade them.

Output MUST be a single JSON object inside a ```json fenced block:
{
  "interpretation_score": <0..100>,
  "interpretation_strengths": "1-2 sentence rationale citing the candidate's specific words",
  "interpretation_gaps": "1-2 sentence rationale naming what was missing or weak vs the model",
  "recommendation_score": <0..100>,
  "recommendation_strengths": "1-2 sentence rationale citing the candidate's specific words",
  "recommendation_gaps": "1-2 sentence rationale naming what was missing or weak vs the model",
  "overall_feedback": "one short sentence — what to focus on next time",
  "next_drill_focus": "what type of problem or skill to practice next, 1 sentence"
}

Grading rubric for INTERPRETATION (each contributes ~25 points):
- Reads the actual numbers from the output (literal accuracy)
- Connects numbers to underlying business behavior (not just restating)
- References an industry benchmark where one applies (FPAR 75-85%, refill rate 30d 60-80%
  chronic, abandonment 8-15%, PDC ≥ 0.80, etc) — partial credit if benchmark direction is
  noted even without exact range
- Flags any ambiguity, edge case, or concern visible in the data shape

Grading rubric for RECOMMENDATION (each contributes ~25 points):
- Action verb at the start of each recommendation (Trigger, Implement, Investigate, Add)
- Names a specific stakeholder/owner (Pharmacy Ops, Care Coordination, Finance, Quality,
  Product, Engineering)
- References an industry-standard practice (PA team triage, medication synchronization,
  90-day supply transfer, adherence outreach trigger, Star Ratings, refill cliff,
  formulary substitution, etc) — generic 'investigate further' is NOT sufficient
- Includes a 'what to monitor next' item with a concrete metric and direction

Hard rules:
- Be specific in feedback. Cite the candidate's actual words when calling out strengths or gaps.
- Do not penalize for using different industry vocabulary than the model — if the term is
  industry-standard, it counts.
- A correct, concise answer beats a long, vague one. Reward clarity.
- If the answer is empty or off-topic, score 0 and say so.
- Compare to the model interpretation/recommendation as a reference, NOT a target — the
  candidate may have a different valid angle.
"""


def grade_interpretation_recommendation(
    problem: Dict[str, Any],
    interpretation: str,
    recommendation: str,
) -> Optional[Dict[str, Any]]:
    """Grade the user's interpretation and recommendation against the problem's model
    examples and the rubric. Returns scoring + feedback dict."""
    user_prompt = (
        f"Problem prompt:\n{problem.get('prompt','')}\n\n"
        f"Example expected output (cells the candidate is interpreting):\n"
        f"Columns: {problem.get('example_output_columns', [])}\n"
        f"Rows: {problem.get('example_output_rows', [])}\n\n"
        f"Model interpretation (reference, NOT the only valid angle):\n"
        f"{problem.get('interpretation_example','(none provided)')}\n\n"
        f"Model recommendation (reference, NOT the only valid angle):\n"
        f"{problem.get('recommendation_example','(none provided)')}\n\n"
        f"---\n"
        f"Candidate's interpretation:\n{interpretation or '(empty)'}\n\n"
        f"Candidate's recommendation:\n{recommendation or '(empty)'}\n\n"
        f"---\n"
        f"Grade the candidate."
    )
    text = _call_claude(INTERP_REC_GRADER_SYSTEM, user_prompt, max_tokens=2000)
    return _extract_json(text)


def interp_rec_grade_to_html(grade: Dict[str, Any]) -> str:
    """Render the interpretation + recommendation grade as nicely formatted HTML."""
    if not grade:
        return '<div style="color:#cf222e;">Grading failed.</div>'
    interp_score = grade.get("interpretation_score", 0)
    rec_score = grade.get("recommendation_score", 0)
    avg = (interp_score + rec_score) / 2

    def _color(s):
        return "#1a7f37" if s >= 80 else ("#9a6700" if s >= 60 else "#cf222e")

    def _block(title, score, strengths, gaps, accent):
        c = _color(score)
        return (
            f'<div style="border:1px solid #d0d7de; border-radius:6px; padding:12px 14px; '
            f'background:#fff; margin-bottom:10px; border-left:4px solid {accent};">'
            f'<div style="font-weight:600; font-size:14px; margin-bottom:8px;">'
            f'{title}: <span style="color:{c}; font-size:16px;">{score}/100</span></div>'
            f'<div style="font-size:13px; margin-bottom:6px;">'
            f'<strong style="color:#1a7f37;">Strengths:</strong> {strengths}</div>'
            f'<div style="font-size:13px;">'
            f'<strong style="color:#cf222e;">Gaps:</strong> {gaps}</div>'
            f'</div>'
        )

    overall = grade.get("overall_feedback", "")
    nxt = grade.get("next_drill_focus", "")
    parts = [
        f'<div style="border:1px solid #d0d7de; border-radius:6px; padding:14px; background:#f6f8fa;">',
        f'<h4 style="margin:0 0 12px;">Business analysis grade · '
        f'<span style="color:{_color(avg)}; font-size:18px;">{int(avg)}/100 avg</span></h4>',
        _block("Interpretation", interp_score,
               grade.get("interpretation_strengths", ""),
               grade.get("interpretation_gaps", ""),
               "#057a55"),
        _block("Recommendation", rec_score,
               grade.get("recommendation_strengths", ""),
               grade.get("recommendation_gaps", ""),
               "#c05621"),
    ]
    if overall:
        parts.append(f'<p style="margin:8px 0 4px;"><strong>Overall:</strong> {overall}</p>')
    if nxt:
        parts.append(f'<p style="margin:4px 0 0; font-style:italic; color:#57606a;"><strong>Next:</strong> {nxt}</p>')
    parts.append('</div>')
    return "".join(parts)


# ============================================================
# Hints (shared)
# ============================================================

def get_hint(problem: Dict[str, Any], hint_index: int) -> str:
    return spu.get_hint(problem, hint_index)


# ============================================================
# Persistence (mirrors nb01 patterns, namespaced for nb02)
# ============================================================

def save_schema_design_attempt(
    problem: Dict[str, Any],
    responses: Dict[str, Any],
    grade: Optional[Dict[str, Any]] = None,
    solved_dir: Optional[str] = None,
) -> Optional[str]:
    """Save the schema_design form responses (and optional grade) to disk so that
    reloading the same problem repopulates the form with prior answers.

    Stored at: <solved_dir>/<problem_id>_schema_design_attempt.json
    Each click of Get Schema Design Feedback / Check Understanding overwrites
    the existing file — only the LATEST attempt is kept per problem.
    """
    if not solved_dir:
        return None
    pid = problem.get("_meta", {}).get("problem_id")
    if not pid:
        return None
    os.makedirs(solved_dir, exist_ok=True)
    payload = {
        "problem_id": pid,
        "subtopic": problem.get("_meta", {}).get("subtopic", "schema_design"),
        "responses": responses,
        "grade": grade,
        "saved_at": datetime.now().isoformat(),
    }
    fname = f"{pid}_schema_design_attempt.json"
    path = os.path.join(solved_dir, fname)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


def load_schema_design_attempt(
    problem_id: Optional[str],
    solved_dir: Optional[str],
) -> Optional[Dict[str, Any]]:
    """Load saved form responses for a problem_id if a prior attempt was saved.
    Returns the full payload (responses + grade + saved_at) or None."""
    if not problem_id or not solved_dir:
        return None
    fname = f"{problem_id}_schema_design_attempt.json"
    path = os.path.join(solved_dir, fname)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


# =============================================================
# Version Control form grader
# =============================================================

VC_FORM_GRADER_SYSTEM = """You are grading a candidate's structured response to a version control / git workflow problem.

The candidate's response has six fields:
  goal              - one-line recommendation
  sections          - dict of subtopic-specific section answers (varies per subtopic)
  tradeoffs         - what was given up by picking this approach
  example           - concrete walkthrough scenario
  edge_cases_per_category - dict of category_id -> list of canned scenario picks
  reference_patterns      - list of named canon patterns (GitHub Flow, Conventional Commits, etc.)

Score each field on a 1-100 scale, then return a JSON object with this schema:

{
  "goal":                {"score": INT_OUT_OF_15, "feedback": "..."},
  "sections":            {"score": INT_OUT_OF_35, "feedback": "..."},
  "tradeoffs":           {"score": INT_OUT_OF_10, "feedback": "..."},
  "example":             {"score": INT_OUT_OF_15, "feedback": "..."},
  "edge_cases":          {"score": INT_OUT_OF_15, "feedback": "..."},
  "reference_patterns":  {"score": INT_OUT_OF_10, "feedback": "..."},
  "total_score": INT_OUT_OF_100,
  "strong_field": "...",
  "improve_field": "...",
  "next_practice": "..."
}

Scoring rubric:
- goal (15): one clear sentence stating a recommendation. Penalize vague positions, multiple competing recommendations, or hedging.
- sections (35): each section answered with substance — branch naming patterns, merge rules, env mapping, etc. Penalize empty sections; reward concrete commands/examples; reward acknowledging the prompt's specific constraints (team size, deploy cadence, dbt-specific tooling).
- tradeoffs (10): names what was given up AND what alternative was rejected with rationale. Penalize "no trade-offs" or generic "trade-offs exist" without specifics.
- example (15): concrete walkthrough, names actual commands or branch names. Penalize generic narratives that could apply to any team.
- edge_cases (15): at least 2 categories ticked with canned scenario picks. Reward picking categories that match the problem's specific risk surface.
- reference_patterns (10): names known canon patterns (GitHub Flow, Conventional Commits, dbt slim CI). Reward 3+ correctly applied patterns.

Be strict but fair. Emphasize whether the response actually answers the prompt's specific requirements, not just generic git knowledge.

Return ONLY a valid JSON object. No prose outside the JSON.
"""


def grade_vc_form(
    problem: Dict[str, Any],
    form_responses: Dict[str, Any],
) -> Optional[Dict[str, Any]]:
    """Grade a version control form response. Returns parsed JSON dict or None."""
    sections_block = "\n".join(
        f"  [{fid}]: {(txt or '').strip()}"
        for fid, txt in (form_responses.get("sections") or {}).items()
        if (txt or "").strip()
    ) or "(no sections answered)"

    # branching_strategy interactive form picks (structured dropdowns/multi-selects)
    branching_picks = form_responses.get("branching_picks") or {}
    branching_block_lines = []
    if branching_picks:
        for sec_id, picks in branching_picks.items():
            line = f"  [{sec_id}]: " + ", ".join(
                f"{pid}={v}" for pid, v in picks.items()
            )
            branching_block_lines.append(line)
    branching_block = "\n".join(branching_block_lines) or "(no structured picks)"
    mode = form_responses.get("mode", "solve")

    edge_cases_per_cat = form_responses.get("edge_cases_per_category", {}) or {}
    edge_cases_applies = form_responses.get("edge_cases_applies", {}) or {}
    edge_lines = []
    for cid, picks in edge_cases_per_cat.items():
        applies = " (✓ applies)" if edge_cases_applies.get(cid) else ""
        if isinstance(picks, list) and picks:
            edge_lines.append(f"  [{cid}]{applies}: " + "; ".join(picks))
    edge_block = "\n".join(edge_lines) or "(no edge cases addressed)"

    refs = form_responses.get("reference_patterns") or []
    refs_block = ", ".join(refs) if refs else "(no reference patterns named)"

    user_prompt = (
        f"Problem prompt:\n{problem.get('prompt','')}\n\n"
        f"Subtopic: {problem.get('_meta', {}).get('subtopic', 'unknown')}\n\n"
        f"GRADING MODE: {mode}\n"
        f"  - solve: candidate picked blind, score strictly\n"
        f"  - walkthrough: candidate read canonical answers and is paraphrasing/confirming for learning;\n"
        f"    score whether their picks match the canonical answers (high credit even when verbatim)\n\n"
        f"---\nCandidate's VC form response:\n\n"
        f"(1) Goal / recommendation:\n{form_responses.get('goal','(empty)')}\n\n"
        f"(2a) Section breakdown — text answers (legacy fields):\n{sections_block}\n\n"
        f"(2b) STRUCTURED PICKS (the candidate's PRIMARY answer for branching_strategy):\n"
        f"{branching_block}\n"
        f"     GRADING NOTE: when structured picks are present, treat them as the candidate's\n"
        f"     answer for the section breakdown. Each section_id maps to one of:\n"
        f"     workflow_pattern, branch_naming, merge_rules, env_mapping, pr_review, ci_integration.\n"
        f"     Score the (2) Section breakdown (35 points) using these picks first; only fall back\n"
        f"     to (2a) text if structured picks are empty. Reward picks that match the canonical\n"
        f"     answers for a small dbt analytics team: GitHub Flow, type-prefix branches, PR+CI gates,\n"
        f"     1 reviewer, squash merge, branch protection on main, scheduled prod from main, slim CI.\n\n"
        f"(3) Trade-offs:\n{form_responses.get('tradeoffs','(empty)')}\n\n"
        f"(4) Edge cases / failure modes addressed:\n{edge_block}\n\n"
        f"(5) Concrete example walkthrough:\n{form_responses.get('example','(empty)')}\n\n"
        f"(6) Reference patterns named: {refs_block}\n\n"
        f"---\nGrade strictly per the 6-axis rubric in the system prompt. "
        f"Return ONLY a JSON object."
    )
    text = _call_claude(VC_FORM_GRADER_SYSTEM, user_prompt, max_tokens=3000)
    parsed = _extract_json(text)
    return parsed


def vc_form_grade_to_html(grade: Dict[str, Any]) -> str:
    """Render the version control form grade as HTML."""
    if not grade:
        return "<p>(no grade)</p>"
    total = grade.get("total_score", 0)
    rows = []
    axes = [
        ("goal", "Goal / recommendation", 15),
        ("sections", "Section breakdown", 35),
        ("tradeoffs", "Trade-offs", 10),
        ("example", "Example walkthrough", 15),
        ("edge_cases", "Edge cases", 15),
        ("reference_patterns", "Reference patterns", 10),
    ]
    for key, label, max_pts in axes:
        ax = grade.get(key) or {}
        score = ax.get("score", "—") if isinstance(ax, dict) else "—"
        fb = ax.get("feedback", "") if isinstance(ax, dict) else ""
        rows.append(
            f"<tr><td style='padding:6px 10px; border-bottom:1px solid #eaeef2; "
            f"font-weight:600; vertical-align:top; width:200px;'>{label}: {score}/{max_pts}</td>"
            f"<td style='padding:6px 10px; border-bottom:1px solid #eaeef2; line-height:1.55;'>"
            f"{fb}</td></tr>"
        )
    strong = grade.get("strong_field", "")
    improve = grade.get("improve_field", "")
    nxt = grade.get("next_practice", "")
    return (
        f"<div style='font-family:-apple-system,BlinkMacSystemFont,sans-serif; max-width:900px;'>"
        f"<h3 style='margin:0 0 8px 0; color:#0c447c;'>Version Control Form Grade · {total}/100</h3>"
        f"<table style='width:100%; border-collapse:collapse; font-size:13px;'>"
        f"<tbody>{''.join(rows)}</tbody></table>"
        + (f"<div style='margin-top:10px; font-size:13px; line-height:1.55;'><strong>Strong:</strong> {strong}</div>" if strong else "")
        + (f"<div style='margin-top:6px; font-size:13px; line-height:1.55;'><strong>Improve:</strong> {improve}</div>" if improve else "")
        + (f"<div style='margin-top:6px; font-size:13px; line-height:1.55;'><strong>Next:</strong> {nxt}</div>" if nxt else "")
        + "</div>"
    )


def save_vc_attempt(
    problem: Dict[str, Any],
    responses: Dict[str, Any],
    grade: Optional[Dict[str, Any]] = None,
    solved_dir: Optional[str] = None,
) -> Optional[str]:
    """Persist a version_control form attempt for replay/grade restoration."""
    if not solved_dir:
        return None
    pid = problem.get("_meta", {}).get("problem_id")
    if not pid:
        return None
    os.makedirs(solved_dir, exist_ok=True)
    payload = {
        "problem_id": pid,
        "subtopic": problem.get("_meta", {}).get("subtopic", "version_control"),
        "responses": responses,
        "grade": grade,
        "saved_at": datetime.now().isoformat(),
    }
    fname = f"{pid}_vc_attempt.json"
    path = os.path.join(solved_dir, fname)
    with open(path, "w") as f:
        json.dump(payload, f, indent=2, default=str)
    return path


def load_vc_attempt(
    problem_id: Optional[str],
    solved_dir: Optional[str],
) -> Optional[Dict[str, Any]]:
    if not problem_id or not solved_dir:
        return None
    fname = f"{problem_id}_vc_attempt.json"
    path = os.path.join(solved_dir, fname)
    if not os.path.exists(path):
        return None
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def save_problem(problem: Dict[str, Any], outputs_dir: str) -> str:
    os.makedirs(outputs_dir, exist_ok=True)
    pid = problem.get("_meta", {}).get("problem_id", uuid.uuid4().hex[:12])
    cat = problem.get("_meta", {}).get("category", "unknown")
    sub = problem.get("_meta", {}).get("subtopic", "unknown")
    fname = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_nb02_{cat}_{sub}_{pid}.json"
    path = os.path.join(outputs_dir, fname)
    with open(path, "w") as f:
        json.dump(problem, f, indent=2, default=str)
    return path


def load_problem(path: str) -> Dict[str, Any]:
    with open(path) as f:
        return json.load(f)


def list_problems(outputs_dir: str, category: Optional[str] = None,
                  subtopic: Optional[str] = None) -> List[Dict[str, str]]:
    if not os.path.isdir(outputs_dir):
        return []
    out = []
    for fname in sorted(os.listdir(outputs_dir), reverse=True):
        if not fname.endswith(".json"):
            continue
        if "nb02_" not in fname:  # only nb02 problems
            continue
        path = os.path.join(outputs_dir, fname)
        try:
            p = load_problem(path)
            meta = p.get("_meta", {})
            if category and meta.get("category") != category:
                continue
            if subtopic and meta.get("subtopic") != subtopic:
                continue
            out.append({
                "path": path,
                "title": p.get("title", fname),
                "category": meta.get("category", ""),
                "subtopic": meta.get("subtopic", ""),
                "kind": meta.get("kind", ""),
                "generated_at": meta.get("generated_at", ""),
            })
        except Exception:
            continue
    return out


def save_solved(problem: Dict[str, Any], user_solution: str, outputs_dir: str,
                grade_result: Optional[Dict[str, Any]] = None) -> str:
    """Record a successful solve. For KPI problems, grade_result is the scoring breakdown."""
    os.makedirs(outputs_dir, exist_ok=True)
    pid = problem.get("_meta", {}).get("problem_id", uuid.uuid4().hex[:12])
    record = {
        "problem": problem,
        "user_solution": user_solution,
        "grade_result": grade_result,
        "solved_at": datetime.now().isoformat(),
        "notebook": "nb02_fuze_interview_drills",
    }
    path = os.path.join(outputs_dir, f"nb02_{pid}.json")
    with open(path, "w") as f:
        json.dump(record, f, indent=2, default=str)
    return path


# ============================================================
# Render helpers (delegate to spu, with tolerant INSERT parser)
# ============================================================

def _strip_sql_comments(ddl: str) -> str:
    """Strip SQL line comments (-- to end of line) and block comments (/* */)
    from DDL. The schema parser treats whatever is left of a comma as a column
    definition, so an inline `-- ...` line creates a garbage column with name
    `--`. This pre-pass removes them."""
    if not ddl:
        return ddl
    out = []
    i = 0
    n = len(ddl)
    while i < n:
        # Block comment /* ... */
        if ddl[i:i+2] == "/*":
            end = ddl.find("*/", i + 2)
            if end == -1:
                break
            i = end + 2
            continue
        # Line comment -- ...
        if ddl[i:i+2] == "--":
            nl = ddl.find("\n", i)
            if nl == -1:
                break
            i = nl  # keep the newline so the parser still sees line breaks
            continue
        out.append(ddl[i])
        i += 1
    return "".join(out)


def schema_to_html(ddl: str) -> str:
    return spu.schema_to_html(_strip_sql_comments(ddl))


# Match column-less INSERTs:  INSERT INTO claims VALUES (...), (...), ...;
import re as _re
_COLLESS_INSERT_RE = _re.compile(
    r"INSERT\s+INTO\s+([\w_]+)\s+VALUES\s*(.+?);",
    _re.IGNORECASE | _re.DOTALL,
)


def _parse_column_less_inserts(sql: str, schema_ddl: str):
    """Parse INSERT statements that omit the column list, looking up column names
    from the CREATE TABLE statements in schema_ddl. Returns same shape as
    spu.parse_inserts: {table_name: (col_names, [row_values, ...])}.
    """
    if not sql:
        return {}
    # Build lookup: table_name -> [col_name, ...]
    schema_cols = {name: [c[0] for c in cols]
                   for name, cols in spu.parse_create_tables(schema_ddl or "")}
    out = {}
    for m in _COLLESS_INSERT_RE.finditer(sql):
        name = m.group(1)
        if name not in schema_cols:
            continue
        cols = schema_cols[name]
        rows = spu._parse_value_rows(m.group(2))
        if name in out:
            out[name][1].extend(rows)
        else:
            out[name] = (cols, rows)
    return out


def insert_data_to_html(sql: str, schema_ddl: str = "") -> str:
    """Render INSERT statements as an HTML table. Tolerant of column-less INSERTs
    when schema_ddl is provided.
    """
    if not sql:
        return ""
    # Try the strict parser first (column lists present)
    tables = spu.parse_inserts(sql)
    # If nothing parsed AND schema is available, try the column-less parser
    if not tables and schema_ddl:
        tables = _parse_column_less_inserts(sql, schema_ddl)
    if not tables:
        return (
            f'<pre style="background:#0d1117; color:#e6edf3; padding:8px; '
            f'border-radius:4px; font-size:12px; white-space:pre-wrap;">{sql}</pre>'
        )
    parts = []
    for name, (cols, rows) in tables.items():
        cleaned = [[spu._clean_sql_value(v) for v in row] for row in rows]
        # Pad rows that have fewer values than columns (defensive)
        max_cols = len(cols) if cols else (max(len(r) for r in cleaned) if cleaned else 0)
        cleaned = [r + [""] * (max_cols - len(r)) if len(r) < max_cols else r[:max_cols]
                   for r in cleaned]
        df = pd.DataFrame(cleaned, columns=cols if cols else [f"col{i+1}" for i in range(max_cols)])
        parts.append(
            f'<div style="margin-bottom:12px;">'
            f'<div style="font-weight:600; margin:6px 0; font-size:13px;">'
            f'Data: <code>{name}</code></div>'
            + df.to_html(index=False, classes="nb-data-table")
            + '</div>'
        )
    return "".join(parts)


def prompt_to_bullets(prompt: str) -> str:
    return spu.prompt_to_bullets(prompt)


# ============================================================
# Nested-bullet renderer (for KPI prompts/instructions and SQL prompts)
# Splits sentences into top-level bullets; if a sentence contains an inline
# list (column list, lettered (a)(b)(c) enumeration), nests as sub-bullets.
# Paren-aware: nested parentheticals like '(do you re-state...?)' inside
# item (e) won't trigger a false split.
# ============================================================

import re as _re_b  # alias to avoid shadowing the module-level _re below this point


def _split_outside_parens(text: str, sep: str = ",") -> list:
    """Split text on `sep` only at paren depth 0. Handles nested parens."""
    parts = []
    buf = []
    depth = 0
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            s = "".join(buf).strip()
            if s:
                parts.append(s)
            buf = []
        else:
            buf.append(ch)
    tail = "".join(buf).strip()
    if tail:
        parts.append(tail)
    return parts


def _extract_lettered_items(text: str) -> list:
    """Find top-level (a) (b) (c) markers and split text into [(letter, content), ...].
    Paren-aware: '(do you ...)' inside an item won't trigger a split."""
    positions = []
    depth = 0
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch == "(":
            if (depth == 0
                and i + 2 < n
                and text[i+1].isalpha()
                and text[i+2] == ")"):
                positions.append((i, text[i+1]))
                i += 3
                continue
            depth += 1
            i += 1
            continue
        if ch == ")":
            depth = max(0, depth - 1)
            i += 1
            continue
        i += 1
    if len(positions) < 2:
        return []
    items = []
    for idx, (pos, letter) in enumerate(positions):
        start = pos + 3
        end = positions[idx + 1][0] if idx + 1 < len(positions) else n
        content = text[start:end].strip().rstrip(",.;")
        items.append((letter, content))
    return items


def _inline_md(text: str) -> str:
    """Convert backticks `code` and **bold** to HTML. Minimal markdown."""
    if not text:
        return ""
    text = _re_b.sub(r"`([^`]+)`", r"<code>\1</code>", text)
    text = _re_b.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    return text


def _is_section_header(line: str) -> bool:
    """A 'section header' is an all-caps line of 2 to 6 words at the start of
    a paragraph. Used to detect prompts structured as STAKEHOLDER CONTEXT /
    WHAT YOU HAVE IN SOURCE / YOUR TASK / etc."""
    s = line.strip()
    if not s or len(s) > 60:
        return False
    # Must be all-caps with optional spaces, slashes, ampersands
    if not _re_b.fullmatch(r"[A-Z][A-Z0-9 /&\-]+", s):
        return False
    # Must have at least one space (single words like "OK" don't count)
    return " " in s


def _render_bullets_block(lines):
    """Given a list of lines that all start with '- ' or '* ', render as <ul>."""
    out = ['<ul style="line-height:1.65; margin:4px 0 8px 22px; padding-left:4px;">']
    for line in lines:
        item = _re_b.sub(r"^\s*[-*•]\s+", "", line).rstrip()
        out.append(f'<li style="margin-bottom:4px;">{_inline_md(item)}</li>')
    out.append("</ul>")
    return "".join(out)


def prompt_to_bullets_nested(text: str) -> str:
    """Render text as structured HTML. Recognizes:
      - UPPERCASE section headers (rendered as h5)
      - Newline-prefixed bullets ('\\n- ' or '\\n* ') rendered as <ul>
      - List-after-colon with 3+ comma-separated items (nested <ul>)
      - Lettered enumerations (a)(b)(c) (nested <ul>)
      - Paragraphs separated by blank lines"""
    if not text:
        return ""

    out = []

    # Split by blank lines into paragraph blocks
    paragraphs = _re_b.split(r"\n\s*\n", text.strip())

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Process line by line: handle section headers + newline bullets
        lines = para.split("\n")
        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Section header (all-caps line)
            if _is_section_header(line):
                out.append(
                    f'<h5 style="margin:14px 0 6px 0; color:#0c447c; '
                    f'font-size:13.5px; font-weight:700; letter-spacing:0.04em;">'
                    f'{line}</h5>'
                )
                i += 1
                continue

            # Run of bullet lines (- or *)
            if _re_b.match(r"^[-*•]\s+", line):
                bullet_lines = []
                while i < len(lines) and _re_b.match(r"^[-*•]\s+", lines[i].strip()):
                    bullet_lines.append(lines[i].strip())
                    i += 1
                # Continuation lines (indented or not starting with bullet) merge into the previous bullet
                while i < len(lines) and lines[i].strip() and not _re_b.match(r"^[-*•]\s+", lines[i].strip()) and not _is_section_header(lines[i].strip()):
                    if bullet_lines:
                        bullet_lines[-1] += " " + lines[i].strip()
                    i += 1
                out.append(_render_bullets_block(bullet_lines))
                continue

            # Plain text — accumulate consecutive non-header non-bullet lines as one paragraph
            text_lines = []
            while i < len(lines) and lines[i].strip() and not _re_b.match(r"^[-*•]\s+", lines[i].strip()) and not _is_section_header(lines[i].strip()):
                text_lines.append(lines[i].strip())
                i += 1
            joined = " ".join(text_lines)
            if joined:
                # Apply the existing sentence-bullet logic on this single block
                out.append(_render_text_paragraph(joined))

    if not out:
        return ""
    return "".join(out)


def _render_text_paragraph(text: str) -> str:
    """Apply the original sentence-splitting bullet logic to a plain-text block.
    This is the legacy rendering path for paragraphs without explicit bullets
    or section headers."""
    sentences = [s.strip() for s in _re_b.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]
    if not sentences:
        return ""
    out = ['<ul style="line-height:1.65; margin:0 0 10px 18px; padding-left:4px;">']
    for s in sentences:
        body = s.rstrip(".")
        # Try lettered enumeration first: "intro: (a) ... (b) ... (c) ..."
        m = _re_b.match(r"^(.+?:)\s*(\([a-z]\)\s+.+)$", body, _re_b.DOTALL)
        if m:
            head = m.group(1).strip()
            rest = m.group(2)
            lettered = _extract_lettered_items(rest)
            if len(lettered) >= 2:
                out.append(f'<li style="margin-bottom:6px;">{_inline_md(head)}')
                out.append('<ul style="line-height:1.55; margin:4px 0 6px 22px; padding-left:4px;">')
                for letter, content in lettered:
                    out.append(
                        f'<li style="margin-bottom:3px;">'
                        f'<strong>({letter})</strong> {_inline_md(content)}</li>'
                    )
                out.append("</ul></li>")
                continue
        # Try generic list after colon (3+ comma-separated items)
        m = _re_b.match(r"^(.+?:)\s*(.+)$", body, _re_b.DOTALL)
        if m:
            head = m.group(1).strip()
            rest = m.group(2)
            items = _split_outside_parens(rest, ",")
            if len(items) >= 3:
                out.append(f'<li style="margin-bottom:6px;">{_inline_md(head)}')
                out.append('<ul style="line-height:1.55; margin:4px 0 6px 22px; padding-left:4px;">')
                for item in items:
                    item = item.rstrip(",.;")
                    if _re_b.fullmatch(r"[a-z_][a-z0-9_]*", item.strip()):
                        out.append(f'<li style="margin-bottom:3px;"><code>{item.strip()}</code></li>')
                    else:
                        out.append(f'<li style="margin-bottom:3px;">{_inline_md(item)}</li>')
                out.append("</ul></li>")
                continue
        out.append(f'<li style="margin-bottom:5px;">{_inline_md(s)}</li>')
    out.append("</ul>")
    return "".join(out)


def glossary_to_html(glossary: list) -> str:
    """Render a glossary list of {term, definition} as a styled definition list."""
    if not glossary:
        return ""
    items = []
    for entry in glossary:
        if not isinstance(entry, dict):
            continue
        term = entry.get("term", "")
        definition = entry.get("definition", "")
        if not term:
            continue
        items.append(
            f'<li style="margin-bottom:6px;"><strong style="color:#0969da;">{term}:</strong> {definition}</li>'
        )
    if not items:
        return ""
    return (
        '<div style="background:#fff8e1; border-left:3px solid #d4a72c; padding:10px 14px; '
        'border-radius:4px; margin:10px 0;">'
        '<div style="font-weight:600; font-size:13px; margin-bottom:6px; color:#8b3a0e;">'
        'Glossary (lay-language definitions for this problem)</div>'
        '<ul style="margin:0 0 0 18px; padding-left:0; line-height:1.5;">'
        + "".join(items) + '</ul></div>'
    )


def _bullets_to_html(text: str, color: str = "#057a55") -> str:
    """Render bullet-style text (with '- ' or '* ' prefixes, OR all on one line
    separated by ' - ' delimiters) as a styled <ul>. Tolerant of the same
    inline-vs-newline format mismatch as calculation_explanation."""
    if not text:
        return ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    # If everything came on one line but has multiple inline '- ' delimiters,
    # split on those (keeping the first bullet)
    joined = " ".join(lines)
    if len(lines) <= 2 and joined.count(" - ") >= 2:
        parts = _re.split(r'\s+(?=-\s)', joined)
        lines = [p.strip() for p in parts if p.strip()]
    items = []
    for l in lines:
        l_clean = _re.sub(r"^[-*]\s*", "", l)
        if l_clean:
            items.append(f'<li style="margin-bottom:6px;">{l_clean}</li>')
    if not items:
        return f'<p style="margin:0; line-height:1.55;">{text}</p>'
    return f'<ul style="margin:0 0 0 22px; padding-left:0; line-height:1.55;">' + "".join(items) + '</ul>'


def interpretation_to_html(text: str) -> str:
    """Render the model interpretation in a soft callout box (green theme)."""
    if not text:
        return ""
    body = _bullets_to_html(text)
    return (
        '<div style="background:#e8f5e9; border-left:3px solid #057a55; padding:10px 14px; '
        'border-radius:4px; margin:10px 0;">'
        '<div style="font-weight:600; font-size:13px; margin-bottom:6px; color:#1a7f37;">'
        'Example interpretation of the expected output (model how to read findings)</div>'
        + body + '</div>'
    )


def recommendation_to_html(text: str) -> str:
    """Render the model recommendation in a soft callout box (orange theme)."""
    if not text:
        return ""
    body = _bullets_to_html(text)
    return (
        '<div style="background:#fff3e0; border-left:3px solid #c05621; padding:10px 14px; '
        'border-radius:4px; margin:10px 0;">'
        '<div style="font-weight:600; font-size:13px; margin-bottom:6px; color:#8b3a0e;">'
        'Example recommendation grounded in industry practice (model how to act on findings)</div>'
        + body + '</div>'
    )


_MODELING_DIAGNOSTIC_NUDGE_SUBTOPICS = {
    "schema_design", "dimensional_modeling", "scd_type_2",
}


def render_sql_problem(p: Dict[str, Any], compact: bool = False) -> str:
    """Render an SQL problem as HTML. When compact=True, schema/data/output sections
    open in a collapsed <details> block to save vertical space inside the editor."""
    title = p.get("title", "Untitled")
    meta = p.get("_meta", {})
    scenario = meta.get("scenario", "")
    subtopic = meta.get("subtopic", "")
    modeling_nudge_html = ""
    if subtopic in _MODELING_DIAGNOSTIC_NUDGE_SUBTOPICS:
        modeling_nudge_html = (
            '<div style="background:#fff8e1; border-left:4px solid #f9a825; '
            'padding:8px 12px; border-radius:4px; font-size:13px; margin-bottom:10px;">'
            '<strong>👉 Diagnose before coding:</strong> for this subtopic, fill out '
            '<strong>Grain</strong> and <strong>Joins</strong> in the <em>Modeling '
            'Diagnostic</em> (section 2) and click <em>Get Modeling Feedback</em> '
            'BEFORE writing SQL. Grain is the headline check here; the SQL is the easy part.'
            '</div>'
        )
    glossary_html = glossary_to_html(p.get("glossary", []))
    calc_html = calculation_explanation_to_html(p.get("calculation_explanation", ""))
    prompt_html = prompt_to_bullets_nested(p.get("prompt", ""))
    schema_html = schema_to_html(p.get("schema_ddl", ""))
    data_html = insert_data_to_html(p.get("example_input_data", ""), p.get("schema_ddl", ""))
    ex_cols = p.get("example_output_columns", [])
    ex_rows = p.get("example_output_rows", [])
    ex_df = pd.DataFrame(ex_rows, columns=ex_cols)
    ex_html = ex_df.to_html(index=False, classes="ex-out") if not ex_df.empty else "<em>(no expected output)</em>"

    open_attr = "" if compact else " open"
    section = lambda label, body, opn=open_attr: (
        f'<details{opn} style="margin-top:14px;">'
        f'<summary style="cursor:pointer; color:#0969da; font-weight:600;">{label}</summary>'
        f'<div style="margin-top:8px;">{body}</div></details>'
    )
    # Interpretation + recommendation examples live under collapsed-by-default details
    # regardless of compact mode — the user should attempt blind first, then peek
    interp_section = ""
    if p.get("interpretation_example"):
        interp_section = (
            '<details style="margin-top:14px;">'
            '<summary style="cursor:pointer; color:#1a7f37; font-weight:600;">'
            '🟢 Show example interpretation (peek when stuck — practice your own first)'
            '</summary>'
            f'<div style="margin-top:8px;">{interpretation_to_html(p.get("interpretation_example",""))}</div>'
            '</details>'
        )
    rec_section = ""
    if p.get("recommendation_example"):
        rec_section = (
            '<details style="margin-top:8px;">'
            '<summary style="cursor:pointer; color:#8b3a0e; font-weight:600;">'
            '🟠 Show example recommendation (peek when stuck — practice your own first)'
            '</summary>'
            f'<div style="margin-top:8px;">{recommendation_to_html(p.get("recommendation_example",""))}</div>'
            '</details>'
        )

    return (
        '<div style="border:1px solid #d0d7de; border-radius:6px; padding:16px; background:#fafbfc;">'
        f'<div style="font-size:11px; color:#57606a; margin-bottom:8px;">'
        f'{meta.get("category","")} → {meta.get("subtopic","")} · {meta.get("dialect","")} · id {meta.get("problem_id","")}'
        '</div>'
        f'<h3 style="margin:0 0 12px;">{title}</h3>'
        f'{modeling_nudge_html}'
        f'<div style="background:#eef5fc; padding:8px 12px; border-radius:4px; font-size:13px; margin-bottom:10px;">'
        f'<strong>Scenario:</strong> {scenario}</div>'
        f'{glossary_html}'
        f'{calc_html}'
        '<h4 style="margin-top:14px;">Prompt</h4>'
        f'{prompt_html}'
        + section("Schema", schema_html)
        + section("Example input data", data_html)
        + section("Expected output (example data)", ex_html)
        + interp_section
        + rec_section
        + '</div>'
    )


def render_kpi_problem(p: Dict[str, Any], compact: bool = False) -> str:
    """Render a KPI problem as HTML."""
    meta = p.get("_meta", {})
    title = p.get("title", "Untitled")
    scenario = p.get("scenario", "")
    subtopic = meta.get("subtopic", "")
    modeling_nudge_html = ""
    if subtopic == "schema_design":
        # Schema_design has its own form as the 4th panel in section 2's accordion
        modeling_nudge_html = (
            '<div style="background:#fff8e1; border-left:4px solid #f9a825; '
            'padding:8px 12px; border-radius:4px; font-size:13px; margin-bottom:10px;">'
            '<strong>👉 Your answer goes in section 2</strong> — open the '
            '<em>Schema Design Response Form</em> panel (4th accordion item). '
            'Section 3 is SQL only and will be unused for this drill.'
            '</div>'
        )
    elif subtopic in _MODELING_DIAGNOSTIC_NUDGE_SUBTOPICS:
        modeling_nudge_html = (
            '<div style="background:#fff8e1; border-left:4px solid #f9a825; '
            'padding:8px 12px; border-radius:4px; font-size:13px; margin-bottom:10px;">'
            '<strong>👉 Diagnose before writing:</strong> for this subtopic, fill out '
            '<strong>Grain</strong> and <strong>Joins</strong> in the <em>Modeling '
            'Diagnostic</em> (section 2) and click <em>Get Modeling Feedback</em> first. '
            'That gets graded feedback on your modeling thinking before you commit it to '
            'the markdown answer below. ASCII diagrams and markdown welcome in the diagnostic '
            'fields.'
            '</div>'
        )
    rubric_html = rubric_to_html(p.get("grading_rubric", []))
    themes_html = themes_to_html(p.get("expected_themes", []))
    open_attr = "" if compact else " open"
    schema_ddl = p.get("schema_ddl", "")
    schema_block_html = ""
    if schema_ddl and schema_ddl.strip():
        schema_block_html = (
            f'<details{open_attr} style="margin-top:14px;">'
            f'<summary style="cursor:pointer; color:#0969da; font-weight:600;">Schema</summary>'
            f'<div style="margin-top:8px;">{schema_to_html(schema_ddl)}</div></details>'
        )
    candidate_dims = p.get("candidate_dimensions", [])
    candidate_dims_block_html = ""
    if candidate_dims and isinstance(candidate_dims, list):
        rows_html = "".join(
            f'<tr style="border-bottom:1px solid #e0e0e0;">'
            f'<td style="padding:8px 12px; font-weight:600;"><code>{d.get("name","?")}</code></td>'
            f'<td style="padding:8px 12px; color:#0969da;"><code>{d.get("key","?")}</code></td>'
            f'<td style="padding:8px 12px; color:#444;">{d.get("description","")}</td>'
            f'</tr>'
            for d in candidate_dims
        )
        candidate_dims_block_html = (
            f'<details{open_attr} style="margin-top:14px;">'
            f'<summary style="cursor:pointer; color:#0969da; font-weight:600;">'
            f'Candidate dimensions you can join'
            f'</summary>'
            f'<div style="margin-top:8px;">'
            f'<div style="font-size:12px; color:#57606a; margin-bottom:6px;">'
            f'Pick from this list in the form. dim tables are NOT pre-built — '
            f'you propose which to use and how (SCD type, surrogate keys).'
            f'</div>'
            f'<table style="width:100%; border-collapse:collapse; font-size:13px;">'
            f'<thead><tr style="background:#f6f8fa; border-bottom:2px solid #d0d7de;">'
            f'<th style="padding:8px 12px; text-align:left;">Dim table</th>'
            f'<th style="padding:8px 12px; text-align:left;">Key column</th>'
            f'<th style="padding:8px 12px; text-align:left;">Description</th>'
            f'</tr></thead>'
            f'<tbody>{rows_html}</tbody></table></div></details>'
        )
    return (
        '<div style="border:1px solid #d0d7de; border-radius:6px; padding:16px; background:#fafbfc;">'
        f'<div style="font-size:11px; color:#57606a; margin-bottom:8px;">'
        f'{meta.get("category","")} → {meta.get("subtopic","")} · markdown · id {meta.get("problem_id","")}'
        '</div>'
        f'<h3 style="margin:0 0 12px;">{title}</h3>'
        f'{modeling_nudge_html}'
        f'<div style="background:#eef5fc; padding:8px 12px; border-radius:4px; font-size:13px; margin-bottom:10px;">'
        f'<strong>Scenario:</strong> {scenario}</div>'
        '<h4 style="margin-top:6px;">Prompt</h4>'
        f'<div style="line-height:1.5;">{prompt_to_bullets_nested(p.get("prompt",""))}</div>'
        f'{schema_block_html}'
        f'{candidate_dims_block_html}'
        '<h4 style="margin-top:18px;">Instructions for your answer</h4>'
        f'<div style="background:#fff8c5; padding:10px 14px 4px 14px; border-left:3px solid #d4a72c; border-radius:4px;">{prompt_to_bullets_nested(p.get("instructions",""))}</div>'
        f'<details{open_attr} style="margin-top:14px;"><summary style="cursor:pointer; color:#0969da; font-weight:600;">Show grading rubric</summary>'
        f'<div style="margin-top:8px;">{rubric_html}</div></details>'
        f'<details style="margin-top:8px;"><summary style="cursor:pointer; color:#0969da;">Show expected themes (peek before you write — coaches you, doesn\'t disqualify you)</summary>'
        f'<div style="margin-top:8px;">{themes_html}</div></details>'
        '</div>'
    )


def calculation_explanation_to_html(explanation: str) -> str:
    """Render the calculation walkthrough in a soft callout box.

    Tolerant of three input formats:
      (a) one step per line, each prefixed '1. ' / '2) ' / etc — split on newlines
      (b) all steps inline on a single line: '1. Foo. 2. Bar. 3. Baz.' — split on
          '<digit>. ' boundaries using regex lookahead
      (c) plain prose with no numbered structure — render as <p>
    """
    if not explanation:
        return ""

    # First try newline split
    lines = [l.strip() for l in explanation.split("\n") if l.strip()]

    # If we got just one (or two) lines but the text contains MULTIPLE inline
    # numbered steps, split on those boundaries instead. This catches the LLM
    # emitting all steps on a single physical line.
    joined = " ".join(lines)
    inline_steps = _re.findall(r'(?:^|\s|\.)(\d+)[\.\)]\s+\S', joined)
    if len(lines) <= 2 and len(set(inline_steps)) >= 2:
        # Split on a boundary BEFORE each '<digit>. ' that follows whitespace
        # (or start of string). The lookahead keeps the digit attached to its step.
        parts = _re.split(r'(?<=\s)(?=\d+[\.\)]\s)|(?<=^)(?=\d+[\.\)]\s)', joined)
        # Some Python regex engines won't honor the empty-position lookbehind on
        # start-of-string; defensively re-split on the more common case
        if len(parts) <= 1:
            parts = _re.split(r'\s+(?=\d+[\.\)]\s)', joined)
        lines = [p.strip() for p in parts if p.strip()]

    has_steps = any(_re.match(r"^\d+[\.\)]", l) for l in lines)
    if has_steps:
        items = []
        for l in lines:
            l_clean = _re.sub(r"^\d+[\.\)]\s*", "", l)
            # Strip a trailing standalone period only when the cleaned step is
            # a single sentence (avoids stripping mid-sentence punctuation)
            items.append(f'<li style="margin-bottom:6px;">{l_clean}</li>')
        body = '<ol style="margin:0 0 0 22px; padding-left:0; line-height:1.55;">' + "".join(items) + '</ol>'
    else:
        body = f'<p style="margin:0; line-height:1.55;">{explanation}</p>'
    return (
        '<div style="background:#eef5fc; border-left:3px solid #2563a8; padding:10px 14px; '
        'border-radius:4px; margin:10px 0;">'
        '<div style="font-weight:600; font-size:13px; margin-bottom:6px; color:#0c447c;">'
        'How the calculation works</div>'
        + body + '</div>'
    )


def expected_to_dataframe(problem: Dict[str, Any], which: str = "example") -> pd.DataFrame:
    return spu.expected_to_dataframe(problem, which)


def rubric_to_html(rubric: List[Dict[str, Any]]) -> str:
    """Render a KPI grading rubric as an HTML table."""
    if not rubric:
        return ""
    df = pd.DataFrame(rubric)
    if "weight" in df.columns:
        df = df[["criterion", "description", "weight"]] if "description" in df.columns else df
    return df.to_html(index=False, classes="kpi-rubric-table")


def themes_to_html(themes: List[str]) -> str:
    if not themes:
        return ""
    items = "".join(f'<li style="margin-bottom:3px;">{t}</li>' for t in themes)
    return f'<ul style="margin:0 0 0 18px; padding-left:0;">{items}</ul>'


def grade_to_html(grade: Dict[str, Any]) -> str:
    """Render a KPI grading result as nicely formatted HTML."""
    if not grade:
        return '<div style="color:#cf222e;">Grading failed.</div>'
    total = grade.get("total_score", 0)
    color = "#1a7f37" if total >= 80 else ("#9a6700" if total >= 60 else "#cf222e")
    parts = [
        f'<div style="border:1px solid #d0d7de; border-radius:6px; padding:14px; background:#f6f8fa;">',
        f'<h4 style="margin:0 0 10px;">Grade: <span style="color:{color}; font-size:18px;">{total}/100</span></h4>',
    ]
    # Per-criterion table
    scores = grade.get("scores", [])
    if scores:
        rows = ""
        for s in scores:
            crit = s.get("criterion", "")
            wt = s.get("weight", 0)
            earned = s.get("earned", 0)
            fb = s.get("feedback", "")
            pct = (earned / wt * 100) if wt else 0
            row_color = "#1a7f37" if pct >= 80 else ("#9a6700" if pct >= 50 else "#cf222e")
            rows += (
                f'<tr><td><strong>{crit}</strong></td>'
                f'<td style="color:{row_color}; font-weight:600;">{earned}/{wt}</td>'
                f'<td style="font-size:13px;">{fb}</td></tr>'
            )
        parts.append(
            '<table style="width:100%; border-collapse:collapse; margin-bottom:10px;">'
            '<thead><tr style="background:#eaeef2;">'
            '<th style="text-align:left; padding:6px;">Criterion</th>'
            '<th style="text-align:left; padding:6px;">Score</th>'
            '<th style="text-align:left; padding:6px;">Feedback</th>'
            '</tr></thead><tbody>' + rows + '</tbody></table>'
        )
    # Themes hit / missed
    hit = grade.get("themes_hit", [])
    missed = grade.get("themes_missed", [])
    if hit or missed:
        parts.append('<div style="display:flex; gap:16px; margin-bottom:10px;">')
        if hit:
            parts.append(
                '<div style="flex:1; background:#dcfce7; border-left:3px solid #1a7f37; padding:8px;">'
                '<strong>Themes hit:</strong>' + themes_to_html(hit) + '</div>'
            )
        if missed:
            parts.append(
                '<div style="flex:1; background:#ffebe9; border-left:3px solid #cf222e; padding:8px;">'
                '<strong>Themes missed:</strong>' + themes_to_html(missed) + '</div>'
            )
        parts.append('</div>')
    # Strong / improve
    strong = grade.get("what_was_strong", "")
    improve = grade.get("what_to_improve", "")
    nxt = grade.get("next_problem_focus", "")
    if strong:
        parts.append(f'<p style="margin:6px 0;"><strong>Strong:</strong> {strong}</p>')
    if improve:
        parts.append(f'<p style="margin:6px 0;"><strong>Improve:</strong> {improve}</p>')
    if nxt:
        parts.append(f'<p style="margin:6px 0; font-style:italic; color:#57606a;"><strong>Next:</strong> {nxt}</p>')
    parts.append('</div>')
    return "".join(parts)


# ============================================================
# Multiple choice drill generator + grader
# ============================================================
# Generates a quiz of mixed question types: MCQ, True/False, and "order"
# (arrange steps in the right sequence). Designed for terminology and
# concept reinforcement before higher stakes free response drills.

MULTIPLE_CHOICE_TOPIC_HINTS = {
    "transformation_modeling": (
        "Cover the standard Kimball + dbt vocabulary an analytics engineer would be expected to know cold: "
        "fact vs dim tables; grain (what one row of a fact represents); SCD Type 1 vs Type 2 vs Type 3 vs hybrid; "
        "surrogate keys vs natural keys; conformed dimensions; junk dimensions; degenerate dimensions; "
        "snowflake vs star schema; materializations (table, view, incremental, ephemeral); "
        "dbt project structure (sources, staging, intermediate, marts); ref() and source() macros; "
        "dbt tests (unique, not_null, accepted_values, relationships); snapshots; seeds; exposures; "
        "incremental strategy (append, merge, delete+insert); idempotency; late arriving facts; "
        "additive vs semi additive vs non additive measures; slowly changing dimensions effective dating; "
        "Bridge tables; role playing dimensions; outrigger dimensions."
    ),
    "product_kpis": (
        "Cover the working vocabulary of a Product Analyst: leading vs lagging indicators; "
        "counter metrics; vanity metrics vs actionable metrics; north star metric; AARRR funnel; "
        "input vs output metrics; activation vs adoption vs retention; cohort retention vs revenue retention; "
        "DAU/MAU stickiness ratio; rolling vs snapshot metrics; event vs user properties; super properties; "
        "tracking plan; event taxonomy; identify vs alias vs track; experiment design (A/A test, A/B test, "
        "multivariate); guardrail metrics; statistical significance vs practical significance; "
        "Type I vs Type II error; SRM (Sample Ratio Mismatch); novelty effect; primacy effect; survivorship bias; "
        "PRD impact measurement section; OKRs vs KPIs; HEART framework; PIRATE / AARRR; jobs to be done."
    ),
    "version_control": (
        "Cover the Git workflows an analytics engineer is expected to know: trunk based development; "
        "git flow; GitHub flow; short lived feature branches; rebase vs merge; fast forward merge; "
        "squash merge; merge commit; force push vs force with lease; revert vs reset (soft, mixed, hard); "
        "cherry pick; bisect; stash; reflog; HEAD vs detached HEAD; conflict markers (<<<<<<<, =======, >>>>>>>); "
        "Conventional Commits; semantic versioning; pull request review checklist (single purpose, naming, "
        "tests, docs); CODEOWNERS; protected branches; pre commit hooks; .gitignore basics; submodules vs subtrees."
    ),
}


MULTIPLE_CHOICE_GENERATOR_SYSTEM = """\
You are an interview prep quiz generator for an analyst. You write multiple choice quizzes that test
terminology and concept understanding the candidate would be expected to know cold in interviews.

Output ONE JSON object with this exact shape (inside a single ```json fenced block; NO prose around it):

{
  "title": "Short quiz title (5 to 8 words)",
  "introduction": "1 to 2 sentence intro framing what the quiz tests",
  "questions": [
    {
      "id": "q1",
      "type": "mcq",
      "question": "Stem of the question, one sentence.",
      "options": ["option A", "option B", "option C", "option D"],
      "correct_answer": 1,
      "explanation": "1 to 2 sentence teaching explanation citing why the correct answer is right and naming the trap in the distractors."
    },
    {
      "id": "q2",
      "type": "true_false",
      "question": "A statement that is either true or false. Avoid double negatives.",
      "options": ["True", "False"],
      "correct_answer": 0,
      "explanation": "1 to 2 sentence teaching explanation."
    },
    {
      "id": "q3",
      "type": "order",
      "question": "Arrange these steps in the order they should be performed when <doing X>.",
      "options": ["step shown out of order A", "step shown out of order B", "step shown out of order C", "step shown out of order D"],
      "correct_answer": [2, 0, 3, 1],
      "explanation": "1 to 2 sentence explanation of the correct sequence and why."
    }
  ]
}

RULES:
- Exactly 8 questions total.
- Mix the types: at least 3 mcq, at least 2 true_false, at least 2 order questions.
- mcq has exactly 4 options. correct_answer is the index (0 to 3) of the correct option.
- true_false has exactly the options ["True", "False"]. correct_answer is 0 for True or 1 for False.
- order has 4 to 5 options shown out of order. correct_answer is a list of indices that, applied to options,
  yields the correct sequence (e.g., correct_answer=[2,0,3,1] means options[2] is first, options[0] second,
  options[3] third, options[1] fourth).
- Every question MUST have an explanation that teaches the concept. The explanation should also name what
  the wrong answers represent so the learner sees the trap.
- Distractors in mcq must be plausible but clearly wrong on inspection. Avoid "all of the above" / "none of the above".
- Avoid trivia. Focus on concepts and terminology that show up in technical interviews and product analyst
  case studies.
- No company names. Generic phrasing only.
- Do NOT include any markdown or HTML in question text, options, or explanations. Plain text only.
"""


def _build_mc_user_prompt(category: str, last_error: Optional[str] = None) -> str:
    label = CATEGORIES[category]["label"]
    topic_hint = MULTIPLE_CHOICE_TOPIC_HINTS.get(category, "")
    guidance = (
        f"Generate a multiple choice interview prep quiz for the category: {label}.\n\n"
        f"Topic surface area to draw from:\n{topic_hint}\n\n"
        "Pick a coherent slice of this surface area for the 8 questions (do NOT try to cover everything). "
        "Aim for a mix of definitional questions (what is X?), comparative questions (X vs Y), and process "
        "questions (which step comes first?).\n"
    )
    if last_error:
        guidance += (
            "\n!!! PREVIOUS ATTEMPT FAILED VALIDATION !!!\n"
            f"{last_error}\n"
            "Fix the issue and emit ONE valid JSON object inside a single ```json fenced block.\n"
        )
    guidance += "\nReturn the JSON object now."
    return guidance


def _validate_mc_problem(parsed: Dict[str, Any]) -> Tuple[bool, str]:
    if not isinstance(parsed, dict):
        return False, "Top level is not a JSON object."
    for k in ("title", "introduction", "questions"):
        if k not in parsed:
            return False, f"Missing required top level key: {k}"
    qs = parsed["questions"]
    if not isinstance(qs, list) or len(qs) != 8:
        return False, f"Expected exactly 8 questions, got {len(qs) if isinstance(qs, list) else 'non-list'}."
    type_counts = {"mcq": 0, "true_false": 0, "order": 0}
    for i, q in enumerate(qs):
        if not isinstance(q, dict):
            return False, f"Question {i} is not an object."
        for k in ("id", "type", "question", "options", "correct_answer", "explanation"):
            if k not in q:
                return False, f"Question {i} missing key: {k}"
        qt = q["type"]
        if qt not in type_counts:
            return False, f"Question {i} has unknown type {qt!r}."
        type_counts[qt] += 1
        opts = q["options"]
        if not isinstance(opts, list):
            return False, f"Question {i} options is not a list."
        ca = q["correct_answer"]
        if qt == "mcq":
            if len(opts) != 4:
                return False, f"Question {i} (mcq) needs exactly 4 options, got {len(opts)}."
            if not (isinstance(ca, int) and 0 <= ca < 4):
                return False, f"Question {i} (mcq) correct_answer must be an int 0..3, got {ca!r}."
        elif qt == "true_false":
            if opts != ["True", "False"]:
                return False, f"Question {i} (true_false) options must be exactly ['True', 'False']."
            if not (isinstance(ca, int) and ca in (0, 1)):
                return False, f"Question {i} (true_false) correct_answer must be 0 or 1."
        elif qt == "order":
            if not (4 <= len(opts) <= 5):
                return False, f"Question {i} (order) needs 4 to 5 options, got {len(opts)}."
            if not (isinstance(ca, list) and len(ca) == len(opts)):
                return False, f"Question {i} (order) correct_answer must be a list of indices the same length as options."
            if sorted(ca) != list(range(len(opts))):
                return False, f"Question {i} (order) correct_answer must be a permutation of 0..{len(opts)-1}."
    if type_counts["mcq"] < 3:
        return False, f"Need at least 3 mcq questions; got {type_counts['mcq']}."
    if type_counts["true_false"] < 2:
        return False, f"Need at least 2 true_false questions; got {type_counts['true_false']}."
    if type_counts["order"] < 2:
        return False, f"Need at least 2 order questions; got {type_counts['order']}."
    return True, "Valid."


def generate_multiple_choice_problem(category: str, max_retries: int = 4,
                                     on_attempt=None,
                                     scenario_mode: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Generate a multiple choice quiz problem for the given category.
    scenario_mode: None or 'random' for generic vocabulary; 'booedup' to anchor
    questions in the user's BooedUp dating app context where it makes sense."""
    if category not in CATEGORIES:
        print(f"Unknown category: {category}")
        return None
    last_error = None
    for attempt in range(1, max_retries + 1):
        if on_attempt:
            try:
                on_attempt(attempt, max_retries, last_error)
            except Exception:
                pass
        user_prompt = _build_mc_user_prompt(category, last_error)
        user_prompt = apply_scenario_anchor(user_prompt, scenario_mode)
        text = _call_claude(MULTIPLE_CHOICE_GENERATOR_SYSTEM, user_prompt, max_tokens=3000)
        parsed = _extract_json(text)
        if not parsed:
            last_error = "Could not parse JSON from response."
            continue
        ok, err = _validate_mc_problem(parsed)
        if not ok:
            last_error = err
            continue
        parsed["_meta"] = {
            "category": category,
            "subtopic": "multiple_choice",
            "kind": "multiple_choice",
            "question_type": None,
            "dialect": None,
            "scenario_mode": scenario_mode or "random",
            "generated_at": datetime.now().isoformat(),
            "problem_id": uuid.uuid4().hex[:12],
            "validation_attempts": attempt,
            "notebook": "nb02_analyst_interview_drills",
        }
        return parsed
    print(f"Multiple choice generation failed after {max_retries} attempts. Last error: {last_error}")
    return None


def grade_multiple_choice_answers(problem: Dict[str, Any],
                                  user_answers: Dict[str, Any]) -> Dict[str, Any]:
    """Grade the user's answers against the quiz's correct_answer keys.

    Returns a dict with:
      score: int — number correct out of total
      total: int
      results: list[{id, type, correct, user_answer, correct_answer, explanation}]
    """
    qs = problem.get("questions", [])
    results = []
    correct = 0
    for q in qs:
        qid = q.get("id", "")
        qt = q.get("type", "")
        user_a = user_answers.get(qid)
        right = q.get("correct_answer")
        is_correct = False
        if qt in ("mcq", "true_false"):
            if isinstance(user_a, int) and user_a == right:
                is_correct = True
        elif qt == "order":
            if isinstance(user_a, list) and user_a == right:
                is_correct = True
        if is_correct:
            correct += 1
        results.append({
            "id": qid,
            "type": qt,
            "question": q.get("question", ""),
            "options": q.get("options", []),
            "user_answer": user_a,
            "correct_answer": right,
            "is_correct": is_correct,
            "explanation": q.get("explanation", ""),
        })
    return {
        "score": correct,
        "total": len(qs),
        "results": results,
    }


def render_multiple_choice_problem(p: Dict[str, Any]) -> str:
    """HTML render of the quiz introduction; questions are rendered as widgets, not HTML."""
    meta = p.get("_meta", {})
    title = p.get("title", "Untitled quiz")
    intro = p.get("introduction", "")
    cat_label = CATEGORIES.get(meta.get("category", ""), {}).get("label", "")
    return (
        '<div style="border:1px solid #d0d7de; border-radius:6px; padding:16px; background:#fafbfc;">'
        f'<div style="font-size:11px; color:#57606a; margin-bottom:8px;">{cat_label} · multiple_choice · id {meta.get("problem_id","")}</div>'
        f'<h3 style="margin:0 0 12px;">{title}</h3>'
        f'<p style="margin:0;">{intro}</p>'
        '</div>'
    )


# ============================================================
# Scenario anchor: BooedUp dating app context
# ============================================================
# When the picker's scenario_mode is "booedup", every generator wraps its
# user prompt with this app context so the LLM grounds the problem in the
# learner's actual product instead of a generic business scenario.

BOOEDUP_APP_CONTEXT = """\
APP CONTEXT — anchor the problem in this product, not a generic scenario:

PRODUCT: BooedUp, a mobile dating app for gay men. The differentiator is a
map first interface (no swiping), real time geolocation, AI driven Type Score
personalization for physical attraction, mutual physical attraction emphasis,
and offline community engagement via speed dating events. All users are
verified.

TECH STACK: FlutterFlow front end, Firebase backend (Firestore, Auth, Cloud
Functions in us-central1, Cloud Messaging for push). Stripe for premium
subscription billing. Node.js 20 Cloud Functions. iOS + Android.

RELATIONSHIP MODEL (core domain concept):
- Two relationship types: Match (romantic) and Wingman (platonic friend).
- Match grants messaging, dating event invites, personalized date recs, and
  reveals the Match Score (compatibility).
- Wingman grants messaging, ability to recommend users, member spotlight
  nominations, and event invites; reveals the Wingman Score (shared lifestyle).
- Transitions: Match↔Wingman (unmatch needed before becoming Wingman, mutual
  agreement needed for the reverse), Match→Block, Wingman→Block, Match→None,
  Wingman→None. Each transition has a 1 month cooldown, reduced to 1 week
  for Premium members, removable via A la carte purchase.

SCORES:
- Type Score: AI driven model predicting whether the viewing user finds the
  candidate physically attractive. Trained on the user's preference signals.
- Match Score: compatibility, visible only after mutual match.
- Wingman Score: based on mutual shared lifestyle interests.

GEO MODEL: every user has three locations they can change with monthly limits
gated by membership tier:
- home_city (where they live)
- work_city (where they commute to)
- visiting_city (a temporary location, e.g., travel)
Basic tier: 1 home city change per 30 day period. Premium tier: 3 each of
home / work / visiting per 30 day period. Tracked via membershipTier,
homeCityMonthlyLimit, homeCityChangeCount, homeCityLastChangedAt,
homeCityLockedUntil, homeCityChangePasses fields on userMetadata.

SUBSCRIPTION TIERS:
- Basic (free, default for new users): minimal city change allowance.
- Premium ($9.99/month USD): 3x more city changes per tier, reduced cooldown
  on relationship transitions, ability to see who viewed your profile.
- A la carte purchases: instant cooldown removal, additional city change
  passes, profile boosts.

KEY FIRESTORE COLLECTIONS (the user's actual schema):
- userDetails — profile bio, demographics, physical attributes
- userPhotos / userVideos / userAudio — media
- userMetadata — membership tier, change counters, lock timestamps
- userConnections — unified Match + Wingman relationship state
- userInteractions — likes, winks, superlikes
- partnerPreferences — physical, lifestyle, relationship preferences
- typeScores — Type Score model outputs per (viewer, candidate) pair
- nearbyUsers — geo indexed for the map view
- blockedUsers / reportedUsers — moderation
- membershipPlans / premiumRecord / userPurchases — billing

KEY USER ACTIONS (the events you would log in a tracking plan):
- Sign up + verification (multi step, requires photo verification to pass)
- Profile setup (lifestyle, physical, relationship preference steps)
- Open map + change radius
- Tap profile marker
- Send first message (after Match or Wingman established)
- Initiate Match / accept Match / decline Match
- Initiate Wingman / accept Wingman / decline Wingman
- Transition (Match → Wingman, Match → Block, etc.)
- Buy Premium / cancel Premium
- Buy A la carte (cooldown removal, change pass)
- RSVP to speed dating event / check in / complete pairings
- Report user / block user

PRIMARY METRICS THAT MATTER:
- Activation funnel: signup → verification passed → profile complete → first
  map view → first interaction → first Match
- D1 / D7 / D30 retention
- Mutual match rate (matches per interaction initiated)
- Type Score quality: precision/recall vs actual mutual matches
- Premium conversion rate and ARPU
- Premium churn rate
- Time to first Match (cohort distribution)
- Messages per Match (engagement depth)
- Report rate, block rate, time to action on reports (safety)
- Speed dating event funnel: RSVP → check in → completed pairings

When you generate a problem, anchor the scenario in BooedUp. Use the
collection names, action names, and metric names above. Replace generic
"e-commerce" or "SaaS" framings with this app. Do NOT invent features
the app does not have (no swiping, no group chat unless framed as a future
hypothetical, no ads since the product relies on subscription + a la carte
revenue).
"""


def with_booedup_context(user_prompt: str) -> str:
    """Prepend the BooedUp app context to a user prompt when scenario_mode is
    set to 'booedup'. Returns the prompt unchanged for any other scenario_mode."""
    return BOOEDUP_APP_CONTEXT + "\n\n" + user_prompt


def apply_scenario_anchor(user_prompt: str, scenario_mode: Optional[str]) -> str:
    """Single entry point for anchoring a user prompt. Pass scenario_mode from
    the picker (None or 'random' = generic; 'booedup' = anchor on the dating
    app). Future scenarios can be added here by extending the if/elif chain."""
    if scenario_mode == "booedup":
        return with_booedup_context(user_prompt)
    return user_prompt



# ============================================================
# Metric explorer — generate worked examples for the bad metric,
# the learner's picked replacement, and each starred alternative.
# Called from the metric_critique form's 🔍 Explain button and
# auto fired at the end of Get Grade.
# ============================================================

METRIC_EXPLORER_SYSTEM = """\
You are a product analytics tutor helping a learner connect metric design choices
to a concrete scenario. The learner has been shown a flawed metric and has picked
a corrected numerator / denominator / guardrail. You must show, with worked
examples on synthetic data, how each candidate metric would actually be computed
and what reading the number would tell the team — and why the original bad metric
fails to address the scenario's stated purpose.

Output ONE JSON object inside a single ```json fenced block. NO prose around it.
"""


def _build_explain_user_prompt(problem, user_picks, alternative_picks):
    """Compose the user prompt for the metric explorer."""
    scenario = problem.get("scenario", "")
    bad_metric = (problem.get("proposed_metric", "")
                  or problem.get("title", "")
                  or "the proposed metric in the prompt")
    rationale = problem.get("stakeholder_rationale", "")
    user_num = user_picks.get("numerator", "")
    user_denom = user_picks.get("denominator", "")
    user_guard = user_picks.get("guardrail", "")

    alt_nums = alternative_picks.get("numerator", []) or []
    alt_denoms = alternative_picks.get("denominator", []) or []
    alt_guards = alternative_picks.get("guardrail", []) or []

    parts = []
    parts.append(f"SCENARIO (purpose): {scenario}")
    parts.append(f"BAD METRIC (under critique): {bad_metric}")
    if rationale:
        parts.append(f"STAKEHOLDER RATIONALE: {rationale}")
    parts.append("")
    parts.append("LEARNER'S PICKED REPLACEMENT METRIC:")
    parts.append(f"  Numerator:   {user_num}")
    parts.append(f"  Denominator: {user_denom}")
    parts.append(f"  Guardrail:   {user_guard}")
    parts.append("")
    parts.append("ALL OTHER STARRED ALTERNATIVES (dynamic picks the learner did NOT choose):")
    for n in alt_nums:
        parts.append(f"  Alt numerator:   {n}")
    for d in alt_denoms:
        parts.append(f"  Alt denominator: {d}")
    for g in alt_guards:
        parts.append(f"  Alt guardrail:   {g}")
    parts.append("")
    parts.append(
        "Return a JSON object with this shape:\n\n"
        "{\n"
        "  \"bad_metric\": {\n"
        "    \"name\": \"<the bad metric's name>\",\n"
        "    \"what_it_measures\": \"<one sentence>\",\n"
        "    \"example_data\": [\n"
        "      {\"row\": \"<entity label>\", \"<col1>\": <num>, \"<col2>\": <num>}\n"
        "    ],\n"
        "    \"calculation\": \"<step by step calculation on the example data>\",\n"
        "    \"value\": \"<the resulting number, e.g. '342 messages this week'>\",\n"
        "    \"interpretation\": \"<what reading this value would actually tell the team>\",\n"
        "    \"why_it_fails_the_purpose\": \"<one or two sentences: why this metric does NOT actually answer the scenario's question>\"\n"
        "  },\n"
        "  \"user_picked_metric\": {\n"
        "    \"name\": \"<readable name, e.g. 'Messages sent in first 24h / Match connections'>\",\n"
        "    \"what_it_measures\": \"<one sentence>\",\n"
        "    \"example_data\": [...],  // RECOMPUTE on the SAME entity population as bad_metric, different aggregation\n"
        "    \"calculation\": \"<step by step>\",\n"
        "    \"value\": \"<resulting rate / number with units>\",\n"
        "    \"interpretation\": \"<what this tells the team>\",\n"
        "    \"why_it_addresses_the_purpose\": \"<one or two sentences linking the metric to the scenario's actual question>\"\n"
        "  },\n"
        "  \"alternatives\": [\n"
        "    {\n"
        "      \"name\": \"<alt metric name>\",\n"
        "      \"what_it_measures\": \"<one sentence>\",\n"
        "      \"example_data\": [...],\n"
        "      \"calculation\": \"<step by step>\",\n"
        "      \"value\": \"<resulting number>\",\n"
        "      \"interpretation\": \"<one or two sentences>\",\n"
        "      \"trade_off_vs_picked\": \"<how this alternative differs from the learner's pick — what it captures or misses>\"\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        "REQUIREMENTS:\n"
        "- Use 4 to 6 synthetic data rows total. Keep them simple integers (5 to 50 range).\n"
        "- Use the SAME synthetic population across bad_metric, user_picked_metric, and "
        "every alternative. Only the AGGREGATION should differ. This makes the comparison "
        "honest — same data, different lens.\n"
        "- Build ONE alternative entry for each starred alternative numerator above. "
        "Pair each with the most natural denominator + guardrail from the alternatives list.\n"
        "- Calculations must show actual arithmetic on the example data (e.g., \"8 + 5 + 0 + 12 = 25 "
        "messages; 25 / 3 Match connections = 8.3 messages per Match\").\n"
        "- Interpretations must be 1 to 2 sentences, written as if a PM is reading the dashboard.\n"
        "- Do not invent metrics that are not in the lists above.\n"
        "- Match the scenario domain — do not invent unrelated products.\n"
    )
    return "\n".join(parts)


def explain_metrics(problem: Dict[str, Any],
                    user_picks: Dict[str, str],
                    alternative_picks: Dict[str, list],
                    max_retries: int = 2) -> Optional[Dict[str, Any]]:
    """Generate the metric explorer JSON. Returns None on failure."""
    last_error = None
    for attempt in range(1, max_retries + 1):
        user_prompt = _build_explain_user_prompt(problem, user_picks, alternative_picks)
        if last_error:
            user_prompt += f"\n\nPREVIOUS ATTEMPT FAILED: {last_error}\nFix the issue and emit valid JSON."
        text = _call_claude(METRIC_EXPLORER_SYSTEM, user_prompt, max_tokens=3500)
        parsed = _extract_json(text)
        if not parsed:
            last_error = "Could not parse JSON from response."
            continue
        # Lightweight shape check
        if "bad_metric" not in parsed or "user_picked_metric" not in parsed:
            last_error = "Missing required top level keys (bad_metric / user_picked_metric)."
            continue
        return parsed
    print(f"explain_metrics failed after {max_retries} attempts. Last error: {last_error}")
    return None
