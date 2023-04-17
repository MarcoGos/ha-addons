# About
This add-on download GFS grib files from the NOAA Nomads server and it produces a weather sensor via the MQTT integration under the device name "GFS forecast".

# Configuration

## Maximum offset
GFS is calculated until 384 hours in advance. The offset is between 1 and 384 hours.

## GFS detailed
Default GFS data is read with a 3 hours offset step, if enabled it will read data with a 1 hour offset step for the first 120 hours.

## Log level
Just leave it to "notice", only when experiencing problems you could change the level to get more information.

# Notes
None

# Known issues
None
