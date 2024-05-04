import logging


logging.basicConfig(
    level=logging.INFO, format="%(name)s %(asctime)s %(levelname)s %(message)s"
)


def get_logger(name) -> logging.Logger:
    """Получаем настроеный логер."""
    return logging.getLogger(name)
