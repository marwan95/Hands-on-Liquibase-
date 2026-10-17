# Grading

The grader checks 2 things:
1. **Hands-on**: it connects to your **real databases** (PostgreSQL `lab`, Oracle, `legacy_dwh`, `legacy_dwh_ci`) and checks the results each module asks for: tables, constraints, tags, `exectype` values, data, and so on.
2. **Quiz**: it compares your letters in [`my-answers.yaml`](../my-answers.yaml) with the answer key.

## Run it
```bash
docker compose run --rm grader                  # full report
docker compose run --rm grader --module 04      # one module (00-10 or exam)
```
The report is printed and also saved to `grading/my-report.md`.

## Scoring
| Item | Points |
|---|---|
| Each hands-on check (modules 00–10) | 1 |
| Each hands-on check (final exam) | 2 |
| Each quiz question | 1 |
| **Total** | **114** |

| Score | Result |
|---|---|
| ≥ 90% | Excellent |
| ≥ 80% | Very good |
| ≥ 70% | **Pass** |
| < 70% | Not yet: keep practising |

- A failed check prints a **hint**. Wrong quiz answers are listed by question number (the correct letter isn't shown), so you can retry.
- Re-run the grader as often as you like.
- Hands-on checks look at the **current** database state. If you reset the lab (`docker compose down -v`), you'll need to redo the modules.

## Sharing your result
Send `grading/my-report.md` to your trainer, or commit it to your branch.

## For maintainers
- The quiz key is stored as **SHA-256 hashes** in `answer_key.json`, so the letters aren't visible at a glance. This prevents accidental spoilers; it isn't anti-cheat (the solutions folder is public by design).
- The source of truth is [`solutions/quiz-answers.yaml`](../solutions/quiz-answers.yaml). After changing a quiz, rebuild the key:
  ```bash
  docker compose run --rm --entrypoint python grader grading/tools/build_answer_key.py
  ```
- Hands-on checks live in `CHECKS` in [`grade.py`](grade.py). The reference solution in [`solutions/lab`](../solutions/lab) was played through module by module on fresh containers and scores 114/114.
