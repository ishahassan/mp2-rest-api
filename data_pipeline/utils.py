import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def setup_logging(verbose=False):
    """
    Configure Python's logging system.

    -Use `logging.DEBUG` when `verbose` is `True`.
    -Use `logging.INFO` when `verbose` is `False`.
    -Include the **time, log level, and message** in each log entry.
    """

    log_level = logging.DEBUG if verbose else logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S"
    )


def validate_input(filepath):
    """Check whether the input path exists and is a file.
    Validate that the input path exists and is a file.

    Returns:
        True  — if the file exists
        False — if the file does not exist
    """

    logger = logging.getLogger(__name__)
    p = Path(filepath)

    if not p.is_file():
        logger.error(f"Input file not found: {filepath}")
        return False

    logger.info(f"Input file validated: {filepath}")
    return True