-- Module 09: a hand-built "legacy" warehouse that has never used Liquibase.
\connect legacy_dwh

CREATE TABLE dim_customer (
    customer_key   SERIAL PRIMARY KEY,
    customer_name  VARCHAR(100) NOT NULL,
    city           VARCHAR(50),
    segment        VARCHAR(20) DEFAULT 'RETAIL'
);

CREATE TABLE dim_date (
    date_key       INT PRIMARY KEY,
    full_date      DATE NOT NULL,
    month_name     VARCHAR(10),
    year_num       INT
);

CREATE TABLE fact_sales (
    sale_id        BIGSERIAL PRIMARY KEY,
    customer_key   INT NOT NULL REFERENCES dim_customer(customer_key),
    date_key       INT NOT NULL REFERENCES dim_date(date_key),
    quantity       INT NOT NULL,
    net_amount     NUMERIC(14,2) NOT NULL
);

CREATE INDEX ix_fact_sales_date ON fact_sales(date_key);

CREATE VIEW v_sales_by_city AS
SELECT c.city, SUM(f.net_amount) AS total_sales
FROM fact_sales f JOIN dim_customer c ON c.customer_key = f.customer_key
GROUP BY c.city;

INSERT INTO dim_customer (customer_name, city) VALUES ('Ahmed', 'Muscat'), ('Sara', 'Dubai');
INSERT INTO dim_date VALUES (20261017, DATE '2026-10-17', 'October', 2026);
INSERT INTO fact_sales (customer_key, date_key, quantity, net_amount) VALUES (1, 20261017, 3, 150.00), (2, 20261017, 1, 75.50);
