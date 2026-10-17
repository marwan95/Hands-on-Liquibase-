# Module 01 – Solutions

## Hands-on
Reference: [lab/changelog/module01.sql](lab/changelog/module01.sql) (it also contains the Module 08 Oracle twins; ignore the `-ora` ones for now).

```sql
--changeset yourname:3
CREATE TABLE products (
    product_id   SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    price        NUMERIC(12,2) NOT NULL
);
--rollback DROP TABLE products;

--changeset yourname:4
ALTER TABLE customers ADD COLUMN phone VARCHAR(20);
--rollback ALTER TABLE customers DROP COLUMN phone;
```

What you should have seen:
- **`update-sql`** prints more than your SQL: the creation of the tracking tables (first run only), `UPDATE databasechangeloglock SET locked = TRUE`, your `CREATE TABLE`s, one `INSERT INTO databasechangelog` **per changeset**, and the lock release.
- **DATABASECHANGELOG:** `exectype = EXECUTED`. Changesets 1 and 2 share a `deployment_id` (same `update`); 3 and 4 have a different one.
- **The second `update`** says "Database is up to date, no changesets to execute".
- **Step 7:** `Validation Failed: 1 changesets check sum changelog/module01.sql::1::yourname was: 9:… but is now: 9:…`. **The whole deployment stops**, not just that changeset. Reverting the edit fixes it.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **B** | Without `--liquibase formatted sql`, the file is treated as one plain script (you'll see this in Module 06). |
| q2 | **C** | A dry run: it prints the SQL and changes nothing. Use it before every real deployment. |
| q3 | **B** | The stored checksum no longer matches, so validation fails and **nothing** deploys until the edit is reverted (or handled, Module 05). |
| q4 | **A** | `deployment_id` groups the changesets deployed by one `update` command. |
| q5 | **D** | Deployed changesets are history. Changes go in **new** changesets. Editing (A, C) breaks or hides history; changing it by hand (B) creates drift (Module 09). |
