--liquibase formatted sql

-- splitStatements:false -> the body contains ';' so it must not be split
-- runOnChange:true      -> redeployed automatically every time you edit it
-- (Module 03 task: deploy it, then edit it once - ROUND(...) was the edit)

--changeset student:m3-fn-1 dbms:postgresql splitStatements:false runOnChange:true
CREATE OR REPLACE FUNCTION fn_customer_total(p_customer_id INT)
RETURNS NUMERIC
LANGUAGE plpgsql
AS $$
DECLARE
    v_total NUMERIC;
BEGIN
    SELECT ROUND(COALESCE(SUM(amount), 0), 2) INTO v_total
    FROM orders
    WHERE customer_id = p_customer_id;
    RETURN v_total;
END;
$$;
--rollback DROP FUNCTION IF EXISTS fn_customer_total(INT);

--changeset student:m3-fn-1-ora dbms:oracle splitStatements:false runOnChange:true endDelimiter:/
CREATE OR REPLACE FUNCTION fn_customer_total(p_customer_id IN NUMBER)
RETURN NUMBER
IS
    v_total NUMBER;
BEGIN
    SELECT ROUND(NVL(SUM(amount), 0), 2) INTO v_total
    FROM orders
    WHERE customer_id = p_customer_id;
    RETURN v_total;
END;
/
--rollback DROP FUNCTION fn_customer_total;
