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

## Usage

This section covers general usage instructions only. Developers, see [CONTRIBUTING.md] for more details.

1. Add required input data and `config.toml`. See the [Input Data](#input-data) and [Config TOML](#config-toml) sections for more details.

2. Run the docker container:
```
docker compose up
```

The container will then start and provide progress updates throughout via CLI logs.

All outputs will then be available in `data/<AREA_NAME>_<DATETIMESTAMP>/` where `<AREA_NAME>` is the name set inside `config.toml` and `<DATETIMESTEMP>` is set at runtime. Logs are also available in `data/<AREA_NAME>_<DATETIMESTAMP>/outputs/log/` in `.txt` format.

> Note: a new outputs directory is build for each run.

> Note: the docker container automatically shutdown once the run is complete.

### <a name="input-data"></a>Input Data

All input data should be placed within subdirectories of the `data/inputs/` folder. This folder is linked to the docker container and will be used to read inputs locally.

- GTFS data can be added within `data/inputs/gtfs/`
- OSM data can be added within `data/inputs/osm/`
- population data can be added within `data/inputs/population/`
- urban centre data can be added within `data/inputs/urban_centre/`

> Note: changing this structure will lead to issues when running the container.

### <a name="config-toml"></a>Config TOML

`config.toml` can be placed within `data/inputs/` directory. More details to follow when a specification has been finalised.

> Note: currently, the same config files used in [`transport-network-performance`] can be used here too, with some exceptions (mainly, there is not control over where outputs are saved).

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
