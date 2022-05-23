import logging
import time

from logging.handlers import RotatingFileHandler


def get_rotating_log(path: str) -> logging.Logger:
    """Creates a rotating log object that writes to a file and the console"""
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    
    # add a rotating handler
    rot_handler = RotatingFileHandler(path, 
                                maxBytes=1000000,
                                backupCount=1)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(c_format)
    rot_handler.setFormatter(f_format)

    logger.addHandler(rot_handler)
    logger.addHandler(console_handler)

    return logger 
