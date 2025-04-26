import logging
from logging.handlers import RotatingFileHandler
import os

def setup_logger(name: str, log_file: str, level=logging.INFO):
    formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s')

    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    handler = RotatingFileHandler(log_file, maxBytes=5*1024*1024, backupCount=5)
    handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        logger.addHandler(handler)
        logger.addHandler(console_handler)

    return logger
