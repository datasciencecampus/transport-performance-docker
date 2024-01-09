"""src/run.py."""

import datetime
import geopandas as gpd
import gtfs_kit as gk
import glob
import os
import pandas as pd
import toml

from shapely.geometry import box
from transport_performance.urban_centres.raster_uc import UrbanCentre
from transport_performance.population.rasterpop import RasterPop
from transport_performance.gtfs.gtfs_utils import bbox_filter_gtfs
from transport_performance.gtfs.validation import GtfsInstance
from transport_performance.osm.osm_utils import filter_osm
from transport_performance.analyse_network import AnalyseNetwork
from transport_performance.metrics import transport_performance
from transport_performance.utils.raster import (
    sum_resample_file,
    merge_raster_files,
)
from r5py import TransportMode
from pandas.testing import assert_frame_equal
from pathlib import Path

from utils import create_dir_structure, setup_logger, plot

# set the container logger name
LOGGER_NAME = "tp-docker-analysis"
CONFIG_PREFIX = "data/inputs/config/"


def main():
    """Execute end-to-end analysis."""
    # read and split out config into separate configs to minimise line lengths
    config_file = os.path.join(CONFIG_PREFIX, os.getenv("CONFIG_FILE"))
    config = toml.load(config_file)
    general_config = config["general"]
    uc_config = config["urban_centre"]
    pop_config = config["population"]
    gtfs_config = config["gtfs"]
    osm_config = config["osm"]
    analyse_net_config = config["analyse_network"]

    # create directory structure upfront
    dirs = create_dir_structure(general_config["area_name"], add_time=False)

    logger = setup_logger(
        LOGGER_NAME,
        file_name=os.path.join(
            dirs["logger_dir"], f"{general_config['area_name']}_analysis.txt"
        ),
    )
    logger.info(
        f"Analysing transport performane of {general_config['area_name']}"
    )
    logger.info(f"Created analysis directory structure at {dirs['files_dir']}")
    logger.info(f"Using config file {config_file}")

    logger.info("Detecting urban centre...")
    # put bbox into a geopandas dataframe for `get_urban_centre` input
    bbox_gdf = gpd.GeoDataFrame(
        geometry=[box(*uc_config["bbox"])], crs=uc_config["bbox_crs"]
    )
    if uc_config["bbox_crs"] != "ESRI:54009":
        logger.info(
            f"Convering bbox_gdf from {uc_config['bbox_crs']} to 'ESRI:54009'"
        )
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
        centre=tuple(uc_config["centre"]),
        centre_crs=uc_config["centre_crs"],
        buffer_size=uc_config["buffer_size"],
        buffer_estimation_crs=uc_config["buffer_estimation_crs"],
    )

    # set the index to the label column to make filtering easier
    uc_gdf.set_index("label", inplace=True)

    # visualise outputs
    m = uc_gdf[::-1].reset_index().explore("label", cmap="viridis")
    uc_output_path = os.path.join(dirs["uc_outputs_dir"], "urban_centre.html")
    m.save(uc_output_path)
    logger.info(f"Saved urban centre map: {uc_output_path}")
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
    logger.debug("Removing `rp` memory allocation...")
    del rp  # removing rp memory alloc
    logger.info("Population pre-processing complete.")

    # clip gtfs to region of interest, setting crs to match the bbox
    logger.info("Clipping GTFS data to urban centre bounding box.")
    gtfs_bbox = list(uc_gdf.loc["bbox"].geometry.bounds)
    gtfs_filtered_path = Path(
        os.path.join(dirs["interim_gtfs"], "filtered.zip")
    )
    bbox_filter_gtfs(
        in_pth=Path(glob.glob("data/inputs/gtfs/*.zip")[0]),
        out_pth=gtfs_filtered_path,
        bbox=gtfs_bbox,
        units=gtfs_config["units"],
        crs=uc_gdf.crs.to_string(),
    )

    logger.info("Reading filtered GTFS...")
    gtfs = GtfsInstance(
        gtfs_pth=gtfs_filtered_path,
        units=gtfs_config["units"],
        route_lookup_pth="data/inputs/gtfs/route_lookup.pkl",
    )
    available_dates = gtfs.feed.get_dates()
    s = available_dates[0]
    f = available_dates[-1]
    logger.info(f"{len(available_dates)} dates available between {s} & {f}.")

    logger.info("Validating filtered GTFS...")
    gtfs.is_valid()
    pre_clean_valid_path = os.path.join(
        dirs["gtfs_outputs_dir"], "pre_clean_validity.csv"
    )
    gtfs.validity_df.to_csv(pre_clean_valid_path, index=False)
    logger.info(f"Pre-cleaning validity data saved: {pre_clean_valid_path}")

    logger.info("Cleaning filtered GTFS...")
    gtfs.clean_feed()

    logger.info("Validating filtered GTFS post cleaning...")
    gtfs.is_valid()
    post_clean_valid_path = os.path.join(
        dirs["gtfs_outputs_dir"], "post_clean_validity.csv"
    )
    gtfs.validity_df.to_csv(post_clean_valid_path, index=False)
    logger.info(f"Post-cleaning validity data saved: {post_clean_valid_path}")

    logger.info("Calulating trips and routes summarys...")
    route_modes_path = os.path.join(
        dirs["gtfs_outputs_dir"], "route_modes.csv"
    )
    route_modes = gtfs.get_route_modes()
    route_modes.to_csv(route_modes_path)
    logger.info(f"Post-cleaning route modes saved: {route_modes_path}")
    route_summary_path = os.path.join(
        dirs["gtfs_outputs_dir"], "routes_summary.csv"
    )
    route_summary = gtfs.summarise_routes(return_summary=False)
    route_summary.to_csv(route_summary_path)
    logger.info(f"Post-cleaning routes summary saved: {route_summary_path}")
    trip_summary_path = os.path.join(
        dirs["gtfs_outputs_dir"], "trips_summary.csv"
    )
    trip_summary = gtfs.summarise_trips(return_summary=False)
    trip_summary.to_csv(trip_summary_path)
    logger.info(f"Post-cleaning trips summary saved: {trip_summary_path}")
    stops_map_path = os.path.join(dirs["gtfs_outputs_dir"], "stops.html")
    gtfs.viz_stops(stops_map_path)
    logger.info(f"Post-cleaning stops map saved: {stops_map_path}")
    hull_map_path = os.path.join(dirs["gtfs_outputs_dir"], "convex_hull.html")
    gtfs.viz_stops(hull_map_path, geoms="hull")
    logger.info(f"Post-cleaning convex hull map saved: {hull_map_path}")

    logger.info("Writing cleaned GTFS to file...")
    # TODO: remove this date restriction as it is incorrect, but needed to
    # ensure consistency with previous results
    gtfs.feed = gk.miscellany.restrict_to_dates(gtfs.feed, ["20231027"])
    gtfs_filtered_path = Path(
        os.path.join(dirs["interim_gtfs"], "cleaned.zip")
    )
    gtfs.feed.write(gtfs_filtered_path)

    logger.info("Cropping OSM input to urban centre BBOX...")
    osm_bbox = list(uc_gdf.to_crs("EPSG:4326").loc["bbox"].geometry.bounds)
    filtered_osm_path = Path(
        os.path.join(dirs["interim_osm"], "filtered.osm.pbf")
    )
    filter_osm(
        pbf_pth=Path(glob.glob("data/inputs/osm/*.pbf")[0]),
        out_pth=filtered_osm_path,
        bbox=osm_bbox,
        tag_filter=osm_config["tag_filter"],
    )
    logger.info("OSM cropping complete.")

    logger.info("Building transport network...")
    an = AnalyseNetwork(
        centroid_gdf,
        filtered_osm_path,
        [gtfs_filtered_path],
        dirs["an_outputs_dir"],
    )

    logger.info("Calculating OD matrix...")
    an.od_matrix(
        departure=datetime.datetime(
            analyse_net_config["departure_year"],
            analyse_net_config["departure_month"],
            analyse_net_config["departure_day"],
            analyse_net_config["departure_hour"],
            analyse_net_config["departure_minute"],
        ),
        departure_time_window=datetime.timedelta(
            hours=analyse_net_config["departure_time_window"],
        ),
        max_time=datetime.timedelta(
            minutes=analyse_net_config["max_time"],
        ),
        transport_modes=[TransportMode.TRANSIT],
    )
    logger.info(f"OD matrix written to: {dirs['an_outputs_dir']}")

    df1 = pd.read_parquet(dirs["an_outputs_dir"]).reset_index(drop=True)
    df2 = pd.read_parquet("data/check/newport_qa.parquet")
    assert_frame_equal(df1, df2)
    logger.info("OD matrix is consistent with expected results!")

    logger.info("Calculating the transport performance...")
    tp_df, stats_df = transport_performance(
        dirs["an_outputs_dir"],
        centroid_gdf,
        pop_gdf,
        urban_centre_name=general_config["area_name"].capitalize(),
        urban_centre_country=general_config["area_country"].capitalize(),
        urban_centre_gdf=uc_gdf.reset_index(),
    )
    logger.info("Transport performance calculated. Saving output files...")
    tp_plot_path = os.path.join(
        dirs["metrics_outputs_dir"], "transport_performance.html"
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
    stats_df.to_csv(tp_stats_path, index=False)
    logger.info(f"Transport performance map saved: {tp_plot_path}")
    logger.info(f"Transport performance stats saved: {tp_stats_path}")

    logger.info(
        f"*** Transport performance analysis of {general_config['area_name']} "
        "complete! ***"
    )


if __name__ == "__main__":
    main()
