import json
import logging
from datetime import datetime
from pathlib import Path

import psycopg2
from psycopg2.extras import execute_values

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
    RAW_DATA_DIR,
)


# --------------------------------------------------
# Logging
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Database connection
# --------------------------------------------------

def get_connection():
    """
    Membuat koneksi ke PostgreSQL.
    """

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# --------------------------------------------------
# Load products
# --------------------------------------------------

def load_products(
    cursor,
    data: dict,
) -> None:

    products = data.get("products", [])

    rows = []

    extracted_at = data.get(
        "extracted_at"
    )

    for product in products:

        dimensions = product.get(
            "dimensions",
            {}
        )

        rows.append(
            (
                product.get("id"),
                product.get("title"),
                product.get("description"),
                product.get("category"),
                product.get("price"),
                product.get("discountPercentage"),
                product.get("rating"),
                product.get("stock"),
                product.get("brand"),
                product.get("sku"),
                product.get("weight"),
                dimensions.get("width"),
                dimensions.get("height"),
                dimensions.get("depth"),
                product.get("warrantyInformation"),
                product.get("shippingInformation"),
                product.get("availabilityStatus"),
                product.get("returnPolicy"),
                product.get("minimumOrderQuantity"),
                product.get("thumbnail"),
                extracted_at,
            )
        )

    sql = """
        INSERT INTO stg_products (
            product_id,
            title,
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
            thumbnail,
            source_extracted_at
        )
        VALUES %s
        ON CONFLICT (product_id)
        DO UPDATE SET
            title = EXCLUDED.title,
            description = EXCLUDED.description,
            category = EXCLUDED.category,
            price = EXCLUDED.price,
            discount_percentage = EXCLUDED.discount_percentage,
            rating = EXCLUDED.rating,
            stock = EXCLUDED.stock,
            brand = EXCLUDED.brand,
            sku = EXCLUDED.sku,
            weight = EXCLUDED.weight,
            width = EXCLUDED.width,
            height = EXCLUDED.height,
            depth = EXCLUDED.depth,
            warranty_information = EXCLUDED.warranty_information,
            shipping_information = EXCLUDED.shipping_information,
            availability_status = EXCLUDED.availability_status,
            return_policy = EXCLUDED.return_policy,
            minimum_order_quantity = EXCLUDED.minimum_order_quantity,
            thumbnail = EXCLUDED.thumbnail,
            source_extracted_at = EXCLUDED.source_extracted_at;
    """

    execute_values(
        cursor,
        sql,
        rows,
    )

    logger.info(
        "Loaded %s products.",
        len(rows),
    )


# --------------------------------------------------
# Load users
# --------------------------------------------------

def load_users(
    cursor,
    data: dict,
) -> None:

    users = data.get("users", [])

    rows = []

    extracted_at = data.get(
        "extracted_at"
    )

    for user in users:

        hair = user.get(
            "hair",
            {}
        )

        address = user.get(
            "address",
            {}
        )

        crypto = user.get(
            "crypto",
            {}
        )

        rows.append(
            (
                user.get("id"),
                user.get("firstName"),
                user.get("lastName"),
                user.get("maidenName"),
                user.get("age"),
                user.get("gender"),
                user.get("email"),
                user.get("phone"),
                user.get("username"),
                user.get("password"),
                user.get("birthDate"),
                user.get("image"),
                user.get("bloodGroup"),
                user.get("height"),
                user.get("weight"),
                user.get("eyeColor"),
                hair.get("color"),
                hair.get("type"),
                user.get("ip"),
                address.get("address"),
                address.get("city"),
                address.get("state"),
                address.get("stateCode"),
                address.get("postalCode"),
                address.get("country"),
                user.get("macAddress"),
                user.get("university"),
                user.get("ein"),
                user.get("ssn"),
                user.get("userAgent"),
                crypto.get("coin"),
                crypto.get("wallet"),
                crypto.get("network"),
                extracted_at,
            )
        )

    sql = """
        INSERT INTO stg_users (
            user_id,
            first_name,
            last_name,
            maiden_name,
            age,
            gender,
            email,
            phone,
            username,
            password,
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
            ein,
            ssn,
            user_agent,
            crypto_coin,
            crypto_wallet,
            crypto_network,
            source_extracted_at
        )
        VALUES %s
        ON CONFLICT (user_id)
        DO UPDATE SET
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
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
            crypto_network = EXCLUDED.crypto_network,
            source_extracted_at = EXCLUDED.source_extracted_at;
    """

    execute_values(
        cursor,
        sql,
        rows,
    )

    logger.info(
        "Loaded %s users.",
        len(rows),
    )


