"""Utility functions for run.py."""

import datetime
import folium
import geopandas as gpd
import logging
import os
import sys

from folium.map import Icon


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
        "interim_uc": os.path.join(interim_dir, "urban_centre"),
        "interim_pop": os.path.join(interim_dir, "population"),
        "interim_gtfs": os.path.join(interim_dir, "gtfs"),
        "interim_osm": os.path.join(interim_dir, "osm"),
        "outputs_dir": outputs_dir,
        "uc_outputs_dir": os.path.join(outputs_dir, "urban_centre"),
        "pop_outputs_dir": os.path.join(outputs_dir, "population"),
        "gtfs_outputs_dir": os.path.join(outputs_dir, "gtfs"),
        "an_outputs_dir": os.path.join(outputs_dir, "analyse_network"),
        "metrics_outputs_dir": os.path.join(outputs_dir, "metrics"),
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


def plot(
    gdf: gpd.GeoDataFrame,
    column: str = None,
    column_control_name: str = None,
    uc_gdf: gpd.GeoDataFrame = None,
    show_uc_gdf: bool = True,
    point: gpd.GeoDataFrame = None,
    show_point: bool = False,
    point_control_name: str = "POI",
    point_color: str = "red",
    point_buffer: int = None,
    overlay: gpd.GeoDataFrame = None,
    overlay_control_name: str = "Overlay",
    cmap: str = "viridis_r",
    color: str = "#12436D",
    caption: str = None,
    max_labels: int = 9,
    save: str = None,
) -> folium.Map:
    """Plot travel times/transport performance.

    Parameters
    ----------
    gdf : gpd.GeoDataFrame
        The geospatial dataframe to visualise
    column : str, optional
        Column within the dataframe to visualise, by default None meaning no
        colourmap will be added
    column_control_name : str, optional
        Name to column to appear in folium control layer, by default None
        meaning the column name will be used in the folium control layer
    uc_gdf : gpd.GeoDataFrame, optional
        The urban centre geodataframe, by default None meaning no urban centre
        will be added to the visualisation.
    show_uc_gdf : bool, optional
        Boolean flag to control whether the urban centre is displayed on
        opening, by default True meaning it will be initially displayed until
        it is deselected on the contol layer
    point : gpd.GeoDataFrame, optional
        Point of interest marker to be added to the visual, by default None
        meaning no plot will be added.
    show_point : bool, optional
        Boolean flag to control whether the point of interest is displayed on
        opening, by default False meaning it will not be displayed initially
        until it is selected on the control layer.
    point_control_name : str, optional
        Name to give the point of interest in the layer control, by default
        "POI",
    point_color : str, optional
        Color of the point of interest marker, by default "red"
    point_buffer : int, optional
        Distance, in m, to added a dashed line from the point of interest,
        by default None meaning no buffer will be added
    overlay : gpd.GeoDataFrame, optional
        An extra geodataframe that can be added as an overlay layer to the
        visual, by default None meaning no overlay is added
    overlay_control_name : str, optional
        Name of the overlay layer in the overlay control menu, by default
        "Overlay".
    cmap : str, optional
        Color map to use for visualising data, by default "viridis_r". Only
        used when `column` is not None.
    color : str, optional
        Color to set the data (i.e. a fixed value), by default "#12436D". Only
        used when `cmap` is set to None.
    caption : str, optional
        Legend caption, by default None meaning `column` will be used.
    max_labels : int, optional
        Maximum number of legend labels, by default 9. Useful to control the
        distance between legend ticks.
    save : str, optional
        Location to save file, by default None meaning no file will be saved.

    Returns
    -------
    folium.Map
        Folium visualisation output

    """
    # create an empty map layer so individual tiles can be addeded
    m = folium.Map(tiles=None, control_scale=True, zoom_control=True)

    # infromation for carto positron tile
    tiles = "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
    attr = (
        '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStre'
        'etMap</a> contributors &copy; <a href="https://carto.com/attribut'
        'ions">CARTO</a>'
    )

    # add Carto Positron tile layer
    folium.TileLayer(
        name="Carto Positron Basemap",
        tiles=tiles,
        attr=attr,
        show=True,
        control=True,
    ).add_to(m)

    # add OpenStreetMap tile layer
    folium.TileLayer(
        name="OpenStreetMap Basemap",
        show=False,
        control=True,
    ).add_to(m)

    # handle legend configuration
    legend_kwds = {}
    if caption is not None:
        legend_kwds["caption"] = caption
    legend_kwds["max_labels"] = max_labels

    # handle setting column layer name in control menu
    if column_control_name is None:
        column_control_name = column

    # add data to the map
    m = gdf.explore(
        column,
        m=m,
        color=color,
        cmap=cmap,
        legend_kwds=legend_kwds,
        name=column_control_name,
    )

    # add the urban centre layer, if one is provided
    if uc_gdf is not None:
        m = uc_gdf.explore(
            m=m,
            color="red",
            style_kwds={"fill": None},
            name="Urban Centre",
            show=show_uc_gdf,
        )

    # add a point marker to the map, if one is provided
    if point is not None:
        marker_kwds = {
            "icon": Icon(
                color="red",
                prefix="fa",
                icon="flag-checkered",
            )
        }
        m = point.explore(
            m=m,
            name=point_control_name,
            marker_type="marker",
            marker_kwds=marker_kwds,
            show=show_point,
        )

        # add in a dashed buffer around the point, if requested
        if point_buffer is not None:
            m = (
                point.to_crs("EPSG:27700")
                .buffer(point_buffer)
                .explore(
                    m=m,
                    color=point_color,
                    style_kwds={"fill": None, "dashArray": 5},
                    name="Max Distance from Destination",
                    show=show_point,
                )
            )

    # add in an extra overlay layer, if requested
    if overlay is not None:
        m = overlay.explore(
            m=m,
            color="#F46A25",
            name=overlay_control_name,
        )

    # get and fit the bounds to the added map layers
    m.fit_bounds(m.get_bounds())

    # add a layer control button
    folium.LayerControl().add_to(m)

    # write to file if requested
    if save is not None:
        dir_name = os.path.dirname(save)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        m.save(save)

    return m


