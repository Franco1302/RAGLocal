import logging


def configure_logging(level: str = "INFO") -> None:
    """Configura formato y nivel global de logging para la aplicacion."""
    logging.basicConfig(
        level=level.upper(),
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    )
