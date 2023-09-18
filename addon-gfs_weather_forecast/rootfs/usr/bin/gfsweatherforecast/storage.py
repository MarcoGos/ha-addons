from typing import Any
from datetime import date
from logger import logger
import json
from const import store_directory

class Storage:
    _state: str
    _used_latitude_longitude: str = ""
    _current: dict[str, Any] = {}
    _loading: dict[str, Any] = {}
    _gfs_pass: int

    def __init__(self) -> None:
        pass

    def store_forecast(self, day_forecast: dict[str, Any]):
        filename = f'{store_directory}forecast.json'
        with open(filename, mode='w') as file:
            file.write(json.dumps(day_forecast))
        logger.debug(f'Stored daily forecast data to {filename}')

    def store_status(self, gfs_date: date, gfs_pass: int, offset: int):
        self._loading = {
            'date': gfs_date.isoformat(),
            'pass': gfs_pass,
            'offset': offset
        }
        self._state = "Loading"
        self._store_status()


    def store_status_done(self, gfs_data: dict[str, Any]):
        self._loading = {}
        self._current = {
            'date': gfs_data['info']['date'],
            'pass': gfs_data['info']['pass']
        }
        self._state = "Finished"
        self._used_latitude_longitude = f"{gfs_data['info']['used_latitude']}, {gfs_data['info']['used_longitude']}"
        self._store_status()

    def _store_status(self):
        status_data: dict[str, Any] = {
            "status": self._state,
            "used_latitude_longitude": self._used_latitude_longitude,
            "current": self._current,
            "loading": self._loading
        }
        filename = f'{store_directory}status.json'
        with open(filename, mode='w') as file:
            file.write(json.dumps(status_data))
        logger.debug(f'Stored status data to {filename}')

        
