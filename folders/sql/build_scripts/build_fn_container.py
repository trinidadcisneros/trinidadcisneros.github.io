"""Build the 'Functions: Parse, Clean & Convert' top-level container in the Single-Table
Recipes tab, with 6 nested family sub-containers (String / Array / Date / Cast / Numeric /
Conditional). Each family = a 'How to pick' decision-tree placeholder + a verified Function
reference table + one Postgres-verified worked 'cleaning recipe' card.
Mirrors build_pop_leaves.py / build_ml_leaves.py. Idempotent (skips if already present),
balance-checked. Decision trees are added separately via itree_specs.py + build_itree_examples.py.
Run:  python3 build_fn_container.py
"""
import re, os, sys, html as _html

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb

PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))
E = lambda s: _html.escape(str(s), quote=False)


# ============================================================
# Function reference data  (func signature, what it does, example, verified result)
# ============================================================
REF = {
 'fn-string': [
  ("INITCAP(text)", "Title-case each word", "INITCAP('thai curry')", "Thai Curry"),
  ("UPPER / LOWER", "Change case", "UPPER('abc')", "ABC"),
  ("SUBSTRING(s FROM a FOR n)", "Slice from position a (1-based), length n", "SUBSTRING('abcdef' FROM 2 FOR 3)", "bcd"),
  ("LEFT / RIGHT(s, n)", "First / last n characters", "LEFT('abcdef', 3)", "abc"),
  ("SPLIT_PART(s, delim, n)", "The nth piece of a delimited string", "SPLIT_PART('30.11.1989', '.', 3)", "1989"),
  ("POSITION(sub IN s)", "1-based index of sub (0 if absent)", "POSITION('@' IN 'a@b.com')", "2"),
  ("TRIM / BTRIM(s, chars)", "Strip leading & trailing chars", "BTRIM('xxhixx','x')", "hi"),
  ("REPLACE(s, from, to)", "Replace every occurrence", "REPLACE('555-12-99','-','')", "5551299"),
  ("CONCAT_WS(sep, a, b, …)", "Join with a separator (skips NULLs)", "CONCAT_WS('-','2024','11','30')", "2024-11-30"),
  ("LENGTH(s)", "Number of characters", "LENGTH('hello')", "5"),
  ("LPAD(s, len, pad)", "Left-pad to a fixed width", "LPAD('7',3,'0')", "007"),
  ("REGEXP_REPLACE(s, pat, r, 'g')", "Regex replace (g = all)", "REGEXP_REPLACE('a1b2c3','[0-9]','','g')", "abc"),
 ],
 'fn-array': [
  ("arr[n]", "Nth element (arrays are 1-based)", "(ARRAY['a','b','c'])[2]", "b"),
  ("ARRAY_LENGTH(arr, 1)", "Length along dimension 1", "ARRAY_LENGTH(ARRAY[10,20,30],1)", "3"),
  ("x = ANY(arr)", "Membership test", "'b' = ANY(ARRAY['a','b','c'])", "true"),
  ("arr @> arr2", "Contains ALL of arr2", "ARRAY['a','b'] @> ARRAY['a']", "true"),
  ("arr && arr2", "Overlaps (any in common)", "ARRAY['a','b'] && ARRAY['x','b']", "true"),
  ("ARRAY_TO_STRING(arr, sep)", "Join array into text", "ARRAY_TO_STRING(ARRAY['a','b','c'],'-')", "a-b-c"),
  ("STRING_TO_ARRAY(s, sep)", "Split text into an array", "STRING_TO_ARRAY('a-b-c','-')", "{a,b,c}"),
  ("UNNEST(arr)", "Expand an array into rows", "UNNEST(ARRAY[10,20,30])", "10 / 20 / 30  (3 rows)"),
 ],
 'fn-date': [
  ("EXTRACT(part FROM ts)", "Pull a NUMBER (month, year, dow…)", "EXTRACT(MONTH FROM TIMESTAMP '2020-11-30 09:30:20')", "11"),
  ("DATE_TRUNC(unit, ts)", "Truncated TIMESTAMP, not a number", "DATE_TRUNC('month', TIMESTAMP '2020-11-30 09:30:20')", "2020-11-01 00:00:00"),
  ("AGE(a, b)", "Interval between two dates", "AGE(DATE '2020-04-01', DATE '2020-01-15')", "2 mons 17 days"),
  ("date - date", "Whole days between (an integer)", "DATE '2020-04-01' - DATE '2020-03-20'", "12"),
  ("date + INTERVAL", "Shift by an interval", "DATE '2020-01-15' + INTERVAL '1 month'", "2020-02-15 00:00:00"),
  ("TO_CHAR(ts, fmt)", "Format a timestamp to text (month / weekday NAMES too &mdash; see the format-pattern accordion below)", "TO_CHAR(TIMESTAMP '2020-11-30','YYYY-MM')", "2020-11"),
  ("EXTRACT(DOW FROM d)", "Day of week (0 = Sunday)", "EXTRACT(DOW FROM DATE '2020-11-30')", "1"),
 ],
 'fn-cast': [
  ("x::type  /  CAST(x AS type)", "Convert a value's type", "'42'::int", "42"),
  ("TO_DATE(s, fmt)", "Parse text into a date", "TO_DATE('30.11.2020','DD.MM.YYYY')", "2020-11-30"),
  ("TO_NUMBER(s, fmt)", "Parse text (with separators) into a number", "TO_NUMBER('1,234','9G999')", "1234"),
  ("TO_CHAR(n, fmt)", "Format a number to text", "TO_CHAR(1234.5,'FM9999.00')", "1234.50"),
  ("NULLIF(a, b)", "NULL when a = b (blank → NULL)", "NULLIF('', '')", "(NULL)"),
  ("COALESCE(a, b, …)", "First non-NULL value", "COALESCE(NULL, 0)", "0"),
 ],
 'fn-numeric': [
  ("ROUND(n, d)", "Round to d decimals", "ROUND(3.14159, 2)", "3.14"),
  ("CEIL / FLOOR(n)", "Up / down to a whole number", "CEIL(4.1)", "5"),
  ("TRUNC(n, d)", "Cut decimals WITHOUT rounding", "TRUNC(4.78, 1)", "4.7"),
  ("ABS(n)", "Absolute value", "ABS(-5)", "5"),
  ("MOD(a, b)", "Remainder", "MOD(10, 3)", "1"),
  ("POWER(a, b)", "a to the power b", "POWER(2, 3)", "8"),
  ("a::numeric / b", "Avoid integer division (7/2 = 3!)", "ROUND(7::numeric / 2, 2)", "3.50"),
  ("GREATEST / LEAST(…)", "Max / min of the arguments", "GREATEST(1, 5, 3)", "5"),
 ],
 'fn-conditional': [
  ("CASE WHEN … THEN … ELSE … END", "Branch by condition", "CASE WHEN 5 > 0 THEN 'pos' ELSE 'neg' END", "pos"),
  ("COALESCE(a, b, …)", "First non-NULL (fill a default)", "COALESCE(NULL, NULL, 0)", "0"),
  ("NULLIF(a, b)", "NULL when equal — guards divide-by-zero", "10 / NULLIF(0, 0)", "(NULL)"),
  ("GREATEST / LEAST(…)", "Max / min, skipping NULLs", "GREATEST(1, NULL, 3)", "3"),
 ],
}

