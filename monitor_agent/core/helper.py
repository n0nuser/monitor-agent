import logging


def getLogger(level: str, filename: str) -> logging.Logger:
    """Creates a logger.

    Args:
        level (str): Could be "debug", "info", "warning", "error", "critical".
        filename (str): File to write the logs.
    """
    translation = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    log_level = translation.get(level, logging.INFO)
    log_filename = filename or "monitor.log"

    logging.basicConfig(
        level=log_level,
        filename=log_filename,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )
