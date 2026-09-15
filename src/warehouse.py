import logging
from datetime import date, datetime, timedelta

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
)


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# ============================================================
# LOAD STAGING DATA
# ============================================================

def load_staging_data(
    connection
):

    products_query = """
        SELECT
            product_id,
            product_name,
            category,
            brand,
            sku,
            price,
            discount_percentage,
            rating,
            stock,
            weight,
            width,
            height,
            depth,
            availability_status
        FROM stg_products_clean
        ORDER BY product_id;
    """

    users_query = """
        SELECT
            user_id,
            first_name,
            last_name,
            gender,
            email,
            phone,
            username,
            age,
            city,
            state,
            state_code,
            postal_code,
            country,
            university
        FROM stg_users_clean
        ORDER BY user_id;
    """

    carts_query = """
        SELECT
            cart_id,
            user_id,
            total,
            discounted_total,
            total_products,
            total_quantity,
            source_extracted_at
        FROM stg_carts_clean
        ORDER BY cart_id;
    """

    cart_items_query = """
        SELECT
            cart_id,
            product_id,
            product_name,
            price,
            quantity,
            total,
            discount_percentage,
            discounted_total
        FROM stg_cart_items_clean
        ORDER BY cart_id, product_id;
    """

    products = pd.read_sql_query(
        products_query,
        connection
    )

    users = pd.read_sql_query(
        users_query,
        connection
    )

    carts = pd.read_sql_query(
        carts_query,
        connection
    )

    cart_items = pd.read_sql_query(
        cart_items_query,
        connection
    )

    logger.info(
        "Loaded staging products: %s rows",
        len(products)
    )

    logger.info(
        "Loaded staging users: %s rows",
        len(users)
    )

    logger.info(
        "Loaded staging carts: %s rows",
        len(carts)
    )

    logger.info(
        "Loaded staging cart items: %s rows",
        len(cart_items)
    )

    return (
        products,
        users,
        carts,
        cart_items,
    )


# ============================================================
# DIM DATE
# ============================================================

def generate_date_dimension(
    carts: pd.DataFrame
) -> pd.DataFrame:

    logger.info(
        "Generating date dimension..."
    )

    if carts.empty:

        raise ValueError(
            "Carts data is empty."
        )

    carts = carts.copy()

    carts["source_extracted_at"] = pd.to_datetime(
        carts["source_extracted_at"],
        errors="coerce",
        utc=True
    )

    min_date = (
        carts["source_extracted_at"]
        .dropna()
        .dt.date
        .min()
    )

    max_date = (
        carts["source_extracted_at"]
        .dropna()
        .dt.date
        .max()
    )

    if pd.isna(min_date) or pd.isna(max_date):

        raise ValueError(
            "No valid transaction dates found."
        )

    date_range = pd.date_range(
        start=min_date,
        end=max_date,
        freq="D"
    )

    rows = []

    for current_date in date_range:

        current = current_date.date()

        rows.append(
            {
                "date_key": int(
                    current.strftime("%Y%m%d")
                ),

                "full_date": current,

                "year": current.year,

                "quarter": (
                    (current.month - 1) // 3
                ) + 1,

                "month": current.month,

                "month_name": current.strftime(
                    "%B"
                ),

                "week_of_year": int(
                    current.strftime("%V")
                ),

                "day_of_month": current.day,

                "day_of_week": current.isoweekday(),

                "day_name": current.strftime(
                    "%A"
                ),

                "is_weekend": (
                    current.weekday() >= 5
                ),
            }
        )

    df = pd.DataFrame(rows)

    logger.info(
        "Generated %s date dimension rows.",
        len(df)
    )

    return df


# ============================================================
# LOAD DIM DATE
# ============================================================

