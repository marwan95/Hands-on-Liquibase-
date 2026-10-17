"""Hands-on Liquibase grader.

Checks the learner's REAL databases (hands-on tasks) and their quiz answers in my-answers.yaml.

Run from the repository root:
    docker compose run --rm grader                 # grade everything
    docker compose run --rm grader --module 03     # one module, detailed
"""
import argparse
import hashlib
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

REPO = Path(os.environ.get("REPO_DIR", "/repo"))
ANSWERS_FILE = REPO / "my-answers.yaml"
KEY_FILE = REPO / "grading" / "answer_key.json"
REPORT_FILE = REPO / "grading" / "my-report.md"

PG = dict(host=os.environ.get("PG_HOST", "localhost"), port=int(os.environ.get("PG_PORT", "5433")),
          user="postgres", password="postgres")
ORACLE = dict(user="lb_lab", password="lb_lab", dsn=os.environ.get("ORACLE_DSN", "localhost:1521/FREEPDB1"))

MODULES = {
    "00": "Setup & core concepts",
    "01": "First deployment",
    "02": "Formats & project structure",
    "03": "Change types",
    "04": "Rollbacks & tags",
    "05": "Checksums & run modes",
    "06": "Preconditions",
    "07": "Contexts, labels & parameters",
    "08": "Oracle & cross-database",
    "09": "Reverse engineering & drift",
    "10": "Data engineering patterns",
    "exam": "Final exam",
}
CHECK_POINTS = {"exam": 2}   # points per hands-on check (default 1)


# --------------------------------------------------------------------------- database helpers
class Db:
    """Lazy connection; every query returns None when the database is unreachable."""

    def __init__(self, kind, **params):
        self.kind, self.params, self.conn, self.error = kind, params, None, None

    def _connect(self):
        if self.conn is not None or self.error is not None:
            return
        try:
            if self.kind == "pg":
                import psycopg
                self.conn = psycopg.connect(**self.params, connect_timeout=5, autocommit=True)
            else:
                import oracledb
                self.conn = oracledb.connect(**self.params, tcp_connect_timeout=5)
        except Exception as exc:  # noqa: BLE001 - report any connection problem as a hint
            self.error = str(exc).splitlines()[0]

    def scalar(self, sql, *args):
        self._connect()
        if self.conn is None:
            return None
        try:
            cur = self.conn.cursor()
            cur.execute(sql, args) if args else cur.execute(sql)
            row = cur.fetchone()
            return row[0] if row else None
        except Exception:  # noqa: BLE001 - missing tables etc. simply mean "not done yet"
            return None

    @property
    def up(self):
        self._connect()
        return self.conn is not None


lab = Db("pg", dbname="lab", **PG)
legacy = Db("pg", dbname="legacy_dwh", **PG)
legacy_ci = Db("pg", dbname="legacy_dwh_ci", **PG)
ora = Db("oracle", **ORACLE)


def n(db, sql, *args):
    """Integer result of a COUNT query (0 when unreachable / missing)."""
    v = db.scalar(sql, *args)
    return int(v) if v is not None else 0


def table(db, name):
    return n(db, "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public' AND table_name=%s", name) == 1


def column(db, tbl, col):
    return n(db, "SELECT COUNT(*) FROM information_schema.columns WHERE table_schema='public' "
                 "AND table_name=%s AND column_name=%s", tbl, col) == 1


def index(db, name):
    return n(db, "SELECT COUNT(*) FROM pg_indexes WHERE schemaname='public' AND indexname=%s", name) == 1


def dbcl(db, where, *args):
    return n(db, f"SELECT COUNT(*) FROM databasechangelog WHERE {where}", *args)


def ora_obj(obj_type, name):
    return n(ora, "SELECT COUNT(*) FROM user_objects WHERE object_type=:1 AND object_name=:2 AND status='VALID'",
             obj_type, name) == 1


