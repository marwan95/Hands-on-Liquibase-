# Module 03 – Solutions

## Hands-on
Reference: [module03.yaml](lab/changelog/module03.yaml) and [module03_routines.sql](lab/changelog/module03_routines.sql).

The TODOs:
```yaml
  - changeSet:
      id: m3-4
      author: yourname
      changes:
        - loadData:
            tableName: products
            file: data/products.csv
            relativeToChangelogFile: true
            columns:
              - column: { name: price, type: NUMERIC }
              - column: { name: supplier_id, type: NUMERIC }
      rollback:
        - delete:
            tableName: products

  - changeSet:
      id: m3-5
      author: yourname
      changes:
        - createIndex:
            indexName: idx_orders_order_date
            tableName: orders
            columns:
              - column: { name: order_date }

  - changeSet:
      id: m3-6
      author: yourname
      changes:
        - createView:
            viewName: v_product_catalog
            replaceIfExists: true
            selectQuery: >
              SELECT p.product_id, p.name, p.price, s.supplier_name, s.country
              FROM products p LEFT JOIN suppliers s ON s.supplier_id = p.supplier_id

  - changeSet:
      id: m3-7
      author: yourname
      changes:
        - createSequence:
            sequenceName: seq_invoice_no
            startValue: 1000
            incrementBy: 1
```
- `loadData` has no automatic rollback, so write one (`delete`).
- **Step 4:** after editing the function, `m3-fn-1` shows `exectype = RERAN`, and its `orderexecuted` jumps, because the existing row is updated rather than duplicated.
- **Step 5:** without `splitStatements:false`, `update-sql` shows the function cut into pieces at each `;`. PostgreSQL would reject them (typically "unterminated dollar-quoted string").

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **D** | `addColumn` → its inverse is `dropColumn`. `dropColumn`/`modifyDataType` lose information, and `sql` is opaque. |
| q2 | **A** | Liquibase splits on `;` by default. Functions, procedures, triggers, `DO` blocks and PL/SQL need `splitStatements:false`. |
| q3 | **C** | `loadUpdateData` upserts by `primaryKey`; `runOnChange` re-applies it on every CSV edit. `loadData` would fail on duplicate keys (Module 10). |
| q4 | **B** | Tables can't be "replaced". Evolve them with new changesets. |
| q5 | **D** | `RERAN`. |
