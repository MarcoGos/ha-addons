import time
from mapping import MAPPING
import sys, getopt
from logger import logger, log_levels
from gfsforecast import GfsForecast
from hacoreapi import HACoreApi
from storage import Storage
from datetime import date
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

storage = Storage(max_offset)
hacoreapi = HACoreApi(api_token)
latitude, longitude = hacoreapi.get_gps_position()
gfs_forecast = GfsForecast(logger, latitude, longitude, max_offset, hacoreapi.get_zone_info())
gfs_date: date
gfs_pass: int

while True:
    start_offset: int = 3
    offset: int = start_offset
    step: int = 3

    new_pass_found, gfs_date, gfs_pass = gfs_forecast.find_latest_pass_info()
    if new_pass_found:
        gfs_forecast.restore_data()
        data_found: bool = True

        if not gfs_forecast.is_done():
            while (offset <= max_offset) & data_found:
                storage.store_status(gfs_date, gfs_pass, offset)
                if not gfs_forecast.offset_is_available(offset):
                    gfs_forecast.init_offset(offset)

                if not gfs_forecast.is_offset_done(offset):
                    if (offset == start_offset):
                        logger.info(f'New pass found: {gfs_date} {gfs_pass}')
                    for key in MAPPING:
                        if not gfs_forecast.is_key_in_offset_done(offset, key):
                            value = gfs_forecast.get_value_from_grib_data(offset, key)
                            if value != None:
                                logger.debug(f'Offset={offset} {key}={value}')    
                                gfs_forecast.store_data_value(offset, key, value)
                            else:
                                data_found = False
                                break
                    if data_found:
                        gfs_forecast.set_offset_to_done(offset)
                        offset += step

            if data_found and (offset > max_offset):
                gfs_forecast.set_done()
                storage.store_forecast(gfs_forecast.get_day_forecast())
                storage.store_status_done(gfs_forecast.get_data())
                
            gfs_forecast.store_data_to_file()

        else:
            logger.debug('No new GFS pass found (yet)...')

    logger.debug(f'Waiting {scan_interval} minutes to continue...')
    if not gfs_forecast.is_done():
        storage.store_status_waiting()
    time.sleep(scan_interval * 60)
