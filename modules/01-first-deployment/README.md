# Module 01 – Your first deployment

**Goal:** write a formatted-SQL changelog, deploy it, and see exactly what Liquibase records.
**Time:** ~45 min

---

## 1. Concepts

A **formatted SQL changelog** is plain SQL plus special comments:
```sql
--liquibase formatted sql              <- MUST be the first line

--changeset yourname:1                 <- starts a changeset: author:id
CREATE TABLE customers (...);
--rollback DROP TABLE customers;       <- how to undo it (raw SQL has no automatic rollback)
```
Everything up to the next `--changeset` belongs to the same changeset.

| Command | What it does | Changes the database? |
|---|---|---|
| `liquibase status --verbose` | Lists pending changesets | No |
| `liquibase update-sql` | Prints the SQL `update` **would** run (dry run) | No |
| `liquibase update` | Deploys pending changesets | **Yes** |
| `liquibase history` | Lists deployed changesets | No |

Columns in `DATABASECHANGELOG` worth knowing:
- `exectype`: `EXECUTED`, `RERAN`, `MARK_RAN`, ... (more in later modules)
- `md5sum`: the checksum, e.g. `9:4240...` (the `9:` is the checksum algorithm version)
- `deployment_id`: the same value for every changeset deployed by **one** `update` command
- `orderexecuted`: the order the changesets ran in

> **Golden rule:** never edit a changeset that has already been deployed. Add a new one.

---

## 2. Hands-on
All commands run in the `lab/` folder (Docker users: see Module 00).

**Step 1: Create `lab/changelog/module01.sql`** (use your own name as the author):
```sql
--liquibase formatted sql

--changeset yourname:1
CREATE TABLE customers (
    customer_id   SERIAL PRIMARY KEY,
    full_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(150) UNIQUE,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
--rollback DROP TABLE customers;

--changeset yourname:2
CREATE TABLE orders (
    order_id      SERIAL PRIMARY KEY,
    customer_id   INT NOT NULL REFERENCES customers(customer_id),
    amount        NUMERIC(12,2) NOT NULL,
    order_date    DATE NOT NULL
);
--rollback DROP TABLE orders;
```

**Step 2: Include it in the master,** [`lab/changelog/db.changelog-master.yaml`](../../lab/changelog/db.changelog-master.yaml):
```yaml
databaseChangeLog:
  - include:
      file: module01.sql
      relativeToChangelogFile: true
```

**Step 3: Dry run, then deploy:**
```bash
liquibase status --verbose
liquibase update-sql      # read it: lock, YOUR SQL, INSERT INTO databasechangelog, unlock
liquibase update
```

**Step 4: Inspect the result** in your SQL client:
```sql
SELECT id, author, filename, orderexecuted, exectype, md5sum, deployment_id
FROM databasechangelog ORDER BY orderexecuted;
```

**Step 5: Run `liquibase update` again.** What does it say?

**Step 6: Your turn.** Add these changesets yourself and deploy them:
- `yourname:3`: create `products` (`product_id` SERIAL PK, `name` VARCHAR(100) NOT NULL, `price` NUMERIC(12,2) NOT NULL), with a rollback
- `yourname:4`: add the column `phone VARCHAR(20)` to `customers`, with a rollback

**Step 7: Break it on purpose.** In changeset **1**, change `VARCHAR(100)` to `VARCHAR(200)` and run `liquibase update`. Read the error (`was: ... but is now: ...`). Then **change it back** and confirm that `update` works again.
(You'll widen `full_name` the correct way in Module 02.)

---

## 3. Quiz
Answer under `module-01` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** What must the first line of a formatted SQL changelog be?
- A) `--changeset author:id`
- B) `--liquibase formatted sql`
- C) `-- liquibase: sql`
- D) Nothing special: any `.sql` file works

**q2.** What does `liquibase update-sql` do?
- A) Runs `update` and prints the SQL
- B) Only checks the syntax
- C) Prints the SQL that `update` would run, without changing the database
- D) Shows the deployment history

**q3.** A teammate edits a changeset that's already deployed. What happens on the next `update`?
- A) The changeset runs again with the new content
- B) A validation (checksum) error: nothing is deployed until it's resolved
- C) The edit is silently ignored
- D) A second tracking row is created

**q4.** Two rows in DATABASECHANGELOG have the same `deployment_id`. What does that mean?
- A) They were deployed by the same `update` command
- B) They have the same author
- C) They're in the same file
- D) They have the same checksum

**q5.** `customers.full_name` must become `VARCHAR(200)`, and changeset 1 is already deployed. What's the correct approach?
- A) Edit changeset 1 and run `clear-checksums`
- B) Change it by hand in pgAdmin
- C) Edit changeset 1 and run `update`
- D) Add a new changeset with `ALTER TABLE ... ALTER COLUMN ... TYPE VARCHAR(200)`

---

## 4. Check your work
```bash
docker compose run --rm grader --module 01
```
Answers & explanations: [solutions/module-01.md](../../solutions/module-01.md)
