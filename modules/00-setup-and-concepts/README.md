# Module 00 – Setup & core concepts

**Goal:** get the lab running and understand the 5 ideas that everything else builds on.
**Time:** ~30 min

---

## 1. Concepts

**The problem:** a database schema changes over time, and every environment (dev, test, prod) must receive the same changes, in the same order, exactly once. Liquibase is version control for your database.

| Term | Meaning |
|---|---|
| **Changelog** | A file (SQL, YAML, XML or JSON) listing every database change in order. The single source of truth. |
| **Changeset** | One unit of change inside a changelog. Identified by **`id` + `author` + file path**. Runs **once**. |
| **DATABASECHANGELOG** | A table Liquibase creates in your database: one row per changeset that already ran, with a **checksum** (fingerprint) of its content. |
| **DATABASECHANGELOGLOCK** | A one-row table that stops two Liquibase runs from deploying at the same time. |
| **liquibase.properties** | Connection settings + changelog path, read automatically from the current folder. |

How `liquibase update` works:
```
take the lock → read the changelog → for each changeset:
    already in DATABASECHANGELOG?  → same checksum? skip : ERROR (someone edited it)
    not there?                     → run it, then insert a tracking row
→ release the lock
```

**Where settings come from (highest priority first):**
command-line flags → Java system properties → environment variables (`LIQUIBASE_COMMAND_PASSWORD`, ...) → `liquibase.properties`

---

## 2. Hands-on

> Complete [Getting started](../../docs/getting-started.md) first: Docker running, repository cloned, Liquibase installed (or using the Docker CLI).

**Step 1: Start the databases** (from the repository root):
```bash
docker compose up -d
docker compose ps        # wait until postgres shows (healthy); Oracle takes 1-3 minutes on first start
```

**Step 2: Look at the lab folder.** Everything you build lives in [`lab/`](../../lab):
```
lab/
  liquibase.properties          PostgreSQL connection (localhost:5433, database "lab")
  liquibase-oracle.properties   Oracle connection (Module 08)
  changelog/
    db.changelog-master.yaml    the master changelog - currently empty
    data/*.csv                  data you will load later
```

**Step 3: Your first Liquibase command:**
```bash
cd lab
liquibase status --verbose
```
<details><summary>Using Docker instead of a local install?</summary>

From the **repository root**, replace `liquibase` with `docker compose run --rm liquibase`:
```bash
docker compose run --rm liquibase status --verbose
```
This works for every command in the course. Oracle: `docker compose run --rm liquibase-oracle <command>`.
</details>

Expected output: `... is up to date`. The master changelog is empty, so there's nothing to deploy yet.

**Step 4: Look inside the database.** Connect with pgAdmin, DBeaver, or CloudBeaver (`docker compose --profile tools up -d` → http://localhost:8978):
- Host `localhost`, port **5433**, database `lab`, user `postgres`, password `postgres`

Find the 2 tables Liquibase just created and run:
```sql
SELECT * FROM databasechangeloglock;
```

**Step 5: Put your name in [`my-answers.yaml`](../../my-answers.yaml)** (the `learner:` line).

---

## 3. Quiz
Write your answers (A/B/C/D) under `module-00` in [`my-answers.yaml`](../../my-answers.yaml).

**q1.** What uniquely identifies a changeset?
- A) Its `id` only
- B) Its checksum
- C) `id` + `author` + file path
- D) `id` + `author`

**q2.** You run `liquibase update` twice in a row without changing anything. What happens the second time?
- A) Nothing runs: every changeset is already recorded and its checksum still matches
- B) Every changeset runs again
- C) It fails with duplicate-key errors
- D) Liquibase drops and recreates the objects

**q3.** Which table stops two deployments from running at the same time?
- A) DATABASECHANGELOG
- B) pg_locks
- C) liquibase.properties
- D) DATABASECHANGELOGLOCK

**q4.** `LIQUIBASE_COMMAND_PASSWORD` is set to a wrong value, and `liquibase.properties` has the right password. Which one does Liquibase use?
- A) The properties file, because it's more specific
- B) The environment variable, because it has higher priority
- C) Neither: it asks interactively
- D) Whichever was changed most recently

**q5.** What does DATABASECHANGELOG store so that Liquibase can detect an edited changeset?
- A) The full SQL text
- B) The file size
- C) A checksum (MD5) of the changeset
- D) The git commit hash

---

## 4. Check your work
```bash
docker compose run --rm grader --module 00
```
Answers & explanations: [solutions/module-00.md](../../solutions/module-00.md). Try the quiz first!
