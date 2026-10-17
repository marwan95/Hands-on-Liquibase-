# Module 06 – Preconditions

**Goal:** make deployments safe to re-run, and stop deployments when data isn't ready.
**Time:** ~40 min

---

## 1. Concepts
A **precondition** is a check that runs **before** a changeset. If it fails, `onFail` decides what happens:

| `onFail` | Result | Use when |
|---|---|---|
| `HALT` (default) | Stops the whole deployment with an error | Safety guards, data-quality checks |
| `MARK_RAN` | Skips the changeset forever and records `MARK_RAN` | "Already exists, nothing to do" |
| `CONTINUE` | Skips it now **without recording it**, and checks again on the next update | Waiting for something else to exist |
| `WARN` | Logs a warning and runs anyway | Informational |

**SQL format** (tested on 5.0.4):
```sql
--changeset yourname:m6-1
--preconditions onFail:MARK_RAN
--precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_orders_amount'
CREATE INDEX idx_orders_amount ON orders(amount);
```
Read it as: "run only if the count is 0; otherwise mark it as ran".

⚠️ `onFailMessage` text with spaces **must be quoted**: `onFailMessage:"Some message"`. Without quotes it's cut at the first space.

**YAML** has built-in checks (`tableExists`, `columnExists`, `indexExists`, `viewExists`, `sequenceExists`, `foreignKeyConstraintExists`, `sqlCheck`, `dbms`, `changeSetExecuted`, ...) combined with `and` / `or` / `not`:
```yaml
      preConditions:
        - onFail: MARK_RAN
        - not:
            - tableExists:
                tableName: audit_events
```

⚠️ A `.sql` file **without** `--liquibase formatted sql` becomes ONE raw script (`status` shows `file.sql::raw::includeAll`), and all your `--changeset` / `--preconditions` / `--rollback` lines are just comments.

---

## 2. Hands-on

**Exercise 1: A DBA's hotfix.**
1. In your SQL client, simulate a DBA creating an index by hand:
   ```sql
   CREATE INDEX idx_orders_amount ON orders(amount);
   ```
2. Create `lab/changelog/module06.sql` with the `m6-1` changeset above (with `--liquibase formatted sql` as the first line), include it in the master, and run `liquibase update`.
3. Check the `exectype` of `m6-1`. Was the `CREATE INDEX` executed?

**Exercise 2: A data-quality guard (HALT).**
1. Insert bad data:
   ```sql
   INSERT INTO customers (full_name, email) VALUES ('Test User', 'test@example.com');
   INSERT INTO orders (customer_id, amount, order_date)
   VALUES ((SELECT customer_id FROM customers WHERE email = 'test@example.com'), -50, CURRENT_DATE);
   ```
2. Add this to `module06.sql`:
   ```sql
   --changeset yourname:m6-2
   --preconditions onFail:HALT onFailMessage:"Negative amounts found - clean the data before deploying"
   --precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM orders WHERE amount < 0
   ALTER TABLE orders ADD CONSTRAINT chk_orders_amount_positive CHECK (amount >= 0);
   --rollback ALTER TABLE orders DROP CONSTRAINT chk_orders_amount_positive;
   ```
3. Run `liquibase update` and read the message. Is `m6-2` in `databasechangelog`?
4. Fix the data with `DELETE FROM orders WHERE amount < 0;`, then run `liquibase update` again.

---

## 3. Quiz
Answer under `module-06` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** Which `onFail` value skips the changeset forever and records it?
- A) HALT
- B) CONTINUE
- C) WARN
- D) MARK_RAN

**q2.** What does `onFail:CONTINUE` do?
- A) Skips the changeset now without recording it, and checks again on the next update
- B) Stops the deployment
- C) Records it as ran
- D) Runs it anyway

**q3.** A production data fix must never run while bad data exists. Which `onFail` is right?
- A) MARK_RAN
- B) HALT
- C) WARN
- D) CONTINUE

**q4.** `liquibase status` lists `changelog/module06.sql::raw::includeAll`. What's wrong?
- A) The file is empty
- B) Two changesets share an id
- C) The file is missing its first line `--liquibase formatted sql`
- D) The file extension is wrong

**q5.** Your HALT message shows only the first word. How do you fix it?
- A) Put the message in quotes
- B) Use underscores instead of spaces
- C) It's impossible in SQL format
- D) Use `onError` instead

---

## 4. Check your work
```bash
docker compose run --rm grader --module 06
```
Answers & explanations: [solutions/module-06.md](../../solutions/module-06.md)
