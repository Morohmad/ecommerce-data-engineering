-- ============================================================
-- PHASE 2
-- CLEAN STAGING TABLES
-- ============================================================


-- ============================================================
-- PRODUCTS
-- ============================================================

CREATE TABLE IF NOT EXISTS stg_products_clean (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    description TEXT,
    category TEXT,
    price NUMERIC(12, 2),
    discount_percentage NUMERIC(5, 2),
    rating NUMERIC(4, 2),
    stock INTEGER,
    brand TEXT,
    sku TEXT,
    weight NUMERIC(10, 2),
    width NUMERIC(10, 2),
    height NUMERIC(10, 2),
    depth NUMERIC(10, 2),
    warranty_information TEXT,
    shipping_information TEXT,
    availability_status TEXT,
    return_policy TEXT,
    minimum_order_quantity INTEGER,
    thumbnail TEXT
);


-- ============================================================
-- USERS
-- ============================================================

CREATE TABLE IF NOT EXISTS stg_users_clean (
    user_id INTEGER PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    maiden_name TEXT,
    age INTEGER,
    gender TEXT,
    email TEXT,
    phone TEXT,
    username TEXT,
    birth_date DATE,
    image TEXT,
    blood_group TEXT,
    height NUMERIC(10, 2),
    weight NUMERIC(10, 2),
    eye_color TEXT,
    hair_color TEXT,
    hair_type TEXT,
    ip_address TEXT,
    address TEXT,
    city TEXT,
    state TEXT,
    state_code TEXT,
    postal_code TEXT,
    country TEXT,
    mac_address TEXT,
    university TEXT,
    user_agent TEXT,
    crypto_coin TEXT,
    crypto_wallet TEXT,
    crypto_network TEXT
);


-- ============================================================
-- CARTS
-- ============================================================

CREATE TABLE IF NOT EXISTS stg_carts_clean (
    cart_id INTEGER PRIMARY KEY,
    user_id INTEGER,
    total NUMERIC(14, 2),
    discounted_total NUMERIC(14, 2),
    total_products INTEGER,
    total_quantity INTEGER,
    source_extracted_at TIMESTAMP WITH TIME ZONE
);


-- ============================================================
-- CART ITEMS
-- ============================================================

CREATE TABLE IF NOT EXISTS stg_cart_items_clean (
    cart_id INTEGER,
    product_id INTEGER,
    product_name TEXT,
    price NUMERIC(12, 2),
    quantity INTEGER,
    total NUMERIC(14, 2),
    discount_percentage NUMERIC(5, 2),
    discounted_total NUMERIC(14, 2),
    thumbnail TEXT,

    PRIMARY KEY (
        cart_id,
        product_id
    )
);