import time
from mapping import MAPPING
import sys, getopt
from logger import logger, log_levels
from gfsforecast import GfsForecast
from hacoreapi import HACoreApi
from storage import Storage
import os

log_level: str = 'info'
max_offset: int = 168
detailed: bool = False
api_token: str = os.environ['SUPERVISOR_TOKEN'] if 'SUPERVISOR_TOKEN' in os.environ else ''
scan_interval: int = 5

try:
    opts, args = getopt.getopt(sys.argv[1:], "l:m:",["log_level=", "max_offset="])
except getopt.GetoptError:
    print('grabforecast.py [-l <loglevel>][-m <maxoffset>]')
    sys.exit(2)
for opt, arg in opts:
    if opt in ("-l", "--log_level"):
        log_level = arg
    if opt in ("-m", "--max_offset"):
        max_offset = int(arg)

logger.setLevel(log_levels[log_level])

storage = Storage()
hacoreapi = HACoreApi(api_token)
latitude, longitude = hacoreapi.get_gps_position()
gfs_forecast = GfsForecast(logger, latitude, longitude, max_offset, hacoreapi.get_zone_info())

while True:
    offset: int = 3
    step: int = 3

    if gfs_forecast.find_latest_pass_info():
        gfs_forecast.restore_data()
        data_found: bool = True

        if not gfs_forecast.is_done():
            while (offset <= max_offset) & data_found:
                if not gfs_forecast.offset_is_available(offset):
                    gfs_forecast.init_offset(offset)
                    storage.store_status(*gfs_forecast.get_date_and_pass(), offset)

                if not gfs_forecast.is_offset_done(offset):
                    for key in MAPPING:
                        if not gfs_forecast.is_key_in_offset_done(offset, key):
                            value = gfs_forecast.get_value_from_grib_data(offset, key)
                            if value != None:
                                logger.debug(f'Offset={offset} {key}={value}')    
                                gfs_forecast.store_data_value(offset, key, value)
                            else:
                                logger.error(f'No data found for key {key} offset {offset}...')
                                data_found = False
                                break
                    if data_found:
                        gfs_forecast.set_offset_to_done(offset)

                offset += step
                if offset >= 120:
                    step = 3

            if (offset > max_offset):
                gfs_forecast.set_done()
                storage.store_forecast(gfs_forecast.get_day_forecast())
                storage.store_status_done(gfs_forecast.get_data())
                
            gfs_forecast.store_data()

        else:
            logger.debug('No new GFS pass found (yet)...')

    logger.debug(f'Waiting {scan_interval} minutes to continue...')
    time.sleep(scan_interval * 60)
