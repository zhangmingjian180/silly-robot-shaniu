import logging
logging.basicConfig(
    format="[ %(asctime)s : %(funcName)s : %(levelname)s ] %(message)s",
    level=logging.DEBUG)

from log import uvicorn_log_file
from config import LOG_DIR
uvicorn_log_file(LOG_DIR)

from api import app
