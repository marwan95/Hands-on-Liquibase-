# Final exam – Solutions

## Part A
Reference: [exam.sql](lab/changelog/exam.sql).

```sql
--changeset yourname:exam-1 dbms:postgresql
CREATE TABLE exam_employees (
    emp_id       SERIAL PRIMARY KEY,
    emp_name     VARCHAR(100) NOT NULL,
    salary       NUMERIC(10,2)
);
--rollback DROP TABLE exam_employees;

--changeset yourname:exam-2 dbms:postgresql
--preconditions onFail:MARK_RAN
--precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'exam_employees' AND column_name = 'department'
ALTER TABLE exam_employees ADD COLUMN department VARCHAR(50);
--rollback ALTER TABLE exam_employees DROP COLUMN department;

--changeset yourname:exam-3 context:dev dbms:postgresql
INSERT INTO exam_employees (emp_name, salary, department) VALUES ('Test Employee A', 1500.00, 'IT');
INSERT INTO exam_employees (emp_name, salary, department) VALUES ('Test Employee B', 2200.00, 'Finance');
--rollback DELETE FROM exam_employees WHERE emp_name LIKE 'Test Employee%';

--changeset yourname:exam-4 runOnChange:true dbms:postgresql
CREATE OR REPLACE VIEW v_exam_payroll AS
SELECT emp_name, salary, department
FROM exam_employees;
--rollback DROP VIEW v_exam_payroll;
```

Commands:
```bash
liquibase tag before-exam                         # A1
liquibase update                                  # A1-A3 (context-filter=prod from the properties file)
liquibase status --verbose --context-filter=dev   # A3: exam-3 is pending
liquibase history                                 # A4
liquibase rollback-sql --tag=before-exam          # A4: preview (exam-4 → exam-2 → exam-1, newest first)
liquibase rollback --tag=before-exam
liquibase update
# A5: add department to the view, then
liquibase update                                  # exam-4 → RERAN
```
Common mistakes: Oracle types on PostgreSQL (`VARCHAR2`), a trailing comma before `)`, forgetting `dbms:postgresql`, and running A4 without a preview.
Note: `status --context-filter=prod` **hides** `exam-3`, so use `--context-filter=dev` (or no filter) to see it pending.

## Part B
| Q | Answer | Why |
|---|---|---|
| q1 | **D** | Revert the accidental edit first. `clear-checksums` / `ANY` hide the problem; deleting tracking rows makes Liquibase re-run the changeset. |
| q2 | **A** | The crashed run left `LOCKED = true`. Check `LOCKEDBY`/`LOCKGRANTED`, make sure nothing is running, then `release-locks`. |
| q3 | **B** | Read-only commands. The others change schema/data, or the tracking tables. |
| q4 | **C** | Re-run only when the definition changes. |
| q5 | **D** | Portable change types, or `dbms` twins. |
| q6 | **A** | Present in production, absent from code-built CI → hand-made drift. Capture it with `diff-changelog`. |
| q7 | **B** | Structure only. Back up first, soft-drop, or use 2 releases. |
| q8 | **C** | Global options go before the command; command options and `-D` go after. |
| q9 | **D** | Failed changesets aren't recorded, so fix and re-run. (Changesets that succeeded before it in the same `update` stay recorded.) |
| q10 | **A** | Validate, review, bookmark, then deploy with an explicit context filter. |
