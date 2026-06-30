"""
Sandbox helpers — connect to the local Postgres / MySQL containers,
load schema and seed data per problem, run user SQL, capture results.
"""

import os
import re
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

import pandas as pd

try:
    import psycopg2
    from psycopg2 import sql as pg_sql
    PG_AVAILABLE = True
except ImportError:
    PG_AVAILABLE = False

try:
    import pymysql
    MYSQL_AVAILABLE = True
except ImportError:
    MYSQL_AVAILABLE = False


# ============================================================
# Connection settings (read from env, fallback to docker-compose defaults)
# ============================================================

def _pg_settings():
    return {
        "host": os.environ.get("POSTGRES_HOST", "localhost"),
        "port": int(os.environ.get("POSTGRES_PORT", 5432)),
        "user": os.environ.get("POSTGRES_USER", "practice"),
        "password": os.environ.get("POSTGRES_PASSWORD", "practice"),
        "dbname": os.environ.get("POSTGRES_DB", "practice"),
    }


def _mysql_settings():
    return {
        "host": os.environ.get("MYSQL_HOST", "localhost"),
        "port": int(os.environ.get("MYSQL_PORT", 3306)),
        "user": os.environ.get("MYSQL_USER", "practice"),
        "password": os.environ.get("MYSQL_PASSWORD", "practice"),
        "database": os.environ.get("MYSQL_DB", "practice"),
    }


# ============================================================
# Health checks
# ============================================================

def check_postgres() -> Tuple[bool, str]:
    """Returns (ok, message)."""
    if not PG_AVAILABLE:
        return False, "psycopg2 not installed (pip install psycopg2-binary)"
    try:
        conn = psycopg2.connect(**_pg_settings())
        conn.close()
        return True, "Postgres reachable"
    except Exception as e:
        return False, f"Postgres unreachable: {e}"


def check_mysql() -> Tuple[bool, str]:
    if not MYSQL_AVAILABLE:
        return False, "PyMySQL not installed (pip install PyMySQL)"
    try:
        conn = pymysql.connect(**_mysql_settings())
        conn.close()
        return True, "MySQL reachable"
    except Exception as e:
        return False, f"MySQL unreachable: {e}"


# ============================================================
# Sandbox reset (drop + recreate the public schema for Postgres,
# drop + recreate the database for MySQL)
# ============================================================

def reset_postgres():
    """Drop and recreate the `public` schema, removing all user tables / functions."""
    conn = psycopg2.connect(**_pg_settings())
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            cur.execute("DROP SCHEMA IF EXISTS public CASCADE;")
            cur.execute("CREATE SCHEMA public;")
            cur.execute("GRANT ALL ON SCHEMA public TO public;")
    finally:
        conn.close()


def reset_mysql():
    """Drop all tables in the practice database."""
    s = _mysql_settings()
    conn = pymysql.connect(**s)
    try:
        with conn.cursor() as cur:
            cur.execute("SET FOREIGN_KEY_CHECKS = 0;")
            cur.execute(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = %s",
                (s["database"],),
            )
            tables = [r[0] for r in cur.fetchall()]
            for t in tables:
                cur.execute(f"DROP TABLE IF EXISTS `{t}`;")
            cur.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
    finally:
        conn.close()


def reset(dialect: str):
    if dialect == "postgresql":
        reset_postgres()
    elif dialect == "mysql":
        reset_mysql()
    else:
        raise ValueError(f"Unknown dialect: {dialect}")


# ============================================================
# Execute SQL (DDL, DML, multi-statement scripts)
# ============================================================

