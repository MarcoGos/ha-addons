# About
This add-on downloads GFS grib files from the NOAA Nomads server and it produces a weather sensor in Home Assistant under the device name "GFS forecast".

# Configuration

## Maximum offset
GFS is calculated for 384 hours in advance. The offset is between 1 and 384 hours.

## GFS detailed
If enabled it will produce additional detailed information. This information is published as an attribute called "detailed_forecast".

## Imperial or Metric
Choose either Imperial or Metric system.

## Log level
Just leave it to "info", only when experiencing problems you could change the level to get more information.

# Restore the state after Home Assistant restarts
After home assistant restarts, the GFS Forecast device is gone. You need an automation which starts once after home assistant restarts and restores the state. Use the following code to restore the sensor state after each HA restart:

```
alias: Restore GFS forecast status
description: ""
trigger:
  - event: start
    platform: homeassistant
condition: []
action:
  - service: hassio.addon_stdin
    data:
      addon: f78e9da0_gfsforecast
      input: restore-sensor
mode: single
```

# Notes
None

# Known issues
None