def load_dim_date(
    cursor,
    df: pd.DataFrame
):

    if df.empty:

        raise ValueError(
            "dim_date data is empty."
        )

    rows = [
        tuple(row)
        for row in df.itertuples(
            index=False,
            name=None
        )
    ]

    sql = """
        INSERT INTO warehouse.dim_date (
            date_key,
            full_date,
            year,
            quarter,
            month,
            month_name,
            week_of_year,
            day_of_month,
            day_of_week,
            day_name,
            is_weekend
        )
        VALUES %s
        ON CONFLICT (date_key)
        DO UPDATE SET
            full_date = EXCLUDED.full_date,
            year = EXCLUDED.year,
            quarter = EXCLUDED.quarter,
            month = EXCLUDED.month,
            month_name = EXCLUDED.month_name,
            week_of_year = EXCLUDED.week_of_year,
            day_of_month = EXCLUDED.day_of_month,
            day_of_week = EXCLUDED.day_of_week,
            day_name = EXCLUDED.day_name,
            is_weekend = EXCLUDED.is_weekend;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded dim_date: %s rows",
        len(rows)
    )


# ============================================================
# LOAD DIM CUSTOMER
# ============================================================

def load_dim_customer(
    cursor,
    users: pd.DataFrame
):

    logger.info(
        "Loading dim_customer..."
    )

    if users.empty:

        raise ValueError(
            "Users data is empty."
        )

    users = users.copy()

    users["age"] = pd.to_numeric(
        users["age"],
        errors="coerce"
    )

    users["gender"] = (
        users["gender"]
        .astype("string")
        .str.lower()
        .str.strip()
    )

    users["country"] = (
        users["country"]
        .astype("string")
        .str.lower()
        .str.strip()
    )

    users["city"] = (
        users["city"]
        .astype("string")
        .str.lower()
        .str.strip()
    )

    rows = []

    for row in users.itertuples(
        index=False
    ):

        rows.append(
            (
                row.user_id,
                row.first_name,
                row.last_name,
                row.gender,
                row.email,
                row.phone,
                row.username,
                row.age,
                row.city,
                row.state,
                row.state_code,
                row.postal_code,
                row.country,
                row.university,
            )
        )

    sql = """
        INSERT INTO warehouse.dim_customer (
            customer_id,
            first_name,
            last_name,
            gender,
            email,
            phone,
            username,
            age,
            city,
            state,
            state_code,
            postal_code,
            country,
            university
        )
        VALUES %s
        ON CONFLICT (customer_id)
        DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            gender = EXCLUDED.gender,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            username = EXCLUDED.username,
            age = EXCLUDED.age,
            city = EXCLUDED.city,
            state = EXCLUDED.state,
            state_code = EXCLUDED.state_code,
            postal_code = EXCLUDED.postal_code,
            country = EXCLUDED.country,
            university = EXCLUDED.university,
            source_updated_at = CURRENT_TIMESTAMP;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded dim_customer: %s rows",
        len(rows)
    )


# ============================================================
# LOAD DIM PRODUCT
# ============================================================

