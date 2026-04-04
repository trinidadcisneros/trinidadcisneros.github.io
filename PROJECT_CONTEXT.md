# BitterScientist.com — Project Context & Handoff Guide

**Owner:** Trinidad Cisneros (trinidad.cisneros@gmail.com)
**Domain:** bitterscientist.com
**Last Updated:** 2026-04-03 (Session 8)

---

## What This File Is For

This file is a handoff document for use with any LLM tool (Claude Cowork, ChatGPT, Cursor, etc.) when starting a new session. Paste or reference this file at the start of a conversation so the assistant understands the site's structure, conventions, and recent work — without having to re-discover everything from scratch.

---

## 1. Site Overview

BitterScientist.com is a personal portfolio and educational blog focused on analytics, data science, statistics, programming, and database concepts. Content is presented as tutorial-style posts, most of which originate as Jupyter notebooks converted to HTML and embedded in wrapper pages with a shared navbar and footer.

**Hosting:** GitHub Pages (static site, no backend)
**Root File:** `index.html` (landing page — hero, "Latest Posts" cards, "Beyond the Data" photo/video carousel)
**Config:** `config.json` at root
**CNAME:** `bitterscientist.com`
**Post Registry:** `static/data/posts.json` (single source of truth for latest posts — landing page reads from this)
**Hero Counter:** Hardcoded "170+ guides & projects published" (posts.json only tracks ~14 featured posts, not all 170+)

---

## 2. Directory Structure

```
bitterscientist.com/
├── index.html                          # Home/welcome page
├── PROJECT_CONTEXT.md                  # This file
├── CNAME
├── config.json
├── soccer.sqlite                       # Sample database for SQL tutorials
│
├── static/
│   ├── css/
│   │   ├── navbar.css                  # Global navbar styles
│   │   ├── footer.css                  # Global footer styles
│   │   ├── theme.css                   # Index/about page base styles
│   │   ├── landing.css                 # Landing page: hero, carousel, scrollable cards
│   │   ├── general_landing.css         # Category landing page styles
│   │   ├── post-table.css              # Post listing table styles
│   │   ├── jn_styling.css              # Jupyter notebook HTML styles (classic template)
│   │   ├── code_block_styling.css      # SQL + diagram code block theming
│   │   ├── sidebar_toc.css             # Sticky sidebar table of contents
│   │   ├── table_style.css             # General HTML table styles
│   │   ├── gist.css                    # GitHub gist embed styles
│   │   ├── monokai.css                 # Monokai code syntax theme
│   │   ├── contact.css                 # Contact page styles
│   │   ├── flowchart.css               # Responsive HTML decision trees (fc- class prefix)
│   │   ├── code_blocks.css             # Legacy code block styles
│   │   ├── video_and_description.css   # Video embed styles
│   │   └── video_blog_posts.css        # Video blog layout styles
│   │
│   ├── js/
│   │   ├── include.js                  # w3-include-html mechanism (loads partials via XHR)
│   │   ├── latest_posts.js             # Reads posts.json → renders latest 10 as scrollable cards
│   │   ├── carousel_init.js            # Dynamic carousel: clones slides, measures widths, injects @keyframes
│   │   ├── video_lightbox.js           # Video playback lightbox for carousel video slides
│   │   ├── sidebar_toc.js              # Auto-generates sticky TOC from notebook headings
│   │   ├── diagram_detect.js           # Detects ASCII diagrams and applies .diagram-block class
│   │   ├── navbase.js                  # Navbar interactions
│   │   ├── nav_multi.js                # Multi-level dropdown nav
│   │   ├── table.js                    # Table interactions
│   │   └── update_mathjax.js           # MathJax rendering for notebooks
│   │
│   ├── data/
│   │   └── posts.json                  # Post registry — landing page auto-populates from this
│   │
│   └── images/
│       ├── headshot.jpg                # Processed headshot (warm filter, 500x500)
│       ├── reel/                       # Original full-res photos and videos (NOT committed to git)
│       └── reel_thumbs/               # Web-optimized 600x400 thumbnails (committed to git)
│
├── folders/
│   ├── navbar_footer/
│   │   ├── navbar_index.html           # Navbar for index page (no "Home" link)
│   │   ├── navbar_pages.html           # Navbar for all content pages
│   │   └── footer.html                 # Shared footer
│   │
│   ├── sql/                            # SQL section (5 consolidated guides)
│   │   ├── sql_landing.html            # SQL landing page (5 guide cards)
│   │   ├── sql_foundations.html        # ★ Standalone HTML — 6 tabs: SELECT, Filtering, Sorting, Functions, GROUP BY, Dialects
│   │   ├── sql_subqueries_ctes.html    # ★ Standalone HTML — 6 tabs: Why Subqueries, WHERE/SELECT/FROM, Combining, CTEs + CTE vs Subquery comparison
│   │   ├── sql_strategy_guide.html     # ★ Standalone HTML — 5 tabs: Master Decision Tree, Single/Multi/Combined Patterns, Window Functions
│   │   ├── sql_problem_patterns.html   # ★ Standalone HTML — 6 tabs: 50 problems (Filtering, Joins, Aggregation, Window, Subqueries, Transforms)
│   │   ├── sql_debugging_guide.html    # ★ Standalone HTML — 14 tabs: Diagnose, Reading, 9 error categories, Execution Order, Code Review, Interview Traps
│   │   ├── sql_table.html              # SQL post listing table (legacy)
│   │   ├── sql_posts.html              # SQL posts overview (legacy)
│   │   ├── sql_master_decision_tree.html              # Wrapper page (legacy — content consolidated into sql_strategy_guide.html)
│   │   ├── sql_single_table_query_strategies.html     # Wrapper page (legacy)
│   │   ├── sql_multi_table_query_strategies.html      # Wrapper page (legacy)
│   │   ├── sql_combined_strategy_patterns.html        # Wrapper page (legacy)
│   │   ├── (10+ additional legacy SQL concept pages — sql_select, sql_filter, sql_sort, etc.)
│   │   └── projects/                   # Jupyter notebooks + converted HTML
│   │       ├── sql_master_decision_tree.ipynb / .html
│   │       ├── sql_single_table_query_strategies.ipynb / .html
│   │       ├── sql_multi_table_query_strategies.ipynb / .html
│   │       ├── sql_combined_strategy_patterns.ipynb / .html
│   │       ├── sql_subqueries_select.ipynb / .html
│   │       └── (other SQL project files)
│   │
│   ├── ds_blogs/                       # Data Science projects (59+ posts)
│   ├── python/                         # Python tutorials (50+ posts)
│   ├── desciptive_stats/               # Descriptive statistics (25 posts) [note: folder name typo is intentional — do not rename]
│   ├── inferetial_stats/               # Inferential statistics (45+ posts) [note: folder name typo is intentional — do not rename]
│   ├── databases/                      # Database design & management
│   ├── javascript/                     # JavaScript tutorials
│   ├── web_dev/                        # HTML/CSS tutorials
│   ├── microsoft/                      # Office technology
│   ├── jupyternb/                      # Jupyter Notebook tutorials
│   ├── GIT/                            # Git tutorials
│   ├── command_line/                   # CLI tutorials
│   ├── r_prog/                         # R programming
│   ├── contact/                        # Contact page
│   ├── about.html                      # About page
│   ├── archive/                        # Archived content
│   ├── template.html                   # Base template for new pages
│   └── posts-tableofcontent-template.html  # Template for post table pages
```

