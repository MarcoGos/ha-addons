# Changelog

## 1.0.0

- Initial version

## 1.0.1

- Added dew point calculation

## 1.0.2

- Added address to configuration to use an ip link

## 1.0.3

- Now using docker hub image

## 1.0.4

- Changed name of device to Davis Weather Station.

## 1.0.5

- Fixed issue when using address.

## 1.0.6

- Added metric windspeed unit of measure alternative (m/s instead of km/h).
- Changed name of windspeed 10 minutes average.

## 1.0.7

- Small fix on starting the add-on

## 1.0.8

- Close connection (and free tcp/serial port) after each data received.

## 1.0.9

- Fixed issue MQTT not updating when interval larger than 60 seconds.

## 1.0.10

- Fixed error on closing link.
- Added long term statistics.

## 1.0.11

- Finally fixed occasionally error on closing link.
- Added Status sensor.
- Better handling of sending payloads to MQTT.
- Improved stability.

## 1.0.12

- Added availability via LWT in MQTT.
- Added Last Error.

## 1.0.13

- Added option to use 8 cardinal directions for wind instead of 16.
- Suppress UV Level and Solar Radiation sensor if value is unavailable.

## 1.0.14

- Corrected UV value (was 10 times higher).

## 1.0.15

- Made UV value a floating point value instead of an integer.