def _split_pg_statements(script: str) -> List[str]:
    """
    Split a Postgres script into statements while preserving DO blocks,
    dollar-quoted bodies, line comments (-- ...), block comments (/* ... */),
    and single-quoted string literals. Returns a list of trimmed statement strings.

    A statement is considered empty (and skipped) if it contains no tokens
    other than whitespace and comments — psycopg2 raises "can't execute an
    empty query" otherwise.
    """
    if not script.strip():
        return []
    statements: List[str] = []
    buf: List[str] = []
    i = 0
    n = len(script)
    in_dollar = False
    dollar_tag = ""

    def _strip_comments_and_ws(s: str) -> str:
        """Return s with -- line comments and /* */ block comments removed,
        then stripped. Used to decide if a chunk is effectively empty."""
        out = []
        j = 0
        m = len(s)
        while j < m:
            if s[j:j+2] == "--":
                # skip to end of line
                nl = s.find("\n", j)
                if nl == -1:
                    break
                j = nl + 1
                continue
            if s[j:j+2] == "/*":
                end = s.find("*/", j + 2)
                if end == -1:
                    break
                j = end + 2
                continue
            out.append(s[j])
            j += 1
        return "".join(out).strip()

    while i < n:
        if not in_dollar:
            # -- line comment: copy through end of line as part of buf
            if script[i:i+2] == "--":
                nl = script.find("\n", i)
                if nl == -1:
                    buf.append(script[i:])
                    i = n
                else:
                    buf.append(script[i:nl+1])
                    i = nl + 1
                continue
            # /* block comment */
            if script[i:i+2] == "/*":
                end = script.find("*/", i + 2)
                if end == -1:
                    buf.append(script[i:])
                    i = n
                else:
                    buf.append(script[i:end+2])
                    i = end + 2
                continue
            # single-quoted string literal (handles '' escape)
            if script[i] == "'":
                buf.append("'")
                i += 1
                while i < n:
                    if script[i] == "'" and i + 1 < n and script[i+1] == "'":
                        buf.append("''")
                        i += 2
                        continue
                    buf.append(script[i])
                    if script[i] == "'":
                        i += 1
                        break
                    i += 1
                continue
            # dollar-quoted body, e.g., $$ or $tag$
            m = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*)?\$", script[i:])
            if m:
                dollar_tag = m.group(0)
                in_dollar = True
                buf.append(dollar_tag)
                i += len(dollar_tag)
                continue
            if script[i] == ";":
                raw = "".join(buf)
                if _strip_comments_and_ws(raw):
                    statements.append(raw.strip())
                buf = []
                i += 1
                continue
            buf.append(script[i])
            i += 1
        else:
            # inside dollar-quoted; look for matching close tag
            if script[i:i + len(dollar_tag)] == dollar_tag:
                buf.append(dollar_tag)
                i += len(dollar_tag)
                in_dollar = False
                dollar_tag = ""
                continue
            buf.append(script[i])
            i += 1
    raw_tail = "".join(buf)
    if _strip_comments_and_ws(raw_tail):
        statements.append(raw_tail.strip())
    return statements


def execute_pg_script(script: str) -> None:
    """Run a multi-statement Postgres script (DDL + DML, including DO blocks)."""
    conn = psycopg2.connect(**_pg_settings())
    conn.autocommit = True
    try:
        with conn.cursor() as cur:
            for stmt in _split_pg_statements(script):
                cur.execute(stmt)
    finally:
        conn.close()


def execute_mysql_script(script: str) -> None:
    """Run a multi-statement MySQL script."""
    conn = pymysql.connect(**_mysql_settings())
    try:
        with conn.cursor() as cur:
            # PyMySQL handles ; splitting via execute; use multi-stmt loop
            for stmt in [s.strip() for s in script.split(";") if s.strip()]:
                cur.execute(stmt)
        conn.commit()
    finally:
        conn.close()


def execute_script(dialect: str, script: str) -> None:
    if dialect == "postgresql":
        execute_pg_script(script)
    elif dialect == "mysql":
        execute_mysql_script(script)
    else:
        raise ValueError(f"Unknown dialect: {dialect}")


# ============================================================
# Run a query and return a DataFrame (used for user-submitted solutions)
# ============================================================