def env_var_none_defence(env_var: str, var_name: str) -> None:
    """Environment variable defences against None values.

    Handles 3 cases:
    1. `None` - when os.getenv() fails
    2. "None" - the default set in the docker-compose.yaml
    3. "" - when the default in docker-compose.yaml is removed (default
    docker behaviour is to set an empty string).

    Parameters
    ----------
    env_var : str
        the environment variable value
    var_name : str
        the name of the environment variable

    Raises
    ------
    ValueError
        When the environment variable is not set as required.

    """
    if (env_var is None) or (env_var == "None") or (env_var == ""):
        raise ValueError(f"{var_name} is a required environment variable.")


def gtfs_osm_subdir_name(country_name: str, gtfs_osm_subdir: str) -> str:
    """Set up the gtfs_osm_subdir variable.

    If default case (where GTFS_OSM_SUBDIR env var is not set), the will use
    the COUNTRY_NAME env var. Else, will use the GTFS_OSM_SUBDIR env var value.
    In both cases, OSM and GTFS sub folder existences are checked.

    Parameters
    ----------
    country_name : str
        value of COUNTRY_NAME env var.
    gtfs_osm_subdir : str
        value of GTFS_OSM_SUBDIR env var.

    Returns
    -------
    str
        value to use for gtfs_osm_subdir variable.

    """
    if (
        (gtfs_osm_subdir is None)
        or (gtfs_osm_subdir == "None")
        or (gtfs_osm_subdir == "")
    ):
        _gtfs_osm_dir_check(country_name)
        return country_name
    else:
        _gtfs_osm_dir_check(gtfs_osm_subdir)
        return gtfs_osm_subdir


def _gtfs_osm_dir_check(subdir: str):
    """Check if a OSM and GTFS subdirectory exists."""
    osm_check = os.path.join("./data/inputs/", subdir, "osm")
    gtfs_check = os.path.join("./data/inputs/", subdir, "gtfs")
    if not os.path.exists(osm_check):
        raise FileNotFoundError(f"{osm_check} does not exist.")
    elif not os.path.exists(gtfs_check):
        raise FileNotFoundError(f"{gtfs_check} does not exist.")
