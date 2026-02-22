import logging
from pythonjsonlogger import jsonlogger
from pathlib import Path

LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logger.handlers = []

    log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"

    formatter = jsonlogger.JsonFormatter(log_format)

    # Inference log
    inference_handler = logging.FileHandler(LOG_DIR / "inference.log")
    inference_handler.setLevel(logging.INFO)
    inference_handler.setFormatter(formatter)

    # Error log
    error_handler = logging.FileHandler(LOG_DIR / "error.log")
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)

    # Console log
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    logger.addHandler(inference_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