_SQLSTATE_HELP = {
    "22P02": "A value could not be converted to the target type (e.g. a ::int / ::numeric / CAST applied to text that isn't a number). Clean or guard the value before casting (CASE / NULLIF, or only cast rows that are numeric).",
    "22003": "A number is out of range for its column type.",
    "22012": "Division by zero. Guard the denominator, e.g. NULLIF(denominator, 0).",
    "22007": "A date/time value could not be parsed in the expected format.",
    "42703": "A column name does not exist (check the spelling and the table alias).",
    "42P01": "A table does not exist (check the table name).",
    "42601": "Syntax error.",
    "42883": "No function or operator matches that name and argument types (often a missing or wrong cast).",
    "42803": "A column must appear in GROUP BY or be wrapped in an aggregate.",
    "42702": "A column reference is ambiguous; qualify it with its table alias.",
    "23505": "A unique / primary-key constraint was violated (duplicate value).",
}


def _format_pg_error(e, stmt: str, full_sql: str) -> str:
    """Build a rich, multi-line error: the primary message + SQLSTATE and a
    plain-English meaning, any DETAIL/HINT/CONTEXT, and the failing SQL printed
    with line numbers (plus a caret at the exact spot when Postgres reports a
    statement_position, e.g. for syntax errors)."""
    diag = getattr(e, "diag", None)
    primary = (getattr(diag, "message_primary", None) or str(e) or "").strip()
    code = getattr(e, "pgcode", None)
    out = [primary + (f"   (SQLSTATE {code})" if code else "")]
    helptext = _SQLSTATE_HELP.get(code)
    if helptext:
        out.append(helptext)
    for label, attr in (("DETAIL", "message_detail"), ("HINT", "message_hint"), ("CONTEXT", "context")):
        val = getattr(diag, attr, None) if diag else None
        if val:
            out.append(f"{label}: {str(val).strip()}")
    src = (stmt or full_sql or "").strip("\n")
    src_lines = src.split("\n")
    err_line = err_col = None
    pos = getattr(diag, "statement_position", None) if diag else None
    if pos:
        try:
            p = int(pos) - 1
            err_line = src.count("\n", 0, p) + 1
            err_col = p - src.rfind("\n", 0, p)   # 1-based column on that line
        except Exception:
            err_line = err_col = None
    if src.strip():
        width = len(str(len(src_lines)))
        out.append("Your SQL:")
        for i, ln in enumerate(src_lines, 1):
            out.append(f"  {str(i).rjust(width)} | {ln}")
            if err_line == i and err_col:
                out.append("  " + " " * width + " | " + " " * (err_col - 1) + "^")
    return "\n".join(out)


def run_query(dialect: str, sql: str) -> Tuple[Optional[pd.DataFrame], Optional[str]]:
    """
    Run user SQL and return (result_df, error_message).

    For Postgres, the user SQL may contain DO blocks followed by a trailing
    SELECT. We execute the whole thing, then return rows from the LAST query
    that produced a result set.
    """
    try:
        if dialect == "postgresql":
            conn = psycopg2.connect(**_pg_settings())
            conn.autocommit = True
            try:
                with conn.cursor() as cur:
                    last_df = None
                    statements = _split_pg_statements(sql)
                    if not statements:
                        return None, "No SQL provided."
                    for stmt in statements:
                        try:
                            cur.execute(stmt)
                        except Exception as ex:
                            return None, _format_pg_error(ex, stmt, sql)
                        if cur.description is not None:
                            cols = [d[0] for d in cur.description]
                            rows = cur.fetchall()
                            last_df = pd.DataFrame(rows, columns=cols)
                    if last_df is None:
                        return pd.DataFrame(), (
                            "Query ran but returned no result set. "
                            "Add a trailing SELECT so the test harness has output."
                        )
                    return last_df, None
            finally:
                conn.close()
        elif dialect == "mysql":
            conn = pymysql.connect(**_mysql_settings())
            try:
                with conn.cursor() as cur:
                    statements = [s.strip() for s in sql.split(";") if s.strip()]
                    if not statements:
                        return None, "No SQL provided."
                    last_df = None
                    for stmt in statements:
                        cur.execute(stmt)
                        if cur.description is not None:
                            cols = [d[0] for d in cur.description]
                            rows = cur.fetchall()
                            last_df = pd.DataFrame(rows, columns=cols)
                    conn.commit()
                    if last_df is None:
                        return pd.DataFrame(), (
                            "Query ran but returned no result set. "
                            "Add a trailing SELECT so the test harness has output."
                        )
                    return last_df, None
            finally:
                conn.close()
        else:
            return None, f"Unknown dialect: {dialect}"
    except Exception as e:
        return None, str(e)


