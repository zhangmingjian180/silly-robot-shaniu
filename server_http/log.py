import logging
import datetime
import os.path
import os
from concurrent_log_handler import ConcurrentRotatingFileHandler
import uvicorn.logging

def uvicorn_log_file(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    elif not os.path.isdir(dirname):
        raise OSError(f"{dirname} is a file, not a dir.")
    else:
        pass

    logger = logging.getLogger("uvicorn.access")
    formatter = uvicorn.logging.AccessFormatter(
        fmt='[ %(asctime)s ] %(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        datefmt="%Y-%m-%d %H:%M:%S")

    for i in range(len(logger.handlers)):
        logger.handlers[i].setFormatter(formatter)

    uvicornLogger = logging.getLogger("uvicorn")
    filename = os.path.join(dirname, uvicornLogger.name + ".log")
    rotateHandler = ConcurrentRotatingFileHandler(filename, 'a', 128 * 1024 * 1024, 5)

    for e in uvicornLogger.handlers:
        rotateHandler.setFormatter(e.formatter)
        uvicornLogger.removeHandler(e)
        uvicornLogger.addHandler(rotateHandler)

    loggers = uvicornLogger.getChildren()
    for logger in loggers:
        filename = os.path.join(dirname, logger.name + ".log")
        rotateHandler = ConcurrentRotatingFileHandler(filename, 'a', 128 * 1024 * 1024, 5)
        for e in logger.handlers:
            rotateHandler.setFormatter(e.formatter)
            logger.removeHandler(e)
            logger.addHandler(rotateHandler)

def fastapi_log(dirname, loglevel):
    name = "fastapi"

    if not os.path.exists(dirname):
        os.makedirs(dirname)
    elif not os.path.isdir(dirname):
        raise OSError(f"{dirname} is a file, not a dir.")
    else:
        pass

    formatter = "[ %(asctime)s : %(levelname)s ] %(message)s"
    level = logging.WARNING

    if loglevel == "DEBUG":
        level = logging.DEBUG
    elif loglevel == "INFO":
        level = logging.INFO
    elif loglevel == "ERROR":
        level = logging.ERROR
    elif loglevel == "CRITICAL":
        level = logging.CRITICAL
    else:
        pass

    fastapiLogger = logging.getLogger(name)
    fastapiLogger.setLevel(level)
    filename = os.path.join(dirname, fastapiLogger.name + ".log")
    rotateHandler = ConcurrentRotatingFileHandler(filename, 'a', 128 * 1024 * 1024, 5)
    rotateHandler.setFormatter(logging.Formatter(formatter))
    fastapiLogger.addHandler(rotateHandler)

    return fastapiLogger

#fastapiLogger = fastapi_log(LOG_DIR, LOG_LEVEL)
