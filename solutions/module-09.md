# Module 09 – Solutions

## Hands-on
Reference: [lab/changelog/legacy/](lab/changelog/legacy). Your `baseline.yaml` and `drift-001.yaml` will have different (timestamp-based) ids. That's expected.

- **A2:** 7 changesets: 3 `createTable`s, the view, the index and 2 foreign keys. Ids look like `1792229374161-1` and the author is `<your OS user> (generated)`. `SERIAL` becomes `autoIncrement: true` columns. The **view is included**; the **data is not**.
- **A3:** all 7 are pending. `update` would fail on the very first one: **`relation "dim_customer" already exists`**.
- **A4:** after `changelog-sync`, `status` is up to date. The rows are recorded (as `EXECUTED` on 5.0.4), and no SQL was run.
- **A5:** `legacy_dwh_ci` has the same tables but **0 rows**, because the baseline captured structure only.
- **B2:** the report shows
  ```
  Missing Column(s):
       public.fact_sales.discount
  Missing Index(s):
       ix_fact_sales_customer ON public.fact_sales(customer_key)
  ```
  "Missing" = present in the **reference** (production), absent from the **target** (CI).
- **B3:** `drift-001.yaml` contains a `createIndex` and an `addColumn`. Production already has both → `changelog-sync`. CI doesn't → `update`.
- **B4:** only `Changed Catalog(s)` remains (the 2 databases have different names). Everything else is `NONE`.

**Automating it:** a nightly CI job builds a fresh database from the changelog, runs `diff` against production, and fails or alerts if any Missing/Unexpected/Changed line isn't `NONE`. Alternative: take a `snapshot` at every release and diff against `offline:postgresql?snapshot=snap.json`.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **D** | Generate, then **record** with `changelog-sync`. `update` would try to create everything again. |
| q2 | **A** | Missing = in the reference (production), not in the target (CI). |
| q3 | **B** | Production already has the changes; you only record them there. |
| q4 | **C** | Structure only; data needs `--diff-types=data` (rarely a good idea for fact tables). |
| q5 | **B** | After `changelog-sync`, the ids/author are stored, so renaming would make them "new" changesets. |