# --------------------------------------------------------------------------- hands-on checks
# Each check: (description, test_function, hint shown when it fails)
CHECKS = {
    "00": [
        ("PostgreSQL lab database is reachable", lambda: lab.up,
         "Start the lab: docker compose up -d   (then wait until 'docker compose ps' shows healthy)"),
        ("Liquibase has run at least once (DATABASECHANGELOGLOCK exists)", lambda: table(lab, "databasechangeloglock"),
         "Run 'liquibase status' (or: docker compose run --rm liquibase status) from the lab folder"),
    ],
    "01": [
        ("Tables customers, orders and products exist",
         lambda: all(table(lab, t) for t in ("customers", "orders", "products")),
         "Deploy changesets 1-3 of changelog/module01.sql with 'liquibase update'"),
        ("customers.phone column exists (changeset 4)", lambda: column(lab, "customers", "phone"),
         "Add changeset 4 (ALTER TABLE customers ADD COLUMN phone ...) and run update"),
        ("At least 4 changesets from changelog/module01.sql were executed",
         lambda: dbcl(lab, "filename LIKE %s AND exectype='EXECUTED'", "%module01.sql") >= 4,
         "Check DATABASECHANGELOG: filename must be changelog/module01.sql"),
    ],
    "02": [
        ("suppliers table exists (from module02.yaml)",
         lambda: table(lab, "suppliers") and dbcl(lab, "filename LIKE %s", "%module02.yaml") >= 1,
         "Create changelog/module02.yaml and include it in the master"),
        ("warehouses table exists (from module02.xml)",
         lambda: table(lab, "warehouses") and dbcl(lab, "filename LIKE %s", "%module02.xml") >= 1,
         "Create changelog/module02.xml and include it in the master"),
        ("warehouses.city is VARCHAR(80) as specified",
         lambda: n(lab, "SELECT character_maximum_length FROM information_schema.columns "
                        "WHERE table_name='warehouses' AND column_name='city'") == 80,
         "Read the spec carefully: city VARCHAR(80)"),
        ("customers.full_name widened to VARCHAR(200) with a NEW changeset",
         lambda: n(lab, "SELECT character_maximum_length FROM information_schema.columns "
                        "WHERE table_name='customers' AND column_name='full_name'") == 200,
         "Add changeset 5 to module01.sql - never edit changeset 1"),
    ],
    "03": [
        ("Foreign key fk_products_supplier exists",
         lambda: n(lab, "SELECT COUNT(*) FROM information_schema.table_constraints "
                        "WHERE constraint_name='fk_products_supplier'") == 1,
         "m3-2: addForeignKeyConstraint"),
        ("suppliers loaded from CSV (3 rows) and products loaded from CSV (4 rows)",
         lambda: n(lab, "SELECT COUNT(*) FROM suppliers") == 3 and n(lab, "SELECT COUNT(*) FROM products") == 4,
         "m3-3 / m3-4: loadData from changelog/data/*.csv"),
        ("Index idx_orders_order_date, view v_product_catalog and sequence seq_invoice_no exist",
         lambda: index(lab, "idx_orders_order_date")
         and n(lab, "SELECT COUNT(*) FROM information_schema.views WHERE table_name='v_product_catalog'") == 1
         and n(lab, "SELECT COUNT(*) FROM information_schema.sequences WHERE sequence_name='seq_invoice_no'") == 1,
         "m3-5 createIndex, m3-6 createView, m3-7 createSequence"),
        ("Function fn_customer_total exists",
         lambda: n(lab, "SELECT COUNT(*) FROM pg_proc WHERE proname='fn_customer_total'") >= 1,
         "changelog/module03_routines.sql with splitStatements:false"),
        ("The function changeset was edited and re-deployed (exectype RERAN)",
         lambda: dbcl(lab, "filename LIKE %s AND exectype='RERAN'", "%module03_routines.sql") >= 1,
         "Use runOnChange:true, edit the function body, run update again"),
    ],
    "04": [
        ("Tag v1.0 exists", lambda: dbcl(lab, "tag='v1.0'") == 1, "liquibase tag v1.0 (before deploying module04)"),
        ("Tag v1.1 exists (re-tagged after the rollback + redeploy)", lambda: dbcl(lab, "tag='v1.1'") == 1,
         "A rollback deletes the tagged row - run 'liquibase tag v1.1' again after redeploying"),
        ("Module 04 is deployed: loyalty_points exists and suppliers.is_active is gone",
         lambda: column(lab, "customers", "loyalty_points") and not column(lab, "suppliers", "is_active"),
         "Run update after the rollback to re-deploy module04.yaml"),
        ("module04.yaml changesets are recorded", lambda: dbcl(lab, "filename LIKE %s", "%module04.yaml") == 2,
         "Both m4-1 and m4-2 must be deployed"),
    ],
    "05": [
        ("deploy_log has at least 2 rows (runAlways ran on several updates)",
         lambda: n(lab, "SELECT COUNT(*) FROM deploy_log") >= 2, "Run 'liquibase update' a few times"),
        ("The runAlways changeset shows exectype RERAN",
         lambda: dbcl(lab, "filename LIKE %s AND exectype='RERAN'", "%module05.sql") >= 1,
         "m5-2 needs runAlways:true"),
        ("Index idx_customers_email exists", lambda: index(lab, "idx_customers_email"), "m5-3"),
    ],
    "06": [
        ("A precondition marked a changeset as MARK_RAN",
         lambda: dbcl(lab, "filename LIKE %s AND exectype='MARK_RAN'", "%module06.sql") >= 1,
         "Create idx_orders_amount manually FIRST, then deploy m6-1 with onFail:MARK_RAN"),
        ("Check constraint chk_orders_amount_positive exists",
         lambda: n(lab, "SELECT COUNT(*) FROM information_schema.table_constraints "
                        "WHERE constraint_name='chk_orders_amount_positive'") == 1,
         "Clean the negative order, then deploy m6-2"),
        ("No negative amounts left in orders",
         lambda: table(lab, "orders") and n(lab, "SELECT COUNT(*) FROM orders WHERE amount < 0") == 0
         and dbcl(lab, "filename LIKE %s", "%module06.sql") >= 1, "DELETE the bad row"),
    ],
    "07": [
        ("campaigns table exists (created through ${schema})", lambda: table(lab, "campaigns"), "m7-1"),
        ("The release-2.0 label is recorded", lambda: dbcl(lab, "labels LIKE %s", "%release-2.0%") >= 1, "m7-3"),
        ("Dev-only test data was NOT deployed (context filter used)",
         lambda: table(lab, "campaigns") and n(lab, "SELECT COUNT(*) FROM campaigns") == 0
         and dbcl(lab, "id='m7-2'") == 0,
         "Deploy with --context-filter=prod (add context-filter=prod to liquibase.properties). "
         "If it already ran: liquibase rollback-count --count=... or reset the lab"),
    ],
    "08": [
        ("Oracle is reachable", lambda: ora.up, "docker compose up -d, wait for hol-oracle to be healthy"),
        ("Oracle has CUSTOMERS, ORDERS, PRODUCTS, SUPPLIERS, CAMPAIGNS",
         lambda: all(ora_obj("TABLE", t) for t in ("CUSTOMERS", "ORDERS", "PRODUCTS", "SUPPLIERS", "CAMPAIGNS")),
         "liquibase --defaults-file=liquibase-oracle.properties update"),
        ("Oracle function FN_CUSTOMER_TOTAL is VALID", lambda: ora_obj("FUNCTION", "FN_CUSTOMER_TOTAL"),
         "m3-fn-1-ora with splitStatements:false endDelimiter:/"),
        ("Oracle-only changesets did NOT run on PostgreSQL",
         lambda: ora_obj("TABLE", "CUSTOMERS") and dbcl(lab, "filename LIKE %s", "%module01.sql") >= 5
         and dbcl(lab, "id LIKE %s", "%-ora") == 0,
         "Every Oracle twin needs dbms:oracle (and Oracle must be deployed)"),
        ("Dev test data was NOT deployed to Oracle",
         lambda: ora_obj("TABLE", "CAMPAIGNS") and n(ora, "SELECT COUNT(*) FROM campaigns") == 0,
         "Add context-filter=prod to liquibase-oracle.properties"),
    ],
    "09": [
        ("legacy_dwh was baselined (>= 7 changesets recorded, nothing re-created)",
         lambda: dbcl(legacy, "filename LIKE %s", "%baseline.yaml") >= 7,
         "generate-changelog, then changelog-sync on legacy_dwh"),
        ("legacy_dwh_ci was built from the changelog",
         lambda: all(table(legacy_ci, t) for t in ("dim_customer", "dim_date", "fact_sales")),
         "liquibase --defaults-file=legacy-ci.properties update"),
        ("Drift captured: legacy_dwh_ci has fact_sales.discount and ix_fact_sales_customer",
         lambda: column(legacy_ci, "fact_sales", "discount") and index(legacy_ci, "ix_fact_sales_customer"),
         "diff-changelog -> drift-001.yaml, include it, update on CI"),
        ("Drift changesets recorded on legacy_dwh with changelog-sync",
         lambda: dbcl(legacy, "filename LIKE %s", "%drift-001.yaml") >= 2,
         "liquibase --defaults-file=legacy.properties changelog-sync"),
    ],
    "10": [
        ("country_codes reflects the edited CSV (OM renamed, JO added)",
         lambda: n(lab, "SELECT COUNT(*) FROM country_codes WHERE country_code='OM' "
                        "AND country_name='Sultanate of Oman'") == 1
         and n(lab, "SELECT COUNT(*) FROM country_codes WHERE country_code='JO'") == 1,
         "Edit changelog/data/country_codes.csv and run update"),
        ("loadUpdateData changeset re-ran (exectype RERAN)",
         lambda: dbcl(lab, "filename LIKE %s AND exectype='RERAN'", "%module10.yaml") >= 1,
         "m10-2 needs runOnChange: true"),
        ("Index ix_country_region exists (CREATE INDEX CONCURRENTLY)", lambda: index(lab, "ix_country_region"),
         "m10-3 needs runInTransaction: false"),
    ],
    "exam": [
        ("Tag before-exam exists", lambda: dbcl(lab, "tag='before-exam'") == 1, "Task A1"),
        ("exam_employees exists with a department column",
         lambda: table(lab, "exam_employees") and column(lab, "exam_employees", "department"), "Tasks A1 + A2"),
        ("Dev-only exam-3 was not deployed and the table has no test rows",
         lambda: table(lab, "exam_employees") and dbcl(lab, "id='exam-3'") == 0
         and n(lab, "SELECT COUNT(*) FROM exam_employees") == 0, "Task A3"),
        ("v_exam_payroll includes department",
         lambda: n(lab, "SELECT COUNT(*) FROM information_schema.columns WHERE table_name='v_exam_payroll' "
                        "AND column_name='department'") == 1, "Task A5"),
        ("exam-4 shows exectype RERAN", lambda: dbcl(lab, "id='exam-4' AND exectype='RERAN'") == 1, "Task A5"),
    ],
}


