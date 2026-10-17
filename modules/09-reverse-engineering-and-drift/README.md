# Module 09 – Reverse engineering & drift detection

**Goal:** adopt an existing database that was built without Liquibase, and catch changes made by hand.
**Time:** ~60 min

---

## 1. Concepts

| Command | What it does |
|---|---|
| `generate-changelog --changelog-file=x.yaml` | Reads an existing database and writes a changelog that rebuilds its **structure**. Refuses to overwrite an existing file. No data unless you add `--diff-types=data`. |
| `changelog-sync` (+ `changelog-sync-sql`) | Records all pending changesets as done **without running them** |
| `diff --reference-url=...` | Report comparing 2 databases |
| `diff-changelog --reference-url=... --changelog-file=drift.yaml` | Writes the differences as changesets |
| `snapshot --snapshot-format=json --output-file=snap.json` | Saves the structure to a file; diff against it later with `--reference-url=offline:postgresql?snapshot=snap.json` |

**`diff` vocabulary:** `--reference-url` = **the source of truth**, `--url` = **the target**. "Missing X" = X exists in the reference but **not** in the target.

**Adopting a database:** `generate-changelog` → (rename the ugly ids/author **now**, if you want) → `changelog-sync` on that database → `update` everywhere else.

**Drift loop:** build a clean database from the changelog → `diff` with production as the reference → `diff-changelog` → include the file → `changelog-sync` on production (it already has the changes) / `update` everywhere else.

---

## 2. Hands-on
The lab already contains a hand-built warehouse, **`legacy_dwh`** (`dim_customer`, `dim_date`, `fact_sales`, an index, a view, some data), and an empty **`legacy_dwh_ci`**. Settings files: [`lab/legacy.properties`](../../lab/legacy.properties) and [`lab/legacy-ci.properties`](../../lab/legacy-ci.properties).

<details><summary>Docker users: equivalent commands</summary>

| Local (in `lab/`) | Docker (from the repo root) |
|---|---|
| `liquibase --defaults-file=legacy.properties <cmd>` | `docker compose run --rm liquibase-legacy <cmd>` |
| `liquibase --defaults-file=legacy-ci.properties <cmd>` | `docker compose run --rm liquibase-legacy-ci <cmd>` |
| `--reference-url=jdbc:postgresql://localhost:5433/legacy_dwh` | `--reference-url=jdbc:postgresql://postgres:5432/legacy_dwh` |
</details>

### Part A: Adopt the warehouse
**A1. Create the master,** `lab/changelog/legacy/legacy-master.yaml`:
```yaml
databaseChangeLog:
  - include: { file: baseline.yaml, relativeToChangelogFile: true }
```

**A2. Generate the baseline from the existing database:**
```bash
liquibase --defaults-file=legacy.properties generate-changelog --changelog-file=changelog/legacy/baseline.yaml
```
Open it. What are the ids and the author? What did `SERIAL` become? Is the view included? The data?

**A3. Check the status.** Everything is "pending", even though the tables exist. **Don't run `update`!** Why not?
```bash
liquibase --defaults-file=legacy.properties status --verbose
```

**A4. Adopt it:**
```bash
liquibase --defaults-file=legacy.properties changelog-sync-sql     # preview
liquibase --defaults-file=legacy.properties changelog-sync
liquibase --defaults-file=legacy.properties status                 # up to date
```

**A5. Build CI from the code only:**
```bash
liquibase --defaults-file=legacy-ci.properties update
```
Compare the 2 databases. Same tables, but how many rows in `legacy_dwh_ci`?

### Part B: Catch the drift
**B1. A colleague's hand-made hotfix.** Run this on **`legacy_dwh`** in your SQL client:
```sql
ALTER TABLE fact_sales ADD COLUMN discount NUMERIC(5,2);
CREATE INDEX ix_fact_sales_customer ON fact_sales(customer_key);
```

**B2. Detect it** (production = reference, CI = target):
```bash
liquibase --defaults-file=legacy-ci.properties diff --reference-url=jdbc:postgresql://localhost:5433/legacy_dwh --reference-username=postgres --reference-password=postgres
```

**B3. Turn the drift into changesets:**
```bash
liquibase --defaults-file=legacy-ci.properties diff-changelog --reference-url=jdbc:postgresql://localhost:5433/legacy_dwh --reference-username=postgres --reference-password=postgres --changelog-file=changelog/legacy/drift-001.yaml
```
Include `drift-001.yaml` in `legacy-master.yaml` after the baseline. Then:
- **CI:** `liquibase --defaults-file=legacy-ci.properties update`
- **Production:** `liquibase --defaults-file=legacy.properties changelog-sync`

**B4.** Run B2 again. Everything should be `NONE` (apart from the catalog name).

---

## 3. Quiz
Answer under `module-09` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** How do you adopt an existing database into Liquibase?
- A) `update`
- B) `diff`, then `update`
- C) `snapshot`, then `rollback`
- D) `generate-changelog`, then `changelog-sync`

**q2.** You run `diff` with production as the reference and CI as the target. The report says `Missing Column(s): fact_sales.discount`. Where does the column exist?
- A) In production, not in CI
- B) In CI, not in production
- C) In both
- D) In neither

**q3.** You captured production's drift in `drift-001.yaml`. Which command applies it to **production**?
- A) `update`
- B) `changelog-sync`
- C) `rollback`
- D) `clear-checksums`

**q4.** Does `generate-changelog` include table data by default?
- A) Yes
- B) Only for small tables
- C) No: structure only, unless you add `--diff-types=data`
- D) Only views

**q5.** When should you rename the generated ids and author (`... (generated)`)?
- A) Any time
- B) Before `changelog-sync`
- C) After `changelog-sync`
- D) It's impossible

---

## 4. Check your work
```bash
docker compose run --rm grader --module 09
```
Answers & explanations: [solutions/module-09.md](../../solutions/module-09.md)
