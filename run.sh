#!/bin/bash

# build docker image
docker build -t transport-performance .

# manchester
AREA_NAME='manchester' BBOX='-2.9061,53.0723,-1.5108,53.8376' BBOX_CRS='EPSG: 4326' CENTRE='53.4901779140037,-2.2324148862360778' CENTRE_CRS='EPSG: 4326' docker compose up

# liverpool
AREA_NAME='liverpool' BBOX='-3.6818,53.0202,-2.2866,53.7865' BBOX_CRS='EPSG: 4326' CENTRE='53.40562178617905,-2.9813298622510875' CENTRE_CRS='EPSG: 4326' docker compose up

