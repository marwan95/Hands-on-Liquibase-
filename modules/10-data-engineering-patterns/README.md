# Module 10 – Data engineering patterns

**Goal:** the patterns used in real data platforms: reference data in git, non-blocking indexes, zero-downtime changes and CI/CD.
**Time:** ~60 min

---

## 1. Concepts

### Pattern 1: Reference data as CSV in git
Lookup tables (countries, currencies, categories) live as CSV files in git.
- `loadUpdateData` + `primaryKey` → **upsert** (update existing keys, insert new ones)
- `runOnChange: true` → re-applied automatically whenever the CSV changes

On PostgreSQL, each row becomes `DO $$ BEGIN UPDATE ...; IF not found THEN INSERT ...; END IF; END $$` (you'll see it in `update-sql`).

### Pattern 2: Statements that can't run in a transaction
Liquibase wraps each changeset in a transaction. `CREATE INDEX CONCURRENTLY`, which builds an index on a big table **without blocking writes**, refuses to run in one. Use `runInTransaction: false`. The cost: no automatic rollback if it fails halfway.

### Pattern 3: Expand → migrate → contract (zero downtime)
Never rename or drop something applications use in one step:
1. **Expand**: add the new column (apps keep working)
2. **Migrate**: backfill (in batches for big tables, separate from DDL); apps switch over
3. **Contract**: drop the old column in a **later** release, after a backup

### Pattern 4: CI/CD
Never run `update` against production from a laptop. A pipeline runs:
`validate` → `update-sql` (an artifact for reviewers) → **`update-testing-rollback`** on a throwaway database → `tag` → deploy with an explicit `context-filter`.
See the template [`docs/ci/liquibase-ci.yml`](../../docs/ci/liquibase-ci.yml).
- Settings come from environment variables: `LIQUIBASE_COMMAND_URL`, `LIQUIBASE_COMMAND_PASSWORD` (from secrets), `LIQUIBASE_COMMAND_CONTEXT_FILTER`.
- A nightly schedule runs the Module 09 drift check.

### Option placement (an easy mistake)
```bash
liquibase --defaults-file=x.properties update --context-filter=prod "-Dschema=dwh"
#          ^ global options BEFORE the command   ^ command options and -D AFTER it
```

---

## 2. Hands-on

**Exercise 1: Reference data.** Create `lab/changelog/module10.yaml` and include it in the master:
```yaml
databaseChangeLog:
  - changeSet:
      id: m10-1
      author: yourname
      changes:
        - createTable:
            tableName: country_codes
            columns:
              - column: { name: country_code, type: CHAR(2), constraints: { primaryKey: true } }
              - column: { name: country_name, type: VARCHAR(100), constraints: { nullable: false } }
              - column: { name: region, type: VARCHAR(20) }

  - changeSet:
      id: m10-2
      author: yourname
      runOnChange: true
      changes:
        - loadUpdateData:
            tableName: country_codes
            file: data/country_codes.csv
            relativeToChangelogFile: true
            primaryKey: country_code
      rollback: []
```
1. Run `liquibase update`.
2. Edit [`lab/changelog/data/country_codes.csv`](../../lab/changelog/data/country_codes.csv): rename `Oman` → `Sultanate of Oman`, and add the line `JO,Jordan,LEVANT`.
3. Run `liquibase update-sql` and read the generated SQL, then `liquibase update`.
4. Check the table and the `exectype` of `m10-2`.

**Exercise 2: Learn from the error.** Add this changeset **without** `runInTransaction`:
```yaml
  - changeSet:
      id: m10-3
      author: yourname
      dbms: postgresql
      changes:
        - sql:
            sql: CREATE INDEX CONCURRENTLY ix_country_region ON country_codes(region)
      rollback:
        - sql:
            sql: DROP INDEX CONCURRENTLY ix_country_region
```
Run `liquibase update` and read the error. Then add `runInTransaction: false` (under `author:`) and run it again. Editing it is safe, because a **failed** changeset is never recorded.

**Exercise 3:** Read [`docs/ci/liquibase-ci.yml`](../../docs/ci/liquibase-ci.yml) and link each step to a module you've done.

---

## 3. Quiz
Answer under `module-10` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** What does `CREATE INDEX CONCURRENTLY` need in a changeset?
- A) `runAlways: true`
- B) `splitStatements: false`
- C) `context: prod`
- D) `runInTransaction: false`

**q2.** What does `loadUpdateData` generate on PostgreSQL for each CSV row?
- A) `UPDATE`, then `INSERT` if no row was found
- B) `INSERT` only
- C) `DELETE` + `INSERT`
- D) `TRUNCATE` + `INSERT`

**q3.** How do you safely rename a column that live applications use?
- A) `renameColumn` in one release
- B) Edit the original `createTable` changeset
- C) Expand → migrate → contract across releases
- D) Drop it and add it again

**q4.** Which CI step proves your rollbacks really work?
- A) `validate`
- B) `update-testing-rollback`
- C) `update-sql`
- D) `status`

**q5.** Where do database passwords belong in a real project?
- A) In `liquibase.properties`, committed to git
- B) In a changelog comment
- C) In the README
- D) In environment variables / a secrets manager (e.g. CI secrets)

---

## 4. Check your work
```bash
docker compose run --rm grader --module 10
```
Answers & explanations: [solutions/module-10.md](../../solutions/module-10.md)
