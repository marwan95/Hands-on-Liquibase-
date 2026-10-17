# Module 04 – Rollbacks & tags

**Goal:** bookmark releases with tags, preview and run rollbacks safely, and learn what a rollback can't do.
**Time:** ~45 min

---

## 1. Concepts

**Tag = a bookmark.** `liquibase tag v1.0` writes `v1.0` into the `TAG` column of the **last** row in `databasechangelog`. Tag before every release.

| Command | Rolls back... |
|---|---|
| `rollback --tag=v1.0` | everything deployed **after** the tag |
| `rollback-count --count=2` | the last N changesets |
| `rollback-to-date --date=2026-10-09T17:00:00` | everything after a time |

**Every rollback command has a `-sql` preview** (`rollback-sql`, `rollback-count-sql`, ...). **Always preview first.**
`future-rollback-sql` shows the rollback SQL for changes **not deployed yet**, so a reviewer can check the "undo plan" before a release.

**How a rollback runs:**
- **newest first**
- for each changeset: run its rollback → **delete its tracking row**
- if any changeset in the range has no rollback → the command fails **before doing anything**

**Important facts:**
- The rollback is **not** part of the checksum, so you can fix a broken rollback on a deployed changeset.
- Rollback SQL is **never executed during `update`**. A wrong rollback stays hidden until you need it. `liquibase update-testing-rollback` (update → rollback → update) catches it early. Use it in CI.
- **A rollback restores structure, not data.** A dropped column comes back with its default value; the original values are gone.
- Tags live on rows. Roll back past a tag and **the tag is gone**, so re-tag after redeploying.
- In production, many teams prefer **roll forward** (a new fixing changeset) over rollback.

---

## 2. Hands-on

**Step 1: Bookmark the current state:**
```bash
liquibase tag v1.0
```
Which row in `databasechangelog` got the tag?

**Step 2:** Create `lab/changelog/module04.yaml` and include it in the master:
```yaml
databaseChangeLog:
  - changeSet:
      id: m4-1
      author: yourname
      changes:
        - addColumn:
            tableName: customers
            columns:
              - column: { name: loyalty_points, type: INT, defaultValueNumeric: 0 }

  # deliberately NO rollback
  - changeSet:
      id: m4-2
      author: yourname
      changes:
        - dropColumn:
            tableName: suppliers
            columnName: is_active
```
Deploy it, then tag it:
```bash
liquibase update
liquibase tag v1.1
```

**Step 3:** Run `SELECT * FROM suppliers;`. The `is_active` column is gone, and so are its values. Before the drop, "Desert Foods" was `false` (see `lab/changelog/data/suppliers.csv`). Remember that for Step 5.

**Step 4: Try to go back to v1.0:**
```bash
liquibase rollback-sql --tag=v1.0
```
It fails. Read the error. Then add a `rollback` block to `m4-2` that re-adds `is_active` as `BOOLEAN` with `defaultValueBoolean: true` (hint: an `addColumn` inside `rollback:`). Run `liquibase validate`. Does the edit break the checksum?

**Step 5: Preview, then roll back:**
```bash
liquibase rollback-sql --tag=v1.0
liquibase rollback --tag=v1.0
```
Check in SQL: `loyalty_points` is gone, `is_active` is back, and the m4 rows are gone from `databasechangelog`. **What value does "Desert Foods" have now?**

**Step 6: Redeploy and re-tag:**
```bash
liquibase update
liquibase tag v1.1
```

---

## 3. Quiz
Answer under `module-04` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** You're asked to roll back production. What do you run **first**?
- A) `rollback-sql --tag=...` to preview and review the exact SQL
- B) `rollback-count --count=1`
- C) `release-locks`
- D) `clear-checksums`

**q2.** You edit **only** the rollback of an already-deployed changeset. What happens on the next `update`?
- A) A checksum error
- B) The changeset re-runs
- C) Nothing special: the rollback isn't part of the checksum
- D) You must add `validCheckSum`

**q3.** A rollback re-adds a dropped column with `DEFAULT true`. What happens to the original values?
- A) They're restored from DATABASECHANGELOG
- B) They're lost: every row gets the default value
- C) They become NULL
- D) They're restored only if you used a tag

**q4.** What does `future-rollback-sql` show?
- A) The rollback SQL of already-deployed changesets
- B) The deployment history
- C) A diff between 2 databases
- D) The rollback SQL of changesets **not yet** deployed

**q5.** You tagged `v1.1`, rolled back to `v1.0`, and then ran `update` again. Where is `v1.1`?
- A) Still on the same row
- B) Gone: it was on a row the rollback deleted, so you re-tag
- C) Moved to the previous row
- D) Converted into a label

---

## 4. Check your work
```bash
docker compose run --rm grader --module 04
```
Answers & explanations: [solutions/module-04.md](../../solutions/module-04.md)
