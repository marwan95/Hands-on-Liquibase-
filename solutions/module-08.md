# Module 08 – Solutions

## Hands-on
Reference: every `*.sql` file in [lab/changelog](lab/changelog). Look for `dbms:postgresql` and the `-ora` twins. Settings: [liquibase-oracle.properties](lab/liquibase-oracle.properties).

What you should have seen:
- **Step 2:** `suppliers` (YAML) is generated as valid Oracle SQL with an identity column; `customers` (raw SQL with `SERIAL`) is sent as written and is invalid on Oracle.
- **Step 5:** PostgreSQL validates; nothing new is pending except the `runAlways` `m5-2`. The `-ora` changesets never appear on PostgreSQL.
- **Step 6, the non-syntax error:** `ORA-01408: such column list already indexed` on `m5-3`. `email` is `UNIQUE`, Oracle has already indexed it, and Oracle forbids a second index on the same columns. **Fix:** `--changeset yourname:m5-3 dbms:postgresql`.
  - ⚠️ Don't explain it with a `--` comment **inside** `m5-3`: that changes its checksum on PostgreSQL (Module 05). Put the explanation in your git commit message.
- After a failure, the successful changesets stay recorded, and the next `update` continues where it stopped.
- `update` summary on Oracle: a few changesets filtered by **DBMS mismatch** (the PostgreSQL-only ones) and 1 by **context mismatch** (`m7-2`).

Example twin:
```sql
--changeset yourname:5 dbms:postgresql
ALTER TABLE customers ALTER COLUMN full_name TYPE VARCHAR(200);
--rollback ALTER TABLE customers ALTER COLUMN full_name TYPE VARCHAR(100);

--changeset yourname:5-ora dbms:oracle
ALTER TABLE customers MODIFY full_name VARCHAR2(200);
--rollback ALTER TABLE customers MODIFY full_name VARCHAR2(100);
```

**Troubleshooting `ORA-12564: TNS:connection refused`:** the newest Oracle JDBC driver sends an empty client-info block that the Oracle Free listener rejects. The lab's `oracle-driver.properties` (loaded through `driver-properties-file=`) fixes it. Debugging path: the error message → test from inside the container → the **listener log** (`docker exec hol-oracle bash -c 'tail -20 $(find /opt/oracle/diag/tnslsnr -name listener.log)'`).

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **C** | Change types are translated for each database; raw SQL isn't. |
| q2 | **A** | Filtered out silently ("DBMS mismatch"), so it doesn't even show as pending. |
| q3 | **D** | Header attributes aren't part of the checksum. |
| q4 | **B** | Valid SQL ≠ the same behaviour. Oracle auto-indexes unique constraints. |
| q5 | **C** | The body contains `;`, and the statement ends with the `/` line. |
