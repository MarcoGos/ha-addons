# About
This add-on uses the [pyvantagepro](https://pypi.org/project/PyVantagePro/) library to communicate to a Davis weather station like Davis Vantage Pro and Davis Vantage Vue. It produces several sensors via the MQTT integration under the device name "Davis Weather Station".

# Configuration

##  Device or Address
First "Show unused optional configuration options" so all options are visible. Now choose a communication protocol by either entering a serial device or an ip address combined with a port (eg. 192.168.1.32:1111).

## Interval
Enter an interval (in seconds) between each readout and update of the sensors. The shorter the interval the more the history will be flooded so keep that in mind.

## Imperial or Metric
Choose either Imperial or Metric system.

## New temperature sensor
Use this setting if the new VP2 TH sensor 7346.070 is used on an older Vantage Pro 2. Temperature will be corrected with -0.5°C or -0.9°F.

## Log level
Just leave it to "notice", only when experiencing problems you could change the level to get more information.

# Notes
- Depending on your configuration, the MQTT server config may need to include the port, typically `1883` or `8883` for SSL communications. For example, `mqtt://core-mosquitto:1883` for Home Assistant's Mosquitto add-on.
- To find out which serial ports you have exposed go to **Supervisor → System → Host system → ⋮ → Hardware**