FAMILY_META = {
 'fn-string':      ('String / text functions', 'string_clean',   'Parse, slice, split, and reshape text. The biggest assessment gap.'),
 'fn-array':       ('Array functions',          'array_access',   'Index, measure, test membership, and unpack array columns (1-based).'),
 'fn-date':        ('Date / time functions',    'date_extract',   'Pull parts, truncate, and format dates. Full problem recipes live in the <a href="#date-operations" style="color:#1565c0;">Date Operations</a> recipe.'),
 'fn-cast':        ('Type casting & conversion','type_cast',      'Turn messy text into proper numbers and dates, and blanks into NULLs.'),
 'fn-numeric':     ('Numeric / math functions', 'numeric_format', 'Round, truncate, modulo, and the integer-division trap.'),
 'fn-conditional': ('Conditional & NULL handling','conditional_null','CASE, COALESCE, NULLIF — branch and tame NULLs.'),
}


# ============================================================
# Worked cards (Postgres-verified)
# ============================================================
CARDS = {
 'fn-string': {
  'diff': 'Medium', 'color': '#e65100', 'title': 'Clean Names & Parse Emails',
  'excerpt': "Tidy a messy name and pull the user + domain out of an email address.",
  'prompt': ["<code>contacts</code> has a <code>raw_name</code> with stray case and spaces, and an <code>email</code>.",
             "Return <code>id</code>, a tidy <code>clean_name</code> (trimmed, title-cased), and the lowercased <code>user_part</code> and <code>domain</code> split out of the email.",
             "Order by id."],
  'inputs': [{'name': 'contacts', 'cols': [('id', 'INT'), ('raw_name', 'TEXT'), ('email', 'TEXT')],
              'headers': ['id', 'raw_name', 'email'],
              'rows': [[1, '  thai CURRY ', 'Thai.Curry@Bistro.com'], [2, 'pho HOUSE', 'info@pho-house.io']]}],
  'exp_headers': ['id', 'clean_name', 'user_part', 'domain'],
  'exp_rows': [[1, 'Thai Curry', 'thai.curry', 'bistro.com'], [2, 'Pho House', 'info', 'pho-house.io']],
  'sol_comment': ("TRIM strips the padding, INITCAP title-cases. For the email, SPLIT_PART on '@' gives piece 1\n"
                  "(the user) and piece 2 (the domain); LOWER normalizes both. Verified."),
  'sol_sql': ("SELECT id,\n"
              "       INITCAP(TRIM(raw_name))            AS clean_name,\n"
              "       LOWER(SPLIT_PART(email, '@', 1))   AS user_part,\n"
              "       LOWER(SPLIT_PART(email, '@', 2))   AS domain\n"
              "FROM contacts\nORDER BY id;"),
 },
 'fn-array': {
  'diff': 'Medium', 'color': '#e65100', 'title': 'Work with a Tags Array',
  'excerpt': "First tag, tag count, and a membership flag from a TEXT[] column.",
  'prompt': ["<code>posts</code> has a <code>tags</code> array (TEXT[]).",
             "Return <code>id</code>, the <code>first_tag</code> (arrays are 1-based), the <code>tag_count</code>, and a boolean <code>has_sql</code> that is true when 'sql' is one of the tags.",
             "Order by id."],
  'inputs': [{'name': 'posts', 'cols': [('id', 'INT'), ('tags', 'TEXT[]')],
              'headers': ['id', 'tags'],
              'rows': [[1, '{sql,python}'], [2, '{excel}'], [3, '{sql,r,stats}']]}],
  'exp_headers': ['id', 'first_tag', 'tag_count', 'has_sql'],
  'exp_rows': [[1, 'sql', 2, 't'], [2, 'excel', 1, 'f'], [3, 'sql', 3, 't']],
  'sol_comment': ("tags[1] is the first element (1-based). ARRAY_LENGTH(tags, 1) counts along the first dimension.\n"
                  "'sql' = ANY(tags) tests membership without unnesting. Verified."),
  'sol_sql': ("SELECT id,\n"
              "       tags[1]                  AS first_tag,\n"
              "       ARRAY_LENGTH(tags, 1)    AS tag_count,\n"
              "       ('sql' = ANY(tags))      AS has_sql\n"
              "FROM posts\nORDER BY id;"),
 },
 'fn-date': {
  'diff': 'Easy', 'color': '#2e7d32', 'title': 'Break a Timestamp into Parts',
  'excerpt': "Year, month, the month bucket, and a YYYY-MM label from a timestamp.",
  'prompt': ["<code>events</code> has a <code>ts</code> timestamp.",
             "Return <code>id</code>, the <code>yr</code> and <code>mon</code> numbers (EXTRACT), the <code>month_start</code> bucket (DATE_TRUNC, as a date), and a <code>label</code> formatted YYYY-MM.",
             "Note EXTRACT returns a NUMBER while DATE_TRUNC returns a truncated timestamp."],
  'inputs': [{'name': 'events', 'cols': [('id', 'INT'), ('ts', 'TIMESTAMP')],
              'headers': ['id', 'ts'],
              'rows': [[1, '2020-11-30 09:30:20'], [2, '2021-02-15 13:00:00']]}],
  'exp_headers': ['id', 'yr', 'mon', 'month_start', 'label'],
  'exp_rows': [[1, 2020, 11, '2020-11-01', '2020-11'], [2, 2021, 2, '2021-02-01', '2021-02']],
  'sol_comment': ("EXTRACT pulls numeric parts. DATE_TRUNC('month', ts) snaps to the first of the month (cast ::date\n"
                  "to drop the 00:00:00). TO_CHAR formats to a text label. Verified."),
  'sol_sql': ("SELECT id,\n"
              "       EXTRACT(YEAR  FROM ts)        AS yr,\n"
              "       EXTRACT(MONTH FROM ts)        AS mon,\n"
              "       DATE_TRUNC('month', ts)::date AS month_start,\n"
              "       TO_CHAR(ts, 'YYYY-MM')        AS label\n"
              "FROM events\nORDER BY id;"),
 },
 'fn-cast': {
  'diff': 'Medium', 'color': '#e65100', 'title': 'Parse Messy Text into Real Types',
  'excerpt': "An amount stored with a comma and a DD.MM.YYYY date string, cast properly.",
  'prompt': ["<code>raw_orders</code> stores <code>amount_txt</code> like '1,234' and <code>ordered_txt</code> like '30.11.2020'.",
             "Return <code>id</code>, the <code>amount</code> as a real number (TO_NUMBER) and <code>ordered</code> as a real date (TO_DATE).",
             "Order by id."],
  'inputs': [{'name': 'raw_orders', 'cols': [('id', 'INT'), ('amount_txt', 'TEXT'), ('ordered_txt', 'TEXT')],
              'headers': ['id', 'amount_txt', 'ordered_txt'],
              'rows': [[1, '1,234', '30.11.2020'], [2, '56', '01.02.2021']]}],
  'exp_headers': ['id', 'amount', 'ordered'],
  'exp_rows': [[1, 1234, '2020-11-30'], [2, 56, '2021-02-01']],
  'sol_comment': ("TO_NUMBER with a 9G999 mask reads the grouping comma. TO_DATE with a DD.MM.YYYY mask parses the\n"
                  "European-style date. Both turn text into a type you can compute on. Verified."),
  'sol_sql': ("SELECT id,\n"
              "       TO_NUMBER(amount_txt, '9G999')      AS amount,\n"
              "       TO_DATE(ordered_txt, 'DD.MM.YYYY')  AS ordered\n"
              "FROM raw_orders\nORDER BY id;"),
 },
 'fn-numeric': {
  'diff': 'Easy', 'color': '#2e7d32', 'title': 'Round, Total, and Test Even',
  'excerpt': "Line total, a rounded price, and an even-quantity flag — minding integer division.",
  'prompt': ["<code>items</code> has a numeric <code>price</code> and an integer <code>qty</code>.",
             "Return <code>id</code>, <code>line_total</code> = price × qty rounded to 2 dp, the <code>rounded_price</code> (to a whole number), and a boolean <code>even_qty</code> via MOD.",
             "Order by id."],
  'inputs': [{'name': 'items', 'cols': [('id', 'INT'), ('price', 'NUMERIC'), ('qty', 'INT')],
              'headers': ['id', 'price', 'qty'],
              'rows': [[1, '19.99', 4], [2, '5.00', 7]]}],
  'exp_headers': ['id', 'line_total', 'rounded_price', 'even_qty'],
  'exp_rows': [[1, '79.96', 20, 't'], [2, '35.00', 5, 'f']],
  'sol_comment': ("ROUND(price*qty, 2) totals to cents; ROUND(price) goes to a whole number. MOD(qty, 2) = 0 flags an\n"
                  "even quantity. (If qty were divided, cast to numeric first so 7/2 isn't integer-truncated to 3.) Verified."),
  'sol_sql': ("SELECT id,\n"
              "       ROUND(price * qty, 2)  AS line_total,\n"
              "       ROUND(price)           AS rounded_price,\n"
              "       (MOD(qty, 2) = 0)      AS even_qty\n"
              "FROM items\nORDER BY id;"),
 },
 'fn-conditional': {
  'diff': 'Medium', 'color': '#e65100', 'title': 'Grade with CASE, Fill NULLs with COALESCE',
  'excerpt': "Letter grade by band, a NULL score filled to 0, and a pass flag.",
  'prompt': ["<code>scores</code> has a <code>student</code> and a <code>score</code> that may be NULL.",
             "Return <code>student</code>, a <code>grade</code> (A ≥ 90, C ≥ 70, else F), the <code>safe_score</code> with NULL filled to 0, and a <code>passed</code> flag ('yes' when the filled score ≥ 70).",
             "Order by student."],
  'inputs': [{'name': 'scores', 'cols': [('student', 'TEXT'), ('score', 'INT')],
              'headers': ['student', 'score'],
              'rows': [['A', 92], ['B', None], ['C', 74]]}],
  'exp_headers': ['student', 'grade', 'safe_score', 'passed'],
  'exp_rows': [['A', 'A', 92, 'yes'], ['B', 'F', 0, 'no'], ['C', 'C', 74, 'yes']],
  'sol_comment': ("A CASE ladder assigns the letter; a NULL score matches no band, so it falls to ELSE 'F'. COALESCE\n"
                  "fills NULL to 0 for safe_score, and the pass test runs on that filled value. Verified."),
  'sol_sql': ("SELECT student,\n"
              "       CASE WHEN score >= 90 THEN 'A'\n"
              "            WHEN score >= 70 THEN 'C'\n"
              "            ELSE 'F' END                            AS grade,\n"
              "       COALESCE(score, 0)                           AS safe_score,\n"
              "       CASE WHEN COALESCE(score, 0) >= 70 THEN 'yes' ELSE 'no' END AS passed\n"
              "FROM scores\nORDER BY student;"),
 },
}

