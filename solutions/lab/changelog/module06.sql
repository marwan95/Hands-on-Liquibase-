--liquibase formatted sql

--changeset student:m6-1 dbms:postgresql
--preconditions onFail:MARK_RAN
--precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM pg_indexes WHERE indexname = 'idx_orders_amount'
CREATE INDEX idx_orders_amount ON orders(amount);
--rollback DROP INDEX idx_orders_amount;

--changeset student:m6-1-ora dbms:oracle
--preconditions onFail:MARK_RAN
--precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM user_indexes WHERE index_name = 'IDX_ORDERS_AMOUNT'
CREATE INDEX idx_orders_amount ON orders(amount);
--rollback DROP INDEX idx_orders_amount;

--changeset student:m6-2
--preconditions onFail:HALT onFailMessage:"Negative amounts found - clean the data before deploying"
--precondition-sql-check expectedResult:0 SELECT COUNT(*) FROM orders WHERE amount < 0
ALTER TABLE orders ADD CONSTRAINT chk_orders_amount_positive CHECK (amount >= 0);
--rollback ALTER TABLE orders DROP CONSTRAINT chk_orders_amount_positive;
