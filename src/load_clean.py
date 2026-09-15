import logging

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    PROCESSED_DATA_DIR,
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
# LOAD CSV
# ============================================================

def load_csv(
    file_name: str
) -> pd.DataFrame:

    file_path = (
        PROCESSED_DATA_DIR /
        file_name
    )

    if not file_path.exists():

        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    logger.info(
        "Reading %s",
        file_path
    )

    return pd.read_csv(
        file_path
    )


# ============================================================
# PRODUCTS
# ============================================================

def load_products(
    cursor,
    df: pd.DataFrame
):

    columns = [
        "product_id",
        "product_name",
        "description",
        "category",
        "price",
        "discount_percentage",
        "rating",
        "stock",
        "brand",
        "sku",
        "weight",
        "width",
        "height",
        "depth",
        "warranty_information",
        "shipping_information",
        "availability_status",
        "return_policy",
        "minimum_order_quantity",
        "thumbnail",
    ]

    rows = [
        tuple(row)
        for row in df[columns].itertuples(
            index=False,
            name=None
        )
    ]

    sql = """
        INSERT INTO stg_products_clean (
            product_id,
            product_name,
            description,
            category,
            price,
            discount_percentage,
            rating,
            stock,
            brand,
            sku,
            weight,
            width,
            height,
            depth,
            warranty_information,
            shipping_information,
            availability_status,
            return_policy,
            minimum_order_quantity,
            thumbnail
        )
        VALUES %s
        ON CONFLICT (product_id)
        DO UPDATE SET
            product_name = EXCLUDED.product_name,
            description = EXCLUDED.description,
            category = EXCLUDED.category,
            price = EXCLUDED.price,
            discount_percentage =
                EXCLUDED.discount_percentage,
            rating = EXCLUDED.rating,
            stock = EXCLUDED.stock,
            brand = EXCLUDED.brand,
            sku = EXCLUDED.sku,
            weight = EXCLUDED.weight,
            width = EXCLUDED.width,
            height = EXCLUDED.height,
            depth = EXCLUDED.depth,
            warranty_information =
                EXCLUDED.warranty_information,
            shipping_information =
                EXCLUDED.shipping_information,
            availability_status =
                EXCLUDED.availability_status,
            return_policy =
                EXCLUDED.return_policy,
            minimum_order_quantity =
                EXCLUDED.minimum_order_quantity,
            thumbnail = EXCLUDED.thumbnail;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded %s products.",
        len(rows)
    )


# ============================================================
# USERS
# ============================================================

def load_users(
    cursor,
    df: pd.DataFrame
):

    columns = [
        "user_id",
        "first_name",
        "last_name",
        "maiden_name",
        "age",
        "gender",
        "email",
        "phone",
        "username",
        "birth_date",
        "image",
        "blood_group",
        "height",
        "weight",
        "eye_color",
        "hair_color",
        "hair_type",
        "ip_address",
        "address",
        "city",
        "state",
        "state_code",
        "postal_code",
        "country",
        "mac_address",
        "university",
        "user_agent",
        "crypto_coin",
        "crypto_wallet",
        "crypto_network",
    ]

    rows = [
        tuple(row)
        for row in df[columns].itertuples(
            index=False,
            name=None
        )
    ]

    sql = """
        INSERT INTO stg_users_clean (
            user_id,
            first_name,
            last_name,
            maiden_name,
            age,
            gender,
            email,
            phone,
            username,
            birth_date,
            image,
            blood_group,
            height,
            weight,
            eye_color,
            hair_color,
            hair_type,
            ip_address,
            address,
            city,
            state,
            state_code,
            postal_code,
            country,
            mac_address,
            university,
            user_agent,
            crypto_coin,
            crypto_wallet,
            crypto_network
        )
        VALUES %s
        ON CONFLICT (user_id)
        DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            maiden_name = EXCLUDED.maiden_name,
            age = EXCLUDED.age,
            gender = EXCLUDED.gender,
            email = EXCLUDED.email,
            phone = EXCLUDED.phone,
            username = EXCLUDED.username,
            birth_date = EXCLUDED.birth_date,
            image = EXCLUDED.image,
            blood_group = EXCLUDED.blood_group,
            height = EXCLUDED.height,
            weight = EXCLUDED.weight,
            eye_color = EXCLUDED.eye_color,
            hair_color = EXCLUDED.hair_color,
            hair_type = EXCLUDED.hair_type,
            ip_address = EXCLUDED.ip_address,
            address = EXCLUDED.address,
            city = EXCLUDED.city,
            state = EXCLUDED.state,
            state_code = EXCLUDED.state_code,
            postal_code = EXCLUDED.postal_code,
            country = EXCLUDED.country,
            mac_address = EXCLUDED.mac_address,
            university = EXCLUDED.university,
            user_agent = EXCLUDED.user_agent,
            crypto_coin = EXCLUDED.crypto_coin,
            crypto_wallet = EXCLUDED.crypto_wallet,
            crypto_network = EXCLUDED.crypto_network;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded %s users.",
        len(rows)
    )


