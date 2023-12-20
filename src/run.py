"""src/run.py."""

import toml

from run_utils import create_dir_structure

# directory to config file
CONFIG_FILE = "data/inputs/config.toml"


def main():
    """Execute end-to-end analysis."""
    # read and split out config into separate configs to minimise line lengths
    config = toml.load(CONFIG_FILE)
    general_config = config["general"]

    # create directory structure upfront
    _ = create_dir_structure(general_config["area_name"], add_time=False)


if __name__ == "__main__":
    main()
