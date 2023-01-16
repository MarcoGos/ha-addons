from typing import Any
from datetime import datetime, date, timedelta
import requests
import time
from mapping import MAPPING
import os
import subprocess
import json
from logging import Logger
import utils

class GfsForecast():
    _inventory: dict[str, Any] = {}
    _latitude: float
    _longitude: float
    _store_directory: str = '/data/'
    _gfs_date: date
    _gfs_pass: int
    _max_offset: int
    _data: dict[str, Any]

    def __init__(self, logger: Logger, latitude: float, longitude: float, max_offset: int):
        self.logger = logger
        self._latitude, self._longitude = latitude, longitude
        self._max_offset = max_offset
        self.find_latest_pass_info()

    def __get_url(self, gfs_date: date, gfs_pass: int, offset: int, inventory: bool = False) -> str:
        url_tempate = 'https://nomads.ncep.noaa.gov/pub/data/nccf/com/gfs/prod/gfs.{}/{}/atmos/gfs.t{}z.pgrb2.0p25.f{}'
        gfsPass_str = '{:>02}'.format(gfs_pass)
        gfsDate_str = '{:>04}{:>02}{:>02}'.format(gfs_date.year, gfs_date.month, gfs_date.day)
        url = url_tempate.format(gfsDate_str, gfsPass_str, gfsPass_str, '{:>03}'.format(offset))
        if inventory:
            url += '.idx'
        return url

    def __get_url_by_offset(self, offset: int, inventory: bool = False) -> str:
        return self.__get_url(self._gfs_date, self._gfs_pass, offset, inventory)

    def __get_inventory_by_url(self, url: str) -> bool:
        self._inventory = {}
        response = requests.head(url)
        if not response.ok:
            return False
        tries = 0
        while tries < 3:
            response = requests.get(url)
            if response.status_code != 200 | (len(response.content) < 20000):
                time.sleep(2)
                tries += 1
            else:
                break
        if response.status_code != 200:
            self.logger.error(f'Could not load inventory...{response.status_code}')
            return False
        inventory_raw = response.content.decode('utf-8').split('\n')

        offset = -1
        prevOffset = -1
        prevCode = ''
        prevLayer = ''
        code: str = ''
        layer: str = ''
        for line in inventory_raw:
            values = line.split(':')
            if len(values) == 1:
                break
            if offset > -1:
                prevOffset = offset
                prevCode = code
                prevLayer = layer
            offset = int(values[1])
            code = values[3]
            layer = values[4]
            if prevOffset > -1:
                key = self.__is_code_needed(prevCode, prevLayer)
                if (key is not None) & (key not in self._inventory):
                    self._inventory[key] = { 'start': prevOffset, 'end': offset -1, 'code': prevCode, 'layer': prevLayer }
        key = self.__is_code_needed(code, layer)
        if (key is not None) & (key not in self._inventory):
            self._inventory[key] = { 'start': offset, 'end': 0, 'code': code, 'layer': layer }
        self.logger.debug(f'Downloaded inventory: {url}')
        return True

    def __get_inventory_by_offset(self, new_offset: int) -> bool:
        if self._gfs_pass == -1:
            self.find_latest_pass_info()

        if not self.__restore_inventory(new_offset):
            url = self.__get_url_by_offset(new_offset, True)
            if self.__get_inventory_by_url(url):
                self.__storeInventory(new_offset)
                return True
            return False
        else:
            return True

    def __is_code_needed(self, code: str, layer: str) -> Any:
        for key in MAPPING:
            if (MAPPING[key]['code'] == code) & (MAPPING[key]['layer'] == layer):
                return key
        return None

    def __get_part_of_grib(self, url: str, start: int, end: int) -> str:
        if (end != 0):
            headers = {'Range': 'bytes={}-{}'.format(start, end)}
        else:
            headers = {'Range': 'bytes={}-'.format(start)}
        tries = 0
        while tries < 3:
            self.logger.debug(f'Download {url}, try {tries +1}')
            response = requests.get(url, headers=headers)
            size = end - start +1
            if (response.status_code == 206) & response.content.startswith(b'GRIB') & (len(response.content) == size): 
                gribfile = './tmp.grib'
                file = open(gribfile, 'wb')
                file.write(response.content)
                file.close()
                time.sleep(1)
                return gribfile
            time.sleep(5)
            tries += 1
        return ''

    def __read_value(self, grib_file: str, correction: float) -> float:
        data = subprocess.check_output(['./wgrib2', grib_file, '-s', '-lon', format(self._longitude), format(self._latitude)], text=True)
        self.logger.debug(f'__read_value data={data}')
        # 1:0:d=2023011100:UGRD:10 m above ground:3 hour fcst::lon=6.000000,lat=52.500000,val=5.1438
        index = data.find('::') +2
        lon_text, lat_text, val_text = data[index:].split(',')
        longitude = float(lon_text.split('=')[-1])
        latitude = float(lat_text.split('=')[-1])

        self.__store_used_latitude_longitude(latitude, longitude)
        value = round(float(val_text.split('=')[-1]) + correction, 1)
        return value

    def get_value_from_grib_data(self, offset: int, key: str) -> Any:
        if not self.__get_inventory_by_offset(offset):
            return None
        if key in self._inventory:
            url = self.__get_url_by_offset(offset)
            invPart = self._inventory[key]
            gribfile = self.__get_part_of_grib(url, invPart['start'], invPart['end'])
            if gribfile != '':
                value = self.__read_value(gribfile, MAPPING[key].get('correction', 0))
                os.remove(gribfile)
                return value
        else:
            self.logger.error(f'Key {key} not found in inventory')

    def __get_inventory_storage_path(self, offset: int) -> str:
        return f"{self._store_directory}inventory_{offset}.json"

    def __storeInventory(self, offset: int):
        self._inventory['info'] = {
            'date': self._gfs_date.isoformat(),
            'pass': self._gfs_pass,
            'offset': int(offset)
        }
        file = open(self.__get_inventory_storage_path(offset), "w")
        json.dump(self._inventory, file)
        file.close()
        self.logger.debug(f'Write inventory {offset}')

    def __restore_inventory(self, offset: int) -> bool:
        if self.__inventory_up_to_date(offset):
            return True
        inventoryFile = self.__get_inventory_storage_path(offset)
        self.logger.debug(f'Restoring inventory {inventoryFile}')
        restored: bool = False
        if os.path.exists(inventoryFile):
            file = open(inventoryFile,)
            try:
                storedInventory: dict[str, Any] = json.load(file)
                info = storedInventory.get('info', {})
                if (info.get('date') == self._gfs_date.isoformat()) & (info.get('pass') == self._gfs_pass):
                    self._inventory = storedInventory
                    restored = True
            except json.JSONDecodeError:
                pass
            finally:
                file.close()

        return restored

    def __inventory_up_to_date(self, offset: int) -> bool:
        if not 'info' in self._inventory:
            return False
        if (self._inventory['info']['date'] == self._gfs_date.isoformat()) & (self._inventory['info']['pass'] == self._gfs_pass) & (self._inventory['info']['offset'] == offset):
            return True
        return False

    def find_latest_pass_info(self) -> bool:
        foundGfsDate = date.today()
        foundGfsPass = -1
        counter = 0
        while (counter < 2) & (foundGfsPass == -1):
            for tryPass in [18, 12, 6, 0]:
                url = self.__get_url(foundGfsDate, tryPass, self._max_offset)
                response = requests.head(url)
                if response.ok:
                    foundGfsPass = tryPass
                    self._gfs_date = foundGfsDate
                    self._gfs_pass = foundGfsPass
                    self.logger.debug(f"Found {foundGfsDate} {foundGfsPass}")
                    return True
            if foundGfsPass == -1:
                counter -= 1
                foundGfsDate += timedelta(days=-1)
        return False

    def init_offset(self, offset: int) -> None:
        self._data[f'{offset}'] = {}

    def store_data_value(self, offset: int, key: str, value: int) -> None:
        if not f'{offset}' in self._data:
            self.init_offset(offset)
        self._data[f'{offset}'][key] = value

    def __get_data_storage_path(self) -> str:
        return f'{self._store_directory}data.json'

    def store_data(self):
        file = open(self.__get_data_storage_path(), 'w')
        json.dump(self._data, file)
        file.close()

    def __store_used_latitude_longitude(self, latitude: float, longitude: float) -> None:
        self._data['info']['used_latitude'] = latitude
        self._data['info']['used_longitude'] = longitude

    def restore_data(self) -> None:
        dataPath = self.__get_data_storage_path()
        if os.path.exists(dataPath):
            file = open(dataPath,)
            try:
                storedData = json.load(file)
                if 'info' in storedData:
                    info = storedData['info']
                    if ('date' in info) & ('pass' in info):
                        if (info['date'] == self._gfs_date.isoformat()) & (info['pass'] == self._gfs_pass):
                            self._data = storedData
                            self.logger.debug('data file found and restored')
                            return
            except json.JSONDecodeError:
                pass
            finally:
                file.close()
        self._data = { 
            'info': {
                'date': self._gfs_date.isoformat(),
                'pass': self._gfs_pass
            }
        }

    def is_done(self) -> bool:
        return 'done' in self._data.get('info', {})

    def offset_is_available(self, offset: int) -> bool:
        return f'{offset}' in self._data

    def is_offset_done(self, offset: int) -> bool:
        return 'done' in self._data.get(f'{offset}', {})

    def is_key_in_offset_done(self, offset: int, key: str) -> bool:
        if not self.offset_is_available(offset):
            return False
        return key in self._data[f'{offset}']

    def set_done(self) -> None:
        self._data['info']['done'] = True

    def set_offset_to_done(self, offset: int) -> None:
        self._data[f'{offset}']['done'] = True

    def get_data(self) -> dict[str, Any]:
        return self._data

    def get_date_and_pass(self) -> tuple[date, int]:
        return self._gfs_date, self._gfs_pass

    def get_day_forecast(self) -> dict[date, Any]:
        forecast: dict[date, Any] = {}
        pass_datetime = datetime.fromisoformat(self._data['info']['date'])
        pass_datetime = datetime(pass_datetime.year, pass_datetime.month, pass_datetime.day, self._data['info']['pass'], 0, 0, 0)

        for offset in self._data:
            if offset == 'info':
                continue
            day_data = self._data[offset]
            dt = pass_datetime + timedelta(hours = int(offset))
            if dt.date() not in forecast:
                forecast[dt.date()] = {
                    'rain_chance': 10,
                    'rain': 0,
                    'sun_chance': 90,
                    'vwind': 0,
                    'uwind': 0,
                    'temperature_max': -999,
                    'temperature_min': 999,
                    'min_temperature_daytime': 999,
                    'windspeed': 0,
                    'windangle': 0
                }

            forecast[dt.date()]['rain'] += day_data['rain']
            if (dt.hour > 8) and (dt.hour < 22):
                forecast[dt.date()]['temperature_max'] = max(forecast[dt.date()]['temperature_max'], day_data['tmp'])
                if dt.hour >= 9:
                    forecast[dt.date()]['min_temperature_daytime'] = min(forecast[dt.date()]['min_temperature_daytime'], day_data['tmp'])
                if day_data['cldtotal'] >= 75:
                    forecast[dt.date()]['sun_chance'] -= 16 * day_data['cldtotal'] / 100
                if forecast[dt.date()]['sun_chance'] == 90 and \
                   (day_data['cldhigh'] >= 80 or day_data['cldlow'] > 10):
                    forecast[dt.date()]['sun_chance'] -= 10

                if day_data['rain'] >= 2:
                    forecast[dt.date()]['rain_chance'] = 90
                elif day_data['rain'] > 0:
                    forecast[dt.date()]['rain_chance'] += 10

                forecast[dt.date()]['vwind'] += day_data['vwind']
                forecast[dt.date()]['uwind'] += day_data['uwind']
                windspeed,_ = utils.get_wind_info(day_data['vwind'], day_data['uwind'])
                forecast[dt.date()]['windspeed'] = max(forecast[dt.date()]['windspeed'], windspeed)
            else:
                forecast[dt.date()]['temperature_min'] = min(forecast[dt.date()]['temperature_min'], day_data['tmp'])

        for forecast_date in forecast:
            _,windangle = utils.get_wind_info(forecast[forecast_date]['vwind'], forecast[forecast_date]['uwind'])
            forecast[forecast_date]['windangle'] = windangle

        return forecast
