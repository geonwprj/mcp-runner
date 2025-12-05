# config/base.py

import logging
from dotenv import load_dotenv
import os

load_dotenv(os.getenv("ENV_FILE", ".env"))

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
logger.addHandler(logging.StreamHandler())
logger.propagate = False

HOST = os.getenv("HOST", "0.0.0.0")
PORT = os.getenv("PORT", 8000)
TRANSPORT = os.getenv("TRANSPORT", "streamable-http")

LOCAL_WORKING_PATH = os.getenv("LOCAL_WORKING_PATH", "/tmp")
