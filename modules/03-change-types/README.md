# Module 03 – Change types (the toolbox)

**Goal:** use the change types a data engineer needs most: constraints, CSV loads, indexes, views, sequences and database functions.
**Time:** ~60 min

---

## 1. Concepts

| Category | Change type | Automatic rollback? |
|---|---|---|
| Tables | `createTable`, `renameTable`, `dropTable` | ✅ ✅ ❌ |
| Columns | `addColumn`, `renameColumn`, `modifyDataType`, `dropColumn` | ✅ ✅ ❌ ❌ |
| Constraints | `addPrimaryKey`, `addForeignKeyConstraint`, `addUniqueConstraint`, `addNotNullConstraint` | ✅ |
| Indexes | `createIndex`, `dropIndex` | ✅ ❌ |
| Objects | `createView`, `createSequence` | ✅ |
| Data | `loadData` (CSV), `loadUpdateData` (CSV upsert), `insert`, `update`, `delete` | ❌ |
| Escape hatch | `sql`, `sqlFile` | ❌ |

**Rule:** create/add/rename can be undone automatically. Drop/modify/data changes **destroy information**, so you write the rollback.

**Two attributes for SQL routines (functions, procedures, triggers):**
- `splitStatements:false`: by default Liquibase splits SQL on every `;`. A function body contains `;`, so splitting would cut it into broken pieces.
- `runOnChange:true`: normally, editing a deployed changeset is an error. With `runOnChange`, Liquibase **re-runs** it when its content changes (`exectype = RERAN`). Perfect for `CREATE OR REPLACE` objects. **Never** use it on `CREATE TABLE`: an edit would re-run the `CREATE` → "already exists".

Full reference: https://docs.liquibase.com/change-types/home.html

---

## 2. Hands-on

**Step 1:** Create `lab/changelog/module03.yaml`. The first 3 changesets are given; you write the TODOs:
```yaml
databaseChangeLog:
  - changeSet:
      id: m3-1
      author: yourname
      changes:
        - addColumn:
            tableName: products
            columns:
              - column: { name: supplier_id, type: INT }

  - changeSet:
      id: m3-2
      author: yourname
      changes:
        - addForeignKeyConstraint:
            constraintName: fk_products_supplier
            baseTableName: products
            baseColumnNames: supplier_id
            referencedTableName: suppliers
            referencedColumnNames: supplier_id

  - changeSet:
      id: m3-3
      author: yourname
      changes:
        - loadData:
            tableName: suppliers
            file: data/suppliers.csv
            relativeToChangelogFile: true
            columns:
              - column: { name: is_active, type: BOOLEAN }
      rollback:
        - delete:
            tableName: suppliers

  # TODO m3-4: loadData products from data/products.csv (price and supplier_id are NUMERIC) + a rollback
  # TODO m3-5: createIndex idx_orders_order_date on orders(order_date)
  # TODO m3-6: createView v_product_catalog (replaceIfExists: true):
  #            SELECT p.product_id, p.name, p.price, s.supplier_name, s.country
  #            FROM products p LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id
  # TODO m3-7: createSequence seq_invoice_no, startValue 1000, incrementBy 1
```

**Step 2:** Create `lab/changelog/module03_routines.sql`:
```sql
--liquibase formatted sql

--changeset yourname:m3-fn-1 splitStatements:false runOnChange:true
CREATE OR REPLACE FUNCTION fn_customer_total(p_customer_id INT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC;
BEGIN
    SELECT COALESCE(SUM(amount), 0) INTO v_total
    FROM orders
    WHERE customer_id = p_customer_id;
    RETURN v_total;
END;
$$;
--rollback DROP FUNCTION IF EXISTS fn_customer_total(INT);
```

**Step 3:** Include `module03.yaml` and then `module03_routines.sql` in the master, and deploy:
```bash
liquibase validate
liquibase update-sql
liquibase update
```
Check the results in SQL: `SELECT * FROM v_product_catalog;` and `SELECT fn_customer_total(1);`

**Step 4: See `runOnChange`.** Edit the function: change `COALESCE(SUM(amount), 0)` to `ROUND(COALESCE(SUM(amount), 0), 2)`. Run `liquibase update`, then check the `exectype` of `m3-fn-1` in `databasechangelog`.

**Step 5 (optional):** Remove `splitStatements:false` from a **copy** of the function in a scratch file and run `update-sql`. Look at how it gets split.

---

## 3. Quiz
Answer under `module-03` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** Which change type has an automatic rollback?
- A) `dropColumn`
- B) `modifyDataType`
- C) `sql`
- D) `addColumn`

**q2.** You deploy a PL/pgSQL function **without** `splitStatements:false`. What happens?
- A) Liquibase splits the body on `;`, PostgreSQL gets broken pieces, and the changeset fails
- B) It works the same
- C) The function is created twice
- D) The changeset is skipped

**q3.** The business maintains a `country_codes` CSV and edits it every few months. What fits best?
- A) `loadData`
- B) `insert` statements
- C) `loadUpdateData` with `primaryKey` + `runOnChange: true`
- D) `sqlFile`

**q4.** Why is `runOnChange:true` on a `CREATE TABLE` changeset a bad idea?
- A) Liquibase ignores it on tables
- B) Any edit re-runs `CREATE TABLE`, which fails with "already exists"
- C) The table is recreated and keeps its data
- D) It disables checksums

**q5.** After a `runOnChange` changeset is edited and redeployed, what `exectype` does it show?
- A) EXECUTED
- B) MARK_RAN
- C) UPDATED
- D) RERAN

---

## 4. Check your work
```bash
docker compose run --rm grader --module 03
```
Answers & explanations: [solutions/module-03.md](../../solutions/module-03.md)
