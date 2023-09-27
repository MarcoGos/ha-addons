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
max_offset: int = 225
api_token: str = os.environ['SUPERVISOR_TOKEN'] if 'SUPERVISOR_TOKEN' in os.environ else ''
scan_interval: int = 10 # minutes

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

    pass_found, gfs_date, gfs_pass = gfs_forecast.find_latest_pass_info()
    if pass_found:
        gfs_forecast.restore_data()
        data_found: bool = False

        if not gfs_forecast.is_done():
            offset = gfs_forecast.get_last_offset(start_offset, max_offset, step)
            if offset == start_offset:
                logger.info(f'New pass found: {gfs_date} {gfs_pass}')
            while offset <= max_offset:
                if not gfs_forecast.offset_is_available(offset):
                    gfs_forecast.init_offset(offset)
                storage.store_status(gfs_date, gfs_pass, offset)
                for key in MAPPING:
                    if not gfs_forecast.is_key_in_offset_done(offset, key):
                        value = gfs_forecast.get_value_from_grib_data(offset, key)
                        if value != None:
                            data_found = True
                            logger.debug(f'Offset={offset} {key}={value}')    
                            gfs_forecast.store_data_value(offset, key, value)
                        else:
                            data_found = False
                            break
                if data_found:
                    gfs_forecast.set_offset_to_done(offset)
                    gfs_forecast.store_data_to_file()
                    offset += step

            if data_found:
                if offset > max_offset:
                    gfs_forecast.set_done()
                    gfs_forecast.store_data_to_file()
                    storage.store_forecast(gfs_forecast.get_day_forecast())
                    storage.store_status_done(gfs_forecast.get_data())                    
        else:
            logger.debug('No new GFS pass found (yet)...')

    if not gfs_forecast.is_done():
        storage.store_status_waiting()

    logger.debug(f'Waiting {scan_interval} minutes to continue...')
    time.sleep(scan_interval * 60)
