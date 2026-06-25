"""Engine for nb02_data_cleaning_modeling_drills.ipynb.

Each DRILL hands you messy RAW data. You write SQL to CLEAN it and BUILD the target
model (CREATE TABLE ... + transforms). You are graded by a CHECK query run against
YOUR tables and compared to the expected rows -- so you're graded on the model you
built, not on a single one-off query.

Self-contained DuckDB sandbox (in-process, no server): `pip install duckdb`.
Postgres-compatible SQL where it matters; DuckDB runs the cleaning/modeling drills.
"""
import duckdb

# ---------------------------------------------------------------- helpers
def _norm(v):
    if v is None:
        return None
    return str(v)


def _run_script(con, sql):
    """Execute a multi-statement SQL string in DuckDB."""
    for stmt in sql.split(';'):
        if stmt.strip():
            con.execute(stmt)


def _table_names(sql):
    import re
    return re.findall(r'CREATE TABLE\s+(\w+)', sql, re.I)


# ---------------------------------------------------------------- drills
DRILLS = {
    'clean_customers': {
        'title': 'Clean a messy customer export',
        'focus': 'data cleaning',
        'scenario': (
            "A CSV export landed in one wide table `raw_customers`. It's dirty: ids stored as text "
            "with leading zeros, names padded with spaces, emails in mixed case (one is blank), "
            "country written four different ways, and one customer appears twice."
        ),
        'raw_setup': """
            CREATE TABLE raw_customers (cust_id TEXT, full_name TEXT, email TEXT, signup TEXT, country TEXT);
            INSERT INTO raw_customers VALUES
              ('001','  Ada Lovelace ','ADA@EXAMPLE.COM','2024-01-05','us'),
              ('002','Alan Turing','alan@example.com','2024-02-10','United States'),
              ('002','Alan Turing','alan@example.com','2024-02-10','United States'),
              ('003','Grace Hopper','grace@example.com ','2024-03-15','USA'),
              ('004','Edsger Dijkstra','','2024-04-01','Netherlands');
        """,
        'raw_tables': ['raw_customers'],
        'task': (
            "Build a clean table called `customers` with columns "
            "`customer_id` (integer), `full_name` (trimmed), `email` (lowercased, NULL when blank), "
            "`signup_date` (a real DATE), and `country_code` (two letters: US or NL). One row per customer."
        ),
        'target': "customers(customer_id INT, full_name TEXT, email TEXT, signup_date DATE, country_code TEXT)",
        'principles': [
            "Trim whitespace from text (names, emails).",
            "Standardize case and values: lowercase emails; map 'us' / 'USA' / 'United States' to one code 'US'.",
            "Treat a blank string as NULL (NULLIF(col, '')).",
            "Cast text to its real type: cust_id -> INTEGER, signup -> DATE.",
            "Remove duplicate rows once everything else is standardized (DISTINCT).",
        ],
        'check_sql': "SELECT customer_id, full_name, email, signup_date, country_code FROM customers ORDER BY customer_id;",
        'expected': [
            [1, 'Ada Lovelace', 'ada@example.com', '2024-01-05', 'US'],
            [2, 'Alan Turing', 'alan@example.com', '2024-02-10', 'US'],
            [3, 'Grace Hopper', 'grace@example.com', '2024-03-15', 'US'],
            [4, 'Edsger Dijkstra', None, '2024-04-01', 'NL'],
        ],
        'reference': """
            CREATE TABLE customers AS
            SELECT DISTINCT
                CAST(cust_id AS INTEGER)                       AS customer_id,
                trim(full_name)                                AS full_name,
                NULLIF(lower(trim(email)), '')                 AS email,        -- blank -> NULL
                CAST(signup AS DATE)                           AS signup_date,
                CASE WHEN lower(trim(country)) IN ('us','usa','united states') THEN 'US'
                     WHEN lower(trim(country)) IN ('nl','netherlands')         THEN 'NL'
                     ELSE upper(trim(country)) END             AS country_code
            FROM raw_customers;
        """,
    },
    'model_orders': {
        'title': 'Normalize a fat orders table into entities',
        'focus': 'data modeling',
        'scenario': (
            "Everything sits in one denormalized `raw_orders` table: every order row repeats the "
            "customer's name and email and the product's name and price. You want a proper model so "
            "facts aren't duplicated and a price lives in exactly one place."
        ),
        'raw_setup': """
            CREATE TABLE raw_orders (order_id INT, customer_name TEXT, customer_email TEXT,
                                     product TEXT, unit_price DECIMAL(8,2), qty INT, order_date DATE);
            INSERT INTO raw_orders VALUES
              (1,'Ada','ada@x.com','Widget', 9.99,2,'2024-01-10'),
              (2,'Ada','ada@x.com','Gadget',19.99,1,'2024-01-12'),
              (3,'Bob','bob@x.com','Widget', 9.99,5,'2024-01-15'),
              (4,'Bob','bob@x.com','Gizmo',  4.99,3,'2024-01-20');
        """,
        'raw_tables': ['raw_orders'],
        'task': (
            "Split `raw_orders` into three tables: `customers`(customer_id, name, email), "
            "`products`(product_id, product_name, unit_price), and `orders`(order_id, customer_id, "
            "product_id, qty, order_date). Give customers and products their own surrogate keys, and "
            "have orders reference them by those keys instead of repeating names and prices."
        ),
        'target': ("customers(customer_id, name, email)  +  products(product_id, product_name, unit_price)  +  "
                   "orders(order_id, customer_id, product_id, qty, order_date)"),
        'principles': [
            "Pull each real-world thing into its own table: a customer, a product, an order.",
            "Give each entity a surrogate key (row_number() over the DISTINCT rows).",
            "Replace the repeated text (name, price) in the fact table with foreign keys.",
            "The fact table (orders) holds keys + measures (qty, date) -- no descriptions.",
            "A value like unit_price now lives in exactly one place (products).",
        ],
        'check_sql': (
            "SELECT c.name, SUM(p.unit_price * o.qty) AS revenue "
            "FROM orders o "
            "JOIN customers c ON c.customer_id = o.customer_id "
            "JOIN products  p ON p.product_id  = o.product_id "
            "GROUP BY c.name ORDER BY c.name;"
        ),
        'check_note': "Graded by behaviour: this query rebuilds revenue per customer from your model, so any consistent surrogate keys pass.",
        'expected': [['Ada', '39.97'], ['Bob', '64.92']],
        'reference': """
            CREATE TABLE customers AS
              SELECT row_number() OVER (ORDER BY customer_email) AS customer_id,
                     customer_name AS name, customer_email AS email
              FROM (SELECT DISTINCT customer_name, customer_email FROM raw_orders) d;

            CREATE TABLE products AS
              SELECT row_number() OVER (ORDER BY product) AS product_id,
                     product AS product_name, unit_price
              FROM (SELECT DISTINCT product, unit_price FROM raw_orders) d;

            CREATE TABLE orders AS
              SELECT r.order_id, c.customer_id, p.product_id, r.qty, r.order_date
              FROM raw_orders r
              JOIN customers c ON c.email        = r.customer_email
              JOIN products  p ON p.product_name = r.product;
        """,
    },
}


