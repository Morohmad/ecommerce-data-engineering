import logging
import subprocess
import sys


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger(__name__)


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


def main():

    logger.info(
        "========================================"
    )

    logger.info(
        "STARTING PHASE 2 ETL PIPELINE"
    )

    logger.info(
        "========================================"
    )

    # --------------------------------------------------------
    # STEP 1
    # Transformation
    # --------------------------------------------------------

    run_step(
        "transform.py"
    )

    # --------------------------------------------------------
    # STEP 2
    # Data quality validation
    # --------------------------------------------------------

    run_step(
        "validate_processed.py"
    )

    # --------------------------------------------------------
    # STEP 3
    # Load to PostgreSQL
    # --------------------------------------------------------

    run_step(
        "load_clean.py"
    )

    # --------------------------------------------------------
    # Completed
    # --------------------------------------------------------

    logger.info(
        "========================================"
    )

    logger.info(
        "PHASE 2 ETL PIPELINE COMPLETED"
    )

    logger.info(
        "========================================"
    )


if __name__ == "__main__":
    main()