import time
from mapping import MAPPING
import sys, getopt
from logger import logger, log_levels
from keyboardthread import KeyboardThread
from gfsforecast import GfsForecast
from sensor import Sensor
import os

log_level: str = 'info'
max_offset: int = 168
api_token: str = os.environ['SUPERVISOR_TOKEN'] if 'SUPERVISOR_TOKEN' in os.environ else ''
gfs_detailed: bool = False

try:
    opts, args = getopt.getopt(sys.argv[1:], "l:m:d",["log_level=", "max_offset", "detailed"])
except getopt.GetoptError:
    print('grabforecast.py [-l <loglevel>][-m <maxoffset>][-d]')
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-l", "--log_level"):
        log_level = arg
    if opt in ("-m", "--max_offset"):
        max_offset = int(arg)
    if opt in ("-d", "--detailed"):
        gfs_detailed = True

logger.setLevel(log_levels[log_level])

def keyboard_callback(inp: str) -> None:
    if (inp == 'restore-sensor'):
        sensor.restore_ha_sensor()
        logger.info('Restored HA sensor')

#start listening to input - thread
keyboard_thread = KeyboardThread(keyboard_callback)

sensor = Sensor(api_token, 'weather.gfsforecast', gfs_detailed)
latitude, longitude = sensor.get_gps_position()
gfs_forecast = GfsForecast(logger, latitude, longitude, max_offset)

while True:
    offset: int = 1 if gfs_detailed else 3
    step: int = 1 if gfs_detailed else 3

    if gfs_forecast.find_latest_pass_info():
        sensor.set_sensor_base_data(*gfs_forecast.get_date_and_pass())
        gfs_forecast.restore_data()
        data_found: bool = True

        if not gfs_forecast.is_done():
            while (offset <= max_offset) & data_found:
                if not gfs_forecast.offset_is_available(offset):
                    gfs_forecast.init_offset(offset)
                    sensor.update_sensor_during_loading(*gfs_forecast.get_date_and_pass(), offset)

                if not gfs_forecast.is_offset_done(offset):
                    for key in MAPPING:
                        if not gfs_forecast.is_key_in_offset_done(offset, key):
                            value = gfs_forecast.get_value_from_grib_data(offset, key)
                            if value != None:
                                logger.debug(f'Offset={offset} {key}={value}')    
                                gfs_forecast.store_data_value(offset, key, value)
                                data_found = True
                            else:
                                logger.error(f'No data found for key {key} offset {offset}...')
                                data_found = False
                                break
                    if data_found:
                        gfs_forecast.set_offset_to_done(offset)
                    gfs_forecast.store_data()

                offset += step
                if offset >= 120:
                    step = 3

            if (offset > max_offset) & data_found:
                gfs_forecast.set_done()
                sensor.update_sensor_with_full_data(gfs_forecast.get_data(), gfs_forecast.get_day_forecast())

    logger.debug('Waiting 5 minutes to continue...')
    time.sleep(5 * 60)
