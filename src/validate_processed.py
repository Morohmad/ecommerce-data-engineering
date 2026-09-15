import logging

import pandas as pd

from config import PROCESSED_DATA_DIR


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


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
            f"Processed file not found: {file_path}"
        )

    return pd.read_csv(
        file_path
    )


# ============================================================
# CHECK NOT EMPTY
# ============================================================

def check_not_empty(
    df: pd.DataFrame,
    dataset_name: str
) -> None:

    if df.empty:

        raise ValueError(
            f"{dataset_name} is empty."
        )

    logger.info(
        "%s is not empty: %s rows",
        dataset_name,
        len(df)
    )


# ============================================================
# CHECK PRIMARY KEY
# ============================================================

def check_primary_key(
    df: pd.DataFrame,
    column: str,
    dataset_name: str
) -> None:

    null_count = df[column].isna().sum()

    duplicate_count = (
        df[column]
        .duplicated()
        .sum()
    )

    logger.info(
        "%s.%s NULL: %s",
        dataset_name,
        column,
        null_count
    )

    logger.info(
        "%s.%s duplicates: %s",
        dataset_name,
        column,
        duplicate_count
    )

    if null_count > 0:

        raise ValueError(
            f"{dataset_name}.{column} "
            f"contains NULL values."
        )

    if duplicate_count > 0:

        raise ValueError(
            f"{dataset_name}.{column} "
            f"contains duplicates."
        )


# ============================================================
# CHECK CART ITEM KEY
# ============================================================

def check_cart_item_key(
    df: pd.DataFrame
) -> None:

    duplicate_count = (
        df[
            [
                "cart_id",
                "product_id",
            ]
        ]
        .duplicated()
        .sum()
    )

    logger.info(
        "Cart item duplicate composite keys: %s",
        duplicate_count
    )

    if duplicate_count > 0:

        raise ValueError(
            "cart_items contains duplicate "
            "(cart_id, product_id)."
        )


# ============================================================
# CHECK NUMERIC RANGE
# ============================================================

def check_product_values(
    df: pd.DataFrame
) -> None:

    invalid_price = (
        df["price"] < 0
    ).sum()

    invalid_rating = (
        (df["rating"] < 0) |
        (df["rating"] > 5)
    ).sum()

    invalid_stock = (
        df["stock"] < 0
    ).sum()

    logger.info(
        "Invalid product price: %s",
        invalid_price
    )

    logger.info(
        "Invalid product rating: %s",
        invalid_rating
    )

    logger.info(
        "Invalid product stock: %s",
        invalid_stock
    )

    if invalid_price > 0:
        raise ValueError(
            "Products contain invalid prices."
        )

    if invalid_rating > 0:
        raise ValueError(
            "Products contain invalid ratings."
        )

    if invalid_stock > 0:
        raise ValueError(
            "Products contain invalid stock."
        )


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "STARTING PHASE 2 DATA VALIDATION"
    )

    logger.info(
        "========================================"
    )

    # --------------------------------------------------------
    # Load
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

    # --------------------------------------------------------
    # Not empty
    # --------------------------------------------------------

    check_not_empty(
        products,
        "products"
    )

    check_not_empty(
        users,
        "users"
    )

    check_not_empty(
        carts,
        "carts"
    )

    check_not_empty(
        cart_items,
        "cart_items"
    )

    # --------------------------------------------------------
    # Primary keys
    # --------------------------------------------------------

    check_primary_key(
        products,
        "product_id",
        "products"
    )

    check_primary_key(
        users,
        "user_id",
        "users"
    )

    check_primary_key(
        carts,
        "cart_id",
        "carts"
    )

    # --------------------------------------------------------
    # Cart item composite key
    # --------------------------------------------------------

    check_cart_item_key(
        cart_items
    )

    # --------------------------------------------------------
    # Product validation
    # --------------------------------------------------------

    check_product_values(
        products
    )

    # --------------------------------------------------------
    # Success
    # --------------------------------------------------------

    logger.info(
        "========================================"
    )

    logger.info(
        "ALL PHASE 2 DATA QUALITY CHECKS PASSED"
    )

    logger.info(
        "========================================"
    )


if __name__ == "__main__":
    main()