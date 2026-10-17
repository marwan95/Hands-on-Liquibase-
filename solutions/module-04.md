# Module 04 – Solutions

## Hands-on
Reference: [module04.yaml](lab/changelog/module04.yaml).

- **Step 1:** `tag v1.0` writes the tag on the **last** row of `databasechangelog` (the most recently executed changeset).
- **Step 4:** `rollback-sql --tag=v1.0` fails: `m4-2` (`dropColumn`) has no inverse. The fix:
  ```yaml
      rollback:
        - addColumn:
            tableName: suppliers
            columns:
              - column:
                  name: is_active
                  type: BOOLEAN
                  defaultValueBoolean: true
  ```
  `liquibase validate` still passes: **the rollback is not part of the checksum**.
- **Step 5:** the preview lists `m4-2`'s rollback (`ADD is_active`) first, then `m4-1`'s (`DROP COLUMN loyalty_points`): **newest first**. After the rollback, the m4 rows are deleted from `databasechangelog`.
- **"Desert Foods"** is now `true`, like every supplier. The rollback restored the **column**, but the original values were destroyed by the drop. **A rollback restores structure, not data.** Protect data before destructive changes:
  - a backup changeset (`CREATE TABLE suppliers_bkp AS SELECT * FROM suppliers;`)
  - or a soft drop (rename the column)
  - or 2 releases (stop using it now, drop it later)
- **Step 6:** `v1.1` disappeared with the rolled-back row, so you re-tag after redeploying.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **A** | Preview and review first. `rollback-count` runs immediately, and the number is easy to get wrong. Prefer tags in production. |
| q2 | **C** | The rollback isn't part of the checksum, so fixing a broken rollback is safe. |
| q3 | **B** | The data is gone; the column comes back with its default. |
| q4 | **D** | `future-rollback-sql` = the undo plan for what you're **about to** deploy. Review it with the release. |
| q5 | **B** | Tags live on rows. Roll back past a tag, and the tag is gone. |

**Extra:** rollback SQL is never executed during `update`, so a wrong rollback stays hidden until you need it. `liquibase update-testing-rollback` (update → rollback → update) catches it. Run it in CI (Module 10).
