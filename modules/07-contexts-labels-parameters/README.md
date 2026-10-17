# Module 07 – Contexts, labels & parameters

**Goal:** deploy one codebase to many environments safely.
**Time:** ~40 min

---

## 1. Concepts

### Parameters: values that differ per environment
```sql
CREATE TABLE ${schema}.campaigns (...);
```
Set them in properties (`parameter.schema=public`) or on the command line. ⚠️ `-D` goes **after** the command, and in quotes on PowerShell:
```bash
liquibase update "-Dschema=sales"
```

### Contexts: which environment
```sql
--changeset yourname:m7-2 context:dev
```
Run with `--context-filter=dev`. Expressions are allowed: `context:"dev or test"`, `context:!prod`.

### Labels: which feature or release
```sql
--changeset yourname:m7-3 labels:release-2.0,JIRA-123
```
Run with `--label-filter=release-2.0`.

**Convention:** contexts = **environments**, labels = **features/releases/tickets**.
**Rule of thumb:** a **value** that differs per environment → parameter. **Whether** something runs per environment → context.

### ⚠️ The trap (tested on 5.0.4)
| The changeset has... | Run with a matching filter | Run with a different filter | Run with **no** filter |
|---|---|---|---|
| no context | runs | **runs** | runs |
| `context:dev` | runs | skipped (stays pending) | **runs!** |

Forget `--context-filter=prod` once, and your dev test data lands in production. **Put the filter in every environment's properties file or pipeline.**

---

## 2. Hands-on

**Step 1:** Add these 2 lines to `lab/liquibase.properties`:
```properties
parameter.schema=public
context-filter=prod
```
From now on your lab behaves like **production**.

**Step 2:** Create `lab/changelog/module07.sql` and include it in the master:
- `m7-1` (no context): `CREATE TABLE ${schema}.campaigns (campaign_id SERIAL PRIMARY KEY, name VARCHAR(100), budget NUMERIC(12,2));` with a rollback
- `m7-2` with `context:dev`: insert 2 test campaigns, with the rollback `DELETE FROM ${schema}.campaigns WHERE name LIKE 'Test Campaign%';`
- `m7-3` with `labels:release-2.0`: `ALTER TABLE ${schema}.campaigns ADD COLUMN start_date DATE;` with a rollback

**Step 3: Compare the dry runs. Don't deploy yet:**
```bash
liquibase update-sql                                   # uses context-filter=prod from the properties file
liquibase update-sql --context-filter=dev
liquibase update-sql --label-filter=release-2.0
```
Which statements show up in each one? What did `${schema}` become?

**Step 4:** Deploy with `liquibase update`. Check the `contexts` and `labels` columns in `databasechangelog`, and `SELECT COUNT(*) FROM campaigns;` (it should be **0**). Run `liquibase status --verbose --context-filter=dev`: `m7-2` is still pending.

> Already deployed `m7-2` by accident? Roll it back with `liquibase rollback-count --count=1` (preview with `rollback-count-sql` first!), as long as it's the most recent changeset.

---

## 3. Quiz
Answer under `module-07` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** A changeset has **no** context, and you run with `--context-filter=prod`. What happens?
- A) It's skipped
- B) It runs: contexts only restrict the changesets that have one
- C) Error
- D) It runs only in dev

**q2.** You run `update` with **no** context filter. What happens to a `context:dev` changeset?
- A) It's skipped
- B) It stays pending
- C) It runs
- D) Error

**q3.** Dev uses the schema `dwh_dev` and prod uses `dwh`. What's the best approach?
- A) A parameter `${schema}`, set per environment
- B) Duplicate every changeset with `context:dev` and `context:prod`
- C) Labels
- D) The `dbms` attribute

**q4.** What's the usual convention?
- A) Contexts = releases, labels = environments
- B) They're interchangeable
- C) Labels are only for database types
- D) Contexts = environments, labels = features/releases

**q5.** Which command is written correctly?
- A) `liquibase -Dschema=sales update`
- B) `liquibase update "-Dschema=sales"`
- C) Both
- D) Neither: parameters only work in properties files

---

## 4. Check your work
```bash
docker compose run --rm grader --module 07
```
Answers & explanations: [solutions/module-07.md](../../solutions/module-07.md)
