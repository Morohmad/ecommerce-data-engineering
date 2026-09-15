import json
import logging
from datetime import datetime, timezone
from pathlib import Path

from api_client import DummyJSONClient
from config import API_BASE_URL, RAW_DATA_DIR


# --------------------------------------------------
# Logging configuration
# --------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def save_json(
    data: dict,
    file_path: Path,
) -> None:
    """
    Menyimpan data API ke file JSON.
    """

    with file_path.open(
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False,
        )


# --------------------------------------------------
# Main extraction process
# --------------------------------------------------

def main() -> None:

    logger.info("Starting API extraction...")

    client = DummyJSONClient(
        base_url=API_BASE_URL
    )

    # Timestamp extraction
    extracted_at = datetime.now(
        timezone.utc
    ).isoformat()

    # --------------------------------------------------
    # Extract products
    # --------------------------------------------------

    logger.info("Extracting products...")

    products = client.get_products()

    products["extracted_at"] = extracted_at

    products_file = RAW_DATA_DIR / "products.json"

    save_json(
        products,
        products_file,
    )

    logger.info(
        "Products saved: %s",
        products_file,
    )

    # --------------------------------------------------
    # Extract users
    # --------------------------------------------------

    logger.info("Extracting users...")

    users = client.get_users()

    users["extracted_at"] = extracted_at

    users_file = RAW_DATA_DIR / "users.json"

    save_json(
        users,
        users_file,
    )

    logger.info(
        "Users saved: %s",
        users_file,
    )

    # --------------------------------------------------
    # Extract carts
    # --------------------------------------------------

    logger.info("Extracting carts...")

    carts = client.get_carts()

    carts["extracted_at"] = extracted_at

    carts_file = RAW_DATA_DIR / "carts.json"

    save_json(
        carts,
        carts_file,
    )

    logger.info(
        "Carts saved: %s",
        carts_file,
    )

    logger.info(
        "Extraction completed successfully."
    )


# --------------------------------------------------
# Entry point
# --------------------------------------------------

if __name__ == "__main__":
    main()