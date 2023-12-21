"""src/run.py."""

import datetime
import geopandas as gpd
import glob
import os
import pandas as pd
import toml

from shapely.geometry import box
from transport_performance.urban_centres.raster_uc import UrbanCentre
from transport_performance.population.rasterpop import RasterPop
from transport_performance.analyse_network import AnalyseNetwork
from transport_performance.metrics import transport_performance
from transport_performance.utils.raster import sum_resample_file
from r5py import TransportMode
from pandas.testing import assert_frame_equal

from utils import create_dir_structure, setup_logger, plot

# directory to config file
CONFIG_FILE = "data/inputs/config.toml"
LOGGER_NAME = "tp-docker-analysis"


def main():
    """Execute end-to-end analysis."""
    # read and split out config into separate configs to minimise line lengths
    config = toml.load(CONFIG_FILE)
    general_config = config["general"]
    uc_config = config["urban_centre"]
    pop_config = config["population"]
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

    logger.info("Detecting urban centre...")
    # put bbox into a geopandas dataframe for `get_urban_centre` input
    bbox_gdf = gpd.GeoDataFrame(
        geometry=[box(*uc_config["bbox"])], crs="ESRI:54009"
    )

    # detect urban centre
    uc = UrbanCentre(glob.glob("data/inputs/urban_centre/*.tif")[0])
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
    logger.info("Urban centre detection complete.")

    logger.info("Resampling population data...")
    pop_raw_input = glob.glob("data/inputs/population/*.tif")[0]
    pop_filename = os.path.basename(pop_raw_input).replace(
        ".tif", "_resampled.tif"
    )
    pop_input = os.path.join(dirs["interim_pop"], pop_filename)
    sum_resample_file(pop_raw_input, pop_input)

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
    logger.info("Population pre-processing complete.")

    logger.info("Building transport network...")
    an = AnalyseNetwork(
        centroid_gdf,
        glob.glob("data/inputs/osm/*.pbf")[0],
        [glob.glob("data/inputs/gtfs/*.zip")[0]],
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
