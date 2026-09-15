import json
import logging
from pathlib import Path

import pandas as pd


from config import (
    RAW_DATA_DIR,
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
# GENERAL FUNCTIONS
# ============================================================

def load_json(
    file_name: str
) -> dict:

    file_path = RAW_DATA_DIR / file_name

    if not file_path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    logger.info(
        "Reading %s",
        file_path
    )

    with file_path.open(
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


def save_csv(
    df: pd.DataFrame,
    file_name: str
) -> None:

    file_path = (
        PROCESSED_DATA_DIR /
        file_name
    )

    df.to_csv(
        file_path,
        index=False,
        encoding="utf-8"
    )

    logger.info(
        "Saved %s rows to %s",
        len(df),
        file_path
    )


# ============================================================
# PRODUCTS
# ============================================================

def transform_products(
    data: dict
) -> pd.DataFrame:

    logger.info(
        "Transforming products..."
    )

    products = data.get(
        "products",
        []
    )

    if not products:
        raise ValueError(
            "Products data is empty."
        )

    df = pd.json_normalize(
        products
    )

    # --------------------------------------------------------
    # Rename columns
    # --------------------------------------------------------

    rename_map = {
        "id": "product_id",
        "title": "product_name",
        "discountPercentage": "discount_percentage",
        "availabilityStatus": "availability_status",
        "returnPolicy": "return_policy",
        "minimumOrderQuantity": "minimum_order_quantity",
        "warrantyInformation": "warranty_information",
        "shippingInformation": "shipping_information",
    }

    df = df.rename(
        columns=rename_map
    )

    # --------------------------------------------------------
    # Select relevant columns only
    # --------------------------------------------------------

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
        "dimensions.width",
        "dimensions.height",
        "dimensions.depth",
        "warranty_information",
        "shipping_information",
        "availability_status",
        "return_policy",
        "minimum_order_quantity",
        "thumbnail",
    ]

    # Only keep columns that actually exist
    columns = [
        column
        for column in columns
        if column in df.columns
    ]

    df = df[columns].copy()

    # --------------------------------------------------------
    # Rename dimensions
    # --------------------------------------------------------

    dimension_rename = {
        "dimensions.width": "width",
        "dimensions.height": "height",
        "dimensions.depth": "depth",
    }

    df = df.rename(
        columns=dimension_rename
    )

    # --------------------------------------------------------
    # Clean text columns
    # --------------------------------------------------------

    text_columns = [
        "product_name",
        "description",
        "category",
        "brand",
        "sku",
        "warranty_information",
        "shipping_information",
        "availability_status",
        "return_policy",
        "thumbnail",
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # --------------------------------------------------------
    # Standardize category
    # --------------------------------------------------------

    if "category" in df.columns:

        df["category"] = (
            df["category"]
            .str.lower()
            .str.strip()
        )

    # --------------------------------------------------------
    # Standardize brand
    # --------------------------------------------------------

    if "brand" in df.columns:

        df["brand"] = (
            df["brand"]
            .replace(
                {
                    "<NA>": pd.NA,
                    "nan": pd.NA,
                    "": pd.NA,
                }
            )
        )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

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
        "minimum_order_quantity",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Round decimal values
    # --------------------------------------------------------

    decimal_columns = [
        "price",
        "discount_percentage",
        "rating",
        "weight",
        "width",
        "height",
        "depth",
    ]

    for column in decimal_columns:

        if column in df.columns:

            df[column] = df[column].round(2)

    # --------------------------------------------------------
    # Handle invalid numeric values
    # --------------------------------------------------------

    if "price" in df.columns:

        df.loc[
            df["price"] < 0,
            "price"
        ] = pd.NA

    if "stock" in df.columns:

        df.loc[
            df["stock"] < 0,
            "stock"
        ] = pd.NA

    if "rating" in df.columns:

        df.loc[
            (df["rating"] < 0) |
            (df["rating"] > 5),
            "rating"
        ] = pd.NA

    # --------------------------------------------------------
    # Remove duplicate products
    # --------------------------------------------------------

    if "product_id" in df.columns:

        before = len(df)

        df = df.drop_duplicates(
            subset=["product_id"]
        )

        after = len(df)

        logger.info(
            "Products duplicates removed: %s",
            before - after
        )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    if "product_id" in df.columns:

        df = df.sort_values(
            "product_id"
        ).reset_index(
            drop=True
        )

    return df


# ============================================================
# USERS
# ============================================================

def transform_users(
    data: dict
) -> pd.DataFrame:

    logger.info(
        "Transforming users..."
    )

    users = data.get(
        "users",
        []
    )

    if not users:
        raise ValueError(
            "Users data is empty."
        )

    df = pd.json_normalize(
        users
    )

    # --------------------------------------------------------
    # Rename columns
    # --------------------------------------------------------

    rename_map = {
        "id": "user_id",
        "firstName": "first_name",
        "lastName": "last_name",
        "maidenName": "maiden_name",
        "birthDate": "birth_date",
        "eyeColor": "eye_color",
        "ip": "ip_address",
        "macAddress": "mac_address",
        "userAgent": "user_agent",
    }

    df = df.rename(
        columns=rename_map
    )

    # --------------------------------------------------------
    # Rename nested fields
    # --------------------------------------------------------

    nested_rename = {
        "hair.color": "hair_color",
        "hair.type": "hair_type",
        "address.address": "address",
        "address.city": "city",
        "address.state": "state",
        "address.stateCode": "state_code",
        "address.postalCode": "postal_code",
        "address.country": "country",
        "crypto.coin": "crypto_coin",
        "crypto.wallet": "crypto_wallet",
        "crypto.network": "crypto_network",
    }

    df = df.rename(
        columns=nested_rename
    )

    # --------------------------------------------------------
    # Select columns
    #
    # Deliberately exclude:
    # password
    # ssn
    # ein
    # --------------------------------------------------------

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
        "bloodGroup",
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

    columns = [
        column
        for column in columns
        if column in df.columns
    ]

    df = df[columns].copy()

    # --------------------------------------------------------
    # Rename bloodGroup
    # --------------------------------------------------------

    df = df.rename(
        columns={
            "bloodGroup": "blood_group"
        }
    )

    # --------------------------------------------------------
    # Clean text
    # --------------------------------------------------------

    text_columns = [
        "first_name",
        "last_name",
        "maiden_name",
        "gender",
        "email",
        "phone",
        "username",
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
        "blood_group",
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .astype("string")
                .str.strip()
            )

    # --------------------------------------------------------
    # Standardize text
    # --------------------------------------------------------

    lowercase_columns = [
        "gender",
        "email",
        "username",
        "city",
        "state",
        "country",
        "crypto_coin",
        "crypto_network",
    ]

    for column in lowercase_columns:

        if column in df.columns:

            df[column] = (
                df[column]
                .str.lower()
                .str.strip()
            )

    # --------------------------------------------------------
    # Numeric columns
    # --------------------------------------------------------

    numeric_columns = [
        "user_id",
        "age",
        "height",
        "weight",
    ]

    for column in numeric_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # --------------------------------------------------------
    # Date
    # --------------------------------------------------------

    if "birth_date" in df.columns:

        df["birth_date"] = pd.to_datetime(
            df["birth_date"],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Basic validation
    # --------------------------------------------------------

    if "age" in df.columns:

        df.loc[
            (df["age"] < 0) |
            (df["age"] > 120),
            "age"
        ] = pd.NA

    if "height" in df.columns:

        df.loc[
            df["height"] <= 0,
            "height"
        ] = pd.NA

    if "weight" in df.columns:

        df.loc[
            df["weight"] <= 0,
            "weight"
        ] = pd.NA

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    if "user_id" in df.columns:

        before = len(df)

        df = df.drop_duplicates(
            subset=["user_id"]
        )

        after = len(df)

        logger.info(
            "Users duplicates removed: %s",
            before - after
        )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    if "user_id" in df.columns:

        df = df.sort_values(
            "user_id"
        ).reset_index(
            drop=True
        )

    return df


# ============================================================
# CARTS
# ============================================================

def transform_carts(
    data: dict
) -> pd.DataFrame:

    logger.info(
        "Transforming carts..."
    )

    carts = data.get(
        "carts",
        []
    )

    if not carts:
        raise ValueError(
            "Carts data is empty."
        )

    rows = []

    extracted_at = data.get(
        "extracted_at"
    )

    for cart in carts:

        rows.append(
            {
                "cart_id": cart.get("id"),
                "user_id": cart.get("userId"),
                "total": cart.get("total"),
                "discounted_total": cart.get(
                    "discountedTotal"
                ),
                "total_products": cart.get(
                    "totalProducts"
                ),
                "total_quantity": cart.get(
                    "totalQuantity"
                ),
                "source_extracted_at": extracted_at,
            }
        )

    df = pd.DataFrame(rows)

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    numeric_columns = [
        "cart_id",
        "user_id",
        "total",
        "discounted_total",
        "total_products",
        "total_quantity",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Round monetary values
    # --------------------------------------------------------

    monetary_columns = [
        "total",
        "discounted_total",
    ]

    for column in monetary_columns:

        df[column] = df[column].round(2)

    # --------------------------------------------------------
    # Remove invalid values
    # --------------------------------------------------------

    df.loc[
        df["total"] < 0,
        "total"
    ] = pd.NA

    df.loc[
        df["discounted_total"] < 0,
        "discounted_total"
    ] = pd.NA

    df.loc[
        df["total_products"] < 0,
        "total_products"
    ] = pd.NA

    df.loc[
        df["total_quantity"] < 0,
        "total_quantity"
    ] = pd.NA

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=["cart_id"]
    )

    after = len(df)

    logger.info(
        "Carts duplicates removed: %s",
        before - after
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = df.sort_values(
        "cart_id"
    ).reset_index(
        drop=True
    )

    return df


# ============================================================
# CART ITEMS
# ============================================================

def transform_cart_items(
    data: dict
) -> pd.DataFrame:

    logger.info(
        "Transforming cart items..."
    )

    carts = data.get(
        "carts",
        []
    )

    if not carts:
        raise ValueError(
            "Carts data is empty."
        )

    rows = []

    for cart in carts:

        cart_id = cart.get(
            "id"
        )

        products = cart.get(
            "products",
            []
        )

        for product in products:

            rows.append(
                {
                    "cart_id": cart_id,
                    "product_id": product.get(
                        "id"
                    ),
                    "product_name": product.get(
                        "title"
                    ),
                    "price": product.get(
                        "price"
                    ),
                    "quantity": product.get(
                        "quantity"
                    ),
                    "total": product.get(
                        "total"
                    ),
                    "discount_percentage": product.get(
                        "discountPercentage"
                    ),
                    "discounted_total": product.get(
                        "discountedTotal"
                    ),
                    "thumbnail": product.get(
                        "thumbnail"
                    ),
                }
            )

    df = pd.DataFrame(rows)

    # --------------------------------------------------------
    # Numeric conversion
    # --------------------------------------------------------

    numeric_columns = [
        "cart_id",
        "product_id",
        "price",
        "quantity",
        "total",
        "discount_percentage",
        "discounted_total",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Text cleaning
    # --------------------------------------------------------

    df["product_name"] = (
        df["product_name"]
        .astype("string")
        .str.strip()
    )

    df["thumbnail"] = (
        df["thumbnail"]
        .astype("string")
        .str.strip()
    )

    # --------------------------------------------------------
    # Round monetary fields
    # --------------------------------------------------------

    monetary_columns = [
        "price",
        "total",
        "discount_percentage",
        "discounted_total",
    ]

    for column in monetary_columns:

        df[column] = df[column].round(2)

    # --------------------------------------------------------
    # Validate quantity
    # --------------------------------------------------------

    df.loc[
        df["quantity"] <= 0,
        "quantity"
    ] = pd.NA

    # --------------------------------------------------------
    # Validate price
    # --------------------------------------------------------

    df.loc[
        df["price"] < 0,
        "price"
    ] = pd.NA

    # --------------------------------------------------------
    # Validate total
    # --------------------------------------------------------

    df.loc[
        df["total"] < 0,
        "total"
    ] = pd.NA

    # --------------------------------------------------------
    # Validate discount
    # --------------------------------------------------------

    df.loc[
        (df["discount_percentage"] < 0) |
        (df["discount_percentage"] > 100),
        "discount_percentage"
    ] = pd.NA

    # --------------------------------------------------------
    # Remove duplicates
    # --------------------------------------------------------

    before = len(df)

    df = df.drop_duplicates(
        subset=[
            "cart_id",
            "product_id",
        ]
    )

    after = len(df)

    logger.info(
        "Cart item duplicates removed: %s",
        before - after
    )

    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    df = df.sort_values(
        [
            "cart_id",
            "product_id",
        ]
    ).reset_index(
        drop=True
    )

    return df


# ============================================================
# MAIN TRANSFORMATION
# ============================================================

def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "STARTING PHASE 2 TRANSFORMATION"
    )

    logger.info(
        "========================================"
    )

    # --------------------------------------------------------
    # Load raw data
    # --------------------------------------------------------

    products_data = load_json(
        "products.json"
    )

    users_data = load_json(
        "users.json"
    )

    carts_data = load_json(
        "carts.json"
    )

    # --------------------------------------------------------
    # Transform
    # --------------------------------------------------------

    products_df = transform_products(
        products_data
    )

    users_df = transform_users(
        users_data
    )

    carts_df = transform_carts(
        carts_data
    )

    cart_items_df = transform_cart_items(
        carts_data
    )

    # --------------------------------------------------------
    # Save processed data
    # --------------------------------------------------------

    save_csv(
        products_df,
        "products_clean.csv"
    )

    save_csv(
        users_df,
        "users_clean.csv"
    )

    save_csv(
        carts_df,
        "carts_clean.csv"
    )

    save_csv(
        cart_items_df,
        "cart_items_clean.csv"
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    logger.info(
        "========================================"
    )

    logger.info(
        "TRANSFORMATION COMPLETED"
    )

    logger.info(
        "Products     : %s rows",
        len(products_df)
    )

    logger.info(
        "Users        : %s rows",
        len(users_df)
    )

    logger.info(
        "Carts        : %s rows",
        len(carts_df)
    )

    logger.info(
        "Cart Items   : %s rows",
        len(cart_items_df)
    )

    logger.info(
        "========================================"
    )


if __name__ == "__main__":
    main()