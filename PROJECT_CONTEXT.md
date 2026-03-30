# BitterScientist.com — Project Context & Handoff Guide

**Owner:** Trinidad Cisneros (trinidad.cisneros@gmail.com)
**Domain:** bitterscientist.com
**Last Updated:** 2026-03-29 (Session 4)

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
│   ├── sql/                            # SQL section (18 posts)
│   │   ├── sql_landing.html            # SQL landing page
│   │   ├── sql_table.html              # SQL post listing table
│   │   ├── sql_posts.html              # SQL posts overview
│   │   ├── sql_master_decision_tree.html              # Wrapper page
│   │   ├── sql_single_table_query_strategies.html     # Wrapper page
│   │   ├── sql_multi_table_query_strategies.html      # Wrapper page
│   │   ├── sql_combined_strategy_patterns.html        # Wrapper page
│   │   ├── (14+ additional SQL concept pages)
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

### Notebook Cell Conventions

- **Section dividers:** `<hr style="border: 3px solid black;">` for major sections, `2px` for subsections, `---` for thin within-subsection dividers
- **Anchor IDs:** Kebab-case matching TOC links, e.g., `<a id='3-pattern-library-with-examples'></a>`
- **ASCII diagrams:** Use box-drawing characters (┌┐└┘├┤┬┴┼─│▼▶) — automatically detected by `diagram_detect.js` and styled with navy gradient theme
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

### SQL (Active — March 2026, 18 posts)
| Post | File | Description |
|---|---|---|
| Which SQL Approach Do I Use? A Master Decision Tree | `sql_master_decision_tree` | Unified flowchart: Step 1 (table count) → 2A (single) → 2B (multi/JOIN) → 2C (transformation) → 3 (date fork) → 4 (subquery). Signal words table, worked example, hyperlinks to all guides. |
| How to Pick the Right SQL Pattern for a Single Table | `sql_single_table_query_strategies` | LAG/LEAD, GROUP BY, HAVING, CASE, window functions, 3-Method Mental Model, subquery decision tree |
| How to Query Across Multiple Tables: JOINs, Subqueries & Set Ops | `sql_multi_table_query_strategies` | INNER/LEFT/CROSS/Self JOIN, UNION, EXISTS, anti-join, Venn diagrams, row count diagnostics, subquery decision tree |
| When a SQL Problem Needs Multiple Techniques at Once | `sql_combined_strategy_patterns` | Two-Pass Decomposition Framework, 8 combo patterns, NULL Trap, worked examples, subquery placement in combo problems |
| SQL Basics: Using a Subquery in the SELECT Clause | `sql_subqueries_select` | Includes 3 examples: basic, filtering, percentage-of-total pattern |

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
- ASCII box-drawing decision trees use Unicode (┌─┬─┐│▼►) consistently across all SQL notebooks

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

---

## 8. How to Use This File

**Starting a new LLM session:**
> "I'm working on my portfolio site bitterscientist.com. Here's the project context: [paste or reference PROJECT_CONTEXT.md]. I want to [describe task]."

**After completing work in a session:**
Update Section 6 (Activity Log) with what was done, what was created/modified, and any new quirks discovered.

**Periodically:**
Review Section 5 (Content Inventory) and add new posts or sections as the site grows.
