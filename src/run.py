"""src/run.py."""

import os
import toml

from run_utils import create_dir_structure, setup_logger

# directory to config file
CONFIG_FILE = "data/inputs/config.toml"
LOGGER_NAME = "tp-docker-analysis"


def main():
    """Execute end-to-end analysis."""
    # read and split out config into separate configs to minimise line lengths
    config = toml.load(CONFIG_FILE)
    general_config = config["general"]

    # create directory structure upfront
    dirs = create_dir_structure(general_config["area_name"], add_time=False)

    logger = setup_logger(
        LOGGER_NAME,
        file_name=os.path.join(
            dirs["logger_dir"], f"{general_config['area_name']}_analysis.txt"
        ),
    )
    logger.info(f"Created analysis directory structure at {dirs['files_dir']}")


if __name__ == "__main__":
    main()
