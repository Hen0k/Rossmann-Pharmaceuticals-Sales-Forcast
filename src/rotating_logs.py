import logging
import time
import os

from logging.handlers import RotatingFileHandler
from fsutil import split_path


# Helper methods
def is_root_dir() -> bool:
    """This helps us get a the path to the root of the repo"""
    cwd = os.getcwd()
    folders = split_path(cwd)
    folder = folders[-1]
    repo_name = 'Rossmann-Pharmaceuticals-Sales-Forcast'
    if folder == repo_name:
        return True
    else:
        return False


def get_rotating_log(filename: str, logger_name: str) -> logging.Logger:
    """Creates a rotating log object that writes to a file and the console"""

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    # add a rotating handler
    if is_root_dir():
        path = os.path.join('logs/', filename)
    else:
        path = os.path.join('../logs/', filename)
    rot_handler = RotatingFileHandler(path,
                                      maxBytes=1000000,
                                      backupCount=1)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    f_format = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    console_handler.setFormatter(c_format)
    rot_handler.setFormatter(f_format)

    logger.addHandler(rot_handler)
    logger.addHandler(console_handler)

    return logger
