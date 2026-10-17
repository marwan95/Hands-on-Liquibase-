# Hands-on Liquibase for Data Engineers

A practical, self-paced Liquibase course. You learn by **doing**: every module has a short lesson, hands-on tasks on real **PostgreSQL** and **Oracle** databases (in Docker), a quiz, and an **automatic grader** that checks your work.

- 🐳 **Starts right away:** one `docker compose up -d` gives you PostgreSQL 18, Oracle Free 23, a ready-made "legacy" warehouse, and optional CloudBeaver
- 🧪 **Hands-on first:** you write the changelogs and break and fix things on purpose
- ✅ **Graded:** `docker compose run --rm grader` checks your databases and your quiz answers
- 🔑 **Solutions in a separate section:** [solutions/](solutions/README.md), with explanations for every answer

Built and tested with **Liquibase 5.0.4**.

---

## Quick start
```bash
git clone https://github.com/marwan95/Hands-on-Liquibase-.git
cd Hands-on-Liquibase-
docker compose up -d                 # PostgreSQL + Oracle
cd lab && liquibase status           # or, without installing Liquibase:  docker compose run --rm liquibase status
```
New to this? Read **[Getting started](docs/getting-started.md)** first: prerequisites, installing Liquibase on Windows/macOS/Linux, or using Liquibase through Docker with no install at all.

## Prerequisites (summary)
- **Docker Desktop** (Windows: with WSL2), 4 GB+ RAM for Docker, about 5 GB disk
- **Git** and an editor (VS Code recommended)
- A SQL client: pgAdmin, DBeaver, SQL Developer, or the included CloudBeaver
- **Basic SQL.** No Liquibase experience needed
- **Liquibase 5.x** installed locally *or* the Docker CLI image ([how](docs/getting-started.md#4-install-liquibase-choose-one-option))

---

## Modules
| # | Module | You will learn | Time |
|---|---|---|---|
| 00 | [Setup & core concepts](modules/00-setup-and-concepts/README.md) | Changelogs, changesets, tracking tables, settings priority | 30 min |
| 01 | [First deployment](modules/01-first-deployment/README.md) | Formatted SQL, `status`, `update-sql`, `update`, checksums | 45 min |
| 02 | [Formats & project structure](modules/02-formats-and-structure/README.md) | YAML/XML change types, master changelog, `include`, `logicalFilePath` | 45 min |
| 03 | [Change types](modules/03-change-types/README.md) | Constraints, CSV `loadData`, indexes, views, sequences, functions, `runOnChange` | 60 min |
| 04 | [Rollbacks & tags](modules/04-rollbacks-and-tags/README.md) | `tag`, `rollback`, previews, what rollbacks can't restore | 45 min |
| 05 | [Checksums & run modes](modules/05-checksums-and-run-modes/README.md) | What breaks a checksum, `validCheckSum`, `runAlways` | 40 min |
| 06 | [Preconditions](modules/06-preconditions/README.md) | `MARK_RAN`, `HALT`, data-quality guards | 40 min |
| 07 | [Contexts, labels & parameters](modules/07-contexts-labels-parameters/README.md) | One codebase, many environments, and the "no filter" trap | 40 min |
| 08 | [Oracle & cross-database](modules/08-oracle-cross-database/README.md) | One changelog for PostgreSQL + Oracle with `dbms` | 60–90 min |
| 09 | [Reverse engineering & drift](modules/09-reverse-engineering-and-drift/README.md) | Adopt an existing database, `diff`, `diff-changelog`, `changelog-sync` | 60 min |
| 10 | [Data engineering patterns](modules/10-data-engineering-patterns/README.md) | Reference data in git, `CONCURRENTLY`, expand/contract, CI/CD | 60 min |
| 11 | [Final exam](modules/11-final-exam/README.md) | Practical tasks + 10 scenario questions | 45 min |

Do the modules **in order**: each one builds on the database state from the previous one.

## How each module works
1. Read the **Concepts** section.
2. Do the **Hands-on** steps in the [`lab/`](lab) folder.
3. Answer the **Quiz** in [`my-answers.yaml`](my-answers.yaml).
4. Run the grader: `docker compose run --rm grader --module 03`.
5. Only then compare with the **[solutions](solutions/README.md)**.

## Grading
| | |
|---|---|
| Hands-on checks | Graded from your real databases (1 point each; 2 in the exam) |
| Quiz questions | 65 multiple-choice questions (1 point each) |
| Total | **114 points**. **Pass at 70%**, Very good ≥ 80%, Excellent ≥ 90% |

Your report is saved to `grading/my-report.md`, ready to share with your trainer. More in [grading/README.md](grading/README.md).

---

## Repository layout
```
docker-compose.yml        PostgreSQL 18, Oracle Free 23, CloudBeaver, Liquibase CLI, grader
docker/                   images and the database init scripts (incl. the Module 09 legacy warehouse)
docs/                     getting started, CI template
lab/                      👉 YOUR workspace: properties files, changelog/, CSV data
modules/                  the lessons, hands-on tasks and quizzes
my-answers.yaml           👉 your quiz answers
grading/                  the grader + answer key (hashed)
solutions/                ⚠️ spoilers: explanations + reference lab
```

## Want to go further?
**Liquibase University** has free official courses (fundamentals, CI/CD, best practices, and more):
👉 **https://learn.liquibase.com/plus/catalog**

Other useful links:
- Documentation: https://docs.liquibase.com
- Change types reference: https://docs.liquibase.com/change-types/home.html
- Releases: https://github.com/liquibase/liquibase/releases

## Feedback
Found a mistake or have an idea for a module? Open an issue or a pull request.
