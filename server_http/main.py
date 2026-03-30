import logging
logging.basicConfig(
    format="[ %(asctime)s : %(funcName)s : %(levelname)s ] %(message)s",
    level=logging.DEBUG
)

from api import app
