"""src/run.py."""

import geopandas as gpd
import glob
import os
import toml

from shapely.geometry import box
from transport_performance.urban_centres.raster_uc import UrbanCentre

from run_utils import create_dir_structure, setup_logger

# directory to config file
CONFIG_FILE = "data/inputs/config.toml"
LOGGER_NAME = "tp-docker-analysis"


def main():
    """Execute end-to-end analysis."""
    # read and split out config into separate configs to minimise line lengths
    config = toml.load(CONFIG_FILE)
    general_config = config["general"]
    uc_config = config["urban_centre"]

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


if __name__ == "__main__":
    main()
