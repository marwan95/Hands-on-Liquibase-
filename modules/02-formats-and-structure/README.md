# Module 02 – Changelog formats & project structure

**Goal:** write changesets in YAML and XML, organise files with a master changelog, and understand why the file path matters.
**Time:** ~45 min

---

## 1. Concepts

### The master changelog
Real projects never keep everything in one file. The master only **includes** other files, in order:
```yaml
databaseChangeLog:
  - include: { file: module01.sql, relativeToChangelogFile: true }
  - include: { file: module02.yaml, relativeToChangelogFile: true }
```
| | `include` | `includeAll` (a folder) |
|---|---|---|
| Order | Exactly as written | **Alphabetical**: `10_x` runs before `2_x`, so zero-pad names (`002_`, `010_`) |
| Recommended | ✅ Explicit and reviewable | Only for folders of many similar scripts |

### The formats
| Format | Style | Automatic rollback | Works on any database |
|---|---|---|---|
| **Formatted SQL** | You write raw SQL | ❌ Write `--rollback` | ❌ Tied to one SQL dialect |
| **YAML / XML / JSON** | You describe the change with *change types* (`createTable`, `addColumn`, ...) | ✅ For most change types | ✅ Liquibase generates the SQL for each database |

You can **mix** formats in one project: YAML for tables, SQL for procedures and database-specific features.

### ⚠️ The file path is part of the identity
Changeset identity = `id + author + path`. If you **move or rename** a file, Liquibase sees "new" changesets and tries to create everything again → `relation already exists`. To prevent it, give the file a fixed logical path:
```sql
--liquibase formatted sql logicalFilePath:changelog/module01.sql
```
(YAML/XML: `logicalFilePath` on `databaseChangeLog` or on a `changeSet`.)

---

## 2. Hands-on

**Step 1: YAML.** Create `lab/changelog/module02.yaml`:
```yaml
databaseChangeLog:
  - changeSet:
      id: m2-1
      author: yourname
      changes:
        - createTable:
            tableName: suppliers
            columns:
              - column:
                  name: supplier_id
                  type: INT
                  autoIncrement: true
                  constraints: { primaryKey: true, nullable: false }
              - column:
                  name: supplier_name
                  type: VARCHAR(100)
                  constraints: { nullable: false }
              - column: { name: country, type: VARCHAR(50) }
              - column: { name: is_active, type: BOOLEAN, defaultValueBoolean: true }
      # no rollback block: Liquibase knows the inverse of createTable
```
Add it to the master **after** `module01.sql`, then:
```bash
liquibase validate        # checks syntax without touching the database - use it often
liquibase update-sql      # what did INT + autoIncrement become on PostgreSQL?
liquibase update
```

**Step 2: XML. Write it yourself.** Create `lab/changelog/module02.xml` with one changeset `m2x-1` that creates the table `warehouses`:
- `warehouse_id`: INT, auto increment, primary key
- `city`: **VARCHAR(80)**, not null
- `capacity`: INT

Use this skeleton:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<databaseChangeLog
    xmlns="http://www.liquibase.org/xml/ns/dbchangelog"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.liquibase.org/xml/ns/dbchangelog
        http://www.liquibase.org/xml/ns/dbchangelog/dbchangelog-latest.xsd">

    <changeSet id="m2x-1" author="yourname">
        <createTable tableName="...">
            <column name="..." type="...">
                <constraints primaryKey="true" nullable="false"/>
            </column>
        </createTable>
    </changeSet>
</databaseChangeLog>
```
Include it after `module02.yaml` and deploy it.

**Step 3: Widen `full_name` the correct way.** In `module01.sql`, add changeset `yourname:5` that changes `customers.full_name` to `VARCHAR(200)`. Its rollback must restore the **previous** size. Deploy it.

**Step 4:** Look at the `filename` column of `databasechangelog`. Note that every row stores its file path.

---

## 3. Quiz
Answer under `module-02` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** In what order does `includeAll` run `1_init.sql`, `2_tables.sql` and `10_indexes.sql`?
- A) 1_init → 2_tables → 10_indexes
- B) In the order the files were created
- C) 1_init → 10_indexes → 2_tables (alphabetical)
- D) Randomly

**q2.** Why doesn't a YAML `createTable` changeset need a rollback block?
- A) Liquibase knows the inverse of the change type (`DROP TABLE`)
- B) YAML changesets can never be rolled back
- C) The rollback is stored in DATABASECHANGELOG
- D) PostgreSQL rolls it back automatically

**q3.** A teammate moves `module01.sql` into a new `v1/` folder and runs `update`. What happens?
- A) Nothing: Liquibase follows the file
- B) A checksum error
- C) Liquibase moves the tracking rows automatically
- D) The changesets look new, so Liquibase tries to create the tables again → "already exists" errors

**q4.** Which attribute prevents the problem in q3?
- A) `runOnChange`
- B) `logicalFilePath`
- C) `validCheckSum`
- D) `context`

**q5.** What's the main advantage of change types (YAML/XML) over raw SQL?
- A) They run faster
- B) They support stored procedures better
- C) Database-independent SQL generation and automatic rollback
- D) The files are smaller

---

## 4. Check your work
```bash
docker compose run --rm grader --module 02
```
Answers & explanations: [solutions/module-02.md](../../solutions/module-02.md)
