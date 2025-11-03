# app/logger.py
import logging

def setup_logger():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO
    )
    return logging.getLogger("smsbot")

logger = setup_logger()
