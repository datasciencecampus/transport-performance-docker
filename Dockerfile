# used python v3.9.13 base impage
FROM python:3.9.13

# create and set this dir as the working directory
WORKDIR /analysis

# copy necessary files
COPY requirements.txt /analysis/
COPY ./src /analysis/src/
COPY ./data /analysis/data/

# install GDAL requirements
# advice taken from here: https://stackoverflow.com/questions/52396635/how-to-add-gdal-in-docker
# also needed to update apt-get to find libgdal-dev
RUN apt-get update && \
    apt-get install -y libgdal-dev g++ --no-install-recommends && \
    apt-get clean -y
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# install open JDK java 11
RUN apt-get -y install openjdk-11-jdk

# install python requirements
RUN pip install --no-cache-dir -r requirements.txt

# run script
CMD [ "java", "--version" ]