def _norm_pg_type(t):
    """Normalize a Postgres canonical type name to a short upper-cased SQL label."""
    low = (t or "").strip().lower()
    if low.endswith("[]"):
        return _norm_pg_type(low[:-2]) + "[]"
    repl = {
        "timestamp without time zone": "TIMESTAMP",
        "timestamp with time zone": "TIMESTAMPTZ",
        "time without time zone": "TIME",
        "character varying": "VARCHAR",
        "character": "CHAR",
        "double precision": "DOUBLE PRECISION",
    }
    return repl.get(low, low.upper())


def run_query_typed(dialect: str, sql: str):
    """Like run_query but ALSO returns each result column's SQL type name.

    Returns (df, types, error) where `types` is a list of upper-cased SQL type
    names aligned to df.columns (e.g. TEXT, INTEGER, NUMERIC, BOOLEAN, DATE,
    TEXT[]), read authoritatively from the database via format_type on the
    result's type OIDs. `types` is None for non-postgres dialects or if the
    type lookup fails (the caller then simply omits the output schema).
    """
    if dialect != "postgresql":
        df, err = run_query(dialect, sql)
        return df, None, err
    try:
        conn = psycopg2.connect(**_pg_settings())
        conn.autocommit = True
        try:
            with conn.cursor() as cur:
                last_df = None
                last_oids = None
                statements = _split_pg_statements(sql)
                if not statements:
                    return None, None, "No SQL provided."
                for stmt in statements:
                    cur.execute(stmt)
                    if cur.description is not None:
                        cols = [d[0] for d in cur.description]
                        last_oids = [d[1] for d in cur.description]
                        rows = cur.fetchall()
                        last_df = pd.DataFrame(rows, columns=cols)
                if last_df is None:
                    return pd.DataFrame(), None, (
                        "Query ran but returned no result set. "
                        "Add a trailing SELECT so the test harness has output."
                    )
                types = None
                if last_oids:
                    try:
                        names = []
                        for oid in last_oids:
                            cur.execute("SELECT format_type(%s, -1)", (oid,))
                            names.append(_norm_pg_type(cur.fetchone()[0]))
                        types = names
                    except Exception:
                        types = None
                return last_df, types, None
        finally:
            conn.close()
    except Exception as e:
        return None, None, str(e)


# ============================================================
# Compare result to expected (order-insensitive by default)
# ============================================================

# Match ISO-style timestamps like "2026-05-14 03:42:19.205133" or with 'T'.
# Used to detect CURRENT_TIMESTAMP columns that drift between expected-output
# generation and user-query execution.
_ISO_TS_RE = re.compile(r'^\d{4}-\d{2}-\d{2}([ T]\d{2}:\d{2}:\d{2}(\.\d+)?)?$')

# A "no value" cell, however pandas / psycopg2 happened to render it:
# None, numpy NaN, pandas NaT / <NA>, SQL NULL, or an empty string. These are
# display artifacts of the SAME thing (a NULL), so they compare as equal.
_NULLISH = {'', 'none', 'nan', 'nat', '<na>', 'null'}

# A clean numeric literal with NO leading-zero padding (so '007' is NOT treated
# as the number 7). Lets '9' == '9.0' and '3.5' == '3.50' — the int-vs-float
# difference pandas creates when a column has a NULL and gets promoted to float.
_NUM_RE = re.compile(r'^-?(0|[1-9]\d*)(\.\d+)?$')

# Allowed drift between two CURRENT_TIMESTAMP captures. Practice tests
# typically run within minutes of generation; 1 hour is conservative.
_TIMESTAMP_TOLERANCE_SECONDS = 3600


def _parse_iso_ts(s: str) -> Optional[datetime]:
    """Parse an ISO-format timestamp string. Returns None if it can't parse."""
    if not isinstance(s, str) or not _ISO_TS_RE.match(s):
        return None
    try:
        s = s.replace('T', ' ')
        if ':' not in s:            # date-only -> treat as that date at midnight
            s = s + ' 00:00:00'
        return datetime.fromisoformat(s)
    except Exception:
        return None


