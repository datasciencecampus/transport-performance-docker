# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).


## [0.4.0] - 2023-12-21

## Added
-  Using `transport-performance` features:
    - `analyse-network` + exports OD matrix in parquet
    - `metrics` + exports stats as csv and an HTML map
    - `osm` for OSM file filtering
    - `gtfs`for GTFS file filtering, validation, cleaning + outputs (route/trip summaries as csv, validation summaries pre/post cleaning as csv, stops/convex hull maps)
    - All above features working in docker container (consistent results inside and out)
- `data/inputs/gtfs/route_lookup.pkl` added (needed for `GtfsInstance`).
- `data/inputs/config.toml` added as an example.

## Changed
- `src/run.py` and `src/utils.py` with features above.
- `.gitignore` to permit above exemptions.
- `README.md` summarises main known limitations.

## [0.3.0] - 2023-12-20

### Added
- Run using `docker compose up` (`docker-compose.yaml`)
- Set-up docker volume between local/host aread `./data/` and container area `./analysis/data/` (automated transferring of files).
- `src/run.py` performs urban centre, population pre-processing, and r5py run (getting consistent results outside docker and previous runs!).
- `src/utils.py` to handle new outputs folder generation, logging, and map plotting.
- `Osmosis` installation in Dockerfile.
- Structure to `data/inputs/` directory.
- CHANGELOG.md now in place.
- CONTRIBUTING.md placeholder.

### Changed
- README.md - now contains intiial installation and usage instructions.

### Fixed
- Refactored Dockerfile to make rebuilding quicker:
    - Copying `src/` content is now the last build stage, so all layers above remain cached while developing `src/` content.

### Removed
- Dockerfile no longer copies `data/` directory.

## [0.2.0] - 2023-12-19

### Added
- `openJDK11` installation in Dockerfile

## [0.1.0] - 2023-12-19

### Added

- Initial repo setup
- Pre-commit config
- Initial python reqs in
- Added GDAL installation in Dockerfile
- Initial `src/run.py` 'Hello, World!` script to check running.


[0.1.0]: https://github.com/datasciencecampus/transport-performance-docker/releases/tag/v0.1.0
[0.2.0]: https://github.com/datasciencecampus/transport-performance-docker/releases/tag/v0.2.0
[0.3.0]: https://github.com/datasciencecampus/transport-performance-docker/releases/tag/v0.3.0
[0.4.0]: https://github.com/datasciencecampus/transport-performance-docker/releases/tag/v0.4.0
