"""src/run_uc_only.py."""

import geopandas as gpd
import os
import toml

from pyprojroot import here
from shapely.geometry import box
from transport_performance.urban_centres.raster_uc import UrbanCentre
from datetime import datetime

from transport_performance.utils.raster import (
    merge_raster_files,
)

from utils import setup_logger


# set the container logger name
LOGGER_NAME = "tp-docker-uc"
output = here("data/uc/")

config = toml.load(here('data/inputs/config/default_config.toml'))


def main():
    """Find urban centres."""
    area_name = os.getenv("AREA_NAME")
    bbox = [float(x) for x in os.getenv("BBOX").split(',')]
    bbox_crs = os.getenv("BBOX_CRS")
    centre = [float(x) for x in os.getenv("CENTRE").split(',')]
    centre_crs = os.getenv("CENTRE_CRS")

    logger = setup_logger(
        LOGGER_NAME,
        file_name=here("data/ucs/log/run.txt"),
    )
    logger.info(f"Detecting urban centre of {area_name}")

    # put bbox into a geopandas dataframe for `get_urban_centre` input
    bbox_gdf = gpd.GeoDataFrame(
        geometry=[box(*bbox)], crs=bbox_crs
    )
    if bbox_crs != "ESRI:54009":
        logger.info(
            f"Convering bbox_gdf from {bbox_crs} to 'ESRI:54009'"
        )
        bbox_gdf.to_crs("ESRI:54009", inplace=True)

    # merge input raster files
    logger.info("Merging input urban centre raster files...")
    merged_uc_file = os.path.join(
        here("data/urban_centre_merged.tif")
    )
    merge_raster_files(
        here("data/inputs/urban_centre/"),
        os.path.dirname(merged_uc_file),
        os.path.basename(merged_uc_file),
        subset_regex=config['urban_centre']['subset_regex'],
    )

    # detect urban centre
    uc = UrbanCentre(merged_uc_file)
    try:
        uc_gdf = uc.get_urban_centre(
            bbox_gdf,
            centre=tuple(centre),
            centre_crs=centre_crs,
            buffer_size=config['urban_centre']['buffer_size'],
            buffer_estimation_crs=(
                config['urban_centre']['buffer_estimation_crs']
            ),
        )
    except:
        logger.info("Urban centre creation failed")
        logger.exception("message")
        return None

    # set the index to the label column to make filtering easier
    uc_gdf.set_index("label", inplace=True)

    # visualise outputs
    m = uc_gdf[::-1].reset_index().explore("label", cmap="viridis")
    uc_map_path = here(f"data/ucs/{area_name}_urban_centre.html")
    m.save(uc_map_path)
    logger.info(f"Saved urban centre map: {uc_map_path}")

    uc_output_path = here(f"data/ucs/{area_name}_uc_gdf.parquet")
    uc_gdf.to_parquet(uc_output_path, index=False)
    logger.info(f"Saved urban centre output to parquet: {uc_output_path}")

    logger.info("Urban centre detection complete.")


if __name__ == "__main__":
    main()
