#!/bin/bash

docker run --rm -it -v $PWD:/build --platform linux/armhf alpine

apk update
apk add build-base zlib-dev wget zip unzip bzip2 gfortran gcc g++
wget ftp://ftp.cpc.ncep.noaa.gov/wd51we/wgrib2/wgrib2.tgz.v3.1.1 -O /tmp/wgrib2.tgz
cd /tmp
tar -xvzf /tmp/wgrib2.tgz
cd /tmp/grib2
export FC=gfortran && export CC=gcc
make
cp wgrib2/wgrib2 /build
