import logging

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
