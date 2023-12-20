"""Utility functions for run.py."""

import datetime
import os


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

    dirs = {
        "files_dir": files_dir,
        "interim_dir": interim_dir,
        "interim_pop": os.path.join(interim_dir, "population"),
        "interim_gtfs": os.path.join(interim_dir, "gtfs"),
        "interim_osm": os.path.join(interim_dir, "osm"),
        "outputs_dir": os.path.join(files_dir, "outputs"),
    }

    for dir in dirs.values():
        os.makedirs(dir)

    return dirs
