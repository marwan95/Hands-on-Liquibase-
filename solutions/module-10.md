# Module 10 – Solutions

## Hands-on
Reference: [module10.yaml](lab/changelog/module10.yaml) and the edited [country_codes.csv](lab/changelog/data/country_codes.csv).

- **Exercise 1:** after the CSV edit, `update-sql` shows for every row:
  ```sql
  DO $$ BEGIN
    UPDATE public.country_codes SET country_name = 'Sultanate of Oman', region = 'GCC' WHERE country_code = 'OM';
    IF not found THEN
      INSERT INTO public.country_codes (country_code, country_name, region) VALUES ('OM', 'Sultanate of Oman', 'GCC');
    END IF;
  END; $$ LANGUAGE plpgsql;
  ```
  After `update`: OM is renamed, JO is inserted, there are no duplicates, and `m10-2` shows `RERAN`.
- **Exercise 2:** without `runInTransaction: false`:
  ```
  ERROR: CREATE INDEX CONCURRENTLY cannot run inside a transaction block
  ```
  The failed changeset was **not recorded**, so editing it is safe. With `runInTransaction: false` it deploys.
- **Exercise 3:** `validate` = Modules 01–02 · `update-sql` = Module 01 · `update-testing-rollback` = Module 04 · `tag` = Module 04 · `LIQUIBASE_COMMAND_CONTEXT_FILTER` = Module 07 · the nightly schedule = Module 09 drift detection · `LIQUIBASE_COMMAND_PASSWORD` from secrets = this module.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **D** | PostgreSQL forbids `CONCURRENTLY` inside a transaction. |
| q2 | **A** | `UPDATE`, then `INSERT` when no row was found. |
| q3 | **C** | Expand → migrate → contract keeps the applications working throughout. |
| q4 | **B** | It deploys, rolls back and redeploys, so a broken rollback fails in CI instead of during an incident. |
| q5 | **D** | Never commit passwords. Commit a `*.example` template instead. |
