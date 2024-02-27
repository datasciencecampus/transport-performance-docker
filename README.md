<img src="https://github.com/datasciencecampus/awesome-campus/blob/master/ons_dsc_logo.png">

# `transport-performance-docker`

## About
A dockerised solution for analysing urban centres using [`transport-network-performance`].

## Installation and Building
This section covers general installation and building only. Developers, see [CONTRIBUTING.md] for more details.

1. Install dependencies: [Docker]

2. Clone this repo and move into the directory:
```
git clone https://github.com/datasciencecampus/transport-performance-docker.git
cd transport-performance-docker
```

3. Build the docker image:
```
docker build -t transport-performance .
```

The `transport-performance` docker image should then be visable using `docker images` in a CLI

> Note: steps 2 and 3 are temporary while this image is not hosted (somewhere like DockerHub, for example).

## Usage

This section covers general usage instructions only. Developers, see [CONTRIBUTING.md] for more details.

1. Add required input data (see the [Input Data](#input-data) section for more details).

2. (Optional) Create a configuration toml to define the 'core' set-up parameters, those that will be consitently used across all urban centre runs (see the [Config TOML](#config-toml) section for more details).

3. Set the following environment variables to run specific urban centre parameters:

| Environment Variable | Required | Default Value | Description |
| --- | --- | --- | --- |
| `COUNTRY_NAME` | Yes | - | Name of the urban centre country |
| `AREA_NAME` | Yes | - | Name of the urban centre (analysis area) |
| `BBOX` | Yes | - | Bounding box coordinates surrounding the entirity of the urban centre. It is a string comma separated list format in left, bottom, right, top order. Note: the limits of this bounding box do not need to be precise, but they should make certain they are large enough to include the entirity of the urban centre |
| `CENTRE` | Yes | - | The coordinate within the urban centre of interest. It is a string comma separated list in Y coord, X coord order. Note: this point does not need to be precise, but must be somewhere within the expected urban centre boundary |
| `BBOX_CRS` | No | `EPSG:4326` | Authority code of the coordinate reference system used to define `BBOX` |
| `CENTRE_CRS` | No | `EPSG:4326` | Authority code of the coordinate reference system used to define `CENTRE` |
| `BUFFER_ESTIMATION_CRS` | No | `EPGS:27700` | Authority code of the coordinate referece system used when calculating the urban centre buffer |
| `GTFS_OSM_SUBDIR` | No | `COUNTRY_NAME` | Subdirectory name in which `gtfs` and `osm` folders are located |
| `EMPTY_FEED` | No | `0` | Whether to remove empty GTFS feeds post filtering. Should be either `0` or `1`. Setting `0` means empty feeds will not be deleted and an error wil be raised. Setting `1` means empty feeds will be deleted and a warning will be raised. |
| `FAST_TRAVEL` | No | `1` | During GTFS cleaning, a flag to identify whether unrealsitic trips (where vehicle would have to travel unrealistically fast) should be removed. These trips will be removed when set to `1`. Setting `0` means this cleaning stage will not occur. |
| `CALCULATE_SUMMARIES` | No | `1` | Whether GTFS trip and route summaries should be generated (counts by modality by date). These will be calcualted when set to `1`. Setting to `0` will skip this step (with a log warning being raised). |
| `BATCH_ORIG` | No | `0` | Whether origins should be batched to improve memory utilisation. Setting to `0` results in no origin/destination batching and if memory availablility allows will be the most performant approach. Setting to `1` will batch origins and can be helpful when memory limitiations impact larger urban centres. |
| `CONFIG_FILE` | No | `default_config.toml` | The file name of the 'base' configuration toml file to use. |

4. Run the docker container (for each specific urban centre, as required):
```
docker compose up
```

The container will then start and provide progress updates throughout via CLI logs.

All outputs will then be available in `data/<AREA_NAME>_<DATETIMESTAMP>/` where `<AREA_NAME>` is the name set inside the environment variable and `<DATETIMESTEMP>` is set at runtime. Logs are also available in `data/<AREA_NAME>_<DATETIMESTAMP>/outputs/log/` in `.txt` format.

> Notes:
> - A new outputs directory is build for each run.
> - The docker container automatically shutsdown once the run is complete.
> - The `Makefile` can be used to spin up instances of the container for a subset of urban centres. See [Using the Makefile](#using-the-makefile) for more information.

### <a name="input-data"></a>Input Data

All input data should be placed within subdirectories of the `data/inputs/` folder. This folder is linked to the docker container and will be used to read inputs locally.

- GTFS data can be added within `data/inputs/<GTFS_OSM_SUBDIR>/gtfs/`
- OSM data can be added within `data/inputs/<GTFS_OSM_SUBDIR>/osm/`
- population data can be added within `data/inputs/population/`
- urban centre data can be added within `data/inputs/urban_centre/`

> Notes:
> - Changing this structure will lead to issues when running the container.
> - `<GTFS_OSM_SUBDIR>` corresponds to the value assigned to the `GTFS_OSM_SUBDIR` environment variable. Unless specified directly, this will default to the value of `COUNTRY_NAME`.

### <a name="config-toml"></a>Config TOML

An updated `.toml` can be placed within `data/inputs/` directory. This captures 'core' configuration parameters that will be used consistently across all urban centre analyses run. More details to follow when a specification has been finalised, but `data/inputs/config/default_config.toml` can be used as a template in the meantime.

### <a name="using-the-makefile"></a>Using the Makefile

### Current known limitations

Below is a summary of the main currently known limitations. See the [GitHub repo issues](https://github.com/datasciencecampus/transport-performance-docker/issues) tab for more details.

1. Does not have `pyosmium`/`osmium-tool` dependencies (`validate_osm` not useable) [#3] (https://github.com/datasciencecampus/transport-performance-docker/issues/3)

## Data Science Campus
At the [Data Science Campus](https://datasciencecampus.ons.gov.uk/about-us/) we apply data science, and build skills, for public good across the UK and internationally. Get in touch with the Campus at [datasciencecampus@ons.gov.uk](datasciencecampus@ons.gov.uk).

## License

<!-- Unless stated otherwise, the codebase is released under [the MIT Licence][mit]. -->

The code, unless otherwise stated, is released under [the MIT Licence][mit].

The documentation for this work is subject to [© Crown copyright][copyright] and is available under the terms of the [Open Government 3.0][ogl] licence.

[mit]: LICENCE
[copyright]: http://www.nationalarchives.gov.uk/information-management/re-using-public-sector-information/uk-government-licensing-framework/crown-copyright/
[ogl]: http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
[CONTRIBUTING.md]: CONTRIBUTING.md
[`transport-network-performance`]: https://github.com/datasciencecampus/transport-network-performance
[Docker]: https://www.docker.com/