ORDER = ['fn-string', 'fn-array', 'fn-date', 'fn-cast', 'fn-numeric', 'fn-conditional']


# ============================================================
# Postgres verify (NULL / array / bool aware)
# ============================================================
def _lit(v):
    if v is None:
        return 'NULL'
    s = str(v)
    return s if re.match(r'^-?\d+$', s) else "'" + s.replace("'", "''") + "'"


def verify_pg(card):
    import pgserver, tempfile
    srv = pgserver.get_server(tempfile.mkdtemp())
    try:
        for inp in card['inputs']:
            srv.psql('CREATE TABLE %s (%s);' % (inp['name'], ', '.join('%s %s' % (n, t) for n, t in inp['cols'])))
            for row in inp['rows']:
                srv.psql('INSERT INTO %s VALUES (%s);' % (inp['name'], ', '.join(_lit(v) for v in row)))
        out = srv.psql('\\pset format unaligned\n\\pset fieldsep |\n\\pset tuples_only on\n' + card['sol_sql'])
        nc = len(card['exp_headers'])
        got = [tuple('' if c == '' else c for c in l.split('|')) for l in out.strip().splitlines()
               if l.count('|') == nc - 1 and 'format is' not in l and 'separator is' not in l]
        exp = [tuple('' if v is None else str(v) for v in r) for r in card['exp_rows']]
        return got == exp, got, exp
    finally:
        srv.cleanup()


