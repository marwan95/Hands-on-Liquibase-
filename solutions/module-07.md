# Module 07 – Solutions

## Hands-on
Reference: [module07.sql](lab/changelog/module07.sql) and [liquibase.properties](lab/liquibase.properties).

```sql
--changeset yourname:m7-1
CREATE TABLE ${schema}.campaigns (
    campaign_id SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    budget      NUMERIC(12,2)
);
--rollback DROP TABLE ${schema}.campaigns;

--changeset yourname:m7-2 context:dev
INSERT INTO ${schema}.campaigns (name, budget) VALUES ('Test Campaign A', 5000.00);
INSERT INTO ${schema}.campaigns (name, budget) VALUES ('Test Campaign B', 12500.50);
--rollback DELETE FROM ${schema}.campaigns WHERE name LIKE 'Test Campaign%';

--changeset yourname:m7-3 labels:release-2.0
ALTER TABLE ${schema}.campaigns ADD COLUMN start_date DATE;
--rollback ALTER TABLE ${schema}.campaigns DROP COLUMN start_date;
```

**Step 3 (dry runs):**
| Run | Includes |
|---|---|
| `update-sql` (prod from the properties file) | m7-1, m7-3 |
| `--context-filter=dev` | m7-1, **m7-2**, m7-3 |
| `--label-filter=release-2.0` (prod context still applies) | m7-1 (it has no label), m7-3 |

`${schema}` became `public`.

**Step 4:** `campaigns` has 0 rows. `m7-2` isn't in `databasechangelog`; it stays pending for dev. The `labels` column of `m7-3` shows `release-2.0`.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **B** | Contexts only restrict the changesets that **have** one. No context = runs everywhere. |
| q2 | **C** | No filter = **everything** runs, including dev data. That's why the filter belongs in each environment's settings. |
| q3 | **A** | A **value** that differs per environment → a parameter. Duplicate changesets drift apart over time. |
| q4 | **D** | Contexts = environments, labels = features/releases/tickets. |
| q5 | **B** | `-D` goes **after** the command. Before it, you get "Unexpected argument". On PowerShell, quote it. |
