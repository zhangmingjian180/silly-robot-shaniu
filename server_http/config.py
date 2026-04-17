import os

MYSQL_HOST = "127.0.0.1"
MYSQL_PORT = 3306
MYSQL_USER = "root"
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD")
MYSQL_DB = "silly_robot"

ACCESS_TOKEN_EXPIRE_DAYS = 30

LOG_DIR = "/var/log/silly-robot-shaniu"
LOG_LEVEL = "DEBUG"
