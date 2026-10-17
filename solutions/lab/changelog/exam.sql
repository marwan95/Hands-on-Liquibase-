--liquibase formatted sql

--changeset student:exam-1 dbms:postgresql
CREATE TABLE exam_employees (
    emp_id       SERIAL PRIMARY KEY,
    emp_name     VARCHAR(100) NOT NULL,
    salary       NUMERIC(10,2)
);
--rollback DROP TABLE exam_employees;

--changeset student:exam-2 dbms:postgresql
--preconditions onFail:MARK_RAN
--precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM information_schema.columns WHERE table_name = 'exam_employees' AND column_name = 'department'
ALTER TABLE exam_employees ADD COLUMN department VARCHAR(50);
--rollback ALTER TABLE exam_employees DROP COLUMN department;

--changeset student:exam-3 context:dev dbms:postgresql
INSERT INTO exam_employees (emp_name, salary, department) VALUES ('Test Employee A', 1500.00, 'IT');
INSERT INTO exam_employees (emp_name, salary, department) VALUES ('Test Employee B', 2200.00, 'Finance');
--rollback DELETE FROM exam_employees WHERE emp_name LIKE 'Test Employee%';

--changeset student:exam-4 runOnChange:true dbms:postgresql
CREATE OR REPLACE VIEW v_exam_payroll AS
SELECT emp_name, salary, department
FROM exam_employees;
--rollback DROP VIEW v_exam_payroll;
