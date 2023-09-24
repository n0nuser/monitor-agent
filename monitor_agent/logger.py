import logging


def get_logger(level: str) -> logging.Logger:
    """Creates a logger.

    Args:
        level (str): Could be "debug", "info", "warning", "error", "critical".
    """
    translation = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL,
    }
    log_level = translation.get(level, logging.INFO)

    # Create a logger
    logger = logging.getLogger()

    # Create a formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Create a stream handler and set the log level
    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(log_level)
    stream_handler.setFormatter(formatter)

    # Add the stream handler to the logger
    logger.addHandler(stream_handler)

    # Set the overall logger level
    logger.setLevel(log_level)

    return logger


LOGGER = get_logger("info")