def load_dim_product(
    cursor,
    products: pd.DataFrame
):

    logger.info(
        "Loading dim_product..."
    )

    if products.empty:

        raise ValueError(
            "Products data is empty."
        )

    products = products.copy()

    numeric_columns = [
        "product_id",
        "price",
        "discount_percentage",
        "rating",
        "stock",
        "weight",
        "width",
        "height",
        "depth",
    ]

    for column in numeric_columns:

        products[column] = pd.to_numeric(
            products[column],
            errors="coerce"
        )

    products["category"] = (
        products["category"]
        .astype("string")
        .str.lower()
        .str.strip()
    )

    rows = []

    for row in products.itertuples(
        index=False
    ):

        rows.append(
            (
                row.product_id,
                row.product_name,
                row.category,
                row.brand,
                row.sku,
                row.price,
                row.discount_percentage,
                row.rating,
                row.stock,
                row.weight,
                row.width,
                row.height,
                row.depth,
                row.availability_status,
            )
        )

    sql = """
        INSERT INTO warehouse.dim_product (
            product_id,
            product_name,
            category,
            brand,
            sku,
            price,
            discount_percentage,
            rating,
            stock,
            weight,
            width,
            height,
            depth,
            availability_status
        )
        VALUES %s
        ON CONFLICT (product_id)
        DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            brand = EXCLUDED.brand,
            sku = EXCLUDED.sku,
            price = EXCLUDED.price,
            discount_percentage =
                EXCLUDED.discount_percentage,
            rating = EXCLUDED.rating,
            stock = EXCLUDED.stock,
            weight = EXCLUDED.weight,
            width = EXCLUDED.width,
            height = EXCLUDED.height,
            depth = EXCLUDED.depth,
            availability_status =
                EXCLUDED.availability_status,
            source_updated_at = CURRENT_TIMESTAMP;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded dim_product: %s rows",
        len(rows)
    )


# ============================================================
# GET SURROGATE KEYS
# ============================================================

def get_customer_keys(
    cursor
) -> pd.DataFrame:

    query = """
        SELECT
            customer_key,
            customer_id
        FROM warehouse.dim_customer;
    """

    return pd.read_sql_query(
        query,
        cursor.connection
    )


def get_product_keys(
    cursor
) -> pd.DataFrame:

    query = """
        SELECT
            product_key,
            product_id
        FROM warehouse.dim_product;
    """

    return pd.read_sql_query(
        query,
        cursor.connection
    )


# ============================================================
# BUILD FACT SALES
# ============================================================

def build_fact_sales(
    carts: pd.DataFrame,
    cart_items: pd.DataFrame,
    customer_keys: pd.DataFrame,
    product_keys: pd.DataFrame
) -> pd.DataFrame:

    logger.info(
        "Building fact_sales..."
    )

    if carts.empty:

        raise ValueError(
            "Carts data is empty."
        )

    if cart_items.empty:

        raise ValueError(
            "Cart items data is empty."
        )

    # --------------------------------------------------------
    # Prepare cart data
    # --------------------------------------------------------

    carts = carts.copy()

    carts["source_extracted_at"] = pd.to_datetime(
        carts["source_extracted_at"],
        errors="coerce",
        utc=True
    )

    carts["date_key"] = (
        carts["source_extracted_at"]
        .dt.strftime("%Y%m%d")
        .astype("Int64")
    )

    # --------------------------------------------------------
    # Join cart item with cart
    # --------------------------------------------------------

    fact = cart_items.merge(
        carts[
            [
                "cart_id",
                "user_id",
                "date_key",
            ]
        ],
        on="cart_id",
        how="inner",
        validate="many_to_one"
    )

    logger.info(
        "After cart join: %s rows",
        len(fact)
    )

    # --------------------------------------------------------
    # Join customer surrogate key
    # --------------------------------------------------------

    fact = fact.merge(
        customer_keys,
        left_on="user_id",
        right_on="customer_id",
        how="inner",
        validate="many_to_one"
    )

    # --------------------------------------------------------
    # Join product surrogate key
    # --------------------------------------------------------

    fact = fact.merge(
        product_keys,
        on="product_id",
        how="inner",
        validate="many_to_one"
    )

    logger.info(
        "After dimension joins: %s rows",
        len(fact)
    )

    # --------------------------------------------------------
    # Convert numeric
    # --------------------------------------------------------

    numeric_columns = [
        "quantity",
        "price",
        "total",
        "discount_percentage",
        "discounted_total",
        "date_key",
        "customer_key",
        "product_key",
    ]

    for column in numeric_columns:

        fact[column] = pd.to_numeric(
            fact[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Calculate metrics
    # --------------------------------------------------------

    fact["gross_amount"] = (
        fact["price"] *
        fact["quantity"]
    )

    fact["net_amount"] = (
        fact["discounted_total"]
    )

    fact["discount_amount"] = (
        fact["gross_amount"] -
        fact["net_amount"]
    )

    # --------------------------------------------------------
    # Protect against negative discount
    # --------------------------------------------------------

    fact.loc[
        fact["discount_amount"] < 0,
        "discount_amount"
    ] = 0

    # --------------------------------------------------------
    # Round monetary fields
    # --------------------------------------------------------

    monetary_columns = [
        "price",
        "gross_amount",
        "discount_percentage",
        "discount_amount",
        "net_amount",
    ]

    for column in monetary_columns:

        fact[column] = fact[column].round(2)

    # --------------------------------------------------------
    # Select final fact columns
    # --------------------------------------------------------

    fact = fact[
        [
            "date_key",
            "customer_key",
            "product_key",
            "cart_id",
            "product_id",
            "quantity",
            "price",
            "gross_amount",
            "discount_percentage",
            "discount_amount",
            "net_amount",
        ]
    ].copy()

    # --------------------------------------------------------
    # Remove invalid rows
    # --------------------------------------------------------

    fact = fact.dropna(
        subset=[
            "date_key",
            "customer_key",
            "product_key",
            "cart_id",
            "product_id",
            "quantity",
            "price",
            "net_amount",
        ]
    )

    # --------------------------------------------------------
    # Ensure valid quantities
    # --------------------------------------------------------

    fact = fact[
        fact["quantity"] > 0
    ]

    # --------------------------------------------------------
    # Ensure valid prices
    # --------------------------------------------------------

    fact = fact[
        fact["price"] >= 0
    ]

    # --------------------------------------------------------
    # Ensure valid net amount
    # --------------------------------------------------------

    fact = fact[
        fact["net_amount"] >= 0
    ]

    # --------------------------------------------------------
    # Convert integer columns
    # --------------------------------------------------------

    integer_columns = [
        "date_key",
        "customer_key",
        "product_key",
        "cart_id",
        "product_id",
        "quantity",
    ]

    for column in integer_columns:

        fact[column] = (
            fact[column]
            .astype(int)
        )

    # --------------------------------------------------------
    # Remove duplicate fact grain
    # --------------------------------------------------------

    before = len(fact)

    fact = fact.drop_duplicates(
        subset=[
            "cart_id",
            "product_id",
        ]
    )

    after = len(fact)

    logger.info(
        "Fact duplicates removed: %s",
        before - after
    )

    return fact


# ============================================================
# LOAD FACT SALES
# ============================================================

def load_fact_sales(
    cursor,
    fact: pd.DataFrame
):

    logger.info(
        "Loading fact_sales..."
    )

    if fact.empty:

        raise ValueError(
            "fact_sales is empty."
        )

    rows = [
        tuple(row)
        for row in fact.itertuples(
            index=False,
            name=None
        )
    ]

    sql = """
        INSERT INTO warehouse.fact_sales (
            date_key,
            customer_key,
            product_key,
            cart_id,
            product_id,
            quantity,
            unit_price,
            gross_amount,
            discount_percentage,
            discount_amount,
            net_amount
        )
        VALUES %s
        ON CONFLICT DO NOTHING;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded fact_sales: %s rows",
        len(rows)
    )


