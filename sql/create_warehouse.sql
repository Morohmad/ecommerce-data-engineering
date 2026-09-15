-- ============================================================
-- E-COMMERCE DATA ENGINEERING
-- PHASE 3
-- DATA WAREHOUSE
-- ============================================================


-- ============================================================
-- CREATE WAREHOUSE SCHEMA
-- ============================================================

CREATE SCHEMA IF NOT EXISTS warehouse;


-- ============================================================
-- DIMENSION: DATE
-- ============================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date DATE NOT NULL UNIQUE,

    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    month_name VARCHAR(20) NOT NULL,

    week_of_year INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,
    day_name VARCHAR(20) NOT NULL,

    is_weekend BOOLEAN NOT NULL
);


-- ============================================================
-- DIMENSION: CUSTOMER
-- ============================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_customer (
    customer_key BIGSERIAL PRIMARY KEY,

    customer_id INTEGER NOT NULL UNIQUE,

    first_name TEXT,
    last_name TEXT,
    gender TEXT,

    email TEXT,
    phone TEXT,

    username TEXT,

    age INTEGER,

    city TEXT,
    state TEXT,
    state_code TEXT,
    postal_code TEXT,
    country TEXT,

    university TEXT,

    source_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- DIMENSION: PRODUCT
-- ============================================================

CREATE TABLE IF NOT EXISTS warehouse.dim_product (
    product_key BIGSERIAL PRIMARY KEY,

    product_id INTEGER NOT NULL UNIQUE,

    product_name TEXT NOT NULL,
    category TEXT,
    brand TEXT,
    sku TEXT,

    price NUMERIC(12, 2),

    discount_percentage NUMERIC(5, 2),

    rating NUMERIC(4, 2),

    stock INTEGER,

    weight NUMERIC(10, 2),

    width NUMERIC(10, 2),
    height NUMERIC(10, 2),
    depth NUMERIC(10, 2),

    availability_status TEXT,

    source_updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);


-- ============================================================
-- FACT: SALES
-- ============================================================

CREATE TABLE IF NOT EXISTS warehouse.fact_sales (
    sales_key BIGSERIAL PRIMARY KEY,

    date_key INTEGER NOT NULL,
    customer_key BIGINT NOT NULL,
    product_key BIGINT NOT NULL,

    cart_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,

    quantity INTEGER NOT NULL,

    unit_price NUMERIC(12, 2) NOT NULL,

    gross_amount NUMERIC(14, 2) NOT NULL,

    discount_percentage NUMERIC(5, 2),

    discount_amount NUMERIC(14, 2),

    net_amount NUMERIC(14, 2) NOT NULL,

    loaded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_fact_date
        FOREIGN KEY (date_key)
        REFERENCES warehouse.dim_date(date_key),

    CONSTRAINT fk_fact_customer
        FOREIGN KEY (customer_key)
        REFERENCES warehouse.dim_customer(customer_key),

    CONSTRAINT fk_fact_product
        FOREIGN KEY (product_key)
        REFERENCES warehouse.dim_product(product_key)
);


-- ============================================================
-- INDEXES
-- ============================================================

CREATE INDEX IF NOT EXISTS idx_fact_sales_date
ON warehouse.fact_sales(date_key);


CREATE INDEX IF NOT EXISTS idx_fact_sales_customer
ON warehouse.fact_sales(customer_key);


CREATE INDEX IF NOT EXISTS idx_fact_sales_product
ON warehouse.fact_sales(product_key);


CREATE INDEX IF NOT EXISTS idx_fact_sales_cart
ON warehouse.fact_sales(cart_id);


CREATE INDEX IF NOT EXISTS idx_dim_customer_country
ON warehouse.dim_customer(country);


CREATE INDEX IF NOT EXISTS idx_dim_product_category
ON warehouse.dim_product(category);