# ============================================================
# HTML rendering
# ============================================================
def ref_table(rows):
    head = ('<table style="border-collapse:collapse; font-size:1.15rem; margin:0 0 6px; width:100%;">'
            '<thead><tr style="border-bottom:2px solid #cbd5e1;">'
            '<th style="text-align:left; padding:6px 14px 6px 0;">Function</th>'
            '<th style="text-align:left; padding:6px 14px 6px 0;">What it does</th>'
            '<th style="text-align:left; padding:6px 14px 6px 0;">Example</th>'
            '<th style="text-align:left; padding:6px 0;">Result</th></tr></thead><tbody>')
    body = ''
    for i, (fn, what, ex, res) in enumerate(rows):
        z = ' background:#f7f9fb;' if i % 2 else ''
        body += ('<tr style="border-bottom:1px solid #eef2f7;%s">'
                 '<td style="padding:6px 14px 6px 0;"><code>%s</code></td>'
                 '<td style="padding:6px 14px 6px 0; color:#475569;">%s</td>'
                 '<td style="padding:6px 14px 6px 0;"><code>%s</code></td>'
                 '<td style="padding:6px 0;"><code>%s</code></td></tr>'
                 % (z, E(fn), what, E(ex), E(res)))
    return head + body + '</tbody></table>'


