# Module 00 – Solutions

## Hands-on
- `liquibase status` against an empty master says *up to date*. Even this first command creates **DATABASECHANGELOGLOCK** (and DATABASECHANGELOG), because Liquibase prepares its tracking tables whenever it connects to deploy or check.
- `SELECT * FROM databasechangeloglock;` shows one row with `locked = false`. If you query it *through* Liquibase (`liquibase execute-sql`), you may see `locked = true`: your own command holds the lock while it runs. That's normal.

## Quiz
| Q | Answer | Why |
|---|---|---|
| q1 | **C** | Identity = `id` + `author` + file path. That's why moving a file matters (Module 02). |
| q2 | **A** | Every changeset is already recorded and its checksum still matches, so nothing runs. A *changed* checksum would make it **fail**, not re-run. |
| q3 | **D** | DATABASECHANGELOGLOCK. If a crash leaves it locked: `list-locks`, check nothing is really running, then `release-locks`. |
| q4 | **B** | Environment variables beat the properties file. Remove a stale one (`unset` / `Remove-Item Env:...`). |
| q5 | **C** | The checksum (`md5sum` column, e.g. `9:4240…`). |
