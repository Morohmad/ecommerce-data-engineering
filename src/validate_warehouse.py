import logging

import psycopg2

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
# CONNECTION
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
# TABLE COUNT
# ============================================================

def check_table_count(
    cursor,
    table_name: str
):

    cursor.execute(
        f"""
        SELECT COUNT(*)
        FROM warehouse.{table_name};
        """
    )

    count = cursor.fetchone()[0]

    logger.info(
        "%s rows: %s",
        table_name,
        count
    )

    if count == 0:

        raise ValueError(
            f"warehouse.{table_name} is empty."
        )


# ============================================================
# CHECK FACT FOREIGN KEYS
# ============================================================

def check_fact_foreign_keys(
    cursor
):

    query = """
        SELECT COUNT(*)
        FROM warehouse.fact_sales f
        LEFT JOIN warehouse.dim_customer c
            ON f.customer_key = c.customer_key
        LEFT JOIN warehouse.dim_product p
            ON f.product_key = p.product_key
        LEFT JOIN warehouse.dim_date d
            ON f.date_key = d.date_key
        WHERE c.customer_key IS NULL
           OR p.product_key IS NULL
           OR d.date_key IS NULL;
    """

    cursor.execute(
        query
    )

    invalid_count = cursor.fetchone()[0]

    logger.info(
        "Fact rows with invalid dimension references: %s",
        invalid_count
    )

    if invalid_count > 0:

        raise ValueError(
            "fact_sales contains invalid dimension references."
        )


# ============================================================
# CHECK NEGATIVE VALUES
# ============================================================

def check_negative_values(
    cursor
):

    query = """
        SELECT COUNT(*)
        FROM warehouse.fact_sales
        WHERE quantity <= 0
           OR unit_price < 0
           OR gross_amount < 0
           OR discount_amount < 0
           OR net_amount < 0;
    """

    cursor.execute(
        query
    )

    invalid_count = cursor.fetchone()[0]

    logger.info(
        "Fact rows with invalid metrics: %s",
        invalid_count
    )

    if invalid_count > 0:

        raise ValueError(
            "fact_sales contains invalid metric values."
        )


# ============================================================
# CHECK FACT GRAIN
# ============================================================

def check_fact_grain(
    cursor
):

    query = """
        SELECT
            cart_id,
            product_id,
            COUNT(*)
        FROM warehouse.fact_sales
        GROUP BY
            cart_id,
            product_id
        HAVING COUNT(*) > 1;
    """

    cursor.execute(
        query
    )

    duplicate_rows = cursor.fetchall()

    logger.info(
        "Duplicate fact grain groups: %s",
        len(duplicate_rows)
    )

    if duplicate_rows:

        raise ValueError(
            "fact_sales violates the defined grain."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "STARTING PHASE 3 WAREHOUSE VALIDATION"
    )

    logger.info(
        "========================================"
    )

    connection = get_connection()

    try:

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Table checks
        # ----------------------------------------------------

        tables = [
            "dim_date",
            "dim_customer",
            "dim_product",
            "fact_sales",
        ]

        for table in tables:

            check_table_count(
                cursor,
                table
            )

        # ----------------------------------------------------
        # Foreign key checks
        # ----------------------------------------------------

        check_fact_foreign_keys(
            cursor
        )

        # ----------------------------------------------------
        # Metric checks
        # ----------------------------------------------------

        check_negative_values(
            cursor
        )

        # ----------------------------------------------------
        # Grain checks
        # ----------------------------------------------------

        check_fact_grain(
            cursor
        )

        # ----------------------------------------------------
        # Success
        # ----------------------------------------------------

        logger.info(
            "========================================"
        )

        logger.info(
            "ALL PHASE 3 VALIDATION CHECKS PASSED"
        )

        logger.info(
            "========================================"
        )

        cursor.close()

    finally:

        connection.close()


if __name__ == "__main__":
    main()