import logging
import subprocess
import sys


# ============================================================
# LOGGING
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


# ============================================================
# RUN SCRIPT
# ============================================================

def run_step(
    script_name: str
):

    logger.info(
        "========================================"
    )

    logger.info(
        "RUNNING: %s",
        script_name
    )

    logger.info(
        "========================================"
    )

    result = subprocess.run(
        [
            sys.executable,
            f"src/{script_name}",
        ],
        check=False,
    )

    if result.returncode != 0:

        raise RuntimeError(
            f"{script_name} failed "
            f"with exit code "
            f"{result.returncode}"
        )


# ============================================================
# MAIN
# ============================================================

def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "STARTING PHASE 3 WAREHOUSE PIPELINE"
    )

    logger.info(
        "========================================"
    )

    # --------------------------------------------------------
    # STEP 1
    # Build warehouse
    # --------------------------------------------------------

    run_step(
        "warehouse.py"
    )

    # --------------------------------------------------------
    # STEP 2
    # Validate warehouse
    # --------------------------------------------------------

    run_step(
        "validate_warehouse.py"
    )

    # --------------------------------------------------------
    # COMPLETED
    # --------------------------------------------------------

    logger.info(
        "========================================"
    )

    logger.info(
        "PHASE 3 PIPELINE COMPLETED SUCCESSFULLY"
    )

    logger.info(
        "========================================"
    )


if __name__ == "__main__":
    main()