def decide_card(tree_id, sub):
    return ('''<div id="%s" class="problem-card collapsed qtype-group" style="border-left-color:#6a1b9a;">
                  <div class="problem-card-header" style="background:#f3e9f7;">
                    <h3 class="problem-card-title" style="margin:0; color:#4a148c;">How to pick: decision tree</h3>
                    <span class="problem-toggle">&#9660;</span>
                  </div>
                  <div class="problem-card-excerpt" style="background:#faf5fc; color:#4a148c;">
                    <p style="margin:0;">%s</p>
                  </div>
                  <div class="problem-card-content">
<div id="%s-itree" class="itree"></div>
                  </div>
                </div>''' % (tree_id, sub, tree_id))


def reference_card(fid, rows):
    return ('''<div id="%s-ref" class="problem-card collapsed qtype-group">
                  <div class="problem-card-header"><h3 class="problem-card-title" style="margin:0;">Function reference <span class="count-badge">%d functions</span></h3><span class="problem-toggle">&#9660;</span></div>
                  <div class="problem-card-excerpt"><p style="margin:0;">Every example below is run in real PostgreSQL &mdash; the Result column is the actual output.</p></div>
                  <div class="problem-card-content">%s</div>
                </div>''' % (fid, len(rows), ref_table(rows)))


