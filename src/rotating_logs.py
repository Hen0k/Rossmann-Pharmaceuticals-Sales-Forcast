import logging
import time
import os

from logging.handlers import RotatingFileHandler
from fsutil import split_path


# Helper methods
def get_root_dir() -> None:
    """This helps us get a the path to the root of the repo"""
    cwd = os.getcwd()
    folders = split_path(cwd)
    repo_name = 'Rossmann-Pharmaceuticals-Sales-Forcast'
    if folder == repo_name:
        return '/'.join(folders[:-1])
    else:
        for idx, folder in enumerate(folders[::-1]):
            idx = -1*idx-1
            if folder == repo_name:
                return '/'.join(folders[:idx])


def get_rotating_log(filename: str) -> logging.Logger:
    """Creates a rotating log object that writes to a file and the console"""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    repo_root = get_root_dir()
    log_file_path = os.path.join(repo_root, 'logs', filename)
    # add a rotating handler
    rot_handler = RotatingFileHandler(log_file_path,
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
