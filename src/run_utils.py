"""Utility functions for run.py."""

import datetime
import logging
import os
import sys


def create_dir_structure(area_name: str, add_time: bool = True) -> dict:
    """Create analysis directory structure.

    Parameters
    ----------
    area_name : str
        Name of the area
    add_time : bool, optional
        Append datetimestamp to analysis folder name, by default True meaning a
        datetimestamp is appended.

    Returns
    -------
    dict
        Directory structure paths.

    """
    if add_time:
        now = datetime.datetime.now().strftime("%Y%m%d_%H%M")
        area_name = area_name + "_"
    else:
        now = ""

    files_dir = os.path.join("data", f"{area_name}{now}")
    interim_dir = os.path.join(files_dir, "interim")
    outputs_dir = os.path.join(files_dir, "outputs")

    dirs = {
        "files_dir": files_dir,
        "interim_dir": interim_dir,
        "interim_pop": os.path.join(interim_dir, "population"),
        "interim_gtfs": os.path.join(interim_dir, "gtfs"),
        "interim_osm": os.path.join(interim_dir, "osm"),
        "outputs_dir": outputs_dir,
        "uc_outputs_dir": os.path.join(outputs_dir, "urban_centre"),
        "logger_dir": os.path.join(outputs_dir, "log"),
    }

    for dir in dirs.values():
        os.makedirs(dir)

    return dirs


def setup_logger(
    logger_name: str,
    level: int = logging.INFO,
    file_name: str = None,
) -> logging.Logger:
    """Build a logger instance.

    Parameters
    ----------
    logger_name : str
        name of logger.
    level : int, optional
        logger level (e.g., logging.DEBUG, logging.WARNING etc.), by default
        logging.INFO.
    file_name : str, optional
        logger filename, if needed to write logs to file, by default None
        meaning log messages will not be written to file.

    Returns
    -------
    logging.Logger
        a logger instance with the requested properties.

    """
    # set up the logger and logging level
    logger = logging.getLogger(logger_name)
    logger.setLevel(level)

    # fix the logger format
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # set up a stream handler
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(sh)

    # set up logger file handler
    if file_name:
        fh = logging.FileHandler(file_name)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    return logger