# ============================================================
# CARTS
# ============================================================

def load_carts(
    cursor,
    df: pd.DataFrame
):

    columns = [
        "cart_id",
        "user_id",
        "total",
        "discounted_total",
        "total_products",
        "total_quantity",
        "source_extracted_at",
    ]

    rows = [
        tuple(row)
        for row in df[columns].itertuples(
            index=False,
            name=None
        )
    ]

    sql = """
        INSERT INTO stg_carts_clean (
            cart_id,
            user_id,
            total,
            discounted_total,
            total_products,
            total_quantity,
            source_extracted_at
        )
        VALUES %s
        ON CONFLICT (cart_id)
        DO UPDATE SET
            user_id = EXCLUDED.user_id,
            total = EXCLUDED.total,
            discounted_total =
                EXCLUDED.discounted_total,
            total_products =
                EXCLUDED.total_products,
            total_quantity =
                EXCLUDED.total_quantity,
            source_extracted_at =
                EXCLUDED.source_extracted_at;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded %s carts.",
        len(rows)
    )


# ============================================================
# CART ITEMS
# ============================================================

def load_cart_items(
    cursor,
    df: pd.DataFrame
):

    columns = [
        "cart_id",
        "product_id",
        "product_name",
        "price",
        "quantity",
        "total",
        "discount_percentage",
        "discounted_total",
        "thumbnail",
    ]

    rows = [
        tuple(row)
        for row in df[columns].itertuples(
            index=False,
            name=None
        )
    ]

    sql = """
        INSERT INTO stg_cart_items_clean (
            cart_id,
            product_id,
            product_name,
            price,
            quantity,
            total,
            discount_percentage,
            discounted_total,
            thumbnail
        )
        VALUES %s
        ON CONFLICT (
            cart_id,
            product_id
        )
        DO UPDATE SET
            product_name =
                EXCLUDED.product_name,
            price =
                EXCLUDED.price,
            quantity =
                EXCLUDED.quantity,
            total =
                EXCLUDED.total,
            discount_percentage =
                EXCLUDED.discount_percentage,
            discounted_total =
                EXCLUDED.discounted_total,
            thumbnail =
                EXCLUDED.thumbnail;
    """

    execute_values(
        cursor,
        sql,
        rows
    )

    logger.info(
        "Loaded %s cart items.",
        len(rows)
    )


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "STARTING PHASE 2 DATABASE LOAD"
    )

    logger.info(
        "========================================"
    )

    # --------------------------------------------------------
    # Read processed data
    # --------------------------------------------------------

    products = load_csv(
        "products_clean.csv"
    )

    users = load_csv(
        "users_clean.csv"
    )

    carts = load_csv(
        "carts_clean.csv"
    )

    cart_items = load_csv(
        "cart_items_clean.csv"
    )

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Load data
        # ----------------------------------------------------

        load_products(
            cursor,
            products
        )

        load_users(
            cursor,
            users
        )

        load_carts(
            cursor,
            carts
        )

        load_cart_items(
            cursor,
            cart_items
        )

        # ----------------------------------------------------
        # Commit transaction
        # ----------------------------------------------------

        connection.commit()

        cursor.close()

        logger.info(
            "Database loading completed successfully."
        )

    except Exception as error:

        if connection:
            connection.rollback()

        logger.exception(
            "Database loading failed: %s",
            error
        )

        raise

    finally:

        if connection:
            connection.close()


if __name__ == "__main__":
    main()