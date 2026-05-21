import logging
import os
from pythonjsonlogger import jsonlogger
def init_logging(level: str = None):
    level = level or os.getenv("LOG_LEVEL", "INFO")
    log_level = getattr(logging, level.upper(), logging.INFO)

    handler = logging.StreamHandler()
    fmt = jsonlogger.JsonFormatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(fmt)
    app_logger = logging.getLogger("app")
    if not any(isinstance(h, logging.StreamHandler) for h in app_logger.handlers):
        app_logger.addHandler(handler)
    app_logger.setLevel(log_level)
    app_logger.propagate = False
    logging.getLogger().setLevel(log_level)