# --------------------------------------------------------------------------- quiz
def answer_hash(module, question, letter):
    return hashlib.sha256(f"hol|{module}|{question}|{letter.strip().upper()}".encode()).hexdigest()


def grade_quiz(module, given, key):
    expected = key.get(module, {})
    results = []
    for q in sorted(expected, key=lambda s: int(s[1:])):
        answer = str((given or {}).get(q) or "").strip().upper()
        results.append((q, answer, bool(answer) and answer_hash(module, q, answer) == expected[q]))
    return results


# --------------------------------------------------------------------------- report
def level(pct):
    if pct >= 90:
        return "Excellent"
    if pct >= 80:
        return "Very good"
    if pct >= 70:
        return "Pass"
    return "Not yet - keep practising"


def main():
    parser = argparse.ArgumentParser(description="Grade the Hands-on Liquibase course")
    parser.add_argument("--module", help="grade one module only, e.g. 03 or exam")
    args = parser.parse_args()

    if not ANSWERS_FILE.exists():
        sys.exit("my-answers.yaml not found in the repository root")
    answers = yaml.safe_load(ANSWERS_FILE.read_text(encoding="utf-8")) or {}
    key = json.loads(KEY_FILE.read_text(encoding="utf-8"))
    learner = answers.get("learner") or "(set 'learner:' in my-answers.yaml)"

    selected = [args.module.zfill(2) if args.module and args.module != "exam" else args.module] if args.module \
        else list(MODULES)
    for m in selected:
        if m not in MODULES:
            sys.exit(f"Unknown module '{m}'. Use one of: {', '.join(MODULES)}")

    lines, total, possible = [], 0, 0
    print(f"\nHands-on Liquibase - grade report for {learner}\n" + "=" * 72)
    rows = []
    for m in selected:
        quiz = grade_quiz(f"module-{m}", answers.get(f"module-{m}"), key)
        checks = [(d, bool(fn()), hint) for d, fn, hint in CHECKS[m]]
        pts = CHECK_POINTS.get(m, 1)
        got = sum(ok for _, _, ok in quiz) + pts * sum(ok for _, ok, _ in checks)
        out_of = len(quiz) + pts * len(checks)
        total, possible = total + got, possible + out_of
        rows.append((m, got, out_of))

        print(f"\n[{m}] {MODULES[m]}  -  {got}/{out_of}")
        lines.append(f"\n### [{m}] {MODULES[m]} - {got}/{out_of}\n")
        for desc, ok, hint in checks:
            mark = "PASS" if ok else "FAIL"
            print(f"   {mark}  hands-on: {desc}")
            lines.append(f"- {'✅' if ok else '❌'} hands-on: {desc}")
            if not ok:
                print(f"         hint: {hint}")
                lines.append(f"  - hint: {hint}")
        unanswered = [q for q, a, ok in quiz if not a]
        incorrect = [q for q, a, ok in quiz if a and not ok]
        correct = len(quiz) - len(unanswered) - len(incorrect)
        details = [f"incorrect: {', '.join(incorrect)}"] * bool(incorrect) + \
                  [f"unanswered: {', '.join(unanswered)}"] * bool(unanswered)
        quiz_line = f"quiz: {correct}/{len(quiz)} correct" + (f"  ({'; '.join(details)})" if details else "")
        all_ok = correct == len(quiz)
        print(f"   {'PASS' if all_ok else 'INFO'}  {quiz_line}")
        lines.append(f"- {'✅' if all_ok else 'ℹ️'} {quiz_line}")

    pct = round(100 * total / possible) if possible else 0
    print("\n" + "=" * 72)
    print(f"TOTAL: {total}/{possible} = {pct}%   ->   {level(pct)}   (pass mark: 70%)")
    for db, name in ((lab, "PostgreSQL lab"), (ora, "Oracle")):
        if db.error and any(m in selected for m in (["08"] if db is ora else ["00"])):
            print(f"note: could not connect to {name}: {db.error}")

    summary = ["| Module | Score |", "|---|---|"] + [f"| {m} {MODULES[m]} | {g}/{o} |" for m, g, o in rows]
    REPORT_FILE.write_text(
        f"# Grade report - {learner}\n\nGenerated {datetime.now():%Y-%m-%d %H:%M}\n\n"
        f"**Total: {total}/{possible} = {pct}% - {level(pct)}** (pass mark 70%)\n\n"
        + "\n".join(summary) + "\n" + "\n".join(lines) + "\n", encoding="utf-8")
    print(f"Report saved to grading/{REPORT_FILE.name}\n")


if __name__ == "__main__":
    main()