def family_container(fid):
    title, subtype, blurb = FAMILY_META[fid]
    label = '<code style="background: #eef2f7; padding: 1px 6px; border-radius: 3px;">nb01 qtype: parse_clean (%s)</code>' % subtype
    body = (decide_card(fid + '-decide', 'Answer the question &mdash; it ends on the right function for the job.')
            + '\n              ' + reference_card(fid, REF[fid])
            + '\n              ' + eb.build_card(CARDS[fid]))
    return ('''<div id="%(fid)s" class="problem-card collapsed qtype-group">
                <div class="problem-card-header"><h3 class="problem-card-title" style="margin: 0;">%(title)s <span class="count-badge">%(n)d functions</span></h3><span class="problem-toggle">&#9660;</span></div>
                <div class="problem-card-excerpt"><p style="margin: 0;">%(label)s &mdash; %(blurb)s</p></div>
                <div class="problem-card-content">
                %(body)s
                </div>
              </div>''' % {'fid': fid, 'title': title, 'n': len(REF[fid]), 'label': label, 'blurb': blurb, 'body': body})


def build_container():
    fams = '\n\n              '.join(family_container(f) for f in ORDER)
    intro = ('<p style="margin-bottom: 16px; line-height: 1.7;">PostgreSQL functions for parsing, cleaning, and converting one column at a time &mdash; the building blocks behind most "clean this messy field" assessment questions. Pick a family below; each has a decision tree, a verified function reference, and a worked cleaning recipe.</p>')
    decide = decide_card('fn-family-decide', 'Not sure which family? Answer the question to land on the right one.')
    return ('''          <!-- RECIPE: functions -->
          <div class="problem-card collapsed" id="functions">
            <div class="problem-card-header">
              <h3 class="problem-card-title" style="margin: 0;">Functions: Parse, Clean &amp; Convert <span class="count-badge">6 families</span></h3>
              <span class="problem-toggle">&#9660;</span>
            </div>
            <div class="problem-card-excerpt">
              <p>Single-column PostgreSQL functions &rarr; cleaned, parsed, or converted values.</p>
            </div>
            <div class="problem-card-content">
              %s
              %s

              %s
            </div>
          </div>
''' % (intro, decide, fams))


def main():
    for f in ORDER:
        ok, got, exp = verify_pg(CARDS[f])
        print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', CARDS[f]['title']))
        if not ok:
            print('  GOT', got)
            print('  EXP', exp)
            raise SystemExit('verify failed; nothing written')

    text = open(PATH).read()
    if 'id="functions"' in text:
        print('Functions container already present; nothing to do.')
        return
    before = eb.balance_report(text)

    # insert right after the date-operations recipe card
    s = text.find('<div class="problem-card collapsed" id="date-operations">')
    if s < 0:
        raise SystemExit('date-operations recipe not found')
    depth = 0
    e = None
    for m in re.finditer(r'<(/?)div\b', text[s:]):
        depth += 1 if m.group(1) == '' else -1
        if depth == 0:
            e = text.find('>', s + m.start()) + 1
            break
    if e is None:
        raise SystemExit('could not balance date-operations')
    block = build_container()
    text = text[:e] + '\n\n' + block + text[e:]

    after = eb.balance_report(text)
    print('\nBalance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('\nWROTE Functions container (6 families) to %s' % PATH)


if __name__ == '__main__':
    main()
