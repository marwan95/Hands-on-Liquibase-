# Getting started

## 1. Prerequisites

| You need | Why | Notes |
|---|---|---|
| **Git** | Clone the course | https://git-scm.com/downloads |
| **Docker Desktop** (or Docker Engine + Compose v2) | Runs PostgreSQL 18, Oracle Free 23, CloudBeaver, the Liquibase CLI and the grader | **Windows:** needs WSL2 (`wsl --install`, then restart) and virtualization enabled in the BIOS. Give Docker at least **4 GB RAM**; Oracle is the heavy one. About **5 GB** of disk for the images. |
| **A SQL client** | Look inside the databases | pgAdmin, DBeaver, SQL Developer, or the included **CloudBeaver** (browser-based) |
| **An editor** | Write changelogs | VS Code with the *YAML* and *XML* extensions works well |
| **Basic SQL** | `CREATE TABLE`, `ALTER TABLE`, `INSERT`, `SELECT` | No Liquibase experience needed |

Check them:
```bash
git --version
docker --version
docker compose version
```

## 2. Get the course
```bash
git clone https://github.com/marwan95/Hands-on-Liquibase-.git
cd Hands-on-Liquibase-
```
> Tip: work on your own branch (`git switch -c my-work`) so you can always compare against `main` or start over.

## 3. Start the lab
```bash
docker compose up -d
docker compose ps
```
Wait until both containers show **(healthy)**. PostgreSQL takes a few seconds; Oracle takes **1–3 minutes** on the very first start (it downloads about 1 GB).

| Service | From your machine | Inside Docker | Credentials |
|---|---|---|---|
| PostgreSQL 18, database `lab` | `localhost:5433` | `postgres:5432` | `postgres` / `postgres` |
| PostgreSQL, `legacy_dwh` & `legacy_dwh_ci` (Module 09) | `localhost:5433` | `postgres:5432` | `postgres` / `postgres` |
| Oracle Free 23, service `FREEPDB1` | `localhost:1521` | `oracle:1521` | `lb_lab` / `lb_lab` (SYSTEM: `oracle`) |
| CloudBeaver (optional) | http://localhost:8978 | – | you create the admin user on first start |

- PostgreSQL uses port **5433** on purpose, so it doesn't clash with a PostgreSQL you may already run on 5432.
- If a port is taken, copy `.env.example` to `.env` and change it (and the matching `lab/*.properties`).
- CloudBeaver: `docker compose --profile tools up -d`. When adding connections inside CloudBeaver, use the **"Inside Docker"** host names.

## 4. Install Liquibase. Choose ONE option

### Option A: Local install (recommended: it's what you'll use at work)
| OS | How |
|---|---|
| **Windows** | Run the installer [`liquibase-windows-x64-installer-5.0.4.exe`](https://github.com/liquibase/liquibase/releases/download/v5.0.4/liquibase-windows-x64-installer-5.0.4.exe). It includes Java and adds Liquibase to your PATH. Open a **new** terminal afterwards. |
| **macOS** | `brew install liquibase` |
| **Linux** | Download [`liquibase-5.0.4.tar.gz`](https://github.com/liquibase/liquibase/releases/download/v5.0.4/liquibase-5.0.4.tar.gz), extract it (e.g. to `~/liquibase`) and add that folder to your `PATH`. Needs **Java 17+** (`java -version`). |

All downloads: https://github.com/liquibase/liquibase/releases/tag/v5.0.4 · https://www.liquibase.com/download

Check it:
```bash
liquibase --version          # Liquibase Version: 5.x
```
The local install includes the **PostgreSQL** driver. For **Oracle** (Module 08), run once inside `lab/`:
```bash
cd lab
lpm add oracle-ojdbc11       # installs into lab/liquibase_libs/ (ignored by git)
```
With a local install, **run every Liquibase command inside the `lab/` folder**: that's where `liquibase.properties` lives.

### Option B: Docker only (nothing to install)
Build the image once (it adds the PostgreSQL and Oracle drivers to the official `liquibase/liquibase:5.0.4` image):
```bash
docker compose --profile cli build
```
Then, **from the repository root**, replace `liquibase` in any course command with:

| Local command (in `lab/`) | Docker command (repo root) |
|---|---|
| `liquibase <cmd>` | `docker compose run --rm liquibase <cmd>` |
| `liquibase --defaults-file=liquibase-oracle.properties <cmd>` | `docker compose run --rm liquibase-oracle <cmd>` |
| `liquibase --defaults-file=legacy.properties <cmd>` | `docker compose run --rm liquibase-legacy <cmd>` |
| `liquibase --defaults-file=legacy-ci.properties <cmd>` | `docker compose run --rm liquibase-legacy-ci <cmd>` |

The containers work on your `lab/` folder, so files you create (e.g. with `generate-changelog`) appear there.

> **Windows + Git Bash:** Git Bash rewrites paths that start with `/`. Prefer PowerShell, or run `export MSYS_NO_PATHCONV=1` first.

## 5. First check
```bash
cd lab
liquibase status --verbose                 # or: docker compose run --rm liquibase status --verbose
```
Expected: `... is up to date`. You're ready for [Module 00](../modules/00-setup-and-concepts/README.md).

## 6. Grading
```bash
docker compose run --rm grader                  # everything
docker compose run --rm grader --module 03      # one module
```
The first run builds the grader image. Details: [grading/README.md](../grading/README.md).

## 7. Start over / clean up
```bash
docker compose down        # stop (keeps your data)
docker compose down -v     # stop and DELETE all lab data: next 'up' starts from scratch
git restore lab/           # put the lab files back to the original state (careful: loses your work)
```

## Troubleshooting
| Symptom | Fix |
|---|---|
| `connection refused` on 5433 / 1521 | `docker compose ps`: are the containers healthy? Is another program using the port? |
| `ORA-12564: TNS:connection refused` | Make sure `liquibase-oracle.properties` still has `driver-properties-file=oracle-driver.properties` (it works around a client-info bug in the newest Oracle driver). |
| `Driver class was not specified ... oracle` | Local install: run `lpm add oracle-ojdbc11` inside `lab/`. |
| `Unexpected argument(s)` | Global options (`--defaults-file`, `--log-level`) go **before** the command; command options (`--url`, `--context-filter`) and `-D` go **after** it. |
| `password authentication failed` | An environment variable such as `LIQUIBASE_COMMAND_PASSWORD` overrides the properties file. Remove it. |
| Oracle never becomes healthy | Give Docker more memory (4 GB+). Check `docker logs hol-oracle`. |
