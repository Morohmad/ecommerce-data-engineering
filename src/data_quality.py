import logging

import psycopg2

from config import (
    DB_HOST,
    DB_PORT,
    DB_NAME,
    DB_USER,
    DB_PASSWORD,
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

    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
    )


# --------------------------------------------------
# Data quality checks
# --------------------------------------------------

def check_table_count(
    cursor,
    table_name: str,
) -> int:

    query = f"""
        SELECT COUNT(*)
        FROM {table_name};
    """

    cursor.execute(query)

    result = cursor.fetchone()[0]

    logger.info(
        "%s row count: %s",
        table_name,
        result,
    )

    return result


def check_null_primary_keys(
    cursor,
    table_name: str,
    primary_key: str,
) -> int:

    query = f"""
        SELECT COUNT(*)
        FROM {table_name}
        WHERE {primary_key} IS NULL;
    """

    cursor.execute(query)

    result = cursor.fetchone()[0]

    logger.info(
        "%s.%s NULL count: %s",
        table_name,
        primary_key,
        result,
    )

    return result


def main():

    connection = get_connection()

    try:

        cursor = connection.cursor()

        logger.info(
            "Running data quality checks..."
        )

        tables = [
            ("stg_products", "product_id"),
            ("stg_users", "user_id"),
            ("stg_carts", "cart_id"),
        ]

        for table_name, primary_key in tables:

            row_count = check_table_count(
                cursor,
                table_name,
            )

            if row_count == 0:
                raise ValueError(
                    f"{table_name} is empty."
                )

            null_count = check_null_primary_keys(
                cursor,
                table_name,
                primary_key,
            )

            if null_count > 0:
                raise ValueError(
                    f"{table_name} contains NULL primary keys."
                )

        logger.info(
            "All data quality checks passed."
        )

        cursor.close()

    finally:

        connection.close()


if __name__ == "__main__":
    main()