# used python v3.9.13 base impage
FROM python:3.9.13

# create and set this dir as the working directory
WORKDIR /analysis

# install dependencies - openJDK11, GDAL, osmosis
# for openjdk + osmosis: advice taken from here: https://github.com/datasciencecampus/studious-sniffle/blob/main/Dockerfile
# for gdal: advice taken from here: https://stackoverflow.com/questions/52396635/how-to-add-gdal-in-docker
# also needed to update apt-get to find libgdal-dev
RUN apt-get update && \
    apt-get install -y libgdal-dev g++ openjdk-11-jdk osmosis && \
    apt-get clean -y

# explicitly set env vars for python `rasterio` dependency
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# copy requirements file to start python dependency installation
COPY requirements.txt /analysis/

# install python requirements
RUN pip install --no-cache-dir -r requirements.txt

# copy source code - last step as most frequent change (speeds up re-building)
COPY ./src /analysis/src/

# run script
CMD [ "python", "src/run.py" ]