---

## 3. Technology Stack

| Component | Technology | Version |
|---|---|---|
| CSS Framework | Bootstrap | 3.4.0 (index), 4.3.1 (content pages) |
| jQuery | jQuery | 3.4.1 |
| Visualization | D3.js | v5 |
| HTML Includes | Custom w3-include-html | via `include.js` |
| Notebooks | Jupyter + nbconvert | `--template classic` flag required |
| Hosting | GitHub Pages | Static |

---

## 4. Key Conventions & Patterns

### Creating New Blog Posts (Jupyter Notebook Workflow)

1. **Create the notebook** (`.ipynb`) in the appropriate `projects/` subfolder
2. **Convert to HTML:**
   ```bash
   python3 -m jupyter nbconvert --to html --template classic <notebook>.ipynb
   ```
   The `--template classic` flag is critical — it produces old-style class names (`text_cell`, `code_cell`, `border-box-sizing`) that `jn_styling.css` expects. Without it, styling breaks.

3. **Create a wrapper HTML page** in the parent folder (e.g., `folders/sql/`) using this structure:
   ```html
   <head>
     <!-- Bootstrap 4.3.1, jQuery 3.4.1, Popper.js -->
     <link rel="stylesheet" href='../../static/css/navbar.css'>
     <link rel="stylesheet" href='../../static/css/footer.css'>
     <link rel="stylesheet" href='../../static/css/theme.css'>
     <link rel="stylesheet" href='../../static/css/general_landing.css'>
     <link rel="stylesheet" href='../../static/css/post-table.css'>
     <link rel="stylesheet" href='../../static/css/jn_styling.css'>
     <link rel="stylesheet" href='../../static/css/code_block_styling.css'>
     <link rel="stylesheet" href='../../static/css/sidebar_toc.css'>
   </head>
   <body>
     <div id="page-container">
       <div id="content-wrap">
         <div w3-include-html="/folders/navbar_footer/navbar_pages.html"></div>
         <div class="title"><h1>Page Title.</h1></div>
         <div class="date_updated">...</div>
         <div class="page-with-sidebar">
           <nav id="sidebar-toc" class="sidebar-toc"></nav>
           <div class="sidebar-main-content">
             <div class="row">
               <div class="col-sm-12">
                 <div class="sub-section">
                   <div id="results">
                     <center><a href="projects/<notebook>.ipynb" download>Download</a></center>
                     <div id="jnotebook" w3-include-html="projects/<notebook>.html">
                       <script src="../../static/js/update_mathjax.js"></script>
                     </div>
                   </div>
                 </div>
               </div>
             </div>
           </div>
         </div>
       </div>
       <div w3-include-html="/folders/navbar_footer/footer.html"></div>
     </div>
     <script src="https://d3js.org/d3.v5.min.js"></script>
     <script src="../../static/js/include.js"></script>
     <script src="../../static/js/sidebar_toc.js"></script>
     <script src="../../static/js/diagram_detect.js"></script>
   </body>
   ```

4. **Add entry to the section's table page** (e.g., `sql_table.html` or `playbooks_table.html`)
5. **Add entry to `static/data/posts.json`** (see below) — the landing page reads this automatically

### Adding a Post to the Landing Page (posts.json)

The landing page (`index.html`) auto-populates from `static/data/posts.json`. The JS (`latest_posts.js`) reads this file, sorts by date descending, and renders the latest 10 as horizontally scrollable cards. **No HTML editing of index.html is needed.**

**To add a new post, append an entry to `posts.json`:**

```json
{
  "date": "2026-04-15",
  "category": "Soft Skills",
  "categoryClass": "playbooks",
  "title": "How to Run a Metrics Review Meeting",
  "url": "folders/playbooks/metrics_review_playbook.html",
  "desc": "A framework for running effective metrics reviews that drive action, not just updates."
}
```

**Field reference:**

| Field | Required | Description |
|---|---|---|
| `date` | Yes | ISO format `YYYY-MM-DD`. Used for sorting — newest first. |
| `category` | Yes | Display name shown on the card (e.g., "Soft Skills", "SQL", "Data Science"). Note: was "Professional Playbooks" until March 29 rename. |
| `categoryClass` | Yes | CSS class for color coding. One of: `playbooks` (navy), `sql` (red-brown), `ds` (green), `stats` (purple) |
| `title` | Yes | Post title as shown on the card |
| `url` | Yes | Relative path from site root to the wrapper HTML page |
| `desc` | Yes | 1-2 sentence description shown below the title on the card |

