# Module 06 – Solutions

## Hands-on
Reference: [module06.sql](lab/changelog/module06.sql).

- **Exercise 1:** the index already existed → the count is 1, not 0 → the precondition fails → `onFail:MARK_RAN` → `m6-1` is recorded as **`MARK_RAN`** and `CREATE INDEX` is **not** executed.
- **Exercise 2:** the update stops with:
  ```
  Migration failed for changeset changelog/module06.sql::m6-2::yourname:
       Reason: changelog/db.changelog-master.yaml : Negative amounts found - clean the data before deploying
  ```
  `m6-2` is **not** recorded. After `DELETE FROM orders WHERE amount < 0;` the next update deploys it (`EXECUTED`).
- If your message showed only "Negative", the quotes were missing.
- If `status` showed `module06.sql::raw::includeAll`, the first line `--liquibase formatted sql` was missing.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **D** | `MARK_RAN` skips the changeset and records it, so it's never checked again. |
| q2 | **A** | `CONTINUE` skips it **without recording**, so it's evaluated again on the next update. |
| q3 | **B** | `HALT` forces a human to look. `MARK_RAN` would silently skip the fix forever while the bad data stays. |
| q4 | **C** | Without the header, the file is one raw script, and all the `--changeset` lines are just comments. |
| q5 | **A** | Quote the message: `onFailMessage:"..."`. |
