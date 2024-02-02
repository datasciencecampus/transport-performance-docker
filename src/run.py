"""src/run.py."""

import datetime
import geopandas as gpd
import pandas as pd
import glob
import os
import toml

from shapely.geometry import box
from transport_performance.urban_centres.raster_uc import UrbanCentre
from transport_performance.population.rasterpop import RasterPop
from transport_performance.gtfs.multi_validation import MultiGtfsInstance
from transport_performance.osm.osm_utils import filter_osm
from transport_performance.analyse_network import AnalyseNetwork
from transport_performance.metrics import transport_performance
from transport_performance.utils.raster import (
    sum_resample_file,
    merge_raster_files,
)
from r5py import TransportMode
from pathlib import Path
from copy import deepcopy
from branca import colormap

from utils import create_dir_structure, setup_logger, plot

# set the container logger name
LOGGER_NAME = "tp-docker-analysis"
CONFIG_PREFIX = "data/inputs/config/"


def main():
    """Execute end-to-end analysis."""
    # immediate error handling (to fail fast)
    # TODO: add in other immediate input error handling
    osm_file = glob.glob("data/inputs/osm/*.pbf")
    if len(osm_file) == 0:
        raise FileNotFoundError("No OSM input data found.")
    elif len(osm_file) > 1:
        raise ValueError(
            "Too many OSM files in input folder. Unable to determine correct "
            "input. Remove unnecessary inputs from this directory."
        )
    else:
        osm_file = Path(osm_file[0])

    # read and split out config into separate configs to minimise line lengths
    config_file = os.path.join(CONFIG_PREFIX, os.getenv("CONFIG_FILE"))
    config = toml.load(config_file)
    general_config = config["general"]
    uc_config = config["urban_centre"]
    pop_config = config["population"]
    # gtfs_config = config["gtfs"]
    osm_config = config["osm"]
    analyse_net_config = config["analyse_network"]

    # get environmental variables
    country_name = os.getenv("COUNTRY_NAME").capitalize()
    area_name = os.getenv("AREA_NAME").capitalize()
    bbox = [float(x) for x in os.getenv("BBOX").split(",")]
    bbox_crs = os.getenv("BBOX_CRS")
    centre = [float(x) for x in os.getenv("CENTRE").split(",")]
    centre_crs = os.getenv("CENTRE_CRS")
    empty_feed = bool(int(os.getenv("EMPTY_FEED")))
    fast_travel = bool(int(os.getenv("FAST_TRAVEL")))
    calculate_summaries = bool(int(os.getenv("CALCULATE_SUMMARIES")))
    batch_orig = bool(int(os.getenv("BATCH_ORIG")))

    # create directory structure upfront
    dirs = create_dir_structure(area_name, add_time=True)

    logger = setup_logger(
        LOGGER_NAME,
        file_name=os.path.join(
            dirs["logger_dir"], f"{area_name}_analysis.txt"
        ),
    )
    logger.info(f"Analysing transport performane of {area_name}")
    logger.info(f"Created analysis directory structure at {dirs['files_dir']}")
    logger.info(f"Using config file: {config_file}")
    logger.info(f"Using area_name: {country_name}")
    logger.info(f"Using area_name: {area_name}")
    logger.info(f"Using bbox: {bbox}")
    logger.info(f"Using bbox_crs: {bbox_crs}")
    logger.info(f"Using centre: {centre}")
    logger.info(f"Using centre_crs: {centre_crs}")
    logger.info(f"Using empty_feed: {empty_feed}")
    logger.info(f"Using fast_travel: {fast_travel}")
    logger.info(f"Using calculate_summaries: {calculate_summaries}")
    logger.info(f"Using batch_orig: {batch_orig}")

    logger.info("Detecting urban centre...")
    # put bbox into a geopandas dataframe for `get_urban_centre` input
    bbox_gdf = gpd.GeoDataFrame(geometry=[box(*bbox)], crs=bbox_crs)
    if bbox_crs != "ESRI:54009":
        logger.info(f"Convering bbox_gdf from {bbox_crs} to 'ESRI:54009'")
        bbox_gdf.to_crs("ESRI:54009", inplace=True)

    # merge input raster files
    logger.info("Merging input urban centre raster files...")
    merged_uc_file = os.path.join(
        dirs["interim_uc"], "urban_centre_merged.tif"
    )
    merge_raster_files(
        "data/inputs/urban_centre/",
        os.path.dirname(merged_uc_file),
        os.path.basename(merged_uc_file),
        subset_regex=uc_config["subset_regex"],
    )

    # detect urban centre
    uc = UrbanCentre(merged_uc_file)
    uc_gdf = uc.get_urban_centre(
        bbox_gdf,
        centre=tuple(centre),
        centre_crs=centre_crs,
        buffer_size=uc_config["buffer_size"],
        buffer_estimation_crs=uc_config["buffer_estimation_crs"],
    )

    # set the index to the label column to make filtering easier
    uc_gdf.set_index("label", inplace=True)

    # visualise outputs
    m = uc_gdf[::-1].reset_index().explore("label", cmap="viridis")
    uc_map_path = os.path.join(dirs["uc_outputs_dir"], "urban_centre.html")
    m.save(uc_map_path)
    logger.info(f"Saved urban centre map: {uc_map_path}")

    uc_output_path = os.path.join(dirs["uc_outputs_dir"], "uc_gdf.parquet")
    uc_gdf.to_parquet(uc_output_path, index=False)
    logger.info(f"Saved urban centre output to parquet: {uc_output_path}")

    logger.debug("Removing `uc` memory allocation...")
    del uc  # remove uc memory alloc
    logger.info("Urban centre detection complete.")

    # merge input population raster files
    logger.info("Merging input population raster files...")
    merged_pop_file = os.path.join(
        dirs["interim_pop"], "population_merged.tif"
    )
    merge_raster_files(
        "data/inputs/population/",
        os.path.dirname(merged_pop_file),
        os.path.basename(merged_pop_file),
        subset_regex=pop_config["subset_regex"],
    )

    logger.info("Resampling population data...")
    pop_filename = os.path.basename(merged_pop_file).replace(
        ".tif", "_resampled.tif"
    )
    pop_input = os.path.join(dirs["interim_pop"], pop_filename)
    sum_resample_file(merged_pop_file, pop_input)

    # extract geometries from urban centre detection
    logger.info("Pre-process population data using detected urban centre...")
    aoi_bounds = uc_gdf.loc["buffer"].geometry
    urban_centre_bounds = uc_gdf.loc["vectorized_uc"].geometry

    # get population data
    rp = RasterPop(pop_input)
    pop_gdf, centroid_gdf = rp.get_pop(
        aoi_bounds,
        threshold=pop_config["threshold"],
        urban_centre_bounds=urban_centre_bounds,
    )
    plot_output = os.path.join(dirs["pop_outputs_dir"], "population.html")
    plot(
        pop_gdf,
        column="population",
        column_control_name="Population",
        cmap="viridis",
        uc_gdf=uc_gdf[0:1],
        save=plot_output,
    )
    logger.info(f"Saved population map: {plot_output}")

    pop_outputs_centroids = os.path.join(
        dirs["pop_outputs_dir"], "pop_centroid.parquet"
    )
    rp.centroid_gdf.to_parquet(pop_outputs_centroids, index=False)
    logger.info(
        f"Saved population centroids to parquet: {pop_outputs_centroids}"
    )

    pop_outputs_gdf = os.path.join(
        dirs["pop_outputs_dir"], "pop_centroid.parquet"
    )
    rp.pop_gdf.to_parquet(pop_outputs_gdf, index=False)
    logger.info(f"Save population gdf to parquet: {pop_outputs_gdf}")

    logger.debug("Removing `rp` memory allocation...")
    del rp  # removing rp memory alloc
    logger.info("Population pre-processing complete.")

    logger.info("Reading GTFS inputs...")
    gtfs = MultiGtfsInstance("data/inputs/gtfs/*.zip")

    logger.info("Clipping GTFS data to urban centre bounding box...")
    gtfs_bbox = list(uc_gdf.to_crs("EPSG:4326").loc["bbox"].geometry.bounds)
    gtfs.filter_to_bbox(gtfs_bbox, delete_empty_feeds=empty_feed)

    # display min, max, and no unique dates across all GTFS inputs
    gtfs_dates = set()
    for inst in gtfs.instances:
        gtfs_dates.update(inst.feed.get_dates())
    logger.info(
        f"{len(gtfs_dates)} dates available between {min(gtfs_dates)} & "
        f"{max(gtfs_dates)}."
    )

    logger.info("Validating filtered GTFS...")
    gtfs.is_valid({"far_stops": fast_travel})
    pre_clean_valid_path = os.path.join(
        dirs["gtfs_outputs_dir"], "pre_clean_validity.csv"
    )
    gtfs.validity_df.to_csv(pre_clean_valid_path, index=False)
    logger.info(f"Pre-cleaning validity data saved: {pre_clean_valid_path}")

    logger.info("Cleaning filtered GTFS...")
    gtfs.clean_feeds({"fast_travel": fast_travel})

    logger.info("Validating filtered GTFS post cleaning...")
    gtfs.is_valid({"far_stops": fast_travel})
    post_clean_valid_path = os.path.join(
        dirs["gtfs_outputs_dir"], "post_clean_validity.csv"
    )
    gtfs.validity_df.to_csv(post_clean_valid_path, index=False)
    logger.info(f"Post-cleaning validity data saved: {post_clean_valid_path}")

    if calculate_summaries:
        post_clean_route_summary_path = os.path.join(
            dirs["gtfs_outputs_dir"], "post_cleaning_routes_summary.csv"
        )
        route_summary = gtfs.summarise_routes(to_days=False)
        route_summary.to_csv(post_clean_route_summary_path, index=False)
        logger.info(
            "Post-cleaning routes summary saved: "
            f"{post_clean_route_summary_path}"
        )

        post_clean_trip_summary_path = os.path.join(
            dirs["gtfs_outputs_dir"], "post_clean_trips_summary.csv"
        )
        trip_summary = gtfs.summarise_trips(to_days=False)
        trip_summary.to_csv(post_clean_trip_summary_path, index=False)
        logger.info(
            "Post-cleaning trips summary saved: "
            f"{post_clean_trip_summary_path}"
        )
    else:
        logger.warning(
            "`calculate summaries` in config toml is False, therefore route/"
            "trip summaries were skipped."
        )

    # TODO: remove when fix is implemented
    # some GTFS do not have stop_code (optional column in GTFS) and this limits
    # `viz_stop`. This creates a dummy `stop_code` column that duplicates the
    # `stop_id` data for the purposes of plotting. Create a copy to prevent
    # working on the original (prevents saving edited data later)
    viz_gtfs = deepcopy(gtfs)
    for inst in viz_gtfs.instances:
        if "stop_code" not in inst.feed.stops.columns:
            inst.feed.stops["stop_code"] = inst.feed.stops["stop_id"]

    stops_map_path = os.path.join(dirs["gtfs_outputs_dir"], "stops.html")
    viz_gtfs.viz_stops(stops_map_path, return_viz=False)
    logger.info(f"Post-cleaning stops map saved: {stops_map_path}")

    logger.info("Writing cleaned GTFS to file...")
    gtfs.filter_to_date(general_config["date"], delete_empty_feeds=empty_feed)

    # manually create a synthetic calendar.txt for R5PY to detect valid dates
    for inst in gtfs.instances:
        if inst.feed.calendar is None:
            logger.warning("Creating a synthetic calendar.txt...")
            # get unique service ids from calendar_dates.txt
            calendar_df = pd.DataFrame(
                inst.feed.calendar_dates.service_id.unique(),
                columns=["service_id"],
            )

            # set all days to zero - allow calendar_dates to control schedule
            calendar_df.loc[:, "monday"] = 0
            calendar_df.loc[:, "tuesday"] = 0
            calendar_df.loc[:, "wednesday"] = 0
            calendar_df.loc[:, "thursday"] = 0
            calendar_df.loc[:, "friday"] = 0
            calendar_df.loc[:, "saturday"] = 0
            calendar_df.loc[:, "sunday"] = 0

            # set start/end date to be either side of analysis date
            date_dt = datetime.datetime.strptime(
                general_config["date"], "%Y%m%d"
            )
            calendar_df.loc[:, "start_date"] = (
                date_dt - datetime.timedelta(days=1)
            ).strftime("%Y%m%d")
            calendar_df.loc[:, "end_date"] = (
                date_dt + datetime.timedelta(days=1)
            ).strftime("%Y%m%d")

            inst.feed.calendar = calendar_df

    gtfs.save_feeds(dirs["interim_gtfs"])
    logger.debug("Removing `gtfs` memory allocation...")
    del gtfs  # remove gtfs memory alloc
    del viz_gtfs  # remove viz_gtfs alloc TODO: remove when fix is implemented
    logger.info("GTFS processing complete.")

    logger.info("Cropping OSM input to urban centre BBOX...")
    osm_bbox = list(uc_gdf.to_crs("EPSG:4326").loc["bbox"].geometry.bounds)
    filtered_osm_path = Path(
        os.path.join(dirs["interim_osm"], "filtered.osm.pbf")
    )
    filter_osm(
        pbf_pth=osm_file,
        out_pth=filtered_osm_path,
        bbox=osm_bbox,
        tag_filter=osm_config["tag_filter"],
    )
    logger.info("OSM cropping complete.")

    logger.info("Building transport network...")
    gtfs_filtered_paths = glob.glob(f"{dirs['interim_gtfs']}/*.zip")
    an = AnalyseNetwork(
        centroid_gdf,
        filtered_osm_path,
        gtfs_filtered_paths,
        dirs["an_outputs_dir"],
    )

    logger.info("Calculating OD matrix...")
    analysis_dt = datetime.datetime.strptime(general_config["date"], "%Y%m%d")
    an.od_matrix(
        batch_orig=batch_orig,
        distance=general_config["max_distance"],
        departure=datetime.datetime(
            analysis_dt.year,
            analysis_dt.month,
            analysis_dt.day,
            analyse_net_config["departure_hour"],
            analyse_net_config["departure_minute"],
        ),
        departure_time_window=datetime.timedelta(
            hours=analyse_net_config["departure_time_window"],
        ),
        max_time=datetime.timedelta(
            minutes=general_config["max_time"],
        ),
        transport_modes=[TransportMode.TRANSIT],
    )
    logger.info(f"OD matrix written to: {dirs['an_outputs_dir']}")
    logger.debug("Removing `an` memory allocation...")
    del an  # remove an memory alloc
    logger.info("Transport network analysis complete.")

    logger.info("Calculating the transport performance...")
    tp_df, stats_df = transport_performance(
        dirs["an_outputs_dir"],
        centroid_gdf,
        pop_gdf,
        travel_time_threshold=general_config["max_time"],
        distance_threshold=general_config["max_distance"],
        urban_centre_name=area_name,
        urban_centre_country=country_name,
        urban_centre_gdf=uc_gdf.reset_index(),
    )
    logger.info("Transport performance calculated. Saving output files...")
    tp_plot_path = os.path.join(
        dirs["metrics_outputs_dir"], "transport_performance.html"
    )
    tp_plot_const_cmap_path = os.path.join(
        dirs["metrics_outputs_dir"], "transport_performance_const_cmap.html"
    )
    tp_output_path = os.path.join(
        dirs["metrics_outputs_dir"], "transport_performance.parquet"
    )
    tp_stats_path = os.path.join(
        dirs["metrics_outputs_dir"], "transport_performance_stats.csv"
    )
    plot(
        tp_df,
        column="transport_performance",
        column_control_name="Transport Performance",
        uc_gdf=uc_gdf[0:1],
        cmap="viridis",
        caption="Transport Performance (%)",
        save=tp_plot_path,
    )
    const_cmap = colormap.LinearColormap(
        colors=[
            "#440154",
            "#414487",
            "#2A788E",
            "#22A884",
            "#7AD151",
            "#FDE725",
        ],
        vmin=0,
        vmax=100,
        max_labels=11,
        tick_labels=list(range(0, 110, 10)),
    )
    plot(
        tp_df,
        column="transport_performance",
        column_control_name="Transport Performance",
        uc_gdf=uc_gdf[0:1],
        cmap=const_cmap,
        caption="Transport Performance (%)",
        save=tp_plot_const_cmap_path,
    )
    stats_df.to_csv(tp_stats_path, index=False)
    tp_df.to_parquet(tp_output_path, index=False)
    logger.info(f"Transport performance map saved: {tp_plot_path}")
    logger.info(
        "Transport performance map (constant cmap) saved: "
        f"{tp_plot_const_cmap_path}"
    )
    logger.info(f"Transport performance stats saved: {tp_stats_path}")
    logger.info(f"Transport performance parquet saved: {tp_output_path}")

    logger.info(
        f"*** Transport performance analysis of {area_name} " "complete! ***"
    )


if __name__ == "__main__":
    main()
