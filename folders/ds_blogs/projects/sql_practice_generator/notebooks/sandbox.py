"""
Sandbox helpers — connect to the local Postgres / MySQL containers,
load schema and seed data per problem, run user SQL, capture results.
"""

import os
import re
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
    Split a Postgres script into statements while preserving DO blocks
    and dollar-quoted bodies. Returns a list of trimmed statement strings.
    """
    if not script.strip():
        return []
    statements: List[str] = []
    buf: List[str] = []
    i = 0
    n = len(script)
    in_dollar = False
    dollar_tag = ""
    while i < n:
        ch = script[i]
        if not in_dollar:
            # detect start of dollar-quoted body, e.g., $$ or $tag$
            m = re.match(r"\$([A-Za-z_][A-Za-z0-9_]*)?\$", script[i:])
            if m:
                dollar_tag = m.group(0)
                in_dollar = True
                buf.append(dollar_tag)
                i += len(dollar_tag)
                continue
            if ch == ";":
                stmt = "".join(buf).strip()
                if stmt:
                    statements.append(stmt)
                buf = []
                i += 1
                continue
            buf.append(ch)
            i += 1
        else:
            # inside dollar-quoted; look for matching close tag
            if script[i:i + len(dollar_tag)] == dollar_tag:
                buf.append(dollar_tag)
                i += len(dollar_tag)
                in_dollar = False
                dollar_tag = ""
                continue
            buf.append(ch)
            i += 1
    tail = "".join(buf).strip()
    if tail:
        statements.append(tail)
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
                        cur.execute(stmt)
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


# ============================================================
# Compare result to expected (order-insensitive by default)
# ============================================================

def compare_results(
    actual: pd.DataFrame,
    expected: pd.DataFrame,
    order_matters: bool = False,
) -> Tuple[bool, str]:
    """Compare actual vs expected. Returns (match, diff_message)."""
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
    # Build a quick diff
    diff_rows = []
    for i in range(len(a_str)):
        if not a_str.iloc[i].equals(e_str.iloc[i]):
            diff_rows.append((i, a_str.iloc[i].to_dict(), e_str.iloc[i].to_dict()))
            if len(diff_rows) >= 5:
                break
    msg = "Result does not match expected output. First differences:\n"
    for i, got, exp in diff_rows:
        msg += f"  Row {i}: got {got}, expected {exp}\n"
    return False, msg
