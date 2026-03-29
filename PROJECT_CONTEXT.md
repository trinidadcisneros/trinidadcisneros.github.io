# BitterScientist.com — Project Context & Handoff Guide

**Owner:** Trinidad Cisneros (trinidad.cisneros@gmail.com)
**Domain:** bitterscientist.com
**Last Updated:** 2026-03-29

---

## What This File Is For

This file is a handoff document for use with any LLM tool (Claude Cowork, ChatGPT, Cursor, etc.) when starting a new session. Paste or reference this file at the start of a conversation so the assistant understands the site's structure, conventions, and recent work — without having to re-discover everything from scratch.

---

## 1. Site Overview

BitterScientist.com is a personal portfolio and educational blog focused on analytics, data science, statistics, programming, and database concepts. Content is presented as tutorial-style posts, most of which originate as Jupyter notebooks converted to HTML and embedded in wrapper pages with a shared navbar and footer.

**Hosting:** GitHub Pages (static site, no backend)
**Root File:** `index.html` (welcome page with latest posts table)
**Config:** `config.json` at root
**CNAME:** `bitterscientist.com`

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
│   └── js/
│       ├── include.js                  # w3-include-html mechanism (loads partials via XHR)
│       ├── sidebar_toc.js              # Auto-generates sticky TOC from notebook headings
│       ├── diagram_detect.js           # Detects ASCII diagrams and applies .diagram-block class
│       ├── navbase.js                  # Navbar interactions
│       ├── nav_multi.js                # Multi-level dropdown nav
│       ├── table.js                    # Table interactions
│       └── update_mathjax.js           # MathJax rendering for notebooks
│
├── folders/
│   ├── navbar_footer/
│   │   ├── navbar_index.html           # Navbar for index page (no "Home" link)
│   │   ├── navbar_pages.html           # Navbar for all content pages
│   │   └── footer.html                 # Shared footer
│   │
│   ├── sql/                            # SQL section
│   │   ├── sql_landing.html            # SQL landing page
│   │   ├── sql_table.html              # SQL post listing table
│   │   ├── sql_posts.html              # SQL posts overview
│   │   ├── sql_single_table_query_strategies.html   # Wrapper page
│   │   ├── sql_multi_table_query_strategies.html    # Wrapper page
│   │   ├── sql_combined_strategy_patterns.html      # Wrapper page
│   │   ├── (15+ additional SQL concept pages)
│   │   └── projects/                   # Jupyter notebooks + converted HTML
│   │       ├── sql_single_table_query_strategies.ipynb / .html
│   │       ├── sql_multi_table_query_strategies.ipynb / .html
│   │       ├── sql_combined_strategy_patterns.ipynb / .html
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

4. **Add entry to the section's table page** (e.g., `sql_table.html`)
5. **Add entry to `index.html`** latest posts table (keep to ~10 entries, drop oldest)

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

### SQL (Active — March 2026)
| Post | File | Description |
|---|---|---|
| SQL Single-Table Query Strategies | `sql_single_table_query_strategies` | LAG/LEAD, GROUP BY, HAVING, CASE, window functions, 3-Method Mental Model |
| SQL Multi-Table Query Strategies | `sql_multi_table_query_strategies` | INNER/LEFT/CROSS/Self JOIN, UNION, EXISTS, anti-join, Venn diagrams, row count diagnostics |
| SQL Combined Strategy Patterns | `sql_combined_strategy_patterns` | Two-Pass Decomposition Framework, 8 combo patterns, NULL Trap, worked examples |

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

### Programming
- **Python:** Data types, pandas, matplotlib, APIs, OOP, file operations, web scraping, geospatial
- **SQL:** SELECT through advanced subqueries, date functions, dialects
- **JavaScript:** Basic tutorials
- **R:** Statistical computing (integrated into stats sections)

---

## 6. Recent Session Activity Log

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

---

## 8. How to Use This File

**Starting a new LLM session:**
> "I'm working on my portfolio site bitterscientist.com. Here's the project context: [paste or reference PROJECT_CONTEXT.md]. I want to [describe task]."

**After completing work in a session:**
Update Section 6 (Activity Log) with what was done, what was created/modified, and any new quirks discovered.

**Periodically:**
Review Section 5 (Content Inventory) and add new posts or sections as the site grows.