# --------------------------------------------------
# Load carts and cart items
# --------------------------------------------------

def load_carts(
    cursor,
    data: dict,
) -> None:

    carts = data.get("carts", [])

    cart_rows = []
    item_rows = []

    extracted_at = data.get(
        "extracted_at"
    )

    for cart in carts:

        cart_rows.append(
            (
                cart.get("id"),
                cart.get("userId"),
                cart.get("total"),
                cart.get("discountedTotal"),
                cart.get("totalProducts"),
                cart.get("totalQuantity"),
                extracted_at,
            )
        )

        for product in cart.get(
            "products",
            []
        ):

            item_rows.append(
                (
                    cart.get("id"),
                    product.get("id"),
                    product.get("title"),
                    product.get("price"),
                    product.get("quantity"),
                    product.get("total"),
                    product.get(
                        "discountPercentage"
                    ),
                    product.get(
                        "discountedTotal"
                    ),
                    product.get("thumbnail"),
                )
            )

    # --------------------------------------------------
    # Remove duplicate cart IDs
    # --------------------------------------------------

    cart_rows_dict = {}

    for row in cart_rows:
        cart_id = row[0]
        cart_rows_dict[cart_id] = row

    cart_rows = list(
        cart_rows_dict.values()
    )

    # --------------------------------------------------
    # Remove duplicate cart item keys
    # Key = (cart_id, product_id)
    # --------------------------------------------------

    item_rows_dict = {}

    for row in item_rows:
        key = (
            row[0],  # cart_id
            row[1],  # product_id
        )

        item_rows_dict[key] = row

    duplicate_item_count = (
        len(item_rows)
        - len(item_rows_dict)
    )

    item_rows = list(
        item_rows_dict.values()
    )

    # --------------------------------------------------
    # Load carts
    # --------------------------------------------------

    cart_sql = """
        INSERT INTO stg_carts (
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
            discounted_total = EXCLUDED.discounted_total,
            total_products = EXCLUDED.total_products,
            total_quantity = EXCLUDED.total_quantity,
            source_extracted_at = EXCLUDED.source_extracted_at;
    """

    execute_values(
        cursor,
        cart_sql,
        cart_rows,
    )

    # --------------------------------------------------
    # Load cart items
    # --------------------------------------------------

    item_sql = """
        INSERT INTO stg_cart_items (
            cart_id,
            product_id,
            title,
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
            title = EXCLUDED.title,
            price = EXCLUDED.price,
            quantity = EXCLUDED.quantity,
            total = EXCLUDED.total,
            discount_percentage =
                EXCLUDED.discount_percentage,
            discounted_total =
                EXCLUDED.discounted_total,
            thumbnail =
                EXCLUDED.thumbnail;
    """

    execute_values(
        cursor,
        item_sql,
        item_rows,
    )

    logger.info(
        "Loaded %s carts.",
        len(cart_rows),
    )

    logger.info(
        "Loaded %s cart items.",
        len(item_rows),
    )

    if duplicate_item_count > 0:
        logger.warning(
            "Removed %s duplicate cart items.",
            duplicate_item_count,
        )

# --------------------------------------------------
# Read JSON
# --------------------------------------------------

def read_json(
    file_name: str,
) -> dict:

    file_path = RAW_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    with file_path.open(
        "r",
        encoding="utf-8",
    ) as file:

        return json.load(file)


# --------------------------------------------------
# Main
# --------------------------------------------------

def main() -> None:

    logger.info(
        "Starting PostgreSQL loading..."
    )

    products = read_json(
        "products.json"
    )

    users = read_json(
        "users.json"
    )

    carts = read_json(
        "carts.json"
    )

    connection = None

    try:

        connection = get_connection()

        cursor = connection.cursor()

        load_products(
            cursor,
            products,
        )

        load_users(
            cursor,
            users,
        )

        load_carts(
            cursor,
            carts,
        )

        connection.commit()

        cursor.close()

        logger.info(
            "Data loading completed successfully."
        )

    except Exception as error:

        if connection:
            connection.rollback()

        logger.exception(
            "Data loading failed: %s",
            error,
        )

        raise

    finally:

        if connection:
            connection.close()


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()