# Module 05 – Solutions

## Hands-on
Reference: [module05.sql](lab/changelog/module05.sql).

- **Step 1:** after 3 updates, `deploy_log` has 3 rows, but `m5-2` has **one** row in `databasechangelog` with `exectype = RERAN`. It's updated on every run.
- **Step 2:** whitespace only → `validate` passes. Checksum version 9 normalises whitespace.
- **Step 3:** a comment line **inside** the body → `Validation Failed ... was: 9:xxx but is now: 9:yyy`. Comments are part of the SQL text.
- **Step 4:** `--validCheckSum: 9:xxx` (the **was:** value, i.e. what's stored in the database) makes Liquibase accept the stored checksum. Use it only for reviewed, harmless edits to changesets already deployed everywhere. Never use `ANY`.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **C** | Whitespace-only edits don't change a v9 checksum (tested on 5.0.4). |
| q2 | **B** | A comment inside the body changes the checksum. (Header attributes and rollbacks don't.) |
| q3 | **A** | It must run on **every** deployment. `runOnChange` would only run it when the text changes. |
| q4 | **D** | It also accepts accidental edits. Example: a column added inside a deployed `CREATE TABLE` raises no error but never gets created. The code and the database silently differ. |
| q5 | **B** | One row, updated each time (`RERAN`). |

**Good to know:** `mark-next-changeset-ran` and `changelog-sync` record changesets **without running them**, but on 5.0.4 they record `EXECUTED`, not `MARK_RAN`. Only preconditions produce `MARK_RAN`.