# ---------------------------------------------------------------- public API
def list_drills():
    return [(k, d['title'], d['focus']) for k, d in DRILLS.items()]


def _fresh(drill_id):
    d = DRILLS[drill_id]
    con = duckdb.connect()
    _run_script(con, d['raw_setup'])
    return con, d


def show(drill_id):
    """Display the scenario, the raw table(s), the task, the target model, and the principles."""
    d = DRILLS[drill_id]
    con, _ = _fresh(drill_id)
    try:
        from IPython.display import display, Markdown
        md = display; M = Markdown
    except Exception:
        md = print; M = lambda x: x
    md(M("## %s  \n*%s drill*\n\n%s" % (d['title'], d['focus'], d['scenario'])))
    for t in d['raw_tables']:
        md(M("**Raw input — `%s`**" % t))
        try:
            md(con.execute("SELECT * FROM %s" % t).df())
        except Exception:
            print(con.execute("SELECT * FROM %s" % t).fetchall())
    md(M("**Your task**\n\n%s\n\n**Target model**: `%s`" % (d['task'], d['target'])))
    md(M("**Principles this drills**\n\n" + "\n".join("- " + p for p in d['principles'])))
    if d.get('check_note'):
        md(M("_Check: %s_" % d['check_note']))
    con.close()


def grade(drill_id, your_sql):
    """Run YOUR_SQL to build the model, then the check query, and compare to expected."""
    d = DRILLS[drill_id]
    con, _ = _fresh(drill_id)
    try:
        _run_script(con, your_sql)
    except Exception as e:
        print("❌ Your SQL errored while building the model:\n   %s" % e)
        con.close(); return False
    try:
        got = con.execute(d['check_sql']).fetchall()
    except Exception as e:
        print("❌ The check query couldn't run against your tables (is the model built / named right?):\n   %s" % e)
        con.close(); return False
    con.close()
    got_n = [tuple(_norm(x) for x in r) for r in got]
    exp_n = [tuple(_norm(x) for x in r) for r in d['expected']]
    if got_n == exp_n:
        print("✅ Passed — your model reproduces the expected result.")
        return True
    print("❌ Not yet. Check query output vs expected:")
    print("   your check output :", got_n)
    print("   expected          :", exp_n)
    return False


def solution(drill_id):
    """Return the reference clean/model SQL (try the drill yourself first!)."""
    return DRILLS[drill_id]['reference'].strip()