**Category class colors:**
- `playbooks` → navy (#0f3460)
- `sql` → red-brown (#b33000)
- `ds` → green (#2e7d32)
- `stats` → purple (#6a1b9a)

To add a new category color, add a CSS rule in `static/css/landing.css`:
```css
.card-category.newclass { color: #hexcolor; }
```

**Important:** The landing page always shows the latest 10 posts by date. Older posts are not deleted — they remain in the JSON for completeness and are available on their respective landing pages. As new posts are added, older ones naturally scroll off the landing page.

### Creating Standalone HTML Pages (Tabbed Guide Pattern — NEW in Session 8)

For content-heavy reference guides that don't originate from notebooks, use the standalone HTML pattern. This is now the preferred approach for new SQL, reference, and debugging guides.

```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>Page Title</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/css/bootstrap.min.css">
  <script src="https://ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js"></script>
  <script src="https://maxcdn.bootstrapcdn.com/bootstrap/3.4.0/js/bootstrap.min.js"></script>
  <link rel="stylesheet" type="text/css" href="../../static/css/navbar.css">
  <link rel="stylesheet" type="text/css" href="../../static/css/footer.css">
  <link rel="stylesheet" type="text/css" href="../../static/css/theme.css">
  <link rel="stylesheet" type="text/css" href="../../static/css/flowchart.css"> <!-- if using flowcharts -->
  <style>
    /* All page-specific CSS embedded here — no external page CSS file */
    .blog-container { max-width: 960px; margin: 0 auto; ... }
    .tab-navigation { display: flex; border-bottom: 2px solid #e0e0e0; ... }
    .tab-nav-item { ... }
    .tab-nav-item.active { color: #b33000; border-bottom: 3px solid #b33000; ... }
    .tab-pane { display: none; }
    .tab-pane.active { display: block; }
    .problem-card { ... }  /* collapsible cards */
    .code-block { background-color: #1a1a2e; color: #e8e8e8; ... }
    /* etc. — see sql_problem_patterns.html for the full CSS reference */
  </style>
</head>
<body>
  <div id="page-container">
    <div id="content-wrap">
      <div w3-include-html="/folders/navbar_footer/navbar_pages.html"></div>
      <div class="blog-container">
        <div class="blog-header">...</div>
        <div class="tab-navigation" id="tab-nav">
          <button class="tab-nav-item active" data-tab="tab-first">First Tab</button>
          <button class="tab-nav-item" data-tab="tab-second">Second Tab</button>
        </div>
        <div id="tab-first" class="tab-pane active">...</div>
        <div id="tab-second" class="tab-pane">...</div>
      </div>
    </div>
    <div w3-include-html="/folders/navbar_footer/footer.html"></div>
  </div>
  <script src="https://www.w3schools.com/lib/w3.js"></script>
  <script>
    // Tab switching + problem card toggling + w3.includeHTML()
  </script>
</body>
</html>
```

**Key components in standalone pages:**
- `.blog-container` — max-width 960px centered content area
- `.blog-header` — centered title, subtitle, meta (e.g., "9 error categories · 14 sections · PostgreSQL")
- `.tab-navigation` / `.tab-nav-item` — horizontal scrollable tab bar, sticky on scroll
- `.tab-pane` — content panels toggled by JS
- `.problem-card` — collapsible cards with header, optional excerpt, and hidden content
- `.section-heading` — left-bordered section titles within tabs
- `.code-block` — dark-themed SQL code with syntax highlighting spans (.keyword, .string, .function, .comment, .number)
- `.info-box`, `.business-example`, `.performance-note`, `.guide-link` — colored callout boxes

### Notebook Cell Conventions

- **Section dividers:** `<hr style="border: 3px solid black;">` for major sections, `2px` for subsections, `---` for thin within-subsection dividers
- **Anchor IDs:** Kebab-case matching TOC links, e.g., `<a id='3-pattern-library-with-examples'></a>`
- **ASCII diagrams:** Use box-drawing characters (┌┐└┘├┤┬┴┼─│▼▶) — automatically detected by `diagram_detect.js` and styled with navy gradient theme. **Deprecated for decision trees** — use HTML flowcharts instead (see below).
- **HTML flowcharts (`flowchart.css`):** Preferred for all decision trees. Uses `fc-` prefixed classes. Two patterns:
  - **Standard tree** (`fc-branches` + `fc-branch`): Side-by-side YES/NO branches. Use for shallow trees (1-2 levels max).
  - **Vertical checklist** (`fc-else`): Purely vertical flow — question → YES answer → "if no ▼" → next question. Use for sequential elimination chains (3+ decisions deep). Example: Step 2A in master decision tree.
  - **Hybrid**: Vertical checklist that ends with a shallow branch (e.g., subquery decision tree ending in 3-column placement guide).
  - Wrapper pages must include `<link rel="stylesheet" href="../../static/css/flowchart.css">` in `<head>`.
  - **Inline SQL syntax:** Use `<code>` inside `fc-node` divs for syntax examples. Renders as block-display monospace with color matching the node type (green/warn/action/start). Example: `<div class="fc-node fc-good">Use LAG/LEAD<code>LAG(col) OVER(ORDER BY date)</code></div>`
- **Notebook source arrays:** Each line must end with `\n` except the last line. Forgetting this causes all lines to concatenate into one string.

### Code Block Styling (3 visual treatments)

| Block Type | Detection | Background |
|---|---|---|
| SQL code | `.text_cell_render .highlight` | Dark `#1e1e2e`, purple keywords, blue functions |
| ASCII diagrams | `.diagram-block` (added by JS) | Navy gradient `#0f172a → #1e293b` |
| Plain `<pre>` | Default pre blocks | Light grey `#f8f9fa` |

### Sidebar TOC

- Auto-generated from h2/h3 headings in `#jnotebook` by `sidebar_toc.js`
- Sticky positioning, 280px wide, hidden below 992px viewport
- Polls for content load (300ms intervals, 15s max) since notebooks load asynchronously via `w3-include-html`

---

## 5. Content Inventory

### SQL (Active — April 2026, 5 consolidated guides)

**All 5 SQL guides are standalone HTML pages** (not Jupyter notebook wrappers). They use Bootstrap 3.4.0, embedded CSS, and a tabbed interface with custom JS tab switching. Each uses the `page-container > content-wrap > blog-container` nesting, `w3-include-html` for navbar/footer, and `include.js`.

| # | Guide | File | Tabs | Description |
|---|---|---|---|---|
| 1 | SQL Foundations: A Complete Reference | `sql_foundations.html` | 6 | SELECT & FROM, Filtering, Sorting & Calculated Fields, Functions, GROUP BY & Aggregation, SQL Dialects. Consolidates 10 former basics posts. |
| 2 | SQL Subqueries & CTEs | `sql_subqueries_ctes.html` | 6 | Why Subqueries Exist (execution order), WHERE/SELECT/FROM Subqueries, Combining Subqueries, CTEs. Includes comprehensive CTE vs Subquery comparison table. Consolidates 4 former subquery posts. |
| 3 | SQL Strategy & Decision Trees | `sql_strategy_guide.html` | 5 | Master Decision Tree, Single-Table Patterns, Multi-Table Patterns, Combined Patterns, Window Functions. Preserves all HTML flowcharts. Consolidates 4 former strategy posts. |
| 4 | SQL Problem Patterns: A Practice Guide | `sql_problem_patterns.html` | 6 | 50 problems across Filtering, Joins, Aggregation, Window Functions, Subqueries, Transforms. Collapsible cards with visible excerpts, ranked solutions with performance analysis. |
| 5 | SQL Debugging & Code Review — PostgreSQL | `sql_debugging_guide.html` | 14 | Diagnose Your Error, Reading Errors, Syntax/Reference/Type/Aggregation/NULL/JOIN/Window Function/Subquery/Arithmetic Errors, Execution Order Errors, Code Review Checklist, Common Interview Traps (9 collapsible examples). |

**Legacy SQL pages still exist** (sql_select.html, sql_filter.html, sql_sort.html, sql_groupby.html, etc.) but are no longer linked from sql_landing.html. The landing page now shows only the 5 consolidated guides.

### Reference Library (Active — April 2026)

**Both debugging guides are standalone HTML pages** (same tabbed framework as the SQL guides). They use Bootstrap 3.4.0, embedded CSS, and collapsible problem-cards.

| # | Guide | File | Tabs | Accent Color | Description |
|---|---|---|---|---|---|
| 1 | Python & Pandas Debugging — Data Wrangling | `python_pandas_debugging_guide.html` | 13 | Blue (#1565c0) | Diagnose Your Error, Reading Tracebacks, 8 error categories (Type, Key/Index, Value, Copy Warning, Merge, Shape, Silent Data, Import), Code Review Checklist, Debugging Workflow, Common Interview Traps with collapsible examples. |
| 2 | dbt Cloud Debugging & Code Review | `dbt_debugging_guide.html` | 12 | Green (#2e7d32) | Diagnose Your Error, Reading Errors, 7 error categories (YAML, Compilation, SQL Runtime, Test, DAG, Incremental, Environment), Code Review Checklist, Debugging Workflow, Common Interview Traps with collapsible examples. |

### Data Science (Selected Highlights)
| Post | Topic |
|---|---|
| Predicting Lead Conversion | Classification modeling |
| Mapping OB-GYN Care Coordination | Network analysis |
| AB Testing Blog | Experiment design |
| Customer Segmentation | Clustering |
| Portfolio Analysis | Financial modeling |

### Statistics
- **Descriptive:** Central tendency, dispersion, distributions, normality diagnostics, data transformations in R
- **Inferential:** Hypothesis testing, t-tests, ANOVA, chi-square, confidence intervals, regression, model tuning in R

### Soft Skills (New — March 2026)
| Post | File | Description |
|---|---|---|
| How to Build a Dashboard — From Request to Delivery | `dashboard_playbook` | Full lifecycle: scoping, metrics, design, build, QA, presenting, iteration, handoff. Decision trees, pattern library, anti-patterns, worked example, communication templates, checklists, timeline estimation. |
| How to Manage an Analytics Intake Queue | `intake_queue_playbook` | Triage matrix (P0–P4), intake process levels, intake form, workload visibility, saying no scripts, managing up, response templates, worked example week. |
| How to Scope and Deliver an Ad-Hoc Analysis | `adhoc_analysis_playbook` | Request decoder, 5-minute scoping framework, SCR analysis structure, deliverable format picker, QA trust checklist, communication templates, worked churn example. |
| How to Handle Competing Priorities from Multiple Stakeholders | `competing_priorities_playbook` | Priority Conflict Matrix, Decision Tree, 5 Types of Conflicts, Stakeholder Map, Scripts, Trade-Off Framework, When to Escalate, Cross-Functional Conflicts, Anti-Patterns, Worked Example, Checklists, Final Takeaway. |

### Soft Skills — Topic Backlog

**Delivery & Execution:**
- [x] How to Scope and Deliver an Ad-Hoc Analysis
- [ ] How to Build and Maintain a Recurring Report
- [ ] How to Run a Self-Service Data QA Pass
- [ ] How to Design and Run an A/B Test (The Operational Side)

**Communication & Influence:**
- [ ] How to Write an Executive Summary That Gets Read
- [ ] How to Structure a Data-Informed Recommendation
- [ ] How to Run a Metrics Review Meeting
- [x] How to Say "The Data Doesn't Support That" Diplomatically

**Stakeholder & Project Management:**
- [x] How to Manage an Analytics Intake Queue
- [x] How to Handle Competing Priorities from Multiple Stakeholders
- [ ] How to Estimate and Communicate Timelines for Analytical Work
- [ ] How to Scope a Project When the Requester Doesn't Know What They Want

**Data Stewardship & Infrastructure:**
- [ ] How to Document a Data Source for the Next Person
- [ ] How to Build and Maintain a Team Metrics Dictionary
- [ ] How to Set Up a Sustainable Folder and Naming Convention
- [ ] How to Evaluate and Recommend a New Tool for the Team

**Career & Growth:**
- [ ] How to Build a Portfolio That Demonstrates Analytical Thinking
- [ ] How to Structure Your First 90 Days in a New Analytics Role
- [ ] How to Mentor Junior Analysts Effectively

### Programming
- **Python:** Data types, pandas, matplotlib, APIs, OOP, file operations, web scraping, geospatial
- **SQL:** SELECT through advanced subqueries, date functions, dialects
- **JavaScript:** Basic tutorials
- **R:** Statistical computing (integrated into stats sections)

---

## 6. Recent Session Activity Log

### Session: April 3, 2026 (Session 8 — SQL Consolidation, Tabbed Pages, Debugging Guide Rebuild)

**Major Restructure: 20 SQL Posts → 5 Consolidated Tabbed Guides**

Identified significant content overlap across 20 individual SQL posts and consolidated them into 5 comprehensive standalone HTML pages using a tabbed interface. This eliminated redundancy while preserving all content.

**Consolidation Map:**
| New Guide | Former Posts Absorbed | Tabs |
|---|---|---|
| `sql_foundations.html` | sql_select, sql_filter, sql_adv_filter, sql_wildcard_filter, sql_sort, sql_calculated_fields, sql_data_functions, sql_date_compotent_intro, sql_groupby, sql_intro_dialects | 6 |
| `sql_subqueries_ctes.html` | sql_subqueries_where, sql_subqueries_select, sql_subqueries_from, sql_multi_subqueries | 6 |
| `sql_strategy_guide.html` | sql_master_decision_tree, sql_single_table_query_strategies, sql_multi_table_query_strategies, sql_combined_strategy_patterns | 5 |
| `sql_problem_patterns.html` | (already existed — enhanced) | 6 |
| `sql_debugging_guide.html` | (rebuilt from notebook to standalone HTML) | 14 |

**New Standalone HTML Page Pattern (replaces Jupyter wrapper pattern for new content):**
All 5 SQL guides use a shared architecture:
- Bootstrap 3.4.0 with embedded `<style>` block (no external page-specific CSS)
- Tab navigation with `data-tab` attributes and custom JS switching
- Collapsible `.problem-card` components with `.problem-card-header`, `.problem-card-content`, `.problem-card-excerpt`
- `page-container > content-wrap > blog-container` nesting
- `w3-include-html` for navbar/footer + `include.js`
- `flowchart.css` linked where HTML flowcharts are used (strategy guide, debugging guide)
- Font sizes scaled to ~1.5625x original via rem units (after multiple adjustment rounds: 2.5x → 50% reduction → 25% increase)

**sql_problem_patterns.html Enhancements:**
- Added visible problem excerpts to all 50 collapsible cards (`.problem-card-excerpt` class)
- Left-aligned collapsible solution titles (changed `justify-content` from `space-between` to `flex-start` with `gap: 10px`)
- Added `white-space: pre-wrap` to `.code-block` and `.code-block code`
- Removed "LeetCode" branding from subtitle and intro paragraph
- Multiple font size scaling rounds (net ~1.5625x original)

**sql_debugging_guide.html Complete Rebuild:**
- Converted from Jupyter notebook wrapper to standalone HTML
- Expanded from 8 tabs to 14 tabs:
  1. Diagnose Your Error (renamed from "Error Tree", moved to first position)
  2. Reading Errors
  3. Syntax Errors (split from "Syntax & Reference")
  4. Reference Errors (split from "Syntax & Reference")
  5. Type Errors (split from "Types & Aggregation")
  6. Aggregation Errors (split from "Types & Aggregation")
  7. NULL Errors (split from "Silent Errors")
  8. JOIN Errors (split from "Silent Errors")
  9. Window Function Errors (split from "Advanced")
  10. Subquery Errors (split from "Advanced")
  11. Arithmetic Errors (split from "Advanced")
  12. Execution Order Errors (renamed, includes DENSE_RANK example, subquery placement rationale, CTE vs subquery comparison, multi-step CTE example)
  13. Code Review Checklist (split from "Code Review")
  14. Common Interview Traps (NEW — 9 collapsible cards with buggy query, explanation, fix, and interview response for each trap)
- Old version backed up as `sql_debugging_guide_old.html`

**sql_subqueries_ctes.html — CTE vs Subquery Comparison Added:**
- Comprehensive comparison table added to CTEs tab with 5 sections:
  - Definitions with syntax examples and plain-language analogies
  - Head-to-head on 7 dimensions (readability, reusability, performance, debugging, recursion, scope, maintainability)
  - 9 use cases with best-choice recommendations
  - "When NOT to use each" anti-patterns
  - Real-world example: same problem solved both ways with explanation

**sql_landing.html Updated:**
- Reduced from 20 post cards to 5 guide cards
- Changed meta from "20 posts" to "5 guides"
- Debugging guide card now lists all 9 error categories

**dbt & Python/Pandas Debugging Guides — Converted to Standalone Tabbed HTML:**

Both reference debugging guides were converted from Jupyter notebook wrappers to standalone HTML pages matching the SQL debugging guide framework:

| Guide | Tabs | Accent | Cards | File |
|---|---|---|---|---|
| dbt Cloud Debugging & Code Review | 12 | Green (#2e7d32) | 33 | `folders/reference/dbt_debugging_guide.html` |
| Python & Pandas Debugging — Data Wrangling | 13 | Blue (#1565c0) | 43 | `folders/reference/python_pandas_debugging_guide.html` |

Key changes:
- Each error pattern (A1, B1, etc.) converted to collapsible problem-cards with excerpt, error message, explanation, fix, and verification
- Interview traps converted from tables to individual collapsible cards with full examples
- Error classification decision trees use HTML flowchart system (fc- classes)
- All three debugging guides now share the same visual framework with different accent colors (SQL=red, Python=blue, dbt=green)
- Cross-linked Related Guides sections between all three guides
- Updated `reference_landing.html` descriptions to reflect new tabbed format

**Bug Fixes:**
- Fixed floating footer on `sql_subqueries_ctes.html` (Related Guides div was outside blog-container nesting)
- Fixed missing navbar/footer on all 3 new pages (sql_foundations, sql_subqueries_ctes, sql_strategy_guide)
- Fixed extra `</div>` in `sql_foundations.html` causing footer to render outside page-container
- Fixed div imbalance in `sql_debugging_guide.html` after rebuild
- Removed extra closing div in `sql_subqueries_ctes.html` (line 1450 orphan tag)

---

### Session: April 2, 2026 (Session 7 — Debugging Guides, Rolling Calculations, Row-Level Filtering)

**Three New Debugging Guides (SQL, Python/Pandas, dbt Cloud):**
Created a cohesive debugging guide series for 60-minute technical interviews, all following a shared "Read → Classify → Fix → Verify" framework:

| Guide | Notebook | Wrapper | Location | Cells | Error Patterns |
|---|---|---|---|---|---|
| SQL Debugging & Code Review — PostgreSQL | `sql_debugging_guide.ipynb` | `sql_debugging_guide.html` | `folders/sql/` | 16 | 9 (A-I) |
| Python & Pandas Debugging — Data Wrangling | `python_pandas_debugging_guide.ipynb` | `python_pandas_debugging_guide.html` | `folders/reference/` | 15 | 8 (A-H) |
| dbt Cloud Debugging & Code Review | `dbt_debugging_guide.ipynb` | `dbt_debugging_guide.html` | `folders/reference/` | 14 | 7 (A-G) |

Each guide contains: error anatomy section, error classification decision tree (HTML flowcharts), pattern library with examples, code review checklist, debugging workflow (HTML flowchart), and interview traps section.

**ASCII → HTML Flowchart Conversion (all three guides):**
All decision trees were initially built with ASCII box-drawing characters, then converted to the site's HTML flowchart system (`flowchart.css`). Cells converted:
- SQL debugging: cells 2, 5, 7, 9, 14
- Python/Pandas debugging: cells 2, 13
- dbt debugging: cells 2, 9, 12

Used both established patterns: vertical checklist (`fc-else`) for sequential elimination chains, and branching (`fc-branches`) for side-by-side category splits.

**Single-Table Guide Enhancements (`sql_single_table_query_strategies.ipynb`):**
- Added Pattern A: Row-Level Filtering (WHERE + ORDER BY) — new first pattern for simple row selection problems
- Re-lettered all existing patterns A→B through J→K (now 11 patterns total)
- Added first branch to decision tree (cell 2): "Just filtering rows?" → WHERE + ORDER BY
- Expanded Pattern F from "Running Totals" to "Running & Rolling Calculations" — ROWS BETWEEN, RANGE BETWEEN, pre-aggregation CTE pattern, 4 approaches ranked by efficiency
- Added worked example (cell 10): step-by-step rolling 7-day restaurant revenue calculation

**Site Updates:**
- `posts.json`: Added 3 new entries (SQL debugging, Python debugging, dbt debugging) — now 21 entries
- `sql_landing.html`: Added debugging guide card, post count 18 → 19
- `reference_landing.html`: Added "Debugging & Code Review" section with Python and dbt cards, post count 56 → 58
- `sql_table.html`: Added SQL debugging guide entry at top

**Pending nbconvert (user must run locally):**
```bash
python3 -m jupyter nbconvert --to html --template classic folders/sql/projects/sql_single_table_query_strategies.ipynb
python3 -m jupyter nbconvert --to html --template classic folders/sql/projects/sql_debugging_guide.ipynb
python3 -m jupyter nbconvert --to html --template classic folders/reference/projects/python_pandas_debugging_guide.ipynb
python3 -m jupyter nbconvert --to html --template classic folders/reference/projects/dbt_debugging_guide.ipynb
```

---

### Session: March 29, 2026 (Session 5 — Flowchart Redesign, Competing Priorities Playbook)

**Flowchart System Overhaul (`flowchart.css` + all 8 notebooks):**

The original ASCII box-drawing decision trees were replaced with HTML div-based flowcharts in Session 4, but deeply nested trees (like Step 2A in the master decision tree, 10+ levels) caused content to overflow and become unreadable — each nesting level of side-by-side `fc-branches` halved the available width.

**Fix — two-phase redesign:**
1. **Flattened HTML structure:** Deeply nested YES/NO chains were restructured from nested `fc-branches` inside `fc-branch` containers to a flat sequential layout. Each question sits at the top level of the `.fc` container.
2. **Vertical checklist pattern:** Replaced confusing side-by-side YES/NO (where NO was a floating label with no clear meaning) with a purely vertical flow: question (dark blue) → YES answer (green) → "if no ▼" (gray connector) → next question. The first YES you hit is your answer.

**CSS changes (`static/css/flowchart.css`):**
- Added `.fc-arrow.fc-else` class — styled "if no ▼" connector for sequential checklists
- Added `overflow-wrap: break-word` on `.fc-node` — prevents text from clipping
- Added `.fc-four` for 4-column branch layouts
- Added CSS safety rule: `.fc-branch .fc-branches .fc-branches` auto-stacks vertically — catches any remaining depth-3+ nesting
- Removed `.fc-pass` (intermediate attempt that was confusing)

**8 cells flattened to vertical checklist pattern:**
| Notebook | Cell | What | Was |
|---|---|---|---|
| sql_master_decision_tree | 2 | Step 2A Single-Table Path | 10 levels deep |
| sql_master_decision_tree | 3 | Step 2B Multi-Table Path | 5 levels |
| sql_master_decision_tree | 6 | Step 4 Subquery Decision | 3 levels |
| sql_single_table_query_strategies | 2 | Decision Tree 5-Second Version | 12 levels |
| sql_single_table_query_strategies | 17 | Method Selection Framework | 3 levels |
| sql_single_table_query_strategies | 21 | Subquery Decision Tree | 3 levels |
| competing_priorities_playbook | 2 | Conflict Decision Tree | 3 levels |
| competing_priorities_playbook | 7 | Escalation Decision Tree | 4 levels |

**20 additional flowchart cells unchanged** — already flat or shallow enough.

**Flowchart pattern inventory across all notebooks (39 cells, 8 notebooks):**
- VERTICAL CHECKLIST (no branches): 4 cells — purely vertical, clearest pattern
- HYBRID (checklist + shallow branch at end): 4 cells — vertical chain ending in 2-3 column branch
- SHALLOW TREE (1-2 levels, flat): ~20 cells — standard side-by-side, no nesting issues
- LINEAR (no branches): ~8 cells — single vertical flow
- FLAT multi-branch (all at same level): ~3 cells — multiple branch sets but no nesting

**New Playbook — Competing Priorities:**
- Created `folders/playbooks/projects/competing_priorities_playbook.ipynb` (13 cells)
- Created wrapper `folders/playbooks/competing_priorities_playbook.html`
- Updated `playbooks_landing.html` (now 5 guides) and `playbooks_table.html`
- Added to `posts.json` (now 15 entries)
- Content: Priority Conflict Matrix, Decision Tree, 5 Types of Conflicts, Stakeholder Map, Communication Scripts, Trade-Off Framework, When to Escalate, Cross-Functional Conflicts, Anti-Patterns, Worked Example, Checklists, Final Takeaway

**Conditional Aggregation & MAX vs SUM content added to SQL guides:**
- `sql_single_table_query_strategies.ipynb` cell 21: "When You DON'T Need a Subquery — The Conditional Aggregation Shortcut" (`AVG(CASE WHEN ... THEN 100.0 ELSE 0 END)`)
- `sql_multi_table_query_strategies.ipynb` cell 15: "The Aggregate Join Trap: MAX() vs SUM() on Joined Constants"
- `sql_combined_strategy_patterns.ipynb` cell 17: "Before You Reach for a Subquery — Check If Conditional Aggregation Works"

**flowchart.css added to all 10 wrapper pages** (5 playbook + 5 SQL)

**Credentials added to site identity:**
- `index.html` `<title>` tag updated to "Trinidad Cisneros, Ph.D., M.S."
- `folders/navbar_footer/footer.html` copyright line updated to "Trinidad Cisneros, Ph.D., M.S."

---

### Session: March 30, 2026 (Session 6 — SQL Syntax in Flowcharts)

**Added inline SQL syntax examples (`<code>` blocks) to every flowchart answer box across all 4 SQL guides.** Users can now see the actual SQL pattern/formula, not just the name.

**CSS addition (`static/css/flowchart.css`):**
- Added `.fc-node code` styling — block display, monospace font (`Consolas`/`Monaco`), subtle background, left-aligned, pre-wrap whitespace
- Color-coded per node type: `.fc-start code` (white on dark), `.fc-good code` (green), `.fc-warn code` (orange-red), `.fc-action code` (navy)

**Cells updated with `<code>` syntax:**
| Notebook | Cell(s) | What was added |
|---|---|---|
| sql_master_decision_tree | 2 | Step 2A: WHERE, LAG/LEAD, GROUP BY, HAVING, ROW_NUMBER, SUM OVER, CASE WHEN, pivot, NOT EXISTS, duplicate detection |
| sql_master_decision_tree | 3 | Step 2B: UNION ALL, Self JOIN, CROSS JOIN, LEFT JOIN+IS NULL, LEFT JOIN, INNER JOIN |
| sql_master_decision_tree | 4 | Step 2C: rate/ratio, count/sum, rank, filter groups — 4 transformation boxes |
| sql_master_decision_tree | 5 | Step 3 Date Fork: LAG/LEAD date math, EXTRACT/DATE_PART, DATEDIFF |
| sql_master_decision_tree | 6 | Step 4 Subquery: SELECT/WHERE/FROM placement + window function alternative |
| sql_single_table_query_strategies | 2 | Decision Tree: same patterns as master Step 2A |
| sql_single_table_query_strategies | 17 | Method Selection: window function, GROUP BY, GROUP BY+HAVING, Self JOIN, CTE+JOIN, correlated subquery |
| sql_single_table_query_strategies | 21 | Subquery Decision Tree: no-subquery, window function, SELECT/WHERE/FROM placement |
| sql_multi_table_query_strategies | 2 | JOIN Decision Tree: UNION ALL, Self JOIN, CROSS JOIN, ANTI JOIN, LEFT JOIN, INNER JOIN (also converted from unusual YES=Q/NO=A layout to vertical checklist) |
| sql_combined_strategy_patterns | 3 | Combo Tree: GROUP BY+CASE, GROUP BY+COUNT, window functions, HAVING + Pass 1 Expanded: Self/CROSS/ANTI/LEFT/INNER JOIN |

**Pattern:** Every green (`fc-good`) and action (`fc-action`) box now contains a `<code>` block with the actual SQL syntax template, so readers see both WHAT to use and HOW to write it.

---

### Session: March 29, 2026 (Session 4 — Carousel, Subqueries, Master Decision Tree, Renaming)

**Carousel Improvements:**
- Created `static/js/carousel_init.js` — JS-driven dynamic carousel replacing fixed CSS animation. Duplicates slides, measures actual widths, injects `@keyframes` dynamically. Handles window resize. Speed: ~60px/sec.
- Created `static/js/video_lightbox.js` — Event-delegated video playback lightbox for carousel video slides
- Added 6 new carousel slides (scotland, self, family_xmas, dubai video, ireland_2023 video, newzealand_ostridge video) — now 24 unique slides total
- Added "Beyond the Data" section header above carousel with subtitle: "A visual snapshot of life when I'm not analyzing data. Learn more about me."
- Generated new thumbnails: `scotland.jpg` (Pillow), `dubai_poster.jpg` and `newzealand_ostridge_poster.jpg` (ffmpeg)

**Hero & Landing Page Updates:**
- Hero bio updated to casual "sandbox" tone — no mention of technical interviews
- Hero counter hardcoded to "170+ guides & projects published" (was JS-driven from posts.json which only has ~14 entries)
- Removed dynamic counter logic from `latest_posts.js`
- Added `.section-subtitle` CSS class in `landing.css` with link styling

**"Playbooks" → "Soft Skills" Rename:**
- Updated navbar: `navbar_pages.html` and `navbar_index.html`
- Updated `posts.json`: all 4 playbook entries changed from "Professional Playbooks" to "Soft Skills"
- Updated `playbooks_landing.html`: title, hero heading, subtitle, meta, all card tags

**SQL Post Title Improvements (more descriptive):**
- "SQL Master Decision Tree" → "Which SQL Approach Do I Use? A Master Decision Tree"
- "SQL Combined Strategy Patterns" → "When a SQL Problem Needs Multiple Techniques at Once"
- "SQL Multi-Table Query Strategies" → "How to Query Across Multiple Tables: JOINs, Subqueries & Set Ops"
- "SQL Single-Table Query Strategies" → "How to Pick the Right SQL Pattern for a Single Table"
- Updated in: `posts.json`, `sql_landing.html`, `sql_landing_new.html`, `sql_table.html`, all 4 wrapper page `<title>` and `<h1>` tags

**New SQL Post — Master Decision Tree:**
- Created `sql_master_decision_tree.ipynb` (11 cells) — unified flowchart covering all 3 strategy guides
- Steps: 1 (table count) → 2A (single-table) → 2B (multi-table/JOIN) → 2C (transformation) → 3 (date fork) → 4 (subquery decision)
- Signal words quick reference table with hyperlinks to all guides
- Worked example walking contest percentage problem through the tree
- Anchor links for cross-step navigation (#single-table-path, #multi-table-path, etc.)
- Created wrapper page `sql_master_decision_tree.html` and generated inner HTML
- Added to `sql_landing.html` (post count 17 → 18) and `posts.json`

**Subquery Decision Trees Added to All 3 Strategy Guides:**
- `sql_single_table_query_strategies.ipynb` — "When Do I Need a Subquery?" section with aggregation level decision tree
- `sql_multi_table_query_strategies.ipynb` — "When Do I Need a Subquery Instead of (or With) a JOIN?" section
- `sql_combined_strategy_patterns.ipynb` — "Subquery Placement in Combo Problems" section (fits two-pass framework)
- All share the same worked example (contest percentage problem) for consistency
- Sections renumbered in all 3 notebooks
- All HTML regenerated

**Subquery SELECT Example 3 Added:**
- Added percentage-of-total pattern example to `sql_subqueries_select.ipynb` (contest registration problem)

**Footer Redesign:**
- `footer.html` rewritten: minimal single-line with auto-year JS, LinkedIn link, Contact link, middot separators
- `footer.css` rewritten: navy background (#1a1a2e), steel blue hover (#4a7fb5)

**Contact Page Redesign:**
- `contact.html` rewritten with navy gradient section-hero banner, white card form, steel blue accents
- Uses `section_landing.css` for hero styles, inline styles for contact-specific card

**Key Technical Details:**
- `carousel_init.js` fixes mobile black gap issue — measures actual slide widths instead of hardcoded 5040px
- Posts.json tracks ~14 featured posts (not all 170+) — hero counter is hardcoded separately
- ASCII box-drawing decision trees were replaced with HTML flowcharts (`flowchart.css`) in Session 5 — see Session 5 log for details

---

### Session: March 29, 2026 (Session 2 — Landing Page Redesign)

**Landing Page Redesign (`index.html`):**
- Added hero section with circular headshot (processed from `self.JPG` with warm dark filter), name linking to LinkedIn, "in" icon + LinkedIn/Contact/About links, and professional bio paragraph
- Built auto-scrolling photo/video carousel from `static/images/reel/` — 18 unique slides (travel photos + video poster frames with play icons), duplicated 6 for seamless CSS animation loop. Pauses on hover.
- Replaced static category card sections and All Posts table with dynamic "Latest Posts" section — horizontally scrollable card row auto-populated from `static/data/posts.json` via `latest_posts.js`
- Created `static/css/landing.css` (hero, headshot, carousel, scroll cards)
- Created `static/js/latest_posts.js` (fetches posts.json, sorts by date, renders top 10)
- Created `static/data/posts.json` (12 entries — single source of truth for all posts)

**Image Processing:**
- Created `static/images/headshot.jpg` — square crop, warm filter (brightness 0.88, contrast 1.2, warm overlay, light vignette), 500x500px, 44KB
- Created `static/images/reel_thumbs/` — 21 web-optimized thumbnails (600x400, ~40-80KB each) with EXIF orientation fix (`ImageOps.exif_transpose`) for correct rotation
- Video poster frames extracted via ffmpeg for .mov/.mp4 files (australia, ireland x2, israel, muay_thai)

**About Page Rewrite (`folders/about.html`):**
- Added matching hero section with headshot + LinkedIn link
- "About This Site" section: cleaner version of original motivation text
- "Beyond the Data" section: personal bio (Muay Thai, Jiu Jitsu, anime, grilling, family, Pashka aka Taco, traveling) with Pashka photo floating left
- Disclaimer moved to de-emphasized section at bottom

**Dollar Sign / MathJax Fix:**
- Removed all `$` currency symbols from all 3 playbook notebooks (regex: `\$(\d+...)` → `\1`)
- Regenerated HTML for all 3 notebooks

**Key Technical Decisions:**
- `static/images/reel/` (originals, ~203MB) should NOT be committed to git — add to `.gitignore`
- `static/images/reel_thumbs/` (optimized thumbnails, ~1.2MB) SHOULD be committed
- Landing page now reads from `posts.json` — no HTML editing needed for new posts

---

### Session: March 29, 2026 (Initial — Playbooks)

**Created:**
- Soft Skills section (`folders/playbooks/`)
  - `playbooks_landing.html` — section landing page with background info, TOC with future topic placeholders
  - `playbooks_table.html` — post listing table
  - `dashboard_playbook.html` — wrapper page with sidebar TOC
  - `projects/dashboard_playbook.ipynb` — 20-cell all-markdown notebook (11 sections)
  - `projects/dashboard_playbook.html` — converted HTML

**Navbar Restructure:**
- Renamed "Data Science Blogs" → "Analytics & Data Science" (same URL)
- Added "Soft Skills" as new top-level nav item (originally "Professional Playbooks", renamed to "Soft Skills" on March 29)
- Consolidated "Tools" + "Databases" → "Technical Skills" dropdown (Programming, SQL & Databases, Web Development, Other Tools)
- Updated both `navbar_pages.html` and `navbar_index.html`

**Dashboard Playbook Content (11 sections):**
1. Master Phase Reference Table (8 phases)
2. Decision Tree: What Kind of Dashboard Is This?
3. Phase Pattern Library (8 phases A–H with checklists, templates, pitfalls)
4. Dashboard Component Pattern Library (10 components)
5. Tool Selection Guide (decision tree + comparison table)
6. What to Avoid — Anti-Patterns (technical + political)
7. Worked Example: Revenue Dashboard for Sales Leadership
8. Communication Templates (5 templates)
9. Quick-Reference Checklists (8 phase checklists)
10. Estimating Timelines & Setting Expectations (scoring framework, baseline estimates, negotiation scripts)
11. Final Takeaway

**Intake Queue Playbook Content (12 sections):**
1. Triage Matrix (P0–P4 with 70/20/10 rule)
2. Decision Tree: What Should I Do With This Request?
3. Building Your Intake Process (3 levels)
4. The Intake Form (6 questions + Slack template)
5. Making Your Workload Visible (weekly snapshot, capacity signal)
6. How to Say No (5 types with scripts + escalation tree)
7. Managing Up (1:1 queue review, overload scripts)
8. Response Templates (6 templates)
9. Anti-Patterns (process + political)
10. Worked Example: A Week in the Life
11. Quick-Reference Checklists
12. Final Takeaway

**Ad-Hoc Analysis Playbook Content (11 sections):**
1. Ad-Hoc Lifecycle at a Glance
2. Request Decoder (translation table + decision tree)
3. 5-Minute Scoping Framework
4. Structuring the Analysis (SCR framework + rabbit hole test)
5. Choosing the Right Deliverable Format (decision tree)
6. QA Trust Checklist (8-step ladder)
7. Communication Templates (6 templates)
8. Anti-Patterns (analysis + communication)
9. Worked Example: "What's Going On With Churn?"
10. Quick-Reference Checklists
11. Final Takeaway

**Key Fix:**
- ASCII decision trees with branches inside boxes render poorly — branches must exit below closed boxes, fork with labeled YES/NO lines, and lead to standalone outcome boxes

---

### Session: March 28–29, 2026

**Created:**
- SQL Single-Table Query Strategies notebook (22 cells, 10 sections)
  - Added Section 6: Method Selection with ASCII decision flow, CTE explanation, efficiency rankings
  - Added alternative approaches and efficiency tables to patterns C, E, F, G, I
- SQL Multi-Table Query Strategies notebook (21 cells, 10 sections)
  - 9 join patterns (A–I) with Venn diagrams for each
  - Decision Tree (5-Second Version)
  - Row Count Diagnostics section with QA queries
- SQL Combined Strategy Patterns notebook (19 cells, 10 sections)
  - Two-Pass Decomposition Framework
  - 8 combo patterns including ANTI JOIN
  - NULL Trap reference, 3 worked examples

**UX Improvements:**
- Created `sidebar_toc.css` + `sidebar_toc.js` — sticky sidebar TOC auto-generated from notebook headings
- Created `code_block_styling.css` — dark theme for SQL, navy gradient for diagrams
- Created `diagram_detect.js` — auto-detects ASCII art and applies styling
- Updated `sql_table.html` with 3 new entries
- Updated `index.html` with latest posts and `post-table.css` link

**Key Fixes:**
- Notebook HTML not rendering: needed `--template classic` for nbconvert
- Missing `\n` in notebook source arrays: lines concatenated into one string
- Sidebar text truncation: widened to 280px, removed JS truncation
- Section renumbering after inserts

---

## 7. Known Quirks & Gotchas

1. **Folder name typos are permanent** — `desciptive_stats` and `inferetial_stats` are misspelled but used in URLs across the site. Do not rename.
2. **Bootstrap version mismatch** — `index.html` uses Bootstrap 3.4.0; content pages use Bootstrap 4.3.1. Be careful with class names.
3. **CSS link syntax** — Some `<link>` tags have a trailing `)` after the href (e.g., `href='../static/css/footer.css' )`). This is a quirk in the codebase; browsers ignore it but it looks odd.
4. **w3-include-html is async** — Any JS that depends on included content must poll/wait for it to load. See `sidebar_toc.js` for the pattern.
5. **nbconvert must use `--template classic`** — The default template produces JupyterLab-style classes that don't match `jn_styling.css`.
6. **Notebook source arrays need `\n`** — When building notebooks programmatically, every line in the source array needs `\n` appended except the last line.
7. **Dollar signs trigger MathJax** — `$` in markdown content gets interpreted as LaTeX by nbconvert. Never use `$` for currency — spell out "dollars" or just use the number (e.g., `2.1M` not `$2.1M`).
8. **EXIF orientation on photos** — Camera JPGs often have rotation in EXIF metadata. When processing with Pillow, always call `ImageOps.exif_transpose(img)` before cropping/resizing.
9. **`static/images/reel/` must be in `.gitignore`** — Original photos/videos total ~203MB. GitHub has a 100MB file limit and a soft 1GB repo limit. Only the optimized `reel_thumbs/` (1.2MB) and `headshot.jpg` (44KB) should be committed.
10. **Landing page is data-driven** — `index.html` no longer has hardcoded post entries. Latest Posts comes from `static/data/posts.json` via `latest_posts.js`. To update landing page content, edit `posts.json` only.
11. **Hero counter is hardcoded** — `posts.json` only tracks ~14 featured posts, not all 170+. The "170+ guides & projects published" counter is hardcoded directly in `index.html`. Update it manually as the site grows.
12. **Carousel is JS-driven** — `carousel_init.js` dynamically calculates animation distance from actual slide widths. Do NOT add fixed `@keyframes carousel-scroll` back to `landing.css` — the JS handles it. Adding/removing slides automatically adjusts the animation.
13. **SQL post titles should be descriptive** — Titles are question-style or "How to..." format for clarity. Old generic names (e.g., "SQL Combined Strategy Patterns") were replaced. Keep this convention for new SQL posts.
14. **Flowchart deep nesting is forbidden** — Never nest `fc-branches` more than 2 levels deep. For sequential YES/NO chains (3+ decisions), use the vertical checklist pattern: question → `fc-good` YES answer → `fc-arrow fc-else` "if no ▼" → next question. See Step 2A in master decision tree for the reference implementation.
15. **flowchart.css must be linked in wrapper pages** — Any wrapper page that includes a notebook with HTML flowcharts needs `<link rel="stylesheet" href="../../static/css/flowchart.css">` in its `<head>`. Currently linked in all 5 playbook + 5 SQL wrapper pages.
16. **Standalone HTML pages use Bootstrap 3.4.0** — The 5 consolidated SQL guides use Bootstrap 3.4.0 (not 4.3.1 like other content pages). This is because the tabbed interface and embedded CSS were built for 3.4.0. Be consistent when editing these pages.
17. **Div balance is critical in standalone HTML pages** — Unlike notebook wrappers (where the notebook HTML is included via XHR), standalone pages have all divs in one file. Off-by-one `</div>` errors cause the footer to float or the page-container to close early. Always verify div balance after editing: `opens = content.count('<div')` must equal `closes = content.count('</div>')`.
18. **Standalone HTML tab switching uses two patterns** — `sql_problem_patterns.html` and `sql_debugging_guide.html` use `data-tab` attributes with event listeners. `sql_foundations.html`, `sql_subqueries_ctes.html`, and `sql_strategy_guide.html` use `onclick="switchTab(event, 'tab-name')"`. Both patterns work — be consistent within each file.
19. **Legacy SQL pages still exist** — Old individual pages (sql_select.html, sql_filter.html, etc.) are no longer linked from sql_landing.html but still exist on disk and may be linked from other parts of the site. Do not delete without checking for inbound links.
20. **Font sizes in consolidated SQL pages use rem units** — After multiple scaling rounds (2.5x → 50% → 25%), the effective font sizes are ~1.5625x the original values. All sizes are in rem for consistency. Don't mix px and rem.

---

## 8. How to Use This File

**Starting a new LLM session:**
> "I'm working on my portfolio site bitterscientist.com. Here's the project context: [paste or reference PROJECT_CONTEXT.md]. I want to [describe task]."

**After completing work in a session:**
Update Section 6 (Activity Log) with what was done, what was created/modified, and any new quirks discovered.

**Periodically:**
Review Section 5 (Content Inventory) and add new posts or sections as the site grows.
