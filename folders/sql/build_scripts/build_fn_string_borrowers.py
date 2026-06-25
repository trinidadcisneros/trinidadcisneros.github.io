"""Add a 2nd worked card to fn-string: 'Clean Names & Blank-Safe Email Domains' — INITCAP/TRIM
the name, SPLIT_PART the email domain, and crucially COALESCE(NULLIF(domain,''), 'unknown') so
BOTH a NULL email and an empty-string email fall back to 'unknown' (SPLIT_PART on '' returns ''
not NULL, so NULLIF is required). Postgres-verified. Idempotent (replace-in-place) + balanced.
Run:  python3 build_fn_string_borrowers.py
"""
import re, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import eabuild as eb
PATH = os.path.normpath(os.path.join(HERE, '..', 'sql_problem_patterns.html'))

CARD = {
    'diff': 'Medium', 'color': '#e65100', 'title': 'Clean Names & Blank-Safe Email Domains',
    'excerpt': "Title-case the name and pull the email domain, with 'unknown' for BOTH NULL and empty-string emails.",
    'prompt': ["<code>borrowers.full_name</code> is ALL-CAPS with stray spaces; <code>contact_email</code> may be NULL or an empty string ('').",
               "Return <code>borrower_id</code>, <code>clean_name</code> (trimmed + title-cased), and <code>email_domain</code> (lowercase, the part after '@').",
               "When the email is NULL <em>or</em> empty, return <code>'unknown'</code> for the domain. Order by <code>borrower_id</code>."],
    'inputs': [{'name': 'borrowers',
                'cols': [('borrower_id', 'INT'), ('full_name', 'TEXT'), ('contact_email', 'TEXT')],
                'headers': ['borrower_id', 'full_name', 'contact_email'],
                'rows': [[1, 'ALICE MARTINEZ', 'alice.martinez@email.com'],
                         [2, 'BOB CHEN', 'bob.chen@provider.org'],
                         [3, 'CAROL WHITE', None],
                         [4, 'DAVID KUMAR', ''],
                         [5, 'EVE JOHNSON', 'eve@startup.io'],
                         [6, 'FRANK GARCIA', 'frank.garcia@company.co.uk']]}],
    'exp_headers': ['borrower_id', 'clean_name', 'email_domain'],
    'exp_rows': [[1, 'Alice Martinez', 'email.com'],
                 [2, 'Bob Chen', 'provider.org'],
                 [3, 'Carol White', 'unknown'],
                 [4, 'David Kumar', 'unknown'],
                 [5, 'Eve Johnson', 'startup.io'],
                 [6, 'Frank Garcia', 'company.co.uk']],
    'sol_comment': ("INITCAP(TRIM(...)) cleans the name. For the domain: SPLIT_PART after the @ gives the part you want,\n"
                    "but the TRAP is the empty-string row -- SPLIT_PART('', '@', 2) returns '' (an empty string), NOT NULL,\n"
                    "so a plain COALESCE would keep that blank. NULLIF(domain, '') converts the blank into NULL FIRST, and\n"
                    "THEN COALESCE swaps NULL -> 'unknown'. The combo COALESCE(NULLIF(x, ''), default) handles NULL and\n"
                    "empty string together. (A NULL email already flows to NULL through SPLIT_PART.) Verified."),
    'sol_sql': ("SELECT borrower_id,\n"
                "       INITCAP(TRIM(full_name)) AS clean_name,\n"
                "       COALESCE(\n"
                "           NULLIF(LOWER(SPLIT_PART(TRIM(contact_email), '@', 2)), ''),\n"
                "           'unknown'\n"
                "       ) AS email_domain\n"
                "FROM borrowers\n"
                "ORDER BY borrower_id;"),
}


def _lit(v):
    if v is None: return 'NULL'
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


def main():
    ok, got, exp = verify_pg(CARD)
    print('[pg-verify %s] %s' % ('OK ' if ok else 'FAIL', CARD['title']))
    if not ok:
        print('GOT', got); print('EXP', exp); raise SystemExit('verify failed')
    text = open(PATH).read()
    before = eb.balance_report(text)
    if 'Blank-Safe Email Domains' in text:
        s, e = eb.find_block(text, 'Blank-Safe Email Domains')
        text = text[:s] + eb.build_card(CARD) + text[e:]
        print('replaced existing card in place.')
    else:
        s, e = eb.find_block(text, 'Parse Emails')   # the existing fn-string email card
        text = text[:e] + '\n              ' + eb.build_card(CARD) + text[e:]
        print('inserted new card after the existing fn-string email card.')
    after = eb.balance_report(text)
    print('Balance before:', before)
    print('Balance after :', after)
    if after['div_open'] != after['div_close'] or after['details_open'] != after['details_close'] \
       or after['final_depth'] != 0 or after['min_depth'] < 0:
        raise SystemExit('balance check failed; NOT writing')
    open(PATH, 'w').write(text)
    print('WROTE borrowers card into fn-string')


if __name__ == '__main__':
    main()
