# Module 11 – Final exam 🎓

**Part A (practical)** is graded automatically from your database (5 tasks × 2 points).
**Part B (scenarios)** is 10 multiple-choice questions (1 point each).
The exam counts in your total like any module. The course pass mark is **70%**.

Open book: the module READMEs and the Liquibase docs are allowed. **The solutions folder is not.** 😉

---

## Part A – Practical (PostgreSQL lab)

All exam changesets are **PostgreSQL only**: add `dbms:postgresql` to each one, because the master is also deployed to Oracle.

**A1. Tag, then create a table.**
1. `liquibase tag before-exam`
2. Create `lab/changelog/exam.sql` (formatted SQL) and include it **last** in the master.
3. Changeset `exam-1`: create `exam_employees` with `emp_id` (auto-increment PK), `emp_name` (VARCHAR(100), not null) and `salary` (NUMERIC(10,2)). Include a correct rollback.
4. Deploy it.

**A2. Precondition.** Changeset `exam-2` adds `department VARCHAR(50)` to `exam_employees`. If the column already exists, it must be **marked as ran instead of failing**. Include a rollback. Deploy it.

**A3. Context.** Changeset `exam-3`, **dev only**, inserts 2 employees. Deploy as production (your properties already contain `context-filter=prod`), so it must **not** run. Confirm it's still pending for dev.

**A4. Safe rollback.** Undo everything since `before-exam` the professional way (look at the history, preview, roll back). Then redeploy.

**A5. A view that gets updated.** Changeset `exam-4` creates the view `v_exam_payroll` (`SELECT emp_name, salary FROM exam_employees`), set up so that **editing it later re-runs it automatically**. Deploy it. Then change the view to also select `department`, and deploy again.

---

## Part B – Scenarios
Answer under `module-exam` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** Monday morning the pipeline fails: `Validation Failed: 1 changesets check sum ... was: 9:aaa but is now: 9:bbb`. What do you do **first**?
- A) Run `clear-checksums`
- B) Add `--validCheckSum: ANY`
- C) Delete the row from DATABASECHANGELOG
- D) Find the edit in git and revert it; put the intended change in a new changeset

**q2.** A deployment crashed when the VPN dropped. Now every `update` fails with "Could not acquire change log lock". What's right?
- A) Check `list-locks`, make sure nothing is really running, then `release-locks`
- B) Drop DATABASECHANGELOG
- C) Restart the database server
- D) Run `changelog-sync`

**q3.** Which group of commands **never** changes your tables or data?
- A) `update-testing-rollback`, `rollback-count`
- B) `status`, `update-sql`, `validate`, `rollback-sql`, `diff`
- C) `changelog-sync`, `update`
- D) `rollback`, `tag`

**q4.** `CREATE OR REPLACE VIEW v_sales ...` should be redeployed whenever its definition changes. Which attribute?
- A) `runAlways:true`
- B) Neither
- C) `runOnChange:true`
- D) `context:view`

**q5.** One changelog must deploy to PostgreSQL and Oracle, and a SQL changeset uses `SERIAL`. What works?
- A) It's impossible
- B) Use a context per database
- C) Use labels
- D) Rewrite it as a YAML/XML change type with `autoIncrement`, or use `dbms` twins

**q6.** A nightly `diff` (production = reference, CI = target) reports `Missing Index(s): ix_sales_region`. What does it most likely mean?
- A) Someone created the index by hand in production (drift)
- B) CI has an extra index
- C) A Liquibase bug
- D) The index was dropped from production

**q7.** Can a rollback bring back the data of a dropped column?
- A) Yes, always
- B) No: it restores structure, not data; back up before destructive changes
- C) Only with tags
- D) Only for YAML changesets

**q8.** Where does a global option like `--defaults-file` go?
- A) After the command
- B) Anywhere
- C) Before the command
- D) Only in the properties file

**q9.** A changeset failed halfway with an SQL error. What is its state?
- A) Recorded as FAILED, blocking all future deployments
- B) Recorded as EXECUTED
- C) Recorded as MARK_RAN
- D) Not recorded: fix it and run `update` again

**q10.** Which order is a safe release?
- A) `validate` → `status` → `update-sql` (review) → `tag` → `update` with the right context filter
- B) `update` → `validate`
- C) `tag` → `rollback` → `update`
- D) `update` only

---

## Check your work
```bash
docker compose run --rm grader --module exam
docker compose run --rm grader               # your full course report
```
Answers & explanations: [solutions/module-exam.md](../../solutions/module-exam.md)
