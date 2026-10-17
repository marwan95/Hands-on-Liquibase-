# Module 05 – Checksums & run modes

**Goal:** understand exactly what breaks a checksum, how to recover, and when to use `runAlways`.
**Time:** ~40 min

---

## 1. Concepts

### Run modes
| Attribute | Behaviour | `exectype` | Data engineering use |
|---|---|---|---|
| (default) | runs once | `EXECUTED` | tables, columns |
| `runOnChange:true` | re-runs when its content changes | `RERAN` | views, functions, reference CSVs |
| `runAlways:true` | runs on **every** `update` | `RERAN` | re-apply grants, `REFRESH MATERIALIZED VIEW`, `ANALYZE`, deployment logs |

### What changes a checksum? (tested on Liquibase 5.0.4)
| Edit to a deployed SQL changeset | Checksum changes? |
|---|---|
| Whitespace / indentation only | ❌ No |
| The rollback | ❌ No |
| A header attribute such as `dbms:` | ❌ No |
| A `--` comment line **inside** the SQL body | ✅ **Yes** |
| Any real SQL change | ✅ Yes |

### Fixing a checksum error
| Situation | Fix |
|---|---|
| Accidental edit | **Revert the file** (always the first choice) |
| Reviewed, harmless edit to a changeset already deployed everywhere | `--validCheckSum: <the "was:" value from the error>` |
| The object should re-apply on change | `runOnChange:true` |
| Many outdated checksums (e.g. after an upgrade) | `liquibase clear-checksums` (recalculated on the next update) |

`--validCheckSum: ANY` accepts **any** edit, including accidental ones. Avoid it.

### Recording without running
- `liquibase mark-next-changeset-ran`: marks the **next** pending changeset as done without executing it
- `liquibase changelog-sync`: marks **all** pending changesets as done (Module 09)
- ⚠️ On 5.0.4 both record `EXECUTED`, not `MARK_RAN`. Only a precondition (Module 06) produces `MARK_RAN`.

---

## 2. Hands-on

**Step 1:** Create `lab/changelog/module05.sql` and include it in the master:
```sql
--liquibase formatted sql

--changeset yourname:m5-1
CREATE TABLE deploy_log (
    id          SERIAL PRIMARY KEY,
    deployed_at TIMESTAMP DEFAULT now(),
    note        TEXT
);
--rollback DROP TABLE deploy_log;

--changeset yourname:m5-2 runAlways:true
INSERT INTO deploy_log (note) VALUES ('deployment ran');
--rollback empty

--changeset yourname:m5-3
CREATE INDEX idx_customers_email ON customers(email);
--rollback DROP INDEX idx_customers_email;
```
Run `liquibase update` **3 times**. Then check `SELECT * FROM deploy_log;` and the `exectype` of `m5-2`. How many rows does `m5-2` have in `databasechangelog`?

**Step 2: Whitespace.** Add extra spaces inside the `CREATE INDEX` line of `m5-3`. Run `liquibase validate`. Is there an error?

**Step 3: A comment.** Add a line `-- index for login lookups` **inside** `m5-3` (between the header and the `CREATE INDEX`). Run `liquibase validate` and read the error. Copy the `was:` value.

**Step 4: Fix it with `validCheckSum`.** Keep the comment, and add this line right under the `--changeset` header:
```sql
--validCheckSum: 9:<the was: value>
```
Run `liquibase validate` again. Then **remove both lines** (the comment and the `validCheckSum`) to keep the file clean, and validate once more.

---

## 3. Quiz
Answer under `module-05` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** You change only the indentation inside a deployed SQL changeset. What happens?
- A) A checksum error
- B) The changeset re-runs
- C) Nothing: whitespace-only changes don't change the checksum
- D) It gets marked MARK_RAN

**q2.** You add a `-- comment` line inside the body of a deployed SQL changeset. What happens?
- A) Comments are ignored
- B) The checksum changes, so validation fails
- C) The changeset re-runs
- D) Only a warning

**q3.** Which run mode fits `REFRESH MATERIALIZED VIEW mv_daily_sales;` after every deployment?
- A) `runAlways:true`
- B) `runOnChange:true`
- C) The default
- D) `context:prod`

**q4.** Why is `--validCheckSum: ANY` dangerous?
- A) It slows down deployments
- B) It deletes tracking rows
- C) It's not supported in SQL format
- D) It accepts accidental edits too, so the code and the database can silently differ

**q5.** You ran `update` 3 times with a `runAlways` insert. How many rows does that changeset have in DATABASECHANGELOG?
- A) 3
- B) 1 (updated each time, exectype RERAN)
- C) 0
- D) 2

---

## 4. Check your work
```bash
docker compose run --rm grader --module 05
```
Answers & explanations: [solutions/module-05.md](../../solutions/module-05.md)
