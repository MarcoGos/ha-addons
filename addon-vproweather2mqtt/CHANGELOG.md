# Changelog

## 1.0.4

- Added log level configuration option
- Removed unit of measure of Solar Radiation sensor
- Removed the Next Archive Record sensor

## 1.0.3

- Better handle MQTT credential check
- Replace heat index and wind chill with own calculations
- Handles temperature correction if new VP2 TH sensor 7346.070 is used on older Vantage Pro 2
- Added auto setting weather station time to system time

## 1.0.2

- Added alternative Heat Index calculation if not gotten from device
- Changed names of entities in Home Assistant
- Fixed solar radiation entity
- Added auto determine Davis weather station model

## 1.0.1

- Changed GitHub path to altered vproweather source. So extra temperature and humidity sensors (also leaf and soil) are added. Cleaned up code. Updated readme.

## 1.0.0

- Initial version