def _values_equivalent(av: str, ev: str) -> bool:
    """True if the two stringified cell values match exactly, OR if both look
    like ISO timestamps within ``_TIMESTAMP_TOLERANCE_SECONDS`` of each other.
    The tolerance handles the CURRENT_TIMESTAMP drift pattern: the test
    harness captures NOW() when generating expected output, and the user
    captures NOW() a few minutes later when running their query — same SQL,
    different wall-clock moment.
    """
    if av == ev:
        return True
    # "No value" in any disguise (None / NaN / NaT / <NA> / NULL / '') is one thing.
    al, el = str(av).strip().lower(), str(ev).strip().lower()
    a_null, e_null = al in _NULLISH, el in _NULLISH
    if a_null or e_null:
        return a_null and e_null     # both null = equal; one null = a real difference
    # Same number, different rendering: 9 == 9.0, 3.5 == 3.50 (int-vs-float from a
    # NULL-promoted column, or Decimal scale). Zero-padded strings are excluded.
    if _NUM_RE.match(al) and _NUM_RE.match(el):
        try:
            return float(av) == float(ev)
        except (TypeError, ValueError):
            pass
    # Same moment: a date vs that date at midnight, or CURRENT_TIMESTAMP drift.
    ta = _parse_iso_ts(av)
    te = _parse_iso_ts(ev)
    if ta is None or te is None:
        return False
    return abs((ta - te).total_seconds()) <= _TIMESTAMP_TOLERANCE_SECONDS


def compare_results(
    actual: pd.DataFrame,
    expected: pd.DataFrame,
    order_matters: bool = False,
) -> Tuple[bool, str]:
    """Compare actual vs expected. Returns (match, diff_message).

    Timestamp columns get a tolerance window (default 1 hour) so that
    ``CURRENT_TIMESTAMP`` captures in expected vs actual don't cause false
    failures on archive-style problems.
    """
    if actual is None:
        return False, "Actual result is None."
    if list(actual.columns) != list(expected.columns):
        return False, (
            f"Column mismatch.\n"
            f"  Got:      {list(actual.columns)}\n"
            f"  Expected: {list(expected.columns)}"
        )
    if len(actual) != len(expected):
        return False, (
            f"Row count mismatch: got {len(actual)}, expected {len(expected)}."
        )
    a = actual.copy().reset_index(drop=True)
    e = expected.copy().reset_index(drop=True)
    if not order_matters:
        try:
            a = a.sort_values(by=list(a.columns), na_position="last").reset_index(drop=True)
            e = e.sort_values(by=list(e.columns), na_position="last").reset_index(drop=True)
        except Exception:
            pass
    # Cast to string for tolerant comparison (handles int vs Decimal etc.)
    a_str = a.astype(str)
    e_str = e.astype(str)
    if a_str.equals(e_str):
        return True, "Match."

    # Tolerant pass: walk each row/column. ISO timestamps within
    # _TIMESTAMP_TOLERANCE_SECONDS of each other count as equivalent.
    diff_rows = []
    timestamp_tolerated = False
    for i in range(len(a_str)):
        row_diff = {}
        for col in a_str.columns:
            av = a_str.iloc[i][col]
            ev = e_str.iloc[i][col]
            if av == ev:
                continue
            if _values_equivalent(av, ev):
                timestamp_tolerated = True
                continue
            row_diff[col] = (av, ev)
        if row_diff:
            diff_rows.append((i, row_diff))
            if len(diff_rows) >= 5:
                break

    if not diff_rows:
        suffix = " (timestamp columns matched within tolerance)" if timestamp_tolerated else ""
        return True, f"Match{suffix}."

    msg = "Result does not match expected output. First differences:\n"
    for i, row_diff in diff_rows:
        cells = ", ".join(
            f"{col}: got {got!r}, expected {exp!r}" for col, (got, exp) in row_diff.items()
        )
        msg += f"  Row {i}: {cells}\n"
    return False, msg