# ============================================================
# MAIN WAREHOUSE ETL
# ============================================================

def run_warehouse_etl():

    logger.info(
        "========================================"
    )

    logger.info(
        "STARTING PHASE 3 DATA WAREHOUSE ETL"
    )

    logger.info(
        "========================================"
    )

    connection = None

    try:

        connection = get_connection()

        (
            products,
            users,
            carts,
            cart_items,
        ) = load_staging_data(
            connection
        )

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Dimension Date
        # ----------------------------------------------------

        date_dimension = generate_date_dimension(
            carts
        )

        load_dim_date(
            cursor,
            date_dimension
        )

        # ----------------------------------------------------
        # Dimension Customer
        # ----------------------------------------------------

        load_dim_customer(
            cursor,
            users
        )

        # ----------------------------------------------------
        # Dimension Product
        # ----------------------------------------------------

        load_dim_product(
            cursor,
            products
        )

        # ----------------------------------------------------
        # Get surrogate keys
        # ----------------------------------------------------

        customer_keys = get_customer_keys(
            cursor
        )

        product_keys = get_product_keys(
            cursor
        )

        # ----------------------------------------------------
        # Build fact
        # ----------------------------------------------------

        fact_sales = build_fact_sales(
            carts,
            cart_items,
            customer_keys,
            product_keys
        )

        # ----------------------------------------------------
        # Load fact
        # ----------------------------------------------------

        load_fact_sales(
            cursor,
            fact_sales
        )

        # ----------------------------------------------------
        # Commit
        # ----------------------------------------------------

        connection.commit()

        cursor.close()

        logger.info(
            "========================================"
        )

        logger.info(
            "PHASE 3 DATA WAREHOUSE ETL COMPLETED"
        )

        logger.info(
            "========================================"
        )

    except Exception as error:

        if connection:
            connection.rollback()

        logger.exception(
            "Warehouse ETL failed: %s",
            error
        )

        raise

    finally:

        if connection:
            connection.close()


if __name__ == "__main__":
    run_warehouse_etl()